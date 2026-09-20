"""Talking to the model, and reading what comes back.

One job in two halves that were two files: build the request for a stage and
send it, then pull the text out of whatever shape the provider answered in.
Splitting them meant every caller of one imported the other anyway.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from collections.abc import Awaitable, Callable, Mapping
from functools import lru_cache
from typing import TypeVar

import httpx
import tiktoken
from pydantic import BaseModel, ValidationError

from app.services.analysis.contracts import CaseAnalysisFailure
from app.services.analysis.settings import AnalysisPipelineConfig
from app.services.llm.core_llm import CoreLlmTarget, resolve_core_llm_target
from app.services.llm.structured_output import (
    structured_output_request_options,
    structured_output_schema,
)

logger = logging.getLogger("app.case_analysis")
# A block with no type, or one of these, carries the text directly.
_VISIBLE_TEXT_BLOCK_TYPES = frozenset({"text", "output_text", "message", None})


def extract_text_value(value: object) -> str:
    """Recursively extract raw text values from provider block payload."""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "".join(extract_text_value(item) for item in value)
    if not isinstance(value, Mapping):
        return ""

    block_type = value.get("type")
    if block_type in {"thinking", "redacted_thinking", "reasoning"}:
        return ""
    if block_type in _VISIBLE_TEXT_BLOCK_TYPES:
        text = value.get("text")
        if isinstance(text, str):
            return text

    nested_content = value.get("content")
    nested = extract_text_value(nested_content)
    if nested:
        return nested

    message = value.get("message")
    return extract_text_value(message)


def extract_visible_text(payload: Mapping[str, object]) -> str:
    """Extract visible assistant text across supported provider response shapes."""
    direct_output = payload.get("output_text")
    if isinstance(direct_output, str):
        return direct_output

    content = payload.get("content")
    answer = extract_text_value(content)
    if answer:
        return answer

    choices = payload.get("choices")
    if isinstance(choices, list):
        return extract_text_value(choices)

    output = payload.get("output")
    return extract_text_value(output)


def log_response_shape(status_code: int, payload: Mapping[str, object]) -> None:
    """Log provider shape metadata without logging prompts or answer text."""
    content = payload.get("content")
    block_types = []
    if isinstance(content, list):
        block_types = [
            str(block.get("type"))
            for block in content
            if isinstance(block, Mapping) and block.get("type") is not None
        ]
    usage = payload.get("usage")
    usage_keys = sorted(usage.keys()) if isinstance(usage, Mapping) else []
    logger.info(
        "Main Case Analysis provider response status=%s keys=%s "
        "content_type=%s block_types=%s stop_reason=%s usage_keys=%s",
        status_code,
        sorted(str(key) for key in payload),
        type(content).__name__,
        block_types,
        payload.get("stop_reason"),
        usage_keys,
    )


def validate_response_payload(response: httpx.Response) -> dict[str, object]:
    """Validate HTTP response payload from analysis provider."""
    if response.status_code in {408, 429, 504}:
        raise CaseAnalysisFailure(
            "analysis_provider_timeout",
            "The post-answer analysis provider timed out",
        )
    if response.status_code >= 500:
        raise CaseAnalysisFailure(
            "analysis_provider_down",
            "The post-answer analysis provider is unavailable",
        )
    if response.status_code in {401, 403}:
        raise CaseAnalysisFailure(
            "analysis_provider_unauthorized",
            "The post-answer analysis provider credentials are invalid",
        )
    if response.status_code != 200:
        raise CaseAnalysisFailure(
            "analysis_provider_error",
            "The post-answer analysis provider returned an error",
        )

    try:
        response_payload = response.json()
    except (TypeError, ValueError) as error:
        raise CaseAnalysisFailure(
            "analysis_invalid_response",
            "The post-answer analysis provider response was invalid",
        ) from error

    if not isinstance(response_payload, dict):
        raise CaseAnalysisFailure(
            "analysis_invalid_response",
            "The post-answer analysis provider response was invalid",
        )

    log_response_shape(response.status_code, response_payload)

    if isinstance(response_payload.get("error"), dict):
        raise CaseAnalysisFailure(
            "analysis_provider_error",
            "The post-answer analysis provider returned an error",
        )

    if response_payload.get("stop_reason") in {
        "refusal",
        "max_tokens",
        "length",
        "pause_turn",
    }:
        raise CaseAnalysisFailure(
            "analysis_incomplete",
            "The post-answer analysis provider did not complete",
        )

    content = response_payload.get("content")
    if content is not None and not isinstance(content, (list, str)):
        raise CaseAnalysisFailure(
            "analysis_invalid_response",
            "The post-answer analysis provider response was invalid",
        )

    return response_payload


ProviderResult = TypeVar("ProviderResult", bound=BaseModel)


@lru_cache(maxsize=1)
def encoding():
    return tiktoken.get_encoding("o200k_base")


def token_count(value: object) -> int:
    serialized = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return len(encoding().encode(serialized, disallowed_special=()))


def input_budget(config: AnalysisPipelineConfig) -> int:
    return min(
        config.input_tokens,
        config.context_tokens - config.output_tokens - config.safety_tokens,
    )


def resolve_target(config: AnalysisPipelineConfig) -> CoreLlmTarget:
    return resolve_core_llm_target(config.model)


def stage_payload(
    config: AnalysisPipelineConfig,
    system: str,
    content: dict[str, object],
    schema: type[BaseModel],
) -> dict[str, object]:
    return {
        "model": config.model,
        **structured_output_request_options(
            feature="case_analysis",
            configured_max_tokens=config.output_tokens,
        ),
        "system": system,
        "messages": [{"role": "user", "content": json.dumps(content, ensure_ascii=False)}],
        "output_config": {
            "format": {
                "type": "json_schema",
                "schema": structured_output_schema(schema),
            }
        },
    }


async def request_stage(
    *,
    client: httpx.AsyncClient,
    target: CoreLlmTarget,
    config: AnalysisPipelineConfig,
    stage: str,
    system: str,
    content: dict[str, object],
    schema: type[ProviderResult],
    calls: list[dict[str, object]],
    checkpoint: Callable[[], Awaitable[None]] | None = None,
) -> ProviderResult:
    payload = stage_payload(config, system, content, schema)
    estimated = await asyncio.to_thread(token_count, payload)
    if estimated > input_budget(config):
        raise CaseAnalysisFailure(f"{stage}_budget_exceeded", "Stage input exceeds budget")
    receipt: dict[str, object] = {
        "stage": stage,
        "model": config.model,
        "estimated_input_tokens": estimated,
        "status": "started",
    }
    calls.append(receipt)
    if checkpoint is not None:
        await checkpoint()
    started = time.monotonic()
    try:
        response = await client.post(
            target.messages_url,
            headers=target.headers,
            json=payload,
            timeout=config.timeout_seconds,
        )
        decoded = validate_response_payload(response)
        result = schema.model_validate_json(extract_visible_text(decoded))
        receipt["status"] = "completed"
        return result
    except httpx.TimeoutException as error:
        raise CaseAnalysisFailure(f"{stage}_timeout", "Analysis stage timed out") from error
    except httpx.RequestError as error:
        raise CaseAnalysisFailure(
            f"{stage}_transport", "Analysis stage transport failed"
        ) from error
    except ValidationError as error:
        # Which fields, not what was in them: the values are case material.
        logger.warning(
            "Analysis stage %s rejected the provider payload: %s",
            stage,
            "; ".join(
                f"{'.'.join(str(part) for part in item['loc']) or '(root)'}: {item['msg']}"
                for item in error.errors()[:10]
            ),
        )
        raise CaseAnalysisFailure(
            f"{stage}_invalid", "Analysis stage violated its schema"
        ) from error
    finally:
        receipt["elapsed_ms"] = round((time.monotonic() - started) * 1000)
        if receipt["status"] == "started":
            receipt["status"] = "failed"
        if checkpoint is not None:
            await checkpoint()


__all__ = [
    "extract_text_value",
    "extract_visible_text",
    "input_budget",
    "log_response_shape",
    "request_stage",
    "resolve_target",
    "stage_payload",
    "token_count",
    "validate_response_payload",
]
