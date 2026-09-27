from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.trace.claims import CaseSourceCitation
from app.trace.trace import CaseAnalysisTrace

ChatUnitBasis = Literal["case_fact", "interpretation", "technical", "general"]


ChatSuggestion = Literal["none", "add_source", "run_analysis"]


class ChatAnswerUnit(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1)
    basis: ChatUnitBasis
    claim_ids: list[str] = Field(default_factory=list)
    supporting_source_ids: list[str] = Field(default_factory=list)
    supporting_citations: list[CaseSourceCitation] = Field(default_factory=list)
    contradicting_source_ids: list[str] = Field(default_factory=list)
    contradicting_citations: list[CaseSourceCitation] = Field(default_factory=list)

    @property
    def cited(self) -> bool:
        return bool(self.supporting_citations or self.contradicting_citations)


@dataclass(frozen=True)
class CaseAnalysisOutput:
    answer: str
    trace: CaseAnalysisTrace | None
    units: tuple[ChatAnswerUnit, ...] = ()
    suggestion: ChatSuggestion = "none"


__all__ = [
    "CaseAnalysisOutput",
]
