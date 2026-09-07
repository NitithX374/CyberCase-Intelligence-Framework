from __future__ import annotations

import json
from collections.abc import Mapping


_VISIBLE_TEXT_BLOCK_TYPES = frozenset(
    {"text", "output_text", "message", "thought_text"}
)


def _extract_llm_text(payload: Mapping[str, object] | object) -> str:
    """Extract raw text across supported provider response shapes (Anthropic, OpenRouter, etc.)."""
    if not isinstance(payload, Mapping):
        return ""

    direct_output = payload.get("output_text")
    if isinstance(direct_output, str) and direct_output.strip():
        return direct_output

    content = payload.get("content")
    if content is not None:
        extracted = _extract_text_value(content)
        if extracted.strip():
            return extracted

    choices = payload.get("choices")
    if isinstance(choices, list):
        extracted = _extract_text_value(choices)
        if extracted.strip():
            return extracted

    output = payload.get("output")
    if output is not None:
        extracted = _extract_text_value(output)
        if extracted.strip():
            return extracted

    return ""


def _extract_text_value(value: object) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "".join(_extract_text_value(item) for item in value)
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
    if nested_content is not None:
        nested = _extract_text_value(nested_content)
        if nested:
            return nested

    message = value.get("message")
    if message is not None:
        return _extract_text_value(message)

    return ""


def _extract_llm_json(raw: str) -> dict[str, object]:
    cleaned = raw.strip()
    if not cleaned:
        raise ValueError("LLM response text is empty")
    candidates = [cleaned]
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start != -1 and end > start and cleaned[start : end + 1] != cleaned:
        candidates.append(cleaned[start : end + 1])
    errors: list[ValueError] = []
    for candidate in candidates:
        try:
            data = json.loads(candidate)
        except ValueError as error:
            errors.append(error)
            continue
        if not isinstance(data, dict):
            raise ValueError("LLM structured response must be an object")
        return data
    raise ValueError("Could not parse valid JSON object from LLM response") from errors[
        -1
    ]
