"""Running one step of an analysis, and reading the latest one.

The pipeline runs with no database connection open: each function reads what it
needs in one short transaction, thinks with the connection released, and writes
what it produced in another.

An analysis is one step of a bounded loop, not the whole of it. It either ends
with a question for the reader — which the next request answers, advancing the
loop — or with a reason it stopped asking, which is recorded on the trace.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.database import async_session
from app.models.analysis import CaseAnalysisResult
from app.models.case import Case
from app.models.chat import ChatMessage
from app.services.analysis.clarification import Ask, decide_followup
from app.services.analysis.contracts import CaseAnalysisFailure, CaseAnalysisGap
from app.services.analysis.pipeline import (
    AnalysisArtifacts,
    AnalysisInput,
    analyse_case,
)
from app.services.analysis.settings import configured_pipeline
from app.services.analysis.steps.technical_context import (
    CaseRagContextPayload,
    technical_context_key,
)
from app.services.chat.followup import (
    analysis_result_message,
    asked_gap_keys,
    load_followup_history,
    question_message,
    rounds_asked,
)
from app.services.sources import SourceError, load_case_source_bundle
from app.services.workflow.shared import (
    CaseUnderAnalysis,
    CaseWorkflowError,
    next_ordinal,
    owned_case,
)


@dataclass(frozen=True)
class AnalysisStep:
    """What one step of the loop produced.

    ``question`` set means the loop paused to ask; ``stop_reason`` set means it
    will not ask again and this analysis is the one the case ends with. Exactly
    one of them is ever set.
    """

    result: CaseAnalysisResult
    rounds_spent: int
    question: ChatMessage | None = None
    # The gap the question came from. The message carries only the gap_key,
    # and the reader is shown the id the analysis gave it.
    gap: CaseAnalysisGap | None = None
    stop_reason: str | None = None

    @property
    def needs_followup(self) -> bool:
        return self.question is not None


async def run_case_analysis(
    *,
    case_id: UUID,
    user_id: UUID | None,
    response_language: str,
    session_factory: Callable = async_session,
    pipeline: Callable = analyse_case,
    continuing_followup: bool = False,
) -> AnalysisStep:
    """Run one step: analyse the case, then ask or stop. The caller waits for it.

    The pipeline runs with no database connection open, which is what lets an
    ablation run the same steps over a dataset instead of a case row — pass a
    different composition as ``pipeline`` and nothing else changes.

    ``continuing_followup`` marks an analysis a reply set off, so the rounds it
    has already spent still count against it. An analysis the reader asked for
    starts a chain of its own.
    """

    started = await read_case_for_analysis(session_factory, case_id=case_id, user_id=user_id)
    try:
        artifacts = await pipeline(
            AnalysisInput(
                sources=started.source_bundle,
                response_language=response_language,
                followup_history=started.followup_history,
                reused_context=started.reused_context,
            )
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
        history = await load_followup_history(db, case.id)
        return CaseUnderAnalysis(
            case_id=case.id,
            source_bundle=bundle,
            followup_history=history,
            reused_context=await reusable_context(
                db, case.id, technical_context_key(bundle.revision, history)
            ),
        )


async def reusable_context(
    db: AsyncSession,
    case_id: UUID,
    key: dict[str, int],
) -> CaseRagContextPayload | None:
    """The retrieval an earlier analysis of this same input already ran.

    Only the latest stored context is considered: an older one describes an
    input the case has since moved past, and reaching further back to find a
    match would mean reviving retrieval for sources that have changed.
    """

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
    if not isinstance(context, str) or not context or not isinstance(context_id, str):
        return None
    table = stored.get("mitre_table")
    return CaseRagContextPayload(
        retrieval_context_id=context_id,
        context=context,
        mitre_table=tuple(table if isinstance(table, list) else ()),
    )


async def store_analysis(
    session_factory: Callable,
    started: CaseUnderAnalysis,
    artifacts: AnalysisArtifacts,
    *,
    continuing_followup: bool = False,
) -> AnalysisStep:
    """Write the analysis, and either the question it asks or why it stopped.

    Both go in one transaction, so a case is never left holding an analysis
    that was meant to ask something and a chat that was never told.
    """

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

        spent = (await rounds_asked(db, case.id) if continuing_followup else 0) + 1
        decision = decide_followup(
            gaps=artifacts.trace.gaps,
            asked_gap_keys=(await asked_gap_keys(db, case.id) if continuing_followup else set()),
            # A freshly written analysis has asked nothing yet, so this round
            # is always open: only the case-wide bounds can close it here.
            asked_this_round=0,
            rounds_spent=spent,
            max_rounds=settings.chat_followup_max_rounds,
            gaps_per_round=settings.chat_followup_gaps_per_round,
        )
        stop_reason = None if isinstance(decision, Ask) else decision.reason

        # Written onto the trace before it is dumped, so the stored analysis
        # carries the reason it stopped rather than the reader having to infer
        # it from a chat that simply went quiet.
        trace = artifacts.trace.model_copy(update={"stop_reason": stop_reason})
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
            retrieval_context_json=retrieval_context_row(artifacts, started),
        )
        db.add(result)
        await db.flush()

        question = None
        gap = decision.gap if isinstance(decision, Ask) else None
        if isinstance(decision, Ask):
            question = question_message(
                case_id=case.id,
                ordinal=await next_ordinal(db, case.id),
                gap=decision.gap,
                analysis_result_id=result.id,
            )
            db.add(question)
        elif stop_reason is not None:
            # Terminal: the loop is over, so the case gets its answer in the
            # conversation it was asked in, not only on the analysis page.
            db.add(
                analysis_result_message(
                    case_id=case.id,
                    ordinal=await next_ordinal(db, case.id),
                    trace=trace,
                    analysis_result_id=result.id,
                )
            )
        case.latest_analysis_result_id = result.id
        case.updated_at = now
        await db.flush()
        await db.refresh(result)
        return AnalysisStep(
            result=result,
            rounds_spent=spent,
            question=question,
            gap=gap,
            stop_reason=stop_reason,
        )


def retrieval_context_row(
    artifacts: AnalysisArtifacts, started: CaseUnderAnalysis
) -> dict[str, object] | None:
    """The retrieval, kept whole, with the input it answers.

    The key travels with the context rather than beside it, so deciding
    whether a stored retrieval still applies is one comparison against one
    column instead of a join between two JSON blobs.
    """

    if artifacts.technical_context is None or not artifacts.retrieval_context_id:
        return None
    return {
        "context_key": technical_context_key(started.source_revision, started.followup_history),
        "retrieval_context_id": artifacts.retrieval_context_id,
        "context": artifacts.technical_context.get("context", ""),
        "mitre_table": list(artifacts.technical_context.get("mitre_table", []) or []),
    }


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
    "AnalysisStep",
    "analysis_freshness",
    "external_context",
    "get_latest_case_analysis",
    "read_case_for_analysis",
    "run_case_analysis",
    "store_analysis",
]
