"""
Legal suggestion generation
===========================
Turns retrieved sections into suggestions a prosecutor can act on.

The central decision here is what the model is allowed to produce. It is asked
only to **choose** among sections already retrieved and to explain, in terms of
the facts of the case, why each might apply. It never writes the text of the
law: the verbatim wording is inserted afterwards from the Qdrant payload,
keyed by the section the model picked. Paraphrasing a statute is therefore not
something the model is trusted not to do — it is something it has no route to
do. A model that invents "มาตรา ๙๙" simply fails the lookup and is dropped.

The hedge is applied the same way. "อาจเข้าข่าย …" is written by
`_headline`, not by the model, so it cannot be dropped, softened or reworded
into a finding of guilt. The model's prose is additionally screened for
assertions of guilt, and a suggestion whose reasoning asserts one is kept but
its reasoning replaced — losing an explanation is better than publishing a
verdict.

Suggestions are limited to sections whose role is `offence`. Only those are
chargeable; a `procedural` or `administrative` section put forward as a charge
sends a prosecutor to the wrong forum.
"""

from __future__ import annotations

import json
import re
from datetime import date
from typing import Any, Sequence

from .retriever import LegalHit, LegalRetrievalResult
from .schema import LegalResult, LegalSectionRef, LegalSuggestion

MAX_SUGGESTIONS = 5

# Phrases that state guilt rather than raise a possibility. Screened out of
# model prose; the system's own hedge stays in the headline regardless.
_VERDICT_PATTERNS = (
    "มีความผิดตามมาตรา",
    "มีความผิดฐาน",
    "ผิดมาตรา",
    "เป็นความผิดตามมาตรา",
    "ต้องรับโทษตามมาตรา",
    "จำเลยมีความผิด",
    "ผู้ต้องหามีความผิด",
)

SYSTEM_PROMPT = """คุณเป็นผู้ช่วยพนักงานอัยการไทย มีหน้าที่ "เสนอแนะ" ว่าพฤติการณ์ในสำนวนอาจเข้าข่ายมาตราใด

กติกาที่ห้ามละเมิด:
1. เลือกเฉพาะมาตราจากรายการที่ให้มาเท่านั้น ห้ามอ้างมาตราที่ไม่มีในรายการเด็ดขาด
2. ห้ามเขียนหรือสรุปความตัวบทกฎหมายเอง ระบบจะใส่ตัวบทให้เอง คุณเขียนได้เฉพาะ "เหตุผล" ที่อ้างอิงข้อเท็จจริงในสำนวน
3. เขียนเป็นความเป็นไปได้เสมอ ("พฤติการณ์...อาจเข้าข่าย") ห้ามฟันธงว่าผิด
4. ห้ามระบุอัตราโทษ จำนวนปี หรือจำนวนเงินค่าปรับ
5. ถ้าไม่มีมาตราใดเข้าข่ายเลย ให้คืนรายการว่าง

ตอบเป็น JSON เท่านั้น:
{"suggestions":[{"citation":"<คัดลอกจากรายการให้ตรงทุกตัวอักษร>","reasoning":"<เหตุผลจากข้อเท็จจริง 1-3 ประโยค>"}]}"""


def _headline(hit: LegalHit) -> str:
    """System-written, always hedged. Never model output."""
    return f"อาจเข้าข่าย {hit.citation}"


def _date_warning(hit: LegalHit, incident_date: date | None) -> str:
    if incident_date is None or not hit.effective_from:
        if not hit.effective_from:
            return "ไม่ทราบวันบังคับใช้ที่แน่นอน ต้องตรวจสอบก่อนใช้อ้างอิง"
        return ""
    try:
        effective = date.fromisoformat(hit.effective_from)
    except ValueError:
        return ""
    if effective > incident_date:
        return (
            f"มาตรานี้ใช้บังคับ {hit.effective_from} ซึ่งหลังวันเกิดเหตุ "
            f"{incident_date.isoformat()} — ต้องใช้ฉบับที่ใช้บังคับขณะเกิดเหตุ"
        )
    return ""


def _to_ref(hit: LegalHit, incident_date: date | None) -> LegalSectionRef:
    return LegalSectionRef(
        citation=hit.citation,
        act_label=hit.act_label,
        section_number=hit.number,
        text=hit.text,
        hierarchy=hit.hierarchy,
        verified_by_human=hit.verified_by_human,
        verification=hit.verification,
        penalties_quotable=hit.penalties_reliable,
        effective_from=hit.effective_from,
        effective_note=hit.effective_note,
        date_warning=_date_warning(hit, incident_date),
        source_url=hit.source_url,
    )


def _screen(reasoning: str) -> str:
    """Drop prose that states guilt instead of raising a possibility."""
    text = " ".join((reasoning or "").split())
    if not text:
        return ""
    if any(pattern in text for pattern in _VERDICT_PATTERNS):
        return "(ระบบตัดคำอธิบายออก เนื่องจากเขียนในลักษณะชี้ขาดว่ามีความผิด)"
    # A penalty figure must never appear in generated prose; the reliable ones
    # are already in the quoted text and the unreliable ones are removed.
    if re.search(r"(จำคุก|ปรับ)[^\n]{0,20}(ปี|เดือน|บาท)", text):
        return "(ระบบตัดคำอธิบายออก เนื่องจากมีการระบุอัตราโทษ)"
    return text


def build_prompt(
    narrative: str,
    hits: Sequence[LegalHit],
    mitre_table: Sequence[Any] | None = None,
) -> str:
    """The user turn: the facts, the techniques, and the candidate sections."""
    lines = [f"สำนวนคดี:\n{narrative.strip()}", ""]

    if mitre_table:
        rows = []
        for row in list(mitre_table)[:8]:
            get = row.get if isinstance(row, dict) else (lambda k, r=row: getattr(r, k, ""))
            name, tid = get("name"), get("technique_id")
            if name:
                rows.append(f"- {name}" + (f" ({tid})" if tid else ""))
        if rows:
            lines += ["เทคนิค MITRE ATT&CK ที่ตรวจพบในเหตุการณ์นี้:", *rows, ""]

    lines.append("มาตราที่ค้นได้ (เลือกจากรายการนี้เท่านั้น):")
    for hit in hits:
        body = " ".join(hit.text.split())
        lines.append(f'\n[{hit.citation}]\n{body[:900]}')
    return "\n".join(lines)


def _parse_response(raw: str) -> list[dict]:
    """Pull the JSON object out of a model reply, tolerating code fences."""
    text = (raw or "").strip()
    fence = re.search(r"```(?:json)?\s*(.+?)\s*```", text, re.S)
    if fence:
        text = fence.group(1)
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        return []
    try:
        payload = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return []
    items = payload.get("suggestions")
    return [i for i in items if isinstance(i, dict)] if isinstance(items, list) else []


class LegalGenerator:
    """Selects and explains. The chat model is injected by the service."""

    def __init__(self, llm=None):
        self._llm = llm

    def llm(self):
        if self._llm is None:
            from .config import create_legal_chat_model

            self._llm = create_legal_chat_model()
        return self._llm

    def generate(
        self,
        narrative: str,
        retrieval: LegalRetrievalResult,
        mitre_table: Sequence[Any] | None = None,
        incident_date: date | None = None,
        max_suggestions: int = MAX_SUGGESTIONS,
    ) -> LegalResult:
        """Never raises. Every failure path returns an empty, explained result."""
        chargeable = [h for h in retrieval.hits if h.chargeable]
        if not chargeable:
            return LegalResult(
                degraded=retrieval.degraded or "ไม่พบมาตราที่เป็นฐานความผิดจากการค้นหา",
                contains_unverified=False,
            )

        try:
            reply = self._ask(narrative, chargeable, mitre_table)
        except Exception as exc:  # noqa: BLE001 — losing the statute must not lose MITRE
            return LegalResult(degraded=f"เรียกโมเดลไม่สำเร็จ: {exc}")

        by_citation = {h.citation: h for h in chargeable}
        related_by_section = {c.citation: c for c in retrieval.context}
        technique_names = _technique_names(mitre_table)

        suggestions: list[LegalSuggestion] = []
        for item in _parse_response(reply):
            citation = str(item.get("citation", "")).strip()
            hit = by_citation.get(citation)
            # A citation the model invented has no entry, and is dropped here
            # rather than reaching a prosecutor with no text behind it.
            if hit is None:
                continue
            suggestions.append(
                LegalSuggestion(
                    headline=_headline(hit),
                    section=_to_ref(hit, incident_date),
                    reasoning=_screen(str(item.get("reasoning", ""))),
                    from_techniques=technique_names,
                    related=[
                        _to_ref(related_by_section[c], incident_date)
                        for c in _cited_citations(hit, related_by_section)
                    ],
                )
            )
            if len(suggestions) >= max_suggestions:
                break

        if not suggestions:
            return LegalResult(degraded="โมเดลไม่ได้เลือกมาตราใดจากรายการที่ค้นได้")
        return LegalResult(
            suggestions=suggestions,
            degraded=retrieval.degraded,
            contains_unverified=any(
                not s.section.verified_by_human for s in suggestions
            ),
        )

    def _ask(self, narrative, hits, mitre_table) -> str:
        from langchain_core.messages import HumanMessage, SystemMessage

        response = self.llm().invoke(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=build_prompt(narrative, hits, mitre_table)),
            ]
        )
        content = getattr(response, "content", response)
        if isinstance(content, list):  # some providers return content blocks
            content = "".join(
                part.get("text", "") if isinstance(part, dict) else str(part)
                for part in content
            )
        return str(content)


def _technique_names(mitre_table: Sequence[Any] | None) -> list[str]:
    if not mitre_table:
        return []
    out = []
    for row in list(mitre_table)[:8]:
        get = row.get if isinstance(row, dict) else (lambda k, r=row: getattr(r, k, ""))
        name, tid = get("name"), get("technique_id")
        if name:
            out.append(f"{name} ({tid})" if tid else str(name))
    return out


def _cited_citations(hit: LegalHit, available: dict[str, LegalSectionRef]) -> list[str]:
    wanted = [f"{hit.act_label} มาตรา {number}" for number in hit.cites]
    return [c for c in wanted if c in available]
