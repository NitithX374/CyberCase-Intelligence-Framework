from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.caseRuns import CaseRunRead

ClarificationState = Literal["pending", "answered", "superseded"]


class CaseClarificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    case_id: UUID
    origin_analysis_result_id: UUID
    origin_snapshot_id: UUID
    gap_key: str
    gap_id: str
    topic: str
    question: str
    metadata_json: dict[str, object]
    state: ClarificationState
    answer_evidence_source_id: UUID | None
    question_message_id: UUID | None
    answer_message_id: UUID | None
    answer_fingerprint: str | None
    answered_at: datetime | None
    created_at: datetime
    updated_at: datetime


class CaseClarificationAnswer(BaseModel):
    answer: str = Field(min_length=1, max_length=400_000)
    idempotency_key: str = Field(min_length=1, max_length=255)
    response_language: Literal["thai", "english"] = "english"


class CaseClarificationAccepted(BaseModel):
    clarification: CaseClarificationRead
    run: CaseRunRead


__all__ = [
    "CaseClarificationAccepted",
    "CaseClarificationAnswer",
    "CaseClarificationRead",
    "ClarificationState",
]
