from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.reports import StructuredReport
from app.services.extraction.llm_extraction import CaseState

REPORT_VERSION = "preliminary_analysis_report_v1"
REPORT_STATUS = "provisional_unverified"
REPORT_TEMPLATE_PROVIDER = "deterministic"
REPORT_TEMPLATE_MODEL = "preliminary_analysis_template_v1"
REPORT_TEMPLATE_PROMPT_VERSION = "chat_preliminary_analysis_template_v1"

_TEMPLATE_SECTION_ITEM_LIMIT = 32
_TEMPLATE_CLAIM_LIMIT = 96
_TEMPLATE_TEXT_LIMIT = 3_800

MITRE_ID_RE = re.compile(r"^T\d{4}(?:\.\d{3})?$")
INCIDENT_ID_RE = re.compile(r"^(?:E|T)-[A-Za-z0-9][A-Za-z0-9_-]*$")
INCIDENT_PROSE_RE = re.compile(r"\b(?:E|T)-[A-Za-z0-9][A-Za-z0-9_-]*\b")
MITRE_PROSE_RE = re.compile(r"\bT\d{4}(?:\.\d{3})?\b")
SECRET_RE = re.compile(
    r"(?i)\b(?:sk-ant|sk-proj|sk)-[A-Za-z0-9_-]{20,}\b|"
    r"\b(?:api[_-]?key|x-api-key|authorization|bearer)\s*[:=]\s*[^\s,]+|"
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----"
)

class ReportSourceMessage(BaseModel):
    """User-authored source text admitted into the frozen report snapshot."""

    model_config = ConfigDict(extra="forbid")

    message_id: UUID
    ordinal: int = Field(gt=0)
    source_type: Literal["user_case_statement", "clarification_answer"]
    content: str = Field(min_length=1, max_length=20_000)

    @field_validator("content")
    @classmethod
    def normalize_content(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("source message content cannot be empty")
        return value


class AdmittedMitreRow(BaseModel):
    """A valid MITRE row already persisted by the RAG chat path."""

    model_config = ConfigDict(extra="forbid")

    technique_id: str = Field(min_length=1, max_length=32)
    name: str = Field(min_length=1, max_length=500)
    entity_type: str = Field(default="", max_length=120)
    tactic: str | None = Field(default=None, max_length=200)
    score: float | None = None
    source: Literal["vector", "graph"] = "vector"
    relevance: Literal["cited_in_answer", "retrieved_only"] = "retrieved_only"
    description: str = Field(default="", max_length=4_000)
    mitre_url: str | None = Field(default=None, max_length=1_000)


class ReportInputSnapshot(BaseModel):
    """Complete server-built input for one report attempt."""

    model_config = ConfigDict(extra="forbid")

    thread_id: UUID
    thread_title: str = Field(min_length=1, max_length=255)
    extraction_id: UUID
    extraction_version: str = Field(min_length=1, max_length=80)
    source_messages: list[ReportSourceMessage] = Field(min_length=1)
    extraction: CaseState
    mitre_rows: list[AdmittedMitreRow] = Field(default_factory=list, max_length=64)
    metadata: dict[str, object] = Field(default_factory=dict)

    @field_validator("source_messages")
    @classmethod
    def validate_source_order(
        cls,
        value: list[ReportSourceMessage],
    ) -> list[ReportSourceMessage]:
        if len({message.message_id for message in value}) != len(value):
            raise ValueError("report source message IDs must be unique")
        if len({message.ordinal for message in value}) != len(value):
            raise ValueError("report source message ordinals must be unique")
        if [message.ordinal for message in value] != sorted(
            message.ordinal for message in value
        ):
            raise ValueError("report source messages must be ordered")
        return value


class ReportValidationError(ValueError):
    """Raised when generated report output cannot be admitted."""


@dataclass(frozen=True)
class ReportRunResult:
    status: Literal["completed", "failed"]
    report: StructuredReport | None
    failure_code: str | None
    failure_message: str | None
    validation_errors: tuple[str, ...]
    latency_ms: float
    provider: str
    model: str
    input_tokens: int | None
    output_tokens: int | None
    prompt_version: str = REPORT_TEMPLATE_PROMPT_VERSION

__all__ = [
    "AdmittedMitreRow",
    "REPORT_STATUS",
    "REPORT_TEMPLATE_MODEL",
    "REPORT_TEMPLATE_PROMPT_VERSION",
    "REPORT_TEMPLATE_PROVIDER",
    "REPORT_VERSION",
    "ReportInputSnapshot",
    "ReportRunResult",
    "ReportSourceMessage",
    "ReportValidationError",
]
