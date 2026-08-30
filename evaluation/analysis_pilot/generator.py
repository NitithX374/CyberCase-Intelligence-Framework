"""Analysis generator for RAW_DIRECT and EXTRACTED_STATE conditions."""

from __future__ import annotations

import asyncio
import json
import time
import uuid
from typing import Any
import httpx
from pydantic import ValidationError

from app.config import settings
from app.services.extraction.llm_extraction import (
    ExtractionInput,
    ExtractionSourceMessage,
    run_baseline_extraction,
)
from app.services.llm.core_llm import (
    CoreLlmConfigurationError,
    resolve_core_llm_target,
)
from app.services.llm.structured_output_router import structured_output_schema
from evaluation.analysis_pilot.config import (
    ANALYSIS_MAX_OUTPUT_TOKENS,
    ANALYSIS_TEMPERATURE,
    ANALYSIS_TIMEOUT_SECONDS,
    DEFAULT_ANALYSIS_MODEL,
)
from evaluation.analysis_pilot.prompts import (
    ANALYSIS_PROMPT_VERSION,
    ANALYSIS_SYSTEM_PROMPT,
    ANALYSIS_USER_TEMPLATE,
    get_prompt_hash,
)
from evaluation.analysis_pilot.schemas import (
    CaseAnalysisOutput,
    ExtractionLogRecord,
    GenerationRecord,
)


async def generate_analysis(
    *,
    case_info_text: str,
    condition: str,
    case: dict[str, Any],
    model: str = DEFAULT_ANALYSIS_MODEL,
    temperature: float = ANALYSIS_TEMPERATURE,
    max_output_tokens: int = ANALYSIS_MAX_OUTPUT_TOKENS,
) -> GenerationRecord:
    """Run the analysis generation LLM call with strict structured output."""
    started = time.perf_counter()
    user_content = ANALYSIS_USER_TEMPLATE.format(case_info=case_info_text)
    prompt_hash = get_prompt_hash(ANALYSIS_SYSTEM_PROMPT, user_content)

    decoding_settings = {
        "temperature": temperature,
        "max_output_tokens": max_output_tokens,
    }

    try:
        target = resolve_core_llm_target(model)
    except CoreLlmConfigurationError as exc:
        latency_ms = (time.perf_counter() - started) * 1000.0
        return GenerationRecord(
            case_id=case["case_id"],
            language=case["language"],
            scenario_id=case["scenario_id"],
            condition=condition,  # type: ignore[arg-type]
            input_used=case_info_text,
            model=model,
            prompt_version=ANALYSIS_PROMPT_VERSION,
            prompt_hash=prompt_hash,
            decoding_settings=decoding_settings,
            latency_ms=latency_ms,
            failure_information=f"Provider not configured: {exc}",
        )

    request_payload: dict[str, Any] = {
        "model": target.model,
        "max_tokens": max_output_tokens,
        "temperature": temperature,
        "system": ANALYSIS_SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": user_content}],
        "output_config": {
            "format": {
                "type": "json_schema",
                "schema": structured_output_schema(
                    CaseAnalysisOutput,
                    provider=target.provider,
                ),
            }
        },
    }

    raw_response: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None

    try:
        async with httpx.AsyncClient(timeout=ANALYSIS_TIMEOUT_SECONDS) as client:
            resp = await client.post(
                target.messages_url,
                headers=target.headers,
                json=request_payload,
            )

        if not 200 <= resp.status_code < 300:
            latency_ms = (time.perf_counter() - started) * 1000.0
            return GenerationRecord(
                case_id=case["case_id"],
                language=case["language"],
                scenario_id=case["scenario_id"],
                condition=condition,  # type: ignore[arg-type]
                input_used=case_info_text,
                model=target.model,
                prompt_version=ANALYSIS_PROMPT_VERSION,
                prompt_hash=prompt_hash,
                decoding_settings=decoding_settings,
                latency_ms=latency_ms,
                failure_information=f"HTTP {resp.status_code}: {resp.text[:500]}",
            )

        resp_payload = resp.json()
        usage = resp_payload.get("usage", {})
        if isinstance(usage, dict):
            input_tokens = usage.get("input_tokens")
            output_tokens = usage.get("output_tokens")

        content = resp_payload.get("content", [])
        if isinstance(content, list):
            raw_response = "".join(
                b.get("text", "")
                for b in content
                if isinstance(b, dict) and b.get("type") == "text"
            )
        elif isinstance(content, str):
            raw_response = content

        if not raw_response:
            latency_ms = (time.perf_counter() - started) * 1000.0
            return GenerationRecord(
                case_id=case["case_id"],
                language=case["language"],
                scenario_id=case["scenario_id"],
                condition=condition,  # type: ignore[arg-type]
                input_used=case_info_text,
                model=target.model,
                prompt_version=ANALYSIS_PROMPT_VERSION,
                prompt_hash=prompt_hash,
                decoding_settings=decoding_settings,
                raw_response=json.dumps(resp_payload),
                latency_ms=latency_ms,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                failure_information="Model returned empty text content",
            )

        parsed_json = json.loads(raw_response)
        validated_output = CaseAnalysisOutput.model_validate(parsed_json)
        latency_ms = (time.perf_counter() - started) * 1000.0

        return GenerationRecord(
            case_id=case["case_id"],
            language=case["language"],
            scenario_id=case["scenario_id"],
            condition=condition,  # type: ignore[arg-type]
            input_used=case_info_text,
            model=target.model,
            prompt_version=ANALYSIS_PROMPT_VERSION,
            prompt_hash=prompt_hash,
            decoding_settings=decoding_settings,
            output=validated_output,
            raw_response=raw_response,
            latency_ms=latency_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )

    except Exception as exc:
        latency_ms = (time.perf_counter() - started) * 1000.0
        return GenerationRecord(
            case_id=case["case_id"],
            language=case["language"],
            scenario_id=case["scenario_id"],
            condition=condition,  # type: ignore[arg-type]
            input_used=case_info_text,
            model=model,
            prompt_version=ANALYSIS_PROMPT_VERSION,
            prompt_hash=prompt_hash,
            decoding_settings=decoding_settings,
            raw_response=raw_response,
            latency_ms=latency_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            failure_information=f"Generation failed: {type(exc).__name__}: {exc}",
        )


async def run_raw_direct_condition(
    case: dict[str, Any],
    *,
    model: str = DEFAULT_ANALYSIS_MODEL,
    temperature: float = ANALYSIS_TEMPERATURE,
) -> GenerationRecord:
    """Condition A: RAW_DIRECT. Feeds only the raw narrative to the analysis LLM."""
    narrative = case["narrative"]
    return await generate_analysis(
        case_info_text=narrative,
        condition="RAW_DIRECT",
        case=case,
        model=model,
        temperature=temperature,
    )


async def run_extracted_state_condition(
    case: dict[str, Any],
    *,
    model: str = DEFAULT_ANALYSIS_MODEL,
    temperature: float = ANALYSIS_TEMPERATURE,
) -> tuple[GenerationRecord, ExtractionLogRecord]:
    """Condition B: EXTRACTED_STATE. Extracts CaseState first, then analyzes."""
    narrative = case["narrative"]
    msg_id = uuid.uuid4()
    thread_id = uuid.uuid4()
    extraction_input = ExtractionInput(
        thread_id=thread_id,
        messages=[
            ExtractionSourceMessage(
                message_id=msg_id,
                ordinal=1,
                source_type="user_case_statement",
                content=narrative,
            )
        ],
    )

    # 1. Run production extraction
    ext_result = await run_baseline_extraction(extraction_input)

    canonical_json: dict[str, Any] | None = None
    if ext_result.extraction is not None:
        canonical_json = ext_result.extraction.model_dump(mode="json")

    extraction_log = ExtractionLogRecord(
        case_id=case["case_id"],
        language=case["language"],
        scenario_id=case["scenario_id"],
        status=ext_result.status,
        raw_response=ext_result.raw_response,
        canonical_case_state=canonical_json,
        failure_code=ext_result.failure_code,
        failure_message=ext_result.failure_message,
        latency_ms=ext_result.latency_ms,
        input_tokens=ext_result.input_tokens,
        output_tokens=ext_result.output_tokens,
    )

    if ext_result.status != "candidate" or ext_result.extraction is None:
        # Record failure, do not silently substitute gold_facts
        gen_record = GenerationRecord(
            case_id=case["case_id"],
            language=case["language"],
            scenario_id=case["scenario_id"],
            condition="EXTRACTED_STATE",
            input_used="",
            model=model,
            prompt_version=ANALYSIS_PROMPT_VERSION,
            prompt_hash="",
            decoding_settings={
                "temperature": temperature,
                "max_output_tokens": ANALYSIS_MAX_OUTPUT_TOKENS,
            },
            latency_ms=0.0,
            failure_information=(
                f"Extraction failed before analysis: {ext_result.failure_code} - "
                f"{ext_result.failure_message}"
            ),
        )
        return gen_record, extraction_log

    # 2. Format Canonical Case State as case information
    case_state_str = json.dumps(canonical_json, indent=2, ensure_ascii=False)

    # 3. Run analysis on extracted state
    gen_record = await generate_analysis(
        case_info_text=case_state_str,
        condition="EXTRACTED_STATE",
        case=case,
        model=model,
        temperature=temperature,
    )

    return gen_record, extraction_log
