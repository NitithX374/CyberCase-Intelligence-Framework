"""
Splitting an incident into the acts it is made of
=================================================
One case file describes several distinct acts, and each falls under a different
section. Embedded whole, they average into a vector that is near nothing in
particular: dense retrieval over a 700-character narrative returned everything
in a band of 0.47–0.51, and in one case พ.ร.บ.คอม ม.๕ and ม.๗ never appeared in
the top twenty at all. Reranking cannot repair that — it reorders what
retrieval found, and those sections were never found.

Retrieving per act fixes what reranking cannot. Hand-written sub-queries in
statutory form scored 0.55–0.61 against the same index where the raw narrative
scored 0.47–0.51, and where a section querying itself reaches 0.93. The ceiling
is high and the narrative is nowhere near it.

**On how the clauses are phrased.** A decomposer that writes "ผู้ใดเข้าถึงโดย
มิชอบซึ่งระบบคอมพิวเตอร์" has already decided the case: มิชอบ is an element of
the offence, not a fact in the file, and retrieval afterwards only confirms the
wording the model chose. The legal work would move here, invisibly, and the
suggestion would be the model's opinion wearing retrieval's clothes.

So the default style is `conduct`: describe what was done, concretely, in the
register statutes use, without asserting that it was unlawful. `legal` phrasing
is available because it is worth measuring, not because it is safe — and when
it is used the clauses must be shown to the reader, since that is where the
judgement was made.
"""

from __future__ import annotations

import json
import re

from .config import LEGAL_RERANK_MODEL

MAX_CLAUSES = 6

_STYLES = {
    "conduct": """คุณเป็นผู้ช่วยพนักงานสอบสวนไทย หน้าที่คือแยก "พฤติการณ์" ในสำนวนออกเป็นการกระทำย่อย ๆ ทีละอย่าง

กติกา:
1. แต่ละข้อ = การกระทำหนึ่งอย่าง เขียนเป็นประโยคเดียว สั้น ๆ
2. เขียนว่า "ทำอะไร กับอะไร" ตามข้อเท็จจริงในสำนวนเท่านั้น
3. ห้ามใส่คำตัดสินทางกฎหมาย เช่น "โดยมิชอบ" "โดยทุจริต" "ผิดกฎหมาย" — บรรยายการกระทำเฉย ๆ
4. ห้ามเดาสิ่งที่สำนวนไม่ได้เขียน
5. ใช้คำที่ตรงกับสิ่งที่เกิดขึ้น เช่น "ระบบคอมพิวเตอร์" "ข้อมูลคอมพิวเตอร์" แยกให้ถูกว่าอันไหน
6. ไม่เกิน 6 ข้อ เอาเฉพาะการกระทำที่สำคัญ

ตัวอย่างที่ดี: "เข้าใช้งานเซิร์ฟเวอร์ด้วยบัญชีของพนักงานที่ลาออกแล้ว"
ตัวอย่างที่ไม่ดี: "เข้าถึงระบบคอมพิวเตอร์โดยมิชอบ"  (มีคำตัดสิน "โดยมิชอบ")

ตอบ JSON เท่านั้น: {"acts":["...","..."]}""",
    "legal": """คุณเป็นผู้ช่วยนักกฎหมายไทย หน้าที่คือแปลงพฤติการณ์ในสำนวนเป็นข้อความแบบตัวบทกฎหมาย

กติกา:
1. แต่ละข้อ = การกระทำหนึ่งอย่าง เขียนขึ้นต้นด้วย "ผู้ใด"
2. ใช้ถ้อยคำแบบที่ตัวบทกฎหมายไทยใช้
3. แยกให้ชัดว่ากระทำต่อ "ระบบคอมพิวเตอร์" หรือ "ข้อมูลคอมพิวเตอร์"
4. ไม่เกิน 6 ข้อ

ตอบ JSON เท่านั้น: {"acts":["ผู้ใด...","ผู้ใด..."]}""",
}


def parse_acts(raw: str) -> list[str]:
    text = re.sub(r"<think>.*?</think>", "", raw or "", flags=re.S).strip()
    fence = re.search(r"```(?:json)?\s*(.+?)\s*```", text, re.S)
    if fence:
        text = fence.group(1)
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        try:
            payload = json.loads(text[start : end + 1])
            acts = payload.get("acts")
            if isinstance(acts, list):
                return [str(a).strip() for a in acts if str(a).strip()]
        except json.JSONDecodeError:
            pass
    # Same lesson as the reranker: read what is there rather than nothing.
    return [m.group(1).strip() for m in re.finditer(r'"\s*([^"]{12,300}?)\s*"', text)][:MAX_CLAUSES]


class LegalDecomposer:
    """Turns one narrative into several retrievable acts."""

    def __init__(self, llm=None, model: str | None = None, style: str = "conduct"):
        self._llm = llm
        self.model = model or LEGAL_RERANK_MODEL
        if style not in _STYLES:
            raise ValueError(f"style must be one of {sorted(_STYLES)}")
        self.style = style
        self.last_usage: dict = {}

    def decompose(self, narrative: str, max_clauses: int = MAX_CLAUSES) -> tuple[list[str], str]:
        """Return (clauses, degraded). Falls back to the whole narrative."""
        try:
            reply = self._ask(narrative)
        except Exception as exc:  # noqa: BLE001
            return [narrative], f"แตกพฤติการณ์ไม่สำเร็จ ใช้สำนวนทั้งก้อน: {exc}"
        acts = parse_acts(reply)[:max_clauses]
        if not acts:
            return [narrative], "อ่านผลการแตกพฤติการณ์ไม่ได้ ใช้สำนวนทั้งก้อน"
        return acts, ""

    def _ask(self, narrative: str) -> str:
        if self._llm is not None:
            from langchain_core.messages import HumanMessage, SystemMessage

            response = self._llm.invoke(
                [
                    SystemMessage(content=_STYLES[self.style]),
                    HumanMessage(content=f"สำนวนคดี:\n{narrative.strip()}"),
                ]
            )
            content = getattr(response, "content", response)
            return str(content)

        import json as _json
        import urllib.request

        from .config import CORE_LLM_OPENROUTER_BASE_URL, OPENROUTER_CYBERCASE

        if not OPENROUTER_CYBERCASE:
            raise RuntimeError("ไม่พบ OPENROUTER_CYBERCASE / OPENROUTER_API_KEY")
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": _STYLES[self.style]},
                {"role": "user", "content": f"สำนวนคดี:\n{narrative.strip()}"},
            ],
            "temperature": 0,
            "max_tokens": 1024,
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
        with urllib.request.urlopen(request, timeout=120) as response:
            payload = _json.loads(response.read())
        self.last_usage = payload.get("usage", {})
        return payload["choices"][0]["message"].get("content") or ""


def merge_results(per_clause: list[list], limit: int) -> list:
    """Interleave one ranked list per act, best of each first.

    Round-robin rather than by score: the scores come from different queries and
    are not comparable, and taking the global maximum would let one vividly
    described act crowd out the others — which is the failure that splitting the
    narrative was meant to fix.
    """
    merged: list = []
    seen: set[str] = set()
    for rank in range(max((len(rows) for rows in per_clause), default=0)):
        for rows in per_clause:
            if rank >= len(rows):
                continue
            hit = rows[rank]
            if hit.citation in seen:
                continue
            seen.add(hit.citation)
            merged.append(hit)
            if len(merged) >= limit:
                return merged
    return merged
