"""Deterministic follow-up decision engine, gap ranking, and metadata construction."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any
import unicodedata
from uuid import UUID

from app.config import settings
from app.services.case_analysis.contracts import CaseAnalysisGap, CaseAnalysisTrace
from app.services.followup.contracts import (
    FollowUpExchange,
    FollowUpResolution,
    answer_indicates_unavailable,
)


_PRIORITY_RANK = {"high": 0}

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

_GAP_REASON_CODES = {
    "NOT_PROVIDED": "material_incident_fact_missing",
    "AMBIGUOUS": "material_incident_fact_ambiguous",
    "CONFLICTING": "material_incident_fact_conflicting",
    "EXPLICITLY_UNKNOWN": "unresolved_gaps_recorded",
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


def normalize_question(question: str) -> str:
    normalized = unicodedata.normalize("NFKC", question)
    return " ".join(normalized.strip().split())


def resolve_gap_reason_code(gap: CaseAnalysisGap) -> str:
    return _GAP_REASON_CODES[gap.status]


def apply_followup_history(
    gaps: Sequence[CaseAnalysisGap],
    exchanges: Sequence[FollowUpExchange],
) -> tuple[CaseAnalysisGap, ...]:
    exhausted = exhausted_gap_keys(exchanges)
    unavailable = unavailable_gap_keys(exchanges)
    updated_gaps: list[CaseAnalysisGap] = []
    for gap in gaps:
        key = normalize_gap_key(gap.gap_key)
        if key not in exhausted:
            updated_gaps.append(gap)
            continue
        updates: dict[str, object] = {"askable": False}
        if key in unavailable and gap.status == "NOT_PROVIDED":
            updates["status"] = "EXPLICITLY_UNKNOWN"
        updated_gaps.append(gap.model_copy(update=updates))
    return tuple(updated_gaps)


def exhausted_gap_keys(
    exchanges: Sequence[FollowUpExchange],
) -> set[str]:
    return {
        key
        for exchange in exchanges
        if exchange.disposition in {"answered", "unavailable", "skipped"}
        for key in [exchange_gap_key(exchange)]
        if key is not None
    }


def unavailable_gap_keys(
    exchanges: Sequence[FollowUpExchange],
) -> set[str]:
    return {
        key
        for exchange in exchanges
        if exchange.disposition == "unavailable"
        or answer_indicates_unavailable(exchange.answer)
        for key in [exchange_gap_key(exchange)]
        if key is not None
    }


def exchange_gap_key(exchange: FollowUpExchange) -> str | None:
    if exchange.gap_key:
        return normalize_gap_key(exchange.gap_key)
    if exchange.gap_topic:
        return normalize_gap_key(exchange.gap_topic)
    return None


def has_claim_links(gap: CaseAnalysisGap) -> bool:
    return bool(gap.affected_claim_ids)


def select_followup_gap(
    gaps: Sequence[CaseAnalysisGap],
    exchanges: Sequence[FollowUpExchange],
) -> CaseAnalysisGap | None:
    exhausted = exhausted_gap_keys(exchanges)
    candidates: list[tuple[int, CaseAnalysisGap]] = [
        (index, gap)
        for index, gap in enumerate(gaps)
        if gap.priority in _PRIORITY_RANK
        and gap.askable
        and gap.status != "EXPLICITLY_UNKNOWN"
        and normalize_gap_key(gap.gap_key) not in exhausted
        and gap.clarification_question is not None
        and gap.clarification_question.strip()
    ]
    ranked = sorted(
        candidates,
        key=lambda item: (
            _PRIORITY_RANK[item[1].priority],
            0 if has_claim_links(item[1]) else 1,
            item[0],
        ),
    )
    for _, gap in ranked:
        return gap
    return None


def followup_context(gap: CaseAnalysisGap) -> dict[str, str]:
    return {
        "gap_id": gap.gap_id,
        "gap_topic": gap.topic,
        "gap_key": gap.gap_key,
    }


def gap_metadata(gap: CaseAnalysisGap) -> dict[str, Any]:
    detail = gap.model_dump(mode="json")
    detail["gap_key"] = gap.gap_key
    detail["followup_context"] = followup_context(gap)
    if gap.affected_claim_ids:
        detail["affects"] = (
            f"Clarifying {gap.topic.lower()} addresses missing investigative evidence for: "
            f"{', '.join(gap.affected_claim_ids)}."
        )
    else:
        detail["affects"] = (
            f"Clarifying this information helps establish facts and complete the case analysis for "
            f"{gap.topic.lower()}."
        )
    return detail


def followup_metadata(
    *,
    round_number: int,
    prior_exchange_count: int,
    source_revision: int,
    action: str,
    reason_code: str,
    selected_gap: CaseAnalysisGap | None = None,
) -> dict[str, Any]:
    return {
        "action": action,
        "chat_followup": {
            "round": round_number,
            "prior_exchange_count": prior_exchange_count,
            "source_revision": source_revision,
            "reason_code": reason_code,
            "gap": gap_metadata(selected_gap) if selected_gap else None,
        },
    }


async def evaluate_followup_outcome(
    *,
    followup_exchanges: Sequence[FollowUpExchange],
    followup_root_ordinal: int,
    source_run_id: UUID,
    source_revision: int,
    canonical_trace: CaseAnalysisTrace | None = None,
) -> FollowUpResolution:
    del followup_root_ordinal, source_run_id
    round_number = max(
        (exchange.round_number for exchange in followup_exchanges),
        default=0,
    ) + 1
    prior_exchange_count = len(followup_exchanges)

    def resolution(
        *,
        action: str,
        reason_code: str,
        selected_gap: CaseAnalysisGap | None = None,
        question: str | None = None,
    ) -> FollowUpResolution:
        return FollowUpResolution(
            question=question,
            metadata_json=followup_metadata(
                round_number=round_number,
                prior_exchange_count=prior_exchange_count,
                source_revision=source_revision,
                action=action,
                reason_code=reason_code,
                selected_gap=selected_gap,
            ),
        )

    if canonical_trace is None:
        return resolution(
            action="proceed",
            reason_code="canonical_state_unavailable",
        )

    canonical_gaps = apply_followup_history(
        canonical_trace.gaps,
        followup_exchanges,
    )
    if not settings.chat_followup_enabled:
        return resolution(
            action="proceed",
            reason_code="followup_disabled",
        )
    if round_number > settings.chat_followup_max_rounds:
        return resolution(
            action="proceed",
            reason_code="max_rounds_reached",
        )

    selected_gap = select_followup_gap(canonical_gaps, followup_exchanges)
    if selected_gap is None:
        return resolution(
            action="proceed",
            reason_code="no_eligible_high_priority_gap",
        )

    return resolution(
        action="follow_up",
        reason_code=_GAP_REASON_CODES[selected_gap.status],
        selected_gap=selected_gap,
        question=selected_gap.clarification_question.strip(),
    )


__all__ = [
    "apply_followup_history",
    "evaluate_followup_outcome",
    "exhausted_gap_keys",
    "followup_context",
    "followup_metadata",
    "gap_metadata",
    "normalize_gap_key",
    "normalize_question",
    "resolve_gap_reason_code",
    "select_followup_gap",
    "unavailable_gap_keys",
]
