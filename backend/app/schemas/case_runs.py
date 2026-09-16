from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

CaseRunStatus = Literal["queued", "running", "completed", "failed"]
CaseRunOperation = Literal["analysis", "ask"]
AnalysisFreshness = Literal["missing", "current", "stale"]


class CaseAnalysisCreate(BaseModel):
    idempotency_key: str = Field(min_length=1, max_length=255)
    response_language: Literal["thai", "english"] = "english"
    expected_evidence_revision: int | None = Field(default=None, ge=0)


class CaseRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    case_id: UUID
    operation: CaseRunOperation
    evidence_revision: int
    request_message_id: UUID | None
    status: CaseRunStatus
    attempt_count: int
    error_code: str | None
    error_message: str | None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    updated_at: datetime


class CaseAnalysisResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    case_id: UUID
    run_id: UUID
    evidence_revision: int
    schema_version: str
    status: Literal["validated"]
    answer: str
    summary: str
    trace_json: dict[str, object] | None
    execution_receipt_json: dict[str, object] | None
    retrieval_context_id: str | None
    pipeline_config: dict[str, object]
    external_context_json: dict[str, object] = Field(default_factory=dict)
    created_at: datetime
    freshness: AnalysisFreshness = "current"


class CaseAnalysisAccepted(BaseModel):
    run: CaseRunRead


__all__ = [
    "AnalysisFreshness",
    "CaseAnalysisAccepted",
    "CaseAnalysisCreate",
    "CaseAnalysisResultRead",
    "CaseRunOperation",
    "CaseRunRead",
    "CaseRunStatus",
]
