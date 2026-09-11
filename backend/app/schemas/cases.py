"""Case aggregate API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.chat import ThreadStatus

CaseProcessingStatus = Literal["idle", "queued", "running", "failed"]
CaseAnalysisFreshness = Literal["missing", "current", "stale"]


class CaseCreate(BaseModel):
    title: str = Field(default="New case", min_length=1, max_length=255)


class CaseUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=255)


class CaseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID | None = None
    title: str
    status: ThreadStatus
    chat_thread_id: UUID | None
    evidence_revision: int = 0
    latest_analysis_result_id: UUID | None = None
    active_run_id: UUID | None = None
    latest_run_id: UUID | None = None
    processing_status: CaseProcessingStatus = "idle"
    analysis_freshness: CaseAnalysisFreshness = "missing"
    created_at: datetime
    updated_at: datetime


__all__ = [
    "CaseAnalysisFreshness",
    "CaseCreate",
    "CaseRead",
    "CaseProcessingStatus",
    "CaseUpdate",
]
