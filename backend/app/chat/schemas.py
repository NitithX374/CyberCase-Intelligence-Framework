from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.analysis.schemas import CaseAnalysisResultRead
from app.trace.messages import MessageMetadata

MessageRole = Literal["user", "assistant"]
MessageKind = Literal["conversation", "followup_question", "followup_answer"]


class ChatMessageCreate(BaseModel):
    content: str = Field(default="", max_length=4_000)
    client_request_id: str | None = Field(default=None, max_length=255)

    @field_validator("client_request_id")
    @classmethod
    def refuse_nul(cls, value: str | None) -> str | None:
        if value is not None and "\x00" in value:
            raise ValueError("client_request_id cannot contain NUL")
        return value


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
    "CaseChatRead",
    "CaseChatResponse",
    "ChatMessageCreate",
    "ChatMessageRead",
    "MessageKind",
    "MessageRole",
]
