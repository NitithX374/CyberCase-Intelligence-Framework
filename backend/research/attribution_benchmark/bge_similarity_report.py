from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

from research.attribution_benchmark.bge_similarity_runtime import file_hash
from research.attribution_benchmark.receipts import save


def distribution(values) -> dict | None:
    scores = np.asarray(values, dtype=float)
    if not len(scores):
        return None
    if not np.isfinite(scores).all():
        raise ValueError("Nonfinite similarity result")
    return {
        "n": len(scores),
        "mean": float(scores.mean()),
        "median": float(np.median(scores)),
        "std": float(scores.std()),
        "minimum": float(scores.min()),
        "maximum": float(scores.max()),
        "percentiles": {
            str(q): float(np.quantile(scores, q / 100))
            for q in (1, 5, 10, 25, 75, 90, 95, 99)
        },
    }


def write_results(
    output: Path, examples: list[dict], pairs: dict, scores: dict, manifest: dict
):
    if set(scores) != set(pairs):
        raise ValueError("Complete paired similarity scores required")
    rows = []
    groups = {}
    for split in ("test", "test_ood"):
        selected = [example for example in examples if example["split"] == split]
        claim_keys = [example["claim_key"] for example in selected]
        unit_keys = [key for example in selected for key in example["unit_keys"]]
        groups[split] = {
            "rows": len(selected),
            "claim_occurrences": distribution(
                [scores[key]["cosine"] for key in claim_keys]
            ),
            "source_unit_occurrences": distribution(
                [scores[key]["cosine"] for key in unit_keys]
            ),
            "unique_claims": distribution(
                [scores[key]["cosine"] for key in set(claim_keys)]
            ),
            "unique_source_units": distribution(
                [scores[key]["cosine"] for key in set(unit_keys)]
            ),
        }
    for example in examples:
        unit_scores = [scores[key]["cosine"] for key in example["unit_keys"]]
        rows.append(
            {
                "id": example["id"],
                "split": example["split"],
                "gold": example["gold"],
                "claim_key": example["claim_key"],
                "claim_cosine": scores[example["claim_key"]]["cosine"],
                "source_unit_keys": example["unit_keys"],
                "source_unit_cosines": unit_scores,
                "source_unit_count": len(unit_scores),
                "source_unit_mean_cosine": float(np.mean(unit_scores))
                if unit_scores
                else None,
                "source_unit_min_cosine": min(unit_scores) if unit_scores else None,
            }
        )
    with (output / "rows.jsonl").open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")
    fields = [
        "key",
        "roles",
        "source",
        "translation",
        "cosine",
        "en_tokens",
        "th_tokens",
        "en_truncated",
        "th_truncated",
    ]
    with (output / "pairs.csv").open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for key in sorted(pairs):
            writer.writerow(
                {
                    "key": key,
                    "roles": "|".join(pairs[key]["roles"]),
                    "source": pairs[key]["source"],
                    "translation": pairs[key]["translation"],
                    **{field: scores[key][field] for field in fields[4:]},
                }
            )
    lowest = []
    for key in sorted(scores, key=lambda key: (scores[key]["cosine"], key))[:100]:
        lowest.append({**scores[key], **pairs[key]})
    save(output / "lowest_100.json", lowest)
    summary = {
        "scope": "Paired original EN / Google MT-TH dense semantic similarity; not translation gold or Claim support labels",
        "runtime": manifest["runtime"],
        "input": manifest["input"],
        "unique_text_pairs": distribution(
            [score["cosine"] for score in scores.values()]
        ),
        "changed_text_pairs": distribution(
            [
                scores[key]["cosine"]
                for key in pairs
                if pairs[key]["source"] != pairs[key]["translation"]
            ]
        ),
        "identical_text_pairs": sum(
            pair["source"] == pair["translation"] for pair in pairs.values()
        ),
        "splits": groups,
        "truncated_en": sum(score["en_truncated"] for score in scores.values()),
        "truncated_th": sum(score["th_truncated"] for score in scores.values()),
        "files_sha256": {
            name: file_hash(output / name)
            for name in ("scores.jsonl", "rows.jsonl", "pairs.csv", "lowest_100.json")
        },
        "notes": [
            "Unique-pair averages avoid repeated-text weighting; row/unit occurrence averages include repeated references",
            "Same text may occur as both a Claim and a Source unit",
            "Empty reference bundles retain null Source metrics, not artificial zero similarity",
            "High cosine does not verify names, amounts, negation, legal roles or inherited-gold validity",
            "No threshold filtering, gold repair, verifier fitting or production changes",
        ],
    }
    save(output / "summary.json", summary)
    table = [
        "| Split | Rows | Claim mean | Claim median | Source-unit mean | Source-unit median |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for split, group in groups.items():
        claim, unit = group["claim_occurrences"], group["source_unit_occurrences"]
        table.append(
            f"| {split} | {group['rows']} | {claim['mean']:.4f} | {claim['median']:.4f} | {unit['mean']:.4f} | {unit['median']:.4f} |"
        )
    text = "\n".join(
        [
            "# BGE-M3 original EN / Google MT-TH cosine similarity",
            "",
            manifest["runtime"]["revision"],
            "",
            f"Complete: {len(scores):,} unique paired texts, {len(rows):,} benchmark rows.",
            "",
            f"Unique-pair mean {summary['unique_text_pairs']['mean']:.4f}; median {summary['unique_text_pairs']['median']:.4f}; identical texts {summary['identical_text_pairs']:,}.",
            "",
            *table,
            "",
            "Source statistics above use occurrences, including repeated references. Per-unique-text statistics are in summary.json.",
            "",
            f"Truncated: EN {summary['truncated_en']}, TH {summary['truncated_th']}.",
            "",
            "Scores are semantic proximity, not independently labelled translation fidelity or Claim/Source support. No acceptance threshold or gold repair is applied.",
            "",
            "Local files: pairs.csv (EN/TH texts and scores), scores.jsonl, rows.jsonl, lowest_100.json, summary.json, manifest.json.",
            "",
            "Method follows the [BGE-M3 model card](https://huggingface.co/BAAI/bge-m3): dense CLS embeddings, no query instructions; float32 normalization and paired dot product. Runtime weights are explicitly fp16 on CUDA in this run.",
            "",
        ]
    )
    (output / "report.md").write_text(text, encoding="utf-8")
    return summary
