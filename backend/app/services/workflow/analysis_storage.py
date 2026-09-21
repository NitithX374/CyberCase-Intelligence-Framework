from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from fastapi import status
from sqlalchemy import select

from app.config import settings
from app.models.analysis import CaseAnalysisResult
from app.models.case import Case
from app.models.chat import ChatMessage
from app.services.analysis.clarification import Ask, FollowupDecision
from app.services.analysis.contracts import (
    CaseAnalysisFailure,
    CaseAnalysisGap,
    CaseAnalysisTrace,
    CaseAssessmentTrace,
)
from app.services.analysis.pipeline import AnalysisArtifacts
from app.services.analysis.settings import configured_pipeline
from app.services.analysis.steps.technical_context import technical_context_key
from app.services.chat.followup import (
    analysis_result_message,
    asked_gap_keys,
    pending_question,
    question_message,
    rounds_asked,
)
from app.services.workflow.shared import (
    CaseUnderAnalysis,
    CaseWorkflowError,
    next_ordinal,
)


@dataclass(frozen=True)
class AnalysisStep:
    result: CaseAnalysisResult
    rounds_spent: int
    question: ChatMessage | None = None
    gap: CaseAnalysisGap | None = None
    stop_reason: str | None = None

    @property
    def needs_followup(self) -> bool:
        return self.question is not None


async def store_assessment(
    session_factory,
    started: CaseUnderAnalysis,
    assessment: CaseAssessmentTrace,
    decision: Ask,
    *,
    continuing_followup: bool,
) -> AnalysisStep:
    async with session_factory() as db, db.begin():
        case = await locked_unchanged_case(db, started)
        spent = (await rounds_asked(db, case.id) if continuing_followup else 0) + 1
        result = CaseAnalysisResult(
            case_id=case.id,
            source_revision=started.source_revision,
            schema_version=assessment.version,
            status="assessment",
            answer="",
            summary="",
            trace_json=assessment.model_dump(mode="json"),
            pipeline_config=configured_pipeline().model_dump(mode="json"),
            external_context_json={
                "source_reference_type": "case_source",
                "source_revision": started.source_revision,
            },
        )
        db.add(result)
        await db.flush()

        standing = await pending_question(db, case.id)
        gap = decision.gap
        if standing is None:
            question = question_message(
                case_id=case.id,
                ordinal=await next_ordinal(db, case.id),
                gap=gap,
                analysis_result_id=result.id,
            )
            db.add(question)
        else:
            question = standing
            gap = gap_of(assessment.gaps, standing.gap_key) or gap

        case.updated_at = datetime.now(UTC)
        await db.flush()
        await db.refresh(result)
        return AnalysisStep(
            result=result,
            rounds_spent=spent,
            question=question,
            gap=gap,
        )


async def store_analysis(
    session_factory,
    started: CaseUnderAnalysis,
    artifacts: AnalysisArtifacts,
    *,
    continuing_followup: bool = False,
    decision: FollowupDecision | None = None,
) -> AnalysisStep:
    if artifacts.trace is None:
        raise CaseWorkflowError(
            "analysis_trace_missing", "Case analysis did not produce a validated trace"
        )

    async with session_factory() as db, db.begin():
        case = await locked_unchanged_case(db, started)
        spent = (await rounds_asked(db, case.id) if continuing_followup else 0) + 1
        resolved_decision = decision or decide_from_trace(
            artifacts.trace,
            asked=await asked_gap_keys(db, case.id) if continuing_followup else set(),
            spent=spent,
        )
        stop_reason = None if isinstance(resolved_decision, Ask) else resolved_decision.reason
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
        gap = resolved_decision.gap if isinstance(resolved_decision, Ask) else None
        if isinstance(resolved_decision, Ask):
            standing = await pending_question(db, case.id)
            if standing is None:
                question = question_message(
                    case_id=case.id,
                    ordinal=await next_ordinal(db, case.id),
                    gap=resolved_decision.gap,
                    analysis_result_id=result.id,
                )
                db.add(question)
            else:
                question = standing
                gap = gap_of(trace.gaps, standing.gap_key) or resolved_decision.gap
        elif stop_reason is not None:
            db.add(
                analysis_result_message(
                    case_id=case.id,
                    ordinal=await next_ordinal(db, case.id),
                    trace=trace,
                    analysis_result_id=result.id,
                )
            )

        case.latest_analysis_result_id = result.id
        case.updated_at = datetime.now(UTC)
        await db.flush()
        await db.refresh(result)
        return AnalysisStep(
            result=result,
            rounds_spent=spent,
            question=question,
            gap=gap,
            stop_reason=stop_reason,
        )


def decide_from_trace(trace: CaseAnalysisTrace, *, asked: set[str], spent: int):
    from app.services.analysis.clarification import decide_followup

    return decide_followup(
        gaps=trace.gaps,
        asked_gap_keys=asked,
        asked_this_round=0,
        rounds_spent=spent,
        max_rounds=settings.chat_followup_max_rounds,
        gaps_per_round=settings.chat_followup_gaps_per_round,
    )


async def locked_unchanged_case(db, started: CaseUnderAnalysis) -> Case:
    case = await db.scalar(select(Case).where(Case.id == started.case_id).with_for_update())
    if case is None:
        raise CaseWorkflowError("case_not_found", "Case not found", status.HTTP_404_NOT_FOUND)
    if case.source_revision != started.source_revision:
        raise CaseWorkflowError(
            "case_sources_changed",
            "The case sources changed while the analysis was running. Analyse again.",
        )
    return case


def gap_of(gaps: list[CaseAnalysisGap], gap_key: str | None) -> CaseAnalysisGap | None:
    if not gap_key:
        return None
    return next((gap for gap in gaps if gap.gap_key == gap_key), None)


def retrieval_context_row(
    artifacts: AnalysisArtifacts, started: CaseUnderAnalysis
) -> dict[str, object] | None:
    if artifacts.technical_context is None or not artifacts.retrieval_context_id:
        return None
    return {
        "context_key": technical_context_key(started.source_revision, started.followup_history),
        "retrieval_context_id": artifacts.retrieval_context_id,
        "context": artifacts.technical_context.get("context", ""),
        "mitre_table": list(artifacts.technical_context.get("mitre_table", []) or []),
    }


def external_context(artifacts: AnalysisArtifacts, source_revision: int) -> dict[str, object]:
    if artifacts.trace is None:
        raise CaseAnalysisFailure(
            "analysis_trace_missing", "Case analysis did not produce a validated trace"
        )
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


__all__ = [
    "AnalysisStep",
    "external_context",
    "store_analysis",
    "store_assessment",
]
