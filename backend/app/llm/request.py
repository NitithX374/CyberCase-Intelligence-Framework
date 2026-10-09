from __future__ import annotations

import asyncio
import logging
import re
import time
from typing import TypeVar

import httpx
from fastapi import status
from pydantic import BaseModel, ValidationError

from app.errors import CaseAnalysisFailure
from app.llm.openrouter import CoreLlmTarget, resolve_core_llm_target
from app.llm.payload import input_budget, stage_payload, thinking_option, token_count
from app.llm.response import (
    check_response_payload,
    decode_response,
    extract_text_value,
    extract_visible_text,
    log_response_shape,
    usage_summary,
)
from app.llm.schema import validate_structured_json
from app.llm.settings import AnalysisPipelineConfig

logger = logging.getLogger("app.case_analysis")
TRANSIENT_TRANSPORT_ERRORS = (
    httpx.ConnectError,
    httpx.ReadError,
    httpx.WriteError,
    httpx.RemoteProtocolError,
)
TRANSIENT_STATUSES = frozenset({429, 500, 502, 503, 504})
TRANSPORT_ATTEMPTS = 2
TRANSPORT_RETRY_DELAY_SECONDS = 2.0
RUNAWAY_ATTEMPTS = 2
JSON_FENCE = re.compile(r"^\s*```(?:json)?\s*|\s*```\s*$")
transport: httpx.AsyncBaseTransport | None = None


ProviderResult = TypeVar("ProviderResult", bound=BaseModel)


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
                response = await client.post(
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
            else:
                if response.status_code not in TRANSIENT_STATUSES or attempt >= TRANSPORT_ATTEMPTS:
                    return response
                logger.warning(
                    "Analysis stage %s answered HTTP %d on attempt %d, retrying",
                    stage,
                    response.status_code,
                    attempt,
                )
            attempt += 1
            await asyncio.sleep(TRANSPORT_RETRY_DELAY_SECONDS)


def validation_problem(error: ValidationError) -> str:
    first = error.errors()[0]
    return f"invalid: {first['type']} at {'.'.join(str(part) for part in first['loc'])}"[:160]


async def validated_reply(
    target: CoreLlmTarget,
    payload: dict[str, object],
    *,
    config: AnalysisPipelineConfig,
    stage: str,
    schema: type[ProviderResult],
    receipt: dict[str, object],
) -> ProviderResult:
    problems: list[str] = []
    for attempt in range(1, RUNAWAY_ATTEMPTS + 1):
        receipt["generation_attempts"] = attempt
        response = await post_stage(target, payload, stage=stage, timeout=config.timeout_seconds)
        decoded = decode_response(response)
        usage = usage_summary(decoded)
        receipt.update(usage)
        if decoded.get("stop_reason") in {"max_tokens", "length"}:
            if attempt == RUNAWAY_ATTEMPTS:
                check_response_payload(decoded, stage=stage)
            logger.warning("Analysis stage %s ran to max_tokens; asking once more", stage)
            receipt["runaway_output_tokens"] = usage["output_tokens"]
            problems.append("ran_to_max_tokens")
            continue
        check_response_payload(decoded, stage=stage)
        text = JSON_FENCE.sub("", extract_visible_text(decoded).strip())
        try:
            result = validate_structured_json(schema, text)
        except ValidationError as error:
            problem = validation_problem(error)
            logger.warning("Analysis stage %s reply failed its schema, %s", stage, problem)
            receipt["invalid_output_tokens"] = usage["output_tokens"]
            problems.append(problem)
            continue
        receipt["status"] = "completed"
        return result
    logger.warning("Analysis stage %s gave no valid reply: %s", stage, "; ".join(problems))
    raise CaseAnalysisFailure(
        f"{stage}_invalid", "Analysis stage violated its schema", status.HTTP_502_BAD_GATEWAY
    )


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
        "output_mode": "in_context_json",
        "request_max_tokens": config.max_tokens,
        "status": "started",
    }
    if calls is not None:
        calls.append(receipt)
    started = time.monotonic()
    try:
        return await validated_reply(
            target, payload, config=config, stage=stage, schema=schema, receipt=receipt
        )
    except httpx.TimeoutException as error:
        raise CaseAnalysisFailure(
            f"{stage}_timeout", "Analysis stage timed out", status.HTTP_504_GATEWAY_TIMEOUT
        ) from error
    except httpx.RequestError as error:
        logger.warning("Analysis stage %s transport failed: %r", stage, error)
        raise CaseAnalysisFailure(
            f"{stage}_transport", "Analysis stage transport failed", status.HTTP_502_BAD_GATEWAY
        ) from error
    finally:
        receipt["elapsed_ms"] = round((time.monotonic() - started) * 1000)
        if receipt["status"] == "started":
            receipt["status"] = "failed"
        logger.info(
            "Analysis stage %s finished status=%s elapsed_ms=%s estimated_input_tokens=%s "
            "output_tokens=%s thinking_tokens=%s output_mode=%s request_max_tokens=%s",
            stage,
            receipt["status"],
            receipt["elapsed_ms"],
            estimated,
            receipt.get("output_tokens"),
            receipt.get("thinking_tokens"),
            receipt["output_mode"],
            receipt["request_max_tokens"],
        )


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
    "validated_reply",
]
