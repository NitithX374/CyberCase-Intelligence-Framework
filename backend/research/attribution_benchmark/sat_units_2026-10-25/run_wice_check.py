from __future__ import annotations

import json
import sys
import time
import unicodedata
from pathlib import Path
from dataclasses import asdict

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))

import numpy as np

from app.trace.b1_verifier import ARTIFACT, selected_indices, supported_probability
from research.attribution_benchmark.verifier_runtime import load_runtime
from research.attribution_benchmark.receipts import save


HERE = Path(__file__).resolve().parent
WICE_PATH = HERE.parents[2] / "research" / "nli_grounding" / "data" / "wice" / "test.jsonl"
OUTPUT_PATH = HERE / "wice_results.json"


def evaluate_confusion(y_true: list[int], y_pred: list[int]) -> dict:
    tp = sum(yt == 1 and yp == 1 for yt, yp in zip(y_true, y_pred))
    fp = sum(yt == 0 and yp == 1 for yt, yp in zip(y_true, y_pred))
    tn = sum(yt == 0 and yp == 0 for yt, yp in zip(y_true, y_pred))
    fn = sum(yt == 1 and yp == 0 for yt, yp in zip(y_true, y_pred))
    n = len(y_true)

    acc = (tp + tn) / n if n else 0.0
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1_sup = (2 * prec * rec) / (prec + rec) if (prec + rec) else 0.0

    # Macro F1 across both binary classes (supported=1, not_supported=0)
    prec_0 = tn / (tn + fn) if (tn + fn) else 0.0
    rec_0 = tn / (tn + fp) if (tn + fp) else 0.0
    f1_0 = (2 * prec_0 * rec_0) / (prec_0 + rec_0) if (prec_0 + rec_0) else 0.0
    macro_f1 = (f1_sup + f1_0) / 2.0

    fsr = fp / (fp + tn) if (fp + tn) else 0.0
    frr = fn / (fn + tp) if (fn + tp) else 0.0

    return {
        "n": n,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "supported_f1": f1_sup,
        "macro_f1": macro_f1,
        "fsr": fsr,
        "frr": frr,
    }


def run_wice(device: str = "cuda"):
    print(f"Loading WiCE test split from {WICE_PATH}...", flush=True)
    if not WICE_PATH.exists():
        raise FileNotFoundError(f"WiCE test split not found: {WICE_PATH}")

    rows = [json.loads(line) for line in WICE_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    print(f"Loaded {len(rows)} WiCE test rows.", flush=True)

    verifier, runtime = load_runtime(device)
    print(f"Loaded runtime on {device}: {runtime['device']}", flush=True)

    # 1. English exposure count on WiCE test
    claim_changed_count = sum(r["claim"] != unicodedata.normalize("NFKC", r["claim"]) for r in rows)
    unit_total = sum(len(r["evidence"]) for r in rows)
    unit_changed_count = sum(u != unicodedata.normalize("NFKC", u) for r in rows for u in r["evidence"])
    print(f"WiCE English exposure: claims changed {claim_changed_count}/{len(rows)}, units changed {unit_changed_count}/{unit_total}", flush=True)

    results_orig = []
    results_nfkc = []
    gold_binary = []

    started = time.perf_counter()
    sep = ARTIFACT["premise_separator"]

    for idx, row in enumerate(rows):
        claim = row["claim"]
        units = row["evidence"]
        gold = 1 if row["label"] == "supported" else 0
        gold_binary.append(gold)

        if units:
            similarities = tuple(verifier.selector.similarities(claim, units))
            indices = selected_indices(similarities)
            premise = sep.join(units[i] for i in indices)

            # Condition 1: Without NFKC
            nli_orig = verifier.nli.predict(premise, claim)
            p_sup_orig = supported_probability(nli_orig.vector)

            # Condition 2: With NFKC on premise & claim
            nli_nfkc = verifier.nli.predict(
                unicodedata.normalize("NFKC", premise),
                unicodedata.normalize("NFKC", claim)
            )
            p_sup_nfkc = supported_probability(nli_nfkc.vector)
        else:
            # Fallback for empty units
            nli_orig = verifier.nli.predict("", claim)
            p_sup_orig = supported_probability(nli_orig.vector)

            nli_nfkc = verifier.nli.predict("", unicodedata.normalize("NFKC", claim))
            p_sup_nfkc = supported_probability(nli_nfkc.vector)

        pred_orig = int(p_sup_orig >= 0.5)
        pred_nfkc = int(p_sup_nfkc >= 0.5)

        results_orig.append(pred_orig)
        results_nfkc.append(pred_nfkc)

        if (idx + 1) % 100 == 0 or idx == len(rows) - 1:
            elapsed = time.perf_counter() - started
            rate = (idx + 1) / elapsed
            print(f"Processed {idx + 1}/{len(rows)} WiCE rows ({rate:.1f} rows/s)...", flush=True)

    # Compute metrics
    metrics_orig = evaluate_confusion(gold_binary, results_orig)
    metrics_nfkc = evaluate_confusion(gold_binary, results_nfkc)

    changed_decisions = sum(po != pn for po, pn in zip(results_orig, results_nfkc))
    print(f"WiCE check completed: decisions changed = {changed_decisions}/{len(rows)}", flush=True)

    report = {
        "dataset": "WiCE test",
        "rows": len(rows),
        "runtime": runtime,
        "english_exposure": {
            "claims_changed": claim_changed_count,
            "claims_total": len(rows),
            "units_changed": unit_changed_count,
            "units_total": unit_total,
        },
        "without_nfkc": metrics_orig,
        "with_nfkc": metrics_nfkc,
        "changed_decisions": changed_decisions,
        "differences (nfkc - orig)": {
            k: metrics_nfkc[k] - metrics_orig[k]
            for k in ("accuracy", "precision", "recall", "supported_f1", "macro_f1", "fsr", "frr")
        }
    }

    save(OUTPUT_PATH, report)
    print(f"Saved WiCE check results to {OUTPUT_PATH}", flush=True)
    return report


if __name__ == "__main__":
    run_wice("cuda")
