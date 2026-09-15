from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

CaseClaimType = Literal["reported", "analytical_inference", "unknown"]
CaseEpistemicStatus = Literal[
    "reported",
    "suspected",
    "contradicted",
    "not_established",
    "unknown",
    "not_confirmed",
]
CaseAnalysisMode = Literal["case_overview", "question_answer"]


def normalize_identifier(value: object, prefix: str, aliases: str) -> object:
    if not isinstance(value, str):
        return value
    match = re.fullmatch(rf"(?:{aliases})[-_]?([0-9]+)", value.strip(), re.I)
    return f"{prefix}-{int(match[1]):02d}" if match else value


class CaseSourceCitation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: str = Field(min_length=1, max_length=160)
    exact_quote: str = Field(min_length=1, max_length=2_000)
    document_id: str | None = Field(default=None, min_length=1, max_length=160)
    filename: str | None = Field(default=None, min_length=1, max_length=255)
    page_numbers: list[int] = Field(default_factory=list, max_length=8)

    @model_validator(mode="before")
    @classmethod
    def normalize_document_locator_inputs(cls, data: object) -> object:
        if isinstance(data, dict):
            doc_id = data.get("document_id")
            filename = data.get("filename")
            pages = data.get("page_numbers")
            has_document_id = bool(doc_id and str(doc_id).strip())
            has_filename = bool(filename and str(filename).strip())
            has_pages = bool(isinstance(pages, (list, tuple)) and len(pages) > 0)
            if (has_document_id or has_filename or has_pages) and not (
                has_document_id and has_filename and has_pages
            ):
                normalized = dict(data)
                normalized["document_id"] = None
                normalized["filename"] = None
                normalized["page_numbers"] = []
                return normalized
        return data

    @field_validator("source_id", "exact_quote", "document_id", "filename")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else None

    @field_validator("page_numbers")
    @classmethod
    def unique_page_numbers(cls, value: list[int]) -> list[int]:
        if any(page < 1 or page > 500 for page in value):
            raise ValueError("citation page numbers must be between 1 and 500")
        if len(value) != len(set(value)):
            raise ValueError("citation page numbers must be unique")
        return value

    @model_validator(mode="after")
    def validate_document_locator(self) -> "CaseSourceCitation":
        has_locator = bool(self.document_id or self.filename or self.page_numbers)
        if has_locator and not (self.document_id and self.filename and self.page_numbers):
            raise ValueError("document citations require an identifier, filename, and pages")
        return self


class CaseGeneratedUnit(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1, max_length=4_000)
    claim_ids: tuple[str, ...] = Field(min_length=1, max_length=64)

    @field_validator("claim_ids", mode="before")
    @classmethod
    def normalize_claim_ids(cls, value: object) -> object:
        if isinstance(value, (list, tuple)):
            return tuple(normalize_identifier(item, "A", "A|claim|c") for item in value)
        return value

    @field_validator("text")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("generated text must be non-empty")
        return normalized


class CaseAnalysisClaim(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claim_id: str = Field(pattern=r"^A-\d{2,}$", max_length=80)
    claim_type: CaseClaimType
    text: str = Field(min_length=1, max_length=4_000)
    epistemic_status: CaseEpistemicStatus
    supporting_source_ids: list[str] = Field(default_factory=list, max_length=64)
    contradicting_source_ids: list[str] = Field(default_factory=list, max_length=64)
    supporting_citations: list[CaseSourceCitation] = Field(default_factory=list, max_length=64)
    contradicting_citations: list[CaseSourceCitation] = Field(default_factory=list, max_length=64)
    reasoning_summary: str | None = Field(default=None, min_length=1, max_length=1_000)

    @field_validator("claim_id", mode="before")
    @classmethod
    def normalize_claim_id(cls, value: object) -> object:
        return normalize_identifier(value, "A", "A|claim|c")

    @field_validator("text", "reasoning_summary")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("claim text values must be non-empty")
        return normalized

    @field_validator("supporting_source_ids", "contradicting_source_ids")
    @classmethod
    def unique_source_ids(cls, value: list[str]) -> list[str]:
        normalized = [item.strip() for item in value]
        if any(not item for item in normalized) or len(set(normalized)) != len(normalized):
            raise ValueError("source IDs must be non-empty and unique")
        return normalized


class CaseAnalysisGap(BaseModel):
    model_config = ConfigDict(extra="forbid")

    gap_id: str = Field(pattern=r"^G-\d{2,}$", max_length=80)
    topic: str = Field(min_length=1, max_length=500)
    status: Literal["NOT_PROVIDED", "EXPLICITLY_UNKNOWN", "AMBIGUOUS", "CONFLICTING"]
    description: str = Field(min_length=1, max_length=4_000)
    affected_claim_ids: list[str] = Field(default_factory=list, max_length=64)
    reason: str = Field(min_length=1, max_length=4_000)
    priority: Literal["high", "medium", "low"]
    askable: bool

    @field_validator("gap_id", mode="before")
    @classmethod
    def normalize_gap_id(cls, value: object) -> object:
        return normalize_identifier(value, "G", "G|gap")

    @field_validator("affected_claim_ids", mode="before")
    @classmethod
    def normalize_affected_claim_ids(cls, value: object) -> object:
        if isinstance(value, (list, tuple)):
            return [normalize_identifier(item, "A", "A|claim|c") for item in value]
        return value


__all__ = [
    "CaseAnalysisMode",
    "CaseAnalysisClaim",
    "CaseAnalysisGap",
    "CaseClaimType",
    "CaseEpistemicStatus",
    "CaseGeneratedUnit",
    "CaseSourceCitation",
]
