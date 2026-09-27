from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, field_validator
from typing_extensions import TypedDict

from app.analysis.schemas import CaseAnalysisResultRead
from app.chat.contracts import ChatAnswerUnit, ChatSuggestion
from app.trace.claims import CaseAnalysisClaim, CaseAnalysisMode
from app.trace.trace import CaseAnalysisTrace, CaseGroundingReport

MessageRole = Literal["user", "assistant"]
MessageKind = Literal["conversation", "followup_question", "followup_answer"]


class ChatMessageCreate(BaseModel):
    content: str = Field(default="")
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


class MessageAnalysisTrace(BaseModel):
    version: Literal["case_analysis_trace_v1"] = "case_analysis_trace_v1"
    validation_status: Literal["validated"] = "validated"
    analysis_mode: CaseAnalysisMode
    summary: str
    claims: list[CaseAnalysisClaim]
    grounding: CaseGroundingReport | None = None


class MessageMetadata(TypedDict, total=False):
    __pydantic_config__ = ConfigDict(extra="ignore")
    analysis_trace: MessageAnalysisTrace
    answer_units: list[ChatAnswerUnit]
    suggestion: ChatSuggestion


_metadata_adapter = TypeAdapter(MessageMetadata)


def message_trace(trace: CaseAnalysisTrace) -> MessageAnalysisTrace:
    return MessageAnalysisTrace(
        analysis_mode=trace.analysis_mode,
        summary=trace.summary,
        claims=trace.claims,
        grounding=trace.grounding,
    )


def serialize_message_metadata(value: MessageMetadata) -> dict[str, object]:
    validated = _metadata_adapter.validate_python(value)
    return _metadata_adapter.dump_python(validated, mode="json")


__all__ = [
    "CaseChatRead",
    "CaseChatResponse",
    "ChatMessageCreate",
    "ChatMessageRead",
    "MessageAnalysisTrace",
    "MessageKind",
    "MessageMetadata",
    "MessageRole",
    "_metadata_adapter",
    "message_trace",
    "serialize_message_metadata",
]
