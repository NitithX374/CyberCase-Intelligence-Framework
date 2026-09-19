"""Analysis request and result contracts."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.services.case_analysis.contracts import CaseAnalysisTrace

AnalysisFreshness = Literal["missing", "current", "stale"]


class CaseAnalysisCreate(BaseModel):
    response_language: Literal["thai", "english"] = "english"


class CaseAnalysisResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    case_id: UUID
    source_revision: int
    schema_version: str
    status: Literal["validated"]
    answer: str
    summary: str
    # The trace's own shape, so the OpenAPI carries it and the client does not
    # have to re-derive a contract this service already validated.
    trace_json: CaseAnalysisTrace | None
    retrieval_context_id: str | None
    pipeline_config: dict[str, object]
    external_context_json: dict[str, object] = Field(default_factory=dict)
    created_at: datetime
    freshness: AnalysisFreshness = "current"


__all__ = [
    "AnalysisFreshness",
    "CaseAnalysisCreate",
    "CaseAnalysisResultRead",
]
