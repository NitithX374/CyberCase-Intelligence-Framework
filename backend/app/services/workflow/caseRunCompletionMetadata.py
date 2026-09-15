from __future__ import annotations

from copy import deepcopy

from app.services.case_analysis.contracts import (
    CaseAnalysisGap,
    CaseAnalysisResult as AnalysisOutput,
    CaseAnalysisTrace,
)


def technical_augmentation(output: AnalysisOutput) -> dict[str, object] | None:
    receipt = output.execution_receipt
    value = receipt.get("technical_augmentation") if isinstance(receipt, dict) else None
    return value if isinstance(value, dict) else None


def mitre_table_from_output(output: AnalysisOutput) -> list[dict[str, object]]:
    value = (technical_augmentation(output) or {}).get("mitre_table", [])
    return [dict(item) for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def build_clarification_metadata(
    output: AnalysisOutput,
    trace: CaseAnalysisTrace,
) -> dict[str, object]:
    metadata = deepcopy(output.followup_metadata or {})
    if not metadata.get("gap_id") or not metadata.get("topic") or not metadata.get("gap_key"):
        gap = next((item for item in trace.gaps if item.askable), None)
        if gap is not None:
            metadata.setdefault("gap_id", gap.gap_id)
            metadata.setdefault("topic", gap.topic)
            metadata.setdefault("gap_key", f"{gap.gap_id}:{gap.topic.strip().lower()}")
    return metadata


def build_selected_gap_detail(
    clarification_topic: str,
    gap: CaseAnalysisGap | None,
    existing_detail: dict[str, object] | None = None,
) -> dict[str, object]:
    existing = existing_detail or {}
    topic = str(existing.get("topic") or (gap.topic if gap else clarification_topic)).strip()
    status = str(existing.get("status") or (gap.status if gap else "NOT_PROVIDED"))
    if status not in {"NOT_PROVIDED", "EXPLICITLY_UNKNOWN", "AMBIGUOUS", "CONFLICTING"}:
        status = "NOT_PROVIDED"
    description = str(
        existing.get("description")
        or (gap.description if gap else f"Additional investigative information is required for {topic}.")
    ).strip()
    reason = str(
        existing.get("reason")
        or (gap.reason if gap else f"Clarifying {topic.lower()} is required to substantiate findings.")
    ).strip()

    raw_affects = str(existing.get("affects") or "").strip()
    if raw_affects and raw_affects != "case-level context" and not raw_affects.startswith("A-"):
        affects = raw_affects
    elif gap and gap.affected_claim_ids:
        affects = f"Clarifying {topic.lower()} addresses missing investigative evidence for: {', '.join(gap.affected_claim_ids)}."
    elif raw_affects:
        affects = f"Clarifying {topic.lower()} addresses missing investigative evidence for: {raw_affects}."
    else:
        affects = f"Clarifying this information helps establish facts and complete the case analysis for {topic.lower()}."

    priority = str(existing.get("priority") or (gap.priority if gap else "high")).lower()
    if priority not in {"high", "medium", "low"}:
        priority = "high"

    askable = bool(existing.get("askable", gap.askable if gap else True))

    return {
        "topic": topic,
        "status": status,
        "description": description,
        "affects": affects,
        "reason": reason,
        "priority": priority,
        "askable": askable,
    }


def build_followup_message_metadata(
    *,
    clarification_topic: str,
    gap_id: str,
    gap_key: str,
    thread_ordinal: int,
    trace: CaseAnalysisTrace,
    existing_followup: dict[str, object] | None = None,
) -> dict[str, object]:
    gap = next(
        (
            item for item in trace.gaps
            if item.gap_id == gap_id or item.topic.strip().lower() == clarification_topic.strip().lower()
        ),
        next((item for item in trace.gaps if item.askable), None),
    )
    existing_detail = existing_followup.get("selected_gap_detail") if isinstance(existing_followup, dict) else None
    existing_detail_dict = existing_detail if isinstance(existing_detail, dict) else None
    selected_gap_detail = build_selected_gap_detail(clarification_topic, gap, existing_detail_dict)
    topic = str(selected_gap_detail["topic"])

    chat_followup: dict[str, object] = {
        "root_ordinal": thread_ordinal,
        "round": 1,
        "gap_id": gap_id,
        "gap_key": gap_key,
        "topic": topic,
        "selected_gap_detail": selected_gap_detail,
    }

    return {
        "action": "follow_up",
        "chat_followup": chat_followup,
    }


__all__ = [
    "build_clarification_metadata",
    "build_followup_message_metadata",
    "mitre_table_from_output",
    "technical_augmentation",
]
