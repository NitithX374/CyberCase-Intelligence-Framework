from __future__ import annotations

import unicodedata
from collections.abc import Sequence

from app.services.case_analysis.contracts import CaseAnalysisGap
from app.services.followup.contracts import answer_indicates_unavailable
from app.services.followup.contracts import ClarificationExchange


_PRIORITY_RANK = {"high": 0, "medium": 1}
_THAI_INCIDENT_TIME_KEYS = {
    "เวลาเกิดเหตุ",
    "เวลาที่เกิดเหตุ",
    "เวลาของเหตุการณ์",
    "ช่วงเวลาเกิดเหตุ",
    "ช่วงเวลาที่เกิดเหตุ",
    "ช่วงเวลาของเหตุการณ์",
}
_ENGLISH_INCIDENT_TIME_KEYS = {
    "event time",
    "incident time",
    "the incident time",
    "time of event",
    "time of incident",
    "time of the event",
    "time of the incident",
}
_THAI_CCTV_IDENTITY_KEYS = {
    "การระบุตัวบุคคลในภาพกล้อง",
    "ตัวบุคคลในภาพกล้อง",
    "บุคคลในภาพกล้อง",
    "อัตลักษณ์บุคคลในภาพกล้อง",
}
_ENGLISH_CCTV_IDENTITY_KEYS = {
    "cctv subject identity",
    "identity in cctv",
    "identity of cctv subject",
    "identity of person in cctv footage",
    "person in cctv",
}


def normalize_gap_key(topic: str) -> str:
    normalized = unicodedata.normalize("NFKC", topic).casefold()
    normalized = "".join(
        " " if unicodedata.category(character).startswith("P") else character
        for character in normalized
    )
    normalized = " ".join(normalized.split())
    compact = normalized.replace(" ", "")
    if compact in _THAI_INCIDENT_TIME_KEYS:
        return "topic:incident-time"
    if normalized in _ENGLISH_INCIDENT_TIME_KEYS:
        return "topic:incident-time"
    if compact in _THAI_CCTV_IDENTITY_KEYS:
        return "topic:cctv-subject-identity"
    if normalized in _ENGLISH_CCTV_IDENTITY_KEYS:
        return "topic:cctv-subject-identity"
    return f"topic:{normalized}"


def apply_clarification_history(
    gaps: Sequence[CaseAnalysisGap],
    exchanges: Sequence[ClarificationExchange],
) -> tuple[CaseAnalysisGap, ...]:
    exhausted = exhausted_gap_keys(exchanges)
    unavailable = unavailable_gap_keys(exchanges)
    updated_gaps: list[CaseAnalysisGap] = []
    for gap in gaps:
        key = normalize_gap_key(gap.topic)
        if key not in exhausted:
            updated_gaps.append(gap)
            continue
        updates: dict[str, object] = {"askable": False}
        if key in unavailable and gap.status == "NOT_PROVIDED":
            updates["status"] = "EXPLICITLY_UNKNOWN"
        updated_gaps.append(gap.model_copy(update=updates))
    return tuple(updated_gaps)


def exhausted_gap_keys(
    exchanges: Sequence[ClarificationExchange],
) -> set[str]:
    return {
        key
        for exchange in exchanges
        if exchange.answer.strip()
        for key in [exchange_gap_key(exchange)]
        if key is not None
    }


def unavailable_gap_keys(
    exchanges: Sequence[ClarificationExchange],
) -> set[str]:
    return {
        key
        for exchange in exchanges
        if answer_indicates_unavailable(exchange.answer)
        for key in [exchange_gap_key(exchange)]
        if key is not None
    }


def select_next_gap(
    gaps: Sequence[CaseAnalysisGap],
    exchanges: Sequence[ClarificationExchange],
) -> CaseAnalysisGap | None:
    exhausted = exhausted_gap_keys(exchanges)
    candidates = [
        (index, gap)
        for index, gap in enumerate(gaps)
        if gap.priority in _PRIORITY_RANK
        and gap.askable
        and gap.status != "EXPLICITLY_UNKNOWN"
        and normalize_gap_key(gap.topic) not in exhausted
    ]
    if not candidates:
        return None
    return min(
        candidates,
        key=lambda item: (
            _PRIORITY_RANK[item[1].priority],
            0 if has_claim_links(item[1]) else 1,
            item[0],
        ),
    )[1]


def followup_context(
    gap: CaseAnalysisGap,
) -> dict[str, str]:
    context = {
        "gap_id": gap.gap_id,
        "gap_topic": gap.topic,
        "gap_key": normalize_gap_key(gap.topic),
    }
    return context


def exchange_gap_key(exchange: ClarificationExchange) -> str | None:
    if exchange.gap_key:
        return exchange.gap_key
    if exchange.gap_topic:
        return normalize_gap_key(exchange.gap_topic)
    return None


def has_claim_links(gap: CaseAnalysisGap) -> bool:
    return bool(gap.affected_claim_ids)


__all__ = [
    "apply_clarification_history",
    "exhausted_gap_keys",
    "followup_context",
    "normalize_gap_key",
    "select_next_gap",
    "unavailable_gap_keys",
]
