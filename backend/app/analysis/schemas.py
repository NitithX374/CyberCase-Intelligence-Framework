from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.trace.trace import CaseAnalysisTrace

AnalysisFreshness = Literal["missing", "current", "stale"]


class CaseAnalysisResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    case_id: UUID
    source_revision: int
    schema_version: Literal["case_analysis_trace_v1"] = "case_analysis_trace_v1"
    status: Literal["validated"]
    summary: str
    trace_json: CaseAnalysisTrace | None
    pipeline_config: dict[str, object]
    external_context_json: dict[str, object] = Field(default_factory=dict)
    created_at: datetime
    freshness: AnalysisFreshness = "current"

    @computed_field
    @property
    def retrieval_context_id(self) -> str | None:
        return self.trace_json.retrieval_context_id if self.trace_json is not None else None


class AnalysisStepRead(BaseModel):
    status: Literal["need_followup", "completed"]
    result: CaseAnalysisResultRead | None = None


__all__ = [
    "AnalysisFreshness",
    "AnalysisStepRead",
    "CaseAnalysisResultRead",
]
