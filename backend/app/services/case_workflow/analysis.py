"""Running an analysis, and reading the latest one.

The pipeline runs with no database connection open: each function reads what it
needs in one short transaction, thinks with the connection released, and writes
what it produced in another.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from uuid import UUID

from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import async_session
from app.models.analysis import CaseAnalysisResult
from app.models.case import Case
from app.services.case_analysis.contracts import CaseAnalysisFailure
from app.services.case_analysis.pipeline import (
    AnalysisArtifacts,
    AnalysisInput,
    Stage,
    analysis_stages,
    run_pipeline,
)
from app.services.case_analysis.pipeline_config import configured_pipeline
from app.services.case_workflow.shared import (
    CaseUnderAnalysis,
    CaseWorkflowError,
    next_ordinal,
    owned_case,
)
from app.services.chat.followup import next_gap, question_message, rounds_asked
from app.services.sources import SourceError, load_case_source_bundle


async def run_case_analysis(
    *,
    case_id: UUID,
    user_id: UUID | None,
    response_language: str,
    session_factory: Callable = async_session,
    stages: tuple[Stage, ...] | None = None,
    continuing_followup: bool = False,
) -> CaseAnalysisResult:
    """Analyse the case and store the result. The caller waits for it.

    The pipeline runs with no database connection open, which is what lets an
    ablation run the same stages over a dataset instead of a case row.

    ``continuing_followup`` marks an analysis a reply set off, so the rounds it
    has already spent still count against it. An analysis the reader asked for
    starts a chain of its own.
    """

    # Read at call time, not at import, so the arm setting is the arm that runs.
    stages = stages or analysis_stages()
    started = await read_case_for_analysis(session_factory, case_id=case_id, user_id=user_id)
    try:
        artifacts = await run_pipeline(
            AnalysisInput(
                sources=started.source_bundle,
                response_language=response_language,
            ),
            stages,
        )
    except CaseAnalysisFailure as error:
        raise CaseWorkflowError(error.code, error.message) from error
    return await store_analysis(
        session_factory, started, artifacts, continuing_followup=continuing_followup
    )


async def read_case_for_analysis(
    session_factory: Callable,
    *,
    case_id: UUID,
    user_id: UUID | None,
) -> CaseUnderAnalysis:
    async with session_factory() as db, db.begin():
        case = await owned_case(db, case_id, user_id)
        try:
            bundle = await load_case_source_bundle(db, case_id=case.id, user_id=user_id)
        except SourceError as error:
            raise CaseWorkflowError(error.code, error.message, error.status_code) from error
        return CaseUnderAnalysis(case_id=case.id, source_bundle=bundle)


async def store_analysis(
    session_factory: Callable,
    started: CaseUnderAnalysis,
    artifacts: AnalysisArtifacts,
    *,
    continuing_followup: bool = False,
) -> CaseAnalysisResult:
    """Write the analysis, and the question it wants to ask, in one transaction."""

    now = datetime.now(UTC)
    async with session_factory() as db, db.begin():
        case = await db.scalar(select(Case).where(Case.id == started.case_id).with_for_update())
        if case is None:
            raise CaseWorkflowError("case_not_found", "Case not found", status.HTTP_404_NOT_FOUND)
        if case.source_revision != started.source_revision:
            raise CaseWorkflowError(
                "case_sources_changed",
                "The case sources changed while the analysis was running. Analyse again.",
            )

        trace = artifacts.trace
        result = CaseAnalysisResult(
            case_id=case.id,
            source_revision=started.source_revision,
            schema_version=trace.version,
            status="validated",
            answer=artifacts.answer,
            summary=trace.summary,
            trace_json=trace.model_dump(mode="json"),
            retrieval_context_id=trace.retrieval_context_id,
            pipeline_config=configured_pipeline().model_dump(mode="json"),
            external_context_json=external_context(artifacts, started.source_revision),
        )
        db.add(result)
        await db.flush()

        spent = await rounds_asked(db, case.id) if continuing_followup else 0
        gap = next_gap(trace, asked=set(), rounds=spent + 1)
        if gap is not None:
            db.add(
                question_message(
                    case_id=case.id,
                    ordinal=await next_ordinal(db, case.id),
                    gap=gap,
                    analysis_result_id=result.id,
                )
            )

        case.latest_analysis_result_id = result.id
        case.updated_at = now
        await db.flush()
        await db.refresh(result)
        return result


def external_context(artifacts: AnalysisArtifacts, source_revision: int) -> dict[str, object]:
    """What external context this analysis was given, and what it led to.

    The retrieval stage cannot know whether its context was used, because the
    model had not run yet. That is settled here, where both are in hand.
    """

    context: dict[str, object] = {
        "source_reference_type": "case_source",
        "source_revision": source_revision,
    }
    augmentation = artifacts.receipt.get("technical_augmentation")
    if not isinstance(augmentation, dict):
        return context
    augmentation = dict(augmentation)
    associations = [item.association_id for item in artifacts.trace.mitre_associations]
    augmentation["association_ids"] = associations
    if augmentation["status"] == "retrieved_from_rag" and associations:
        augmentation["status"] = "retrieved_with_matches"
    context["mitre_table"] = list(augmentation.get("mitre_table", []))
    context["technical_augmentation"] = augmentation
    return context


async def get_latest_case_analysis(
    db: AsyncSession,
    *,
    case_id: UUID,
    user_id: UUID | None,
) -> tuple[Case, CaseAnalysisResult | None]:
    case = await db.scalar(
        select(Case)
        .options(selectinload(Case.latest_analysis_result))
        .where(Case.id == case_id, Case.user_id == user_id)
    )
    if case is None:
        raise CaseWorkflowError("case_not_found", "Case not found", status.HTTP_404_NOT_FOUND)
    return case, case.latest_analysis_result


def analysis_freshness(case: Case, result: CaseAnalysisResult | None) -> str:
    if result is None:
        return "missing"
    return "current" if result.source_revision == case.source_revision else "stale"


__all__ = [
    "analysis_freshness",
    "external_context",
    "get_latest_case_analysis",
    "read_case_for_analysis",
    "run_case_analysis",
    "store_analysis",
]
