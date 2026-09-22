from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.ladder_joint_detection.constants import OUTPUT_ROOT, SOURCE_NAME, SPLITS
from experiments.ladder_joint_detection.validation import validate_joint_records


def _load_report(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _joint_record(row: dict) -> dict:
    return {
        "id": row["id"],
        "text": row["original_text"],
        "sentence_label": int(row["sentence_label"]),
        "evidence_spans": row["evidence_spans"],
        "split": row["split"],
        "source": SOURCE_NAME,
        "alignment_type": row["alignment_type"],
        "has_span_annotation": bool(row["has_span_annotation"]),
        "span_loss_mask": bool(row["span_loss_mask"]),
        "has_attack_evidence": row["has_attack_evidence"],
        "entity_ids": row["entity_ids"],
    }


def _statistics(records: list[dict], report: dict) -> dict:
    result = {"negative_span_supervision_safe": report["negative_span_supervision_safe"], "splits": {}}
    for split in SPLITS:
        rows = [record for record in records if record["split"] == split]
        positives = [record for record in rows if record["sentence_label"] == 1]
        negatives = [record for record in rows if record["sentence_label"] == 0]
        result["splits"][split] = {
            "total": len(rows),
            "positive": len(positives),
            "negative": len(negatives),
            "positives_with_span_annotation": sum(record["has_span_annotation"] for record in positives),
            "positives_without_span_annotation": sum(not record["has_span_annotation"] for record in positives),
            "positive_span_supervision_percentage": round(
                100 * sum(record["has_span_annotation"] for record in positives) / len(positives), 4
            )
            if positives
            else 0.0,
            "negative_span_supervised": sum(record["span_loss_mask"] for record in negatives),
            "masked_rows": sum(not record["span_loss_mask"] for record in rows),
        }
    return result


def _write_exclusions(report: dict, output_root: Path) -> None:
    fieldnames = ["split", "source_path", "source_line", "kind", "message", "raw_text"]
    with (output_root / "joint_exclusions.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for item in report["malformed_records"]:
            writer.writerow({key: item.get(key, "") for key in fieldnames})


def build_joint_dataset(output_root: Path = OUTPUT_ROOT) -> dict:
    report = _load_report(output_root / "alignment_report.json")
    if report["decision"] == "UNSAFE":
        raise RuntimeError("Joint dataset construction refused because the audit decision is UNSAFE")
    records = [_joint_record(row) for row in report["rows"]]
    expected_counts = Counter(row["split"] for row in report["rows"])
    validate_joint_records(records, expected_counts)
    output_root.mkdir(parents=True, exist_ok=True)
    for split in SPLITS:
        rows = [record for record in records if record["split"] == split]
        path = output_root / f"joint_{split}.jsonl"
        path.write_text(
            "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
            encoding="utf-8",
        )
    statistics = _statistics(records, report)
    (output_root / "joint_dataset_statistics.json").write_text(
        json.dumps(statistics, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    _write_exclusions(report, output_root)
    return statistics


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the partially supervised LADDER joint dataset")
    parser.add_argument("--output-root", type=Path, default=OUTPUT_ROOT)
    args = parser.parse_args()
    statistics = build_joint_dataset(args.output_root.resolve())
    print(json.dumps(statistics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
