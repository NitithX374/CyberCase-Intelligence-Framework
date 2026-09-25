from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.analysis import CaseAnalysisResultRead
from app.schemas.message_metadata import MessageMetadata

MessageRole = Literal["user", "assistant"]
MessageKind = Literal["conversation", "followup_question", "followup_answer"]


class ChatMessageCreate(BaseModel):
    content: str = Field(default="")
    client_request_id: str | None = Field(default=None, max_length=255)


class ChatMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    case_id: UUID
    ordinal: int
    role: MessageRole
    content: str
    message_kind: MessageKind
    gap_key: str | None = None
    qa_id: str | None = None
    analysis_result_id: UUID | None
    in_reply_to_message_id: UUID | None = None
    metadata_json: MessageMetadata
    created_at: datetime


class CaseChatRead(BaseModel):
    case_id: UUID
    messages: list[ChatMessageRead] = Field(default_factory=list)
    pending_question_id: UUID | None = None


class CaseChatResponse(BaseModel):
    messages: list[ChatMessageRead]
    pending_question_id: UUID | None = None
    analysis: CaseAnalysisResultRead | None = None


__all__ = [
    "CaseChatResponse",
    "CaseChatRead",
    "ChatMessageCreate",
    "ChatMessageRead",
    "MessageKind",
    "MessageRole",
]
