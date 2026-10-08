from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.trace.claims import (
    CaseAnalysisClaim,
    CaseAnalysisGap,
    CaseAnalysisMode,
    CaseProviderClaim,
    CaseReadingClaim,
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
    role: str | None = Field(default=None, min_length=1, max_length=500)
    support: SupportStatus | None = None
    projection_grounding: CaseProjectionGrounding | None = None
    field_spans: dict[str, CaseClaimSpan] = Field(default_factory=dict)

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
    projection_grounding: CaseProjectionGrounding | None = None
    field_spans: dict[str, CaseClaimSpan] = Field(default_factory=dict)

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
    projection_grounding: CaseProjectionGrounding | None = None
    field_spans: dict[str, CaseClaimSpan] = Field(default_factory=dict)


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
    claims_semantically_supported: int = 0
    claims_semantically_not_supported: int = 0
    claims_semantically_unassessed: int = 0
    claims_admitted_to_judgement: int = 0
    claims_withheld_from_judgement: int = 0
    claim_verifier_calls: int = 0
    claim_validation_ms: float = Field(default=0, ge=0)
    claim_verifier_model: str | None = None
    claim_verifier_threshold: float | None = Field(default=None, ge=0.5, le=1)
    claim_verifier_artifact_sha256: str | None = None
    claim_source_units_considered: int = 0
    claim_source_units_selected: int = 0
    claim_verifier_truncated_pairs: int = 0
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


class CaseClaimSpan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claim_id: str = Field(pattern=r"^A-\d{2,}$")
    start: int = Field(ge=0, strict=True)
    end: int = Field(gt=0, strict=True)

    @model_validator(mode="after")
    def ordered_offsets(self):
        if self.end <= self.start:
            raise ValueError("Claim span end must follow its start")
        return self


class CaseViewFieldIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    view: Literal["party", "timeline_event", "impact"]
    record_index: int = Field(ge=0)
    field: Literal["name", "role", "time", "event", "description"]
    text: str = Field(min_length=1)
    reason: Literal["unresolved", "ambiguous"]
    claim_id: str = Field(pattern=r"^A-\d{2,}$")


class CaseViewExtraction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    method: str = Field(default="legacy", min_length=1, max_length=200)
    model: str
    revision: str | None = Field(default=None, pattern=r"^[a-f0-9]{40}$")
    library_version: str | None = None
    device: str | None = None
    threshold: float | None = Field(default=None, gt=0, lt=1)
    quantization: str | None = None
    runtime_revision: str | None = Field(default=None, pattern=r"^[a-f0-9]{40}$")
    field_resolution_issues: list[CaseViewFieldIssue] = Field(default_factory=list)
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
    grounding: CaseGroundingReport | None = None
    view_extraction: CaseViewExtraction | None = None
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


class CaseProviderReadingReply(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal["case_analysis_trace_v1"]
    claims: list[CaseReadingClaim] = Field(max_length=64)


class CaseProviderJudgement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal["case_analysis_trace_v1"]
    summary: str = Field(min_length=1, max_length=24_000)
    gaps: list[CaseAnalysisGap] = Field(default_factory=list, max_length=32)
    mitre_associations: list[CaseMitreAssociation] = Field(default_factory=list, max_length=64)


__all__ = [
    "CaseAnalysisTrace",
    "CaseClaimSpan",
    "CaseGroundingReport",
    "CaseImpactItem",
    "CaseInvolvedParty",
    "CaseMitreAssociation",
    "CaseProjectionGrounding",
    "CaseProviderAnalysis",
    "CaseProviderJudgement",
    "CaseProviderReading",
    "CaseProviderReadingReply",
    "CaseSummaryUnit",
    "CaseTimelineItem",
    "CaseViewExtraction",
    "CaseViewFieldIssue",
    "ProviderImpactItem",
    "ProviderParty",
    "ProviderTimelineItem",
    "SupportStatus",
]
