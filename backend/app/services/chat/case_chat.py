from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.database import async_session
from app.models.analysis import CaseAnalysisResult
from app.models.case import Case
from app.models.chat import ChatMessage
from app.schemas.chat import CaseChatRead, ChatMessageCreate, ChatMessageRead
from app.services.analysis.clarification import Ask, decide_followup
from app.services.analysis.contracts import CaseAnalysisTrace, CaseAssessmentTrace
from app.services.cases.ownership import owned_case
from app.services.chat.followup import (
    answer_message,
    asked_gap_keys,
    asked_this_round,
    last_question_awaiting_analysis,
    pending_question,
    question_message,
    rounds_asked,
)
from app.services.workflow.answer_question import (
    answer_case_question,
    answer_recorded_question,
    being_answered,
)
from app.services.workflow.run_analysis import (
    AnalysisStep,
    analysis_running,
    run_case_analysis,
)
from app.services.workflow.shared import next_ordinal


@dataclass(frozen=True)
class RecordedFollowup:
    messages: list[ChatMessage]
    first_new_ordinal: int
    next_question: ChatMessage | None


async def get_case_chat(
    db: AsyncSession,
    *,
    case_id: UUID,
    user_id: UUID | None,
) -> CaseChatRead:
    case = await owned_case(
        db,
        case_id,
        user_id,
        options=(selectinload(Case.chat_messages), selectinload(Case.latest_analysis_result)),
    )
    messages = [ChatMessageRead.model_validate(message) for message in case.chat_messages]
    answered = case.latest_analysis_result is not None or messages
    return CaseChatRead(
        case_id=case.id,
        status="answered" if answered else "idle",
        messages=messages,
    )


async def post_case_message(
    *,
    case_id: UUID,
    user_id: UUID | None,
    request: ChatMessageCreate,
    session_factory: Callable = async_session,
) -> tuple[list[ChatMessage], AnalysisStep | None]:
    if (
        sent := await sent_message(session_factory, case_id, user_id, request.client_request_id)
    ) is not None:
        if await closes_unanalysed_round(session_factory, case_id, sent):
            return await analyse_after_round(
                case_id=case_id,
                user_id=user_id,
                request=request,
                first_new_ordinal=sent.ordinal,
                session_factory=session_factory,
            )
        if await unanswered(session_factory, sent):
            question, answer = await answer_recorded_question(
                case_id=case_id,
                user_id=user_id,
                question_id=sent.id,
                session_factory=session_factory,
            )
            return [question, answer], None
        return await messages_from(session_factory, case_id, sent.ordinal), None

    standing = await standing_question(session_factory, case_id, user_id)
    if standing is None:
        return await reply_in_conversation(
            case_id=case_id,
            user_id=user_id,
            request=request,
            session_factory=session_factory,
        )

    recorded = await record_answer_and_ask_next(
        case_id=case_id, user_id=user_id, request=request, session_factory=session_factory
    )
    if recorded is None:
        return await reply_in_conversation(
            case_id=case_id,
            user_id=user_id,
            request=request,
            session_factory=session_factory,
        )
    if recorded.next_question is not None:
        return recorded.messages, None
    return await analyse_after_round(
        case_id=case_id,
        user_id=user_id,
        request=request,
        first_new_ordinal=recorded.first_new_ordinal,
        session_factory=session_factory,
    )


async def reply_in_conversation(
    *,
    case_id: UUID,
    user_id: UUID | None,
    request: ChatMessageCreate,
    session_factory: Callable,
) -> tuple[list[ChatMessage], AnalysisStep | None]:
    question, answer = await answer_case_question(
        case_id=case_id,
        user_id=user_id,
        content=request.content,
        client_request_id=request.client_request_id,
        session_factory=session_factory,
    )
    return [question, answer], None


async def standing_question(
    session_factory: Callable, case_id: UUID, user_id: UUID | None
) -> ChatMessage | None:
    async with session_factory() as db:
        case = await owned_case(db, case_id, user_id)
        return await pending_question(db, case.id)


async def record_answer_and_ask_next(
    *,
    case_id: UUID,
    user_id: UUID | None,
    request: ChatMessageCreate,
    session_factory: Callable,
) -> RecordedFollowup | None:
    async with session_factory() as db, db.begin():
        case = await owned_case(db, case_id, user_id, lock=True)
        question = await pending_question(db, case.id)
        if question is None:
            return None
        answer = answer_message(
            case_id=case.id,
            ordinal=await next_ordinal(db, case.id),
            content=request.content.strip(),
            question=question,
            client_request_id=request.client_request_id,
        )
        db.add(answer)
        await db.flush()
        first_new_ordinal = answer.ordinal
        following = await next_question_of_round(db, case_id=case.id, question=question)
        if following is not None:
            db.add(following)

    return RecordedFollowup(
        messages=await messages_from(session_factory, case_id, first_new_ordinal),
        first_new_ordinal=first_new_ordinal,
        next_question=following,
    )


async def analyse_after_round(
    *,
    case_id: UUID,
    user_id: UUID | None,
    request: ChatMessageCreate,
    first_new_ordinal: int,
    session_factory: Callable,
) -> tuple[list[ChatMessage], AnalysisStep | None]:
    step = await run_case_analysis(
        case_id=case_id,
        user_id=user_id,
        session_factory=session_factory,
        continuing_followup=True,
    )
    return await messages_from(session_factory, case_id, first_new_ordinal), step


async def sent_message(
    session_factory: Callable,
    case_id: UUID,
    user_id: UUID | None,
    client_request_id: str | None,
) -> ChatMessage | None:
    if client_request_id is None:
        return None
    async with session_factory() as db:
        await owned_case(db, case_id, user_id)
        return await db.scalar(
            select(ChatMessage).where(
                ChatMessage.case_id == case_id,
                ChatMessage.client_request_id == client_request_id,
            )
        )


async def unanswered(session_factory: Callable, sent: ChatMessage) -> bool:
    if sent.message_kind != "conversation":
        return False
    async with session_factory() as db:
        reply = await db.scalar(
            select(ChatMessage.id).where(ChatMessage.in_reply_to_message_id == sent.id).limit(1)
        )
    return reply is None and not being_answered(sent.id)


async def closes_unanalysed_round(
    session_factory: Callable, case_id: UUID, sent: ChatMessage
) -> bool:
    if sent.message_kind != "followup_answer" or analysis_running(case_id):
        return False
    async with session_factory() as db:
        question = await last_question_awaiting_analysis(db, case_id)
    return question is not None and sent.in_reply_to_message_id == question.id


async def next_question_of_round(
    db: AsyncSession, *, case_id: UUID, question: ChatMessage
) -> ChatMessage | None:
    analysis_result_id = question.analysis_result_id
    result = await db.get(CaseAnalysisResult, analysis_result_id)
    if result is None:
        return None
    if result.status == "assessment":
        gaps = CaseAssessmentTrace.model_validate(result.trace_json).gaps
    else:
        gaps = CaseAnalysisTrace.model_validate(result.trace_json).gaps
    decision = decide_followup(
        gaps=gaps,
        asked_gap_keys=await asked_gap_keys(db, case_id),
        asked_this_round=len(await asked_this_round(db, analysis_result_id)),
        rounds_spent=await rounds_asked(db, case_id),
        max_rounds=settings.chat_followup_max_rounds,
        gaps_per_round=settings.chat_followup_gaps_per_round,
    )
    if not isinstance(decision, Ask):
        return None
    return question_message(
        case_id=case_id,
        ordinal=await next_ordinal(db, case_id),
        gap=decision.gap,
        analysis_result_id=analysis_result_id,
    )


async def messages_from(
    session_factory: Callable, case_id: UUID, first_ordinal: int
) -> list[ChatMessage]:
    async with session_factory() as db:
        rows = await db.scalars(
            select(ChatMessage)
            .where(ChatMessage.case_id == case_id, ChatMessage.ordinal >= first_ordinal)
            .order_by(ChatMessage.ordinal)
        )
        return list(rows)


__all__ = ["get_case_chat", "post_case_message"]
