from __future__ import annotations

from copy import deepcopy
from typing import Any
from uuid import UUID

from app.services.case_analysis.contracts import (
    CaseAnalysisGap,
    CaseAnalysisResult as AnalysisOutput,
    CaseAnalysisTrace,
)


def trace_source_ids(trace: CaseAnalysisTrace) -> list[str]:
    ids: list[str] = []
    for claim in trace.claims:
        ids.extend(claim.supporting_source_ids)
        ids.extend(claim.contradicting_source_ids)
    return list(dict.fromkeys(ids))


def technical_augmentation(output: AnalysisOutput) -> dict[str, object] | None:
    receipt = output.execution_receipt
    value = receipt.get("technical_augmentation") if isinstance(receipt, dict) else None
    return value if isinstance(value, dict) else None


def mitre_table_from_output(output: AnalysisOutput) -> list[dict[str, object]]:
    value = (technical_augmentation(output) or {}).get("mitre_table", [])
    return [dict(item) for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def rag_invoked(augmentation: dict[str, object]) -> bool:
    applicability = augmentation.get("applicability")
    return isinstance(applicability, dict) and applicability.get("decision") == "RETRIEVE"


def rag_attempt(augmentation: dict[str, object]) -> dict[str, object]:
    status = augmentation.get("status")
    failure_code = augmentation.get("failure_code")
    status_map = {
        "not_applicable": "no_applicable_context",
        "insufficient_context": "no_applicable_context",
        "retrieved_without_supported_match": "no_applicable_context",
        "retrieved_with_matches": "used",
        "failed": "unavailable",
    }
    metadata: dict[str, object] = {
        "status": status_map.get(status, "no_applicable_context"),
    }
    if isinstance(failure_code, str):
        metadata["failure_code"] = failure_code
    return metadata


def augmentation_message_metadata(
    augmentation: dict[str, object],
    is_present: bool,
) -> dict[str, object]:
    if not is_present:
        return {}
    return {
        "mitre_table": deepcopy(augmentation.get("mitre_table", [])),
        "mitre_applicability": deepcopy(augmentation.get("applicability", {})),
        "rag_attempt": rag_attempt(augmentation),
        "technical_augmentation": deepcopy(augmentation),
    }


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
    result_id: UUID,
    clarification_id: UUID,
    snapshot_id: UUID,
    clarification_topic: str,
    gap_id: str,
    gap_key: str,
    thread_ordinal: int,
    augmentation_payload: dict[str, object],
    is_augmentation_present: bool,
    run_pipeline_config: dict[str, object],
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

    chat_followup: dict[str, object] = {
        "kind": "clarification",
        "action": "ask_followup",
        "root_ordinal": thread_ordinal,
        "round": 1,
        "selected_gap_detail": selected_gap_detail,
    }
    if isinstance(existing_followup, dict):
        for key in ("policy_version", "prompt_version", "provider", "model", "decision", "reason_code", "stop_reason"):
            if key in existing_followup:
                chat_followup[key] = existing_followup[key]

    return {
        "analysis_kind": "clarification_question",
        "analysis_result_id": str(result_id),
        "clarification_id": str(clarification_id),
        "evidence_snapshot_id": str(snapshot_id),
        "gap_id": gap_id,
        "gap_key": gap_key,
        "chat_followup": chat_followup,
        **augmentation_message_metadata(augmentation_payload, is_augmentation_present),
        "chat_action": {
            "action": "initial_analysis",
            "route": "analysis",
            "rag_invoked": rag_invoked(augmentation_payload),
            "retrieval_context_reused": False,
            "analysis_mode": "case_overview",
            "prompt_version": run_pipeline_config.get("version", "main_case_analysis_v1"),
        },
    }


def build_analysis_result_message_metadata(
    *,
    result_id: UUID,
    snapshot_id: UUID,
    trace: CaseAnalysisTrace,
    augmentation_payload: dict[str, object],
    is_augmentation_present: bool,
    run_pipeline_config: dict[str, object],
) -> dict[str, object]:
    return {
        "analysis_kind": "grounded_main_analysis",
        "analysis_state_scope": "canonical_case_overview",
        "canonical_case_state": True,
        "analysis_result_id": str(result_id),
        "evidence_snapshot_id": str(snapshot_id),
        "evidence_sha256": trace.evidence_sha256,
        "evidence_source_ids": trace_source_ids(trace),
        "analysis_trace": trace.model_dump(mode="json"),
        **augmentation_message_metadata(augmentation_payload, is_augmentation_present),
        "chat_action": {
            "action": "initial_analysis",
            "route": "analysis",
            "rag_invoked": rag_invoked(augmentation_payload),
            "retrieval_context_reused": False,
            "analysis_mode": "case_overview",
            "prompt_version": run_pipeline_config.get("version", "main_case_analysis_v1"),
        },
    }
