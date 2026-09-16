from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case
from app.models.case_run import CaseAnalysisResult as PersistedAnalysisResult, CaseRun
from app.models.chat import ChatMessage
from app.models.rag_context import RagContext
from app.schemas.message_metadata import serialize_message_metadata
from app.services.case_analysis.contracts import (
    CaseAnalysisFailure,
    CaseAnalysisOutput as AnalysisOutput,
    CaseAnalysisTrace,
)
from app.services.case_analysis.validation import validate_case_trace
from app.services.case_materials import CaseSourceBundle, load_case_source_bundle


class CaseRunCompletionError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def technical_augmentation(output: AnalysisOutput) -> dict[str, object] | None:
    receipt = output.execution_receipt
    value = receipt.get("technical_augmentation") if isinstance(receipt, dict) else None
    return value if isinstance(value, dict) else None


def mitre_table_from_output(output: AnalysisOutput) -> list[dict[str, object]]:
    value = (technical_augmentation(output) or {}).get("mitre_table", [])
    return [dict(item) for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def build_followup_message_metadata(
    *,
    followup_metadata: dict[str, object],
    analysis_result_id: UUID,
    evidence_revision: int,
    thread_ordinal: int,
) -> dict[str, object]:
    metadata = dict(followup_metadata)
    chat_followup = metadata.get("chat_followup")
    if not isinstance(chat_followup, dict):
        raise CaseRunCompletionError("clarification_metadata_missing", "Case clarification metadata is missing")
    gap = chat_followup.get("gap")
    if not isinstance(gap, dict):
        raise CaseRunCompletionError("clarification_metadata_missing", "Case clarification gap is missing")
    chat_followup = dict(chat_followup)
    chat_followup.update(
        {
            "root_ordinal": thread_ordinal,
            "source_analysis_id": str(analysis_result_id),
            "source_revision": evidence_revision,
        }
    )
    metadata["action"] = "follow_up"
    metadata["chat_followup"] = chat_followup
    return metadata


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
        if not owns_run(run, case.id, claimed_attempt):
            return False

        if run.evidence_revision != case.evidence_revision:
            await mark_superseded(run, now)
            return False
        source_bundle = await load_case_source_bundle(db, case_id=case.id, user_id=None)
        trace = validated_output(output, source_bundle)
        if run.evidence_revision != case.evidence_revision:
            await mark_superseded(run, now)
            return False
        augmentation = technical_augmentation(output)
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
        external_context = {
            "source_reference_type": "case_source",
            "evidence_revision": run.evidence_revision,
        }
        if augmentation is not None:
            external_context.update(
                {
                    "mitre_table": list(augmentation.get("mitre_table", [])),
                    "technical_augmentation": dict(augmentation),
                }
            )
        if output.followup_question:
            external_context["followup_question"] = output.followup_question.strip()
            if output.followup_metadata:
                external_context["followup_metadata"] = dict(output.followup_metadata)
        result = PersistedAnalysisResult(
            case_id=case.id,
            run_id=run.id,
            evidence_revision=run.evidence_revision,
            schema_version=trace.version,
            status="validated",
            answer=output.answer.strip(),
            summary=trace.summary,
            trace_json=trace.model_dump(mode="json"),
            execution_receipt_json=dict(output.execution_receipt) if isinstance(output.execution_receipt, dict) else output.execution_receipt,
            retrieval_context_id=trace.retrieval_context_id,
            pipeline_config=dict(run.pipeline_config) if isinstance(run.pipeline_config, dict) else run.pipeline_config,
            external_context_json=external_context,
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
                    mitre_table=list(augmentation.get("mitre_table", [])),
                )
                db.add(rag_context)
        await db.flush()

        has_followup = bool(output.followup_question and output.followup_question.strip())
        if has_followup:
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
                followup_metadata=output.followup_metadata or {},
                analysis_result_id=result.id,
                evidence_revision=run.evidence_revision,
                thread_ordinal=next_ordinal,
            )
            external_context["followup_metadata"] = followup_message_meta
            result.external_context_json = external_context
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


async def mark_superseded(
    run: CaseRun,
    finished_at: datetime,
) -> None:
    run.status = "failed"
    run.error_code = "case_run_superseded"
    run.error_message = "Case evidence changed while this run was executing. Retry analysis."
    run.finished_at = finished_at
    run.updated_at = finished_at


def owns_run(run: CaseRun | None, case_id: UUID, claimed_attempt: int) -> bool:
    return bool(
        run is not None
        and run.case_id == case_id
        and run.status == "running"
        and run.attempt_count == claimed_attempt
    )


def validated_output(
    output: AnalysisOutput,
    source_bundle: CaseSourceBundle,
) -> CaseAnalysisTrace:
    trace = output.trace
    if not isinstance(trace, CaseAnalysisTrace):
        raise CaseRunCompletionError("analysis_trace_missing", "Case analysis did not produce a validated trace")
    if not output.answer.strip():
        raise CaseRunCompletionError("analysis_answer_missing", "Case analysis answer is empty")
    try:
        return validate_case_trace(
            trace,
            source_bundle,
            mitre_table=mitre_table_from_output(output),
        )
    except CaseAnalysisFailure as error:
        raise CaseRunCompletionError(error.code, error.message) from error


__all__ = [
    "CaseRunCompletionError",
    "build_followup_message_metadata",
    "complete_case_run",
    "mitre_table_from_output",
    "technical_augmentation",
]
