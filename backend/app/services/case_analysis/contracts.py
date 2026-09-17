from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.services.case_analysis.analysis_source_contracts import (
    CaseAnalysisMode,
    CaseAnalysisClaim,
    CaseAnalysisGap,
    CaseClaimType,
    CaseEpistemicStatus,
    CaseGeneratedUnit,
    CaseSourceCitation,
)
from app.services.case_analysis.analysis_trace_contracts import (
    CaseAnalysisFailureMetadata,
    CaseAnalysisTrace,
    CaseImpactItem,
    CaseInvolvedParty,
    CaseMitreAssociation,
    CaseProviderAnalysis,
    CaseTimelineItem,
)


class CaseAnalysisFailure(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


ResponseLanguage = Literal["thai", "english"]


def resolve_response_language(user_message: object) -> ResponseLanguage:
    if not isinstance(user_message, str) or not user_message.strip():
        raise ValueError("User message must be a non-empty string")
    if any("\u0e00" <= character <= "\u0e7f" for character in user_message):
        return "thai"
    if any(character.isascii() and character.isalpha() for character in user_message):
        return "english"
    raise ValueError("User message language must be Thai or English")


@dataclass(frozen=True)
class CaseQuestionAnswerOutput:
    answer: str
    cited_source_ids: tuple[str, ...]
    clarification_question: str | None = None
    execution_receipt: dict[str, object] | None = None


class CaseQuestionAnswerResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answer: str = Field(min_length=1, max_length=24_000)
    cited_source_ids: list[str] = Field(default_factory=list, max_length=64)
    clarification_question: str | None = Field(default=None, max_length=4_000)

    @field_validator("answer", mode="before")
    @classmethod
    def strip_answer(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @field_validator("clarification_question", mode="before")
    @classmethod
    def validate_clarification_question(cls, value: object) -> object:
        if value is None:
            return None
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Clarification question must be non-empty when supplied")
        return value.strip()


@dataclass(frozen=True)
class CaseAnalysisOutput:
    answer: str
    trace: CaseAnalysisTrace | None
    trace_failure: CaseAnalysisFailureMetadata | None = None
    execution_receipt: dict[str, object] | None = None
    followup_question: str | None = None
    followup_metadata: dict[str, object] | None = None


__all__ = [
    "CaseAnalysisClaim",
    "CaseAnalysisFailure",
    "CaseAnalysisFailureMetadata",
    "CaseAnalysisGap",
    "CaseAnalysisMode",
    "CaseAnalysisOutput",
    "CaseAnalysisTrace",
    "CaseClaimType",
    "CaseEpistemicStatus",
    "CaseSourceCitation",
    "CaseGeneratedUnit",
    "CaseImpactItem",
    "CaseInvolvedParty",
    "CaseMitreAssociation",
    "CaseProviderAnalysis",
    "CaseQuestionAnswerOutput",
    "CaseQuestionAnswerResponse",
    "CaseTimelineItem",
    "ResponseLanguage",
    "resolve_response_language",
]
