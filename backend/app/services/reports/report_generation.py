from __future__ import annotations

import time

from app.services.reports.report_contracts import ReportInputSnapshot, ReportRunResult
from app.services.reports.report_template import build_template_report
from app.services.reports.report_validation import source_snapshot_hash


REPORT_PROMPT_VERSION = "deterministic_raw_evidence_report_v1"


async def run_report_generation(snapshot: ReportInputSnapshot) -> ReportRunResult:
    started = time.perf_counter()
    try:
        report = build_template_report(snapshot)
        return ReportRunResult(
            status="completed",
            report=report,
            prompt_version=REPORT_PROMPT_VERSION,
            provider="deterministic",
            model="template",
            latency_ms=round((time.perf_counter() - started) * 1000, 3),
        )
    except Exception as error:
        return ReportRunResult(
            status="failed",
            report=None,
            prompt_version=REPORT_PROMPT_VERSION,
            provider="deterministic",
            model="template",
            validation_errors=(str(error),),
            failure_code="report_generation_failed",
            failure_message="The report could not be generated.",
            latency_ms=round((time.perf_counter() - started) * 1000, 3),
        )


__all__ = [
    "REPORT_PROMPT_VERSION",
    "run_report_generation",
    "source_snapshot_hash",
]
