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
from app.services.chat.case_answer import build_answer_context, generate_case_answer
from app.services.sources.case_source_bundle import CaseSourceBundle, load_case_source_bundle
from app.services.sources.source_service import SourceError
from app.services.workflow.shared import (
    CaseWorkflowError,
    next_ordinal,
    owned_case,
)


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

        try:
            bundle = await load_case_source_bundle(db, case_id=case.id, user_id=user_id)
        except SourceError as error:
            if error.code == "case_sources_missing":
                bundle = CaseSourceBundle(revision=case.source_revision, sources=())
            else:
                raise
        question = ChatMessage(
            case_id=case.id,
            ordinal=await next_ordinal(db, case.id),
            role="user",
            content=question_text,
            message_kind="conversation",
            analysis_result_id=result.id if result is not None else None,
            client_request_id=client_request_id,
            metadata_json=serialize_message_metadata({"action": "conversation"}),
        )
        db.add(question)
        await db.flush()
        history = await answer_history(
            db, case.id, result.id if result is not None else None, question.ordinal
        )
        context = build_answer_context(
            result=result,
            question=question_text,
            history=history,
            source_bundle=bundle,
        )
        question_id = question.id
        analysis_id = result.id if result is not None else None

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
            analysis_result_id=analysis_id if analysis_id is not None else None,
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
    db: AsyncSession, case_id: UUID, analysis_result_id: UUID | None, before_ordinal: int
) -> list[ChatMessage]:
    query = select(ChatMessage).where(
        ChatMessage.case_id == case_id,
        ChatMessage.ordinal < before_ordinal,
        ChatMessage.message_kind == "conversation",
    )
    if analysis_result_id is None:
        query = query.where(ChatMessage.analysis_result_id.is_(None))
    else:
        query = query.where(ChatMessage.analysis_result_id == analysis_result_id)
    rows = await db.scalars(query.order_by(ChatMessage.ordinal.desc()).limit(12))
    return list(reversed(list(rows)))


def answer_instruction(response_language: str) -> str:
    return "ตอบคำถามนี้" if response_language == "thai" else "Answer this question."


__all__ = [
    "answer_case_question",
    "answer_history",
    "answer_instruction",
    "sent_exchange",
]
