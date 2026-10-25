from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))

import numpy as np

from research.attribution_benchmark.data import cluster_key, read_split
from research.attribution_benchmark.paired_statistics import confusion, mcnemar
from research.attribution_benchmark.receipts import save

NEWLINE = chr(10)
CONDITIONS = (
    "pub_en",
    "pub_th",
    "pub_norm_th",
    "rloc_en",
    "rloc_th",
    "rloc_th_nfkc",
    "sat_en",
    "sat_th",
    "sat_en_nfkc",
    "sat_th_nfkc",
)
DIFFERENCES = (
    ("sat_en", "pub_en"),
    ("sat_th", "pub_th"),
    ("sat_en_nfkc", "pub_en"),
    ("sat_th_nfkc", "pub_th"),
    ("sat_en_nfkc", "sat_en"),
    ("sat_th_nfkc", "sat_th"),
    ("sat_en", "rloc_en"),
    ("sat_th", "rloc_th"),
    ("rloc_th_nfkc", "pub_norm_th"),
    ("rloc_th_nfkc", "rloc_th"),
    ("rloc_en", "pub_en"),
    ("rloc_th", "pub_th"),
    ("pub_th", "pub_en"),
)


def decision(record, condition):
    if condition == "pub_en":
        return record["published_en_supported"]
    if condition == "pub_th":
        return record["published_th_supported"]
    if condition == "pub_norm_th":
        return record["published_th_normalized_supported"]
    return record[condition]["supported"]



def metrics_from_counts(counts):
    tp, fp, tn, fn = counts.T

    def divide(top, bottom):
        return np.divide(top, bottom, out=np.full_like(top, np.nan, dtype=float), where=bottom > 0)

    return {
        "accuracy": divide(tp + tn, tp + fp + tn + fn),
        "precision": divide(tp, tp + fp),
        "recall": divide(tp, tp + fn),
        "f1": divide(2 * tp, 2 * tp + fp + fn),
        "fsr": divide(fp, fp + tn),
        "frr": divide(fn, fn + tp),
    }


def bootstrap(rows, records):
    generator = np.random.default_rng(20261007)
    draws = {condition: np.zeros((2000, 4)) for condition in CONDITIONS}
    for subset in sorted({row["src_dataset"] for row in rows}):
        clusters = defaultdict(lambda: {condition: np.zeros(4) for condition in CONDITIONS})
        for row in rows:
            if row["src_dataset"] != subset:
                continue
            gold = row["attribution_label"] == "attributable"
            for condition in CONDITIONS:
                pred = decision(records[row["id"]], condition)
                cell = 0 if gold and pred else 1 if pred else 3 if gold else 2
                clusters[cluster_key(row)][condition][cell] += 1
        keys = sorted(clusters)
        indices = generator.integers(len(keys), size=(2000, len(keys)))
        for condition in CONDITIONS:
            counts = np.asarray([clusters[key][condition] for key in keys])
            draws[condition] += counts[indices].sum(axis=1)
    values = {condition: metrics_from_counts(draws[condition]) for condition in CONDITIONS}
    interval = lambda array: np.nanquantile(array, [0.025, 0.975]).tolist()
    return {
        "per_condition95": {
            condition: {metric: interval(array) for metric, array in values[condition].items()}
            for condition in CONDITIONS
        },
        "differences95": {
            f"{a}-{b}": {
                metric: interval(values[a][metric] - values[b][metric]) for metric in values[a]
            }
            for a, b in DIFFERENCES
        },
    }


def dropped_pieces(reference):
    return sum(
        1
        for paragraph in reference.split(NEWLINE)
        if paragraph.strip()
        for piece in re.split(r"(?<=[.!?])\s+", paragraph.strip())
        if piece.strip() and len(piece.strip()) <= 3
    )


def run(folder: Path):
    lines = (folder / "scores.jsonl").read_text(encoding="utf-8").split(NEWLINE)
    records = {}
    for line in lines:
        if line:
            record = json.loads(line)
            records[record["id"]] = record
    result = {"runtime": json.loads((folder / "runtime.json").read_text(encoding="utf-8"))}
    for split in ("test", "test_ood"):
        rows = read_split(split)
        if any(row["id"] not in records for row in rows):
            raise ValueError(f"Incomplete scores for {split}")
        subset = [records[row["id"]] for row in rows]
        gold = [int(row["attribution_label"] == "attributable") for row in rows]
        points = {
            condition: confusion(gold, [decision(record, condition) for record in subset])
            for condition in CONDITIONS
        }
        point_differences = {
            f"{a}-{b}": {
                metric: points[a][key] - points[b][key]
                for metric, key in (
                    ("accuracy", "accuracy"),
                    ("precision", "precision"),
                    ("recall", "recall"),
                    ("f1", "f1"),
                    ("fsr", "false_acceptance_rate"),
                    ("frr", "false_rejection_rate"),
                )
            }
            for a, b in DIFFERENCES
        }
        agreement = {
            f"{a}-{b}": sum(
                decision(record, a) != decision(record, b) for record in subset
            )
            for a, b in DIFFERENCES
        }
        mcnemars = {
            f"{a}-{b}": mcnemar(
                [decision(r, b) == bool(y) for r, y in zip(subset, gold, strict=True)],
                [decision(r, a) == bool(y) for r, y in zip(subset, gold, strict=True)],
            )
            for a, b in DIFFERENCES[:4]
        }
        units = {}
        unit_keys = ["rloc_en", "rloc_th", "rloc_th_nfkc", "sat_en", "sat_th", "sat_en_nfkc", "sat_th_nfkc"]
        for key in unit_keys:
            if key in subset[0]:
                counts = [record[key]["units"] for record in subset]
                selected = [record[key]["selected"] for record in subset]
                units[key] = {
                    "median_units": float(np.median(counts)),
                    "mean_units": float(np.mean(counts)),
                    "median_selected": float(np.median(selected)),
                    "mean_selected": float(np.mean(selected)),
                    "truncated_rows": sum(record[key]["nli"]["truncated"] for record in subset),
                    "median_raw_tokens": float(np.median([record[key]["nli"]["raw_tokens"] for record in subset])),
                    "empty_premise_rows": sum(record[key]["units"] == 0 for record in subset),
                    "mean_ms": float(np.mean([record[key]["duration_ms"] for record in subset])),
                }
        for language in ("en", "th"):
            units[f"pub_{language}"] = {
                "truncated_rows": sum(record[f"published_{language}_nli"]["truncated"] for record in subset)
            }

        result[split] = {
            "rows": len(rows),
            "points": points,
            "point_differences": point_differences,
            "decision_differences": agreement,
            "row_mcnemar_descriptive_only": mcnemars,
            "cluster_bootstrap": bootstrap(rows, records),
            "units": units,
            "empty_reference_rows": sum(not row["references"] for row in rows),
            "rows_with_regex_dropped_pieces": sum(
                any(dropped_pieces(reference) for reference in row["references"]) for row in rows
            ),
            "rows_more_than_2000_char_unit_split": sum(
                any(len(unit) == 2000 for unit in record["sat_en_units"]) for record in subset
            ),
        }
    save(folder / "summary.json", result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.folder)
    for split in ("test", "test_ood"):
        for condition, point in result[split]["points"].items():
            print(split, condition, point["tp"], point["fp"], point["tn"], point["fn"], round(point["f1"], 4), round(point["false_acceptance_rate"], 4))


if __name__ == "__main__":
    main()
