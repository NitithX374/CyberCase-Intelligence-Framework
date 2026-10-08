from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.trace.messages import ChatAnswerUnit, ChatSuggestion
from app.trace.trace import CaseAnalysisTrace

BASES = ("case_fact", "interpretation", "technical", "general")
SUGGESTIONS = ("none", "add_source", "run_analysis")


@dataclass(frozen=True)
class CaseAnalysisOutput:
    answer: str
    trace: CaseAnalysisTrace | None
    units: tuple[ChatAnswerUnit, ...] = ()
    suggestion: ChatSuggestion = "none"


class ChatReplyQuote(BaseModel):
    model_config = ConfigDict(extra="ignore")

    source_id: str = ""
    exact_quote: str = ""


class ChatReplyUnit(BaseModel):
    model_config = ConfigDict(extra="ignore")

    text: str = ""
    basis: Literal["case_fact", "interpretation", "technical", "general"] = "case_fact"
    claim_ids: list[str] = Field(default_factory=list)
    quotes: list[ChatReplyQuote] = Field(default_factory=list)

    @field_validator("text", mode="before")
    @classmethod
    def text_or_nothing(cls, value: object) -> object:
        return value if isinstance(value, str) else ""

    @field_validator("basis", mode="before")
    @classmethod
    def known_basis(cls, value: object) -> str:
        basis = str(value or "").strip().lower()
        return basis if basis in BASES else "case_fact"

    @field_validator("claim_ids", mode="before")
    @classmethod
    def claim_id_strings(cls, value: object) -> list[str]:
        if isinstance(value, str):
            value = [value]
        if not isinstance(value, (list, tuple)):
            return []
        return [item for item in value if isinstance(item, str) and item.strip()]

    @field_validator("quotes", mode="before")
    @classmethod
    def quote_records(cls, value: object) -> list[object]:
        if not isinstance(value, (list, tuple)):
            return []
        return [item for item in value if isinstance(item, Mapping)]


class ChatReply(BaseModel):
    model_config = ConfigDict(extra="ignore")

    units: list[ChatReplyUnit] = Field(default_factory=list)
    suggestion: Literal["none", "add_source", "run_analysis"] = "none"

    @field_validator("units", mode="before")
    @classmethod
    def unit_records(cls, value: object) -> list[object]:
        if not isinstance(value, (list, tuple)):
            return []
        return [item for item in value if isinstance(item, Mapping)]

    @field_validator("suggestion", mode="before")
    @classmethod
    def known_suggestion(cls, value: object) -> str:
        suggestion = str(value or "").strip().lower()
        return suggestion if suggestion in SUGGESTIONS else "none"
