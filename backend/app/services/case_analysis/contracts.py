from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


ANALYSIS_TRACE_VERSION = "analysis_trace_v2"
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
    "ProviderCaseAnalysis",
]
