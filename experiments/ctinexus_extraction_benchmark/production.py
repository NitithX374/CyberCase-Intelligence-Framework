from __future__ import annotations

from typing import Any

from .runtime import prepare_runtime

prepare_runtime()

from app.config import settings
from app.services.extraction import extraction_runner
from app.services.extraction.extraction_contracts import ExtractionValidationError
from app.services.extraction.extraction_runner import run_baseline_extraction

from backend.experiments.ctinexus.adapter import ctinexus_doc_to_extraction_input

from .constants import PRODUCTION_MODEL, PRODUCTION_PROMPT_VERSION, PRODUCTION_SCHEMA_VERSION
from .dataset import CTINexusCase
from .projection import production_prediction

extraction_runner.ExtractionValidationError = ExtractionValidationError


def _api_call_count(result: Any, serialized_input_length: int) -> int:
    no_call_codes = {
        "extractor_disabled",
        "extraction_input_too_large",
        "extractor_not_configured",
    }
    if result.failure_code in no_call_codes:
        return 0
    if serialized_input_length <= 0:
        return 0
    return 1


async def extract_production(case: CTINexusCase, model: str = PRODUCTION_MODEL):
    settings.chat_extraction_model = model
    extraction_input = ctinexus_doc_to_extraction_input(case.document)
    serialized_input_length = len(extraction_input.model_dump_json())
    result = await run_baseline_extraction(extraction_input)
    diagnostics = {
        "api_calls": _api_call_count(result, serialized_input_length),
        "validation_failure": result.failure_code == "extraction_validation_failed",
        "empty_output": bool(result.extraction is not None and not result.extraction.entities and not result.extraction.relationships),
        "provider": result.provider,
        "returned_model": result.model,
        "input_tokens": result.input_tokens,
        "output_tokens": result.output_tokens,
        "approximate_cost": None,
        "cost_note": "The production extraction client exposes token usage but not request cost.",
    }
    contract = {
        "entrypoint": "backend.app.services.extraction.extraction_runner.run_baseline_extraction",
        "model": model,
        "prompt_version": PRODUCTION_PROMPT_VERSION,
        "schema_version": PRODUCTION_SCHEMA_VERSION,
        "mode": "single_pass_llm",
    }
    return production_prediction(
        case,
        result.extraction,
        model=model,
        status="success" if result.extraction is not None else "failed",
        failure_code=result.failure_code,
        failure_message=result.failure_message,
        latency_ms=result.latency_ms,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        diagnostics=diagnostics,
        contract=contract,
    )
