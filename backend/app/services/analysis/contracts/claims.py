from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass
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
    exact_quote: str = Field(default="", max_length=2_000)
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

    @field_validator("page_numbers", mode="before")
    @classmethod
    def sanitize_page_numbers(cls, value: object) -> object:
        if isinstance(value, (list, tuple)):
            seen: list[int] = []
            for p in value:
                if isinstance(p, int) and 1 <= p <= 500 and p not in seen:
                    seen.append(p)
                elif isinstance(p, str) and p.strip().isdigit():
                    num = int(p.strip())
                    if 1 <= num <= 500 and num not in seen:
                        seen.append(num)
            return seen
        return value

    @model_validator(mode="after")
    def drop_incomplete_locator(self) -> CaseSourceCitation:
        if not (self.document_id and self.filename and self.page_numbers):
            self.document_id = None
            self.filename = None
            self.page_numbers = []
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
    reasoning_summary: str | None = Field(default=None, max_length=1_000)

    @model_validator(mode="before")
    @classmethod
    def sanitize_raw_citations(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data
        for field_name in ("supporting_citations", "contradicting_citations"):
            raw = data.get(field_name)
            if not isinstance(raw, (list, tuple)):
                continue
            cleaned = []
            for item in raw:
                if isinstance(item, CaseSourceCitation):
                    if item.exact_quote.strip():
                        cleaned.append(item)
                elif isinstance(item, dict):
                    citation = normalized_citation(item)
                    if citation is not None:
                        cleaned.append(citation)
            data[field_name] = cleaned[:64]
        return data

    @field_validator("claim_id", mode="before")
    @classmethod
    def normalize_claim_id(cls, value: object) -> object:
        return normalize_identifier(value, "A", "A|claim|c")

    @field_validator("reasoning_summary", mode="before")
    @classmethod
    def normalize_reasoning_summary(cls, value: object) -> object:
        if isinstance(value, str):
            stripped = value.strip()
            return stripped if stripped else None
        return value

    @field_validator("text")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("claim text values must be non-empty")
        return normalized

    @field_validator("supporting_source_ids", "contradicting_source_ids", mode="before")
    @classmethod
    def unique_source_ids(cls, value: object) -> object:
        if not isinstance(value, (list, tuple)):
            return value
        normalized: list[str] = []
        for item in value:
            if not isinstance(item, str):
                continue
            source_id = item.strip()
            if source_id and source_id not in normalized:
                normalized.append(source_id)
        return normalized[:64]


def normalized_citation(data: dict[object, object]) -> dict[str, object] | None:
    source_id = data.get("source_id")
    quote = data.get("exact_quote")
    if not isinstance(source_id, str) or not isinstance(quote, str):
        return None
    source_id = source_id.strip()
    quote = quote.strip()
    if not source_id or not quote or len(source_id) > 160 or len(quote) > 2_000:
        return None
    return {
        "source_id": source_id,
        "exact_quote": quote,
        "document_id": bounded_locator(data.get("document_id"), 160),
        "filename": bounded_locator(data.get("filename"), 255),
        "page_numbers": data.get("page_numbers")
        if isinstance(data.get("page_numbers"), (list, tuple))
        else [],
    }


def bounded_locator(value: object, limit: int) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    return normalized if normalized and len(normalized) <= limit else None


class CaseAnalysisGap(BaseModel):
    model_config = ConfigDict(extra="forbid")

    gap_id: str = Field(pattern=r"^G-\d{2,}$", max_length=80)
    gap_key: str = Field(min_length=1, max_length=160)
    topic: str = Field(min_length=1, max_length=500)
    status: Literal["NOT_PROVIDED", "EXPLICITLY_UNKNOWN", "AMBIGUOUS", "CONFLICTING"]
    description: str = Field(min_length=1, max_length=4_000)
    affected_claim_ids: list[str] = Field(default_factory=list, max_length=64)
    reason: str = Field(min_length=1, max_length=4_000)
    priority: Literal["high", "medium", "low"]
    askable: bool
    clarification_question: str | None = Field(default=None, max_length=300)

    @field_validator("gap_id", mode="before")
    @classmethod
    def normalize_gap_id(cls, value: object) -> object:
        return normalize_identifier(value, "G", "G|gap")

    @field_validator("gap_key", "topic", "clarification_question", mode="before")
    @classmethod
    def normalize_gap_text(cls, value: object) -> object:
        if value is None:
            return None
        if not isinstance(value, str):
            return value
        normalized = value.strip()
        if not normalized:
            raise ValueError("Gap text values must be non-empty")
        if "\n" in normalized or "\r" in normalized:
            raise ValueError("Gap text values cannot contain line breaks")
        return normalized

    @field_validator("affected_claim_ids", mode="before")
    @classmethod
    def normalize_affected_claim_ids(cls, value: object) -> object:
        if isinstance(value, (list, tuple)):
            return [normalize_identifier(item, "A", "A|claim|c") for item in value]
        return value


class CaseAssessmentTrace(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal["case_assessment_v1"] = "case_assessment_v1"
    gaps: list[CaseAnalysisGap] = Field(default_factory=list, max_length=32)


@dataclass(frozen=True)
class CaseFollowupExchange:
    qa_id: str
    gap_key: str
    question: str
    answer: str | None = None

    @property
    def is_answered(self) -> bool:
        return bool(self.answer and self.answer.strip())


def followup_qa_id(index: int) -> str:
    return f"QA-{index:02d}"


def followup_payload(history: Sequence[CaseFollowupExchange]) -> list[dict[str, str]]:
    return [
        {"qa_id": item.qa_id, "question": item.question, "answer": item.answer or ""}
        for item in history
        if item.is_answered
    ]
