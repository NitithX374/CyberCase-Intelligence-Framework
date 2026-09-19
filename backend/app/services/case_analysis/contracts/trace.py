from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.services.case_analysis.contracts.sources import (
    CaseAnalysisClaim,
    CaseAnalysisGap,
    CaseAnalysisMode,
    normalize_identifier,
)


class CaseInvolvedParty(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=500)
    role: str = Field(min_length=1, max_length=500)
    claim_ids: list[str] = Field(default_factory=list, max_length=64)

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
    claim_ids: list[str] = Field(default_factory=list, max_length=64)

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
    claim_ids: list[str] = Field(default_factory=list, max_length=64)

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
    # What the technique means, in the reader's own words rather than ATT&CK's.
    # Optional because analyses stored before it existed have to keep reading.
    plain_meaning: str = Field(default="", max_length=600)
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


class CaseGroundingReport(BaseModel):
    """How much of what the model asserted is actually bound to a source.

    A quotation the model invented is dropped during validation rather than
    rejected, because one bad citation should not lose a whole analysis. Dropped
    silently, though, a fabricated quote and a correct one look the same
    afterwards. These are the counts that tell them apart.
    """

    model_config = ConfigDict(extra="forbid")

    claims: int = 0
    citations_claimed: int = 0
    citations_verified: int = 0
    # Of the citations that were not found: wording drawn from the source but
    # quoted loosely, against wording that is in no source at all. The first is
    # a real fact quoted badly; only the second is an invention.
    citations_paraphrased: int = 0
    citations_unfound: int = 0
    claims_without_citation: int = 0
    # Two claims under one id: the second is dropped, because everything
    # downstream keys on it.
    claims_duplicated: int = 0
    # A technique the model named that the retrieval never returned — the
    # ATT&CK counterpart of a quotation that is in no source.
    associations_outside_context: int = 0
    # How much of the case was drawn on at all. Grounding alone rises when an
    # analysis drops what it cannot support, so the two are only readable
    # together: quoting one sentence perfectly is not a better analysis.
    sources_cited: int = 0
    sources_total: int = 0


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
    # Written by validation, not by the model. Absent on traces stored
    # before it was counted.
    grounding: CaseGroundingReport | None = None


class CaseProviderAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal["case_analysis_trace_v1"]
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
