import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from config import OUTPUTS_DIR, CACHE_DIR, SEED, set_seed
from src.datasets.wice import load_wice_split
from src.metrics import compute_classification_metrics
from src.bootstrap import paired_bootstrap_test

def main():
    set_seed(SEED)
    print("=" * 80)
    print("COMPUTING CROSS-FAMILY CONTROLLED RE-EVALUATION")
    print("=" * 80)

    # 1. Load ground truth
    test_ex = load_wice_split("test")
    y_test = np.array([ex.gold_label_binary for ex in test_ex])
    assert len(y_test) == 1070
    assert np.sum(y_test == 1) == 330
    assert np.sum(y_test == 0) == 740

    train_ex = load_wice_split("train")
    y_train = np.array([ex.gold_label_binary for ex in train_ex])

    # 2. Load mDeBERTa predictions from wice_predictions.csv
    pred_csv_path = OUTPUTS_DIR / "wice_predictions.csv"
    df_mdeberta = pd.read_csv(pred_csv_path)
    assert len(df_mdeberta) == 1070

    mdeberta_preds = {
        "B0": df_mdeberta["pred_B0"].to_numpy().astype(int),
        "B0-LR": df_mdeberta["pred_B0_LR"].to_numpy().astype(int),
        "B1": df_mdeberta["pred_B1"].to_numpy().astype(int),
        "B1-LR": df_mdeberta["pred_B1_LR"].to_numpy().astype(int),
        "B3": df_mdeberta["pred_B3"].to_numpy().astype(int),
    }

    # 3. Load MiniLM features & compute predictions
    cache_dir = CACHE_DIR / "cross_family_minilm"
    f_full_train = np.array([json.loads(l)["probs"] for l in open(cache_dir / "train_full_fwd_probs.jsonl", "r", encoding="utf-8") if l.strip()], dtype=np.float32)
    f_full_test = np.array([json.loads(l)["probs"] for l in open(cache_dir / "test_full_fwd_probs.jsonl", "r", encoding="utf-8") if l.strip()], dtype=np.float32)

    f_filt_train = np.array([json.loads(l)["probs"] for l in open(cache_dir / "train_filt_fwd_probs.jsonl", "r", encoding="utf-8") if l.strip()], dtype=np.float32)
    f_filt_test = np.array([json.loads(l)["probs"] for l in open(cache_dir / "test_filt_fwd_probs.jsonl", "r", encoding="utf-8") if l.strip()], dtype=np.float32)

    f_rev_train = np.array([json.loads(l)["probs"] for l in open(cache_dir / "train_filt_rev_probs.jsonl", "r", encoding="utf-8") if l.strip()], dtype=np.float32)
    f_rev_test = np.array([json.loads(l)["probs"] for l in open(cache_dir / "test_filt_rev_probs.jsonl", "r", encoding="utf-8") if l.strip()], dtype=np.float32)

    # MiniLM B0: argmax == 0 (entailment)
    minilm_b0 = (np.argmax(f_full_test, axis=1) == 0).astype(int)

    # MiniLM B0-LR: LR on full forward
    clf_b0_lr = LogisticRegression(C=1.0, class_weight="balanced", random_state=SEED, max_iter=1000)
    clf_b0_lr.fit(f_full_train, y_train)
    minilm_b0_lr = clf_b0_lr.predict(f_full_test)

    # MiniLM B1: argmax == 0 (entailment)
    minilm_b1 = (np.argmax(f_filt_test, axis=1) == 0).astype(int)

    # MiniLM B1-LR: LR on filt forward
    clf_b1_lr = LogisticRegression(C=1.0, class_weight="balanced", random_state=SEED, max_iter=1000)
    clf_b1_lr.fit(f_filt_train, y_train)
    minilm_b1_lr = clf_b1_lr.predict(f_filt_test)

    # MiniLM B3: LR on 6D [filt_fwd, filt_rev]
    clf_b3 = LogisticRegression(C=1.0, class_weight="balanced", random_state=SEED, max_iter=1000)
    clf_b3.fit(np.hstack([f_filt_train, f_rev_train]), y_train)
    minilm_b3 = clf_b3.predict(np.hstack([f_filt_test, f_rev_test]))

    minilm_preds = {
        "B0": minilm_b0,
        "B0-LR": minilm_b0_lr,
        "B1": minilm_b1,
        "B1-LR": minilm_b1_lr,
        "B3": minilm_b3,
    }

    # 4. Helper function to compute full metrics table
    def get_full_metrics_table(preds_dict):
        table = {}
        for method, p in preds_dict.items():
            tp = int(np.sum((p == 1) & (y_test == 1)))
            fp = int(np.sum((p == 1) & (y_test == 0)))
            tn = int(np.sum((p == 0) & (y_test == 0)))
            fn = int(np.sum((p == 0) & (y_test == 1)))

            assert tp + fp + tn + fn == 1070
            assert tp + fn == 330
            assert tn + fp == 740

            acc = (tp + tn) / 1070
            supp_p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            supp_r = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            supp_f1 = 2 * supp_p * supp_r / (supp_p + supp_r) if (supp_p + supp_r) > 0 else 0.0

            unsupp_p = tn / (tn + fn) if (tn + fn) > 0 else 0.0
            unsupp_r = tn / (tn + fp) if (tn + fp) > 0 else 0.0
            unsupp_f1 = 2 * unsupp_p * unsupp_r / (unsupp_p + unsupp_r) if (unsupp_p + unsupp_r) > 0 else 0.0

            macro_f1 = (supp_f1 + unsupp_f1) / 2.0
            fsr = fp / (tn + fp)

            table[method] = {
                "tp": tp,
                "fp": fp,
                "tn": tn,
                "fn": fn,
                "pred_pos": tp + fp,
                "pred_neg": tn + fn,
                "gold_pos": 330,
                "gold_neg": 740,
                "accuracy": acc,
                "macro_f1": macro_f1,
                "supp_p": supp_p,
                "supp_r": supp_r,
                "supp_f1": supp_f1,
                "fsr": fsr,
            }
        return table

    mdeberta_metrics = get_full_metrics_table(mdeberta_preds)
    minilm_metrics = get_full_metrics_table(minilm_preds)

    # 5. Paired bootstrap for all requested comparisons (N_boot=1000, seed=42)
    # Target comparisons:
    # 2A: B1 vs B0 (B1 - B0)
    # 2B: B1-LR vs B0-LR (B1-LR - B0-LR)
    # 3A: B0-LR vs B0 (B0-LR - B0)
    # 3B: B1-LR vs B1 (B1-LR - B1)
    # 4:  B3 vs B1-LR (B3 - B1-LR)
    comparisons = [
        ("2A_filter_raw", "B1", "B0"),
        ("2B_filter_lr", "B1-LR", "B0-LR"),
        ("3A_lr_nofilt", "B0-LR", "B0"),
        ("3B_lr_filt", "B1-LR", "B1"),
        ("4_reverse_nli", "B3", "B1-LR"),
    ]

    bootstraps = {"mDeBERTa": {}, "MiniLM": {}}

    for tag, ma, mb in comparisons:
        # mDeBERTa: ma - mb
        bs_mdeb = paired_bootstrap_test(y_test, mdeberta_preds[ma], mdeberta_preds[mb], n_bootstraps=1000, seed=SEED)
        bootstraps["mDeBERTa"][f"{ma}_vs_{mb}"] = {
            "tag": tag,
            "method_a": ma,
            "method_b": mb,
            "accuracy": bs_mdeb["accuracy"],
            "macro_f1": bs_mdeb["macro_f1"],
            "supported_f1": bs_mdeb["supported_f1"],
            "fsr": bs_mdeb["fsr"],
        }

        # MiniLM: ma - mb
        bs_mini = paired_bootstrap_test(y_test, minilm_preds[ma], minilm_preds[mb], n_bootstraps=1000, seed=SEED)
        bootstraps["MiniLM"][f"{ma}_vs_{mb}"] = {
            "tag": tag,
            "method_a": ma,
            "method_b": mb,
            "accuracy": bs_mini["accuracy"],
            "macro_f1": bs_mini["macro_f1"],
            "supported_f1": bs_mini["supported_f1"],
            "fsr": bs_mini["fsr"],
        }

    out_data = {
        "mdeberta_metrics": mdeberta_metrics,
        "minilm_metrics": minilm_metrics,
        "bootstraps": bootstraps,
    }

    out_path = OUTPUTS_DIR / "cross_family_controlled_reevaluation.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_data, f, indent=2)

    print(f"Successfully computed and saved results to {out_path}")

    # Print summary tables
    print("\n" + "=" * 95)
    print("TABLE: mDeBERTa-v3-base FULL TEST METRICS")
    print("=" * 95)
    df_mdeb = pd.DataFrame(mdeberta_metrics).T[["tp", "fp", "tn", "fn", "accuracy", "macro_f1", "supp_p", "supp_r", "supp_f1", "fsr"]]
    print(df_mdeb.to_string())

    print("\n" + "=" * 95)
    print("TABLE: multilingual-MiniLMv2-L6 FULL TEST METRICS")
    print("=" * 95)
    df_mini = pd.DataFrame(minilm_metrics).T[["tp", "fp", "tn", "fn", "accuracy", "macro_f1", "supp_p", "supp_r", "supp_f1", "fsr"]]
    print(df_mini.to_string())

    print("\n" + "=" * 95)
    print("BOOTSTRAP RESULTS SUMMARY")
    print("=" * 95)
    for model_name in ["mDeBERTa", "MiniLM"]:
        print(f"\n--- {model_name} ---")
        for comp, res in bootstraps[model_name].items():
            print(f"Comparison: {comp} ({res['tag']})")
            print(f"  Delta Acc:      {res['accuracy']['mean_diff']:+.4f} [{res['accuracy']['ci_lower']:+.4f}, {res['accuracy']['ci_upper']:+.4f}]")
            print(f"  Delta Macro-F1: {res['macro_f1']['mean_diff']:+.4f} [{res['macro_f1']['ci_lower']:+.4f}, {res['macro_f1']['ci_upper']:+.4f}]")
            print(f"  Delta Supp-F1:  {res['supported_f1']['mean_diff']:+.4f} [{res['supported_f1']['ci_lower']:+.4f}, {res['supported_f1']['ci_upper']:+.4f}]")
            print(f"  Delta FSR:      {res['fsr']['mean_diff']:+.4f} [{res['fsr']['ci_lower']:+.4f}, {res['fsr']['ci_upper']:+.4f}]")

if __name__ == "__main__":
    main()
