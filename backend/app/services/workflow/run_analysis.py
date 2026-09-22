"""Advance a case without holding a database connection during model work."""

from __future__ import annotations

from collections.abc import Callable
from uuid import UUID

from fastapi import status
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.database import async_session
from app.models.analysis import CaseAnalysisResult
from app.models.case import Case
from app.schemas.rag import LegalReferenceResult
from app.services.analysis.clarification import Ask
from app.services.analysis.contracts import CaseAnalysisFailure
from app.services.analysis.pipeline import (
    AnalysisAdvance,
    AnalysisArtifacts,
    AnalysisInput,
    advance_case,
)
from app.services.analysis.steps.technical_context import (
    CaseRagContextPayload,
    technical_context_key,
)
from app.services.chat.followup import asked_gap_keys, load_followup_history, rounds_asked
from app.services.sources import SourceError, load_case_source_bundle
from app.services.workflow.analysis_storage import (
    AnalysisStep,
    external_context,
    store_analysis,
    store_assessment,
)
from app.services.workflow.shared import CaseUnderAnalysis, CaseWorkflowError, owned_case


async def run_case_analysis(
    *,
    case_id: UUID,
    user_id: UUID | None,
    response_language: str,
    session_factory: Callable = async_session,
    pipeline: Callable = advance_case,
    continuing_followup: bool = False,
) -> AnalysisStep:
    started = await read_case_for_analysis(
        session_factory,
        case_id=case_id,
        user_id=user_id,
        continuing_followup=continuing_followup,
    )
    try:
        outcome = await pipeline(
            AnalysisInput(
                sources=started.source_bundle,
                response_language=response_language,
                followup_history=started.followup_history,
                reused_context=started.reused_context,
                asked_gap_keys=started.asked_gap_keys,
                rounds_spent=started.rounds_spent,
                max_rounds=settings.chat_followup_max_rounds,
                gaps_per_round=settings.chat_followup_gaps_per_round,
            )
        )
    except CaseAnalysisFailure as error:
        raise CaseWorkflowError(error.code, error.message) from error

    if isinstance(outcome, AnalysisAdvance):
        if isinstance(outcome.decision, Ask):
            return await store_assessment(
                session_factory,
                started,
                outcome.assessment,
                outcome.decision,
                continuing_followup=continuing_followup,
            )
        if outcome.artifacts is None:
            raise CaseWorkflowError(
                "analysis_trace_missing", "Case analysis did not produce a validated trace"
            )
        return await store_analysis(
            session_factory,
            started,
            outcome.artifacts,
            continuing_followup=continuing_followup,
            decision=outcome.decision,
        )

    if not isinstance(outcome, AnalysisArtifacts):
        raise CaseWorkflowError("analysis_result_invalid", "Analysis pipeline result is invalid")
    return await store_analysis(
        session_factory,
        started,
        outcome,
        continuing_followup=continuing_followup,
    )


async def read_case_for_analysis(
    session_factory: Callable,
    *,
    case_id: UUID,
    user_id: UUID | None,
    continuing_followup: bool = False,
) -> CaseUnderAnalysis:
    async with session_factory() as db, db.begin():
        case = await owned_case(db, case_id, user_id)
        try:
            bundle = await load_case_source_bundle(db, case_id=case.id, user_id=user_id)
        except SourceError as error:
            raise CaseWorkflowError(error.code, error.message, error.status_code) from error
        history = await load_followup_history(db, case.id)
        return CaseUnderAnalysis(
            case_id=case.id,
            source_bundle=bundle,
            followup_history=history,
            reused_context=await reusable_context(
                db, case.id, technical_context_key(bundle.revision, history)
            ),
            asked_gap_keys=frozenset(
                await asked_gap_keys(db, case.id) if continuing_followup else set()
            ),
            rounds_spent=(await rounds_asked(db, case.id) if continuing_followup else 0) + 1,
        )


async def reusable_context(
    db: AsyncSession,
    case_id: UUID,
    key: dict[str, int],
) -> CaseRagContextPayload | None:
    row = await db.scalar(
        select(CaseAnalysisResult)
        .where(
            CaseAnalysisResult.case_id == case_id,
            CaseAnalysisResult.retrieval_context_json.is_not(None),
        )
        .order_by(CaseAnalysisResult.created_at.desc())
        .limit(1)
    )
    stored = row.retrieval_context_json if row is not None else None
    if not isinstance(stored, dict) or stored.get("context_key") != key:
        return None
    context = stored.get("context")
    context_id = stored.get("retrieval_context_id")
    if (
        not isinstance(context, str)
        or not context
        or not isinstance(context_id, str)
        or not context_id.strip()
    ):
        return None
    table = stored.get("mitre_table")
    if not isinstance(table, list):
        return None
    try:
        legal_relevance = LegalReferenceResult.model_validate(stored.get("legal_relevance"))
    except ValidationError:
        return None
    return CaseRagContextPayload(
        retrieval_context_id=context_id,
        context=context,
        mitre_table=tuple(table),
        legal_relevance=legal_relevance,
    )


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
    result = case.latest_analysis_result
    return case, result if result is None or result.status == "validated" else None


def analysis_freshness(case: Case, result: CaseAnalysisResult | None) -> str:
    if result is None:
        return "missing"
    return "current" if result.source_revision == case.source_revision else "stale"


__all__ = [
    "AnalysisStep",
    "analysis_freshness",
    "external_context",
    "get_latest_case_analysis",
    "read_case_for_analysis",
    "run_case_analysis",
    "store_analysis",
]
