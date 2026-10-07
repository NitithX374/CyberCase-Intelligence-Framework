import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix
import joblib

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from config import OUTPUTS_DIR, CACHE_DIR, SEED, set_seed
from src.datasets.wice import load_wice_split
from src.datasets.attributionbench import load_attributionbench_split
from src.fusion import FusionClassifier
from src.metrics import compute_classification_metrics

def load_cached_forward(cache_file: Path) -> np.ndarray:
    recs = [json.loads(line) for line in open(cache_file, "r", encoding="utf-8") if line.strip()]
    return np.array([[r["p_entailment"], r["p_neutral"], r["p_contradiction"]] for r in recs], dtype=np.float32)

def main():
    set_seed(SEED)
    print("=" * 80)
    print("COMPUTING B1-LR (FILTERED FORWARD 3D + LOGISTIC REGRESSION CONTROL)")
    print("=" * 80)

    # 1. Load WiCE Gold Labels
    train_ex = load_wice_split("train")
    dev_ex = load_wice_split("dev")
    test_ex = load_wice_split("test")

    y_train = np.array([ex.gold_label_binary for ex in train_ex])
    y_dev = np.array([ex.gold_label_binary for ex in dev_ex])
    y_test = np.array([ex.gold_label_binary for ex in test_ex])

    # 2. Load Filtered Forward Features (3D)
    tau_str = "0_20"
    train_f_filt = load_cached_forward(CACHE_DIR / "forward_nli" / f"train_forward_filt_{tau_str}.jsonl")
    dev_f_filt = load_cached_forward(CACHE_DIR / "forward_nli" / f"dev_forward_filt_{tau_str}.jsonl")
    test_f_filt = load_cached_forward(CACHE_DIR / "forward_nli" / f"test_forward_filt_{tau_str}.jsonl")

    print(f"Features loaded: Train {train_f_filt.shape}, Dev {dev_f_filt.shape}, Test {test_f_filt.shape}")

    # 3. Train B1-LR (Forward 3D Logistic Regression on Filtered Units)
    clf_b1_lr = FusionClassifier(C=1.0, class_weight="balanced", random_state=SEED)
    clf_b1_lr.fit(train_f_filt, y_train)

    # Save model
    joblib.dump(clf_b1_lr, OUTPUTS_DIR / "models" / "b1_lr_classifier.joblib")

    # Evaluate on WiCE DEV
    dev_b1_lr_preds = clf_b1_lr.predict(dev_f_filt)
    m_dev = compute_classification_metrics(y_dev, dev_b1_lr_preds)
    print(f"B1-LR DEV:  Acc={m_dev['accuracy']:.4f}, Macro-F1={m_dev['macro_f1']:.4f}, Supp-F1={m_dev['supported_f1']:.4f}, FSR={m_dev['false_support_rate']:.4f}")

    # Evaluate on WiCE TEST
    test_b1_lr_preds = clf_b1_lr.predict(test_f_filt)
    m_test = compute_classification_metrics(y_test, test_b1_lr_preds)
    tn, fp, fn, tp = confusion_matrix(y_test, test_b1_lr_preds, labels=[0, 1]).ravel()

    print(f"B1-LR TEST: Acc={m_test['accuracy']:.4f}, Macro-F1={m_test['macro_f1']:.4f}, Supp-F1={m_test['supported_f1']:.4f}, FSR={m_test['false_support_rate']:.4f}")
    print(f"B1-LR TEST CM: TP={tp}, FP={fp}, TN={tn}, FN={fn}")

    # 4. Compare Full WiCE Test Matrix: B0, B0-LR, B1, B1-LR, B2, B3
    df_preds = pd.read_csv(OUTPUTS_DIR / "wice_predictions.csv")
    y_b0 = df_preds["pred_B0"].values
    y_b0_lr = df_preds["pred_B0_LR"].values
    y_b1 = df_preds["pred_B1"].values
    y_b2 = df_preds["pred_B2"].values
    y_b3 = df_preds["pred_B3"].values
    y_b1_lr = test_b1_lr_preds

    # Paired Bootstrap between B3 and B1-LR (Isolating Reverse NLI with filtering constant)
    rng = np.random.default_rng(SEED)
    n_boot = 1000
    N = len(y_test)
    d_acc, d_mf1, d_sf1, d_fsr = [], [], [], []
    for _ in range(n_boot):
        idx = rng.integers(0, N, size=N)
        yt_s = y_test[idx]
        b3_s = y_b3[idx]
        b1lr_s = y_b1_lr[idx]

        d_acc.append(accuracy_score(yt_s, b3_s) - accuracy_score(yt_s, b1lr_s))
        d_mf1.append(
            f1_score(yt_s, b3_s, average="macro", zero_division=0)
            - f1_score(yt_s, b1lr_s, average="macro", zero_division=0)
        )
        d_sf1.append(
            f1_score(yt_s, b3_s, pos_label=1, zero_division=0)
            - f1_score(yt_s, b1lr_s, pos_label=1, zero_division=0)
        )
        neg = (yt_s == 0)
        fsr_b3 = np.sum((b3_s == 1) & neg) / np.sum(neg) if np.sum(neg) > 0 else 0.0
        fsr_b1lr = np.sum((b1lr_s == 1) & neg) / np.sum(neg) if np.sum(neg) > 0 else 0.0
        d_fsr.append(fsr_b3 - fsr_b1lr)

    print("\n" + "=" * 80)
    print("PAIRED BOOTSTRAP: B3 vs B1-LR (ISOLATING REVERSE NLI ON FILTERED PREMISES)")
    print("=" * 80)
    print(f"Delta Accuracy:     {np.mean(d_acc):+.2%} [{np.percentile(d_acc, 2.5):+.2%}, {np.percentile(d_acc, 97.5):+.2%}]")
    print(f"Delta Macro-F1:     {np.mean(d_mf1):+.4f} [{np.percentile(d_mf1, 2.5):+.4f}, {np.percentile(d_mf1, 97.5):+.4f}]")
    print(f"Delta Supported-F1: {np.mean(d_sf1):+.4f} [{np.percentile(d_sf1, 2.5):+.4f}, {np.percentile(d_sf1, 97.5):+.4f}]")
    print(f"Delta FSR:          {np.mean(d_fsr):+.2%} [{np.percentile(d_fsr, 2.5):+.2%}, {np.percentile(d_fsr, 97.5):+.2%}]")
    print(f"Macro-F1 Significant (CI excludes 0): {'YES' if np.percentile(d_mf1, 2.5) > 0 or np.percentile(d_mf1, 97.5) < 0 else 'NO'}")

    # 5. Evaluate B1-LR on AttributionBench ID and OOD
    print("\n" + "=" * 80)
    print("EVALUATING B1-LR ON ATTRIBUTIONBENCH (TRANSFER)")
    print("=" * 80)
    id_f_filt = load_cached_forward(CACHE_DIR / "forward_nli" / f"attrbench_id_forward_filt_{tau_str}.jsonl")
    ood_f_filt = load_cached_forward(CACHE_DIR / "forward_nli" / f"attrbench_ood_forward_filt_{tau_str}.jsonl")

    id_ex = load_attributionbench_split("id")
    ood_ex = load_attributionbench_split("ood")
    y_id = np.array([ex.gold_label_binary for ex in id_ex])
    y_ood = np.array([ex.gold_label_binary for ex in ood_ex])

    id_b1_lr_preds = clf_b1_lr.predict(id_f_filt)
    ood_b1_lr_preds = clf_b1_lr.predict(ood_f_filt)

    m_id_b1_lr = compute_classification_metrics(y_id, id_b1_lr_preds)
    m_ood_b1_lr = compute_classification_metrics(y_ood, ood_b1_lr_preds)

    print(f"B1-LR AttrBench ID:  Acc={m_id_b1_lr['accuracy']:.4f}, Macro-F1={m_id_b1_lr['macro_f1']:.4f}, Supp-F1={m_id_b1_lr['supported_f1']:.4f}, FSR={m_id_b1_lr['false_support_rate']:.4f}")
    print(f"B1-LR AttrBench OOD: Acc={m_ood_b1_lr['accuracy']:.4f}, Macro-F1={m_ood_b1_lr['macro_f1']:.4f}, Supp-F1={m_ood_b1_lr['supported_f1']:.4f}, FSR={m_ood_b1_lr['false_support_rate']:.4f}")

    # Save B1-LR to predictions CSV
    df_preds["pred_B1_LR"] = test_b1_lr_preds
    df_preds.to_csv(OUTPUTS_DIR / "wice_predictions.csv", index=False)

    out_json = {
        "b1_lr_wice_test": m_test,
        "b1_lr_wice_cm": {"tp": int(tp), "fp": int(fp), "tn": int(tn), "fn": int(fn)},
        "paired_b3_vs_b1_lr": {
            "delta_acc": float(np.mean(d_acc)),
            "delta_acc_ci": [float(np.percentile(d_acc, 2.5)), float(np.percentile(d_acc, 97.5))],
            "delta_mf1": float(np.mean(d_mf1)),
            "delta_mf1_ci": [float(np.percentile(d_mf1, 2.5)), float(np.percentile(d_mf1, 97.5))],
            "delta_sf1": float(np.mean(d_sf1)),
            "delta_sf1_ci": [float(np.percentile(d_sf1, 2.5)), float(np.percentile(d_sf1, 97.5))],
            "delta_fsr": float(np.mean(d_fsr)),
            "delta_fsr_ci": [float(np.percentile(d_fsr, 2.5)), float(np.percentile(d_fsr, 97.5))],
            "significant_mf1": bool(np.percentile(d_mf1, 2.5) > 0 or np.percentile(d_mf1, 97.5) < 0),
        },
        "b1_lr_attrbench_id": m_id_b1_lr,
        "b1_lr_attrbench_ood": m_ood_b1_lr,
    }
    json.dump(out_json, open(OUTPUTS_DIR / "b1_lr_audit.json", "w", encoding="utf-8"), indent=2)
    print("\nSaved B1-LR audit to outputs/b1_lr_audit.json")

if __name__ == "__main__":
    main()
