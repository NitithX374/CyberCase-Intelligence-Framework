"""Analysis request, result and step contracts.

An analysis is one step of a bounded clarification loop. A step either pauses
with a question for the reader or finishes with a result, and the envelope says
which — so the client never has to guess whether a body it was handed is a
finished analysis.
"""

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


class FollowupQuestionRead(BaseModel):
    """The one question the analysis is waiting on."""

    message_id: UUID
    gap_id: str
    gap_key: str
    question: str


class AnalysisStepRead(BaseModel):
    """What one analysis step produced.

    ``need_followup`` carries the question and no result: the analysis behind
    it is stored and readable from ``GET /analysis``, but it is not the case's
    answer yet, and handing it over as one invites a client to render a partial
    analysis as a finished one.
    """

    status: Literal["need_followup", "completed"]
    round: int
    max_rounds: int
    # Why the loop stopped asking. Set only when status is completed, and never
    # "sufficient": a spent budget and a settled case read differently.
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
