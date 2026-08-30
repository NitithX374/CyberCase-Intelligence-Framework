from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


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
        if any(not item for item in normalized) or len(set(normalized)) != len(normalized):
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
    supporting_source_message_ids: list[str] = Field(default_factory=list, max_length=64)
    contradicting_source_message_ids: list[str] = Field(default_factory=list, max_length=64)
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

    @field_validator("supporting_source_message_ids", "contradicting_source_message_ids")
    @classmethod
    def unique_evidence_source_ids(cls, value: list[str]) -> list[str]:
        normalized = [item.strip() for item in value]
        if any(not item for item in normalized) or len(set(normalized)) != len(normalized):
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
    mitre_associations: list[MitreAssociation] = Field(default_factory=list, max_length=64)
    evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    retrieval_context_id: str | None = Field(default=None, min_length=1, max_length=160)

    @field_validator("summary")
    @classmethod
    def normalize_summary(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("summary must be non-empty")
        return normalized


class ProviderCaseAnalysisV3(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal["analysis_trace_v3"]
    answer: str = Field(min_length=1, max_length=24_000)
    summary: str = Field(min_length=1, max_length=24_000)
    claims: list[AnalysisClaimV3] = Field(max_length=64)
    mitre_associations: list[MitreAssociation] = Field(default_factory=list, max_length=64)


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


__all__ = [
    "ANALYSIS_TRACE_VERSION",
    "ANALYSIS_TRACE_V3_VERSION",
    "AnalysisClaim",
    "AnalysisClaimV3",
    "AnalysisGapV3",
    "AnalysisMode",
    "AnalysisTrace",
    "AnalysisTraceDraft",
    "AnalysisTraceFailureMetadata",
    "AnalysisTraceFailure",
    "AnalysisTraceV3",
    "AnalysisTraceV3FailureMetadata",
    "CaseAnalysisResult",
    "ClaimType",
    "EpistemicStatus",
    "GapPriority",
    "GapStatus",
    "MitreAssociation",
    "ProviderCaseAnalysis",
    "ProviderCaseAnalysisV3",
    "ValidatedAnalysisTrace",
]
