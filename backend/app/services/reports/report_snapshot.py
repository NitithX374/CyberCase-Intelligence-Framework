from __future__ import annotations

from datetime import datetime, timezone

from app.models.chat import ChatMessage, ChatThread
from app.models.rag_context import RagContext
from app.services.chat.raw_evidence import build_raw_evidence_snapshot
from app.services.reports.report_contracts import (
    AdmittedMitreRow,
    ReportGenerationConflict,
    ReportInputSnapshot,
    ReportSourceMessage,
)


def build_current_report_snapshot(
    thread: ChatThread,
    *,
    rag_context: RagContext | None = None,
) -> ReportInputSnapshot:
    messages = sorted(list(thread.messages), key=lambda message: message.ordinal)
    evidence = build_raw_evidence_snapshot(messages)
    if not evidence.text:
        raise ReportGenerationConflict(
            "report_evidence_missing",
            "User-authored case evidence is required before generating a report.",
        )
    analysis_message = _analysis_message(messages)
    if analysis_message is None:
        raise ReportGenerationConflict(
            "report_analysis_missing",
            "A completed main analysis is required before generating a report.",
        )
    source_ids = set(evidence.source_message_ids)
    source_messages: list[ReportSourceMessage] = []
    for message in messages:
        if message.id not in source_ids:
            continue
        kind = message.metadata_json.get("evidence_kind")
        if kind not in {
            "initial_case_narrative",
            "clarification_answer",
            "added_case_information",
        }:
            kind = "initial_case_narrative" if not source_messages else "added_case_information"
        source_messages.append(
            ReportSourceMessage(
                message_id=message.id,
                ordinal=message.ordinal,
                evidence_kind=kind,
                content=message.content,
            )
        )
    metadata = analysis_message.metadata_json
    trace = metadata.get("analysis_trace")
    active_rag_context = _active_rag_context(analysis_message, rag_context)
    return ReportInputSnapshot(
        thread_id=thread.id,
        thread_title=thread.title,
        created_at=datetime.now(timezone.utc),
        source_messages=source_messages,
        evidence_sha256=evidence.sha256,
        analysis_message_id=analysis_message.id,
        analysis_answer=analysis_message.content,
        analysis_trace=trace if isinstance(trace, dict) else None,
        retrieval_context_id=(
            active_rag_context.retrieval_context_id if active_rag_context else None
        ),
        mitre_rows=_mitre_rows(active_rag_context.mitre_table if active_rag_context else []),
        unresolved_issues=_unresolved_issues(metadata),
    )


def _analysis_message(
    messages: list[ChatMessage],
) -> ChatMessage | None:
    candidates = [
        message
        for message in messages
        if message.role == "assistant"
        and message.metadata_json.get("analysis_kind") == "grounded_main_analysis"
    ]
    return candidates[-1] if candidates else None


def _active_rag_context(
    analysis_message: ChatMessage,
    rag_context: RagContext | None,
) -> RagContext | None:
    if rag_context is None:
        return None
    if analysis_message.retrieval_context_id != rag_context.retrieval_context_id:
        return None
    return rag_context


def _mitre_rows(value: object) -> list[AdmittedMitreRow]:
    if not isinstance(value, list):
        return []
    rows: list[AdmittedMitreRow] = []
    for raw in value:
        if not isinstance(raw, dict):
            continue
        identifier = raw.get("technique_id") or raw.get("external_id") or raw.get("id")
        if not isinstance(identifier, str) or not identifier.startswith("T"):
            continue
        rows.append(
            AdmittedMitreRow(
                technique_id=identifier,
                name=str(raw.get("name") or raw.get("technique_name") or ""),
                reason=str(raw.get("reason") or raw.get("caseAssociationReason") or ""),
                tactic=str(raw.get("tactic") or ""),
                description=str(raw.get("description") or ""),
            )
        )
    return rows


def _unresolved_issues(metadata: dict[str, object]) -> list[str]:
    followup = metadata.get("chat_followup")
    if not isinstance(followup, dict):
        return []
    gap_analysis = followup.get("gap_analysis")
    if not isinstance(gap_analysis, dict):
        return []
    gaps = gap_analysis.get("gaps")
    if not isinstance(gaps, list):
        return []
    return [
        str(gap.get("description"))
        for gap in gaps
        if isinstance(gap, dict) and gap.get("description")
    ]


__all__ = ["build_current_report_snapshot"]
