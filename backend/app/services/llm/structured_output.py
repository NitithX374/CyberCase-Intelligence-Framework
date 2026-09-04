"""Provider-facing JSON Schema and request helpers for structured model output."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal

from pydantic import BaseModel

from app.services.llm.core_llm import CoreLlmProvider

StructuredOutputFeature = Literal[
    "case_analysis",
    "gap_analysis",
    "followup",
    "mitre_applicability",
]

_STRUCTURED_OUTPUT_FEATURES = frozenset(
    {"case_analysis", "gap_analysis", "followup", "mitre_applicability"}
)
_OPENROUTER_OUTPUT_TOKEN_FLOORS: dict[StructuredOutputFeature, int] = {
    "case_analysis": 16_384,
    "gap_analysis": 4_096,
    "followup": 2_048,
    "mitre_applicability": 1_024,
}

_ANTHROPIC_UNSUPPORTED_SCHEMA_KEYS = frozenset(
    {
        "exclusiveMaximum",
        "exclusiveMinimum",
        "maxItems",
        "maxLength",
        "maxProperties",
        "maximum",
        "minItems",
        "minLength",
        "minProperties",
        "minimum",
        "multipleOf",
        "pattern",
        "uniqueItems",
        "default",
    }
)
_ANTHROPIC_SUPPORTED_STRING_FORMATS = frozenset(
    {
        "date-time",
        "time",
        "date",
        "duration",
        "email",
        "hostname",
        "uri",
        "ipv4",
        "ipv6",
        "uuid",
    }
)


def anthropic_json_schema(model: type[BaseModel]) -> dict[str, Any]:
    """Build an Anthropic-compatible schema without weakening local validation.

    Pydantic's full schema remains the source of truth for response validation.
    This copy only removes JSON Schema constraints unsupported by Anthropic's
    structured-output grammar and closes object schemas recursively.
    """

    normalized = _normalize_schema(model.model_json_schema())
    if not isinstance(normalized, dict):
        raise TypeError("Pydantic model schema must be a JSON object")
    return normalized


def structured_output_schema(
    model: type[BaseModel],
    *,
    provider: CoreLlmProvider,
) -> dict[str, Any]:
    """Build the provider-specific structured-output schema for ``model``."""

    if provider == "anthropic":
        return anthropic_json_schema(model)
    if provider == "openrouter":
        schema = anthropic_json_schema(model)
        _require_all_object_properties(schema)
        return schema
    raise ValueError(f"Unsupported core LLM provider: {provider!r}")


def structured_output_request_options(
    *,
    provider: CoreLlmProvider,
    feature: StructuredOutputFeature,
    configured_max_tokens: int,
    temperature: float | None = None,
) -> dict[str, object]:
    """Return only the provider-specific structured-output request options."""

    if feature not in _STRUCTURED_OUTPUT_FEATURES:
        raise ValueError(f"Unsupported structured-output feature: {feature!r}")

    if provider == "anthropic":
        options: dict[str, object] = {"max_tokens": configured_max_tokens}
        if temperature is not None:
            options["temperature"] = temperature
        return options

    if provider == "openrouter":
        options = {
            "max_tokens": max(
                configured_max_tokens,
                _OPENROUTER_OUTPUT_TOKEN_FLOORS[feature],
            )
        }
        if temperature is not None:
            options["temperature"] = temperature
        return options

    raise ValueError(f"Unsupported core LLM provider: {provider!r}")


def _normalize_schema(value: object) -> object:
    if isinstance(value, list):
        return [_normalize_schema(item) for item in value]
    if not isinstance(value, Mapping):
        return value

    normalized: dict[str, Any] = {}
    for key, child in value.items():
        key_text = str(key)
        if key_text in _ANTHROPIC_UNSUPPORTED_SCHEMA_KEYS:
            continue
        if key_text == "format" and child not in _ANTHROPIC_SUPPORTED_STRING_FORMATS:
            continue
        normalized[key_text] = _normalize_schema(child)

    # Keep an explicitly open mapping (for example a bounded delta value)
    # open. Pydantic emits ``additionalProperties: true`` for dict fields;
    # closing that mapping would make a valid structured mutation impossible.
    if (
        normalized.get("type") == "object"
        and "additionalProperties" not in normalized
    ):
        normalized["additionalProperties"] = False
    return normalized


def _require_all_object_properties(value: object) -> None:
    if isinstance(value, list):
        for item in value:
            _require_all_object_properties(item)
        return
    if not isinstance(value, dict):
        return

    for child in value.values():
        _require_all_object_properties(child)

    if value.get("type") != "object":
        return
    properties = value.get("properties", {})
    if not isinstance(properties, Mapping):
        raise TypeError("JSON Schema object properties must be a mapping")
    value["required"] = list(properties.keys())


__all__ = [
    "StructuredOutputFeature",
    "anthropic_json_schema",
    "structured_output_request_options",
    "structured_output_schema",
]
