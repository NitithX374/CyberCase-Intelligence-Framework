from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.reports import StructuredReport


class ReportSourceMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message_id: UUID
    ordinal: int = Field(gt=0)
    evidence_kind: Literal[
        "initial_case_narrative",
        "clarification_answer",
        "added_case_information",
    ]
    content: str = Field(min_length=1)


class AdmittedMitreRow(BaseModel):
    model_config = ConfigDict(extra="allow")

    technique_id: str = Field(pattern=r"^T\d{4}(?:\.\d{3})?$")
    name: str = ""
    reason: str = ""
    tactic: str = ""
    description: str = ""


class ReportInputSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    thread_id: UUID
    thread_title: str
    created_at: datetime
    source_messages: list[ReportSourceMessage] = Field(min_length=1)
    evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    analysis_message_id: UUID
    analysis_answer: str = Field(min_length=1)
    analysis_trace: dict[str, object] | None = None
    retrieval_context_id: str | None = Field(default=None, min_length=1, max_length=160)
    mitre_rows: list[AdmittedMitreRow] = Field(default_factory=list)
    unresolved_issues: list[str] = Field(default_factory=list)


class ReportServiceError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class ReportGenerationConflict(ReportServiceError):
    pass


class ReportNotFound(ReportServiceError):
    pass


class ReportValidationError(ValueError):
    pass


@dataclass(frozen=True)
class ReportRunResult:
    status: Literal["completed", "failed"]
    report: StructuredReport | None
    prompt_version: str
    provider: str
    model: str
    validation_errors: tuple[str, ...] = ()
    failure_code: str | None = None
    failure_message: str | None = None
    latency_ms: float | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None


def read_render_snapshot(
    raw: dict[str, object] | ReportInputSnapshot | None,
) -> ReportInputSnapshot | None:
    if raw is None:
        return None
    return ReportInputSnapshot.model_validate(raw)


__all__ = [
    "AdmittedMitreRow",
    "ReportGenerationConflict",
    "ReportInputSnapshot",
    "ReportNotFound",
    "ReportRunResult",
    "ReportServiceError",
    "ReportSourceMessage",
    "ReportValidationError",
    "read_render_snapshot",
]
