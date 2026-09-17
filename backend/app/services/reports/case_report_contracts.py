from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Literal
from uuid import UUID

from app.schemas.reports import PRELIMINARY_REPORT_SECTION_IDS, StructuredReport
from app.services.case_materials.case_source_bundle import CaseSourceBundle
from app.services.case_analysis.mitre_applicability_gate import MitreApplicabilityRecord


CaseTechnicalAugmentationStatus = Literal[
    "not_applicable",
    "insufficient_context",
    "retrieved_from_rag",
    "retrieved_with_matches",
    "retrieved_without_supported_match",
    "failed",
]


@dataclass(frozen=True)
class CaseReportTechnicalAugmentation:
    status: CaseTechnicalAugmentationStatus = "not_applicable"
    applicability: MitreApplicabilityRecord | None = None
    retrieval_context_id: str | None = None
    retrieval_context_reused: bool = False
    mitre_table: list[dict[str, object]] = field(default_factory=list)
    association_ids: list[str] = field(default_factory=list)
    failure_code: str | None = None
    version: str = "case_mitre_augmentation_v1"

    def model_dump(self, *args: object, **kwargs: object) -> dict[str, object]:
        return {
            "status": self.status,
            "applicability": self.applicability,
            "retrieval_context_id": self.retrieval_context_id,
            "retrieval_context_reused": self.retrieval_context_reused,
            "mitre_table": self.mitre_table,
            "association_ids": self.association_ids,
            "failure_code": self.failure_code,
            "version": self.version,
        }

    @classmethod
    def model_validate(cls, value: object) -> CaseReportTechnicalAugmentation:
        if isinstance(value, cls):
            return value
        if not isinstance(value, dict):
            raise TypeError(f"Expected dict, got {type(value)}")
        return cls(
            status=str(value.get("status") or "not_applicable"),
            applicability=value.get("applicability"),
            retrieval_context_id=value.get("retrieval_context_id"),
            retrieval_context_reused=bool(value.get("retrieval_context_reused", False)),
            mitre_table=list(value.get("mitre_table") or []),
            association_ids=list(value.get("association_ids") or []),
            failure_code=value.get("failure_code"),
            version=str(value.get("version") or "case_mitre_augmentation_v1"),
        )


@dataclass(frozen=True)
class CaseReportInput:
    case_id: UUID
    analysis_result_id: UUID
    source_bundle: CaseSourceBundle
    analysis_answer: str
    analysis_summary: str
    analysis_trace: dict[str, object]
    case_title: str = "CyberCase Investigation"
    technical_augmentation: CaseReportTechnicalAugmentation | None = None
    unresolved_issues: list[str] = field(default_factory=list)

    def model_copy(self, *, update: dict[str, object] | None = None) -> CaseReportInput:
        if not update:
            return self
        return replace(self, **update)


def case_source_ids(report_input: CaseReportInput) -> set[str]:
    return {source.source_id for source in report_input.source_bundle.sources}


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
class ReportRunResult:
    status: Literal["completed", "failed"]
    report: StructuredReport | None
    prompt_version: str
    provider: str = "deterministic"
    model: str = "case-template"
    validation_errors: tuple[str, ...] = ()
    failure_code: str | None = None
    failure_message: str | None = None
    latency_ms: float | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None


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
        if not set(claim.source_evidence_ids).issubset(allowed_source_ids):
            raise ReportValidationError("A case report claim cites a non-evidence source")
        if not set(claim.mitre_technique_ids).issubset(mitre_ids):
            raise ReportValidationError("A report claim cites an unrecognized MITRE technique")


__all__ = [
    "CaseReportInput",
    "CaseReportTechnicalAugmentation",
    "CaseTechnicalAugmentationStatus",
    "ReportGenerationConflict",
    "ReportNotFound",
    "ReportRunResult",
    "ReportServiceError",
    "ReportValidationError",
    "case_source_ids",
    "validate_case_structured_report",
]
