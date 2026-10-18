import json
import os
import subprocess
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix
import joblib

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from config import OUTPUTS_DIR, CACHE_DIR, SEED, set_seed
from src.datasets.wice import load_wice_split
from src.metrics import compute_classification_metrics
from src.bootstrap import paired_bootstrap_test
from src.fusion import tune_binary_threshold

def main():
    set_seed(SEED)
    print("=" * 90)
    print("CANONICAL FINAL AUDIT: LOCKED PROTOCOL & CONTROLLED CROSS-FAMILY VERIFICATION")
    print("=" * 90)

    # ---------------------------------------------------------
    # 1. LOAD & VERIFY DATASETS
    # ---------------------------------------------------------
    train_ex = load_wice_split("train")
    dev_ex = load_wice_split("dev")
    test_ex = load_wice_split("test")

    y_train = np.array([ex.gold_label_binary for ex in train_ex])
    y_dev = np.array([ex.gold_label_binary for ex in dev_ex])
    y_test = np.array([ex.gold_label_binary for ex in test_ex])

    print("Checking WiCE Split Counts:")
    print(f"  TRAIN: {len(y_train)} (Gold Pos={np.sum(y_train==1)}, Gold Neg={np.sum(y_train==0)})")
    print(f"  DEV:   {len(y_dev)} (Gold Pos={np.sum(y_dev==1)}, Gold Neg={np.sum(y_dev==0)})")
    print(f"  TEST:  {len(y_test)} (Gold Pos={np.sum(y_test==1)}, Gold Neg={np.sum(y_test==0)})")

    assert len(y_train) == 3750 and np.sum(y_train == 1) == 1377 and np.sum(y_train == 0) == 2373
    assert len(y_dev) == 1043 and np.sum(y_dev == 1) == 342 and np.sum(y_dev == 0) == 701
    assert len(y_test) == 1070 and np.sum(y_test == 1) == 330 and np.sum(y_test == 0) == 740
    print("  -> Label mapping & split counts VERIFIED.")

    # ---------------------------------------------------------
    # 2. LOAD FORWARD & REVERSE FEATURES
    # ---------------------------------------------------------
    # Helper to load cached JSONL probs
    def load_mdeberta_probs(split, filt_str="all"):
        if filt_str == "all":
            path = CACHE_DIR / "forward_nli" / f"{split}_forward_all.jsonl"
        else:
            path = CACHE_DIR / "forward_nli" / f"{split}_forward_filt_{filt_str}.jsonl"
        rows = [json.loads(l) for l in open(path, "r", encoding="utf-8") if l.strip()]
        return np.array([[r["p_entailment"], r["p_neutral"], r["p_contradiction"]] for r in rows], dtype=np.float32)

    def load_mdeberta_rev(split, filt_str="all"):
        if filt_str == "all":
            path = CACHE_DIR / "reverse_nli" / f"{split}_reverse_all.jsonl"
        else:
            path = CACHE_DIR / "reverse_nli" / f"{split}_reverse_filt_{filt_str}.jsonl"
        rows = [json.loads(l) for l in open(path, "r", encoding="utf-8") if l.strip()]
        return np.array([[r["p_entailment"], r["p_neutral"], r["p_contradiction"]] for r in rows], dtype=np.float32)

    # mDeBERTa features
    mdeb_train_full = load_mdeberta_probs("train", "all")
    mdeb_dev_full = load_mdeberta_probs("dev", "all")
    mdeb_test_full = load_mdeberta_probs("test", "all")

    mdeb_train_filt = load_mdeberta_probs("train", "0_20")
    mdeb_dev_filt = load_mdeberta_probs("dev", "0_20")
    mdeb_test_filt = load_mdeberta_probs("test", "0_20")

    mdeb_train_rev = load_mdeberta_rev("train", "0_20")
    mdeb_dev_rev = load_mdeberta_rev("dev", "0_20")
    mdeb_test_rev = load_mdeberta_rev("test", "0_20")

    # MiniLM features
    cache_mini = CACHE_DIR / "cross_family_minilm"
    mini_train_full = np.array([json.loads(l)["probs"] for l in open(cache_mini / "train_full_fwd_probs.jsonl") if l.strip()], dtype=np.float32)
    mini_dev_full = np.array([json.loads(l)["probs"] for l in open(cache_mini / "dev_full_fwd_probs.jsonl") if l.strip()], dtype=np.float32)
    mini_test_full = np.array([json.loads(l)["probs"] for l in open(cache_mini / "test_full_fwd_probs.jsonl") if l.strip()], dtype=np.float32)

    mini_train_filt = np.array([json.loads(l)["probs"] for l in open(cache_mini / "train_filt_fwd_probs.jsonl") if l.strip()], dtype=np.float32)
    mini_dev_filt = np.array([json.loads(l)["probs"] for l in open(cache_mini / "dev_filt_fwd_probs.jsonl") if l.strip()], dtype=np.float32)
    mini_test_filt = np.array([json.loads(l)["probs"] for l in open(cache_mini / "test_filt_fwd_probs.jsonl") if l.strip()], dtype=np.float32)

    mini_train_rev = np.array([json.loads(l)["probs"] for l in open(cache_mini / "train_filt_rev_probs.jsonl") if l.strip()], dtype=np.float32)
    mini_dev_rev = np.array([json.loads(l)["probs"] for l in open(cache_mini / "dev_filt_rev_probs.jsonl") if l.strip()], dtype=np.float32)
    mini_test_rev = np.array([json.loads(l)["probs"] for l in open(cache_mini / "test_filt_rev_probs.jsonl") if l.strip()], dtype=np.float32)

    # ---------------------------------------------------------
    # 3. TUNE DEV THRESHOLDS (STRICT DEV ONLY, ZERO TEST INSPECTION)
    # ---------------------------------------------------------
    print("\n--- Tuning 1D Decision Thresholds on DEV (P_entail >= theta) ---")
    # mDeBERTa:
    mdeb_th_b0, mdeb_dev_f1_b0 = tune_binary_threshold(y_dev, mdeb_dev_full[:, 0])
    mdeb_th_b1, mdeb_dev_f1_b1 = tune_binary_threshold(y_dev, mdeb_dev_filt[:, 0])
    print(f"mDeBERTa DEV B0 theta: {mdeb_th_b0:.4f} (DEV Macro-F1 = {mdeb_dev_f1_b0:.4f})")
    print(f"mDeBERTa DEV B1 theta: {mdeb_th_b1:.4f} (DEV Macro-F1 = {mdeb_dev_f1_b1:.4f})")

    # MiniLM:
    mini_th_b0, mini_dev_f1_b0 = tune_binary_threshold(y_dev, mini_dev_full[:, 0])
    mini_th_b1, mini_dev_f1_b1 = tune_binary_threshold(y_dev, mini_dev_filt[:, 0])
    print(f"MiniLM   DEV B0 theta: {mini_th_b0:.4f} (DEV Macro-F1 = {mini_dev_f1_b0:.4f})")
    print(f"MiniLM   DEV B1 theta: {mini_th_b1:.4f} (DEV Macro-F1 = {mini_dev_f1_b1:.4f})")

    # ---------------------------------------------------------
    # 4. TRAIN LOGISTIC REGRESSION (TRAIN SPLIT ONLY, ZERO LEAKAGE)
    # ---------------------------------------------------------
    print("\n--- Training Task-Specific Logistic Regression Heads (TRAIN ONLY) ---")
    # mDeBERTa LR models
    mdeb_clf_b0_lr = LogisticRegression(C=1.0, class_weight="balanced", random_state=SEED, max_iter=1000)
    mdeb_clf_b0_lr.fit(mdeb_train_full, y_train)

    mdeb_clf_b1_lr = LogisticRegression(C=1.0, class_weight="balanced", random_state=SEED, max_iter=1000)
    mdeb_clf_b1_lr.fit(mdeb_train_filt, y_train)

    mdeb_clf_b3 = LogisticRegression(C=1.0, class_weight="balanced", random_state=SEED, max_iter=1000)
    mdeb_clf_b3.fit(np.hstack([mdeb_train_filt, mdeb_train_rev]), y_train)

    # MiniLM LR models
    mini_clf_b0_lr = LogisticRegression(C=1.0, class_weight="balanced", random_state=SEED, max_iter=1000)
    mini_clf_b0_lr.fit(mini_train_full, y_train)

    mini_clf_b1_lr = LogisticRegression(C=1.0, class_weight="balanced", random_state=SEED, max_iter=1000)
    mini_clf_b1_lr.fit(mini_train_filt, y_train)

    mini_clf_b3 = LogisticRegression(C=1.0, class_weight="balanced", random_state=SEED, max_iter=1000)
    mini_clf_b3.fit(np.hstack([mini_train_filt, mini_train_rev]), y_train)

    # Print B1-LR coefficients
    print(f"mDeBERTa B1-LR Weights [w_E, w_N, w_C]: {mdeb_clf_b1_lr.coef_[0]}, Intercept: {mdeb_clf_b1_lr.intercept_[0]}")
    print(f"MiniLM   B1-LR Weights [w_E, w_N, w_C]: {mini_clf_b1_lr.coef_[0]}, Intercept: {mini_clf_b1_lr.intercept_[0]}")

    # ---------------------------------------------------------
    # 5. PREDICT ON HELD-OUT TEST SPLIT
    # ---------------------------------------------------------
    # Canonical Predictions under Protocol 1 (DEV-tuned threshold for B0, B1)
    mdeb_preds = {
        "B0": (mdeb_test_full[:, 0] >= mdeb_th_b0).astype(int),
        "B0-LR": mdeb_clf_b0_lr.predict(mdeb_test_full),
        "B1": (mdeb_test_filt[:, 0] >= mdeb_th_b1).astype(int),
        "B1-LR": mdeb_clf_b1_lr.predict(mdeb_test_filt),
        "B3": mdeb_clf_b3.predict(np.hstack([mdeb_test_filt, mdeb_test_rev])),
    }

    mini_preds = {
        "B0": (mini_test_full[:, 0] >= mini_th_b0).astype(int),
        "B0-LR": mini_clf_b0_lr.predict(mini_test_full),
        "B1": (mini_test_filt[:, 0] >= mini_th_b1).astype(int),
        "B1-LR": mini_clf_b1_lr.predict(mini_test_filt),
        "B3": mini_clf_b3.predict(np.hstack([mini_test_filt, mini_test_rev])),
    }

    # Naive Argmax predictions for documentation / ablation contrast
    mdeb_preds_argmax = {
        "B0_argmax": (np.argmax(mdeb_test_full, axis=1) == 0).astype(int),
        "B1_argmax": (np.argmax(mdeb_test_filt, axis=1) == 0).astype(int),
    }
    mini_preds_argmax = {
        "B0_argmax": (np.argmax(mini_test_full, axis=1) == 0).astype(int),
        "B1_argmax": (np.argmax(mini_test_filt, axis=1) == 0).astype(int),
    }

    # ---------------------------------------------------------
    # 6. COMPUTE FULL CONFUSION MATRICES & METRICS
    # ---------------------------------------------------------
    def evaluate_all(preds_dict):
        metrics_out = {}
        for name, p in preds_dict.items():
            tp = int(np.sum((p == 1) & (y_test == 1)))
            fp = int(np.sum((p == 1) & (y_test == 0)))
            tn = int(np.sum((p == 0) & (y_test == 0)))
            fn = int(np.sum((p == 0) & (y_test == 1)))

            assert tp + fp + tn + fn == 1070
            assert tp + fn == 330
            assert tn + fp == 740

            acc = (tp + tn) / 1070.0
            supp_p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            supp_r = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            supp_f1 = 2 * supp_p * supp_r / (supp_p + supp_r) if (supp_p + supp_r) > 0 else 0.0

            unsupp_p = tn / (tn + fn) if (tn + fn) > 0 else 0.0
            unsupp_r = tn / (tn + fp) if (tn + fp) > 0 else 0.0
            unsupp_f1 = 2 * unsupp_p * unsupp_r / (unsupp_p + unsupp_r) if (unsupp_p + unsupp_r) > 0 else 0.0

            macro_f1 = (supp_f1 + unsupp_f1) / 2.0
            fsr = fp / (tn + fp)  # Exact mathematical definition: FP / (FP + TN)

            metrics_out[name] = {
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
        return metrics_out

    mdeb_metrics = evaluate_all(mdeb_preds)
    mini_metrics = evaluate_all(mini_preds)
    mdeb_argmax_metrics = evaluate_all(mdeb_preds_argmax)
    mini_argmax_metrics = evaluate_all(mini_preds_argmax)

    # ---------------------------------------------------------
    # 7. RUN PAIRED BOOTSTRAP (N_boot=1000, seed=42, same indices)
    # ---------------------------------------------------------
    comparisons = [
        ("filter_1d_thresh", "B1", "B0"),
        ("filter_3d_lr", "B1-LR", "B0-LR"),
        ("lr_nofilt", "B0-LR", "B0"),
        ("lr_filt", "B1-LR", "B1"),
        ("reverse_nli", "B3", "B1-LR"),
    ]

    bootstraps = {"mDeBERTa": {}, "MiniLM": {}}
    for tag, ma, mb in comparisons:
        bootstraps["mDeBERTa"][f"{ma}_vs_{mb}"] = {
            "tag": tag,
            "method_a": ma,
            "method_b": mb,
            **paired_bootstrap_test(y_test, mdeb_preds[ma], mdeb_preds[mb], n_bootstraps=1000, seed=SEED),
        }
        bootstraps["MiniLM"][f"{ma}_vs_{mb}"] = {
            "tag": tag,
            "method_a": ma,
            "method_b": mb,
            **paired_bootstrap_test(y_test, mini_preds[ma], mini_preds[mb], n_bootstraps=1000, seed=SEED),
        }

    # ---------------------------------------------------------
    # 8. EXPORT CANONICAL SOURCE-OF-TRUTH ARTIFACTS
    # ---------------------------------------------------------
    canon_dir = OUTPUTS_DIR / "canonical"
    canon_dir.mkdir(parents=True, exist_ok=True)

    # 8.1 Final Predictions CSV
    df_preds = pd.DataFrame({
        "example_id": [ex.example_id for ex in test_ex],
        "claim_id": [ex.claim_id for ex in test_ex],
        "gold_label_binary": y_test,
        "mdeberta_pred_B0": mdeb_preds["B0"],
        "mdeberta_pred_B0_LR": mdeb_preds["B0-LR"],
        "mdeberta_pred_B1": mdeb_preds["B1"],
        "mdeberta_pred_B1_LR": mdeb_preds["B1-LR"],
        "mdeberta_pred_B3": mdeb_preds["B3"],
        "minilm_pred_B0": mini_preds["B0"],
        "minilm_pred_B0_LR": mini_preds["B0-LR"],
        "minilm_pred_B1": mini_preds["B1"],
        "minilm_pred_B1_LR": mini_preds["B1-LR"],
        "minilm_pred_B3": mini_preds["B3"],
    })
    df_preds.to_csv(canon_dir / "final_predictions.csv", index=False)

    # 8.2 Final Metrics JSON
    final_metrics_data = {
        "protocol": "Strict DEV-Tuned Threshold on P(E) for B0/B1; TRAIN-fit Logistic Regression for B0-LR/B1-LR/B3",
        "dataset": "WiCE Claim Verification (Held-out Test Split, N=1070)",
        "fsr_formula": "FP / (FP + TN) [False Positive Rate over Gold Negatives]",
        "mdeberta": mdeb_metrics,
        "minilm": mini_metrics,
        "mdeberta_argmax_ablation": mdeb_argmax_metrics,
        "minilm_argmax_ablation": mini_argmax_metrics,
    }
    with open(canon_dir / "final_metrics.json", "w", encoding="utf-8") as f:
        json.dump(final_metrics_data, f, indent=2)

    # 8.3 Final Bootstrap JSON
    with open(canon_dir / "final_bootstrap.json", "w", encoding="utf-8") as f:
        json.dump(bootstraps, f, indent=2)

    # 8.4 Final Thresholds JSON
    final_thresholds = {
        "mdeberta": {
            "b0_theta": mdeb_th_b0,
            "b1_theta": mdeb_th_b1,
            "semantic_tau": 0.20,
        },
        "minilm": {
            "b0_theta": mini_th_b0,
            "b1_theta": mini_th_b1,
            "semantic_tau": 0.20,
        },
    }
    with open(canon_dir / "final_thresholds.json", "w", encoding="utf-8") as f:
        json.dump(final_thresholds, f, indent=2)

    # 8.5 Final LR Coefficients JSON
    final_lr_coefs = {
        "mdeberta_b1_lr": {
            "features": ["P_entailment", "P_neutral", "P_contradiction"],
            "weights": mdeb_clf_b1_lr.coef_[0].tolist(),
            "intercept": float(mdeb_clf_b1_lr.intercept_[0]),
            "C": float(mdeb_clf_b1_lr.C),
            "class_weight": "balanced",
            "solver": "lbfgs",
            "seed": SEED,
        },
        "minilm_b1_lr": {
            "features": ["P_entailment", "P_neutral", "P_contradiction"],
            "weights": mini_clf_b1_lr.coef_[0].tolist(),
            "intercept": float(mini_clf_b1_lr.intercept_[0]),
            "C": float(mini_clf_b1_lr.C),
            "class_weight": "balanced",
            "solver": "lbfgs",
            "seed": SEED,
        },
    }
    with open(canon_dir / "final_lr_coefficients.json", "w", encoding="utf-8") as f:
        json.dump(final_lr_coefs, f, indent=2)

    # 8.6 Experiment Config & Metadata
    try:
        git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(BASE_DIR)).decode("utf-8").strip()
    except Exception:
        git_sha = "unknown"

    import sklearn
    import transformers
    import torch

    config_metadata = {
        "seed": SEED,
        "git_commit_sha": git_sha,
        "n_bootstraps": 1000,
        "backbone_primary": "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7",
        "backbone_post_hoc_sensitivity": "MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli",
        "sentence_embedding_model": "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        "semantic_tau": 0.20,
        "nli_max_length": 512,
        "package_versions": {
            "python": sys.version,
            "torch": torch.__version__,
            "transformers": transformers.__version__,
            "sklearn": sklearn.__version__,
            "numpy": np.__version__,
            "pandas": pd.__version__,
        },
    }
    with open(canon_dir / "experiment_config.json", "w", encoding="utf-8") as f:
        json.dump(config_metadata, f, indent=2)

    print(f"\nAll Canonical Source-of-Truth artifacts successfully saved to {canon_dir}")

    # ---------------------------------------------------------
    # PRINT PRETTY TABLES
    # ---------------------------------------------------------
    print("\n" + "=" * 105)
    print("CANONICAL HELD-OUT TEST METRICS (Protocol 1: DEV-Tuned Threshold for B0/B1)")
    print("=" * 105)

    def print_table(title, metrics_dict):
        print(f"\n--- {title} ---")
        rows = []
        for k, v in metrics_dict.items():
            rows.append({
                "Method": k,
                "TP": v["tp"],
                "FP": v["fp"],
                "TN": v["tn"],
                "FN": v["fn"],
                "Acc": f"{v['accuracy']:.2%}",
                "Macro-F1": f"{v['macro_f1']:.4f}",
                "Supp-P": f"{v['supp_p']:.2%}",
                "Supp-R": f"{v['supp_r']:.2%}",
                "Supp-F1": f"{v['supp_f1']:.4f}",
                "FSR": f"{v['fsr']:.2%}",
            })
        print(pd.DataFrame(rows).to_string(index=False))

    print_table("mDeBERTa-v3-base (Primary Official Champion)", mdeb_metrics)
    print_table("multilingual-MiniLMv2-L6 (Post-Hoc Backbone Sensitivity)", mini_metrics)

    print("\n" + "=" * 105)
    print("BOOTSTRAP 95% CONFIDENCE INTERVALS (Paired Bootstrap N=1000, seed=42)")
    print("=" * 105)
    for model_name in ["mDeBERTa", "MiniLM"]:
        print(f"\n--- {model_name} ---")
        for comp, res in bootstraps[model_name].items():
            d_mf1 = res["macro_f1"]
            d_sf1 = res["supported_f1"]
            d_fsr = res["fsr"]
            d_acc = res["accuracy"]
            sig_mf1 = "YES" if (d_mf1["ci_lower"] > 0 or d_mf1["ci_upper"] < 0) else "NO"
            print(f"{comp:18s} ({res['tag']:18s}): "
                  f"Delta Macro-F1 = {d_mf1['mean_diff']:+.4f} [{d_mf1['ci_lower']:+.4f}, {d_mf1['ci_upper']:+.4f}] (Sig={sig_mf1:3s}) | "
                  f"Delta Supp-F1 = {d_sf1['mean_diff']:+.4f} [{d_sf1['ci_lower']:+.4f}, {d_sf1['ci_upper']:+.4f}] | "
                  f"Delta FSR = {d_fsr['mean_diff']:+.2%} [{d_fsr['ci_lower']:+.2%}, {d_fsr['ci_upper']:+.2%}]")

if __name__ == "__main__":
    main()
