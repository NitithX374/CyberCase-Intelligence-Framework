from __future__ import annotations

import logging
import re
from collections.abc import Mapping
from copy import deepcopy

import httpx

from app.services.case_analysis.contracts import CaseAnalysisFailure

logger = logging.getLogger("app.case_analysis")
_VISIBLE_TEXT_BLOCK_TYPES = frozenset({"text", "output_text"})


def formatIdentifier(value: object, prefix: str, aliases: str) -> object:
    """Format claim or association identifier into normalized prefix-number string."""
    if not isinstance(value, str):
        return value
    match = re.fullmatch(rf"(?:{aliases})[-_]?([0-9]+)", value.strip(), re.I)
    return f"{prefix}-{int(match[1]):02d}" if match else value


def normalizeAnalysisIdentifiers(payload: dict[str, object]) -> dict[str, object]:
    """Normalize claim IDs and association IDs across parsed analysis payload."""
    normalized = deepcopy(payload)
    for collection, field, prefix, aliases in (
        ("claims", "claim_id", "A", "A|claim|c"),
        ("mitre_associations", "association_id", "MA", "MA|assoc|association"),
    ):
        rows = normalized.get(collection)
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            if field in row:
                row[field] = formatIdentifier(row[field], prefix, aliases)
            references = row.get("claim_ids")
            if isinstance(references, list):
                row["claim_ids"] = [
                    formatIdentifier(value, "A", "A|claim|c") for value in references
                ]
    return normalized


def extractTextValue(value: object) -> str:
    """Recursively extract raw text values from provider block payload."""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "".join(extractTextValue(item) for item in value)
    if not isinstance(value, Mapping):
        return ""

    block_type = value.get("type")
    if block_type in {"thinking", "redacted_thinking", "reasoning"}:
        return ""
    if block_type in _VISIBLE_TEXT_BLOCK_TYPES:
        text = value.get("text")
        if isinstance(text, str):
            return text

    text = value.get("text")
    if isinstance(text, str) and block_type in {None, "message", "output_text"}:
        return text

    nested_content = value.get("content")
    nested = extractTextValue(nested_content)
    if nested:
        return nested

    message = value.get("message")
    return extractTextValue(message)


def extractVisibleText(payload: Mapping[str, object]) -> str:
    """Extract visible assistant text across supported provider response shapes."""
    direct_output = payload.get("output_text")
    if isinstance(direct_output, str):
        return direct_output

    content = payload.get("content")
    answer = extractTextValue(content)
    if answer:
        return answer

    choices = payload.get("choices")
    if isinstance(choices, list):
        return extractTextValue(choices)

    output = payload.get("output")
    return extractTextValue(output)


def logResponseShape(status_code: int, payload: Mapping[str, object]) -> None:
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
        sorted(str(key) for key in payload.keys()),
        type(content).__name__,
        block_types,
        payload.get("stop_reason"),
        usage_keys,
    )


def stripTrailingOcrBoilerplate(text: str) -> str:
    """Strip default trailing OCR metadata disclaimers emitted by provider."""
    if not text:
        return text
    lines = text.rstrip().split("\n")
    while lines:
        last_line = lines[-1].strip()
        if not last_line:
            lines.pop()
            continue
        cleaned = last_line.lstrip("*-# \t").rstrip(".*- \t")
        if any(
            marker in cleaned.lower()
            for marker in (
                "ocr confidence",
                "ocr quality",
                "extraction metadata",
                "document recognition quality",
                "low confidence",
                "unverified extraction",
            )
        ):
            lines.pop()
            continue
        break
    return "\n".join(lines).rstrip()


def validateResponsePayload(response: httpx.Response) -> dict[str, object]:
    """Validate HTTP response payload from analysis provider."""
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
    if response.status_code in {408, 429, 504}:
        raise CaseAnalysisFailure(
            "analysis_provider_timeout",
            "The post-answer analysis provider timed out",
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

    logResponseShape(response.status_code, response_payload)

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
    "extractTextValue",
    "extractVisibleText",
    "formatIdentifier",
    "logResponseShape",
    "normalizeAnalysisIdentifiers",
    "stripTrailingOcrBoilerplate",
    "validateResponsePayload",
]
