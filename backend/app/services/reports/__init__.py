from app.services.reports.report_contracts import (
    AdmittedMitreRow,
    ReportInputSnapshot,
    ReportRunResult,
    ReportSourceMessage,
    ReportValidationError,
)
from app.services.reports.report_errors import (
    ReportGenerationConflict,
    ReportNotFound,
    ReportServiceError,
)
from app.services.reports.report_generation import (
    REPORT_PROMPT_VERSION,
    run_report_generation,
)
from app.services.reports.report_html import (
    get_report_css,
    render_chat_report_html,
    render_chat_report_html_from_view_model,
)
from app.services.reports.report_pdf import render_chat_report_pdf
from app.services.reports.report_service import ChatReportService, ReportService
from app.services.reports.report_template import build_template_report
from app.services.reports.report_validation import (
    source_snapshot_hash,
    validate_structured_report,
)
from app.services.reports.report_view_model import (
    ReportLanguage,
    ReportViewModel,
    build_report_view_model,
)

ReportGenerationError = ReportServiceError

__all__ = [
    "AdmittedMitreRow",
    "ChatReportService",
    "REPORT_PROMPT_VERSION",
    "ReportGenerationConflict",
    "ReportGenerationError",
    "ReportInputSnapshot",
    "ReportLanguage",
    "ReportNotFound",
    "ReportRunResult",
    "ReportService",
    "ReportServiceError",
    "ReportSourceMessage",
    "ReportValidationError",
    "ReportViewModel",
    "build_report_view_model",
    "build_template_report",
    "get_report_css",
    "render_chat_report_html",
    "render_chat_report_html_from_view_model",
    "render_chat_report_pdf",
    "run_report_generation",
    "source_snapshot_hash",
    "validate_structured_report",
]
