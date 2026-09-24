from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal

from pydantic import BaseModel

StructuredOutputFeature = Literal[
    "case_analysis",
    "mitre_applicability",
]

_STRUCTURED_OUTPUT_FEATURES = frozenset({"case_analysis", "mitre_applicability"})
_OUTPUT_TOKEN_FLOORS: dict[StructuredOutputFeature, int] = {
    "case_analysis": 16_384,
    "mitre_applicability": 1_024,
}

_UNSUPPORTED_SCHEMA_KEYS = frozenset(
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
_SUPPORTED_STRING_FORMATS = frozenset(
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


def structured_output_schema(model: type[BaseModel]) -> dict[str, Any]:
    schema = normalize_schema(model.model_json_schema())
    if not isinstance(schema, dict):
        raise TypeError("Pydantic model schema must be a JSON object")
    require_all_object_properties(schema)
    return schema


def structured_output_request_options(
    *,
    feature: StructuredOutputFeature,
    configured_max_tokens: int,
    temperature: float | None = None,
) -> dict[str, object]:
    if feature not in _STRUCTURED_OUTPUT_FEATURES:
        raise ValueError(f"Unsupported structured-output feature: {feature!r}")
    options: dict[str, object] = {
        "max_tokens": max(configured_max_tokens, _OUTPUT_TOKEN_FLOORS[feature])
    }
    if temperature is not None:
        options["temperature"] = temperature
    return options


def normalize_schema(value: object) -> object:
    if isinstance(value, list):
        return [normalize_schema(item) for item in value]
    if not isinstance(value, Mapping):
        return value

    normalized: dict[str, Any] = {}
    for key, child in value.items():
        key_text = str(key)
        if key_text in _UNSUPPORTED_SCHEMA_KEYS:
            continue
        if key_text == "format" and child not in _SUPPORTED_STRING_FORMATS:
            continue
        normalized[key_text] = normalize_schema(child)

    if normalized.get("type") == "object" and "additionalProperties" not in normalized:
        normalized["additionalProperties"] = False
    return normalized


def require_all_object_properties(value: object) -> None:
    if isinstance(value, list):
        for item in value:
            require_all_object_properties(item)
        return
    if not isinstance(value, dict):
        return

    for child in value.values():
        require_all_object_properties(child)

    if value.get("type") != "object":
        return
    properties = value.get("properties", {})
    if not isinstance(properties, Mapping):
        raise TypeError("JSON Schema object properties must be a mapping")
    value["required"] = list(properties.keys())


__all__ = [
    "StructuredOutputFeature",
    "structured_output_request_options",
    "structured_output_schema",
]
