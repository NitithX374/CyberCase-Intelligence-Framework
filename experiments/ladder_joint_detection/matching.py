from __future__ import annotations

from collections import defaultdict

from .constants import IRRELEVANT_LABEL, RELEVANT_LABEL
from .models import AuditBundle, EntityRecord, RowAudit, SourceData
from .spans import SpanMappingError, derive_spans, span_signature


def _records_by_text(records):
    grouped = defaultdict(list)
    for record in records:
        grouped[record.normalized_text].append(record)
    return {key: tuple(value) for key, value in grouped.items()}


def _classification_label_conflicts(classifications_by_text) -> tuple[str, ...]:
    return tuple(
        sorted(
            key
            for key, records in classifications_by_text.items()
            if {record.sentence_label for record in records} == {0, 1}
        )
    )


def _positive_row(classification, entities, duplicate_alignment, negative_conflict):
    if not entities:
        return RowAudit(
            classification,
            (),
            "unmatched_classification",
            (),
            False,
            False,
            None,
            negative_conflict,
            duplicate_alignment,
            "no_exact_entity_alignment",
        )
    successful: list[tuple[EntityRecord, tuple]] = []
    reasons: list[str] = []
    for entity in entities:
        if not entity.has_attack_token:
            reasons.append(f"{entity.record_id}:no_atk_tokens")
            continue
        try:
            successful.append((entity, derive_spans(classification, entity)))
        except SpanMappingError as error:
            reasons.append(f"{entity.record_id}:{error}")
    signatures = {span_signature(spans) for _, spans in successful}
    if len(successful) == len(entities) and len(signatures) == 1 and successful:
        spans = successful[0][1]
        return RowAudit(
            classification,
            tuple(entity.record_id for entity in entities),
            "exact_normalized",
            spans,
            True,
            True,
            True,
            negative_conflict,
            duplicate_alignment,
            "valid_attack_spans",
        )
    reason = "inconsistent_duplicate_spans" if len(signatures) > 1 else ";".join(reasons)
    return RowAudit(
        classification,
        tuple(entity.record_id for entity in entities),
        "exact_no_span",
        (),
        False,
        False,
        None,
        negative_conflict,
        duplicate_alignment,
        reason or "no_valid_attack_spans",
    )


def _negative_row(classification, entities, duplicate_alignment, safe):
    conflict = bool(entities)
    return RowAudit(
        classification,
        tuple(entity.record_id for entity in entities),
        "negative_all_o" if safe else "negative_span_masked",
        (),
        safe,
        safe,
        False if safe else None,
        conflict,
        duplicate_alignment,
        "negative_label_without_entity_conflict" if safe else "negative_entity_conflict",
    )


def build_audit_bundle(source_data: SourceData) -> AuditBundle:
    rows: list[RowAudit] = []
    classification_conflicts: list[str] = []
    negative_conflicts: list[str] = []
    entity_by_split_text: dict[str, dict[str, tuple[EntityRecord, ...]]] = {}
    classification_by_split_text: dict[str, dict[str, tuple]] = {}
    for split, classifications in source_data.classifications.items():
        classification_by_split_text[split] = _records_by_text(classifications)
        classification_conflicts.extend(
            f"{split}:{key}" for key in _classification_label_conflicts(classification_by_split_text[split])
        )
        entity_by_split_text[split] = _records_by_text(source_data.entities[split])
        for key, records in classification_by_split_text[split].items():
            if any(record.sentence_label == IRRELEVANT_LABEL for record in records) and key in entity_by_split_text[split]:
                negative_conflicts.append(f"{split}:{key}")
    negative_safe = not classification_conflicts and not negative_conflicts

    for split, classifications in source_data.classifications.items():
        entity_lookup = entity_by_split_text[split]
        class_lookup = classification_by_split_text[split]
        for classification in classifications:
            entities = entity_lookup.get(classification.normalized_text, ())
            duplicate = len(entities) > 1 or len(class_lookup[classification.normalized_text]) > 1
            if classification.sentence_label == RELEVANT_LABEL:
                rows.append(_positive_row(classification, entities, duplicate, False))
            else:
                rows.append(_negative_row(classification, entities, duplicate, negative_safe))

    decision = _decision(rows, source_data, classification_conflicts)
    return AuditBundle(
        source_data,
        tuple(rows),
        {},
        decision,
        negative_safe,
        tuple(sorted(classification_conflicts)),
        tuple(sorted(negative_conflicts)),
    )


def _decision(rows, source_data: SourceData, classification_conflicts) -> str:
    if classification_conflicts or any(item.kind == "classification_row" for item in source_data.malformed):
        return "UNSAFE"
    positive_rows = [row for row in rows if row.classification.sentence_label == RELEVANT_LABEL]
    exact_positive_rows = [row for row in positive_rows if row.entity_ids]
    valid_positive_rows = [row for row in exact_positive_rows if row.has_span_annotation]
    if not valid_positive_rows:
        return "UNSAFE"
    if len(valid_positive_rows) == len(positive_rows) and not source_data.malformed:
        return "SAFE"
    return "PARTIALLY_SAFE"
