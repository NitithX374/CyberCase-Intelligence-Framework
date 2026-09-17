from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case
from app.models.case_run import CaseAnalysisResult as PersistedAnalysisResult, CaseRun
from app.models.rag_context import RagContext
from app.services.case_analysis.contracts import (
    CaseAnalysisOutput as AnalysisOutput,
    CaseAnalysisTrace,
)


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
        trace = validated_output(output)
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
) -> CaseAnalysisTrace:
    trace = output.trace
    if not isinstance(trace, CaseAnalysisTrace):
        raise CaseRunCompletionError("analysis_trace_missing", "Case analysis did not produce a validated trace")
    if not output.answer.strip():
        raise CaseRunCompletionError("analysis_answer_missing", "Case analysis answer is empty")
    return trace


__all__ = [
    "CaseRunCompletionError",
    "complete_case_run",
    "mitre_table_from_output",
    "technical_augmentation",
]
