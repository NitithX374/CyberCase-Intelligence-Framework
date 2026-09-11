from app.services.reports.case_report_contracts import (
    CaseReportInputSnapshot,
    CaseReportSource,
    CaseReportTechnicalAugmentation,
    CaseTechnicalAugmentationStatus,
    ensure_case_report_snapshot,
    native_source_ids,
)
from app.services.reports.case_report_pdf import render_case_report_pdf
from app.services.reports.case_report_persistence import (
    CaseReportService,
    build_case_report_snapshot,
    serialize_chat_report,
)
from app.services.reports.case_report_template import (
    build_case_template_report,
    run_case_report_generation,
)
from app.services.reports.report_contracts import (
    ReportGenerationConflict,
    ReportNotFound,
    ReportRunResult,
    ReportServiceError,
    ReportValidationError,
)
from app.services.reports.report_validation import (
    source_snapshot_hash,
    validate_case_structured_report,
)

ReportService = CaseReportService
ReportGenerationError = ReportServiceError

__all__ = [
    "CaseReportInputSnapshot",
    "CaseReportService",
    "CaseReportSource",
    "CaseReportTechnicalAugmentation",
    "CaseTechnicalAugmentationStatus",
    "ReportGenerationConflict",
    "ReportGenerationError",
    "ReportNotFound",
    "ReportRunResult",
    "ReportService",
    "ReportServiceError",
    "ReportValidationError",
    "build_case_template_report",
    "build_case_report_snapshot",
    "ensure_case_report_snapshot",
    "native_source_ids",
    "render_case_report_pdf",
    "run_case_report_generation",
    "serialize_chat_report",
    "source_snapshot_hash",
    "validate_case_structured_report",
]
