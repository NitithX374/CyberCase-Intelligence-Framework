"""Chat Thread, Message, and Run API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

ThreadStatus = Literal[
    "idle",
    "processing",
    "awaiting_followup",
    "answered",
    "failed",
]

MessageRole = Literal["user", "assistant"]

RunStatus = Literal[
    "queued",
    "running",
    "completed",
    "failed",
]

class ChatThreadCreate(BaseModel):
    title: str = Field(
        default="New chat",
        min_length=1,
        max_length=255,
    )


class ChatThreadUpdate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=255,
    )


class ChatMessageCreate(BaseModel):
    content: str = Field(min_length=1)
    idempotency_key: str = Field(
        min_length=1,
        max_length=255,
    )
    action: Literal["ask", "add_case_info"] | None = None


class ChatThreadRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    status: ThreadStatus
    created_at: datetime
    updated_at: datetime


class ChatMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    thread_id: UUID
    ordinal: int
    role: MessageRole
    content: str
    retrieval_context_id: str | None
    metadata_json: dict[str, Any]
    created_at: datetime


class ChatThreadDetail(ChatThreadRead):
    messages: list[ChatMessageRead] = Field(default_factory=list)


class ChatRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    thread_id: UUID
    request_message_id: UUID
    status: RunStatus
    error_code: str | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime


class ChatMessageAccepted(BaseModel):
    message: ChatMessageRead
    run: ChatRunRead


__all__ = [
    "ChatMessageAccepted",
    "ChatMessageCreate",
    "ChatMessageRead",
    "ChatRunRead",
    "ChatThreadCreate",
    "ChatThreadDetail",
    "ChatThreadRead",
    "ChatThreadUpdate",
    "MessageRole",
    "RunStatus",
    "ThreadStatus",
]
