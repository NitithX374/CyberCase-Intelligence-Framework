"""The case conversation: asking about an analysis, and answering what it asks.

A question is answered in the request that sent it, from the analysis the case
already has. When the analysis left something open it asks about it here, one
question at a time, and each reply stays a message — conversation the next
analysis reads as follow-up history, not a case source that revises the
material. The case is analysed again once the round's questions are spent, not
after every reply.
"""

from __future__ import annotations

from collections.abc import Callable
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
from app.schemas.chat import CaseChatRead, ChatMessageCreate, ChatMessageRead
from app.services.case_analysis.clarification import Ask, decide_followup
from app.services.case_analysis.contracts import CaseAnalysisTrace
from app.services.case_workflow import (
    AnalysisStep,
    CaseWorkflowError,
    answer_case_question,
    next_ordinal,
    owned_case,
    run_case_analysis,
)
from app.services.chat.followup import (
    answer_message,
    asked_gap_keys,
    asked_this_round,
    pending_question,
    question_message,
    rounds_asked,
)


class CaseChatError(Exception):
    def __init__(
        self, code: str, message: str, status_code: int = status.HTTP_409_CONFLICT
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


async def get_case_chat(
    db: AsyncSession,
    *,
    case_id: UUID,
    user_id: UUID | None,
) -> CaseChatRead:
    case = await db.scalar(
        select(Case)
        .options(selectinload(Case.chat_messages), selectinload(Case.latest_analysis_result))
        .where(Case.id == case_id)
    )
    if case is None or case.user_id != user_id:
        raise CaseChatError("case_not_found", "Case not found", status.HTTP_404_NOT_FOUND)

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
    """Handle one sent message. Returns the messages it produced.

    A send that follows an unanswered question is that question's answer. The
    reader does not say so and the client does not mark it: the open question
    is the one the case is waiting on, and there is only ever one.

    A send that answers a question may then run an analysis, which takes long
    enough that a client can give up and retry. The retry finds the message its
    id already created and is given what that send produced.
    """

    already = await messages_of_send(session_factory, case_id, request.client_request_id)
    if already is not None:
        return already, None

    answered = await answer_pending_question(
        case_id=case_id, user_id=user_id, request=request, session_factory=session_factory
    )
    if answered is not None:
        return answered

    try:
        question, answer = await answer_case_question(
            case_id=case_id,
            user_id=user_id,
            content=request.content,
            response_language=request.response_language,
            client_request_id=request.client_request_id,
            session_factory=session_factory,
        )
    except CaseWorkflowError as error:
        raise CaseChatError(error.code, error.message, error.status_code) from error
    return [question, answer], None


async def messages_of_send(
    session_factory: Callable, case_id: UUID, client_request_id: str | None
) -> list[ChatMessage] | None:
    """Everything a send already produced, when the client is sending it again."""

    if client_request_id is None:
        return None
    async with session_factory() as db:
        sent = await db.scalar(
            select(ChatMessage).where(
                ChatMessage.case_id == case_id,
                ChatMessage.client_request_id == client_request_id,
            )
        )
    if sent is None:
        return None
    return await messages_from(session_factory, case_id, sent.ordinal)


async def answer_pending_question(
    *,
    case_id: UUID,
    user_id: UUID | None,
    request: ChatMessageCreate,
    session_factory: Callable,
) -> tuple[list[ChatMessage], AnalysisStep | None] | None:
    """Record the reply. None if nothing was asked.

    The round's remaining questions are asked first, one at a time, so each
    reply answers a named gap. Only when the round is spent does the case cost
    another analysis.
    """

    async with session_factory() as db, db.begin():
        try:
            case = await owned_case(db, case_id, user_id)
        except CaseWorkflowError as error:
            raise CaseChatError(error.code, error.message, error.status_code) from error
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
        # The reply is conversation. It does not revise the case material, so
        # source_revision does not move and the analysis already running over
        # this case is not invalidated by someone answering a question.
        first_new_ordinal = answer.ordinal
        following = await next_question_of_round(db, case_id=case.id, question=question)
        if following is not None:
            db.add(following)

    if following is not None:
        return await messages_from(session_factory, case_id, first_new_ordinal), None

    try:
        step = await run_case_analysis(
            case_id=case_id,
            user_id=user_id,
            response_language=request.response_language,
            session_factory=session_factory,
            continuing_followup=True,
        )
    except CaseWorkflowError as error:
        raise CaseChatError(error.code, error.message, error.status_code) from error
    return await messages_from(session_factory, case_id, first_new_ordinal), step


async def next_question_of_round(
    db: AsyncSession, *, case_id: UUID, question: ChatMessage
) -> ChatMessage | None:
    """The next question from the analysis that asked this one, if any is left.

    None means this round is over — not that the case is settled. The caller
    analyses again, and that analysis decides afresh whether to ask or stop.
    """

    analysis_result_id = question.analysis_result_id
    result = await db.get(CaseAnalysisResult, analysis_result_id)
    if result is None:
        return None
    trace = CaseAnalysisTrace.model_validate(result.trace_json)
    decision = decide_followup(
        gaps=trace.gaps,
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


__all__ = ["CaseChatError", "get_case_chat", "post_case_message"]
