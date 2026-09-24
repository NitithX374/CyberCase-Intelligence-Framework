from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

CaseAnalysisFreshness = Literal["missing", "current", "stale"]
CaseStatus = Literal["idle", "answered"]


class CaseCreate(BaseModel):
    title: str = Field(default="New case", min_length=1, max_length=255)


class CaseUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=255)


class CaseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID | None = None
    title: str
    status: CaseStatus
    source_revision: int = 0
    latest_analysis_result_id: UUID | None = None
    analysis_freshness: CaseAnalysisFreshness = "missing"
    created_at: datetime
    updated_at: datetime


__all__ = [
    "CaseAnalysisFreshness",
    "CaseCreate",
    "CaseRead",
    "CaseStatus",
    "CaseUpdate",
]
