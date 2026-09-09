from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from fastapi import HTTPException, status
from app.models.chat import ChatThread
from app.services.chat.chat_run_creation import read_retry_request
from app.schemas.chat import ChatThreadCreate, ChatThreadUpdate


class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _verify_thread_access(
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
        thread = ChatThread(
            title=request.title,
            user_id=user_id,
        )

        self.db.add(thread)
        await self.db.commit()
        await self.db.refresh(thread)

        return thread

    async def update_thread(
        self,
        thread_id: UUID,
        request: ChatThreadUpdate,
        user_id: UUID | None = None,
    ) -> ChatThread:
        thread = await self.db.get(ChatThread, thread_id)
        if thread is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat thread not found",
            )
        self._verify_thread_access(thread, user_id)

        thread.title = request.title

        await self.db.commit()
        await self.db.refresh(thread)
        return thread

    async def delete_thread(
        self,
        thread_id: UUID,
        user_id: UUID | None = None,
    ) -> None:
        statement = (
            select(ChatThread).where(ChatThread.id == thread_id).with_for_update()
        )
        result = await self.db.execute(statement)
        thread = result.scalar_one_or_none()

        if thread is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat thread not found",
            )
        self._verify_thread_access(thread, user_id)

        await self.db.delete(thread)
        await self.db.commit()

    async def list_threads(
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

    async def get_thread(
        self,
        thread_id: UUID,
        user_id: UUID | None = None,
    ) -> ChatThread:
        statement = (
            select(ChatThread)
            .options(selectinload(ChatThread.messages))
            .where(ChatThread.id == thread_id)
        )

        result = await self.db.execute(statement)
        thread = result.scalar_one_or_none()

        if thread is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat thread not found",
            )
        self._verify_thread_access(thread, user_id)

        thread.retry_request = await read_retry_request(self.db, thread)
        return thread
