from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.trace.trace import CaseProjectionGrounding, SupportStatus


class ReportRow(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ReportParty(ReportRow):
    name: str
    role: str | None
    claim_context: list[str] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)
    support: SupportStatus | None = None
    projection_grounding: CaseProjectionGrounding | None = None


class ReportEvent(ReportRow):
    time: str | None
    event: str
    references: list[str] = Field(default_factory=list)
    support: SupportStatus | None = None
    projection_grounding: CaseProjectionGrounding | None = None


class ReportImpact(ReportRow):
    description: str
    references: list[str] = Field(default_factory=list)
    support: SupportStatus | None = None
    projection_grounding: CaseProjectionGrounding | None = None


class ReportSummaryUnit(ReportRow):
    text: str
    references: list[int] = Field(default_factory=list)
    support: SupportStatus


class ReportQuoteContext(ReportRow):
    before: str = ""
    after: str = ""
    cut_before: bool = False
    cut_after: bool = False


class ReportPlace(ReportRow):
    written: str = ""
    source: str = ""


class ReportMark(ReportRow):
    marks: str
    place: Literal["ignored", "edge"]


class ReportUnverifiedQuote(ReportRow):
    written_quote: str
    evidence_unit_id: str | None = None
    places: list[ReportPlace] = Field(default_factory=list)
    meaning_passage: str | None = None


class ReportFinding(ReportRow):
    ordinal: int
    text: str
    status: str
    is_inference: bool
    source_labels: list[str] = Field(default_factory=list)
    contradicting_source_labels: list[str] = Field(default_factory=list)
    supporting_quotes: list[str] = Field(default_factory=list)
    contradicting_quotes: list[str] = Field(default_factory=list)
    supporting_contexts: list[ReportQuoteContext | None] = Field(default_factory=list)
    contradicting_contexts: list[ReportQuoteContext | None] = Field(default_factory=list)
    supporting_tolerated: list[list[ReportPlace]] = Field(default_factory=list)
    contradicting_tolerated: list[list[ReportPlace]] = Field(default_factory=list)
    supporting_marked: list[list[ReportMark]] = Field(default_factory=list)
    contradicting_marked: list[list[ReportMark]] = Field(default_factory=list)
    unverified_quotes: list[ReportUnverifiedQuote] = Field(default_factory=list)
    reasoning_summary: str | None = None


class ReportTechnique(ReportRow):
    technique_id: str
    name: str
    tactic: str
    meaning: str
    reason: str
    findings: list[int] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)


class ReportGap(ReportRow):
    topic: str
    priority: str
    status: str
    description: str
    reason: str


class ReportSource(ReportRow):
    label: str
    kind: str
    detail: str


class CaseReportContent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal["case_report_content_v1"] = "case_report_content_v1"
    title: str
    analysed: str | None = None
    summary: str
    views_derived_from_claims: bool = False
    summary_units: list[ReportSummaryUnit] = Field(default_factory=list)
    parties: list[ReportParty] = Field(default_factory=list)
    timeline: list[ReportEvent] = Field(default_factory=list)
    impacts: list[ReportImpact] = Field(default_factory=list)
    findings: list[ReportFinding] = Field(default_factory=list)
    techniques: list[ReportTechnique] = Field(default_factory=list)
    techniques_matched: bool = False
    mapping_note: str | None = None
    rationale_note: str | None = None
    gaps: list[ReportGap] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    sources: list[ReportSource] = Field(default_factory=list)


class CaseReportCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    analysis_result_id: UUID | None = None


class CaseReportRead(BaseModel):
    model_config = ConfigDict(extra="forbid")

    report_id: UUID
    version_number: int
    case_id: UUID
    analysis_result_id: UUID
    report: CaseReportContent
    created_at: datetime


__all__ = [
    "CaseReportContent",
    "CaseReportCreate",
    "CaseReportRead",
    "ReportEvent",
    "ReportFinding",
    "ReportGap",
    "ReportImpact",
    "ReportMark",
    "ReportParty",
    "ReportPlace",
    "ReportQuoteContext",
    "ReportSource",
    "ReportSummaryUnit",
    "ReportTechnique",
    "ReportUnverifiedQuote",
]
