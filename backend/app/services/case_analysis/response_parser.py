from __future__ import annotations

import logging
from collections.abc import Mapping

import httpx

from app.services.case_analysis.contracts import CaseAnalysisFailure

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


__all__ = [
    "extract_text_value",
    "extract_visible_text",
    "log_response_shape",
    "validate_response_payload",
]
