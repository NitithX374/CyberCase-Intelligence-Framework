from __future__ import annotations

import json
import time

from pydantic import ValidationError

from app.config import settings
from app.services.reports.report_contracts import (
    REPORT_TEMPLATE_MODEL, REPORT_TEMPLATE_PROVIDER, REPORT_TEMPLATE_PROMPT_VERSION,
    ReportInputSnapshot, ReportRunResult,
)
from app.services.reports.report_template import build_template_report
from app.services.reports.report_validation import (
    ReportValidationError,
    validation_error_text,
)

async def run_report_generation(
    snapshot: ReportInputSnapshot,
) -> ReportRunResult:
    """Build one deterministic template report and fail closed."""

    started = time.perf_counter()
    provider = REPORT_TEMPLATE_PROVIDER
    model = REPORT_TEMPLATE_MODEL

    def failure(
        code: str,
        message: str,
        *,
        validation_errors: tuple[str, ...] = (),
        input_tokens: int | None = None,
        output_tokens: int | None = None,
    ) -> ReportRunResult:
        return ReportRunResult(
            status="failed",
            report=None,
            failure_code=code,
            failure_message=message,
            validation_errors=validation_errors,
            latency_ms=latency_ms(started),
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )

    if not settings.chat_report_enabled:
        return failure(
            "report_generation_disabled",
            "Report generation is disabled",
        )

    input_payload = snapshot.model_dump(mode="json")
    serialized_input = json.dumps(input_payload, ensure_ascii=False)
    if len(serialized_input) > max(1, settings.chat_report_max_input_chars):
        return failure(
            "report_input_too_large",
            "The report input exceeds the configured character limit",
        )

    try:
        report = build_template_report(snapshot)
    except (ReportValidationError, ValidationError) as exc:
        error = validation_error_text(exc)
        return failure(
            "report_validation_failed",
            "The deterministic report failed validation",
            validation_errors=(error,),
        )
    except Exception:
        return failure(
            "report_template_error",
            "The deterministic report template failed",
        )

    return ReportRunResult(
        status="completed",
        report=report,
        failure_code=None,
        failure_message=None,
        validation_errors=(),
        latency_ms=latency_ms(started),
        provider=provider,
        model=model,
        input_tokens=None,
        output_tokens=None,
    )

def latency_ms(started: float) -> float:
    return round((time.perf_counter() - started) * 1000, 3)
