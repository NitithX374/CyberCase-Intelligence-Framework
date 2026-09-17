from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from uuid import UUID

from fastapi import status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models.case import Case
from app.models.case_run import CaseRun
from app.models.chat import ChatMessage
from app.schemas.case_followups import CaseFollowUpAnswer
from app.schemas.chat import CaseChatRead, ChatMessageCreate, ChatMessageRead
from app.schemas.message_metadata import serialize_message_metadata
from app.services.case_analysis.case_analysis import request_case_reasoning
from app.services.case_analysis.contracts import CaseQuestionAnswerOutput
from app.services.case_analysis.pipeline_config import configured_pipeline
from app.services.case_materials import load_case_source_bundle
from app.services.chat.case_chat_context import load_case_chat_context
from app.services.gap_clarification import GapClarificationError, resume_gap_clarification


class CaseChatError(Exception):
    def __init__(self, code: str, message: str, status_code: int = status.HTTP_409_CONFLICT) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


async def lock_case_chat(
    db: AsyncSession,
    case_id: UUID,
    user_id: UUID | None,
) -> Case:
    case = await db.scalar(select(Case).where(Case.id == case_id).with_for_update())
    if case is None or case.user_id != user_id:
        raise CaseChatError("case_not_found", "Case not found", 404)
    return case


async def get_case_chat(
    db: AsyncSession,
    *,
    case_id: UUID,
    user_id: UUID | None,
) -> CaseChatRead:
    case = await db.scalar(
        select(Case)
        .options(
            selectinload(Case.chat_messages),
        )
        .where(Case.id == case_id)
    )
    if case is None or case.user_id != user_id:
        raise CaseChatError("case_not_found", "Case not found", 404)
    messages = [
        ChatMessageRead.model_validate(message)
        for message in sorted(case.chat_messages, key=lambda m: m.ordinal)
    ]
    answered_followup_ids = {
        message.in_reply_to_message_id
        for message in case.chat_messages
        if message.in_reply_to_message_id is not None
    }
    has_pending_followup = any(
        message.message_kind == "followup_question" and message.id not in answered_followup_ids
        for message in case.chat_messages
    )
    status_value = "awaiting_followup" if has_pending_followup else (
        "answered" if case.latest_analysis_result_id is not None else "idle"
    )
    return CaseChatRead(case_id=case.id, status=status_value, messages=messages)


def build_followup_answer(request: ChatMessageCreate) -> CaseFollowUpAnswer:
    if request.followup is None:
        raise CaseChatError(
            "followup_answers_required",
            "Follow-up answer is required",
            status.HTTP_422_UNPROCESSABLE_CONTENT,
        )
    return request.followup


async def submit_case_followup_answer(
    db: AsyncSession,
    *,
    case_id: UUID,
    user_id: UUID | None,
    request: ChatMessageCreate,
) -> tuple[ChatMessage, ChatMessage | None, ChatMessage | None, CaseRun | None]:
    if not request.request_key:
        raise CaseChatError(
            "idempotency_key_required",
            "client_request_id or idempotency_key is required",
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    target_id = request.in_reply_to_message_id
    if target_id is None:
        raise CaseChatError(
            "followup_target_required",
            "in_reply_to_message_id is required when intent is followup_answer",
            status.HTTP_422_UNPROCESSABLE_CONTENT,
        )
    answer = build_followup_answer(request)
    session_factory = async_sessionmaker(
        bind=db.bind,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    try:
        result = await resume_gap_clarification(
            case_id=case_id,
            user_id=user_id,
            question_id=target_id,
            content=answer.answer or "",
            disposition=answer.disposition,
            request_key=request.request_key,
            gap_id=answer.gap_id,
            clarification_session_id=request.clarification_session_id,
            session_factory=session_factory,
        )
    except GapClarificationError as error:
        raise CaseChatError(error.code, error.message, error.status_code) from error
    return result.answer_message, result.next_question, result.reply_message, result.run


async def ask_case(
    db: AsyncSession,
    *,
    case_id: UUID,
    user_id: UUID | None,
    request: ChatMessageCreate,
) -> tuple[ChatMessageRead, ChatMessageRead]:
    request_key = request.request_key
    if not request_key:
        raise CaseChatError(
            "idempotency_key_required",
            "client_request_id or idempotency_key is required",
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    if not request.content.strip():
        raise CaseChatError(
            "case_chat_content_empty",
            "Case Chat message is empty",
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    case = await db.scalar(select(Case).where(Case.id == case_id))
    if case is None or case.user_id != user_id:
        raise CaseChatError("case_not_found", "Case not found", 404)

    existing_user_msg = await db.scalar(
        select(ChatMessage).where(
            ChatMessage.case_id == case.id,
            ChatMessage.client_request_id == request_key,
        )
    )
    if existing_user_msg is not None:
        existing_assistant_msg = await db.scalar(
            select(ChatMessage).where(
                ChatMessage.case_id == case.id,
                ChatMessage.in_reply_to_message_id == existing_user_msg.id,
                ChatMessage.role == "assistant",
            )
        )
        if existing_assistant_msg is not None:
            return (
                ChatMessageRead.model_validate(existing_user_msg),
                ChatMessageRead.model_validate(existing_assistant_msg),
            )
        user_message = existing_user_msg
    else:
        next_ordinal = (
            await db.scalar(
                select(func.coalesce(func.max(ChatMessage.ordinal), 0)).where(
                    ChatMessage.case_id == case.id
                )
            )
            + 1
        )
        user_message = ChatMessage(
            case_id=case.id,
            client_request_id=request_key,
            ordinal=next_ordinal,
            role="user",
            content=request.content.strip(),
            message_kind="conversation",
            metadata_json=serialize_message_metadata(
                {
                    "action": "conversation",
                }
            ),
        )
        db.add(user_message)
        await db.flush()

    user_read = ChatMessageRead.model_validate(user_message)

    source_bundle = await load_case_source_bundle(
        db,
        case_id=case.id,
        user_id=user_id,
        require_sources=False,
    )
    await db.refresh(case)
    chat_context = await load_case_chat_context(
        db,
        case=case,
        current_message_ordinal=user_message.ordinal,
    )

    await db.commit()

    await asyncio.sleep(settings.chat_ask_start_delay_seconds)
    async with asyncio.timeout(45):
        output = await request_case_reasoning(
            mode="question_answer",
            source_bundle=source_bundle,
            pipeline_config=configured_pipeline().model_dump(mode="json"),
            question=user_read.content,
            user_message=user_read.content,
            technical_context=chat_context.technical_context,
            conversation_history=chat_context.conversation_history,
            analysis_context=chat_context.analysis_context,
            active_clarification=chat_context.active_clarification,
            current_evidence_revision=chat_context.current_evidence_revision,
            analysis_evidence_revision=chat_context.analysis_evidence_revision,
        )
    if not isinstance(output, CaseQuestionAnswerOutput):
        raise CaseChatError(
            "case_chat_answer_invalid",
            "Case Chat returned an invalid answer",
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    assistant_content = output.answer
    if output.clarification_question:
        assistant_content = f"{assistant_content}\n\n{output.clarification_question}"

    next_ordinal = (
        await db.scalar(
            select(func.coalesce(func.max(ChatMessage.ordinal), 0)).where(
                ChatMessage.case_id == case_id
            )
        )
        + 1
    )
    assistant_message = ChatMessage(
        case_id=case_id,
        ordinal=next_ordinal,
        role="assistant",
        content=assistant_content,
        message_kind="conversation",
        in_reply_to_message_id=user_read.id,
        metadata_json=serialize_message_metadata(
            {
                "action": "conversation",
                "execution_receipt": output.execution_receipt,
            }
        ),
    )
    db.add(assistant_message)

    refreshed_case = await db.get(Case, case_id)
    if refreshed_case is not None:
        refreshed_case.updated_at = datetime.now(timezone.utc)

    await db.commit()
    assistant_read = ChatMessageRead.model_validate(assistant_message)
    return user_read, assistant_read


__all__ = [
    "CaseChatError",
    "ask_case",
    "get_case_chat",
    "submit_case_followup_answer",
]
