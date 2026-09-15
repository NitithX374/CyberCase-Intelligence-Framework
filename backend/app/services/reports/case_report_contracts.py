from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.services.case_analysis.mitreApplicabilityGate import MitreApplicabilityRecord


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
    exact_text: str = Field(min_length=1)
    filename: str | None = None


class CaseReportTechnicalAugmentation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal["case_mitre_augmentation_v1"]
    status: CaseTechnicalAugmentationStatus
    applicability: MitreApplicabilityRecord
    retrieval_context_id: str | None = None
    retrieval_context_reused: bool = False
    mitre_table: list[dict[str, object]] = Field(default_factory=list, max_length=256)
    association_ids: list[str] = Field(default_factory=list, max_length=64)
    failure_code: str | None = Field(default=None, max_length=120)


class CaseReportInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: UUID
    case_title: str = "CyberCase Investigation"
    analysis_result_id: UUID
    evidence_revision: int = Field(ge=0)
    sources: list[CaseReportSource] = Field(min_length=1, max_length=256)
    analysis_answer: str = Field(min_length=1)
    analysis_summary: str = Field(min_length=1)
    analysis_trace: dict[str, object]
    technical_augmentation: CaseReportTechnicalAugmentation | None = None
    unresolved_issues: list[str] = Field(default_factory=list, max_length=64)


def native_source_ids(report_input: CaseReportInput) -> set[str]:
    return {str(source.source_id) for source in report_input.sources}


__all__ = [
    "CaseReportInput",
    "CaseReportSource",
    "CaseReportTechnicalAugmentation",
    "CaseTechnicalAugmentationStatus",
    "native_source_ids",
]
