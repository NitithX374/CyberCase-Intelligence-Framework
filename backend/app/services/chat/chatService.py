from __future__ import annotations

import inspect
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import commit_dependency_transaction
from app.models.case import Case
from app.models.caseRun import CaseRun
from app.models.chat import ChatMessage, ChatThread
from app.schemas.chat import (
    ChatCaseLinkRead,
    ChatThreadCreate,
    ChatThreadUpdate,
)


class ChatService:
    """Service handling Chat thread lifecycle, access verification, and message retrieval."""

    def __init__(self, db: AsyncSession):
        self.db = db

    def verify_thread_access(
        self,
        thread: ChatThread,
        user_id: UUID | None,
    ) -> None:
        if thread.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat thread not found",
            )

    async def create_thread(
        self,
        request: ChatThreadCreate,
        user_id: UUID | None = None,
    ) -> ChatThread:
        case = Case(title=request.title, user_id=user_id)
        self.db.add(case)
        await self.db.commit()
        await self.db.refresh(case)
        return case.chat_thread

    async def ensure_thread_for_case(
        self,
        case_id: UUID,
        user_id: UUID | None = None,
    ) -> ChatThread:
        await commit_dependency_transaction(self.db)
        async with self.db.begin():
            case = await self.db.scalar(
                select(Case)
                .options(selectinload(Case.chat_messages))
                .where(Case.id == case_id)
                .with_for_update()
            )
            if case is None or case.user_id != user_id:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "Case not found")
            return case.chat_thread

    async def update_thread(
        self,
        thread_id: UUID,
        request: ChatThreadUpdate,
        user_id: UUID | None = None,
    ) -> ChatThread:
        case_or_thread = None
        if hasattr(self.db, "get"):
            try:
                res = self.db.get(Case, thread_id)
                if inspect.isawaitable(res):
                    case_or_thread = await res
                else:
                    case_or_thread = res
            except Exception:
                pass
        if case_or_thread is None:
            exec_res = await self.db.execute(
                select(Case)
                .options(selectinload(Case.chat_messages))
                .where(Case.id == thread_id)
                .with_for_update()
            )
            case_or_thread = exec_res.scalar_one_or_none()
        if case_or_thread is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat thread not found",
            )
        if getattr(case_or_thread, "user_id", None) != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat thread not found",
            )

        case_or_thread.title = request.title
        await self.db.commit()
        if isinstance(case_or_thread, Case):
            await self.db.refresh(case_or_thread)
            return case_or_thread.chat_thread
        return case_or_thread

    async def delete_thread(
        self,
        thread_id: UUID,
        user_id: UUID | None = None,
    ) -> None:
        exec_res = await self.db.execute(
            select(Case).where(Case.id == thread_id).with_for_update()
        )
        case_or_thread = exec_res.scalar_one_or_none()
        if case_or_thread is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat thread not found",
            )
        if getattr(case_or_thread, "user_id", None) != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat thread not found",
            )

        if isinstance(case_or_thread, ChatThread):
            await self.db.delete(case_or_thread)
            await self.db.commit()
            return

        # Defensive check for retained runs referencing messages
        check = await self.db.execute(
            select(CaseRun.id)
            .join(ChatMessage, CaseRun.request_message_id == ChatMessage.id)
            .where(ChatMessage.case_id == case_or_thread.id)
            .limit(1)
        )
        referenced_run_id = check.scalar_one_or_none()
        if referenced_run_id is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "chat_thread_has_retained_runs",
                    "message": "Chat thread cannot be deleted while retained Case runs reference its messages",
                },
            )
        await self.db.execute(delete(ChatMessage).where(ChatMessage.case_id == case_or_thread.id))
        await self.db.commit()

    async def list_threads(
        self,
        user_id: UUID | None = None,
    ) -> list[ChatThread]:
        statement = (
            select(Case)
            .options(selectinload(Case.chat_messages))
        )
        if user_id is not None:
            statement = statement.where(Case.user_id == user_id)
        else:
            statement = statement.where(Case.user_id.is_(None))
        statement = statement.order_by(Case.updated_at.desc())

        result = await self.db.execute(statement)
        return [case.chat_thread for case in result.scalars().all()]

    async def get_thread(
        self,
        thread_id: UUID,
        user_id: UUID | None = None,
    ) -> ChatThread:
        exec_res = await self.db.execute(
            select(Case)
            .options(selectinload(Case.chat_messages))
            .where(Case.id == thread_id)
        )
        case_or_thread = exec_res.scalar_one_or_none()
        if case_or_thread is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat thread not found",
            )
        if getattr(case_or_thread, "user_id", None) != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat thread not found",
            )
        if isinstance(case_or_thread, ChatThread):
            return case_or_thread
        return case_or_thread.chat_thread

    async def get_case_link(
        self,
        thread_id: UUID,
        user_id: UUID | None = None,
    ) -> ChatCaseLinkRead:
        exec_res = await self.db.execute(select(Case).where(Case.id == thread_id))
        case_or_thread = exec_res.scalar_one_or_none()
        if case_or_thread is None or getattr(case_or_thread, "user_id", None) != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat thread not found",
            )
        linked_case = getattr(case_or_thread, "case", None)
        if isinstance(case_or_thread, ChatThread):
            if linked_case is not None:
                return ChatCaseLinkRead(
                    thread_id=case_or_thread.id,
                    status="linked",
                    case_id=linked_case.id,
                )
            return ChatCaseLinkRead(
                thread_id=case_or_thread.id,
                status="historical_unavailable",
                case_id=None,
            )
        return ChatCaseLinkRead(
            thread_id=case_or_thread.id,
            status="linked",
            case_id=case_or_thread.id,
        )

    async def get_run(
        self,
        thread_id: UUID,
        run_id: UUID,
    ) -> CaseRun:
        statement = select(CaseRun).where(
            CaseRun.case_id == thread_id, CaseRun.id == run_id
        )
        result = await self.db.execute(statement)
        run = result.scalar_one_or_none()
        if run is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case run not found",
            )
        return run


__all__ = [
    "ChatService",
]
