from __future__ import annotations;

from dataclasses import dataclass, field
from typing import Literal

ReportLanguage = Literal["th", "en"]

@dataclass(frozen=True)
class TimelineViewRow:
    order: int
    time_display: str
    event: str
    source_evidence: str
    actors: str = ""
    status: str = "reported"


@dataclass(frozen=True)
class EvidenceViewRow:
    item_id: str
    title: str
    artifact_type: str
    description: str
    source_type: str
    confidence: str


@dataclass(frozen=True)
class IndicatorViewRow:
    indicator_type: str
    value: str
    note: str


@dataclass(frozen=True)
class MitreMappingViewRow:
    finding: str
    case_evidence_support: str
    technique_id: str
    technique_name: str
    status_display: str
    tactic: str
    source: str
    relevance: str


@dataclass(frozen=True)
class UnresolvedIssueViewRow:
    description: str
    category: str
    reason: str = ""


@dataclass(frozen=True)
class VerificationActionViewRow:
    order: int
    action: str


@dataclass(frozen=True)
class ProvenanceViewRow:
    label: str
    value: str


@dataclass(frozen=True)
class ReportViewModel:
    report_id: str
    case_title: str
    generated_date: str
    report_status: str
    version_label: str
    language: ReportLanguage
    i18n: dict[str, str]

    # 5.1 สรุปเหตุการณ์ / Incident Summary
    summary_paragraphs: list[str] = field(default_factory=list)

    # 5.2 ลำดับเหตุการณ์ / Chronological Timeline
    timeline_rows: list[TimelineViewRow] = field(default_factory=list)

    # 5.3 หลักฐานและตัวบ่งชี้สำคัญ / Evidence & Key Indicators
    evidence_rows: list[EvidenceViewRow] = field(default_factory=list)
    has_indicators: bool = False
    indicator_rows: list[IndicatorViewRow] = field(default_factory=list)

    # 5.5 ผลการวิเคราะห์และ MITRE ATT&CK Mapping / Technical Analysis
    has_mitre_mappings: bool = False
    mitre_rows: list[MitreMappingViewRow] = field(default_factory=list)

    # 5.6 ประเด็นที่ยังไม่สามารถยืนยันและสิ่งที่ควรตรวจสอบเพิ่มเติม / Gaps & Next Steps
    unresolved_issues: list[UnresolvedIssueViewRow] = field(default_factory=list)
    verification_actions: list[VerificationActionViewRow] = field(default_factory=list)

    # 5.7 ข้อจำกัดและข้อมูลการตรวจสอบย้อนกลับ / Limitations & Provenance
    limitations: list[str] = field(default_factory=list)
    provenance_rows: list[ProvenanceViewRow] = field(default_factory=list)
