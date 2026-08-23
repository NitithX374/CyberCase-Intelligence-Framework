from __future__ import annotations;

from app.models.report import ChatReport
from app.schemas.reports import ChatReportRead, StructuredReport

def serialize_chat_report(report: ChatReport) -> ChatReportRead:
    structured_report: StructuredReport | None = None
    if isinstance(report.structured_report, dict):
        structured_report = StructuredReport.model_validate(report.structured_report)
    validation_errors = report.validation_errors_json
    if not isinstance(validation_errors, list):
        validation_errors = []
    return ChatReportRead(
        report_id=report.id,
        thread_id=report.thread_id,
        version_number=report.version_number,
        idempotency_key=report.idempotency_key,
        source_snapshot_hash=report.source_snapshot_hash,
        analysis_message_id=report.analysis_message_id,
        retrieval_context_id=report.retrieval_context_id,
        prompt_version=report.prompt_version,
        provider=report.provider,
        model=report.model,
        decoding_settings=dict(report.decoding_settings or {}),
        persistence_status=report.status,
        validation_status=report.validation_status,
        report=structured_report,
        validation_errors=[str(error) for error in validation_errors],
        failure_code=report.failure_code,
        failure_message=report.failure_message,
        created_at=report.created_at,
        finished_at=report.finished_at,
        latency_ms=report.latency_ms,
        input_tokens=report.input_tokens,
        output_tokens=report.output_tokens,
        source_snapshot=report.source_snapshot_json if isinstance(report.source_snapshot_json, dict) else None,
    )
