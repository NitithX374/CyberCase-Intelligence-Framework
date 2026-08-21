from __future__ import annotations

import json
import re
import time
from collections.abc import Mapping
from uuid import UUID

from app.config import settings
from app.services.extraction.extraction_contracts import (
    BaselineExtraction, ExtractionModelResponse,
)

def normalize_model_response(
    response: ExtractionModelResponse | str | Mapping[str, object],
) -> tuple[str, int | None, int | None]:
    if isinstance(response, ExtractionModelResponse):
        return response.text, response.input_tokens, response.output_tokens
    if isinstance(response, str):
        return response, None, None
    if isinstance(response, Mapping):
        return json.dumps(dict(response), ensure_ascii=False), None, None
    raise TypeError("unsupported extraction model response")


def safe_retained_response(value: str | None) -> str | None:
    if value is None:
        return None
    if contains_secret_or_prompt_text(value):
        return None
    return value[: max(1, settings.chat_extraction_max_raw_response_chars)]


def contains_secret_or_prompt_text(value: str) -> bool:
    for pattern in (
        r"(?i)\b(?:sk-ant|sk-proj|sk)-[A-Za-z0-9_-]{20,}\b",
        r"(?i)\b(?:api[_-]?key|x-api-key|authorization|bearer)\s*[:=]\s*[^\s,]+",
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    ):
        if re.search(pattern, value):
            return True
    normalized = " ".join(value.casefold().split())
    return any(
        marker in normalized
        for marker in (
            "prompt version: baseline_extraction_prompt_v1",
            "prompt version: baseline_extraction_prompt_v2",
            "prompt version: baseline_extraction_prompt_v3",
            "prompt version: baseline_extraction_prompt_v4",
            "prompt version: baseline_extraction_prompt_v5",
            "extract only facts explicitly reported",
            "return structured json only",
            "you are the cybercase baseline incident-fact extractor",
        )
    )


def textual_values(extraction: BaselineExtraction) -> list[str]:
    values: list[str] = [*extraction.warnings]
    for fact in extraction.facts:
        values.extend([fact.fact_id, fact.statement, fact.category, fact.status])
    for entity in extraction.entities:
        values.extend([entity.entity_id, entity.name, entity.entity_type])
        if entity.reported_role is not None:
            values.append(entity.reported_role)
    for relationship in extraction.relationships:
        values.extend(
            [
                relationship.relationship_id,
                relationship.subject_entity_id,
                relationship.predicate,
                relationship.object_entity_id,
                relationship.statement,
            ]
        )
    for evidence in extraction.evidence:
        values.extend(
            [
                evidence.evidence_id,
                evidence.title,
                evidence.description,
                evidence.artifact_type,
            ]
        )
    for event in extraction.timeline:
        values.extend([event.event_id, event.event])
        if event.timestamp_text is not None:
            values.append(event.timestamp_text)
        values.extend(event.actors)
        values.extend(event.evidence_ids)
    for impact in extraction.impacts:
        values.extend(
            [
                impact.impact_id,
                impact.description,
                impact.impact_type,
                impact.status,
            ]
        )
        values.extend(impact.affected_entity_ids)
    for missing in extraction.missing_information:
        values.extend([missing.missing_id, missing.description, missing.importance])
    return values


def item_id(item: object) -> str:
    for field_name in (
        "fact_id",
        "entity_id",
        "relationship_id",
        "evidence_id",
        "event_id",
        "impact_id",
        "missing_id",
    ):
        value = getattr(item, field_name, None)
        if isinstance(value, str):
            return value
    return ""


def optional_int(value: object) -> int | None:
    if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
        return value
    return None


def latency_ms(started: float) -> float:
    return round((time.perf_counter() - started) * 1000, 3)


def message_id(message: object) -> UUID:
    value = getattr(message, "id", None)
    if isinstance(value, UUID):
        return value
    return UUID(str(value))


def message_ordinal(message: object) -> int | None:
    value = getattr(message, "ordinal", None)
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    return None


def message_role(message: object) -> str | None:
    value = getattr(message, "role", None)
    return value if isinstance(value, str) else None


def message_content(message: object) -> str:
    value = getattr(message, "content", None)
    if not isinstance(value, str) or not value.strip():
        raise ValueError("source message content must be nonempty text")
    return value


def is_terminal_assistant_message(message: object) -> bool:
    if message_role(message) != "assistant":
        return False
    retrieval_context_id = getattr(message, "retrieval_context_id", None)
    if retrieval_context_id is not None:
        return True
    metadata = getattr(message, "metadata_json", None)
    return isinstance(metadata, dict) and "mitre_table" in metadata
