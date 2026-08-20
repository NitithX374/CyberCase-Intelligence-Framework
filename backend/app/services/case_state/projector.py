"""Deterministic retrieval-query projection for validated Case State."""

from __future__ import annotations

from copy import deepcopy
import json
from collections.abc import Mapping

from app.services.extraction.llm_extraction import CaseState, normalize_case_state


_RETRIEVAL_QUERY_PREFIX = (
    "<case_state_retrieval_json>\n"
)
_RETRIEVAL_QUERY_SUFFIX = "\n</case_state_retrieval_json>"


def project_case_state_to_retrieval_query(
    case_state_json: CaseState | Mapping[str, object],
) -> str:
    """Project one complete validated Case State into a retrieval-only query.

    The projection prioritizes substantive facts, technical entities, evidence artifacts,
    and impacts, avoiding duplicate semantic assertions from relationships/timeline.
    Source-message identifiers and operational metadata are excluded.
    """

    validated = (
        case_state_json
        if isinstance(case_state_json, CaseState)
        else normalize_case_state(deepcopy(dict(case_state_json)))
    )

    seen_statements: set[str] = set()

    projected_facts: list[dict[str, object]] = []
    for item in validated.facts:
        norm = " ".join(item.statement.casefold().split())
        if norm and norm not in seen_statements:
            seen_statements.add(norm)
            projected_facts.append(
                {
                    "fact_id": item.fact_id,
                    "statement": item.statement,
                    "category": item.category,
                    "status": item.status,
                    "confidence": item.confidence,
                }
            )

    projected_entities: list[dict[str, object]] = [
        {
            "entity_id": item.entity_id,
            "name": item.name,
            "entity_type": item.entity_type,
            "reported_role": item.reported_role,
            "confidence": item.confidence,
        }
        for item in validated.entities
    ]

    projected_evidence: list[dict[str, object]] = [
        {
            "evidence_id": item.evidence_id,
            "title": item.title,
            "description": item.description,
            "artifact_type": item.artifact_type,
            "status": item.status,
            "confidence": item.confidence,
            "source_type": item.source_type,
        }
        for item in validated.evidence
    ]

    projected_impacts: list[dict[str, object]] = [
        {
            "impact_id": item.impact_id,
            "description": item.description,
            "impact_type": item.impact_type,
            "affected_entity_ids": list(item.affected_entity_ids),
            "status": item.status,
            "confidence": item.confidence,
        }
        for item in validated.impacts
    ]

    projected_relationships: list[dict[str, object]] = []
    for item in validated.relationships:
        norm = " ".join(item.statement.casefold().split())
        if not norm or norm not in seen_statements:
            projected_relationships.append(
                {
                    "relationship_id": item.relationship_id,
                    "subject_entity_id": item.subject_entity_id,
                    "predicate": item.predicate,
                    "object_entity_id": item.object_entity_id,
                    "statement": item.statement,
                    "status": item.status,
                    "confidence": item.confidence,
                }
            )

    projected_timeline: list[dict[str, object]] = []
    for item in validated.timeline:
        norm = " ".join(item.event.casefold().split())
        if not norm or norm not in seen_statements:
            projected_timeline.append(
                {
                    "event_id": item.event_id,
                    "timestamp": (
                        item.timestamp.isoformat()
                        if item.timestamp is not None
                        else None
                    ),
                    "timestamp_text": item.timestamp_text,
                    "event": item.event,
                    "actors": list(item.actors),
                    "evidence_ids": list(item.evidence_ids),
                    "status": item.status,
                    "confidence": item.confidence,
                }
            )

    payload: dict[str, object] = {
        "facts": projected_facts,
        "entities": projected_entities,
        "relationships": projected_relationships,
        "evidence": projected_evidence,
        "timeline": projected_timeline,
        "impacts": projected_impacts,
    }
    serialized = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return _RETRIEVAL_QUERY_PREFIX + serialized + _RETRIEVAL_QUERY_SUFFIX


__all__ = ["project_case_state_to_retrieval_query"]
