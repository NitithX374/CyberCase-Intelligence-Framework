"""Typed Case report output and API contracts."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

ReportSupportType = Literal[
    "user_reported",
    "analytical_inference",
    "unknown",
]
ReportStatus = Literal["provisional_unverified"]
ReportPersistenceStatus = Literal["completed", "failed"]
ReportValidationStatus = Literal["validated", "failed"]
ReportVersion = str
ReportSectionId = Literal[
    "case_summary",
    "case_evidence",
    "mitre_attack_mapping",
    "mapping_rationale",
    "evidence_to_examine",
    "preliminary_recommendations",
    "system_limitations",
]
ReportHeading = str

PRELIMINARY_REPORT_SECTION_IDS: tuple[str, ...] = (
    "case_summary",
    "case_evidence",
    "mitre_attack_mapping",
    "mapping_rationale",
    "evidence_to_examine",
    "preliminary_recommendations",
    "system_limitations",
)

PRELIMINARY_REPORT_SECTION_HEADINGS: dict[str, str] = {
    "case_summary": "1. สรุปคดี",
    "case_evidence": "2. ตัวบ่งชี้ที่พบ",
    "mitre_attack_mapping": "3. MITRE ATT&CK Mapping",
    "mapping_rationale": "4. เหตุผลของการ Mapping",
    "evidence_to_examine": "5. หลักฐานที่ควรตรวจสอบ",
    "preliminary_recommendations": "6. คำแนะนำเบื้องต้น",
    "system_limitations": "7. ข้อจำกัดของระบบ",
}


class ReportClaim(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claim_id: str = Field(min_length=1, max_length=80)
    section_id: ReportSectionId
    text: str = Field(min_length=1, max_length=4_000)
    support_type: ReportSupportType
    source_evidence_ids: list[str] = Field(default_factory=list, max_length=32)
    mitre_technique_ids: list[str] = Field(default_factory=list, max_length=32)


class ReportSection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    section_id: ReportSectionId
    heading: ReportHeading
    paragraphs: list[str] = Field(default_factory=list, max_length=16)
    items: list[str] = Field(default_factory=list, max_length=256)


class StructuredReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    report_version: ReportVersion = "preliminary_analysis_report_v1"
    status: ReportStatus = "provisional_unverified"
    title: str = Field(min_length=1, max_length=200)
    sections: list[ReportSection] = Field(default_factory=list)
    claims: list[ReportClaim] = Field(default_factory=list, max_length=96)
    limitations: list[str] = Field(default_factory=list, max_length=32)


class CaseReportCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    analysis_result_id: UUID | None = None
    idempotency_key: str | None = Field(default=None, max_length=255)

    @field_validator("idempotency_key")
    @classmethod
    def normalize_idempotency_key(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class CaseReportRead(BaseModel):
    model_config = ConfigDict(extra="forbid")

    report_id: UUID
    version_number: int
    idempotency_key: str
    case_id: UUID
    analysis_result_id: UUID
    retrieval_context_id: str | None = None
    prompt_version: str
    persistence_status: ReportPersistenceStatus
    validation_status: ReportValidationStatus
    report: StructuredReport | None
    validation_errors: list[str]
    failure_code: str | None
    failure_message: str | None
    created_at: datetime
    finished_at: datetime | None
    latency_ms: float | None
    input_tokens: int | None
    output_tokens: int | None


__all__ = [
    "CaseReportCreate",
    "CaseReportRead",
    "PRELIMINARY_REPORT_SECTION_HEADINGS",
    "PRELIMINARY_REPORT_SECTION_IDS",
    "ReportClaim",
    "ReportHeading",
    "ReportPersistenceStatus",
    "ReportSection",
    "ReportSectionId",
    "ReportStatus",
    "ReportSupportType",
    "ReportValidationStatus",
    "ReportVersion",
    "StructuredReport",
]
