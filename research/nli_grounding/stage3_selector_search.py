import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from config import OUTPUTS_DIR, CACHE_DIR, SEED, set_seed
from src.datasets.wice import load_wice_split, WiCEExample

def evaluate_selector_on_dev(selector_fn, dev_examples, sims_list):
    precisions, recalls, f1s = [], [], []
    units_before, units_after = [], []

    for ex, s_list in zip(dev_examples, sims_list):
        n_u = len(ex.evidence_units)
        units_before.append(n_u)

        kept_indices = selector_fn(s_list, ex.evidence_units)
        # Always retain at least top-1
        if not kept_indices and s_list:
            kept_indices = [int(np.argmax(s_list))]
        units_after.append(len(kept_indices))

        if ex.gold_evidence_indices:
            gold_set = set(ex.gold_evidence_indices)
            sel_set = set(kept_indices)
            tp = len(gold_set.intersection(sel_set))
            p = tp / len(sel_set) if len(sel_set) > 0 else 0.0
            r = tp / len(gold_set) if len(gold_set) > 0 else 0.0
            f1 = (2 * p * r) / (p + r) if (p + r) > 0 else 0.0

            precisions.append(p)
            recalls.append(r)
            f1s.append(f1)

    avg_before = float(np.mean(units_before))
    avg_after = float(np.mean(units_after))
    pct_removed = (1.0 - (avg_after / avg_before)) * 100.0

    return {
        "evidence_precision": float(np.mean(precisions)),
        "evidence_recall": float(np.mean(recalls)),
        "mean_per_ex_f1": float(np.mean(f1s)),
        "avg_units_before": avg_before,
        "avg_units_after": avg_after,
        "pct_units_removed": pct_removed,
    }

def main():
    print("=" * 80)
    print("STAGE 3: RETRIEVAL AUDIT FOR CANDIDATE SEMANTIC SELECTORS ON DEV")
    print("=" * 80)

    dev_ex = load_wice_split("dev")
    sims = [json.loads(l)["similarities"] for l in open(CACHE_DIR / "semantic_scores" / "dev.jsonl", "r", encoding="utf-8") if l.strip()]

    selectors = {}

    # Selector A — Current (tau = 0.20)
    selectors["Selector A (tau=0.20 - Current)"] = lambda s, u: [i for i, val in enumerate(s) if val >= 0.20]

    # Selector B — Top-K (k in {3, 5, 8})
    for k in [3, 5, 8]:
        selectors[f"Selector B (Top-{k})"] = (lambda k_val: lambda s, u: list(np.argsort(s)[::-1][:min(k_val, len(s))]))(k)

    # Selector C — Threshold + Top-K (tau in {0.15, 0.20, 0.25}, k in {5, 8})
    for tau in [0.15, 0.20, 0.25]:
        for k in [5, 8]:
            def make_sel_c(t, k_max):
                def sel(s, u):
                    filt = [i for i, val in enumerate(s) if val >= t]
                    if len(filt) > k_max:
                        # Sort filtered by similarity descending and keep top k_max
                        filt_sorted = sorted(filt, key=lambda i: s[i], reverse=True)
                        return filt_sorted[:k_max]
                    return filt
                return sel
            selectors[f"Selector C (tau={tau:.2f}, max_k={k})"] = make_sel_c(tau, k)

    # Selector D — Relative Margin (delta in {0.10, 0.15, 0.20})
    for delta in [0.10, 0.15, 0.20]:
        def make_sel_d(d):
            def sel(s, u):
                if not s:
                    return []
                max_s = max(s)
                return [i for i, val in enumerate(s) if val >= max_s - d]
            return sel
        selectors[f"Selector D (Margin delta={delta:.2f})"] = make_sel_d(delta)

    rows = []
    for name, fn in selectors.items():
        res = evaluate_selector_on_dev(fn, dev_ex, sims)
        rows.append({
            "Selector": name,
            "Evidence Precision": f"{res['evidence_precision']:.2%}",
            "Evidence Recall": f"{res['evidence_recall']:.2%}",
            "Mean Evidence F1": f"{res['mean_per_ex_f1']:.4f}",
            "Avg Units Before": f"{res['avg_units_before']:.1f}",
            "Avg Units After": f"{res['avg_units_after']:.2f}",
            "% Units Removed": f"{res['pct_units_removed']:.1f}%",
            "raw_f1": res['mean_per_ex_f1'],
            "raw_rec": res['evidence_recall'],
            "raw_units": res['avg_units_after'],
        })

    df = pd.DataFrame(rows)
    print(df[["Selector", "Evidence Precision", "Evidence Recall", "Mean Evidence F1", "Avg Units After", "% Units Removed"]].to_string(index=False))

    json.dump(rows, open(OUTPUTS_DIR / "stage3_selector_dev_retrieval.json", "w", encoding="utf-8"), indent=2)

if __name__ == "__main__":
    main()
