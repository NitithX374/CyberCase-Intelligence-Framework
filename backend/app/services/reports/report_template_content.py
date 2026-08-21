from __future__ import annotations;

from collections.abc import Callable
from dataclasses import dataclass

from app.schemas.reports import ReportClaim
from app.services.extraction.extraction_contracts import (
    ExtractedEntity,
    ExtractedRelationship,
    ExtractedTimelineEvent,
)
from app.services.reports.report_contracts import (
    _TEMPLATE_SECTION_ITEM_LIMIT,
    ReportInputSnapshot,
)

TextFormatter = Callable[[object], str]
OmissionRecorder = Callable[[str, int], None]


@dataclass(frozen=True)
class InvestigationEvidence:
    entities: list[ExtractedEntity]
    relationships: list[ExtractedRelationship]
    items: list[str]
    claims: list[ReportClaim]


def build_investigation_evidence(
    snapshot: ReportInputSnapshot,
    *,
    bounded_text: TextFormatter,
    record_omission: OmissionRecorder,
    claim_start: int,
) -> InvestigationEvidence:
    claims: list[ReportClaim] = []
    entities = snapshot.extraction.entities
    relationships = snapshot.extraction.relationships
    entity_by_id = {entity.entity_id: entity for entity in entities}
    timeline_candidates: list[tuple[str, ExtractedTimelineEvent]] = []
    for event in snapshot.extraction.timeline:
        if event.timestamp is not None and event.timestamp_text:
            timestamp = f"{event.timestamp.isoformat()} ({event.timestamp_text})"
        elif event.timestamp is not None:
            timestamp = event.timestamp.isoformat()
        else:
            timestamp = event.timestamp_text or "not reported"
        actors = ", ".join(event.actors) or "none persisted"
        linked_evidence = ", ".join(event.evidence_ids) or "none persisted"
        timeline_candidates.append(
            (
                bounded_text(
                    f"{event.event_id} | Time: {timestamp} | Event: {event.event} | "
                    f"Actors: {actors} | Linked evidence: {linked_evidence} | Status: "
                    f"{event.status} | Confidence: {event.confidence}."
                ),
                event,
            )
        )

    entity_candidates = [
        bounded_text(
            f"Entity | Name: {entity.name} | Type: {entity.entity_type} | "
            f"Reported role: {entity.reported_role or 'not reported'} | "
            f"Persisted status: not available | Confidence: {entity.confidence}."
        )
        for entity in entities
    ]
    relationship_candidates: list[str] = []
    for relationship in relationships:
        subject = entity_by_id.get(relationship.subject_entity_id)
        object_ = entity_by_id.get(relationship.object_entity_id)
        subject_name = (
            subject.name if subject is not None else relationship.subject_entity_id
        )
        object_name = (
            object_.name if object_ is not None else relationship.object_entity_id
        )
        relationship_candidates.append(
            bounded_text(
                f"Relationship | {subject_name} -> {relationship.predicate} -> "
                f"{object_name} | Statement: {relationship.statement} | Status: "
                f"{relationship.status} | Confidence: {relationship.confidence}."
            )
        )

    evidence_to_examine_items: list[str] = []
    # Reserve one visible row for each later category so mixed content cannot
    # silently erase entity or relationship coverage at the 32-item boundary.
    included_timeline = timeline_candidates[: _TEMPLATE_SECTION_ITEM_LIMIT - 2]
    if included_timeline:
        evidence_to_examine_items.extend(text for text, _ in included_timeline)
    else:
        evidence_to_examine_items.append(
            "No timeline events were persisted for this snapshot."
        )
    record_omission(
        "Timeline events",
        len(timeline_candidates) - len(included_timeline),
    )

    entity_capacity = _TEMPLATE_SECTION_ITEM_LIMIT - len(evidence_to_examine_items) - 1
    included_entities = entity_candidates[: max(0, entity_capacity)]
    if included_entities:
        evidence_to_examine_items.extend(included_entities)
    else:
        evidence_to_examine_items.append("No entities were persisted for this snapshot.")
    record_omission("Entities", len(entity_candidates) - len(included_entities))

    relationship_capacity = (
        _TEMPLATE_SECTION_ITEM_LIMIT - len(evidence_to_examine_items)
    )
    included_relationships = relationship_candidates[:relationship_capacity]
    if included_relationships:
        evidence_to_examine_items.extend(included_relationships)
    else:
        evidence_to_examine_items.append(
            "No relationships were persisted for this snapshot."
        )
    record_omission(
        "Relationships",
        len(relationship_candidates) - len(included_relationships),
    )

    for text, event in included_timeline:
        claims.append(
            ReportClaim(
                claim_id=f"C-{claim_start + len(claims) + 1:03d}",
                section_id="evidence_to_examine",
                text=text,
                support_type=(
                    "user_reported"
                    if event.status == "reported"
                    else "extraction_candidate"
                ),
                evidence_ids=list(event.evidence_ids),
                timeline_event_ids=[event.event_id],
            )
        )



    return InvestigationEvidence(
        entities=entities,
        relationships=relationships,
        items=evidence_to_examine_items,
        claims=claims,
    )
