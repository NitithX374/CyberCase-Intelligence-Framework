"""Case-owned chat message and status contracts."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.case_runs import CaseRunRead
from app.schemas.case_followups import CaseFollowUpAnswer
from app.schemas.message_metadata import MessageMetadata

CaseChatStatus = Literal[
    "idle",
    "processing",
    "awaiting_followup",
    "answered",
    "failed",
]
MessageRole = Literal["user", "assistant"]
MessageKind = Literal["conversation", "followup_question", "followup_answer"]


class ChatMessageCreate(BaseModel):
    content: str = Field(default="")
    idempotency_key: str = Field(min_length=1, max_length=255)
    intent: Literal["ask", "followup_answer"] = "ask"
    in_reply_to_message_id: UUID | None = None
    response_language: Literal["thai", "english"] = "english"
    followup: CaseFollowUpAnswer | None = None


class ChatMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    case_id: UUID
    ordinal: int
    role: MessageRole
    content: str
    retrieval_context_id: str | None
    message_kind: MessageKind
    analysis_result_id: UUID | None
    in_reply_to_message_id: UUID | None = None
    metadata_json: MessageMetadata
    created_at: datetime


class CaseChatRead(BaseModel):
    case_id: UUID
    status: CaseChatStatus = "idle"
    messages: list[ChatMessageRead] = Field(default_factory=list)


class CaseChatMessageAccepted(BaseModel):
    message: ChatMessageRead
    run: CaseRunRead | None = None


__all__ = [
    "CaseChatMessageAccepted",
    "CaseChatRead",
    "CaseChatStatus",
    "ChatMessageCreate",
    "ChatMessageRead",
    "MessageKind",
    "MessageRole",
]
