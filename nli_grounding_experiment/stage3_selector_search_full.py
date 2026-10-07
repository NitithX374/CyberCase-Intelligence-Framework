import json
import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd
import torch
import joblib

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from config import OUTPUTS_DIR, CACHE_DIR, SEED, set_seed
from src.datasets.wice import load_wice_split, WiCEExample
from src.metrics import compute_classification_metrics
from src.nli import NLIRunner

def evaluate_retrieval(selector_fn, examples, sims_list):
    precisions, recalls, f1s = [], [], []
    units_before, units_after = [], []
    retained_indices_all = []

    for ex, s_list in zip(examples, sims_list):
        n_u = len(ex.evidence_units)
        units_before.append(n_u)

        kept_indices = selector_fn(s_list, ex.evidence_units)
        # Always retain at least top-1
        if not kept_indices and s_list:
            kept_indices = [int(np.argmax(s_list))]
        units_after.append(len(kept_indices))
        retained_indices_all.append(kept_indices)

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
        "retained_indices": retained_indices_all,
    }

def get_selectors():
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

    return selectors

def run_stage3():
    set_seed(SEED)
    print("=" * 80)
    print("STAGE 3: COMPREHENSIVE SEMANTIC SELECTOR SEARCH ON DEV")
    print("=" * 80)

    dev_ex = load_wice_split("dev")
    y_dev = np.array([ex.gold_label_binary for ex in dev_ex])
    sims_dev = [json.loads(l)["similarities"] for l in open(CACHE_DIR / "semantic_scores" / "dev.jsonl", "r", encoding="utf-8") if l.strip()]

    selectors = get_selectors()
    retrieval_results = {}
    selector_premises = {}

    for name, fn in selectors.items():
        ret = evaluate_retrieval(fn, dev_ex, sims_dev)
        retrieval_results[name] = ret
        premises = []
        for ex, kept in zip(dev_ex, ret["retained_indices"]):
            if kept:
                p = " ".join([ex.evidence_units[i] for i in kept])
            elif ex.evidence_units:
                p = ex.evidence_units[0]
            else:
                p = ""
            premises.append(p)
        selector_premises[name] = premises

    # Deduplicate premise-claim pairs
    unique_pairs = {}
    for name, p_list in selector_premises.items():
        for idx, (p, ex) in enumerate(zip(p_list, dev_ex)):
            key = (p, ex.claim)
            if key not in unique_pairs:
                unique_pairs[key] = len(unique_pairs)

    pair_list = list(unique_pairs.keys())
    print(f"Total DEV examples: {len(dev_ex)}")
    print(f"Total candidate selectors: {len(selectors)}")
    print(f"Unique (premise, claim) pairs across all 13 selectors on DEV: {len(pair_list)}")

    # Check NLI cache for unique pairs
    nli_cache_file = CACHE_DIR / "stage3_dev_nli_cache.jsonl"
    pair_to_probs = {}

    # Preload from dev_forward_filt_0_20.jsonl
    filt_cache = CACHE_DIR / "forward_nli" / "dev_forward_filt_0_20.jsonl"
    if filt_cache.exists():
        filt_records = [json.loads(l) for l in open(filt_cache, "r", encoding="utf-8") if l.strip()]
        for idx, (rec, ex) in enumerate(zip(filt_records, dev_ex)):
            p = selector_premises["Selector A (tau=0.20 - Current)"][idx]
            pair_to_probs[(p, ex.claim)] = np.array([rec["p_entailment"], rec["p_neutral"], rec["p_contradiction"]], dtype=np.float32)

    if nli_cache_file.exists():
        print("Loading cached NLI probabilities for Stage 3...")
        for line in open(nli_cache_file, "r", encoding="utf-8"):
            if line.strip():
                item = json.loads(line)
                pair_to_probs[(item["premise"], item["claim"])] = np.array(item["probs"], dtype=np.float32)

    missing_pairs = [p for p in pair_list if p not in pair_to_probs]
    if missing_pairs:
        print(f"Running Forward NLI on {len(missing_pairs)} missing pairs...")
        runner = NLIRunner()
        p_missing = [p[0] for p in missing_pairs]
        h_missing = [p[1] for p in missing_pairs]
        probs, _ = runner.predict_probs(p_missing, h_missing, batch_size=128)
        
        with open(nli_cache_file, "a", encoding="utf-8") as f:
            for pair, prob in zip(missing_pairs, probs):
                pair_to_probs[pair] = prob
                f.write(json.dumps({"premise": pair[0], "claim": pair[1], "probs": prob.tolist()}, ensure_ascii=False) + "\n")
        print(f"NLI evaluation complete.")

    # Load CURRENT_CHAMPION classifier head
    clf = joblib.load(OUTPUTS_DIR / "models" / "b1_lr_classifier.joblib")

    # Evaluate claim-level performance for each selector
    summary_rows = []
    for name, p_list in selector_premises.items():
        ret = retrieval_results[name]
        feats = np.array([pair_to_probs[(p, ex.claim)] for p, ex in zip(p_list, dev_ex)], dtype=np.float32)
        preds = clf.predict(feats)
        m = compute_classification_metrics(y_dev, preds)

        summary_rows.append({
            "Selector": name,
            "Accuracy": f"{m['accuracy']:.2%}",
            "Macro-F1": f"{m['macro_f1']:.4f}",
            "Supported-F1": f"{m['supported_f1']:.4f}",
            "FSR": f"{m['false_support_rate']:.2%}",
            "Evid Precision": f"{ret['evidence_precision']:.2%}",
            "Evid Recall": f"{ret['evidence_recall']:.2%}",
            "Evid F1": f"{ret['mean_per_ex_f1']:.4f}",
            "Units/Ex": f"{ret['avg_units_after']:.2f}",
            "% Removed": f"{ret['pct_units_removed']:.1f}%",
            "raw_macro_f1": m['macro_f1'],
            "raw_supp_f1": m['supported_f1'],
            "raw_fsr": m['false_support_rate'],
            "raw_evid_recall": ret['evidence_recall'],
            "raw_units": ret['avg_units_after'],
        })

    df = pd.DataFrame(summary_rows)
    # Sort according to priority: 1. Macro-F1 descending, 2. FSR ascending, 3. Evidence Recall descending
    df_sorted = df.sort_values(by=["raw_macro_f1", "raw_fsr", "raw_evid_recall"], ascending=[False, True, False])
    print("\n" + "=" * 100)
    print("STAGE 3 DEV RESULTS (SORTED BY PRIORITY):")
    print("=" * 100)
    cols = ["Selector", "Accuracy", "Macro-F1", "Supported-F1", "FSR", "Evid Precision", "Evid Recall", "Evid F1", "Units/Ex", "% Removed"]
    print(df_sorted[cols].to_string(index=False))

    out_json = OUTPUTS_DIR / "stage3_selector_search_results.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary_rows, f, indent=2)

    # Check candidate promotion
    baseline_row = [r for r in summary_rows if "Current" in r["Selector"]][0]
    best_row = df_sorted.iloc[0].to_dict()

    print("\n" + "=" * 80)
    print(f"Current Selector A (tau=0.20): Macro-F1 = {baseline_row['Macro-F1']}, Supp-F1 = {baseline_row['Supported-F1']}, FSR = {baseline_row['FSR']}, Units = {baseline_row['Units/Ex']}")
    print(f"Top Candidate ({best_row['Selector']}): Macro-F1 = {best_row['Macro-F1']}, Supp-F1 = {best_row['Supported-F1']}, FSR = {best_row['FSR']}, Units = {best_row['Units/Ex']}")
    print("=" * 80)

if __name__ == "__main__":
    run_stage3()
