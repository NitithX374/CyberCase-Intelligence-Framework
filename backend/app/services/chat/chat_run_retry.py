from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatMessage, ChatRun, ChatThread
from app.schemas.chat import ChatMessageCreate, ChatRetryRequest
from app.services.workflow.run_recovery import INTERRUPTED_RUN_CODE


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
            from app.services.chat.chat_run_creation import request_fingerprint

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
