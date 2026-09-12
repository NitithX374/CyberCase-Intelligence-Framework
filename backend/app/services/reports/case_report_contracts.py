from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.services.case_analysis.mitreApplicabilityGate import MitreApplicabilityRecord
from app.services.reports.report_contracts import ReportValidationError

CaseTechnicalAugmentationStatus = Literal[
    "not_applicable",
    "insufficient_context",
    "retrieved_with_matches",
    "retrieved_without_supported_match",
    "failed",
]


class CaseReportSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: UUID
    source_kind: str = Field(min_length=1, max_length=40)
    revision_id: UUID
    revision: int = Field(ge=1)
    exact_text: str = Field(min_length=1)
    text_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    provenance_json: dict[str, object]
    document_id: UUID | None = None
    filename: str | None = None


class CaseReportTechnicalAugmentation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal["case_mitre_augmentation_v1"]
    status: CaseTechnicalAugmentationStatus
    applicability: MitreApplicabilityRecord
    retrieval_context_id: str | None = None
    retrieval_context_reused: bool = False
    mitre_table: list[dict[str, object]] = Field(default_factory=list, max_length=256)
    query_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    association_ids: list[str] = Field(default_factory=list, max_length=64)
    failure_code: str | None = Field(default=None, max_length=120)


class CaseReportInputSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    format_version: Literal["case_report_snapshot_v1"] = "case_report_snapshot_v1"
    case_id: UUID
    case_title: str = "CyberCase Investigation"
    thread_id: UUID | None = None
    thread_title: str | None = None
    analysis_result_id: UUID
    evidence_snapshot_id: UUID
    evidence_revision: int = Field(ge=0)
    created_at: datetime
    sources: list[CaseReportSource] = Field(min_length=1, max_length=256)
    evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    analysis_answer: str = Field(min_length=1)
    analysis_summary: str = Field(min_length=1)
    analysis_trace: dict[str, object]
    retrieval_context_id: str | None = Field(default=None, min_length=1, max_length=160)
    technical_augmentation: CaseReportTechnicalAugmentation | None = None
    unresolved_issues: list[str] = Field(default_factory=list, max_length=64)


def native_source_ids(snapshot: CaseReportInputSnapshot) -> set[str]:
    return {str(source.source_id) for source in snapshot.sources}


def ensure_case_report_snapshot(snapshot: object) -> CaseReportInputSnapshot:
    try:
        return CaseReportInputSnapshot.model_validate(snapshot)
    except Exception as error:
        raise ReportValidationError("Case report snapshot is invalid") from error


__all__ = [
    "CaseReportInputSnapshot",
    "CaseReportSource",
    "CaseReportTechnicalAugmentation",
    "CaseTechnicalAugmentationStatus",
    "ensure_case_report_snapshot",
    "native_source_ids",
]
