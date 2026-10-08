from __future__ import annotations

import json
from copy import copy
from functools import lru_cache, reduce
from operator import or_
from types import UnionType
from typing import Annotated, Any, Literal, TypeVar, Union, get_args, get_origin

from pydantic import BaseModel, ConfigDict, create_model
from pydantic_core import PydanticUndefined

ProviderResult = TypeVar("ProviderResult", bound=BaseModel)


def wire_annotation(annotation: Any) -> Any:
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return wire_model(annotation)
    origin = get_origin(annotation)
    if origin is None or origin is Literal:
        return annotation
    arguments = get_args(annotation)
    if origin is Annotated:
        return Annotated[wire_annotation(arguments[0]), *arguments[1:]]
    converted = tuple(wire_annotation(argument) for argument in arguments)
    if origin in {Union, UnionType}:
        return reduce(or_, converted)
    if hasattr(annotation, "copy_with"):
        return annotation.copy_with(converted)
    return origin[converted]


@lru_cache(maxsize=32)
def wire_model(model: type[BaseModel]) -> type[BaseModel]:
    fields = {}
    for name, field in model.model_fields.items():
        required = copy(field)
        required.default = PydanticUndefined
        required.default_factory = None
        annotation = wire_annotation(field.annotation)
        required.annotation = annotation
        fields[name] = (annotation, required)
    return create_model(
        model.__name__, __config__=ConfigDict(extra="forbid", strict=True), **fields
    )


def normalize_schema(value: object) -> object:
    if isinstance(value, list):
        return [normalize_schema(item) for item in value]
    if not isinstance(value, dict):
        return value
    return {
        "enum" if key == "const" else key: [child] if key == "const" else normalize_schema(child)
        for key, child in value.items()
    }


def structured_output_schema(model: type[BaseModel]) -> dict[str, Any]:
    schema = normalize_schema(wire_model(model).model_json_schema())
    if not isinstance(schema, dict):
        raise TypeError("Pydantic model schema must be a JSON object")
    return schema


def structured_system_prompt(system: str, model: type[BaseModel]) -> str:
    contract = json.dumps(
        structured_output_schema(model), ensure_ascii=False, separators=(",", ":")
    )
    return (
        f"{system}\n\n"
        "Return exactly one JSON object matching the response contract below. "
        "Include every required field, including nested fields. Use only the allowed enum values "
        "and JSON types; do not add fields. Use null only where allowed, and empty arrays only "
        "when no grounded items are available and the contract permits them. "
        "Do not invent facts to fill the contract. Do not include Markdown fences or prose "
        "outside the JSON object.\n"
        f"<response_contract>\n{contract}\n</response_contract>"
    )


def validate_structured_json(model: type[ProviderResult], text: str) -> ProviderResult:
    wire_model(model).model_validate_json(text)
    return model.model_validate_json(text)


__all__ = ["structured_output_schema", "structured_system_prompt", "validate_structured_json"]
