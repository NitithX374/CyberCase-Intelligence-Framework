"""Incident Report Generation, View Model & Export Services."""

from app.services.reports.report_generation import (
    AdmittedMitreRow,
    REPORT_TEMPLATE_MODEL,
    REPORT_TEMPLATE_PROMPT_VERSION,
    REPORT_TEMPLATE_PROVIDER,
    ReportInputSnapshot,
    ReportRunResult,
    ReportSourceMessage,
    ReportValidationError,
    build_template_report,
    run_report_generation,
    source_snapshot_hash,
    validate_structured_report,
)
from app.services.reports.report_html import (
    get_report_css,
    render_chat_report_html,
    render_chat_report_html_from_view_model,
)
from app.services.reports.report_pdf import render_chat_report_pdf
from app.services.reports.report_service import (
    ChatReportService,
    ReportGenerationConflict,
    ReportNotFound,
    ReportService,
    ReportServiceError,
)
from app.services.reports.report_view_model import (
    ReportLanguage,
    ReportViewModel,
    build_report_view_model,
)

ReportGenerationError = ReportServiceError

__all__ = [
    "AdmittedMitreRow",
    "REPORT_TEMPLATE_MODEL",
    "REPORT_TEMPLATE_PROMPT_VERSION",
    "REPORT_TEMPLATE_PROVIDER",
    "ReportInputSnapshot",
    "ReportLanguage",
    "ReportRunResult",
    "ReportSourceMessage",
    "ReportValidationError",
    "ReportViewModel",
    "build_report_view_model",
    "build_template_report",
    "ReportGenerationError",
    "run_report_generation",
    "source_snapshot_hash",
    "validate_structured_report",
    "render_chat_report_pdf",
    "render_chat_report_html",
    "render_chat_report_html_from_view_model",
    "get_report_css",
    "ReportService",
    "ChatReportService",
    "ReportGenerationConflict",
    "ReportNotFound",
    "ReportServiceError",
]
