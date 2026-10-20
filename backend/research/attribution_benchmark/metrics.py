from collections import defaultdict

import numpy as np
from sklearn.metrics import accuracy_score, average_precision_score, classification_report, confusion_matrix, f1_score, roc_auc_score

from data import LABELS


SEED = 20261006
BOOTSTRAP_REPLICATES = 2000


def predictions(rows, threshold):
    return ["attributable" if row["p_entailment"] >= threshold else "not attributable" for row in rows]


def summarize(rows, predicted):
    gold = [row["gold"] for row in rows]
    report = classification_report(gold, predicted, labels=list(LABELS), output_dict=True, zero_division=0)
    matrix = confusion_matrix(gold, predicted, labels=list(LABELS)).tolist()
    negative, positive = sum(matrix[0]), sum(matrix[1])
    if not negative or not positive:
        raise ValueError("Both gold classes are required for this report")
    scores = [1.0 - row["p_entailment"] for row in rows]
    return {
        "units": len(rows), "accuracy": float(accuracy_score(gold, predicted)),
        "macro_f1": report["macro avg"]["f1-score"],
        "per_class": {label: report[label] for label in LABELS},
        "confusion_labels": list(LABELS), "confusion_matrix": matrix,
        "false_acceptance": {"count": matrix[0][1], "gold_denominator": negative, "rate": matrix[0][1] / negative},
        "false_warning": {"count": matrix[1][0], "gold_denominator": positive, "rate": matrix[1][0] / positive},
        "fp_percent_total": 100 * matrix[0][1] / len(rows), "fn_percent_total": 100 * matrix[1][0] / len(rows),
        "auroc_not_attributable": float(roc_auc_score([label == LABELS[0] for label in gold], scores)),
        "ap_not_attributable": float(average_precision_score([label == LABELS[0] for label in gold], scores)),
        "valid_label_coverage": 1.0, "failures": 0,
        "truncated_units": sum(row["lengths"]["truncated"] for row in rows),
        "premise_tokens_removed": sum(row["lengths"]["removed_premise_tokens"] for row in rows),
        "premise_tokens_original": sum(row["lengths"]["premise_tokens"] for row in rows),
    }


def grouped(rows, threshold):
    sources = sorted({row["src_dataset"] for row in rows})
    output = {source: summarize([row for row in rows if row["src_dataset"] == source],
                              predictions([row for row in rows if row["src_dataset"] == source], threshold))
              for source in sources}
    return {
        "source_subsets": output,
        "mean_source_macro_f1": float(np.mean([item["macro_f1"] for item in output.values()])),
        "pooled": summarize(rows, predictions(rows, threshold)),
    }


def choose_threshold(rows):
    sources = [[row for row in rows if row["src_dataset"] == source] for source in sorted({row["src_dataset"] for row in rows})]
    candidates = [(value / 100, float(np.mean([
        f1_score([row["gold"] for row in selected], predictions(selected, value / 100), labels=list(LABELS),
                 average="macro", zero_division=0) for selected in sources
    ]))) for value in range(1, 100)]
    threshold, score = min(candidates, key=lambda item: (-item[1], abs(item[0] - 0.5), item[0]))
    return {
        "threshold": threshold, "dev_mean_source_macro_f1": score,
        "selection": "EN dev only; maximize mean source-subset Macro-F1; ties closest to 0.5 then lower threshold",
        "grid": "0.01..0.99 inclusive, step 0.01", "candidates": candidates,
    }


def f1_from_counts(values):
    errors = values[:, 1] + values[:, 2]
    left = 2 * values[:, 0]
    right = 2 * values[:, 3]
    f1_left = np.divide(left, left + errors, out=np.zeros_like(left), where=left + errors > 0)
    f1_right = np.divide(right, right + errors, out=np.zeros_like(right), where=right + errors > 0)
    return (f1_left + f1_right) / 2


def bootstrap(rows, threshold):
    random = np.random.default_rng(SEED)
    draws = []
    output = {}
    for source in sorted({row["src_dataset"] for row in rows}):
        clusters = defaultdict(lambda: np.zeros(4, dtype=np.float64))
        selected = [row for row in rows if row["src_dataset"] == source]
        for row, prediction in zip(selected, predictions(selected, threshold), strict=True):
            cell = 2 * LABELS.index(row["gold"]) + LABELS.index(prediction)
            clusters[row["cluster"]][cell] += 1
        counts = np.asarray(list(clusters.values()))
        weights = random.multinomial(len(counts), np.repeat(1 / len(counts), len(counts)), size=BOOTSTRAP_REPLICATES)
        values = f1_from_counts(weights @ counts)
        point = float(f1_from_counts(counts.sum(axis=0, keepdims=True))[0])
        expected = summarize(selected, predictions(selected, threshold))["macro_f1"]
        if not np.isclose(point, expected, atol=1e-12):
            raise ValueError("Bootstrap count formula disagrees with sklearn Macro-F1")
        output[source] = {"clusters": len(counts), "macro_f1_ci95": np.quantile(values, [0.025, 0.975]).tolist()}
        draws.append(values)
    return {
        "source_subsets": output,
        "mean_source_macro_f1_ci95": np.quantile(np.mean(draws, axis=0), [0.025, 0.975]).tolist(),
        "seed": SEED, "replicates": BOOTSTRAP_REPLICATES,
        "unit": "source-subset-stratified question+response clusters; all claims retained within resampled cluster",
    }


def argmax_reference(rows):
    predicted = ["attributable" if row["nli_argmax"] == "entailment" else "not attributable" for row in rows]
    sources = sorted({row["src_dataset"] for row in rows})
    scores = {source: summarize([row for row in rows if row["src_dataset"] == source],
                               [predicted[i] for i, row in enumerate(rows) if row["src_dataset"] == source])
              for source in sources}
    return {"source_subsets": scores, "mean_source_macro_f1": float(np.mean([x["macro_f1"] for x in scores.values()])),
            "pooled": summarize(rows, predicted)}
