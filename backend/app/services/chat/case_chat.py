from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from uuid import UUID

from fastapi import status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.case import Case
from app.models.case_run import CaseAnalysisResult, CaseRun
from app.models.chat import ChatMessage
from app.schemas.case_followups import CaseFollowUpAnswer
from app.schemas.chat import CaseChatRead, ChatMessageCreate, ChatMessageRead
from app.schemas.message_metadata import serialize_message_metadata
from app.services.chat.case_answer import generate_case_answer, load_case_answer_context
from app.services.followup.case_followup import (
    CaseFollowUpError,
    submit_followup_answer,
)


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
            selectinload(Case.latest_analysis_result),
        )
        .where(Case.id == case_id)
    )
    if case is None or case.user_id != user_id:
        raise CaseChatError("case_not_found", "Case not found", 404)
    messages = [ChatMessageRead.model_validate(message) for message in case.chat_messages]
    answered_ids = {
        message.in_reply_to_message_id
        for message in case.chat_messages
        if message.in_reply_to_message_id is not None
    }
    has_pending_followup = any(
        message.message_kind == "followup_question" and message.id not in answered_ids
        for message in case.chat_messages
    )
    if has_pending_followup:
        chat_status = "awaiting_followup"
    elif case.latest_analysis_result is not None or messages:
        chat_status = "answered"
    else:
        chat_status = "idle"
    return CaseChatRead(case_id=case.id, status=chat_status, messages=messages)


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
) -> tuple[ChatMessage, CaseRun | None]:
    case = await lock_case_chat(db, case_id, user_id)
    target_id = request.in_reply_to_message_id
    if target_id is None:
        raise CaseChatError(
            "followup_target_required",
            "in_reply_to_message_id is required when intent is followup_answer",
            status.HTTP_422_UNPROCESSABLE_CONTENT,
        )
    try:
        message, run = await submit_followup_answer(
            db,
            case_id=case.id,
            followup_id=target_id,
            user_id=user_id,
            answer=build_followup_answer(request),
            idempotency_key=request.request_key,
            response_language=request.response_language,
        )
    except CaseFollowUpError as error:
        raise CaseChatError(error.code, error.message, error.status_code) from error
    return message, run


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

    # ── Transaction A: Validation, User message persistence, Idempotency, Context loading ──
    case = await db.scalar(select(Case).where(Case.id == case_id))
    if case is None or case.user_id != user_id:
        raise CaseChatError("case_not_found", "Case not found", 404)

    context_result = await db.scalar(
        select(CaseAnalysisResult).where(
            CaseAnalysisResult.id == case.latest_analysis_result_id,
            CaseAnalysisResult.case_id == case.id,
            CaseAnalysisResult.status == "validated",
        )
    )
    if context_result is None:
        raise CaseChatError(
            "analysis_required",
            "Analyze the Case before asking a Chat question",
            status.HTTP_412_PRECONDITION_FAILED,
        )

    if context_result.evidence_revision != case.evidence_revision:
        raise CaseChatError(
            "analysis_stale",
            "Case analysis is stale; run analysis before asking",
            status.HTTP_409_CONFLICT,
        )

    if not isinstance(context_result.pipeline_config, dict) or not context_result.pipeline_config.get("version"):
        raise CaseChatError("case_ask_context_invalid", "Latest Case analysis configuration is unavailable")

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
            analysis_result_id=context_result.id,
            metadata_json=serialize_message_metadata(
                {
                    "action": "conversation",
                }
            ),
        )
        db.add(user_message)
        await db.flush()

    user_read = ChatMessageRead.model_validate(user_message)

    context, source_bundle = await load_case_answer_context(
        db,
        analysis_result_id=context_result.id,
        question_message_id=user_message.id,
    )

    # Commit Transaction A and release DB lock before external LLM call
    await db.commit()

    # ── Outside DB: LLM call with 45s timeout ──
    async with asyncio.timeout(45):
        output = await generate_case_answer(
            context=context,
            source_bundle=source_bundle,
            user_message=request,
        )

    # ── Transaction B: Persist Assistant reply ──
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
        content=output.answer,
        message_kind="conversation",
        analysis_result_id=context_result.id,
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
