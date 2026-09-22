from __future__ import annotations

from collections import Counter

from .constants import IRRELEVANT_LABEL, RELEVANT_LABEL, SPLITS
from .models import AuditBundle


def validate_audit_bundle(bundle: AuditBundle) -> None:
    expected = sum(len(bundle.source_data.classifications[split]) for split in SPLITS)
    if len(bundle.rows) != expected:
        raise ValueError(f"Audit row count mismatch: {len(bundle.rows)} != {expected}")
    identifiers = [row.classification.record_id for row in bundle.rows]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("Classification identifiers are not unique")
    for row in bundle.rows:
        if row.classification.sentence_label == RELEVANT_LABEL:
            if row.has_span_annotation and (not row.span_loss_mask or not row.evidence_spans):
                raise ValueError(f"Relevant row has invalid span supervision: {row.classification.record_id}")
            if not row.has_span_annotation and (row.span_loss_mask or row.evidence_spans):
                raise ValueError(f"Unaligned relevant row is not masked: {row.classification.record_id}")
        elif row.classification.sentence_label == IRRELEVANT_LABEL:
            if row.evidence_spans:
                raise ValueError(f"Negative row contains evidence spans: {row.classification.record_id}")
            if row.span_loss_mask != row.has_span_annotation:
                raise ValueError(f"Negative row has inconsistent supervision flags: {row.classification.record_id}")
        else:
            raise ValueError(f"Unexpected sentence label: {row.classification.sentence_label}")
    if any(item.kind == "classification_row" for item in bundle.source_data.malformed):
        raise ValueError("Malformed classification rows prevent joint dataset construction")


def _as_bool(value) -> bool:
    return bool(value)


def validate_joint_records(records: list[dict], expected_counts: Counter) -> None:
    if Counter(record["split"] for record in records) != expected_counts:
        raise ValueError("Joint dataset split counts do not preserve classification rows")
    identifiers = [record["id"] for record in records]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("Joint dataset identifiers are not unique")
    for record in records:
        spans = record["evidence_spans"]
        for span in spans:
            if not 0 <= span["start"] < span["end"] <= len(record["text"]):
                raise ValueError(f"Span outside text bounds: {record['id']}")
            if record["text"][span["start"] : span["end"]] != span["text"]:
                raise ValueError(f"Span text mismatch: {record['id']}")
        if record["sentence_label"] == RELEVANT_LABEL:
            if record["has_span_annotation"]:
                if not record["span_loss_mask"] or not spans:
                    raise ValueError(f"Relevant annotated row is invalid: {record['id']}")
            elif record["span_loss_mask"] or spans:
                raise ValueError(f"Relevant unannotated row is invalid: {record['id']}")
        elif record["sentence_label"] == IRRELEVANT_LABEL:
            if spans or _as_bool(record["has_attack_evidence"]):
                raise ValueError(f"Negative row contains attack evidence: {record['id']}")
            if record["has_span_annotation"] != record["span_loss_mask"]:
                raise ValueError(f"Negative supervision flags are inconsistent: {record['id']}")
        else:
            raise ValueError(f"Unexpected joint sentence label: {record['id']}")
