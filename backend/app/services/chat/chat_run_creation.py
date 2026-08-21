import hashlib
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case_state import CaseStateVersion
from app.models.chat import ChatMessage, ChatRun, ChatThread
from app.schemas.chat import ChatMessageCreate
from app.services.chat.clarification_chain import reconstruct_clarification_chain
from app.services.followup import build_clarified_query


async def create_message_and_run(
    db: AsyncSession,
    thread_id: UUID,
    request: ChatMessageCreate,
) -> tuple[ChatMessage, ChatRun]:
    fingerprint_content = request.content
    if request.action is not None:
        fingerprint_content = f"{request.content}\x00{request.action}"
    request_fingerprint = hashlib.sha256(
        fingerprint_content.encode("utf-8")
    ).hexdigest()
    async with db.begin():
        statement = (
            select(ChatThread).where(ChatThread.id == thread_id).with_for_update()
        )
        result = await db.execute(statement)
        thread = result.scalar_one_or_none()

        if thread is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat thread not found",
            )
        existing_statement = select(ChatRun).where(
            ChatRun.thread_id == thread_id,
            ChatRun.idempotency_key == request.idempotency_key,
        )

        existing_result = await db.execute(existing_statement)
        existing_run = existing_result.scalar_one_or_none()
        if existing_run is not None:
            if existing_run.request_fingerprint != request_fingerprint:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Idempotency key was already used with different content",
                )
            existing_message = await db.get(
                ChatMessage, existing_run.request_message_id
            )
            if existing_run.status == "failed":
                active_run_statement = select(ChatRun).where(
                    ChatRun.thread_id == thread.id,
                    ChatRun.status.in_(("queued", "running")),
                )
                active_run_result = await db.execute(active_run_statement)
                if active_run_result.scalar_one_or_none() is not None:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Chat thread already has an active run",
                    )

                latest_run_result = await db.execute(
                    select(ChatRun.id)
                    .join(
                        ChatMessage,
                        ChatMessage.id == ChatRun.request_message_id,
                    )
                    .where(ChatRun.thread_id == thread.id)
                    .order_by(
                        ChatMessage.ordinal.desc(),
                        ChatRun.created_at.desc(),
                        ChatRun.id.desc(),
                    )
                    .limit(1)
                )
                latest_run_id = latest_run_result.scalar_one_or_none()
                transcript_advanced = (
                    existing_message is None
                    or thread.next_message_ordinal != existing_message.ordinal + 1
                )
                if transcript_advanced or latest_run_id != existing_run.id:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Failed chat run is no longer the latest request",
                    )

                existing_run.status = "queued"
                existing_run.error_code = None
                existing_run.error_message = None
                existing_run.started_at = None
                existing_run.finished_at = None
                existing_run.lease_owner = None
                existing_run.lease_expires_at = None
                thread.status = "processing"
                thread.active_rag_session_id = None
                await db.flush()
                await db.refresh(existing_run)
            return existing_message, existing_run

        active_run_statement = select(ChatRun).where(
            ChatRun.thread_id == thread.id,
            ChatRun.status.in_(("queued", "running")),
        )

        active_run_result = await db.execute(active_run_statement)
        active_run = active_run_result.scalar_one_or_none()

        if active_run is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Chat thread already has an active run",
            )

        ordinal = thread.next_message_ordinal
        rag_query = request.content
        followup_root_ordinal = ordinal
        followup_round = 0
        clarification_answer = (
            thread.status == "awaiting_followup"
            and thread.current_case_state_version_id is not None
        )
        post_answer_action = (
            request.action if thread.status == "answered" else None
        )
        if clarification_answer:
            post_answer_action = "add_case_info"
        post_answer_parent_version_id = None
        if thread.status == "answered":
            if post_answer_action is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail=(
                        "An explicit action of 'ask' or 'add_case_info' "
                        "is required after a terminal answer"
                    ),
                )
            if thread.current_case_state_version_id is None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="The answered thread has no current case state",
                )
            case_state_result = await db.execute(
                select(CaseStateVersion).where(
                    CaseStateVersion.id == thread.current_case_state_version_id,
                    CaseStateVersion.thread_id == thread.id,
                )
            )
            if case_state_result.scalar_one_or_none() is None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="The current case state could not be loaded",
                )
            post_answer_parent_version_id = thread.current_case_state_version_id
        if clarification_answer:
            case_state_result = await db.execute(
                select(CaseStateVersion).where(
                    CaseStateVersion.id == thread.current_case_state_version_id,
                    CaseStateVersion.thread_id == thread.id,
                )
            )
            if case_state_result.scalar_one_or_none() is None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="The current case state could not be loaded",
                )
            post_answer_parent_version_id = thread.current_case_state_version_id

        if thread.status == "awaiting_followup":
            history_result = await db.execute(
                select(ChatMessage)
                .where(ChatMessage.thread_id == thread.id)
                .order_by(ChatMessage.ordinal)
            )
            history = history_result.scalars().all()
            chain = reconstruct_clarification_chain(
                history,
                pending_answer=request.content,
            )
            if chain is not None:
                followup_root_ordinal = chain.root_ordinal
                followup_round = len(chain.exchanges)
                rag_query = build_clarified_query(
                    original_user_content=chain.original_user_content,
                    clarification_exchanges=chain.exchanges,
                )

        thread.active_rag_session_id = None
        thread.next_message_ordinal += 1
        thread.status = "processing"

        message = ChatMessage(
            thread_id=thread.id,
            ordinal=ordinal,
            content=request.content,
            role="user",
        )
        db.add(message)
        await db.flush()

        request_payload: dict[str, object] = {
            "content": request.content,
            "rag_query": rag_query,
            "followup_root_ordinal": followup_root_ordinal,
            "followup_round": followup_round,
        }
        if post_answer_action is not None:
            request_payload["action"] = post_answer_action
            if clarification_answer:
                request_payload["clarification_answer"] = True
            if post_answer_parent_version_id is not None:
                request_payload["case_state_version_id"] = str(
                    post_answer_parent_version_id
                )

        run = ChatRun(
            thread_id=thread.id,
            request_message_id=message.id,
            operation="query",
            input_rag_session_id=None,
            idempotency_key=request.idempotency_key,
            request_fingerprint=request_fingerprint,
            request_payload=request_payload,
        )
        db.add(run)
        await db.flush()
        await db.refresh(message)
        await db.refresh(run)
    return message, run


__all__ = ["create_message_and_run"]
