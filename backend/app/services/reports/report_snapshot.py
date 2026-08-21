from __future__ import annotations;

from typing import Any
from uuid import UUID

from app.models.chat import ChatMessage, ChatThread
from app.models.rag_context import RagContext
from app.schemas.rag import MitreTableRow
from app.services.extraction.llm_extraction import (
    EXTRACTION_METADATA_KEY,
    build_extraction_input,
    normalize_case_state,
)
from app.services.reports.report_contracts import (
    AdmittedMitreRow,
    ReportInputSnapshot,
    ReportSourceMessage,
)
from app.services.reports.report_errors import ReportGenerationConflict
from app.services.reports.report_generation import MITRE_ID_RE

def build_current_report_snapshot(
    thread: ChatThread,
    *,
    current_case_state_json: dict[str, object] | None = None,
    rag_context: RagContext | None = None,
    case_state_version_id: UUID | None = None,
) -> ReportInputSnapshot:
    """Build the only report input admitted by the current chat state.

    The server derives provenance from persisted rows. Assistant content is used
    only to find the terminal answer and its structured metadata; it is never
    copied into the report model input.
    """

    ordered_messages = sorted(thread.messages, key=lambda message: message.ordinal)
    if not ordered_messages:
        raise ReportGenerationConflict(
            "report_empty_thread",
            "Send and complete a chat message before generating a report.",
        )

    if thread.status not in {"idle", "answered"}:
        code_by_status = {
            "processing": "report_chat_processing",
            "awaiting_followup": "report_followup_pending",
            "failed": "report_chat_failed",
        }
        raise ReportGenerationConflict(
            code_by_status.get(thread.status, "report_thread_not_ready"),
            {
                "processing": "Wait for the chat response to finish before generating a report.",
                "awaiting_followup": "Answer the pending clarification before generating a report.",
                "failed": "Resolve the failed chat response before generating a report.",
            }.get(thread.status, "The chat is not ready for report generation."),
        )

    latest_assistant = next(
        (
            message
            for message in reversed(ordered_messages)
            if message.role == "assistant"
        ),
        None,
    )
    if latest_assistant is None or not _is_terminal_assistant(latest_assistant):
        raise ReportGenerationConflict(
            "report_terminal_answer_missing",
            "Complete a terminal assistant answer before generating a report.",
        )

    extraction_assistant = next(
        (
            message
            for message in reversed(ordered_messages)
            if message.role == "assistant"
            and _is_terminal_assistant(message)
            and isinstance(
                _metadata_dict(message.metadata_json).get(EXTRACTION_METADATA_KEY),
                dict,
            )
        ),
        None,
    )
    if extraction_assistant is None:
        raise ReportGenerationConflict(
            "report_extraction_missing",
            "A validated baseline extraction is required before generating a report.",
        )

    latest_metadata = _metadata_dict(latest_assistant.metadata_json)
    metadata = _metadata_dict(extraction_assistant.metadata_json)
    extraction_metadata = metadata.get(EXTRACTION_METADATA_KEY)
    if not isinstance(extraction_metadata, dict):
        raise ReportGenerationConflict(
            "report_extraction_missing",
            "A validated baseline extraction is required before generating a report.",
        )
    if (
        extraction_metadata.get("status") != "candidate"
        or extraction_metadata.get("validation_status") != "validated"
    ):
        raise ReportGenerationConflict(
            "report_extraction_not_validated",
            "The latest baseline extraction is missing or failed validation.",
        )

    source_ids = _source_message_ids(extraction_metadata)
    messages_by_id = {message.id: message for message in ordered_messages}
    source_messages = [messages_by_id.get(message_id) for message_id in source_ids]
    if any(message is None or message.role != "user" for message in source_messages):
        raise ReportGenerationConflict(
            "report_extraction_stale",
            "The persisted extraction no longer matches the chat messages.",
        )

    root_message = source_messages[0]
    assert root_message is not None
    try:
        extraction_input = build_extraction_input(
            thread_id=thread.id,
            messages=ordered_messages,
            root_ordinal=root_message.ordinal,
        )
    except (TypeError, ValueError) as exc:
        raise ReportGenerationConflict(
            "report_extraction_stale",
            "The persisted extraction no longer matches the chat messages.",
        ) from exc

    expected_source_ids = [message.message_id for message in extraction_input.messages]
    if expected_source_ids != source_ids:
        raise ReportGenerationConflict(
            "report_extraction_stale",
            "The latest extraction does not cover the current case messages.",
        )

    try:
        extraction_payload = (
            current_case_state_json
            if current_case_state_json is not None
            else extraction_metadata
        )
        extraction = normalize_case_state(extraction_payload)
    except Exception as exc:
        raise ReportGenerationConflict(
            "report_extraction_not_validated",
            "The latest baseline extraction is missing or failed validation.",
        ) from exc

    report_source_messages = [
        ReportSourceMessage(
            message_id=message.message_id,
            ordinal=message.ordinal,
            source_type=message.source_type,
            content=message.content,
        )
        for message in extraction_input.messages
    ]
    mitre_value = (
        rag_context.mitre_table
        if rag_context is not None
        else latest_metadata.get("mitre_table", metadata.get("mitre_table"))
    )
    mitre_rows = _admitted_mitre_rows(mitre_value)
    if len(mitre_rows) > 64:
        raise ReportGenerationConflict(
            "report_mitre_rows_too_many",
            "The persisted MITRE mapping contains too many rows for one report.",
        )

    extraction_id = extraction_assistant.id
    original_version = (
        extraction_metadata.get("version")
        or extraction_metadata.get("prompt_version")
        or "canonical_case_state"
    )
    return ReportInputSnapshot(
        thread_id=thread.id,
        thread_title=thread.title or "New chat",
        extraction_id=extraction_id,
        extraction_version=str(original_version),
        source_messages=report_source_messages,
        extraction=extraction,
        mitre_rows=mitre_rows,
        metadata={
            "extraction_prompt_version": extraction_metadata.get("prompt_version"),
            "extraction_provider": extraction_metadata.get("provider"),
            "extraction_model": extraction_metadata.get("model"),
            "source_message_ids": [str(message_id) for message_id in source_ids],
            "mitre_source_message_id": str(latest_assistant.id),
            "case_state_version_id": (
                str(case_state_version_id) if case_state_version_id is not None else None
            ),
            "retrieval_context_id": (
                rag_context.retrieval_context_id if rag_context is not None
                else latest_assistant.retrieval_context_id
            ),
        },
    )

def _is_terminal_assistant(message: ChatMessage) -> bool:
    if message.role != "assistant":
        return False
    if message.retrieval_context_id is not None:
        return True
    return "mitre_table" in _metadata_dict(message.metadata_json)


def _metadata_dict(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _source_message_ids(metadata: dict[str, Any]) -> list[UUID]:
    raw_ids = metadata.get("source_message_ids")
    if not isinstance(raw_ids, list) or not raw_ids:
        raise ReportGenerationConflict(
            "report_extraction_stale",
            "The persisted extraction has no valid source messages.",
        )
    source_ids: list[UUID] = []
    for raw_id in raw_ids:
        try:
            source_ids.append(UUID(str(raw_id)))
        except (TypeError, ValueError) as exc:
            raise ReportGenerationConflict(
                "report_extraction_stale",
                "The persisted extraction has invalid source message IDs.",
            ) from exc
    if len(set(source_ids)) != len(source_ids):
        raise ReportGenerationConflict(
            "report_extraction_stale",
            "The persisted extraction has duplicate source message IDs.",
        )
    return source_ids


def _admitted_mitre_rows(value: object) -> list[AdmittedMitreRow]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ReportGenerationConflict(
            "report_mitre_metadata_invalid",
            "The persisted MITRE mapping is invalid.",
        )

    rows: list[AdmittedMitreRow] = []
    seen_ids: set[str] = set()
    for raw_row in value:
        try:
            row = MitreTableRow.model_validate(raw_row)
        except Exception:
            continue
        if not MITRE_ID_RE.fullmatch(row.technique_id):
            continue
        if row.technique_id in seen_ids:
            continue
        try:
            admitted = AdmittedMitreRow.model_validate(row.model_dump(mode="json"))
        except Exception:
            continue
        rows.append(admitted)
        seen_ids.add(admitted.technique_id)
    return rows
