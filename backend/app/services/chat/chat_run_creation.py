from datetime import datetime, timezone
import hashlib
import json
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatMessage, ChatRun, ChatThread
from app.schemas.chat import ChatMessageCreate, ChatRetryRequest
from app.schemas.message_metadata import serialize_message_metadata
from app.services.chat.clarification_chain import reconstruct_clarification_chain
from app.services.chat.document_provenance import validated_document_source_payloads
from app.services.followup.stateful import clarification_answer_context
from app.services.workflow.run_recovery import INTERRUPTED_RUN_CODE


def request_fingerprint(request: ChatMessageCreate) -> str:
    source = f"{request.content}\x00{request.action or ''}"
    if request.document_sources:
        serialized_sources = json.dumps(
            [value.model_dump(mode="json") for value in request.document_sources],
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        source = f"{source}\x00{serialized_sources}"
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


async def requeue_interrupted_run(
    db: AsyncSession, thread: ChatThread, message: ChatMessage, run: ChatRun
) -> None:
    if run.status != "failed" or run.error_code != INTERRUPTED_RUN_CODE:
        return
    if message.ordinal != thread.next_message_ordinal - 1:
        raise HTTPException(409, "A newer message superseded this interrupted request")
    active = await db.execute(
        select(ChatRun.id).where(
            ChatRun.thread_id == thread.id,
            ChatRun.status.in_(("queued", "running")),
        )
    )
    if active.scalar_one_or_none() is not None:
        raise HTTPException(409, "Chat thread already has an active run")
    run.status = "queued"
    run.error_code = None
    run.error_message = None
    run.started_at = None
    run.finished_at = None
    run.lease_owner = None
    run.lease_expires_at = None
    run.updated_at = datetime.now(timezone.utc)
    thread.status = "processing"
    await db.flush()


async def read_retry_request(
    db: AsyncSession, thread: ChatThread
) -> ChatRetryRequest | None:
    result = await db.execute(
        select(ChatRun, ChatMessage)
        .join(
            ChatMessage,
            ChatMessage.id == ChatRun.request_message_id,
        )
        .where(
            ChatRun.thread_id == thread.id,
            ChatRun.status == "failed",
            ChatRun.error_code == INTERRUPTED_RUN_CODE,
            ChatMessage.ordinal == thread.next_message_ordinal - 1,
        )
    )
    row = result.one_or_none()
    if row is None:
        return None
    run, message = row
    payload = run.request_payload
    original = payload.get("retry_request")
    if original is None:
        for action in (None, "ask", "add_case_info"):
            candidate = ChatMessageCreate(
                idempotency_key=run.idempotency_key,
                content=message.content,
                action=action,
                document_sources=payload.get("document_sources", []),
            )
            if request_fingerprint(candidate) == run.request_fingerprint:
                original = candidate.model_dump(mode="json")
                break
    if original is None:
        return None
    return ChatRetryRequest(
        **original,
        request_ordinal=message.ordinal,
        clarification_answer=payload["clarification_answer"],
    )


async def create_message_and_run(
    db: AsyncSession,
    thread_id: UUID,
    request: ChatMessageCreate,
) -> tuple[ChatMessage, ChatRun]:
    fingerprint = request_fingerprint(request)
    async with db.begin():
        thread = await _locked_thread(db, thread_id)
        existing = await _existing_run(db, thread_id, request, fingerprint)
        if existing is not None:
            await requeue_interrupted_run(db, thread, *existing)
            return existing
        await _ensure_no_active_run(db, thread_id)
        action, evidence_kind = _resolve_action(thread, request.action)
        if request.document_sources and evidence_kind == "analyst_question":
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_CONTENT,
                "Document sources can only accompany case evidence",
            )
        ordinal = thread.next_message_ordinal
        root_ordinal, followup_round, clarification_context = await _followup_position(
            db, thread, request.content, ordinal
        )
        message_metadata: dict[str, object] = {"evidence_kind": evidence_kind}
        document_sources = validated_document_source_payloads(
            request.content,
            request.document_sources,
        )
        if document_sources:
            message_metadata["document_sources"] = document_sources
        if clarification_context is not None:
            message_metadata["clarification_context"] = clarification_context
        message = ChatMessage(
            thread_id=thread.id,
            ordinal=ordinal,
            content=request.content,
            role="user",
            metadata_json=serialize_message_metadata(message_metadata),
        )
        db.add(message)
        await db.flush()
        run_request_payload: dict[str, object] = {
            "retry_request": request.model_dump(mode="json"),
            "content": request.content,
            "action": action,
            "followup_root_ordinal": root_ordinal,
            "followup_round": followup_round,
            "clarification_answer": evidence_kind == "clarification_answer",
        }
        if document_sources:
            run_request_payload["document_sources"] = document_sources
        run = ChatRun(
            thread_id=thread.id,
            request_message_id=message.id,
            idempotency_key=request.idempotency_key,
            request_fingerprint=fingerprint,
            request_payload=run_request_payload,
        )
        db.add(run)
        thread.next_message_ordinal += 1
        thread.status = "processing"
        await db.flush()
        await db.refresh(message)
        await db.refresh(run)
        return message, run


async def _locked_thread(db: AsyncSession, thread_id: UUID) -> ChatThread:
    result = await db.execute(
        select(ChatThread).where(ChatThread.id == thread_id).with_for_update()
    )
    thread = result.scalar_one_or_none()
    if thread is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Chat thread not found")
    return thread


async def _existing_run(
    db: AsyncSession,
    thread_id: UUID,
    request: ChatMessageCreate,
    fingerprint: str,
) -> tuple[ChatMessage, ChatRun] | None:
    result = await db.execute(
        select(ChatRun).where(
            ChatRun.thread_id == thread_id,
            ChatRun.idempotency_key == request.idempotency_key,
        )
    )
    run = result.scalar_one_or_none()
    if run is None:
        return None
    if run.request_fingerprint != fingerprint:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Idempotency key was already used with different content",
        )
    message = await db.get(ChatMessage, run.request_message_id)
    if message is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Request message is missing")
    return message, run


async def _ensure_no_active_run(db: AsyncSession, thread_id: UUID) -> None:
    result = await db.execute(
        select(ChatRun.id).where(
            ChatRun.thread_id == thread_id,
            ChatRun.status.in_(("queued", "running")),
        )
    )
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Chat thread already has an active run",
        )


def _resolve_action(
    thread: ChatThread,
    requested_action: str | None,
) -> tuple[str, str]:
    if thread.status == "awaiting_followup":
        return "add_case_info", "clarification_answer"
    if thread.next_message_ordinal == 1:
        if requested_action == "ask":
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_CONTENT,
                "The first message must describe the case",
            )
        return "initial_analysis", "initial_case_narrative"
    if thread.status == "answered":
        if requested_action not in {"ask", "add_case_info"}:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_CONTENT,
                "An explicit action of 'ask' or 'add_case_info' is required",
            )
        kind = (
            "analyst_question"
            if requested_action == "ask"
            else "added_case_information"
        )
        return requested_action, kind
    return "add_case_info", "added_case_information"


async def _followup_position(
    db: AsyncSession,
    thread: ChatThread,
    pending_answer: str,
    ordinal: int,
) -> tuple[int, int, dict[str, str] | None]:
    if thread.status != "awaiting_followup":
        return ordinal, 0, None
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.thread_id == thread.id)
        .order_by(ChatMessage.ordinal)
    )
    chain = reconstruct_clarification_chain(
        list(result.scalars().all()), pending_answer=pending_answer
    )
    if chain is None:
        return ordinal, 0, None
    context = chain.pending_context
    if context is None:
        return chain.root_ordinal, len(chain.exchanges), None
    question_message_id = context.get("question_message_id")
    if question_message_id is None:
        return chain.root_ordinal, len(chain.exchanges), None
    return (
        chain.root_ordinal,
        len(chain.exchanges),
        clarification_answer_context(question_message_id, context),
    )


__all__ = [
    "create_message_and_run",
    "read_retry_request",
    "requeue_interrupted_run",
    "request_fingerprint",
]
