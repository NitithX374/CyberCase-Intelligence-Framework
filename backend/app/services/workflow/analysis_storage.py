from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from fastapi import status
from sqlalchemy import select

from app.errors import CaseAnalysisFailure, CaseWorkflowError
from app.llm.settings import configured_pipeline
from app.models.analysis import CaseAnalysisResult
from app.models.case import Case
from app.models.chat import ChatMessage
from app.services.analysis.clarification import Ask, ProceedReason
from app.services.analysis.pipeline import AnalysisArtifacts
from app.services.analysis.steps.technical_context import technical_context_key
from app.services.chat.followup import analysis_result_message, pending_question, question_message
from app.services.sources.case_source_bundle import sources_read
from app.services.workflow.shared import CaseUnderAnalysis, next_ordinal
from app.trace.claims import CaseAssessmentTrace, followup_snapshot


@dataclass(frozen=True)
class AnalysisStep:
    result: CaseAnalysisResult
    question: ChatMessage | None = None

    @property
    def needs_followup(self) -> bool:
        return self.question is not None


async def store_assessment(
    session_factory,
    started: CaseUnderAnalysis,
    assessment: CaseAssessmentTrace,
    decision: Ask,
) -> AnalysisStep:
    async with session_factory() as db, db.begin():
        case = await locked_unchanged_case(db, started)
        result = CaseAnalysisResult(
            case_id=case.id,
            source_revision=started.source_revision,
            status="assessment",
            summary="",
            trace_json=assessment.model_dump(mode="json"),
            pipeline_config=configured_pipeline().model_dump(mode="json"),
        )
        db.add(result)
        await db.flush()

        question = await pending_question(db, case.id)
        if question is None:
            question = question_message(
                case_id=case.id,
                ordinal=await next_ordinal(db, case.id),
                gap=decision.gap,
                analysis_result_id=result.id,
            )
            db.add(question)

        case.updated_at = datetime.now(UTC)
        await db.flush()
        await db.refresh(result)
        return AnalysisStep(result=result, question=question)


async def store_analysis(
    session_factory,
    started: CaseUnderAnalysis,
    artifacts: AnalysisArtifacts,
    stop_reason: ProceedReason | None,
) -> AnalysisStep:
    trace = artifacts.trace
    if stop_reason is not None:
        trace = trace.model_copy(update={"stop_reason": stop_reason})
    async with session_factory() as db, db.begin():
        case = await locked_unchanged_case(db, started)
        result = CaseAnalysisResult(
            case_id=case.id,
            source_revision=started.source_revision,
            status="validated",
            summary=trace.summary,
            trace_json=trace.model_dump(mode="json"),
            pipeline_config=configured_pipeline().model_dump(mode="json"),
            external_context_json={
                **external_context(artifacts),
                "sources_read": sources_read(started.source_bundle),
                "followup_history": followup_snapshot(started.followup_history),
            },
            retrieval_context_json=retrieval_context_row(artifacts, started),
        )
        db.add(result)
        await db.flush()
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
        return AnalysisStep(result=result)


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


def retrieval_context_row(
    artifacts: AnalysisArtifacts, started: CaseUnderAnalysis
) -> dict[str, object] | None:
    technical_context = artifacts.technical_context
    if technical_context is None:
        return None
    return {
        "context_key": technical_context_key(started.source_revision, started.followup_history),
        "context": technical_context.context,
    }


def external_context(artifacts: AnalysisArtifacts) -> dict[str, object]:
    if artifacts.trace is None:
        raise CaseAnalysisFailure(
            "analysis_trace_missing", "Case analysis did not produce a validated trace"
        )
    context: dict[str, object] = {}
    if artifacts.augmentation is None:
        return context
    retrieved = artifacts.technical_context
    if retrieved is not None:
        context["legal_relevance"] = retrieved.legal_relevance.model_dump(mode="json")
    associations = [item.association_id for item in artifacts.trace.mitre_associations]
    context["technical_augmentation"] = artifacts.augmentation.recorded(associations).model_dump(
        mode="json"
    )
    return context


__all__ = [
    "AnalysisStep",
    "external_context",
    "store_analysis",
    "store_assessment",
]
