from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from app.trace.b1_verifier import (
    ARTIFACT_SHA256,
    selected_indices,
    supported_probability,
)

from research.attribution_benchmark.data import cluster_key, read_split, sha256
from research.attribution_benchmark.paired_statistics import confusion, mcnemar
from research.attribution_benchmark.receipts import digest, save
from research.attribution_benchmark.translate_th import plan, read_cache


def metrics_from_counts(counts):
    tp, fp, tn, fn = counts.T
    total = tp + fp + tn + fn

    def divide(top, bottom):
        return np.divide(
            top, bottom, out=np.full_like(top, np.nan, dtype=float), where=bottom > 0
        )

    support_f1 = divide(2 * tp, 2 * tp + fp + fn)
    negative_f1 = divide(2 * tn, 2 * tn + fp + fn)
    return {
        "accuracy": divide(tp + tn, total),
        "supported_f1": support_f1,
        "macro_f1": (support_f1 + negative_f1) / 2,
        "false_acceptance_rate": divide(fp, fp + tn),
        "supported_retention": divide(tp, tp + fn),
    }


def transfer_bootstrap(rows, scores):
    generator = np.random.default_rng(20261007)
    draws = {language: np.zeros((2000, 4), dtype=float) for language in ("en", "th")}
    cluster_counts = {}
    for subset in sorted({row["src_dataset"] for row in rows}):
        clusters = defaultdict(lambda: {language: np.zeros(4) for language in draws})
        for row in rows:
            if row["src_dataset"] != subset:
                continue
            gold = row["attribution_label"] == "attributable"
            for language in draws:
                pred = scores[row["id"]][f"{language}_supported"]
                cell = 0 if gold and pred else 1 if pred else 3 if gold else 2
                clusters[cluster_key(row)][language][cell] += 1
        keys = sorted(clusters)
        cluster_counts[subset] = len(keys)
        indices = generator.integers(len(keys), size=(2000, len(keys)))
        for language in draws:
            counts = np.asarray([clusters[key][language] for key in keys])
            draws[language] += counts[indices].sum(axis=1)
    intervals = {language: metrics_from_counts(draws[language]) for language in draws}
    return {
        "clusters_by_subset": cluster_counts,
        "method": "Paired 2000 question/response cluster bootstrap resamples within source subsets; seed 20261007",
        "en95": {
            metric: np.nanquantile(values, [0.025, 0.975]).tolist()
            for metric, values in intervals["en"].items()
        },
        "th95": {
            metric: np.nanquantile(values, [0.025, 0.975]).tolist()
            for metric, values in intervals["th"].items()
        },
        "th_minus_en95": {
            metric: np.nanquantile(
                intervals["th"][metric] - values, [0.025, 0.975]
            ).tolist()
            for metric, values in intervals["en"].items()
        },
    }


def run(translations: Path, evaluation: Path):
    examples, texts = plan()
    cached = read_cache(translations / "translations.jsonl")
    score_path = evaluation / "scores.jsonl"
    records = [
        json.loads(line) for line in score_path.read_text(encoding="utf-8").splitlines()
    ]
    scores = {row["id"]: row for row in records}
    if len(scores) != len(records) or set(scores) != {row["id"] for row in examples}:
        raise ValueError("Complete unique matched EN/TH score coverage required")
    for example in examples:
        row = scores[example["id"]]
        claim = cached[example["claim_key"]]["translation"]
        units = [cached[key]["translation"] for key in example["unit_keys"]]
        if (
            row["input_sha256"] != digest([claim, units, example])
            or row["artifact_sha256"] != ARTIFACT_SHA256
            or row["gold"] != example["gold"]
        ):
            raise ValueError("Saved scores differ from frozen paired inputs/gold")
        for language in ("en", "th"):
            result = row[language]
            if len(result["similarities"]) != len(example["unit_keys"]):
                raise ValueError(
                    "Saved similarities do not address original unit mapping"
                )
            vector = [
                result["nli"][label]
                for label in ("entailment", "neutral", "contradiction")
            ]
            if abs(result["p_supported"] - supported_probability(vector)) > 1e-12:
                raise ValueError("Saved score differs from frozen classifier")
            if result["indices"] != list(
                selected_indices(result["similarities"])
            ) or row[f"{language}_supported"] != (result["p_supported"] >= 0.5):
                raise ValueError("Saved selection/admission differs from frozen method")
    result = {
        "rows": len(records),
        "artifact_sha256": ARTIFACT_SHA256,
        "scores_sha256": sha256(score_path),
        "translations_sha256": sha256(translations / "translations.jsonl"),
        "runtime": json.loads(
            (evaluation / "runtime.json").read_text(encoding="utf-8")
        ),
        "scope": "Machine-translated benchmark support classification with inherited English gold; native Thai accuracy and real-world truth unproven",
    }
    for split in ("test", "test_ood"):
        rows = read_split(split)
        subset = [scores[row["id"]] for row in rows]
        gold = [int(row["attribution_label"] == "attributable") for row in rows]
        en = [row["en_supported"] for row in subset]
        th = [row["th_supported"] for row in subset]
        result[split] = {
            "en": confusion(gold, en),
            "th": confusion(gold, th),
            "cluster_bootstrap": transfer_bootstrap(rows, scores),
            "row_mcnemar_descriptive_only": mcnemar(
                [p == y for p, y in zip(en, gold, strict=True)],
                [p == y for p, y in zip(th, gold, strict=True)],
            ),
            "archived_en_decision_differences": sum(
                row["en_supported"] != (row["archived_en_p_supported"] >= 0.5)
                for row in subset
            ),
            "empty_source_rows": sum(row["empty_source"] for row in subset),
            "length": {
                language: {
                    "truncated": sum(
                        row[language]["nli"]["truncated"] for row in subset
                    ),
                    "mean_selected_units": float(
                        np.mean([len(row[language]["indices"]) for row in subset])
                    ),
                    "mean_ms": float(
                        np.mean([row[language]["duration_ms"] for row in subset])
                    ),
                    "p95_ms": float(
                        np.quantile(
                            [row[language]["duration_ms"] for row in subset], 0.95
                        )
                    ),
                }
                for language in ("en", "th")
            },
        }
    result["verification"] = (
        "Every original row/gold/input hash, frozen LR score, selected indices and admission decision verified; no fitting/tuning"
    )
    save(evaluation / "verified_summary.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Independent complete EN/MT-TH receipt validation and paired cluster uncertainty"
    )
    parser.add_argument("--translations", type=Path, required=True)
    parser.add_argument("--evaluation", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.translations, args.evaluation)))


if __name__ == "__main__":
    main()
