from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path

from .constants import (
    ENTITY_LABELS,
    IRRELEVANT_LABEL,
    OUTPUT_ROOT,
    RELEVANT_LABEL,
    SOURCE_NAME,
    SPLITS,
)
from .models import AuditBundle, ClassificationRecord, DiagnosticCandidate, RowAudit


def _write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _span_json(row: RowAudit) -> str:
    return json.dumps([asdict(span) for span in row.evidence_spans], ensure_ascii=False)


def _row_dict(row: RowAudit, diagnostic: DiagnosticCandidate | None = None) -> dict:
    item = {
        "classification_id": row.classification.record_id,
        "source_row": row.classification.source_row,
        "split": row.classification.split,
        "text": row.classification.original_text,
        "normalized_text": row.classification.normalized_text,
        "sentence_label": row.classification.sentence_label,
        "entity_ids": json.dumps(row.entity_ids),
        "alignment_type": row.alignment_type,
        "has_span_annotation": row.has_span_annotation,
        "span_loss_mask": row.span_loss_mask,
        "has_attack_evidence": row.has_attack_evidence,
        "negative_conflict": row.negative_conflict,
        "duplicate_alignment": row.duplicate_alignment,
        "span_reason": row.span_reason,
        "evidence_spans": _span_json(row),
    }
    if diagnostic:
        item.update(
            {
                "diagnostic_entity_id": diagnostic.entity_id,
                "diagnostic_candidate_text": diagnostic.text,
                "diagnostic_candidate_normalized_text": diagnostic.normalized_text,
                "diagnostic_similarity": round(diagnostic.similarity, 6),
                "diagnostic_category": diagnostic.category,
            }
        )
    return item


def _split_statistics(bundle: AuditBundle, split: str) -> dict:
    classifications = bundle.source_data.classifications[split]
    entities = bundle.source_data.entities[split]
    rows = [row for row in bundle.rows if row.classification.split == split]
    class_lookup: dict[str, list[ClassificationRecord]] = {}
    entity_lookup: dict[str, list] = {}
    for record in classifications:
        class_lookup.setdefault(record.normalized_text, []).append(record)
    for record in entities:
        entity_lookup.setdefault(record.normalized_text, []).append(record)
    positive_rows = [row for row in rows if row.classification.sentence_label == RELEVANT_LABEL]
    negative_rows = [row for row in rows if row.classification.sentence_label == IRRELEVANT_LABEL]
    entity_only_keys = sorted(set(entity_lookup).difference(class_lookup))
    return {
        "classification_total": len(classifications),
        "classification_positive": len(positive_rows),
        "classification_negative": len(negative_rows),
        "entity_extraction_total": len(entities),
        "entity_sentences_with_atk": sum(entity.has_attack_token for entity in entities),
        "entity_sentences_without_atk": sum(not entity.has_attack_token for entity in entities),
        "positive_exact_matches": sum(bool(row.entity_ids) for row in positive_rows),
        "positive_unmatched": sum(not row.entity_ids for row in positive_rows),
        "positive_exact_match_percentage": round(
            100 * sum(bool(row.entity_ids) for row in positive_rows) / len(positive_rows), 4
        )
        if positive_rows
        else 0.0,
        "positive_with_span_annotation": sum(row.has_span_annotation for row in positive_rows),
        "positive_without_span_annotation": sum(not row.has_span_annotation for row in positive_rows),
        "positive_span_supervision_percentage": round(
            100 * sum(row.has_span_annotation for row in positive_rows) / len(positive_rows), 4
        )
        if positive_rows
        else 0.0,
        "exact_alignment_count": sum(bool(row.entity_ids) for row in rows),
        "negative_conflict_count": sum(row.negative_conflict for row in negative_rows),
        "entity_only_samples": len(entity_only_keys),
        "entity_only_records": sum(len(entity_lookup[key]) for key in entity_only_keys),
        "classification_duplicate_texts": sum(len(value) > 1 for value in class_lookup.values()),
        "entity_duplicate_texts": sum(len(value) > 1 for value in entity_lookup.values()),
        "duplicate_alignment_count": sum(row.duplicate_alignment for row in rows),
        "one_to_many_matches": sum(len(entity_lookup.get(row.classification.normalized_text, ())) > 1 for row in rows),
        "many_to_one_matches": sum(
            len(class_lookup.get(key, ())) > 1 for key in entity_lookup if key in class_lookup
        ),
        "entity_sentences_matching_classification_negatives": sum(
            key in class_lookup and any(record.sentence_label == IRRELEVANT_LABEL for record in class_lookup[key])
            for key in entity_lookup
        ),
        "malformed_records": sum(item.split == split for item in bundle.source_data.malformed),
    }


def _conflict_rows(bundle: AuditBundle) -> list[dict]:
    conflicts: list[dict] = []
    conflict_keys = set(bundle.classification_label_conflict_keys)
    for row in bundle.rows:
        key = f"{row.classification.split}:{row.classification.normalized_text}"
        conflict_type = None
        if key in conflict_keys:
            conflict_type = "classification_label_conflict"
        elif row.negative_conflict:
            conflict_type = "entity_matches_negative_classification"
        elif row.span_reason == "inconsistent_duplicate_spans":
            conflict_type = "inconsistent_duplicate_entity_spans"
        if conflict_type:
            item = _row_dict(row)
            item["conflict_type"] = conflict_type
            conflicts.append(item)
    return conflicts


def _report_rows(bundle: AuditBundle, diagnostics: dict[str, DiagnosticCandidate]) -> list[dict]:
    rows = []
    for row in bundle.rows:
        diagnostic = diagnostics.get(row.classification.record_id)
        item = _row_dict(row, diagnostic if not row.entity_ids else None)
        item["id"] = row.classification.record_id
        item["original_text"] = row.classification.original_text
        item["entity_ids"] = list(row.entity_ids)
        item["evidence_spans"] = [asdict(span) for span in row.evidence_spans]
        rows.append(item)
    return rows


def _markdown(bundle: AuditBundle, report: dict, conflicts: list[dict]) -> str:
    lines = [
        "# LADDER Joint Attack-Relevance Alignment Audit",
        "",
        f"Decision: **{bundle.decision}**",
        "",
        "This audit uses exact conservative normalized matching. Similarity candidates are diagnostic only and never create training pairs.",
        "",
        "## Configuration",
        "",
        f"- Relevant label: `{RELEVANT_LABEL}`",
        f"- Irrelevant label: `{IRRELEVANT_LABEL}`",
        f"- Entity labels: `{', '.join(sorted(ENTITY_LABELS))}`",
        f"- Negative all-O span supervision safe: `{bundle.negative_span_supervision_safe}`",
        "",
        "## Split statistics",
        "",
        "| Split | CLS total | Positive CLS | Negative CLS | Entity sentences | Exact alignments | Positive exact rate | Positive spans | Positive masked | Entity-only | Negative conflicts |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for split in SPLITS:
        stats = report["split_statistics"][split]
        lines.append(
            f"| {split} | {stats['classification_total']} | {stats['classification_positive']} | "
            f"{stats['classification_negative']} | {stats['entity_extraction_total']} | "
            f"{stats['exact_alignment_count']} | {stats['positive_exact_match_percentage']}% | "
            f"{stats['positive_with_span_annotation']} | "
            f"{stats['positive_without_span_annotation']} | {stats['entity_only_samples']} | "
            f"{stats['negative_conflict_count']} |"
        )
    lines.extend(["", "## Alignment details", ""])
    lines.extend(
        [
            "| Split | Classification duplicate texts | Entity duplicate texts | Duplicate alignments | One-to-many | Many-to-one | Entity-only records | Entity sentences without ATK | Entity-to-negative matches | Malformed records |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for split in SPLITS:
        stats = report["split_statistics"][split]
        lines.append(
            f"| {split} | {stats['classification_duplicate_texts']} | {stats['entity_duplicate_texts']} | "
            f"{stats['duplicate_alignment_count']} | {stats['one_to_many_matches']} | "
            f"{stats['many_to_one_matches']} | {stats['entity_only_records']} | "
            f"{stats['entity_sentences_without_atk']} | "
            f"{stats['entity_sentences_matching_classification_negatives']} | "
            f"{stats['malformed_records']} |"
        )
    lines.extend(["", "## Main mismatch categories", ""])
    category_counts: dict[str, int] = {}
    for candidate in report["diagnostic_candidates"].values():
        category_counts[candidate["category"]] = category_counts.get(candidate["category"], 0) + 1
    if category_counts:
        for category, count in sorted(category_counts.items()):
            lines.append(f"- `{category}`: {count}")
    else:
        lines.append("- No unmatched positive diagnostics were available.")
    lines.extend(["", "## Matched examples", ""])
    for row in report["matched_examples"]:
        lines.append(f"- `{row['split']}` label `{row['sentence_label']}`: {row['text']}")
    lines.extend(["", "## Unmatched positive examples", ""])
    for row in report["unmatched_examples"]:
        candidate = row.get("diagnostic_candidate_text", "")
        lines.append(f"- `{row['split']}`: {row['text']} | diagnostic candidate: {candidate}")
    lines.extend(["", "## Conflicts", ""])
    if conflicts:
        for row in conflicts[:100]:
            lines.append(f"- `{row['conflict_type']}` `{row['split']}`: {row['text']}")
    else:
        lines.append("- None.")
    lines.extend(["", "## Partially supervised dataset interpretation", ""])
    lines.append(
        "All classification rows remain sentence-supervised. Positive rows without defensible entity alignment have span loss masked. Entity-only rows are retained in this audit but are not added as sentence-classification samples."
    )
    return "\n".join(lines) + "\n"


def write_audit_outputs(bundle: AuditBundle, diagnostics: dict[str, DiagnosticCandidate], output_root: Path = OUTPUT_ROOT) -> dict:
    output_root.mkdir(parents=True, exist_ok=True)
    split_statistics = {split: _split_statistics(bundle, split) for split in SPLITS}
    conflicts = _conflict_rows(bundle)
    matched = [_row_dict(row) for row in bundle.rows if row.entity_ids]
    unmatched = [
        _row_dict(row, diagnostics.get(row.classification.record_id))
        for row in bundle.rows
        if row.classification.sentence_label == RELEVANT_LABEL and not row.entity_ids
    ]
    report_rows = _report_rows(bundle, diagnostics)
    report = {
        "source": SOURCE_NAME,
        "decision": bundle.decision,
        "label_mapping": {"relevant": RELEVANT_LABEL, "irrelevant": IRRELEVANT_LABEL},
        "entity_labels": sorted(ENTITY_LABELS),
        "negative_span_supervision_safe": bundle.negative_span_supervision_safe,
        "classification_label_conflict_keys": list(bundle.classification_label_conflict_keys),
        "negative_conflict_keys": list(bundle.negative_conflict_keys),
        "split_statistics": split_statistics,
        "malformed_records": [asdict(item) for item in bundle.source_data.malformed],
        "diagnostic_candidates": {
            key: asdict(value) for key, value in diagnostics.items()
        },
        "matched_examples": matched[:20],
        "unmatched_examples": unmatched[:20],
        "conflict_examples": conflicts[:100],
        "rows": report_rows,
    }
    (output_root / "alignment_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    fieldnames = list(report_rows[0]) if report_rows else ["id"]
    _write_csv(output_root / "matched_samples.csv", matched, list(matched[0]) if matched else fieldnames)
    _write_csv(output_root / "conflicts.csv", conflicts, list(conflicts[0]) if conflicts else fieldnames + ["conflict_type"])
    for split in SPLITS:
        split_rows = [row for row in unmatched if row["split"] == split]
        _write_csv(output_root / f"unmatched_{split}.csv", split_rows, list(split_rows[0]) if split_rows else fieldnames)
    (output_root / "alignment_report.md").write_text(
        _markdown(bundle, report, conflicts), encoding="utf-8"
    )
    return report
