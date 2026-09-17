from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.case import Case
from app.models.case_materials import CaseSource
from app.models.case_run import CaseAnalysisResult
from app.models.chat import ChatMessage
from app.services.case_analysis.analysis_trace_contracts import (
    CaseAnalysisGap,
    CaseAnalysisTrace,
)
from app.services.case_materials.case_source_bundle import (
    case_source_bundle_from_case,
    provider_source_payload,
)
from app.services.gap_clarification.contracts import GapClarificationState
from app.services.gap_clarification.runtime import GapClarificationError, parse_uuid


@dataclass(frozen=True)
class GapClarificationContext:
    case: Case
    gap: CaseAnalysisGap
    sources: list[dict[str, object]]
    pipeline_config: dict[str, object]
    questions_asked: list[dict[str, object]]
    answers_received: list[dict[str, object]]


async def load_gap_context(
    db: AsyncSession,
    state: GapClarificationState,
    *,
    session_id: str,
    lock_case: bool = False,
    include_history: bool = True,
) -> GapClarificationContext:
    case_statement = (
        select(Case)
        .options(selectinload(Case.sources).selectinload(CaseSource.document))
        .where(Case.id == parse_uuid(state["case_id"], "case_id"))
    )
    if lock_case:
        case_statement = case_statement.with_for_update()
    case = (await db.execute(case_statement)).scalar_one_or_none()
    if case is None:
        raise GapClarificationError("case_not_found", "Case not found", 404)

    expected_revision = state["source_evidence_revision"]
    if case.evidence_revision != expected_revision:
        raise GapClarificationError(
            "clarification_stale",
            "Case evidence changed; restart clarification",
        )

    analysis = await db.scalar(
        select(CaseAnalysisResult).where(
            CaseAnalysisResult.id == parse_uuid(
                state["source_analysis_id"], "source_analysis_id"
            ),
            CaseAnalysisResult.case_id == case.id,
        )
    )
    if analysis is None:
        raise GapClarificationError(
            "clarification_context_invalid",
            "Clarification analysis context is no longer available",
        )
    if analysis.evidence_revision > expected_revision or case.latest_analysis_result_id != analysis.id:
        raise GapClarificationError(
            "clarification_stale",
            "The active analysis changed; restart clarification",
        )

    trace = _validated_trace(analysis.trace_json)
    gap = next((item for item in trace.gaps if item.gap_id == state["gap_id"]), None)
    if gap is None:
        raise GapClarificationError(
            "clarification_gap_missing",
            "The selected clarification gap is no longer available",
        )

    bundle = case_source_bundle_from_case(case)
    questions_asked: list[dict[str, object]] = []
    answers_received: list[dict[str, object]] = []
    if include_history:
        questions_asked, answers_received = await load_clarification_history(
            db,
            case_id=case.id,
            analysis_id=str(analysis.id),
            gap_id=gap.gap_id,
            session_id=session_id,
        )

    if not isinstance(analysis.pipeline_config, dict):
        raise GapClarificationError(
            "clarification_context_invalid",
            "Analysis pipeline configuration is invalid",
        )

    return GapClarificationContext(
        case=case,
        gap=gap,
        sources=[provider_source_payload(source) for source in bundle.sources],
        pipeline_config=dict(analysis.pipeline_config),
        questions_asked=questions_asked,
        answers_received=answers_received,
    )


async def load_clarification_history(
    db: AsyncSession,
    *,
    case_id: UUID,
    analysis_id: str,
    gap_id: str,
    session_id: str,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    question_messages = list(
        (
            await db.scalars(
                select(ChatMessage)
                .where(
                    ChatMessage.case_id == case_id,
                    ChatMessage.message_kind == "followup_question",
                )
                .order_by(ChatMessage.ordinal.desc())
                .limit(64)
            )
        ).all()
    )
    answer_messages = list(
        (
            await db.scalars(
                select(ChatMessage)
                .where(
                    ChatMessage.case_id == case_id,
                    ChatMessage.message_kind == "followup_answer",
                )
                .order_by(ChatMessage.ordinal.desc())
                .limit(64)
            )
        ).all()
    )
    messages = sorted([*question_messages, *answer_messages], key=lambda message: message.ordinal)
    questions: list[dict[str, object]] = []
    answers: list[dict[str, object]] = []
    for message in messages:
        followup = _followup_metadata(message)
        if not _belongs_to_context(followup, analysis_id, gap_id, session_id):
            continue
        if message.message_kind == "followup_question":
            questions.append(
                {
                    "question": message.content,
                    "target_information": followup.get("target_information"),
                    "attempt": followup.get("round"),
                    "rationale_summary": followup.get("rationale_summary"),
                }
            )
            continue
        answer = followup.get("answer")
        answers.append(dict(answer) if isinstance(answer, dict) else {"answer": message.content})
    return questions, answers


def _validated_trace(trace_json: object) -> CaseAnalysisTrace:
    if not isinstance(trace_json, dict):
        raise GapClarificationError(
            "clarification_context_invalid",
            "Analysis trace is unavailable",
        )
    try:
        return CaseAnalysisTrace.model_validate(trace_json)
    except ValidationError as error:
        raise GapClarificationError(
            "clarification_context_invalid",
            "Analysis trace is invalid",
        ) from error


def _followup_metadata(message: ChatMessage) -> dict[str, object]:
    metadata = message.metadata_json if isinstance(message.metadata_json, dict) else {}
    followup = metadata.get("chat_followup")
    return dict(followup) if isinstance(followup, dict) else {}


def _belongs_to_context(
    followup: dict[str, object],
    analysis_id: str,
    gap_id: str,
    session_id: str,
) -> bool:
    if str(followup.get("source_analysis_id")) != analysis_id:
        return False
    if str(followup.get("clarification_session_id")) != session_id:
        return False
    gap = followup.get("gap")
    return isinstance(gap, dict) and str(gap.get("gap_id")) == gap_id


__all__ = ["GapClarificationContext", "load_clarification_history", "load_gap_context"]
