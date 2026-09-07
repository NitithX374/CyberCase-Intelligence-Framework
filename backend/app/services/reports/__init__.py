from app.services.reports.report_contracts import (
    AdmittedMitreRow,
    ReportGenerationConflict,
    ReportInputSnapshot,
    ReportNotFound,
    ReportRunResult,
    ReportServiceError,
    ReportSourceMessage,
    ReportValidationError,
    read_render_snapshot,
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
from app.services.reports.report_persistence import ChatReportService
from app.services.reports.report_template import build_template_report
from app.services.reports.report_validation import (
    source_snapshot_hash,
    validate_structured_report,
)
from app.services.reports.report_view_model_builder import build_report_view_model
from app.services.reports.report_view_model_contracts import (
    ReportLanguage,
    ReportViewModel,
)

ReportService = ChatReportService
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
    "read_render_snapshot",
    "render_chat_report_html",
    "render_chat_report_html_from_view_model",
    "render_chat_report_pdf",
    "run_report_generation",
    "source_snapshot_hash",
    "validate_structured_report",
]
