from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case
from app.models.caseRun import CaseAnalysisResult as PersistedAnalysisResult, CaseRun
from app.models.chat import ChatMessage
from app.models.ragContext import RagContext
from app.schemas.messageMetadata import serialize_message_metadata
from app.services.case_analysis.contracts import (
    CaseAdmittedSource,
    CaseAnalysisFailure,
    CaseAnalysisResult as AnalysisOutput,
    CaseAnalysisTrace,
)
from app.services.case_analysis.validation import validate_case_trace
from app.services.case_materials import AssembledCaseEvidence, assembleCaseEvidence
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

        if run.evidence_revision != case.evidence_revision:
            await _mark_superseded(run, now)
            return False
        assembled = await assembleCaseEvidence(db, case_id=case.id, user_id=None)
        trace = _validated_output(output, assembled)
        if run.evidence_revision != case.evidence_revision:
            await _mark_superseded(run, now)
            return False
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
                updated_at=now,
            )
            .returning(CaseRun.id)
        )
        if completion.scalar_one_or_none() is None:
            return False
        provider_metadata = {
            "source_reference_type": "case_evidence_source",
            "evidence_revision": run.evidence_revision,
        }
        if augmentation is not None:
            provider_metadata.update(
                {
                    "mitre_table": deepcopy(augmentation.get("mitre_table", [])),
                    "technical_augmentation": deepcopy(augmentation),
                }
            )
        if output.followup_question:
            provider_metadata["followup_question"] = output.followup_question.strip()
            if output.followup_metadata:
                provider_metadata["followup_metadata"] = deepcopy(output.followup_metadata)
        result = PersistedAnalysisResult(
            case_id=case.id,
            run_id=run.id,
            evidence_revision=run.evidence_revision,
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
        if augmentation is not None and trace.retrieval_context_id:
            existing_rag = await db.scalar(
                select(RagContext).where(
                    (RagContext.retrieval_context_id == trace.retrieval_context_id)
                    | (RagContext.case_run_id == run.id)
                )
            )
            if existing_rag is None:
                query_str = str(augmentation.get("query", augmentation.get("trigger_text", "")))
                rag_context = RagContext(
                    retrieval_context_id=trace.retrieval_context_id,
                    case_id=case.id,
                    case_run_id=run.id,
                    query_text=query_str,
                    context_text=str(augmentation.get("context", "")),
                    mitre_table=deepcopy(augmentation.get("mitre_table", [])),
                )
                db.add(rag_context)
        await db.flush()

        has_followup = output.followup_question is not None
        if has_followup:
            followup_metadata_raw = output.followup_metadata or {}
            existing_followup = (
                followup_metadata_raw.get("chat_followup")
                if isinstance(followup_metadata_raw, dict)
                else None
            )
            clarification_meta = build_clarification_metadata(output, trace)
            gap_id = str(clarification_meta.get("gap_id") or "G-001")
            topic = str(clarification_meta.get("topic") or "")
            gap_key = str(clarification_meta.get("gap_key") or f"{gap_id}:{topic.lower()}")
            followup_message_id = uuid4()
            next_ordinal = (
                await db.scalar(
                    select(func.coalesce(func.max(ChatMessage.ordinal), 0)).where(
                        ChatMessage.case_id == case.id
                    )
                )
                + 1
            )
            followup_message_meta = build_followup_message_metadata(
                clarification_topic=topic,
                gap_id=gap_id,
                gap_key=gap_key,
                thread_ordinal=next_ordinal,
                trace=trace,
                existing_followup=existing_followup,
            )
            question = ChatMessage(
                id=followup_message_id,
                case_id=case.id,
                ordinal=next_ordinal,
                role="assistant",
                content=output.followup_question.strip(),
                message_kind="followup_question",
                analysis_result_id=result.id,
                metadata_json=serialize_message_metadata(followup_message_meta),
            )
            db.add(question)
            await db.flush()

        case.latest_analysis_result_id = result.id
        case.updated_at = now
        await db.flush()
    return True


async def _mark_superseded(
    run: CaseRun,
    finished_at: datetime,
) -> None:
    run.status = "failed"
    run.error_code = "case_run_superseded"
    run.error_message = "Case evidence changed while this run was executing. Retry analysis."
    run.finished_at = finished_at
    run.updated_at = finished_at


def _owns_run(run: CaseRun | None, case_id: UUID, claimed_attempt: int) -> bool:
    return bool(
        run is not None
        and run.case_id == case_id
        and run.status == "running"
        and run.attempt_count == claimed_attempt
    )


def _validated_output(
    output: AnalysisOutput,
    assembled: AssembledCaseEvidence,
) -> CaseAnalysisTrace:
    trace = output.trace
    if not isinstance(trace, CaseAnalysisTrace):
        raise CaseRunCompletionError("analysis_trace_missing", "Case analysis did not produce a validated trace")
    if not output.answer.strip():
        raise CaseRunCompletionError("analysis_answer_missing", "Case analysis answer is empty")
    sources = tuple(
        CaseAdmittedSource(
            str(s.id),
            s.exact_text,
        )
        for s in assembled.active_sources
    )
    doc_context = []
    for s in assembled.active_sources:
        if s.document_id and s.document and isinstance(s.provenance_json, dict):
            pages = s.provenance_json.get("pages")
            if isinstance(pages, list):
                doc_context.append(
                    {
                        "source_id": str(s.id),
                        "documents": [{"document_id": str(s.document_id), "filename": s.document.filename, "page_spans": pages}],
                    }
                )
    try:
        return validate_case_trace(
            trace,
            sources,
            doc_context,
            mitre_table=mitre_table_from_output(output),
        )
    except CaseAnalysisFailure as error:
        raise CaseRunCompletionError(error.code, error.message) from error


completeCaseRun = complete_case_run

__all__ = ["CaseRunCompletionError", "completeCaseRun", "complete_case_run"]
