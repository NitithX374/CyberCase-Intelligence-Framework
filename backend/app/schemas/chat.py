"""Chat Thread, Message, and Run API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.documentSources import (
    CaseNarrativeDocumentPageSpan as CaseNarrativeDocumentPageSpan,
    CaseNarrativeDocumentSource as CaseNarrativeDocumentSource,
)
from app.schemas.caseRuns import CaseRunRead
from app.schemas.messageMetadata import MessageMetadata

ThreadStatus = Literal[
    "idle",
    "processing",
    "awaiting_followup",
    "answered",
    "failed",
]

MessageRole = Literal["user", "assistant"]
MessageKind = Literal["conversation", "clarification_answer", "followup_question"]

ChatCaseLinkStatus = Literal["linked", "historical_unavailable"]

RunStatus = Literal[
    "queued",
    "running",
    "completed",
    "failed",
]


class ChatThreadCreate(BaseModel):
    title: str = Field(
        default="New case",
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
    action: Literal["ask"] | None = None
    intent: Literal["ask", "clarification_answer"] = "ask"
    clarification_id: UUID | None = None
    response_language: Literal["thai", "english"] = "english"
    document_sources: list[CaseNarrativeDocumentSource] = Field(
        default_factory=list,
        max_length=1,
    )


class ChatThreadRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID | None = None
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
    message_kind: MessageKind
    analysis_result_id: UUID | None
    metadata_json: MessageMetadata
    created_at: datetime


class ChatRetryRequest(ChatMessageCreate):
    request_ordinal: int = Field(ge=1)
    clarification_answer: bool


class ChatThreadDetail(ChatThreadRead):
    retry_request: ChatRetryRequest | None = None
    messages: list[ChatMessageRead] = Field(default_factory=list)


class ChatCaseLinkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    thread_id: UUID
    status: ChatCaseLinkStatus
    case_id: UUID | None = None


class CaseChatMessageAccepted(BaseModel):
    message: ChatMessageRead
    run: CaseRunRead


__all__ = [
    "CaseNarrativeDocumentPageSpan",
    "CaseNarrativeDocumentSource",
    "CaseChatMessageAccepted",
    "ChatMessageCreate",
    "ChatMessageRead",
    "ChatCaseLinkRead",
    "ChatCaseLinkStatus",
    "ChatThreadCreate",
    "ChatThreadDetail",
    "ChatThreadRead",
    "ChatThreadUpdate",
    "MessageRole",
    "MessageKind",
    "RunStatus",
    "ThreadStatus",
]
