"""Analysis Trace v1 contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


ANALYSIS_TRACE_VERSION = "analysis_trace_v1"

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
MitreAssociationStatus = Literal["candidate_only"]
MitreSupportRole = Literal["external_technical_context"]


class AnalysisClaim(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claim_id: str = Field(min_length=1, max_length=80, pattern=r"^A-\d{2,}$")
    claim_type: ClaimType
    text: str = Field(min_length=1, max_length=4_000)
    epistemic_status: EpistemicStatus
    entity_ids: list[str] = Field(max_length=64)
    relationship_ids: list[str] = Field(max_length=64)
    evidence_ids: list[str] = Field(max_length=64)
    timeline_event_ids: list[str] = Field(max_length=64)

    @field_validator(
        "entity_ids",
        "relationship_ids",
        "evidence_ids",
        "timeline_event_ids",
    )
    @classmethod
    def validate_reference_list(cls, value: list[str]) -> list[str]:
        normalized = [item.strip() for item in value]
        if any(not item for item in normalized):
            raise ValueError("reference IDs must not be empty")
        if len(set(normalized)) != len(normalized):
            raise ValueError("reference IDs must be unique within a claim")
        return normalized

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("claim text must not be empty")
        return normalized


class MitreAssociation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    association_id: str = Field(
        min_length=1,
        max_length=80,
        pattern=r"^MA-\d{2,}$",
    )
    technique_id: str = Field(
        min_length=5,
        max_length=9,
        pattern=r"^T\d{4}(?:\.\d{3})?$",
    )
    claim_ids: list[str] = Field(min_length=1, max_length=64)
    reason: str = Field(min_length=1, max_length=4_000)
    status: MitreAssociationStatus
    support_role: MitreSupportRole

    @field_validator("claim_ids")
    @classmethod
    def validate_claim_ids(cls, value: list[str]) -> list[str]:
        normalized = [item.strip() for item in value]
        if any(not item for item in normalized):
            raise ValueError("claim IDs must not be empty")
        if len(set(normalized)) != len(normalized):
            raise ValueError("claim IDs must be unique within an association")
        return normalized

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("association reason must not be empty")
        return normalized

class ProviderCaseAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal["analysis_trace_v1"]
    answer: str = Field(min_length=1, max_length=24_000)
    claims: list[AnalysisClaim] = Field(max_length=64)
    mitre_associations: list[MitreAssociation] = Field(max_length=64)

    @field_validator("answer")
    @classmethod
    def validate_answer(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("analysis answer must not be empty")
        return normalized


class AnalysisTraceDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal["analysis_trace_v1"] = "analysis_trace_v1"
    validation_status: Literal["validated"] = "validated"
    reference_membership: Literal["validated"] = "validated"
    semantic_entailment: Literal[
        "not_deterministically_established"
    ] = "not_deterministically_established"
    analysis_mode: AnalysisMode
    claims: list[AnalysisClaim]
    mitre_associations: list[MitreAssociation] = Field(default_factory=list)


class AnalysisTrace(AnalysisTraceDraft):
    case_state_version_id: str = Field(min_length=1, max_length=64)
    retrieval_context_id: str = Field(min_length=1, max_length=160)


class AnalysisTraceFailureMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal["analysis_trace_v1"] = "analysis_trace_v1"
    validation_status: Literal["unavailable"] = "unavailable"
    failure_code: str = Field(min_length=1, max_length=120)


@dataclass(frozen=True)
class CaseAnalysisResult:
    answer: str
    trace: AnalysisTraceDraft | None
    trace_failure: AnalysisTraceFailureMetadata | None = None


__all__ = [
    "ANALYSIS_TRACE_VERSION",
    "AnalysisClaim",
    "AnalysisMode",
    "AnalysisTrace",
    "AnalysisTraceDraft",
    "AnalysisTraceFailureMetadata",
    "CaseAnalysisResult",
    "ClaimType",
    "EpistemicStatus",
    "MitreAssociation",
    "MitreAssociationStatus",
    "MitreSupportRole",
    "ProviderCaseAnalysis",
]
