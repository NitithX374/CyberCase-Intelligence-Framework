from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.services.analysis.contracts import CaseAnalysisTrace

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
    summary: str
    trace_json: CaseAnalysisTrace | None
    retrieval_context_id: str | None
    pipeline_config: dict[str, object]
    external_context_json: dict[str, object] = Field(default_factory=dict)
    created_at: datetime
    freshness: AnalysisFreshness = "current"


class FollowupQuestionRead(BaseModel):
    message_id: UUID
    gap_id: str
    gap_key: str
    question: str


class AnalysisStepRead(BaseModel):
    status: Literal["need_followup", "completed"]
    round: int
    max_rounds: int
    stop_reason: str | None = None
    question: FollowupQuestionRead | None = None
    result: CaseAnalysisResultRead | None = None


__all__ = [
    "AnalysisFreshness",
    "AnalysisStepRead",
    "CaseAnalysisCreate",
    "CaseAnalysisResultRead",
    "FollowupQuestionRead",
]
