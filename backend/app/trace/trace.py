from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.trace.claims import (
    CaseAnalysisClaim,
    CaseAnalysisGap,
    CaseAnalysisMode,
    CaseReadingClaim,
    ClaimIds,
    clipped,
    normalize_identifier,
)

MAX_SUMMARY_CHARS = 24_000

SupportStatus = Literal["bound", "mixed", "unbound", "no_claim"]


class ProviderParty(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=500)
    role: str = Field(min_length=1, max_length=500)
    claim_ids: ClaimIds = Field(default_factory=list)

    @field_validator("name", "role")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("party text values must be non-empty")
        return normalized


class CaseInvolvedParty(ProviderParty):
    role: str | None = Field(default=None, min_length=1, max_length=500)
    support: SupportStatus | None = None

    @field_validator("name", "role")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        return None if value is None else super().normalize_text(value)


class ProviderTimelineItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    time: str = Field(min_length=1, max_length=500)
    event: str = Field(min_length=1, max_length=2_000)
    claim_ids: ClaimIds = Field(default_factory=list)

    @field_validator("time", "event")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("timeline text values must be non-empty")
        return normalized


class CaseTimelineItem(ProviderTimelineItem):
    time: str | None = Field(default=None, min_length=1, max_length=500)
    event: str = Field(min_length=1, max_length=4_000)
    support: SupportStatus | None = None

    @field_validator("time", "event")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        return None if value is None else super().normalize_text(value)


class ProviderImpactItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: str = Field(min_length=1, max_length=2_000)
    claim_ids: ClaimIds = Field(default_factory=list)

    @field_validator("description")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("impact text values must be non-empty")
        return normalized


class CaseImpactItem(ProviderImpactItem):
    description: str = Field(min_length=1, max_length=4_000)
    support: SupportStatus | None = None


class CaseMitreAssociation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    association_id: str = Field(pattern=r"^MA-\d{2,}$", max_length=80)
    technique_id: str
    claim_ids: ClaimIds
    reason: str = Field(min_length=1, max_length=4_000)
    plain_meaning: Annotated[str, clipped(600)] = Field(default="", max_length=600)
    status: Literal["candidate_only"]
    support_role: Literal["external_technical_context"]

    @field_validator("association_id", mode="before")
    @classmethod
    def normalize_association_id(cls, value: object) -> object:
        return normalize_identifier(value, "MA", "MA|assoc|association")

    @field_validator("technique_id", mode="before")
    @classmethod
    def normalize_technique_id(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


class CaseSummaryUnit(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1, max_length=MAX_SUMMARY_CHARS)
    claim_ids: ClaimIds = Field(default_factory=list)
    support: SupportStatus


class CaseViewExtraction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    method: str = Field(min_length=1, max_length=200)
    model: str
    input_claim_ids: ClaimIds
    excluded_claim_ids: ClaimIds
    duration_ms: float = Field(ge=0)
    status: Literal["completed", "failed", "skipped"] = "completed"
    warning: str | None = Field(default=None, max_length=200)
    items_dropped: int = Field(default=0, ge=0)


class CaseAnalysisTrace(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal["case_analysis_trace_v1"] = "case_analysis_trace_v1"
    validation_status: Literal["validated"] = "validated"
    analysis_mode: CaseAnalysisMode
    summary: str = Field(min_length=1, max_length=MAX_SUMMARY_CHARS)
    summary_units: list[CaseSummaryUnit] = Field(default_factory=list)
    involved_parties: list[CaseInvolvedParty] = Field(default_factory=list, max_length=64)
    timeline: list[CaseTimelineItem] = Field(default_factory=list, max_length=64)
    claims: list[CaseAnalysisClaim] = Field(max_length=64)
    impacts: list[CaseImpactItem] = Field(default_factory=list, max_length=64)
    gaps: list[CaseAnalysisGap] = Field(default_factory=list, max_length=64)
    mitre_associations: list[CaseMitreAssociation] = Field(default_factory=list, max_length=64)
    retrieval_context_id: str | None = Field(default=None, min_length=1, max_length=160)
    view_extraction: CaseViewExtraction | None = None
    stop_reason: str | None = Field(default=None, max_length=40)


class CaseProviderReading(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal["case_analysis_trace_v1"]
    claims: list[CaseAnalysisClaim] = Field(max_length=64)


class CaseProviderReadingReply(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal["case_analysis_trace_v1"]
    claims: list[CaseReadingClaim] = Field(max_length=64)


class CaseProviderJudgement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal["case_analysis_trace_v1"]
    summary: str = Field(min_length=1, max_length=24_000)
    gaps: list[CaseAnalysisGap] = Field(default_factory=list, max_length=32)


__all__ = [
    "CaseAnalysisTrace",
    "CaseImpactItem",
    "CaseInvolvedParty",
    "CaseMitreAssociation",
    "CaseProviderJudgement",
    "CaseProviderReading",
    "CaseProviderReadingReply",
    "CaseSummaryUnit",
    "CaseTimelineItem",
    "CaseViewExtraction",
    "ProviderImpactItem",
    "ProviderParty",
    "ProviderTimelineItem",
    "SupportStatus",
]
