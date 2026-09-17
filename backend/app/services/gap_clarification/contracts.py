from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from typing_extensions import TypedDict


class GapNextStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: Literal["ask", "resolved", "explicitly_unknown", "not_productive"]
    question: str | None = Field(default=None, max_length=2_000)
    target_information: str | None = Field(default=None, max_length=1_000)
    rationale_summary: str | None = Field(default=None, max_length=1_000)

    @field_validator("question", "target_information", "rationale_summary")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        trimmed = value.strip()
        return trimmed or None

    @model_validator(mode="after")
    def validate_action(self) -> "GapNextStep":
        if self.action == "ask":
            if not self.question:
                raise ValueError("ask decisions require a question")
            if not self.target_information:
                raise ValueError("ask decisions require target_information")
        elif self.question is not None or self.target_information is not None:
            raise ValueError(
                f"{self.action} decisions cannot include question or target_information"
            )
        return self


class GapAnswerInterpretation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    response_type: Literal[
        "case_fact",
        "scope_clarification",
        "explicitly_unknown",
        "skip",
        "unrelated",
    ]
    normalized_fact: str | None = Field(default=None, max_length=4_000)
    resolved_information: str | None = Field(default=None, max_length=2_000)
    gap_resolution: Literal["resolved", "partially_resolved", "unresolved"]

    @field_validator("normalized_fact", "resolved_information")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        trimmed = value.strip()
        return trimmed or None

    @model_validator(mode="after")
    def validate_fact(self) -> "GapAnswerInterpretation":
        if self.response_type == "case_fact" and not self.normalized_fact:
            raise ValueError("case_fact responses require normalized_fact")
        return self


class ClarificationResumeAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    content: str = Field(default="", max_length=400_000)
    disposition: Literal["answered", "unavailable", "skipped"] = "answered"
    request_key: str = Field(min_length=1, max_length=255)
    question_message_id: str

    @field_validator("content", "request_key")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        return value.strip()

    @model_validator(mode="after")
    def validate_content(self) -> "ClarificationResumeAnswer":
        if self.disposition == "answered" and not self.content:
            raise ValueError("answered clarification requires content")
        if self.disposition != "answered" and self.content:
            raise ValueError(
                f"{self.disposition} clarification cannot include content"
            )
        return self


class GapClarificationState(TypedDict, total=False):
    case_id: str
    source_analysis_id: str
    source_evidence_revision: int
    response_language: Literal["thai", "english"]
    gap_id: str
    pending_question_message_id: str | None
    latest_answer: dict[str, object] | None
    latest_interpretation: dict[str, object] | None
    attempt_count: int
    resolution_status: Literal[
        "unresolved",
        "resolved",
        "explicitly_unknown",
        "skipped",
        "not_productive",
        "stale",
    ]


__all__ = [
    "ClarificationResumeAnswer",
    "GapAnswerInterpretation",
    "GapClarificationState",
    "GapNextStep",
]
