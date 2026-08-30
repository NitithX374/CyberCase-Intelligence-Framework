from __future__ import annotations

import sys
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from .constants import PROJECT_ROOT


def production_extraction_contract() -> dict[str, Any]:
    backend = str(PROJECT_ROOT / "backend")
    if backend not in sys.path:
        sys.path.insert(0, backend)
    from app.config import settings
    from app.services.extraction.extraction_config import BASELINE_EXTRACTION_MODE, BASELINE_EXTRACTION_PROMPT_VERSION, BASELINE_EXTRACTION_VERSION
    from app.services.llm.core_llm import resolve_core_llm_target
    target = resolve_core_llm_target(settings.chat_extraction_model, require_key=False)
    return {"entrypoint": "backend.app.services.extraction.extraction_runner.run_baseline_extraction", "version": BASELINE_EXTRACTION_VERSION, "mode": BASELINE_EXTRACTION_MODE, "prompt_version": BASELINE_EXTRACTION_PROMPT_VERSION, "provider": target.provider, "model": target.model, "fallback": None}


async def extract_case_state(sample_id: str, source: str) -> dict[str, Any]:
    backend = str(PROJECT_ROOT / "backend")
    if backend not in sys.path:
        sys.path.insert(0, backend)
    from app.services.extraction.extraction_contracts import ExtractionInput, ExtractionSourceMessage, ExtractionValidationError
    from app.services.extraction import extraction_runner

    extraction_runner.ExtractionValidationError = ExtractionValidationError

    extraction_input = ExtractionInput(
        thread_id=uuid5(NAMESPACE_URL, f"sevenllm-representation:{sample_id}:thread"),
        messages=[ExtractionSourceMessage(message_id=uuid5(NAMESPACE_URL, f"sevenllm-representation:{sample_id}:message"), ordinal=1, source_type="user_case_statement", content=source)],
    )
    result = await extraction_runner.run_baseline_extraction(extraction_input)
    case_state = result.extraction.model_dump(mode="json") if result.extraction else None
    return {
        "status": result.status, "extraction_success": result.extraction is not None,
        "case_state": case_state, "failure_code": result.failure_code,
        "failure_reason": result.failure_message, "latency_ms": result.latency_ms,
        "provider": result.provider, "model": result.model, "prompt_version": result.prompt_version,
        "input_tokens": result.input_tokens, "output_tokens": result.output_tokens,
        "source_message_id": str(extraction_input.messages[0].message_id),
    }
