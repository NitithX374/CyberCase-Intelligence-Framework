from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    TypeAdapter,
    field_validator,
    model_validator,
)


class CaseAnalysisFailure(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def formatIdentifier(value: object, prefix: str, aliases: str) -> object:
    if not isinstance(value, str):
        return value
    match = re.fullmatch(rf"(?:{aliases})[-_]?([0-9]+)", value.strip(), re.I)
    return f"{prefix}-{int(match[1]):02d}" if match else value


_format_identifier = formatIdentifier

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


@dataclass(frozen=True)
class CaseAdmittedSource:
    source_id: str
    revision: int
    content: str
    content_sha256: str


def build_case_source_registry(
    context: Mapping[str, object],
) -> tuple[CaseAdmittedSource, ...]:
    ids = context.get("source_ids")
    revisions = context.get("source_revisions")
    texts = context.get("_source_text_by_source_id")
    if (
        not isinstance(ids, list)
        or not ids
        or not all(isinstance(value, str) and value.strip() for value in ids)
        or len(ids) != len(set(ids))
        or not isinstance(revisions, Mapping)
        or not isinstance(texts, Mapping)
        or set(ids) != set(revisions)
        or set(ids) != set(texts)
    ):
        raise CaseAnalysisFailure(
            "case_sources_invalid",
            "Case evidence source registry is invalid",
        )
    sources: list[CaseAdmittedSource] = []
    for source_id in ids:
        revision = revisions[source_id]
        content = texts[source_id]
        if not isinstance(revision, int) or revision < 1:
            raise CaseAnalysisFailure(
                "case_source_revision_invalid",
                "Case evidence source revision is invalid",
            )
        if not isinstance(content, str) or not content.strip():
            raise CaseAnalysisFailure(
                "case_source_empty",
                "Case evidence source text is empty",
            )
        sources.append(
            CaseAdmittedSource(
                source_id=source_id,
                revision=revision,
                content=content,
                content_sha256=hashlib.sha256(content.encode("utf-8")).hexdigest(),
            )
        )
    return tuple(sources)


class CaseEvidenceCitation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: str = Field(min_length=1, max_length=160)
    source_revision: int = Field(ge=1)
    exact_quote: str = Field(min_length=1, max_length=2_000)
    document_id: str | None = Field(default=None, min_length=1, max_length=160)
    filename: str | None = Field(default=None, min_length=1, max_length=255)
    page_numbers: list[int] = Field(default_factory=list, max_length=8)

    @model_validator(mode="before")
    @classmethod
    def normalize_document_locator_inputs(cls, data: object) -> object:
        if isinstance(data, dict):
            doc_id = data.get("document_id")
            fname = data.get("filename")
            pages = data.get("page_numbers")
            has_doc_id = bool(doc_id and str(doc_id).strip())
            has_fname = bool(fname and str(fname).strip())
            has_pages = bool(isinstance(pages, (list, tuple)) and len(pages) > 0)
            has_any = has_doc_id or has_fname or has_pages
            has_all = has_doc_id and has_fname and has_pages
            if has_any and not has_all:
                copy_data = dict(data)
                copy_data["document_id"] = None
                copy_data["filename"] = None
                copy_data["page_numbers"] = []
                return copy_data
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
    def validate_document_locator(self) -> "CaseEvidenceCitation":
        has_document_locator = bool(
            self.document_id or self.filename or self.page_numbers
        )
        if has_document_locator and not (
            self.document_id and self.filename and self.page_numbers
        ):
            raise ValueError(
                "document citations require an identifier, filename, and pages"
            )
        return self


class CaseGeneratedUnit(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1, max_length=4_000)
    claim_ids: tuple[str, ...] = Field(min_length=1, max_length=64)

    @field_validator("claim_ids", mode="before")
    @classmethod
    def normalize_claim_ids(cls, value: object) -> object:
        if isinstance(value, (list, tuple)):
            return tuple(_format_identifier(item, "A", "A|claim|c") for item in value)
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
    supporting_citations: list[CaseEvidenceCitation] = Field(
        default_factory=list, max_length=64
    )
    contradicting_citations: list[CaseEvidenceCitation] = Field(
        default_factory=list, max_length=64
    )
    reasoning_summary: str | None = Field(default=None, min_length=1, max_length=1_000)

    @field_validator("claim_id", mode="before")
    @classmethod
    def normalize_claim_id(cls, value: object) -> object:
        return _format_identifier(value, "A", "A|claim|c")

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
        return _format_identifier(value, "G", "G|gap")

    @field_validator("affected_claim_ids", mode="before")
    @classmethod
    def normalize_affected_claim_ids(cls, value: object) -> object:
        if isinstance(value, (list, tuple)):
            return [_format_identifier(item, "A", "A|claim|c") for item in value]
        return value


class CaseInvolvedParty(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=500)
    role: str = Field(min_length=1, max_length=500)
    claim_ids: list[str] = Field(min_length=1, max_length=64)

    @field_validator("name", "role")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("party text values must be non-empty")
        return normalized

    @field_validator("claim_ids", mode="before")
    @classmethod
    def normalize_claim_ids(cls, value: object) -> object:
        if isinstance(value, (list, tuple)):
            return [_format_identifier(item, "A", "A|claim|c") for item in value]
        return value

    @field_validator("claim_ids")
    @classmethod
    def unique_claim_ids(cls, value: list[str]) -> list[str]:
        normalized = [item.strip() for item in value]
        if len(set(normalized)) != len(normalized):
            raise ValueError("claim IDs must be unique")
        return normalized


class CaseTimelineItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    time: str = Field(min_length=1, max_length=500)
    event: str = Field(min_length=1, max_length=2_000)
    claim_ids: list[str] = Field(min_length=1, max_length=64)

    @field_validator("time", "event")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("timeline text values must be non-empty")
        return normalized

    @field_validator("claim_ids", mode="before")
    @classmethod
    def normalize_claim_ids(cls, value: object) -> object:
        if isinstance(value, (list, tuple)):
            return [_format_identifier(item, "A", "A|claim|c") for item in value]
        return value

    @field_validator("claim_ids")
    @classmethod
    def unique_claim_ids(cls, value: list[str]) -> list[str]:
        normalized = [item.strip() for item in value]
        if len(set(normalized)) != len(normalized):
            raise ValueError("claim IDs must be unique")
        return normalized


class CaseImpactItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: str = Field(min_length=1, max_length=2_000)
    claim_ids: list[str] = Field(min_length=1, max_length=64)

    @field_validator("description")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("impact text values must be non-empty")
        return normalized

    @field_validator("claim_ids", mode="before")
    @classmethod
    def normalize_claim_ids(cls, value: object) -> object:
        if isinstance(value, (list, tuple)):
            return [_format_identifier(item, "A", "A|claim|c") for item in value]
        return value

    @field_validator("claim_ids")
    @classmethod
    def unique_claim_ids(cls, value: list[str]) -> list[str]:
        normalized = [item.strip() for item in value]
        if len(set(normalized)) != len(normalized):
            raise ValueError("claim IDs must be unique")
        return normalized


class CaseMitreAssociation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    association_id: str = Field(pattern=r"^MA-\d{2,}$", max_length=80)
    technique_id: str = Field(pattern=r"^T\d{4}(?:\.\d{3})?$", max_length=9)
    claim_ids: list[str] = Field(min_length=1, max_length=64)
    reason: str = Field(min_length=1, max_length=4_000)
    status: Literal["candidate_only"]
    support_role: Literal["external_technical_context"]

    @field_validator("association_id", mode="before")
    @classmethod
    def normalize_association_id(cls, value: object) -> object:
        return _format_identifier(value, "MA", "MA|assoc|association")

    @field_validator("claim_ids", mode="before")
    @classmethod
    def normalize_claim_ids(cls, value: object) -> object:
        if isinstance(value, (list, tuple)):
            return [_format_identifier(item, "A", "A|claim|c") for item in value]
        return value


class CaseAnalysisTrace(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal["case_analysis_trace_v1"] = "case_analysis_trace_v1"
    validation_status: Literal["validated"] = "validated"
    analysis_mode: CaseAnalysisMode
    summary: str = Field(min_length=1, max_length=24_000)
    involved_parties: list[CaseInvolvedParty] = Field(
        default_factory=list, max_length=64
    )
    timeline: list[CaseTimelineItem] = Field(
        default_factory=list, max_length=64
    )
    claims: list[CaseAnalysisClaim] = Field(max_length=64)
    impacts: list[CaseImpactItem] = Field(
        default_factory=list, max_length=64
    )
    gaps: list[CaseAnalysisGap] = Field(default_factory=list, max_length=64)
    mitre_associations: list[CaseMitreAssociation] = Field(
        default_factory=list, max_length=64
    )
    evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    retrieval_context_id: str | None = Field(default=None, min_length=1, max_length=160)


class CaseProviderAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal["case_analysis_trace_v1"]
    answer: str = Field(min_length=1, max_length=24_000)
    summary: str = Field(min_length=1, max_length=24_000)
    involved_parties: list[CaseInvolvedParty] = Field(max_length=64)
    timeline: list[CaseTimelineItem] = Field(max_length=64)
    claims: list[CaseAnalysisClaim] = Field(max_length=64)
    impacts: list[CaseImpactItem] = Field(max_length=64)
    gaps: list[CaseAnalysisGap] = Field(default_factory=list, max_length=32)
    mitre_associations: list[CaseMitreAssociation] = Field(
        default_factory=list, max_length=64
    )


class CaseProviderMitreMapping(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal["case_mitre_mapping_v1"]
    associations: list[CaseMitreAssociation] = Field(
        default_factory=list, max_length=64
    )


class CaseAnalysisFailureMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal["case_analysis_trace_v1"] = "case_analysis_trace_v1"
    validation_status: Literal["unavailable"] = "unavailable"
    failure_code: str = Field(min_length=1, max_length=120)


ResponseLanguage = Literal["thai", "english"]
VALID_RESPONSE_LANGUAGES: frozenset[str] = frozenset({"thai", "english"})


def validate_response_language(value: object) -> ResponseLanguage:
    if value == "thai":
        return "thai"
    if value == "english":
        return "english"
    raise ValueError(f"Unsupported response language: {value!r}")


def resolve_response_language(user_message: object) -> ResponseLanguage:
    if not isinstance(user_message, str) or not user_message.strip():
        raise ValueError("User message must be a non-empty string")

    if any("\u0e00" <= character <= "\u0e7f" for character in user_message):
        return "thai"
    if any(character.isascii() and character.isalpha() for character in user_message):
        return "english"

    raise ValueError("User message language must be Thai or English")


AnalysisMode = CaseAnalysisMode
AnalysisTraceFailure = CaseAnalysisFailureMetadata
ValidatedAnalysisTrace = CaseAnalysisTrace


@dataclass(frozen=True)
class CaseAnalysisResult:
    answer: str
    trace: CaseAnalysisTrace | None
    trace_failure: CaseAnalysisFailureMetadata | None = None
    execution_receipt: dict[str, object] | None = None
    followup_question: str | None = None
    followup_metadata: dict[str, object] | None = None


ReadableAnalysisTrace = CaseAnalysisTrace
_analysis_trace_reader = TypeAdapter(CaseAnalysisTrace)


def read_analysis_trace(payload: object) -> CaseAnalysisTrace:
    return _analysis_trace_reader.validate_python(payload)


__all__ = [
    "AnalysisMode",
    "AnalysisTraceFailure",
    "CaseAdmittedSource",
    "CaseAnalysisClaim",
    "CaseAnalysisFailure",
    "CaseAnalysisFailureMetadata",
    "CaseAnalysisGap",
    "CaseAnalysisMode",
    "CaseAnalysisResult",
    "CaseAnalysisTrace",
    "CaseClaimType",
    "CaseEpistemicStatus",
    "CaseEvidenceCitation",
    "CaseGeneratedUnit",
    "CaseImpactItem",
    "CaseInvolvedParty",
    "CaseMitreAssociation",
    "CaseProviderAnalysis",
    "CaseProviderMitreMapping",
    "CaseTimelineItem",
    "ReadableAnalysisTrace",
    "ResponseLanguage",
    "VALID_RESPONSE_LANGUAGES",
    "ValidatedAnalysisTrace",
    "build_case_source_registry",
    "formatIdentifier",
    "read_analysis_trace",
    "resolve_response_language",
    "validate_response_language",
]
