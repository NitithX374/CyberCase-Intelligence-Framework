from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatMessage, ChatRun
from app.schemas.chat import ChatMessageCreate, ChatMessageRead
from app.services.chat.chat_run_creation import create_message_and_run
from app.services.chat.clarification_chain import (
    ClarificationChain,
    reconstruct_clarification_chain,
)


class ChatMessageService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_message_and_run(
        self,
        thread_id: UUID,
        request: ChatMessageCreate,
    ) -> tuple[ChatMessage, ChatRun]:
        return await create_message_and_run(self.db, thread_id, request)

    async def get_run(
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

    async def list_messages(
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


__all__ = [
    "ChatMessageService",
    "ClarificationChain",
    "reconstruct_clarification_chain",
]
