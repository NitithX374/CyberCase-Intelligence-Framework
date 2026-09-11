from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from uuid import UUID

from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case
from app.models.caseClarification import CaseClarification
from app.models.caseMaterials import CaseEvidenceSnapshot
from app.models.caseRun import CaseAnalysisResult, CaseRun
from app.models.chat import ChatMessage, ChatThread
from app.schemas.caseClarifications import CaseClarificationAnswer
from app.schemas.caseRuns import CaseAnalysisCreate
from app.schemas.chat import ChatMessageCreate
from app.schemas.messageMetadata import serialize_message_metadata
from app.services.case_materials import CaseMaterialsService
from app.services.followup.caseClarification import (
    CaseClarificationError,
    find_answered_clarification,
    submit_clarification_answer,
)
from app.services.workflow.caseRunService import (
    CaseRunError,
    case_run_fingerprint,
    case_run_fingerprint_matches,
    enqueue_case_analysis,
    requeue_failed_case_run,
)


class CaseChatError(Exception):
    def __init__(self, code: str, message: str, status_code: int = status.HTTP_409_CONFLICT) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


async def lockCaseChat(
    db: AsyncSession,
    case_id: UUID,
    user_id: UUID | None,
) -> tuple[Case, ChatThread]:
    case = await db.scalar(select(Case).where(Case.id == case_id).with_for_update())
    if case is None or case.user_id != user_id:
        raise CaseChatError("case_not_found", "Case not found", 404)
    thread = await db.scalar(select(ChatThread).where(ChatThread.case_id == case.id).with_for_update())
    if thread is None:
        raise CaseChatError(
            "chat_not_open",
            "Open Chat from the Case before sending a message",
            404,
        )
    return case, thread


async def findPendingClarification(db: AsyncSession, case_id: UUID) -> CaseClarification | None:
    return await db.scalar(
        select(CaseClarification)
        .where(CaseClarification.case_id == case_id, CaseClarification.state == "pending")
        .order_by(CaseClarification.created_at.desc())
    )


async def findCaseRunByIdempotencyKey(
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
    if not await case_run_fingerprint_matches(db, run):
        raise CaseChatError("idempotency_conflict", "Case run fingerprint does not match the saved intent")
    if run.request_message_id is None:
        raise CaseChatError("case_chat_request_missing", "Case Chat request message is missing")
    message = await db.get(ChatMessage, run.request_message_id)
    if message is None:
        raise CaseChatError("case_chat_request_missing", "Case Chat request message is missing")
    return message, run


def buildChatRequestPayload(request: ChatMessageCreate, operation: str = "ask") -> dict[str, object]:
    return {
        "operation": operation,
        "content": request.content.strip(),
        "action": "ask",
        "response_language": request.response_language,
    }


def buildClarificationRequest(request: ChatMessageCreate) -> CaseClarificationAnswer:
    return CaseClarificationAnswer(
        answer=request.content,
        idempotency_key=request.idempotency_key,
        response_language=request.response_language,
    )


async def createCaseChatMessageAndRun(
    db: AsyncSession,
    *,
    case_id: UUID,
    user_id: UUID | None,
    request: ChatMessageCreate,
) -> tuple[ChatMessage, CaseRun]:
    if not request.content.strip():
        raise CaseChatError("case_chat_content_empty", "Case Chat message is empty", 422)
    case, thread = await lockCaseChat(db, case_id, user_id)
    if request.document_sources:
        raise CaseChatError(
            "case_chat_document_sources_unsupported",
            "Add documents from the Case materials workspace before analysis",
            status.HTTP_422_UNPROCESSABLE_CONTENT,
        )

    if request.intent == "clarification_answer":
        if request.clarification_id is None:
            raise CaseChatError(
                "clarification_id_required",
                "clarification_id is required when intent is clarification_answer",
                status.HTTP_422_UNPROCESSABLE_CONTENT,
            )
        clarification = await db.scalar(
            select(CaseClarification)
            .where(
                CaseClarification.id == request.clarification_id,
                CaseClarification.case_id == case.id,
            )
            .with_for_update()
        )
        if clarification is None:
            raise CaseChatError(
                "clarification_not_found",
                "Specified clarification was not found for this case",
                status.HTTP_404_NOT_FOUND,
            )
        if clarification.state == "answered":
            answered = await find_answered_clarification(
                db,
                case_id=case.id,
                request=buildClarificationRequest(request),
            )
            if answered is not None and answered.id == clarification.id:
                return await submitCaseClarification(db, case.id, user_id, answered, request)
            raise CaseChatError(
                "clarification_already_answered",
                "Clarification has already been answered",
                status.HTTP_409_CONFLICT,
            )
        if clarification.state != "pending":
            raise CaseChatError(
                "clarification_not_pending",
                f"Clarification is not pending (current state: {clarification.state})",
                status.HTTP_409_CONFLICT,
            )
        return await submitCaseClarification(db, case.id, user_id, clarification, request)

    expected_payload = buildChatRequestPayload(request, "ask")
    existing = await findCaseRunByIdempotencyKey(db, case.id, request.idempotency_key, expected_payload)
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
    return await createCaseAsk(db, case, thread, request)


async def submitCaseClarification(
    db: AsyncSession,
    case_id: UUID,
    user_id: UUID | None,
    clarification: CaseClarification,
    request: ChatMessageCreate,
) -> tuple[ChatMessage, CaseRun]:
    try:
        _, run = await submit_clarification_answer(
            db,
            case_id=case_id,
            clarification_id=clarification.id,
            user_id=user_id,
            request=buildClarificationRequest(request),
        )
    except CaseClarificationError as error:
        raise CaseChatError(error.code, error.message, error.status_code) from error
    message = await db.get(ChatMessage, clarification.answer_message_id)
    if message is None:
        raise CaseChatError("clarification_message_missing", "Clarification answer message is missing")
    return message, run


async def createCaseAsk(
    db: AsyncSession,
    case: Case,
    thread: ChatThread,
    request: ChatMessageCreate,
) -> tuple[ChatMessage, CaseRun]:
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
    snapshot = await db.get(CaseEvidenceSnapshot, context_result.snapshot_id)
    if snapshot is None or snapshot.case_id != case.id:
        raise CaseChatError("case_ask_context_invalid", "Latest Case analysis context is invalid")
    if not isinstance(context_result.pipeline_config, dict) or not context_result.pipeline_config.get("version"):
        raise CaseChatError("case_ask_context_invalid", "Latest Case analysis configuration is unavailable")
    message = ChatMessage(
        thread_id=thread.id,
        ordinal=thread.next_message_ordinal,
        role="user",
        content=request.content.strip(),
        message_kind="conversation",
        metadata_json=serialize_message_metadata(
            {
                "analysis_kind": "question_request",
                "analysis_state_scope": "response_scoped",
                "context_analysis_result_id": str(context_result.id),
                "evidence_snapshot_id": str(snapshot.id),
                "chat_action": {
                    "action": "ask",
                    "route": "case",
                    "rag_invoked": False,
                    "retrieval_context_reused": False,
                    "analysis_mode": "question_answer",
                    "prompt_version": context_result.pipeline_config.get("version"),
                },
            }
        ),
    )
    db.add(message)
    await db.flush()
    payload = {
        **buildChatRequestPayload(request, "ask"),
        "context_analysis_result_id": str(context_result.id),
        "context_snapshot_id": str(snapshot.id),
    }
    run = CaseRun(
        case_id=case.id,
        operation="ask",
        snapshot_id=snapshot.id,
        request_message_id=message.id,
        context_analysis_result_id=context_result.id,
        idempotency_key=request.idempotency_key,
        request_fingerprint=case_run_fingerprint(
            {"request": payload, "snapshot_id": str(snapshot.id), "pipeline": context_result.pipeline_config}
        ),
        request_payload=payload,
        pipeline_config=deepcopy(context_result.pipeline_config),
    )
    db.add(run)
    thread.next_message_ordinal += 1
    thread.status = "processing"
    thread.updated_at = datetime.now(timezone.utc)
    await db.flush()
    return message, run


__all__ = ["CaseChatError", "createCaseChatMessageAndRun"]
