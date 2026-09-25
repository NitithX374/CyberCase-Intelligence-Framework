from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from uuid import UUID

from pydantic import BaseModel, Field, ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.database import async_session
from app.models.analysis import CaseAnalysisResult
from app.models.case import Case
from app.schemas.rag import LegalReferenceResult
from app.services.analysis.clarification import Ask, Proceed
from app.services.analysis.contracts import CaseAnalysisFailure, CaseAssessmentTrace
from app.services.analysis.language import case_language
from app.services.analysis.pipeline import (
    AnalysisAdvance,
    AnalysisArtifacts,
    AnalysisInput,
    advance_case,
)
from app.services.analysis.steps.technical_context import (
    CaseRagContextPayload,
    CaseTechnicalAugmentation,
    technical_context_key,
)
from app.services.cases.ownership import owned_case
from app.services.chat.followup import (
    asked_gap_keys,
    case_messages,
    followup_history_from,
    last_question_awaiting_analysis,
    rounds_asked,
)
from app.services.sources.case_source_bundle import WITH_SOURCES, analysable_bundle
from app.services.sources.source_service import SourceError
from app.services.workflow.analysis_storage import (
    AnalysisStep,
    external_context,
    store_analysis,
    store_assessment,
)
from app.services.workflow.shared import CaseUnderAnalysis, CaseWorkflowError

_running: Counter[UUID] = Counter()


@contextmanager
def analysing(case_id: UUID) -> Iterator[None]:
    _running[case_id] += 1
    try:
        yield
    finally:
        _running[case_id] -= 1
        if _running[case_id] <= 0:
            del _running[case_id]


def analysis_running(case_id: UUID) -> bool:
    return _running[case_id] > 0


async def run_case_analysis(
    *,
    case_id: UUID,
    user_id: UUID | None,
    session_factory: Callable = async_session,
    pipeline: Callable = advance_case,
    continuing_followup: bool = False,
) -> AnalysisStep:
    with analysing(case_id):
        started = await read_case_for_analysis(
            session_factory,
            case_id=case_id,
            user_id=user_id,
            continuing_followup=continuing_followup,
        )
        outcome = await think(pipeline, started)
        return await store_outcome(session_factory, started, outcome)


class UnassessedAdvance(AnalysisAdvance):
    pass


async def think(pipeline: Callable, started: CaseUnderAnalysis) -> AnalysisAdvance:
    try:
        outcome = await pipeline(
            AnalysisInput(
                sources=started.source_bundle,
                response_language=case_language(started.source_bundle),
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
    if isinstance(outcome, AnalysisArtifacts):
        return UnassessedAdvance(CaseAssessmentTrace(gaps=[]), Proceed("no_eligible_gap"), outcome)
    return outcome


async def store_outcome(
    session_factory: Callable,
    started: CaseUnderAnalysis,
    outcome: AnalysisAdvance,
) -> AnalysisStep:
    if not isinstance(outcome, AnalysisAdvance):
        raise CaseWorkflowError("analysis_result_invalid", "Analysis pipeline result is invalid")
    if isinstance(outcome.decision, Ask):
        return await store_assessment(
            session_factory, started, outcome.assessment, outcome.decision
        )
    if outcome.artifacts is None or outcome.artifacts.trace is None:
        raise CaseWorkflowError(
            "analysis_trace_missing", "Case analysis did not produce a validated trace"
        )
    stop_reason = None if isinstance(outcome, UnassessedAdvance) else outcome.decision.reason
    return await store_analysis(session_factory, started, outcome.artifacts, stop_reason)


async def read_case_for_analysis(
    session_factory: Callable,
    *,
    case_id: UUID,
    user_id: UUID | None,
    continuing_followup: bool = False,
) -> CaseUnderAnalysis:
    async with session_factory() as db, db.begin():
        case = await owned_case(db, case_id, user_id, lock=True, options=WITH_SOURCES)
        try:
            bundle = analysable_bundle(case)
        except SourceError as error:
            raise CaseWorkflowError(error.code, error.message, error.status_code) from error
        chat = await case_messages(db, case.id)
        history = followup_history_from(chat)
        continuing = continuing_followup or (
            await last_question_awaiting_analysis(db, case.id) is not None
        )
        return CaseUnderAnalysis(
            case_id=case.id,
            source_bundle=bundle,
            followup_history=history,
            reused_context=await reusable_context(
                db, case.id, technical_context_key(bundle.revision, history)
            ),
            asked_gap_keys=asked_gap_keys(chat) if continuing else frozenset(),
            rounds_spent=(rounds_asked(chat) if continuing else 0) + 1,
        )


class RecordedRetrieval(BaseModel):
    context: str = Field(min_length=1)
    technical_augmentation: CaseTechnicalAugmentation
    legal_relevance: LegalReferenceResult


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
    try:
        recorded = RecordedRetrieval.model_validate(
            {**row.external_context_json, "context": stored.get("context")}
        )
    except ValidationError:
        return None
    augmentation = recorded.technical_augmentation
    if not augmentation.retrieval_context_id:
        return None
    return CaseRagContextPayload(
        retrieval_context_id=augmentation.retrieval_context_id,
        context=recorded.context,
        mitre_table=tuple(augmentation.mitre_table),
        legal_relevance=recorded.legal_relevance,
    )


async def get_latest_case_analysis(
    db: AsyncSession,
    *,
    case_id: UUID,
    user_id: UUID | None,
) -> tuple[Case, CaseAnalysisResult | None]:
    case = await owned_case(
        db, case_id, user_id, options=(selectinload(Case.latest_analysis_result),)
    )
    result = case.latest_analysis_result
    return case, result if result is None or result.status == "validated" else None


def analysis_freshness(case: Case, result: CaseAnalysisResult | None) -> str:
    if result is None:
        return "missing"
    return "current" if result.source_revision == case.source_revision else "stale"


__all__ = [
    "AnalysisStep",
    "UnassessedAdvance",
    "analysing",
    "analysis_freshness",
    "analysis_running",
    "external_context",
    "get_latest_case_analysis",
    "read_case_for_analysis",
    "run_case_analysis",
    "store_analysis",
]
