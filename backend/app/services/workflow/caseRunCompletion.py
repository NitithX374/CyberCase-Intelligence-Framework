from __future__ import annotations

import hashlib
from copy import deepcopy
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case
from app.models.caseMaterials import CaseEvidenceSnapshot
from app.models.caseRun import CaseAnalysisResult as PersistedAnalysisResult, CaseRun
from app.models.chat import ChatMessage, ChatThread
from app.schemas.messageMetadata import serialize_message_metadata
from app.services.case_analysis.contracts import (
    CaseAdmittedSource,
    CaseAnalysisFailure,
    CaseAnalysisResult as AnalysisOutput,
    CaseAnalysisTrace,
)
from app.services.case_analysis.validation import validate_case_trace
from app.services.followup.caseClarification import (
    create_pending_clarification,
    supersede_prior_clarifications,
)
from app.services.workflow.caseRunCompletionMetadata import (
    build_clarification_metadata,
    build_followup_message_metadata,
    mitre_table_from_output,
    technical_augmentation,
)


class CaseRunCompletionError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


async def complete_case_run(
    db: AsyncSession,
    run_id: UUID,
    claimed_attempt: int,
    output: AnalysisOutput,
) -> bool:
    now = datetime.now(timezone.utc)
    async with db.begin():
        run_case = await db.scalar(select(CaseRun.case_id).where(CaseRun.id == run_id))
        if run_case is None:
            return False
        case = await db.scalar(select(Case).where(Case.id == run_case).with_for_update())
        if case is None:
            return False
        run = await db.scalar(select(CaseRun).where(CaseRun.id == run_id).with_for_update())
        if not _owns_run(run, case.id, claimed_attempt):
            return False
        snapshot = await db.get(CaseEvidenceSnapshot, run.snapshot_id)
        if snapshot is None or snapshot.case_id != case.id:
            raise CaseRunCompletionError("case_snapshot_missing", "Pinned Case evidence snapshot is missing")
        trace = _validated_output(output, snapshot)
        augmentation = technical_augmentation(output)
        augmentation_payload = augmentation or {}
        completion = await db.execute(
            update(CaseRun)
            .where(
                CaseRun.id == run_id,
                CaseRun.status == "running",
                CaseRun.attempt_count == claimed_attempt,
            )
            .values(
                status="completed",
                error_code=None,
                error_message=None,
                finished_at=now,
                lease_owner=None,
                lease_expires_at=None,
                updated_at=now,
            )
            .returning(CaseRun.id)
        )
        if completion.scalar_one_or_none() is None:
            return False
        provider_metadata = {
            "source_reference_type": "case_evidence_source",
            "snapshot_id": str(run.snapshot_id),
        }
        if augmentation is not None:
            provider_metadata.update(
                {
                    "mitre_table": deepcopy(augmentation.get("mitre_table", [])),
                    "technical_augmentation": deepcopy(augmentation),
                }
            )
        result = PersistedAnalysisResult(
            case_id=case.id,
            run_id=run.id,
            snapshot_id=run.snapshot_id,
            schema_version=trace.version,
            status="validated",
            answer=output.answer.strip(),
            summary=trace.summary,
            trace_json=trace.model_dump(mode="json"),
            execution_receipt_json=deepcopy(output.execution_receipt),
            retrieval_context_id=trace.retrieval_context_id,
            pipeline_config=deepcopy(run.pipeline_config),
            provider_metadata_json=provider_metadata,
        )
        db.add(result)
        await db.flush()

        has_followup = output.followup_question is not None
        thread = await db.scalar(select(ChatThread).where(ChatThread.id == case.id).with_for_update())
        if has_followup:
            if thread is None:
                thread = ChatThread(id=case.id, title=case.title, user_id=case.user_id)
                db.add(thread)
                await db.flush()
            followup_metadata_raw = output.followup_metadata or {}
            existing_followup = (
                followup_metadata_raw.get("chat_followup")
                if isinstance(followup_metadata_raw, dict)
                else None
            )
            clarification_meta = build_clarification_metadata(output, trace)
            clarification = await create_pending_clarification(
                db,
                case_id=case.id,
                result_id=result.id,
                snapshot_id=run.snapshot_id,
                question=output.followup_question,
                metadata=clarification_meta,
            )
            followup_message_meta = build_followup_message_metadata(
                result_id=result.id,
                clarification_id=clarification.id,
                snapshot_id=run.snapshot_id,
                clarification_topic=clarification.topic,
                gap_id=clarification.gap_id,
                gap_key=clarification.gap_key,
                thread_ordinal=thread.next_message_ordinal,
                augmentation_payload=augmentation_payload,
                is_augmentation_present=augmentation is not None,
                run_pipeline_config=run.pipeline_config,
                trace=trace,
                existing_followup=existing_followup,
            )
            question = ChatMessage(
                thread_id=thread.id,
                ordinal=thread.next_message_ordinal,
                role="assistant",
                content=output.followup_question.strip(),
                message_kind="followup_question",
                analysis_result_id=result.id,
                metadata_json=serialize_message_metadata(followup_message_meta),
            )
            db.add(question)
            await db.flush()
            clarification.question_message_id = question.id
            thread.next_message_ordinal += 1

        await supersede_prior_clarifications(
            db,
            case_id=case.id,
            result_id=result.id,
        )
        if thread is not None:
            thread.status = "awaiting_followup" if has_followup else "answered"
            thread.updated_at = now
        case.latest_analysis_result_id = result.id
        case.updated_at = now
        await db.flush()
    return True


def _owns_run(run: CaseRun | None, case_id: UUID, claimed_attempt: int) -> bool:
    return bool(
        run is not None
        and run.case_id == case_id
        and run.status == "running"
        and run.attempt_count == claimed_attempt
    )


def _validated_output(
    output: AnalysisOutput,
    snapshot: CaseEvidenceSnapshot,
) -> CaseAnalysisTrace:
    trace = output.trace
    if not isinstance(trace, CaseAnalysisTrace):
        raise CaseRunCompletionError("analysis_trace_missing", "Case analysis did not produce a validated trace")
    if not output.answer.strip():
        raise CaseRunCompletionError("analysis_answer_missing", "Case analysis answer is empty")
    if trace.evidence_sha256 != snapshot.text_sha256:
        raise CaseRunCompletionError("analysis_trace_invalid", "Analysis trace is not bound to the pinned evidence snapshot")
    try:
        return validate_case_trace(
            trace,
            _snapshot_sources(snapshot),
            _snapshot_document_context(snapshot),
            mitre_table=mitre_table_from_output(output),
        )
    except CaseAnalysisFailure as error:
        raise CaseRunCompletionError(error.code, error.message) from error


def _snapshot_sources(snapshot: CaseEvidenceSnapshot) -> tuple[CaseAdmittedSource, ...]:
    if not isinstance(snapshot.manifest_json, list):
        raise CaseRunCompletionError("case_snapshot_invalid", "Pinned Case snapshot manifest is invalid")
    sources: list[CaseAdmittedSource] = []
    for entry in snapshot.manifest_json:
        if not isinstance(entry, dict):
            raise CaseRunCompletionError("case_snapshot_invalid", "Pinned Case snapshot source entry is invalid")
        source_id = entry.get("source_id")
        revision = entry.get("revision")
        content = entry.get("exact_text")
        text_sha256 = entry.get("text_sha256")
        if not isinstance(source_id, str) or not isinstance(revision, int) or not isinstance(content, str) or not isinstance(text_sha256, str):
            raise CaseRunCompletionError("case_snapshot_invalid", "Pinned Case snapshot source reference is incomplete")
        if hashlib.sha256(content.encode("utf-8")).hexdigest() != text_sha256:
            raise CaseRunCompletionError("case_snapshot_invalid", "Pinned Case snapshot source hash is invalid")
        sources.append(CaseAdmittedSource(source_id, revision, content, text_sha256))
    return tuple(sources)


def _snapshot_document_context(snapshot: CaseEvidenceSnapshot) -> list[dict[str, object]]:
    context: list[dict[str, object]] = []
    for entry in snapshot.manifest_json:
        if not isinstance(entry, dict):
            continue
        provenance = entry.get("provenance")
        if not isinstance(provenance, dict):
            continue
        document_id = entry.get("document_id")
        filename = entry.get("filename")
        pages = provenance.get("pages")
        if isinstance(document_id, str) and isinstance(filename, str) and isinstance(pages, list):
            context.append(
                {
                    "source_id": entry.get("source_id"),
                    "documents": [{"document_id": document_id, "filename": filename, "page_spans": pages}],
                }
            )
    return context


completeCaseRun = complete_case_run

__all__ = ["CaseRunCompletionError", "completeCaseRun", "complete_case_run"]
