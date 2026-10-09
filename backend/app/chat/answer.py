from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from uuid import UUID, uuid4

from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.analysis.language import case_language, question_language
from app.analysis.latest import recorded_technical_context
from app.cases.ownership import owned_case
from app.cases.service import analysis_freshness
from app.chat.answer_contract import CaseAnalysisOutput
from app.chat.compose import generate_case_answer
from app.database import async_session
from app.errors import CaseAnalysisFailure, CaseWorkflowError
from app.followup.conversation import case_messages, followup_history_from, next_ordinal
from app.models.analysis_result import CaseAnalysisResult
from app.models.chat_message import ChatMessage
from app.sources.bundle import WITH_SOURCES, CaseSourceBundle, analysable_bundle
from app.sources.service import SourceError
from app.trace.messages import MessageMetadata, message_trace, serialize_message_metadata

_answering: set[UUID] = set()


@contextmanager
def answering(question_id: UUID) -> Iterator[None]:
    _answering.add(question_id)
    try:
        yield
    finally:
        _answering.discard(question_id)


def being_answered(question_id: UUID) -> bool:
    return question_id in _answering


async def answer_case_question(
    *,
    case_id: UUID,
    user_id: UUID | None,
    content: str,
    client_request_id: str | None = None,
    session_factory: Callable = async_session,
    answer_request=generate_case_answer,
) -> tuple[ChatMessage, ChatMessage]:
    question_id = uuid4()
    with answering(question_id):
        await record_question(
            case_id=case_id,
            user_id=user_id,
            question_id=question_id,
            content=content,
            client_request_id=client_request_id,
            session_factory=session_factory,
        )
        return await reply_to(case_id, user_id, question_id, session_factory, answer_request)


async def answer_recorded_question(
    *,
    case_id: UUID,
    user_id: UUID | None,
    question_id: UUID,
    session_factory: Callable = async_session,
    answer_request=generate_case_answer,
) -> tuple[ChatMessage, ChatMessage]:
    with answering(question_id):
        return await reply_to(case_id, user_id, question_id, session_factory, answer_request)


async def record_question(
    *,
    case_id: UUID,
    user_id: UUID | None,
    question_id: UUID,
    content: str,
    client_request_id: str | None,
    session_factory: Callable,
) -> None:
    question_text = message_text(content)
    async with session_factory() as db, db.begin():
        case = await owned_case(db, case_id, user_id, lock=True)
        db.add(
            ChatMessage(
                id=question_id,
                case_id=case.id,
                ordinal=await next_ordinal(db, case.id),
                role="user",
                content=question_text,
                message_kind="conversation",
                analysis_result_id=case.latest_analysis_result_id,
                client_request_id=client_request_id,
            )
        )


def message_text(content: str) -> str:
    text = content.replace("\x00", "").strip()
    if not text:
        raise CaseWorkflowError(
            "case_chat_content_empty",
            "Case Chat message is empty",
            status.HTTP_422_UNPROCESSABLE_CONTENT,
        )
    return text


async def reply_to(
    case_id: UUID,
    user_id: UUID | None,
    question_id: UUID,
    session_factory: Callable,
    answer_request,
) -> tuple[ChatMessage, ChatMessage]:
    async with session_factory() as db, db.begin():
        case = await owned_case(db, case_id, user_id, lock=True, options=WITH_SOURCES)
        question = await db.get(ChatMessage, question_id)
        analysis_id = question.analysis_result_id
        result = await db.get(CaseAnalysisResult, analysis_id) if analysis_id is not None else None
        try:
            bundle = analysable_bundle(case)
        except SourceError as error:
            if error.code != "case_sources_missing":
                raise
            bundle = CaseSourceBundle(revision=case.source_revision, sources=())
        history = await answer_history(db, case.id, analysis_id, question.ordinal)
        followups = followup_history_from(await case_messages(db, case.id))
        freshness = analysis_freshness(case, result)

    try:
        output = await answer_request(
            result=result,
            question=question.content,
            history=history,
            sources=bundle,
            language=question_language(question.content, case_language(bundle)),
            followups=followups,
            technical_context=recorded_technical_context(result) if result is not None else None,
            analysis_status="none" if freshness == "missing" else freshness,
        )
    except CaseAnalysisFailure as error:
        raise CaseAnalysisFailure(error.code, error.message, status.HTTP_502_BAD_GATEWAY) from error

    async with session_factory() as db, db.begin():
        await owned_case(db, case_id, user_id, lock=True)
        answer = ChatMessage(
            case_id=case_id,
            ordinal=await next_ordinal(db, case_id),
            role="assistant",
            content=output.answer.strip(),
            message_kind="conversation",
            analysis_result_id=analysis_id,
            in_reply_to_message_id=question_id,
            metadata_json=serialize_message_metadata(answer_metadata(output)),
        )
        db.add(answer)
        await db.flush()
        await db.refresh(answer)
        return question, answer


def answer_metadata(output: CaseAnalysisOutput) -> MessageMetadata:
    metadata: MessageMetadata = {}
    if output.trace is not None:
        metadata["analysis_trace"] = message_trace(output.trace)
    if output.units:
        metadata["answer_units"] = list(output.units)
    if output.suggestion != "none":
        metadata["suggestion"] = output.suggestion
    return metadata


async def answer_history(
    db: AsyncSession, case_id: UUID, analysis_result_id: UUID | None, before_ordinal: int
) -> list[ChatMessage]:
    query = select(ChatMessage).where(
        ChatMessage.case_id == case_id,
        ChatMessage.ordinal < before_ordinal,
        ChatMessage.message_kind == "conversation",
    )
    query = query.where(ChatMessage.analysis_result_id == analysis_result_id)
    rows = await db.scalars(query.order_by(ChatMessage.ordinal.desc()).limit(12))
    return list(reversed(list(rows)))


__all__ = [
    "answer_case_question",
    "answer_history",
    "answer_recorded_question",
    "being_answered",
    "message_text",
]
