from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatMessage
from app.schemas.message_metadata import message_trace, serialize_message_metadata
from app.services.analysis.contracts import (
    CaseAnalysisGap,
    CaseAnalysisTrace,
    CaseFollowupExchange,
    followup_qa_id,
)


async def rounds_asked(db: AsyncSession, case_id: UUID) -> int:
    return await db.scalar(
        select(func.count(func.distinct(ChatMessage.analysis_result_id))).where(
            ChatMessage.case_id == case_id, ChatMessage.gap_key.is_not(None)
        )
    )


async def asked_this_round(db: AsyncSession, analysis_result_id: UUID) -> set[str]:
    rows = await db.scalars(
        select(ChatMessage.gap_key).where(
            ChatMessage.analysis_result_id == analysis_result_id,
            ChatMessage.gap_key.is_not(None),
        )
    )
    return set(rows)


async def asked_gap_keys(db: AsyncSession, case_id: UUID) -> set[str]:
    rows = await db.scalars(
        select(ChatMessage.gap_key).where(
            ChatMessage.case_id == case_id, ChatMessage.gap_key.is_not(None)
        )
    )
    return {key for key in rows if key}


async def load_followup_history(
    db: AsyncSession, case_id: UUID
) -> tuple[CaseFollowupExchange, ...]:
    return followup_history_from(
        list(
            await db.scalars(
                select(ChatMessage)
                .where(ChatMessage.case_id == case_id)
                .order_by(ChatMessage.ordinal)
            )
        )
    )


def followup_history_from(
    messages: Sequence[ChatMessage],
) -> tuple[CaseFollowupExchange, ...]:
    messages = sorted(messages, key=lambda message: message.ordinal)
    replies = {
        message.in_reply_to_message_id: message
        for message in messages
        if message.in_reply_to_message_id is not None
    }
    questions = [message for message in messages if message.gap_key]
    return tuple(
        CaseFollowupExchange(
            qa_id=followup_qa_id(index),
            gap_key=question.gap_key or "",
            question=question.content,
            answer=reply.content if (reply := replies.get(question.id)) else None,
        )
        for index, question in enumerate(questions, start=1)
    )


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


async def pending_question(db: AsyncSession, case_id: UUID) -> ChatMessage | None:
    question = await db.scalar(
        select(ChatMessage)
        .where(ChatMessage.case_id == case_id, ChatMessage.gap_key.is_not(None))
        .order_by(ChatMessage.ordinal.desc())
    )
    if question is None:
        return None
    reply = await db.scalar(
        select(ChatMessage.id).where(ChatMessage.in_reply_to_message_id == question.id)
    )
    return None if reply else question


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
        metadata_json=serialize_message_metadata(
            {"action": "conversation", "analysis_trace": message_trace(trace)}
        ),
    )


__all__ = [
    "answer_message",
    "asked_gap_keys",
    "analysis_result_message",
    "followup_history_from",
    "asked_this_round",
    "load_followup_history",
    "pending_question",
    "question_message",
    "rounds_asked",
]
