from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

FollowUpState = Literal["pending", "answered", "superseded"]
FollowUpDisposition = Literal["answered", "unavailable", "skipped"]


class CaseFollowUpRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    case_id: UUID
    origin_analysis_result_id: UUID
    gap_key: str
    gap_id: str
    topic: str
    question: str
    metadata_json: dict[str, object]
    state: FollowUpState
    answer_evidence_source_id: UUID | None
    question_message_id: UUID | None
    answer_message_id: UUID | None
    answer_fingerprint: str | None
    answered_at: datetime | None
    created_at: datetime
    updated_at: datetime


class CaseFollowUpAnswer(BaseModel):
    gap_id: str = Field(min_length=1, max_length=80)
    answer: str | None = Field(default=None, max_length=400_000)
    disposition: FollowUpDisposition

    @field_validator("gap_id")
    @classmethod
    def normalize_gap_id(cls, value: str) -> str:
        return value.strip()

    @field_validator("answer")
    @classmethod
    def normalize_answer(cls, value: str | None) -> str | None:
        if value is None:
            return None
        trimmed = value.strip()
        return trimmed or None

    @model_validator(mode="after")
    def validate_disposition(self) -> "CaseFollowUpAnswer":
        if self.disposition == "answered" and not self.answer:
            raise ValueError("Answered follow-ups require an answer")
        if self.disposition != "answered" and self.answer:
            raise ValueError("Unavailable or skipped follow-ups cannot include an answer")
        return self


__all__ = [
    "CaseFollowUpAnswer",
    "CaseFollowUpRead",
    "FollowUpDisposition",
    "FollowUpState",
]
