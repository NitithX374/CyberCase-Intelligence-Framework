from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.trace.claims import (
    CaseAnalysisClaim,
    CaseAnalysisGap,
    CaseAnalysisMode,
    CaseProviderClaim,
    ClaimIds,
    clipped,
    normalize_identifier,
)

MAX_SUMMARY_CHARS = 24_000

SupportStatus = Literal["bound", "mixed", "unbound", "no_claim"]


class CaseProjectionGrounding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    verdict: Literal["supported", "not_supported", "unassessed"]
    reason: str = Field(min_length=1, max_length=120)
    model: str | None = Field(default=None, max_length=200)
    entailment: float | None = Field(default=None, ge=0, le=1)


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
    support: SupportStatus | None = None
    projection_grounding: CaseProjectionGrounding | None = None


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
    support: SupportStatus | None = None
    projection_grounding: CaseProjectionGrounding | None = None


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
    support: SupportStatus | None = None
    projection_grounding: CaseProjectionGrounding | None = None


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


class CaseGroundingReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claims: int = 0
    citations_claimed: int = 0
    citations_verified: int = 0
    citations_pointed: int = 0
    citations_unfound: int = 0
    claims_without_citation: int = 0
    claims_duplicated: int = 0
    citations_duplicated: int = 0
    citations_marked: int = 0
    citations_meaning_pointed: int = 0
    evidence_ids_claimed: int = 0
    evidence_ids_resolved: int = 0
    evidence_ids_invalid: int = 0
    evidence_id_resolution_rate: float | None = Field(default=None, ge=0, le=1)
    claims_with_direct_evidence: int = 0
    claims_with_recovered_evidence: int = 0
    claims_without_resolved_evidence: int = 0
    meaning_pointer_eligible: int = 0
    meaning_pointer_attempted: int = 0
    meaning_pointer_unavailable: int = 0
    meaning_pointer_unavailable_reason: str | None = Field(default=None, max_length=120)
    meaning_pointer_skipped: int = 0
    associations_outside_context: int = 0
    associations_without_claim: int = 0
    summary_ids_unknown: int = 0
    sources_cited: int = 0
    sources_total: int = 0

    @model_validator(mode="before")
    @classmethod
    def without_retired_counts(cls, data: object) -> object:
        if isinstance(data, dict) and "citations_paraphrased" in data:
            data = {key: value for key, value in data.items() if key != "citations_paraphrased"}
        return data


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
    grounding: CaseGroundingReport | None = None
    stop_reason: str | None = Field(default=None, max_length=40)


class CaseProviderAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal["case_analysis_trace_v1"]
    claims: list[CaseProviderClaim] = Field(max_length=64)
    summary: str = Field(min_length=1, max_length=MAX_SUMMARY_CHARS)
    involved_parties: list[ProviderParty] = Field(max_length=64)
    timeline: list[ProviderTimelineItem] = Field(max_length=64)
    impacts: list[ProviderImpactItem] = Field(max_length=64)
    gaps: list[CaseAnalysisGap] = Field(default_factory=list, max_length=32)
    mitre_associations: list[CaseMitreAssociation] = Field(default_factory=list, max_length=64)


class CaseProviderReading(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal["case_analysis_trace_v1"]
    claims: list[CaseAnalysisClaim] = Field(max_length=64)
    involved_parties: list[CaseInvolvedParty] = Field(max_length=64)
    timeline: list[CaseTimelineItem] = Field(max_length=64)
    impacts: list[CaseImpactItem] = Field(max_length=64)


class CaseProviderReadingReply(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal["case_analysis_trace_v1"]
    claims: list[CaseProviderClaim] = Field(max_length=64)
    involved_parties: list[ProviderParty] = Field(max_length=64)
    timeline: list[ProviderTimelineItem] = Field(max_length=64)
    impacts: list[ProviderImpactItem] = Field(max_length=64)


class CaseProviderJudgement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal["case_analysis_trace_v1"]
    summary: str = Field(min_length=1, max_length=24_000)
    gaps: list[CaseAnalysisGap] = Field(default_factory=list, max_length=32)
    mitre_associations: list[CaseMitreAssociation] = Field(default_factory=list, max_length=64)


__all__ = [
    "CaseAnalysisTrace",
    "CaseGroundingReport",
    "CaseInvolvedParty",
    "CaseImpactItem",
    "CaseMitreAssociation",
    "CaseProviderAnalysis",
    "CaseProjectionGrounding",
    "CaseProviderJudgement",
    "CaseProviderReading",
    "CaseProviderReadingReply",
    "CaseSummaryUnit",
    "CaseTimelineItem",
    "ProviderImpactItem",
    "ProviderParty",
    "ProviderTimelineItem",
    "SupportStatus",
]
