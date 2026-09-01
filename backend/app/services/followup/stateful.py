from __future__ import annotations

import re
import unicodedata
from collections.abc import Mapping, Sequence

from app.services.case_analysis.contracts import (
    AnalysisGapV3,
    AnalysisTraceV3,
)
from app.services.followup.contracts import answer_indicates_unavailable
from app.services.followup.schemas import ClarificationExchange, GapAnalysis, GapItem


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
    analysis: GapAnalysis,
    exchanges: Sequence[ClarificationExchange],
) -> GapAnalysis:
    exhausted = exhausted_gap_keys(exchanges)
    unavailable = unavailable_gap_keys(exchanges)
    gaps: list[GapItem] = []
    for gap in analysis.gaps:
        key = normalize_gap_key(gap.topic)
        if key not in exhausted:
            gaps.append(gap)
            continue
        payload = gap.model_dump(mode="json")
        payload["askable"] = False
        if key in unavailable and gap.status == "NOT_PROVIDED":
            payload["status"] = "EXPLICITLY_UNKNOWN"
        gaps.append(GapItem.model_validate(payload))
    return GapAnalysis(gaps=gaps)


def exhausted_gap_keys(
    exchanges: Sequence[ClarificationExchange],
) -> set[str]:
    return {
        key
        for exchange in exchanges
        if exchange.answer.strip()
        for key in [_exchange_gap_key(exchange)]
        if key is not None
    }


def unavailable_gap_keys(
    exchanges: Sequence[ClarificationExchange],
) -> set[str]:
    return {
        key
        for exchange in exchanges
        if answer_indicates_unavailable(exchange.answer)
        for key in [_exchange_gap_key(exchange)]
        if key is not None
    }


def select_next_gap(
    gaps: Sequence[AnalysisGapV3 | GapItem],
    exchanges: Sequence[ClarificationExchange],
) -> AnalysisGapV3 | GapItem | None:
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
            0 if _has_claim_links(item[1]) else 1,
            item[0],
        ),
    )[1]


def policy_gap(gap: AnalysisGapV3 | GapItem) -> GapItem:
    if isinstance(gap, GapItem):
        return gap
    return GapItem(
        topic=gap.topic,
        status=gap.status,
        description=gap.description,
        affects=", ".join(gap.affected_claim_ids) or "case-level context",
        reason=gap.reason,
        priority=gap.priority,
        askable=gap.askable,
    )


def relevant_claim_context(
    trace: AnalysisTraceV3,
    gap: AnalysisGapV3,
) -> dict[str, object]:
    affected = set(gap.affected_claim_ids)
    return {
        "relevant_claims": [
            {
                "claim_id": claim.claim_id,
                "text": claim.text,
                "epistemic_status": claim.epistemic_status,
            }
            for claim in trace.claims
            if claim.claim_id in affected
        ]
    }


def followup_context(
    gap: AnalysisGapV3 | GapItem,
    *,
    evidence_sha256: str | None,
) -> dict[str, str]:
    context = {
        "gap_topic": gap.topic,
        "gap_key": normalize_gap_key(gap.topic),
    }
    gap_id = gap.gap_id if isinstance(gap, AnalysisGapV3) else None
    if gap_id is not None:
        context["gap_id"] = gap_id
    if evidence_sha256 is not None:
        context["evidence_sha256"] = evidence_sha256
    return context


def clarification_answer_context(
    question_message_id: str,
    context: Mapping[str, object],
) -> dict[str, str]:
    output = {"question_message_id": question_message_id}
    mapping = {
        "gap_id": "answered_gap_id",
        "gap_topic": "answered_gap_topic",
        "gap_key": "answered_gap_key",
        "evidence_sha256": "question_evidence_sha256",
    }
    for source, target in mapping.items():
        value = context.get(source)
        if isinstance(value, str) and value:
            output[target] = value
    return output


def _exchange_gap_key(exchange: ClarificationExchange) -> str | None:
    if exchange.gap_key:
        return exchange.gap_key
    if exchange.gap_topic:
        return normalize_gap_key(exchange.gap_topic)
    return None


def _has_claim_links(gap: AnalysisGapV3 | GapItem) -> bool:
    if isinstance(gap, AnalysisGapV3):
        return bool(gap.affected_claim_ids)
    return bool(re.search(r"(?<![A-Z0-9])A-\d{2,}(?![A-Z0-9])", gap.affects))


__all__ = [
    "apply_clarification_history",
    "clarification_answer_context",
    "exhausted_gap_keys",
    "followup_context",
    "normalize_gap_key",
    "policy_gap",
    "relevant_claim_context",
    "select_next_gap",
    "unavailable_gap_keys",
]
