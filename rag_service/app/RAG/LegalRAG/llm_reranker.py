"""
LLM reranking of retrieved sections
===================================
Reorders candidates by whether the conduct actually meets the elements of each
section, which is the judgement a cosine score cannot make.

The measurement that motivated this: querying the index with a section's own
text returns that section at 0.935 and its nearest neighbour at 0.862, so the
embeddings separate พ.ร.บ.คอม ม.๕ from ม.๗ perfectly well. Querying with a case
narrative returns everything in a band of 0.47–0.51. The index is not the
problem and the model is not the problem — the gap between how an incident is
described and how a statute is written is, and no amount of ranking by distance
closes it.

What does close it is reading. ม.๕ and ม.๗ differ by one word, ระบบ against
ข้อมูล, and that word is the whole offence. ม.๘ is longer than either and
carries the vocabulary of both, so it wins vague queries on breadth alone. A
model asked "does this conduct meet the elements of this section" answers that;
a distance does not.

Scores are elements-based and deliberately coarse. The model is told to look
for the specific act the section requires, not for topical resemblance, and to
score 0 when the section belongs to a different kind of actor — which is what
puts พ.ร.บ.คอม ม.๒๒-๒๔ (offences by พนักงานเจ้าหน้าที่ handling data obtained
under a court order) at the top of results for an external intruder.

One call per query, all candidates in it. Per-candidate calls would multiply
cost and latency by the candidate count for no gain.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from .config import LEGAL_RERANK_MODEL

# Enough candidates for the right section to be present, few enough to fit one
# prompt comfortably. Dense recall@20 was .833, so the ceiling this can reach is
# set by what retrieval hands over.
DEFAULT_CANDIDATES = 20

SYSTEM_PROMPT = """คุณเป็นผู้ช่วยนักกฎหมายไทย หน้าที่คือประเมินว่า "พฤติการณ์ในสำนวน" เข้าองค์ประกอบความผิดของแต่ละมาตราที่ให้มาหรือไม่

วิธีให้คะแนน (0-3):
3 = พฤติการณ์เข้าองค์ประกอบครบถ้วนชัดเจน
2 = น่าจะเข้า แต่ยังขาดข้อเท็จจริงบางส่วน
1 = เกี่ยวข้องห่าง ๆ ไม่ครบองค์ประกอบ
0 = ไม่เข้าเลย

ให้ 0 เสมอเมื่อ:
- มาตรานั้นใช้กับ "ผู้กระทำ" คนละประเภท (เช่น มาตราที่ลงโทษพนักงานเจ้าหน้าที่ แต่ผู้ต้องหาเป็นบุคคลภายนอก)
- มาตรานั้นต้องการวัตถุแห่งการกระทำคนละอย่าง (เช่น "ระบบคอมพิวเตอร์" กับ "ข้อมูลคอมพิวเตอร์" ไม่ใช่สิ่งเดียวกัน)
- เข้ากันแค่เพราะใช้คำคล้ายกัน แต่คนละบริบท

อ่านตัวบทให้ครบก่อนตัดสิน อย่าเดาจากชื่อมาตรา ห้ามแต่งตัวบทเอง ห้ามเสนอมาตราที่ไม่มีในรายการ

ตอบ JSON เท่านั้น:
{"scores":[{"citation":"<คัดลอกให้ตรงทุกตัวอักษร>","score":0-3,"element":"<องค์ประกอบที่เข้าหรือที่ขาด สั้น ๆ>"}]}"""


@dataclass
class RerankedHit:
    citation: str
    score: int
    element: str
    dense_rank: int


def build_prompt(narrative: str, hits) -> str:
    lines = [f"พฤติการณ์ในสำนวน:\n{narrative.strip()}", "", "มาตราที่ต้องประเมิน:"]
    for hit in hits:
        body = " ".join(hit.text.split())
        lines.append(f"\n[{hit.citation}]\n{body[:700]}")
    return "\n".join(lines)


def _strip_thinking(text: str) -> str:
    """Qwen3.5 reasons by default and the block is not part of the answer."""
    return re.sub(r"<think>.*?</think>", "", text or "", flags=re.S)


# Fallback reader for a specific malformation seen from qwen3.5-9b: every entry
# emitted into one object without `},{` between them. That parses cleanly —
# duplicate keys are legal JSON and the last one wins — so twenty judgements
# silently became one. Anything that reads model output as JSON needs a way to
# notice that it got less than it asked for.
_TRIPLE_RE = re.compile(
    r'"citation"\s*:\s*"(?P<citation>[^"]+)"\s*,\s*'
    r'"score"\s*:\s*(?P<score>\d+)\s*'
    r'(?:,\s*"element"\s*:\s*"(?P<element>[^"]*)")?'
)


def parse_scores(raw: str, expected: int = 0) -> list[dict]:
    """Rows of {citation, score, element} from a model reply.

    `expected` is the number of candidates sent. When strict JSON yields
    noticeably fewer rows than that, the flat scan is used instead: a reply
    holding one row for twenty candidates is a parse failure wearing the
    costume of a result.
    """
    text = _strip_thinking(raw).strip()
    fence = re.search(r"```(?:json)?\s*(.+?)\s*```", text, re.S)
    if fence:
        text = fence.group(1)

    rows: list[dict] = []
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        try:
            payload = json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            payload = None
        if isinstance(payload, dict):
            found = payload.get("scores")
            if isinstance(found, list):
                rows = [r for r in found if isinstance(r, dict)]

    if len(rows) >= max(expected, 1):
        return rows

    flat = [
        {
            "citation": m.group("citation"),
            "score": int(m.group("score")),
            "element": m.group("element") or "",
        }
        for m in _TRIPLE_RE.finditer(text)
    ]
    return flat if len(flat) > len(rows) else rows


class LlmReranker:
    """Reorders dense results by legal fit. Falls back to the dense order."""

    def __init__(self, llm=None, model: str | None = None):
        self._llm = llm
        self.model = model or LEGAL_RERANK_MODEL
        # Token counts and cost from the last call, for reporting.
        self.last_usage: dict = {}

    def llm(self):
        if self._llm is None:
            from .config import create_legal_chat_model

            self._llm = create_legal_chat_model(
                temperature=0.0, max_tokens=2048, model=self.model
            )
        return self._llm

    def rerank(self, narrative: str, hits: list, min_score: int = 1) -> tuple[list, str]:
        """Return (reordered hits, degraded reason).

        On any failure the dense order is returned unchanged: a worse ordering
        is recoverable, an exception in the middle of a query is not.
        """
        if not hits:
            return [], ""
        try:
            reply = self._ask(narrative, hits)
        except Exception as exc:  # noqa: BLE001
            return hits, f"LLM rerank ไม่สำเร็จ ใช้ลำดับเดิม: {exc}"

        rows = parse_scores(reply, expected=len(hits))
        if not rows:
            return hits, "อ่านผล LLM rerank ไม่ได้ ใช้ลำดับเดิม"

        by_citation = {h.citation: h for h in hits}
        dense_rank = {h.citation: i for i, h in enumerate(hits)}
        scored: list[tuple[int, int, object]] = []
        seen: set[str] = set()
        for row in rows:
            citation = str(row.get("citation", "")).strip()
            hit = by_citation.get(citation)
            # A citation the model invented or mangled has no hit behind it.
            if hit is None or citation in seen:
                continue
            seen.add(citation)
            try:
                value = int(row.get("score", 0))
            except (TypeError, ValueError):
                value = 0
            if value < min_score:
                continue
            hit.score = value / 3.0
            hit.element = str(row.get("element", ""))[:200]
            # Dense rank breaks ties, so the coarse 0-3 scale does not throw
            # away the ordering information retrieval already produced.
            scored.append((-value, dense_rank[citation], hit))

        if not scored:
            return [], "โมเดลประเมินว่าไม่มีมาตราใดเข้าองค์ประกอบ"
        scored.sort(key=lambda row: (row[0], row[1]))
        return [row[2] for row in scored], ""

    def _ask(self, narrative: str, hits) -> str:
        if self._llm is not None:
            return self._ask_injected(narrative, hits)
        return self._ask_openrouter(narrative, hits)

    def _ask_openrouter(self, narrative: str, hits) -> str:
        """Call OpenRouter directly so reasoning can be switched off.

        qwen3.5-9b thinks by default, and through the Anthropic-compatible shim
        the thinking is not reachable: it consumed the whole token budget and
        `content` came back empty on every request. OpenRouter's own endpoint
        takes `reasoning: {"enabled": false}`, after which the model answers in
        seven tokens instead of four thousand.
        """
        import json as _json
        import urllib.request

        from .config import CORE_LLM_OPENROUTER_BASE_URL, OPENROUTER_CYBERCASE

        if not OPENROUTER_CYBERCASE:
            raise RuntimeError("ไม่พบ OPENROUTER_CYBERCASE / OPENROUTER_API_KEY")
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_prompt(narrative, hits)},
            ],
            "temperature": 0,
            "max_tokens": 2048,
            "reasoning": {"enabled": False},
        }
        request = urllib.request.Request(
            f"{CORE_LLM_OPENROUTER_BASE_URL}/v1/chat/completions",
            data=_json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {OPENROUTER_CYBERCASE}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(request, timeout=180) as response:
            payload = _json.loads(response.read())
        self.last_usage = payload.get("usage", {})
        return payload["choices"][0]["message"].get("content") or ""

    def _ask_injected(self, narrative: str, hits) -> str:
        from langchain_core.messages import HumanMessage, SystemMessage

        response = self.llm().invoke(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=build_prompt(narrative, hits)),
            ]
        )
        content = getattr(response, "content", response)
        if isinstance(content, list):
            content = "".join(
                part.get("text", "") if isinstance(part, dict) else str(part)
                for part in content
            )
        return str(content)
