from __future__ import annotations

import json

from app.config import settings
from app.services.extraction.extraction_contracts import (
    CaseState, ExtractionInput, ExtractionValidationError,
)
from app.services.extraction.extraction_normalizer import normalize_case_state
from app.services.extraction.extraction_utils import (
    contains_secret_or_prompt_text, item_id, message_id, textual_values,
)

def validate_baseline_extraction(
    value: object,
    extraction_input: ExtractionInput | None = None,
) -> CaseState:
    """Validate structure, provenance references, limits, and safe text."""

    extraction = normalize_case_state(value)

    limits = (
        ("facts", extraction.facts, settings.chat_extraction_max_facts),
        ("entities", extraction.entities, settings.chat_extraction_max_entities),
        (
            "relationships",
            extraction.relationships,
            settings.chat_extraction_max_relationships,
        ),
        ("evidence", extraction.evidence, settings.chat_extraction_max_evidence),
        ("timeline", extraction.timeline, settings.chat_extraction_max_timeline),
        ("impacts", extraction.impacts, settings.chat_extraction_max_impacts),
        (
            "missing_information",
            extraction.missing_information,
            settings.chat_extraction_max_missing_information,
        ),
    )
    for name, items, limit in limits:
        if len(items) > max(0, limit):
            raise ExtractionValidationError(
                f"{name} exceeds the configured item limit"
            )

    source_ids = (
        {str(message.message_id) for message in extraction_input.messages}
        if extraction_input is not None
        else None
    )

    collections = (
        ("facts", extraction.facts),
        ("entities", extraction.entities),
        ("relationships", extraction.relationships),
        ("evidence", extraction.evidence),
        ("timeline", extraction.timeline),
        ("impacts", extraction.impacts),
        ("missing_information", extraction.missing_information),
    )
    for collection_name, items in collections:
        collection_ids: list[str] = []
        for item in items:
            current_item_id = item_id(item)
            if not current_item_id.strip():
                raise ExtractionValidationError(f"{collection_name} item IDs cannot be empty")
            collection_ids.append(current_item_id)
            refs = {str(message_id) for message_id in item.source_message_ids}
            if not refs or (source_ids is not None and not refs <= source_ids):
                raise ExtractionValidationError(
                    f"{current_item_id} contains an invalid source message reference"
                )
            if len(refs) != len(item.source_message_ids):
                raise ExtractionValidationError(
                    f"{current_item_id} contains duplicate source message references"
                )
        if len(set(collection_ids)) != len(collection_ids):
            raise ExtractionValidationError(
                f"{collection_name} item IDs must be unique within the collection"
            )

    entity_ids = {item.entity_id for item in extraction.entities}
    semantic_edges: set[tuple[str, str, str]] = set()
    for relationship in extraction.relationships:
        if relationship.subject_entity_id not in entity_ids:
            raise ExtractionValidationError(
                f"{relationship.relationship_id} contains an invalid subject entity reference"
            )
        if relationship.object_entity_id not in entity_ids:
            raise ExtractionValidationError(
                f"{relationship.relationship_id} contains an invalid object entity reference"
            )
        if relationship.subject_entity_id == relationship.object_entity_id:
            raise ExtractionValidationError(
                f"{relationship.relationship_id} cannot connect an entity to itself"
            )
        semantic_edge = (
            relationship.subject_entity_id,
            relationship.predicate,
            relationship.object_entity_id,
        )
        if semantic_edge in semantic_edges:
            raise ExtractionValidationError(
                f"{relationship.relationship_id} duplicates an existing semantic edge"
            )
        semantic_edges.add(semantic_edge)

    evidence_ids = {item.evidence_id for item in extraction.evidence}
    for event in extraction.timeline:
        if not set(event.evidence_ids) <= evidence_ids:
            raise ExtractionValidationError(
                f"{event.event_id} contains an invalid evidence reference"
            )

    for impact in extraction.impacts:
        if not set(impact.affected_entity_ids) <= entity_ids:
            raise ExtractionValidationError(
                f"{impact.impact_id} contains an invalid affected entity reference"
            )

    extracted_text_values = textual_values(extraction)
    max_text_chars = max(1, settings.chat_extraction_max_text_chars)
    if any(len(value) > max_text_chars for value in extracted_text_values):
        raise ExtractionValidationError(
            "extraction text exceeds the configured character limit"
        )
    if any(not value.strip() for value in extracted_text_values):
        raise ExtractionValidationError("extraction text cannot be empty")

    serialized = json.dumps(extraction.model_dump(mode="json"), ensure_ascii=False)
    if contains_secret_or_prompt_text(serialized):
        raise ExtractionValidationError(
            "extraction output contains a secret or system-prompt text"
        )
    return extraction
