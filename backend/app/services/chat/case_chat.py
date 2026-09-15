from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from uuid import UUID

from fastapi import status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.case import Case
from app.models.case_run import CaseAnalysisResult, CaseRun
from app.models.chat import ChatMessage
from app.schemas.case_clarifications import CaseClarificationAnswer
from app.schemas.chat import CaseChatRead, ChatMessageCreate, ChatMessageRead
from app.schemas.message_metadata import serialize_message_metadata
from app.services.followup.case_clarification import (
    CaseClarificationError,
    submit_clarification_answer,
)
from app.services.workflow.case_run_service import (
    CaseRunError,
    requeue_failed_case_run,
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
            selectinload(Case.case_runs),
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
    latest_run = max(case.case_runs, key=lambda item: item.created_at, default=None)
    if latest_run is not None and latest_run.status in {"queued", "running"}:
        chat_status = "processing"
    elif latest_run is not None and latest_run.status == "failed":
        chat_status = "failed"
    elif has_pending_followup:
        chat_status = "awaiting_followup"
    elif case.latest_analysis_result is not None or messages:
        chat_status = "answered"
    else:
        chat_status = "idle"
    return CaseChatRead(case_id=case.id, status=chat_status, messages=messages)


async def find_case_run_by_idempotency_key(
    db: AsyncSession,
    case_id: UUID,
    idempotency_key: str,
    expected_payload: dict[str, object],
) -> tuple[ChatMessage, CaseRun] | None:
    run = await db.scalar(
        select(CaseRun)
        .where(CaseRun.case_id == case_id, CaseRun.idempotency_key == idempotency_key)
        .with_for_update()
    )
    if run is None:
        return None
    if not isinstance(run.request_payload, dict) or any(
        run.request_payload.get(key) != value for key, value in expected_payload.items()
    ):
        raise CaseChatError("idempotency_conflict", "Idempotency key was already used with different intent")
    if run.request_message_id is None:
        raise CaseChatError("case_chat_request_missing", "Case Chat request message is missing")
    message = await db.get(ChatMessage, run.request_message_id)
    if message is None:
        raise CaseChatError("case_chat_request_missing", "Case Chat request message is missing")
    return message, run


def build_chat_request_payload(request: ChatMessageCreate, operation: str = "ask") -> dict[str, object]:
    return {
        "operation": operation,
        "content": request.content.strip(),
        "action": "conversation",
        "response_language": request.response_language,
    }


def build_clarification_request(request: ChatMessageCreate) -> CaseClarificationAnswer:
    return CaseClarificationAnswer(
        answer=request.content,
        idempotency_key=request.idempotency_key,
        response_language=request.response_language,
    )


async def create_case_chat_message_and_run(
    db: AsyncSession,
    *,
    case_id: UUID,
    user_id: UUID | None,
    request: ChatMessageCreate,
) -> tuple[ChatMessage, CaseRun]:
    if not request.content.strip():
        raise CaseChatError("case_chat_content_empty", "Case Chat message is empty", 422)
    case = await lock_case_chat(db, case_id, user_id)

    if request.intent == "followup_answer":
        target_id = request.in_reply_to_message_id
        if target_id is None:
            raise CaseChatError(
                "followup_target_required",
                "in_reply_to_message_id is required when intent is followup_answer",
                status.HTTP_422_UNPROCESSABLE_CONTENT,
            )
        try:
            clarification_read, run = await submit_clarification_answer(
                db,
                case_id=case.id,
                clarification_id=target_id,
                user_id=user_id,
                request=build_clarification_request(request),
            )
        except CaseClarificationError as error:
            raise CaseChatError(error.code, error.message, error.status_code) from error
        message = await db.get(ChatMessage, clarification_read.answer_message_id)
        if message is None:
            raise CaseChatError("case_chat_message_missing", "Clarification answer message is missing")
        return message, run

    expected_payload = build_chat_request_payload(request, "ask")
    existing = await find_case_run_by_idempotency_key(db, case.id, request.idempotency_key, expected_payload)
    if existing is not None:
        try:
            await requeue_failed_case_run(db, case, existing[1])
        except CaseRunError as error:
            raise CaseChatError(error.code, error.message, error.status_code) from error
        return existing
    active = await db.scalar(
        select(CaseRun.id).where(
            CaseRun.case_id == case.id,
            CaseRun.status.in_(("queued", "running")),
        )
    )
    if active is not None:
        raise CaseChatError("case_run_active", "Case already has an active analysis run")

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
    if not isinstance(context_result.pipeline_config, dict) or not context_result.pipeline_config.get("version"):
        raise CaseChatError("case_ask_context_invalid", "Latest Case analysis configuration is unavailable")
    next_ordinal = (
        await db.scalar(
            select(func.coalesce(func.max(ChatMessage.ordinal), 0)).where(
                ChatMessage.case_id == case.id
            )
        )
        + 1
    )
    message = ChatMessage(
        case_id=case.id,
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
    db.add(message)
    await db.flush()
    payload = {
        **build_chat_request_payload(request, "ask"),
    }
    run = CaseRun(
        case_id=case.id,
        operation="ask",
        evidence_revision=case.evidence_revision,
        request_message_id=message.id,
        idempotency_key=request.idempotency_key,
        request_payload=payload,
        pipeline_config=deepcopy(context_result.pipeline_config),
    )
    db.add(run)
    case.updated_at = datetime.now(timezone.utc)
    await db.flush()
    return message, run


__all__ = ["CaseChatError", "create_case_chat_message_and_run"]
