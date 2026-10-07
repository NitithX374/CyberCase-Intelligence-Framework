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
from src.metrics import compute_classification_metrics
from src.fusion import FusionClassifier

def paired_bootstrap(y_true, y_a, y_b, n_boot=1000, seed=SEED):
    rng = np.random.default_rng(seed)
    n = len(y_true)
    d_acc, d_mf1, d_sf1, d_fsr = [], [], [], []
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        yt_s, ya_s, yb_s = y_true[idx], y_a[idx], y_b[idx]

        d_acc.append(accuracy_score(yt_s, ya_s) - accuracy_score(yt_s, yb_s))
        d_mf1.append(
            f1_score(yt_s, ya_s, average="macro", zero_division=0)
            - f1_score(yt_s, yb_s, average="macro", zero_division=0)
        )
        d_sf1.append(
            f1_score(yt_s, ya_s, pos_label=1, zero_division=0)
            - f1_score(yt_s, yb_s, pos_label=1, zero_division=0)
        )
        neg = (yt_s == 0)
        fsr_a = np.sum((ya_s == 1) & neg) / np.sum(neg) if np.sum(neg) > 0 else 0.0
        fsr_b = np.sum((yb_s == 1) & neg) / np.sum(neg) if np.sum(neg) > 0 else 0.0
        d_fsr.append(fsr_a - fsr_b)

    return {
        "d_acc": (float(np.mean(d_acc)), float(np.percentile(d_acc, 2.5)), float(np.percentile(d_acc, 97.5))),
        "d_mf1": (float(np.mean(d_mf1)), float(np.percentile(d_mf1, 2.5)), float(np.percentile(d_mf1, 97.5))),
        "d_sf1": (float(np.mean(d_sf1)), float(np.percentile(d_sf1, 2.5)), float(np.percentile(d_sf1, 97.5))),
        "d_fsr": (float(np.mean(d_fsr)), float(np.percentile(d_fsr, 2.5)), float(np.percentile(d_fsr, 97.5))),
    }

def main():
    set_seed(SEED)
    print("=" * 80)
    print("STAGE 1: VERIFY B1-LR & ESTABLISH INITIAL CHAMPION BASELINE")
    print("=" * 80)

    # Load test gold
    test_ex = load_wice_split("test")
    y_test = np.array([ex.gold_label_binary for ex in test_ex])

    # Load predictions
    df_preds = pd.read_csv(OUTPUTS_DIR / "wice_predictions.csv")
    y_b0 = df_preds["pred_B0"].values
    y_b0lr = df_preds["pred_B0_LR"].values
    y_b1 = df_preds["pred_B1"].values
    y_b1lr = df_preds["pred_B1_LR"].values
    y_b3 = df_preds["pred_B3"].values

    # 1. B1-LR Confusion Matrix & Core Metrics
    tn, fp, fn, tp = confusion_matrix(y_test, y_b1lr, labels=[0, 1]).ravel()
    acc = (tp + tn) / len(y_test)
    sp = tp / (tp + fp)
    sr = tp / (tp + fn)
    sf1 = (2 * sp * sr) / (sp + sr)
    f1_neg = (2 * tn) / (2 * tn + fp + fn)
    mf1 = (sf1 + f1_neg) / 2.0
    fsr = fp / (fp + tn)

    print("B1-LR WiCE TEST Performance:")
    print(f"Confusion Matrix: TP={tp}, FP={fp}, TN={tn}, FN={fn} (Total={len(y_test)})")
    print(f"Accuracy:           {acc:.4%} ({acc:.6f})")
    print(f"Macro-F1:           {mf1:.4f}")
    print(f"Supported Precision:{sp:.4%}")
    print(f"Supported Recall:   {sr:.4%}")
    print(f"Supported F1:       {sf1:.4f}")
    print(f"False Support Rate: {fsr:.4%}")

    # 2. Paired Bootstrap vs B0, B0-LR, B1, B3
    comparisons = [
        ("B1-LR vs B0", y_b1lr, y_b0),
        ("B1-LR vs B0-LR", y_b1lr, y_b0lr),
        ("B1-LR vs B1", y_b1lr, y_b1),
        ("B1-LR vs B3", y_b1lr, y_b3),
    ]

    boot_rows = []
    for comp_name, ya, yb in comparisons:
        res = paired_bootstrap(y_test, ya, yb)
        boot_rows.append({
            "Comparison": comp_name,
            "Delta Accuracy": f"{res['d_acc'][0]:+.2%} [{res['d_acc'][1]:+.2%}, {res['d_acc'][2]:+.2%}]",
            "Delta Macro-F1": f"{res['d_mf1'][0]:+.4f} [{res['d_mf1'][1]:+.4f}, {res['d_mf1'][2]:+.4f}]",
            "Delta Supported-F1": f"{res['d_sf1'][0]:+.4f} [{res['d_sf1'][1]:+.4f}, {res['d_sf1'][2]:+.4f}]",
            "Delta FSR": f"{res['d_fsr'][0]:+.2%} [{res['d_fsr'][1]:+.2%}, {res['d_fsr'][2]:+.2%}]",
            "Macro-F1 Sig?": "YES" if (res['d_mf1'][1] > 0 or res['d_mf1'][2] < 0) else "NO",
            "Supp-F1 Sig?": "YES" if (res['d_sf1'][1] > 0 or res['d_sf1'][2] < 0) else "NO",
            "FSR Sig?": "YES" if (res['d_fsr'][1] > 0 or res['d_fsr'][2] < 0) else "NO",
        })

    df_boot = pd.DataFrame(boot_rows)
    print("\nPaired Bootstrap Results (B1-LR vs Baselines, N=1000, Seed=42):")
    print(df_boot.to_string(index=False))

    # Save to disk
    out_dict = {
        "b1_lr_metrics": {
            "tp": int(tp), "fp": int(fp), "tn": int(tn), "fn": int(fn),
            "accuracy": acc, "macro_f1": mf1, "supp_p": sp, "supp_r": sr, "supp_f1": sf1, "fsr": fsr
        },
        "paired_bootstrap": boot_rows
    }
    json.dump(out_dict, open(OUTPUTS_DIR / "stage1_b1_lr_verification.json", "w", encoding="utf-8"), indent=2)

if __name__ == "__main__":
    main()
