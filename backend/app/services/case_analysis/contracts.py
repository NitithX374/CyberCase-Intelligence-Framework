from __future__ import annotations

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

    @field_validator("text", "reasoning_summary")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("text values must be non-empty")
        return normalized

    @field_validator(
        "supporting_source_message_ids", "contradicting_source_message_ids"
    )
    @classmethod
    def unique_evidence_source_ids(cls, value: list[str]) -> list[str]:
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

    @field_validator("topic", "description", "reason")
    @classmethod
    def normalize_gap_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("gap text values must be non-empty")
        return normalized

    @field_validator("affected_claim_ids")
    @classmethod
    def unique_affected_claim_ids(cls, value: list[str]) -> list[str]:
        normalized = [item.strip() for item in value]
        if any(not item for item in normalized) or len(set(normalized)) != len(
            normalized
        ):
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
    retrieval_context_id: str | None = Field(default=None, min_length=1, max_length=160)

    @field_validator("summary")
    @classmethod
    def normalize_summary(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("summary must be non-empty")
        return normalized


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


class ProviderCaseAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal["analysis_trace_v2"]
    answer: str = Field(min_length=1, max_length=24_000)
    claims: list[AnalysisClaim] = Field(max_length=64)
    mitre_associations: list[MitreAssociation] = Field(max_length=64)


class AnalysisTraceDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal["analysis_trace_v2"] = "analysis_trace_v2"
    validation_status: Literal["validated"] = "validated"
    analysis_mode: AnalysisMode
    claims: list[AnalysisClaim]
    mitre_associations: list[MitreAssociation] = Field(default_factory=list)


class AnalysisTrace(AnalysisTraceDraft):
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


AnalysisTraceFailure = AnalysisTraceFailureMetadata | AnalysisTraceV3FailureMetadata
ValidatedAnalysisTrace = AnalysisTraceDraft | AnalysisTraceV3


@dataclass(frozen=True)
class CaseAnalysisResult:
    answer: str
    trace: ValidatedAnalysisTrace | None
    trace_failure: AnalysisTraceFailure | None = None


ReadableAnalysisTrace = Annotated[
    AnalysisTrace | AnalysisTraceV3,
    Field(discriminator="version"),
]

_analysis_trace_reader = TypeAdapter(ReadableAnalysisTrace)


def read_analysis_trace(payload: object) -> ReadableAnalysisTrace:
    return _analysis_trace_reader.validate_python(payload)


__all__ = [
    "ANALYSIS_TRACE_VERSION",
    "ANALYSIS_TRACE_V3_VERSION",
    "AnalysisClaim",
    "AnalysisClaimV3",
    "AnalysisEvidenceCitation",
    "AnalysisGapV3",
    "AnalysisMode",
    "AnalysisTrace",
    "AnalysisTraceDraft",
    "AnalysisTraceFailure",
    "AnalysisTraceFailureMetadata",
    "AnalysisTraceV3",
    "AnalysisTraceV3FailureMetadata",
    "CaseAnalysisResult",
    "ClaimType",
    "EpistemicStatus",
    "GapPriority",
    "GapStatus",
    "MitreAssociation",
    "PROVIDER_CLAIM_IDS",
    "ProviderAnalysisClaimV3",
    "ProviderCaseAnalysis",
    "ProviderCaseAnalysisV3",
    "ProviderClaimId",
    "ProviderMitreAssociation",
    "ReadableAnalysisTrace",
    "ValidatedAnalysisTrace",
    "read_analysis_trace",
]
