from __future__ import annotations;

import logging
from collections.abc import Mapping

from app.services.case_analysis.case_analysis_prompt_config import _VISIBLE_TEXT_BLOCK_TYPES

logger = logging.getLogger("app.case_analysis")

def _extract_visible_text(payload: Mapping[str, object]) -> str:
    """Extract visible assistant text across supported provider response shapes.

    OpenRouter's Anthropic-compatible endpoint normally returns ``content``
    blocks, but routed models can expose an OpenAI-style ``choices`` envelope or
    use ``output_text`` block names.  Reasoning-only blocks are intentionally
    ignored; they are not a user-facing case analysis.
    """

    direct_output = payload.get("output_text")
    if isinstance(direct_output, str):
        return direct_output

    content = payload.get("content")
    answer = _extract_text_value(content)
    if answer:
        return answer

    choices = payload.get("choices")
    if isinstance(choices, list):
        return _extract_text_value(choices)

    output = payload.get("output")
    return _extract_text_value(output)


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
    nested = _extract_text_value(nested_content)
    if nested:
        return nested

    message = value.get("message")
    return _extract_text_value(message)


def _log_response_shape(status_code: int, payload: Mapping[str, object]) -> None:
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
