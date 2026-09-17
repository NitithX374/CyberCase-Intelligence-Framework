from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
from uuid import UUID, uuid4

from langgraph.types import Command
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.database import async_session
from app.models.case import Case
from app.models.case_materials import CaseSource
from app.models.case_run import CaseAnalysisResult, CaseRun
from app.models.chat import ChatMessage
from app.services.case_analysis.analysis_trace_contracts import CaseAnalysisTrace
from app.services.gap_clarification.checkpoint import graph_config, open_checkpointer
from app.services.gap_clarification.completion import enqueue_completion_analysis
from app.services.gap_clarification.contracts import ClarificationResumeAnswer, GapClarificationState
from app.services.gap_clarification.graph import build_gap_clarification_graph
from app.services.gap_clarification.persistence import answer_message_content, find_reply_message
from app.services.gap_clarification.runtime import GapClarificationError, bind_session_factory


@dataclass(frozen=True)
class ClarificationResumeResult:
    answer_message: ChatMessage
    next_question: ChatMessage | None
    reply_message: ChatMessage | None
    run: CaseRun | None


async def start_gap_clarification_for_analysis(
    *,
    case_id: UUID,
    analysis_result_id: UUID,
    session_factory: Callable = async_session,
) -> str | None:
    if not settings.chat_followup_enabled:
        return None
    async with session_factory() as db:
        case = await load_case(db, case_id)
        analysis = await db.scalar(
            select(CaseAnalysisResult)
            .options(selectinload(CaseAnalysisResult.run))
            .where(
                CaseAnalysisResult.id == analysis_result_id,
                CaseAnalysisResult.case_id == case_id,
            )
        )
        if case is None or analysis is None:
            raise GapClarificationError("clarification_context_invalid", "Analysis clarification context is missing")
        if case.latest_analysis_result_id != analysis.id or case.evidence_revision != analysis.evidence_revision:
            raise GapClarificationError("clarification_stale", "Analysis is not current for clarification")
        gap = select_gap(CaseAnalysisTrace.model_validate(analysis.trace_json))
        if gap is None:
            return None
        existing = await existing_session_message(db, case.id, str(analysis.id), gap["gap_id"])
        if existing is not None:
            return session_id_from_message(existing)
        session_id = str(uuid4())
        initial = build_initial_state(case, analysis, gap)
    async with open_checkpointer() as saver:
        graph = build_gap_clarification_graph(saver)
        with bind_session_factory(session_factory):
            await graph.ainvoke(initial, config=graph_config(session_id))
    return session_id


async def start_gap_clarification_for_run(
    *,
    run_id: UUID,
    session_factory: Callable = async_session,
) -> str | None:
    async with session_factory() as db:
        analysis = await db.scalar(select(CaseAnalysisResult).where(CaseAnalysisResult.run_id == run_id))
        if analysis is None:
            return None
        return await start_gap_clarification_for_analysis(
            case_id=analysis.case_id,
            analysis_result_id=analysis.id,
            session_factory=session_factory,
        )


async def resume_gap_clarification(
    *,
    case_id: UUID,
    user_id: UUID | None,
    question_id: UUID,
    content: str,
    disposition: str,
    request_key: str,
    gap_id: str | None = None,
    clarification_session_id: str | None = None,
    session_factory: Callable = async_session,
) -> ClarificationResumeResult:
    async with session_factory() as db:
        case = await db.scalar(select(Case).where(Case.id == case_id))
        if case is None or case.user_id != user_id:
            raise GapClarificationError("case_not_found", "Case not found", 404)
        question = await db.scalar(
            select(ChatMessage).where(
                ChatMessage.id == question_id,
                ChatMessage.case_id == case_id,
                ChatMessage.message_kind == "followup_question",
                ChatMessage.role == "assistant",
            )
        )
        if question is None:
            raise GapClarificationError("followup_not_found", "Clarification question not found", 404)
        followup = followup_metadata(question)
        session_id = str(followup.get("clarification_session_id") or "")
        if not session_id:
            raise GapClarificationError("clarification_session_missing", "Clarification session is missing")
        if clarification_session_id and clarification_session_id != session_id:
            raise GapClarificationError("clarification_session_mismatch", "Clarification session does not belong to this question")
        gap = followup.get("gap")
        if gap_id and (not isinstance(gap, dict) or str(gap.get("gap_id")) != gap_id):
            raise GapClarificationError("clarification_gap_mismatch", "This answer does not belong to the selected clarification gap", 422)
        source_analysis_id = followup.get("source_analysis_id")
        existing = await db.scalar(
            select(ChatMessage).where(
                ChatMessage.case_id == case_id,
                ChatMessage.client_request_id == request_key,
            )
        )
        if existing is not None:
            expected_content = answer_message_content(
                ClarificationResumeAnswer(
                    content=content,
                    disposition=disposition,
                    request_key=request_key,
                    question_message_id=str(question_id),
                )
            )
            if existing.content not in {expected_content, disposition} or existing.in_reply_to_message_id != question.id:
                raise GapClarificationError("idempotency_conflict", "Idempotency key was already used with a different clarification answer")
            next_question = await pending_question_after(db, case_id, session_id, existing.ordinal)
            reply_message = await find_reply_message(db, case_id, existing.id)
            return ClarificationResumeResult(existing, next_question, reply_message, None)
        if not isinstance(source_analysis_id, str) or case.latest_analysis_result_id is None or str(case.latest_analysis_result_id) != source_analysis_id:
            raise GapClarificationError("clarification_stale", "The active analysis changed; restart clarification")
        answered = await db.scalar(
            select(ChatMessage.id).where(
                ChatMessage.case_id == case_id,
                ChatMessage.in_reply_to_message_id == question.id,
                ChatMessage.message_kind == "followup_answer",
            )
        )
        if answered is not None:
            raise GapClarificationError("clarification_already_answered", "This clarification question already has an answer")
        if int(followup.get("source_revision", -1)) != case.evidence_revision:
            raise GapClarificationError("clarification_stale", "Case evidence changed; restart clarification")
    resume_payload = {
        "content": content,
        "disposition": disposition,
        "request_key": request_key,
        "question_message_id": str(question_id),
    }
    async with open_checkpointer() as saver:
        graph = build_gap_clarification_graph(saver)
        with bind_session_factory(session_factory):
            await graph.ainvoke(Command(resume=resume_payload), config=graph_config(session_id))
    async with session_factory() as db:
        answer = await db.scalar(
            select(ChatMessage).where(
                ChatMessage.case_id == case_id,
                ChatMessage.client_request_id == request_key,
            )
        )
        if answer is None:
            raise GapClarificationError("clarification_answer_missing", "Clarification answer was not persisted")
        next_question = await pending_question_after(db, case_id, session_id, answer.ordinal)
        reply_message = await find_reply_message(db, case_id, answer.id)
        run = await enqueue_completion_analysis(
            db,
            case_id=case_id,
            user_id=user_id,
            session_id=session_id,
            answer=answer,
            next_question=next_question,
            request_key=request_key,
        )
        await db.commit()
        return ClarificationResumeResult(answer, next_question, reply_message, run)


async def load_case(db: AsyncSession, case_id: UUID) -> Case | None:
    result = await db.execute(
        select(Case)
        .options(selectinload(Case.sources).selectinload(CaseSource.document))
        .where(Case.id == case_id)
    )
    return result.scalar_one_or_none()


def select_gap(trace: CaseAnalysisTrace) -> dict[str, object] | None:
    ranked = sorted(
        enumerate(trace.gaps),
        key=lambda item: (
            0 if item[1].priority == "high" else 1 if item[1].priority == "medium" else 2,
            0 if item[1].affected_claim_ids else 1,
            item[0],
        ),
    )
    for _, gap in ranked:
        if gap.askable and gap.status != "EXPLICITLY_UNKNOWN":
            return gap.model_dump(mode="json")
    return None


def build_initial_state(case: Case, analysis: CaseAnalysisResult, gap: dict[str, object]) -> GapClarificationState:
    request_payload = analysis.run.request_payload if analysis.run and isinstance(analysis.run.request_payload, dict) else {}
    language = request_payload.get("response_language")
    return {
        "case_id": str(case.id),
        "source_analysis_id": str(analysis.id),
        "source_evidence_revision": analysis.evidence_revision,
        "response_language": language if language in {"thai", "english"} else "english",
        "gap_id": str(gap["gap_id"]),
        "pending_question_message_id": None,
        "latest_answer": None,
        "latest_interpretation": None,
        "attempt_count": 0,
        "resolution_status": "unresolved",
    }


async def existing_session_message(db: AsyncSession, case_id: UUID, analysis_id: str, gap_id: object) -> ChatMessage | None:
    messages = await db.scalars(select(ChatMessage).where(ChatMessage.case_id == case_id, ChatMessage.message_kind == "followup_question"))
    for message in messages:
        followup = followup_metadata(message)
        gap = followup.get("gap")
        if followup.get("source_analysis_id") == analysis_id and isinstance(gap, dict) and gap.get("gap_id") == gap_id:
            return message
    return None


async def pending_question_after(db: AsyncSession, case_id: UUID, session_id: str, ordinal: int) -> ChatMessage | None:
    messages = await db.scalars(
        select(ChatMessage).where(
            ChatMessage.case_id == case_id,
            ChatMessage.message_kind == "followup_question",
            ChatMessage.ordinal > ordinal,
        ).order_by(ChatMessage.ordinal)
    )
    for message in messages:
        if followup_metadata(message).get("clarification_session_id") != session_id:
            continue
        answered = await db.scalar(select(ChatMessage.id).where(ChatMessage.in_reply_to_message_id == message.id))
        if answered is None:
            return message
    return None


def followup_metadata(message: ChatMessage) -> dict[str, object]:
    metadata = message.metadata_json if isinstance(message.metadata_json, dict) else {}
    followup = metadata.get("chat_followup")
    return dict(followup) if isinstance(followup, dict) else {}


def session_id_from_message(message: ChatMessage) -> str | None:
    value = followup_metadata(message).get("clarification_session_id")
    return str(value) if value else None


__all__ = [
    "ClarificationResumeResult",
    "GapClarificationError",
    "resume_gap_clarification",
    "select_gap",
    "start_gap_clarification_for_analysis",
    "start_gap_clarification_for_run",
]
