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


class CaseQuoteCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: str = Field(min_length=1, max_length=160)
    source_revision: int = Field(ge=1)
    exact_quote: str = Field(min_length=1, max_length=2_000)
    role: Literal["supporting", "contradicting"]

    @field_validator("source_id", "exact_quote")
    @classmethod
    def require_trimmed_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized or normalized != value:
            raise ValueError("Source references must contain trimmed text")
        return normalized


class CaseClaimCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1, max_length=4_000)
    claim_type: CaseClaimType
    epistemic_status: CaseEpistemicStatus
    evidence: tuple[CaseQuoteCandidate, ...] = Field(min_length=1, max_length=64)
    reasoning_summary: str | None = Field(default=None, min_length=1, max_length=1_000)


class CaseExtractedClaims(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claims: tuple[CaseClaimCandidate, ...] = Field(min_length=1, max_length=256)


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


class CaseGeneratedSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    units: tuple[CaseGeneratedUnit, ...] = Field(min_length=1, max_length=64)


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


CaseClaimCandidate.model_rebuild()


# ==============================================================================
# Legacy V3 & Cross-Version Trace Models
# ==============================================================================

class AnalysisEvidenceCitation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_message_id: str = Field(min_length=1, max_length=160)
    exact_quote: str = Field(min_length=1, max_length=2_000)
    document_id: str | None = Field(default=None, min_length=1, max_length=160)
    filename: str | None = Field(default=None, min_length=1, max_length=255)
    page_numbers: list[int] = Field(default_factory=list, max_length=8)

    @field_validator("source_message_id", "exact_quote", "document_id", "filename")
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
    def validate_document_locator(self) -> "AnalysisEvidenceCitation":
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


ANALYSIS_TRACE_VERSION = "analysis_trace_v2"
ANALYSIS_TRACE_V3_VERSION = "analysis_trace_v3"
AnalysisMode = Literal["case_overview", "question_answer"]
ClaimType = Literal["reported", "analytical_inference", "unknown"]
EpistemicStatus = Literal[
    "reported",
    "suspected",
    "contradicted",
    "not_established",
    "unknown",
    "not_confirmed",
]
GapStatus = Literal[
    "NOT_PROVIDED",
    "EXPLICITLY_UNKNOWN",
    "AMBIGUOUS",
    "CONFLICTING",
]
GapPriority = Literal["high", "medium", "low"]
PROVIDER_CLAIM_IDS = tuple(f"A-{index:02d}" for index in range(1, 65))
ProviderClaimId = Literal[*PROVIDER_CLAIM_IDS]


class AnalysisClaim(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claim_id: str = Field(pattern=r"^A-\d{2,}$", max_length=80)
    claim_type: ClaimType
    text: str = Field(min_length=1, max_length=4_000)
    epistemic_status: EpistemicStatus
    source_message_ids: list[str] = Field(default_factory=list, max_length=64)

    @field_validator("text")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("source_message_ids")
    @classmethod
    def unique_source_ids(cls, value: list[str]) -> list[str]:
        normalized = [item.strip() for item in value]
        if any(not item for item in normalized) or len(set(normalized)) != len(
            normalized
        ):
            raise ValueError("source message IDs must be non-empty and unique")
        return normalized


class MitreAssociation(BaseModel):
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


class AnalysisClaimV3(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claim_id: str = Field(pattern=r"^A-\d{2,}$", max_length=80)
    claim_type: ClaimType
    text: str = Field(min_length=1, max_length=4_000)
    epistemic_status: EpistemicStatus
    supporting_source_message_ids: list[str] = Field(
        default_factory=list, max_length=64
    )
    contradicting_source_message_ids: list[str] = Field(
        default_factory=list, max_length=64
    )
    supporting_citations: list[AnalysisEvidenceCitation] = Field(
        default_factory=list, max_length=64
    )
    contradicting_citations: list[AnalysisEvidenceCitation] = Field(
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

    @field_validator(
        "supporting_source_message_ids", "contradicting_source_message_ids"
    )
    @classmethod
    def unique_source_ids(cls, value: list[str]) -> list[str]:
        normalized = [item.strip() for item in value]
        if any(not item for item in normalized) or len(set(normalized)) != len(
            normalized
        ):
            raise ValueError("source message IDs must be non-empty and unique")
        return normalized


class AnalysisGapV3(BaseModel):
    model_config = ConfigDict(extra="forbid")

    gap_id: str = Field(pattern=r"^G-\d{2,}$", max_length=80)
    topic: str = Field(min_length=1, max_length=500)
    status: GapStatus
    description: str = Field(min_length=1, max_length=4_000)
    affected_claim_ids: list[str] = Field(default_factory=list, max_length=64)
    reason: str = Field(min_length=1, max_length=4_000)
    priority: GapPriority
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


    @field_validator("affected_claim_ids")
    @classmethod
    def unique_affected_claim_ids(cls, value: list[str]) -> list[str]:
        normalized = [item.strip() for item in value]
        if any(not item for item in normalized) or len(set(normalized)) != len(normalized):
            raise ValueError("affected claim IDs must be non-empty and unique")
        return normalized


class AnalysisTraceV3(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal["analysis_trace_v3"] = "analysis_trace_v3"
    validation_status: Literal["validated"] = "validated"
    analysis_mode: AnalysisMode
    summary: str = Field(min_length=1, max_length=24_000)
    claims: list[AnalysisClaimV3] = Field(max_length=64)
    gaps: list[AnalysisGapV3] = Field(default_factory=list, max_length=64)
    mitre_associations: list[MitreAssociation] = Field(
        default_factory=list, max_length=64
    )
    evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    retrieval_context_id: str | None = Field(
        default=None, min_length=1, max_length=160
    )


class ProviderAnalysisClaimV3(AnalysisClaimV3):
    claim_id: ProviderClaimId


class ProviderMitreAssociation(MitreAssociation):
    claim_ids: list[ProviderClaimId] = Field(min_length=1, max_length=64)


class ProviderCaseAnalysisV3(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal["analysis_trace_v3"]
    answer: str = Field(min_length=1, max_length=24_000)
    summary: str = Field(min_length=1, max_length=24_000)
    claims: list[ProviderAnalysisClaimV3] = Field(max_length=64)
    mitre_associations: list[ProviderMitreAssociation] = Field(
        default_factory=list,
        max_length=64,
    )


class AnalysisTrace(BaseModel):
    """Historical v2 analysis trace model retained strictly for read-only deserialization."""

    model_config = ConfigDict(extra="forbid")

    version: Literal["analysis_trace_v2"] = "analysis_trace_v2"
    validation_status: Literal["validated"] = "validated"
    analysis_mode: AnalysisMode
    claims: list[AnalysisClaim]
    mitre_associations: list[MitreAssociation] = Field(default_factory=list)
    retrieval_context_id: str = Field(min_length=1, max_length=160)
    evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class AnalysisTraceFailureMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal["analysis_trace_v2"] = "analysis_trace_v2"
    validation_status: Literal["unavailable"] = "unavailable"
    failure_code: str = Field(min_length=1, max_length=120)


class AnalysisTraceV3FailureMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal["analysis_trace_v3"] = "analysis_trace_v3"
    validation_status: Literal["unavailable"] = "unavailable"
    failure_code: str = Field(min_length=1, max_length=120)


AnalysisTraceFailure = (
    AnalysisTraceFailureMetadata | AnalysisTraceV3FailureMetadata | CaseAnalysisFailureMetadata
)
ValidatedAnalysisTrace = AnalysisTraceV3 | CaseAnalysisTrace


@dataclass(frozen=True)
class CaseAnalysisResult:
    answer: str
    trace: CaseAnalysisTrace | AnalysisTraceV3 | None
    trace_failure: AnalysisTraceFailure | None = None
    execution_receipt: dict[str, object] | None = None
    followup_question: str | None = None
    followup_metadata: dict[str, object] | None = None


ReadableAnalysisTrace = Annotated[
    AnalysisTrace | AnalysisTraceV3 | CaseAnalysisTrace,
    Field(discriminator="version"),
]

_analysis_trace_reader = TypeAdapter(ReadableAnalysisTrace)


def read_analysis_trace(payload: object) -> ReadableAnalysisTrace:
    return _analysis_trace_reader.validate_python(payload)


# ==============================================================================
# Backward-compatibility aliases for smooth transition away from 'native' naming
# ==============================================================================
NativeClaimType = CaseClaimType
NativeEpistemicStatus = CaseEpistemicStatus
NativeAnalysisMode = CaseAnalysisMode
NativeAdmittedSource = CaseAdmittedSource
build_native_source_registry = build_case_source_registry
NativeCaseEvidenceCitation = CaseEvidenceCitation
NativeClaimCandidate = CaseClaimCandidate
NativeQuoteCandidate = CaseQuoteCandidate
NativeExtractedClaims = CaseExtractedClaims
NativeGeneratedUnit = CaseGeneratedUnit
NativeGeneratedSummary = CaseGeneratedSummary
NativeInvolvedParty = CaseInvolvedParty
NativeTimelineItem = CaseTimelineItem
NativeImpactItem = CaseImpactItem
NativeCaseAnalysisClaim = CaseAnalysisClaim
NativeCaseAnalysisGap = CaseAnalysisGap
NativeMitreAssociation = CaseMitreAssociation
NativeCaseAnalysisTrace = CaseAnalysisTrace
NativeProviderCaseAnalysis = CaseProviderAnalysis
NativeProviderMitreMapping = CaseProviderMitreMapping
NativeCaseAnalysisFailureMetadata = CaseAnalysisFailureMetadata
NativeCaseAnalysisResult = CaseAnalysisResult


__all__ = [
    "ANALYSIS_TRACE_VERSION",
    "ANALYSIS_TRACE_V3_VERSION",
    "AnalysisClaim",
    "AnalysisClaimV3",
    "AnalysisEvidenceCitation",
    "AnalysisGapV3",
    "AnalysisMode",
    "AnalysisTrace",
    "AnalysisTraceFailure",
    "AnalysisTraceFailureMetadata",
    "AnalysisTraceV3",
    "AnalysisTraceV3FailureMetadata",
    "CaseAdmittedSource",
    "CaseAnalysisClaim",
    "CaseAnalysisFailure",
    "CaseAnalysisFailureMetadata",
    "CaseAnalysisGap",
    "CaseAnalysisMode",
    "CaseAnalysisResult",
    "CaseAnalysisTrace",
    "CaseClaimCandidate",
    "CaseClaimType",
    "CaseEpistemicStatus",
    "CaseEvidenceCitation",
    "CaseExtractedClaims",
    "CaseGeneratedSummary",
    "CaseGeneratedUnit",
    "CaseImpactItem",
    "CaseInvolvedParty",
    "CaseMitreAssociation",
    "CaseProviderAnalysis",
    "CaseProviderMitreMapping",
    "CaseQuoteCandidate",
    "CaseTimelineItem",
    "ClaimType",
    "EpistemicStatus",
    "GapPriority",
    "GapStatus",
    "MitreAssociation",
    "NativeAdmittedSource",
    "NativeAnalysisMode",
    "NativeCaseAnalysisClaim",
    "NativeCaseAnalysisFailureMetadata",
    "NativeCaseAnalysisGap",
    "NativeCaseAnalysisResult",
    "NativeCaseAnalysisTrace",
    "NativeCaseEvidenceCitation",
    "NativeClaimCandidate",
    "NativeClaimType",
    "NativeEpistemicStatus",
    "NativeExtractedClaims",
    "NativeGeneratedSummary",
    "NativeGeneratedUnit",
    "NativeImpactItem",
    "NativeInvolvedParty",
    "NativeMitreAssociation",
    "NativeProviderCaseAnalysis",
    "NativeProviderMitreMapping",
    "NativeQuoteCandidate",
    "NativeTimelineItem",
    "PROVIDER_CLAIM_IDS",
    "ProviderAnalysisClaimV3",
    "ProviderCaseAnalysisV3",
    "ProviderClaimId",
    "ProviderMitreAssociation",
    "ReadableAnalysisTrace",
    "ResponseLanguage",
    "VALID_RESPONSE_LANGUAGES",
    "ValidatedAnalysisTrace",
    "build_case_source_registry",
    "build_native_source_registry",
    "formatIdentifier",
    "read_analysis_trace",
    "resolve_response_language",
    "validate_response_language",
]
