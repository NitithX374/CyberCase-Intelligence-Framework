from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.services.case_analysis.analysis_source_contracts import (
    CaseAnalysisClaim,
    CaseAnalysisGap,
    CaseAnalysisMode,
    normalize_identifier,
)


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
            return [normalize_identifier(item, "A", "A|claim|c") for item in value]
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
            return [normalize_identifier(item, "A", "A|claim|c") for item in value]
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
            return [normalize_identifier(item, "A", "A|claim|c") for item in value]
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
        return normalize_identifier(value, "MA", "MA|assoc|association")

    @field_validator("claim_ids", mode="before")
    @classmethod
    def normalize_claim_ids(cls, value: object) -> object:
        if isinstance(value, (list, tuple)):
            return [normalize_identifier(item, "A", "A|claim|c") for item in value]
        return value


class CaseAnalysisTrace(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal["case_analysis_trace_v1"] = "case_analysis_trace_v1"
    validation_status: Literal["validated"] = "validated"
    analysis_mode: CaseAnalysisMode
    summary: str = Field(min_length=1, max_length=24_000)
    involved_parties: list[CaseInvolvedParty] = Field(default_factory=list, max_length=64)
    timeline: list[CaseTimelineItem] = Field(default_factory=list, max_length=64)
    claims: list[CaseAnalysisClaim] = Field(max_length=64)
    impacts: list[CaseImpactItem] = Field(default_factory=list, max_length=64)
    gaps: list[CaseAnalysisGap] = Field(default_factory=list, max_length=64)
    mitre_associations: list[CaseMitreAssociation] = Field(default_factory=list, max_length=64)
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
    mitre_associations: list[CaseMitreAssociation] = Field(default_factory=list, max_length=64)


class CaseAnalysisFailureMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal["case_analysis_trace_v1"] = "case_analysis_trace_v1"
    validation_status: Literal["unavailable"] = "unavailable"
    failure_code: str = Field(min_length=1, max_length=120)


__all__ = [
    "CaseAnalysisFailureMetadata",
    "CaseAnalysisTrace",
    "CaseInvolvedParty",
    "CaseImpactItem",
    "CaseMitreAssociation",
    "CaseProviderAnalysis",
    "CaseTimelineItem",
]
