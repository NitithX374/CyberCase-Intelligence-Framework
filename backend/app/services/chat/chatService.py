from __future__ import annotations

import hashlib
import json
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import commit_dependency_transaction
from app.models.case import Case
from app.models.chat import ChatMessage, ChatRun, ChatThread
from app.schemas.chat import (
    ChatCaseLinkRead,
    ChatMessageCreate,
    ChatMessageRead,
    ChatRetryRequest,
    ChatThreadCreate,
    ChatThreadUpdate,
)
from app.services.cases.caseService import buildCaseWithChat

INTERRUPTED_CHAT_RUN_CODE = "chat_run_interrupted"


def computeRequestFingerprint(request: ChatMessageCreate) -> str:
    """Compute deterministic SHA-256 fingerprint for a chat message request."""
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


async def findRetryRequest(
    db: AsyncSession,
    thread: ChatThread,
) -> ChatRetryRequest | None:
    """Find and reconstruct retry request for an interrupted failed chat run."""
    result = await db.execute(
        select(ChatRun, ChatMessage)
        .join(ChatMessage, ChatMessage.id == ChatRun.request_message_id)
        .where(
            ChatRun.thread_id == thread.id,
            ChatRun.status == "failed",
            ChatRun.error_code == INTERRUPTED_CHAT_RUN_CODE,
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
            if computeRequestFingerprint(candidate) == run.request_fingerprint:
                original = candidate.model_dump(mode="json")
                break

    if original is None:
        return None

    return ChatRetryRequest(
        **original,
        request_ordinal=message.ordinal,
        clarification_answer=payload["clarification_answer"],
    )


class ChatService:
    """Service handling Chat thread lifecycle, access verification, and message retrieval."""

    def __init__(self, db: AsyncSession):
        self.db = db

    def verifyThreadAccess(
        self,
        thread: ChatThread,
        user_id: UUID | None,
    ) -> None:
        owner_id = thread.case.user_id if thread.case is not None else thread.user_id
        if owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat thread not found",
            )

    async def createThread(
        self,
        request: ChatThreadCreate,
        user_id: UUID | None = None,
    ) -> ChatThread:
        case, thread = buildCaseWithChat(request.title, user_id)
        self.db.add(case)
        self.db.add(thread)
        await self.db.commit()
        await self.db.refresh(thread)
        return thread

    async def ensureThreadForCase(
        self,
        case_id: UUID,
        user_id: UUID | None = None,
    ) -> ChatThread:
        await commit_dependency_transaction(self.db)
        async with self.db.begin():
            case_result = await self.db.execute(
                select(Case).where(Case.id == case_id).with_for_update()
            )
            case = case_result.scalar_one_or_none()
            if case is None or case.user_id != user_id:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "Case not found")

            thread_result = await self.db.execute(
                select(ChatThread).where(ChatThread.id == case.id).with_for_update()
            )
            thread = thread_result.scalar_one_or_none()
            if thread is None:
                thread = ChatThread(id=case.id, title=case.title, user_id=case.user_id)
                self.db.add(thread)
                await self.db.flush()
            return thread

    async def updateThread(
        self,
        thread_id: UUID,
        request: ChatThreadUpdate,
        user_id: UUID | None = None,
    ) -> ChatThread:
        thread = await self.db.get(
            ChatThread,
            thread_id,
            options=[selectinload(ChatThread.case)],
        )
        if thread is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat thread not found",
            )
        self.verifyThreadAccess(thread, user_id)

        thread.title = request.title
        if thread.case is not None:
            thread.case.title = request.title

        await self.db.commit()
        await self.db.refresh(thread)
        return thread

    async def deleteThread(
        self,
        thread_id: UUID,
        user_id: UUID | None = None,
    ) -> None:
        statement = (
            select(ChatThread)
            .options(selectinload(ChatThread.case))
            .where(ChatThread.id == thread_id)
            .with_for_update()
        )
        result = await self.db.execute(statement)
        thread = result.scalar_one_or_none()

        if thread is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat thread not found",
            )
        self.verifyThreadAccess(thread, user_id)

        await self.db.delete(thread)
        await self.db.commit()

    async def listThreads(
        self,
        user_id: UUID | None = None,
    ) -> list[ChatThread]:
        if user_id is not None:
            statement = (
                select(ChatThread)
                .where(ChatThread.user_id == user_id)
                .order_by(ChatThread.updated_at.desc())
            )
        else:
            statement = (
                select(ChatThread)
                .where(ChatThread.user_id.is_(None))
                .order_by(ChatThread.updated_at.desc())
            )

        result = await self.db.execute(statement)
        return list(result.scalars().all())

    async def getThread(
        self,
        thread_id: UUID,
        user_id: UUID | None = None,
    ) -> ChatThread:
        statement = (
            select(ChatThread)
            .options(
                selectinload(ChatThread.messages),
                selectinload(ChatThread.case),
            )
            .where(ChatThread.id == thread_id)
        )

        result = await self.db.execute(statement)
        thread = result.scalar_one_or_none()

        if thread is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat thread not found",
            )
        self.verifyThreadAccess(thread, user_id)

        thread.retry_request = await findRetryRequest(self.db, thread)
        return thread

    async def getCaseLink(
        self,
        thread_id: UUID,
        user_id: UUID | None = None,
    ) -> ChatCaseLinkRead:
        statement = (
            select(ChatThread)
            .options(selectinload(ChatThread.case))
            .where(ChatThread.id == thread_id)
        )
        result = await self.db.execute(statement)
        thread = result.scalar_one_or_none()
        if thread is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat thread not found",
            )
        self.verifyThreadAccess(thread, user_id)
        if thread.case is None:
            return ChatCaseLinkRead(
                thread_id=thread.id,
                status="historical_unavailable",
            )
        return ChatCaseLinkRead(
            thread_id=thread.id,
            status="linked",
            case_id=thread.case.id,
        )

    async def getRun(
        self,
        thread_id: UUID,
        run_id: UUID,
    ) -> ChatRun:
        statement = select(ChatRun).where(
            ChatRun.thread_id == thread_id, ChatRun.id == run_id
        )
        result = await self.db.execute(statement)
        run = result.scalar_one_or_none()
        if run is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat run not found",
            )
        return run

    async def listMessages(
        self,
        thread_id: UUID,
    ) -> list[ChatMessageRead]:
        statement = (
            select(ChatMessage)
            .where(ChatMessage.thread_id == thread_id)
            .order_by(ChatMessage.ordinal)
        )
        result = await self.db.execute(statement)
        return [
            ChatMessageRead.model_validate(message)
            for message in result.scalars().all()
        ]

    # Backward-compatibility method aliases
    _verify_thread_access = verifyThreadAccess
    create_thread = createThread
    ensure_thread_for_case = ensureThreadForCase
    update_thread = updateThread
    delete_thread = deleteThread
    list_threads = listThreads
    get_thread = getThread
    get_case_link = getCaseLink
    get_run = getRun
    list_messages = listMessages


# Compatibility alias for ChatMessageService
ChatMessageService = ChatService

# Compatibility function aliases
read_retry_request = findRetryRequest
historical_request_fingerprint = computeRequestFingerprint

__all__ = [
    "INTERRUPTED_CHAT_RUN_CODE",
    "ChatMessageService",
    "ChatService",
    "computeRequestFingerprint",
    "findRetryRequest",
    "historical_request_fingerprint",
    "read_retry_request",
]
