from typing import Literal

from pydantic import BaseModel, ConfigDict, TypeAdapter
from typing_extensions import TypedDict

from app.services.analysis.contracts import (
    CaseAnalysisClaim,
    CaseAnalysisMode,
    CaseAnalysisTrace,
    CaseGroundingReport,
)


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
