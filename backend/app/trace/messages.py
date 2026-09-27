from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter
from typing_extensions import TypedDict

from app.trace.claims import CaseAnalysisClaim, CaseAnalysisMode, CaseSourceCitation
from app.trace.trace import CaseAnalysisTrace, CaseGroundingReport

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
    "ChatAnswerUnit",
    "ChatSuggestion",
    "ChatUnitBasis",
    "MessageAnalysisTrace",
    "MessageMetadata",
    "_metadata_adapter",
    "message_trace",
    "serialize_message_metadata",
]
