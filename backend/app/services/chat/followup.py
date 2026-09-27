from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis import CaseAnalysisResult
from app.models.chat import ChatMessage
from app.schemas.message_metadata import message_trace, serialize_message_metadata
from app.trace.claims import CaseAnalysisGap, CaseFollowupExchange, followup_qa_id
from app.trace.trace import CaseAnalysisTrace


async def case_messages(db: AsyncSession, case_id: UUID) -> list[ChatMessage]:
    rows = await db.scalars(
        select(ChatMessage).where(ChatMessage.case_id == case_id).order_by(ChatMessage.ordinal)
    )
    return list(rows)


def asked_gap_keys(messages: Sequence[ChatMessage]) -> frozenset[str]:
    return frozenset(message.gap_key for message in messages if message.gap_key)


def rounds_asked(messages: Sequence[ChatMessage]) -> int:
    return len(
        {
            message.analysis_result_id
            for message in messages
            if message.gap_key and message.analysis_result_id is not None
        }
    )


def asked_in_round(messages: Sequence[ChatMessage], analysis_result_id: UUID) -> int:
    return sum(
        1
        for message in messages
        if message.gap_key and message.analysis_result_id == analysis_result_id
    )


def numbered_questions(messages: Sequence[ChatMessage]) -> list[tuple[str, ChatMessage]]:
    questions = [
        message
        for message in sorted(messages, key=lambda message: message.ordinal)
        if message.gap_key
    ]
    return [(followup_qa_id(index), question) for index, question in enumerate(questions, 1)]


def followup_history_from(
    messages: Sequence[ChatMessage],
) -> tuple[CaseFollowupExchange, ...]:
    replies = {
        message.in_reply_to_message_id: message
        for message in messages
        if message.in_reply_to_message_id is not None
    }
    return tuple(
        CaseFollowupExchange(
            qa_id=qa_id,
            gap_key=question.gap_key or "",
            question=question.content,
            answer=reply.content if (reply := replies.get(question.id)) else None,
        )
        for qa_id, question in numbered_questions(messages)
    )


def followup_qa_ids(messages: Sequence[ChatMessage]) -> dict[UUID, str]:
    questions = {question.id: qa_id for qa_id, question in numbered_questions(messages)}
    replies = {
        message.id: questions[message.in_reply_to_message_id]
        for message in messages
        if message.in_reply_to_message_id in questions
    }
    return questions | replies


def question_message(
    *,
    case_id: UUID,
    ordinal: int,
    gap: CaseAnalysisGap,
    analysis_result_id: UUID,
) -> ChatMessage:
    return ChatMessage(
        case_id=case_id,
        ordinal=ordinal,
        role="assistant",
        content=gap.clarification_question,
        message_kind="followup_question",
        gap_key=gap.gap_key,
        analysis_result_id=analysis_result_id,
    )


async def latest_question(db: AsyncSession, case_id: UUID) -> tuple[ChatMessage | None, bool]:
    question = await db.scalar(
        select(ChatMessage)
        .where(ChatMessage.case_id == case_id, ChatMessage.gap_key.is_not(None))
        .order_by(ChatMessage.ordinal.desc())
        .limit(1)
    )
    if question is None:
        return None, False
    reply = await db.scalar(
        select(ChatMessage.id).where(ChatMessage.in_reply_to_message_id == question.id).limit(1)
    )
    return question, reply is not None


async def analysed_since(db: AsyncSession, case_id: UUID, ordinal: int) -> bool:
    analysis = await db.scalar(
        select(ChatMessage.id)
        .join(CaseAnalysisResult, ChatMessage.analysis_result_id == CaseAnalysisResult.id)
        .where(
            ChatMessage.case_id == case_id,
            ChatMessage.ordinal > ordinal,
            ChatMessage.role == "assistant",
            ChatMessage.message_kind == "conversation",
            ChatMessage.in_reply_to_message_id.is_(None),
            CaseAnalysisResult.status == "validated",
        )
        .limit(1)
    )
    return analysis is not None


async def pending_question(db: AsyncSession, case_id: UUID) -> ChatMessage | None:
    question, answered = await latest_question(db, case_id)
    if question is None or answered or await analysed_since(db, case_id, question.ordinal):
        return None
    return question


async def last_question_awaiting_analysis(db: AsyncSession, case_id: UUID) -> ChatMessage | None:
    question, _ = await latest_question(db, case_id)
    if question is None or question.analysis_result_id is None:
        return None
    answer = await db.scalar(
        select(ChatMessage)
        .where(ChatMessage.in_reply_to_message_id == question.id)
        .order_by(ChatMessage.ordinal)
        .limit(1)
    )
    if answer is None or await analysed_since(db, case_id, answer.ordinal):
        return None
    return question


def answer_message(
    *,
    case_id: UUID,
    ordinal: int,
    content: str,
    question: ChatMessage,
    client_request_id: str | None,
) -> ChatMessage:
    return ChatMessage(
        case_id=case_id,
        ordinal=ordinal,
        role="user",
        content=content,
        message_kind="followup_answer",
        analysis_result_id=question.analysis_result_id,
        in_reply_to_message_id=question.id,
        client_request_id=client_request_id,
    )


def analysis_result_message(
    *,
    case_id: UUID,
    ordinal: int,
    trace: CaseAnalysisTrace,
    analysis_result_id: UUID,
) -> ChatMessage:
    return ChatMessage(
        case_id=case_id,
        ordinal=ordinal,
        role="assistant",
        content=trace.summary,
        message_kind="conversation",
        analysis_result_id=analysis_result_id,
        metadata_json=serialize_message_metadata({"analysis_trace": message_trace(trace)}),
    )


__all__ = [
    "analysis_result_message",
    "answer_message",
    "asked_gap_keys",
    "asked_in_round",
    "case_messages",
    "followup_history_from",
    "followup_qa_ids",
    "last_question_awaiting_analysis",
    "latest_question",
    "numbered_questions",
    "pending_question",
    "question_message",
    "rounds_asked",
]
