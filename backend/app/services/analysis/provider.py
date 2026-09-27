from __future__ import annotations

import asyncio
import json
import logging
import time
from collections.abc import Mapping
from functools import lru_cache
from typing import TypeVar

import httpx
import tiktoken
from fastapi import status
from pydantic import BaseModel, ValidationError

from app.services.analysis.contracts import CaseAnalysisFailure
from app.services.analysis.settings import AnalysisPipelineConfig
from app.services.llm.core_llm import CoreLlmTarget, resolve_core_llm_target
from app.services.llm.structured_output import structured_output_schema

logger = logging.getLogger("app.case_analysis")
_VISIBLE_TEXT_BLOCK_TYPES = frozenset({"text", "output_text", "message", None})
TRANSIENT_TRANSPORT_ERRORS = (
    httpx.ConnectError,
    httpx.ReadError,
    httpx.WriteError,
    httpx.RemoteProtocolError,
)
TRANSPORT_ATTEMPTS = 2
TRANSPORT_RETRY_DELAY_SECONDS = 2.0
transport: httpx.AsyncBaseTransport | None = None


def extract_text_value(value: object) -> str:
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


def token_or_none(value: object) -> int | None:
    return value if isinstance(value, int) else None


def usage_summary(payload: Mapping[str, object]) -> dict[str, int | None]:
    usage = payload.get("usage")
    if not isinstance(usage, Mapping):
        usage = {}
    details = usage.get("output_tokens_details")
    if not isinstance(details, Mapping):
        details = {}
    return {
        "input_tokens": token_or_none(usage.get("input_tokens")),
        "output_tokens": token_or_none(usage.get("output_tokens")),
        "thinking_tokens": token_or_none(details.get("thinking_tokens")),
    }


def log_response_shape(stage: str, payload: Mapping[str, object]) -> None:
    content = payload.get("content")
    block_types = []
    if isinstance(content, list):
        block_types = [
            str(block.get("type"))
            for block in content
            if isinstance(block, Mapping) and block.get("type") is not None
        ]
    logger.info(
        "Analysis stage %s provider response keys=%s "
        "content_type=%s block_types=%s stop_reason=%s usage=%s",
        stage,
        sorted(str(key) for key in payload),
        type(content).__name__,
        block_types,
        payload.get("stop_reason"),
        usage_summary(payload),
    )


def decode_response(response: httpx.Response) -> dict[str, object]:
    if response.status_code in {408, 429, 504}:
        raise CaseAnalysisFailure(
            "analysis_provider_timeout",
            "The analysis provider timed out",
            status.HTTP_504_GATEWAY_TIMEOUT,
        )
    if response.status_code >= 500:
        raise CaseAnalysisFailure(
            "analysis_provider_down",
            "The analysis provider is unavailable",
            status.HTTP_502_BAD_GATEWAY,
        )
    if response.status_code in {401, 403}:
        raise CaseAnalysisFailure(
            "analysis_provider_unauthorized",
            "The analysis provider credentials are invalid",
        )
    if response.status_code != 200:
        raise CaseAnalysisFailure(
            "analysis_provider_error",
            "The analysis provider returned an error",
        )

    try:
        response_payload = response.json()
    except (TypeError, ValueError) as error:
        raise CaseAnalysisFailure(
            "analysis_invalid_response",
            "The analysis provider response was invalid",
            status.HTTP_502_BAD_GATEWAY,
        ) from error

    if not isinstance(response_payload, dict):
        raise CaseAnalysisFailure(
            "analysis_invalid_response",
            "The analysis provider response was invalid",
            status.HTTP_502_BAD_GATEWAY,
        )
    return response_payload


def check_response_payload(response_payload: Mapping[str, object], *, stage: str) -> None:
    log_response_shape(stage, response_payload)

    if isinstance(response_payload.get("error"), dict):
        raise CaseAnalysisFailure(
            "analysis_provider_error",
            "The analysis provider returned an error",
            status.HTTP_502_BAD_GATEWAY,
        )

    stop_reason = response_payload.get("stop_reason")
    if stop_reason in {"refusal", "max_tokens", "length", "pause_turn"}:
        raise CaseAnalysisFailure(
            f"{stage}_incomplete",
            "Analysis stage did not complete",
            status.HTTP_409_CONFLICT if stop_reason == "refusal" else status.HTTP_502_BAD_GATEWAY,
        )

    content = response_payload.get("content")
    if content is not None and not isinstance(content, (list, str)):
        raise CaseAnalysisFailure(
            "analysis_invalid_response",
            "The analysis provider response was invalid",
            status.HTTP_502_BAD_GATEWAY,
        )


def validate_response_payload(
    response: httpx.Response, *, stage: str = "analysis"
) -> dict[str, object]:
    response_payload = decode_response(response)
    check_response_payload(response_payload, stage=stage)
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
        config.context_tokens - config.max_tokens - config.safety_tokens,
    )


def thinking_option(config: AnalysisPipelineConfig) -> dict[str, object]:
    if config.thinking_tokens == 0:
        return {"type": "disabled"}
    return {"type": "enabled", "budget_tokens": config.thinking_tokens}


def stage_payload(
    config: AnalysisPipelineConfig,
    system: str,
    content: dict[str, object] | str,
    schema: type[BaseModel],
    *,
    temperature: float | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "model": config.model,
        "max_tokens": config.max_tokens,
        "thinking": thinking_option(config),
        "system": system,
        "messages": [
            {
                "role": "user",
                "content": content
                if isinstance(content, str)
                else json.dumps(content, ensure_ascii=False),
            }
        ],
        "output_config": {
            "format": {
                "type": "json_schema",
                "schema": structured_output_schema(schema),
            }
        },
    }
    if temperature is not None:
        payload["temperature"] = temperature
    if config.providers:
        payload["provider"] = {"order": list(config.providers), "allow_fallbacks": False}
    return payload


async def post_stage(
    target: CoreLlmTarget,
    payload: dict[str, object],
    *,
    stage: str,
    timeout: float,
) -> httpx.Response:
    async with httpx.AsyncClient(transport=transport) as client:
        attempt = 1
        while True:
            try:
                return await client.post(
                    target.messages_url,
                    headers=target.headers,
                    json=payload,
                    timeout=timeout,
                )
            except TRANSIENT_TRANSPORT_ERRORS as error:
                if attempt >= TRANSPORT_ATTEMPTS:
                    raise
                logger.warning(
                    "Analysis stage %s transport error on attempt %d, retrying: %r",
                    stage,
                    attempt,
                    error,
                )
                attempt += 1
                await asyncio.sleep(TRANSPORT_RETRY_DELAY_SECONDS)


async def request_stage(
    *,
    config: AnalysisPipelineConfig,
    stage: str,
    system: str,
    content: dict[str, object] | str,
    schema: type[ProviderResult],
    calls: list[dict[str, object]] | None = None,
    temperature: float | None = None,
) -> ProviderResult:
    target = resolve_core_llm_target(config.model)
    payload = stage_payload(config, system, content, schema, temperature=temperature)
    estimated = await asyncio.to_thread(token_count, payload)
    if estimated > input_budget(config):
        raise CaseAnalysisFailure(f"{stage}_budget_exceeded", "Stage input exceeds budget")
    receipt: dict[str, object] = {
        "stage": stage,
        "model": config.model,
        "estimated_input_tokens": estimated,
        "status": "started",
    }
    if calls is not None:
        calls.append(receipt)
    started = time.monotonic()
    try:
        response = await post_stage(target, payload, stage=stage, timeout=config.timeout_seconds)
        decoded = decode_response(response)
        receipt.update(usage_summary(decoded))
        check_response_payload(decoded, stage=stage)
        result = schema.model_validate_json(extract_visible_text(decoded))
        receipt["status"] = "completed"
        return result
    except httpx.TimeoutException as error:
        raise CaseAnalysisFailure(
            f"{stage}_timeout", "Analysis stage timed out", status.HTTP_504_GATEWAY_TIMEOUT
        ) from error
    except httpx.RequestError as error:
        logger.warning("Analysis stage %s transport failed: %r", stage, error)
        raise CaseAnalysisFailure(
            f"{stage}_transport", "Analysis stage transport failed", status.HTTP_502_BAD_GATEWAY
        ) from error
    except ValidationError as error:
        logger.warning(
            "Analysis stage %s rejected the provider payload: %s",
            stage,
            "; ".join(
                f"{'.'.join(str(part) for part in item['loc']) or '(root)'}: {item['msg']}"
                for item in error.errors()[:10]
            ),
        )
        raise CaseAnalysisFailure(
            f"{stage}_invalid", "Analysis stage violated its schema", status.HTTP_502_BAD_GATEWAY
        ) from error
    finally:
        receipt["elapsed_ms"] = round((time.monotonic() - started) * 1000)
        if receipt["status"] == "started":
            receipt["status"] = "failed"


__all__ = [
    "check_response_payload",
    "decode_response",
    "extract_text_value",
    "extract_visible_text",
    "input_budget",
    "log_response_shape",
    "post_stage",
    "request_stage",
    "stage_payload",
    "thinking_option",
    "token_count",
    "usage_summary",
    "validate_response_payload",
]
