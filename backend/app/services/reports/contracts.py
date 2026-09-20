from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.reports import PRELIMINARY_REPORT_SECTION_IDS, StructuredReport
from app.services.case_analysis.contracts import CaseFollowupExchange
from app.services.case_analysis.mitre_gate.llm import MitreApplicabilityRecord
from app.services.sources.case_source_bundle import CaseSourceBundle

CaseTechnicalAugmentationStatus = Literal[
    "not_applicable",
    "insufficient_context",
    "retrieved_from_rag",
    "retrieved_with_matches",
    "retrieved_without_supported_match",
    "failed",
]


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
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    case_id: UUID
    case_title: str = "CyberCase Investigation"
    analysis_result_id: UUID
    source_bundle: CaseSourceBundle
    analysis_summary: str = Field(min_length=1)
    analysis_trace: dict[str, object]
    technical_augmentation: CaseReportTechnicalAugmentation | None = None
    unresolved_issues: list[str] = Field(default_factory=list, max_length=64)
    # What the reader was asked and answered. Not case sources, but a claim may
    # rest on one, so the report has to recognise the ids.
    followup_history: tuple[CaseFollowupExchange, ...] = ()


def case_source_ids(report_input: CaseReportInput) -> set[str]:
    """Everything a report claim is allowed to cite.

    The bundle, plus the follow-up answers. An answer is not a case source and
    the report says so in its limitations — but a claim that rests on one cited
    it during analysis, and refusing the id here would fail the whole report
    over a citation that was checked and found good.
    """

    return {source.source_id for source in report_input.source_bundle.sources} | {
        item.qa_id for item in report_input.followup_history if item.is_answered
    }


class ReportServiceError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class ReportGenerationConflict(ReportServiceError):
    pass


class ReportNotFound(ReportServiceError):
    pass


class ReportValidationError(ValueError):
    pass


@dataclass(frozen=True)
class BuiltReport:
    """What building a report produced. It is a template render, so it either
    produced a report or raised; there is no provider, prompt or token count."""

    report: StructuredReport


def validate_case_structured_report(
    report: StructuredReport,
    *,
    allowed_source_ids: set[str],
    mitre_ids: set[str],
) -> None:
    section_ids = tuple(section.section_id for section in report.sections)
    if section_ids != PRELIMINARY_REPORT_SECTION_IDS:
        raise ReportValidationError("Report sections do not match the required order")
    claim_ids: set[str] = set()
    for claim in report.claims:
        if claim.claim_id in claim_ids:
            raise ReportValidationError("Report claim identifiers must be unique")
        claim_ids.add(claim.claim_id)
        if not set(claim.source_ids).issubset(allowed_source_ids):
            raise ReportValidationError(
                "A case report claim cites something that is not a case source"
            )
        if not set(claim.mitre_technique_ids).issubset(mitre_ids):
            raise ReportValidationError("A report claim cites an unrecognized MITRE technique")


__all__ = [
    "CaseReportInput",
    "CaseReportTechnicalAugmentation",
    "CaseTechnicalAugmentationStatus",
    "ReportGenerationConflict",
    "ReportNotFound",
    "BuiltReport",
    "ReportServiceError",
    "ReportValidationError",
    "case_source_ids",
    "validate_case_structured_report",
]
