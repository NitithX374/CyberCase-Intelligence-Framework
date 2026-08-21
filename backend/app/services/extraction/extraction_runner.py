from __future__ import annotations

import asyncio
import json
import logging
import time

import httpx
from pydantic import ValidationError

from app.config import settings
from app.services.llm.core_llm import CoreLlmConfigurationError, resolve_core_llm_target
from app.services.extraction.extraction_adapter import AnthropicExtractionAdapter
from app.services.extraction.extraction_config import BASELINE_EXTRACTION_SYSTEM_PROMPT
from app.services.extraction.extraction_contracts import (
    ExtractionFailure, ExtractionInput, ExtractionModelAdapter,
)
from app.services.extraction.extraction_results import ExtractionRunResult
from app.services.extraction.extraction_utils import normalize_model_response
from app.services.extraction.extraction_validation import validate_baseline_extraction

logger = logging.getLogger("app.extraction")

async def run_baseline_extraction(
    extraction_input: ExtractionInput,
    *,
    adapter: ExtractionModelAdapter | None = None,
) -> ExtractionRunResult:
    """Execute exactly one bounded model call and fail closed on bad output."""

    started = time.perf_counter()
    target = resolve_core_llm_target(
        settings.chat_extraction_model,
        require_key=False,
    )
    provider = target.provider
    model = target.model

    def failure(
        code: str,
        message: str,
        *,
        raw_response: str | None = None,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
    ) -> ExtractionRunResult:
        return ExtractionRunResult(
            status="failed",
            extraction=None,
            failure_code=code,
            failure_message=message,
            raw_response=raw_response,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms(started),
            provider=provider,
            model=model,
        )

    if not settings.chat_extraction_enabled:
        return failure(
            "extractor_disabled",
            "The baseline extraction module is disabled",
        )

    input_payload = extraction_input.model_dump(mode="json")
    serialized_input = json.dumps(input_payload, ensure_ascii=False)
    if len(serialized_input) > max(1, settings.chat_extraction_max_input_chars):
        return failure(
            "extraction_input_too_large",
            "The extraction input exceeds the configured character limit",
        )

    selected_adapter = adapter
    if selected_adapter is None:
        try:
            resolve_core_llm_target(settings.chat_extraction_model)
        except CoreLlmConfigurationError as exc:
            return failure(
                "extractor_not_configured",
                str(exc),
            )
        selected_adapter = AnthropicExtractionAdapter()

    raw_response: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    try:
        response = await asyncio.wait_for(
            selected_adapter.complete(
                system_prompt=BASELINE_EXTRACTION_SYSTEM_PROMPT,
                input_payload=input_payload,
                model=model,
                max_output_tokens=max(1, settings.chat_extraction_max_output_tokens),
            ),
            timeout=max(0.01, settings.chat_extraction_timeout_seconds),
        )
        raw_response, input_tokens, output_tokens = normalize_model_response(
            response
        )
    except (asyncio.TimeoutError, TimeoutError):
        return failure(
            "extraction_timeout",
            "The extraction model request timed out",
        )
    except httpx.TimeoutException:
        return failure(
            "extraction_timeout",
            "The extraction model request timed out",
        )
    except httpx.RequestError:
        return failure(
            "extraction_transport_error",
            "The extraction model request failed",
        )
    except ExtractionFailure as exc:
        return failure(
            exc.code,
            exc.message,
            raw_response=exc.raw_response,
            input_tokens=exc.input_tokens,
            output_tokens=exc.output_tokens,
        )
    except Exception:
        return failure(
            "extraction_adapter_error",
            "The extraction adapter failed",
        )

    if len(raw_response) > max(1, settings.chat_extraction_max_raw_response_chars):
        return failure(
            "extraction_response_too_large",
            "The extraction model response exceeds the configured limit",
            raw_response=raw_response,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )

    try:
        parsed = json.loads(raw_response)
    except (TypeError, ValueError):
        return failure(
            "extraction_invalid_json",
            "The extraction model did not return valid JSON",
            raw_response=raw_response,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )

    try:
        extraction = validate_baseline_extraction(parsed, extraction_input)
    except (ExtractionValidationError, ValidationError) as exc:
        logger.warning("Baseline extraction validation failed: %s | raw: %s", exc, raw_response)
        return failure(
            "extraction_validation_failed",
            "The extraction model output failed validation",
            raw_response=raw_response,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )

    return ExtractionRunResult(
        status="candidate",
        extraction=extraction,
        failure_code=None,
        failure_message=None,
        raw_response=raw_response,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=latency_ms(started),
        provider=provider,
        model=model,
    )

def latency_ms(started: float) -> float:
    return round((time.perf_counter() - started) * 1000, 3)
