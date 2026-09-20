"""Answering a question about an analysis that has already run.

One model call the caller is waiting for, so it happens in the request that
asked for it. The question is stored before the call and the answer after, with
no connection held across it.
"""

from __future__ import annotations

from collections.abc import Callable
from uuid import UUID

from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session
from app.models.analysis import CaseAnalysisResult
from app.models.chat import ChatMessage
from app.schemas.message_metadata import message_trace, serialize_message_metadata
from app.services.case_workflow.shared import (
    CaseWorkflowError,
    next_ordinal,
    owned_case,
)
from app.services.chat.case_answer import build_answer_context, generate_case_answer
from app.services.sources import load_case_source_bundle


async def answer_case_question(
    *,
    case_id: UUID,
    user_id: UUID | None,
    content: str,
    response_language: str,
    client_request_id: str | None = None,
    session_factory: Callable = async_session,
    answer_request=generate_case_answer,
) -> tuple[ChatMessage, ChatMessage]:
    """Store the question, answer it, store the answer. Returns both messages."""

    question_text = content.strip()
    if not question_text:
        raise CaseWorkflowError(
            "case_chat_content_empty",
            "Case Chat message is empty",
            status.HTTP_422_UNPROCESSABLE_CONTENT,
        )

    async with session_factory() as db, db.begin():
        case = await owned_case(db, case_id, user_id)
        already_sent = await sent_exchange(db, case.id, client_request_id)
        if already_sent is not None:
            return already_sent
        result = await db.scalar(
            select(CaseAnalysisResult).where(
                CaseAnalysisResult.id == case.latest_analysis_result_id,
                CaseAnalysisResult.case_id == case.id,
            )
        )
        if result is None:
            raise CaseWorkflowError(
                "analysis_required",
                "Analyze the Case before asking a Chat question",
                status.HTTP_412_PRECONDITION_FAILED,
            )
        bundle = await load_case_source_bundle(db, case_id=case.id, user_id=user_id)
        question = ChatMessage(
            case_id=case.id,
            ordinal=await next_ordinal(db, case.id),
            role="user",
            content=question_text,
            message_kind="conversation",
            analysis_result_id=result.id,
            client_request_id=client_request_id,
            metadata_json=serialize_message_metadata({"action": "conversation"}),
        )
        db.add(question)
        await db.flush()
        context = build_answer_context(
            result=result,
            question=question_text,
            history=await answer_history(db, case.id, result.id, question.ordinal),
            source_bundle=bundle,
        )
        question_id = question.id
        analysis_id = result.id

    output = await answer_request(
        context=context,
        source_bundle=bundle,
        user_message=answer_instruction(response_language),
    )

    async with session_factory() as db, db.begin():
        answer = ChatMessage(
            case_id=case_id,
            ordinal=await next_ordinal(db, case_id),
            role="assistant",
            content=output.answer.strip(),
            message_kind="conversation",
            analysis_result_id=analysis_id,
            in_reply_to_message_id=question_id,
            metadata_json=serialize_message_metadata(
                {"action": "conversation", "analysis_trace": message_trace(output.trace)}
                if output.trace
                else {"action": "conversation"}
            ),
        )
        db.add(answer)
        await db.flush()
        stored_question = await db.get(ChatMessage, question_id)
        await db.refresh(answer)
        return stored_question, answer


async def sent_exchange(
    db: AsyncSession, case_id: UUID, client_request_id: str | None
) -> tuple[ChatMessage, ChatMessage] | None:
    """The exchange this send already produced, when the client is retrying."""

    if client_request_id is None:
        return None
    question = await db.scalar(
        select(ChatMessage).where(
            ChatMessage.case_id == case_id,
            ChatMessage.client_request_id == client_request_id,
        )
    )
    if question is None:
        return None
    answer = await db.scalar(
        select(ChatMessage).where(ChatMessage.in_reply_to_message_id == question.id)
    )
    return (question, answer) if answer is not None else None


async def answer_history(
    db: AsyncSession, case_id: UUID, analysis_result_id: UUID, before_ordinal: int
) -> list[ChatMessage]:
    rows = await db.scalars(
        select(ChatMessage)
        .where(
            ChatMessage.case_id == case_id,
            ChatMessage.ordinal < before_ordinal,
            ChatMessage.message_kind == "conversation",
            ChatMessage.analysis_result_id == analysis_result_id,
        )
        .order_by(ChatMessage.ordinal.desc())
        .limit(12)
    )
    return list(reversed(list(rows)))


def answer_instruction(response_language: str) -> str:
    return "ตอบคำถามนี้" if response_language == "thai" else "Answer this question."


__all__ = [
    "answer_case_question",
    "answer_history",
    "answer_instruction",
    "sent_exchange",
]
