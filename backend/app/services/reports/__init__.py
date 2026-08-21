"""Incident Report Generation, View Model & Export Services."""

from app.services.reports.report_generation import (
    AdmittedMitreRow,
    AnthropicReportAdapter,
    REPORT_TEMPLATE_MODEL,
    REPORT_TEMPLATE_PROMPT_VERSION,
    REPORT_TEMPLATE_PROVIDER,
    ReportInputSnapshot,
    ReportModelAdapter,
    ReportModelResponse,
    ReportProviderFailure,
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
from app.services.reports.report_prompt import REPORT_SYSTEM_PROMPT
from app.services.reports.report_provider_schema import (
    ProviderStructuredReport,
    provider_report_to_structured_report,
)
from app.services.reports.report_service import (
    ChatReportService,
    ReportGenerationConflict,
    ReportNotFound,
    ReportService,
)
from app.services.reports.report_view_model import (
    ReportLanguage,
    ReportViewModel,
    build_report_view_model,
)

ReportGenerationError = ReportProviderFailure
generate_report_payload = run_report_generation
build_report_pdf_bytes = render_chat_report_pdf

__all__ = [
    "AdmittedMitreRow",
    "AnthropicReportAdapter",
    "REPORT_TEMPLATE_MODEL",
    "REPORT_TEMPLATE_PROMPT_VERSION",
    "REPORT_TEMPLATE_PROVIDER",
    "ReportInputSnapshot",
    "ReportLanguage",
    "ReportModelAdapter",
    "ReportModelResponse",
    "ReportProviderFailure",
    "ReportRunResult",
    "ReportSourceMessage",
    "ReportValidationError",
    "ReportViewModel",
    "build_report_view_model",
    "build_template_report",
    "ReportGenerationError",
    "generate_report_payload",
    "run_report_generation",
    "source_snapshot_hash",
    "validate_structured_report",
    "build_report_pdf_bytes",
    "render_chat_report_pdf",
    "render_chat_report_html",
    "render_chat_report_html_from_view_model",
    "get_report_css",
    "REPORT_SYSTEM_PROMPT",
    "ProviderStructuredReport",
    "provider_report_to_structured_report",
    "ReportService",
    "ChatReportService",
    "ReportGenerationConflict",
    "ReportNotFound",
]
