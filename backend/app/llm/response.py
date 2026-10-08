from __future__ import annotations

import logging
from collections.abc import Mapping

import httpx
from fastapi import status

from app.errors import CaseAnalysisFailure

logger = logging.getLogger("app.case_analysis")
_VISIBLE_TEXT_BLOCK_TYPES = frozenset({"text", "output_text", "message", None})


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
    if response.status_code == 429:
        raise CaseAnalysisFailure(
            "analysis_provider_rate_limited",
            "The analysis provider is limiting requests",
            status.HTTP_429_TOO_MANY_REQUESTS,
        )
    if response.status_code in {408, 504}:
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
