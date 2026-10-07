import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import beta
from sklearn.metrics import confusion_matrix, accuracy_score, f1_score
import joblib

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from config import OUTPUTS_DIR, CACHE_DIR
from src.datasets.attributionbench import load_attributionbench_split
from src.metrics import compute_classification_metrics
from src.calibration import evaluate_selective_prediction

def clopper_pearson_ci(k: int, n: int, confidence: float = 0.95) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    alpha = 1.0 - confidence
    lower = 0.0 if k == 0 else beta.ppf(alpha / 2, k, n - k + 1)
    upper = 1.0 if k == n else beta.ppf(1 - alpha / 2, k + 1, n - k)
    return float(lower), float(upper)

def audit_split(split_name: str):
    print("=" * 80)
    print(f"AUDITING ATTRIBUTIONBENCH {split_name.upper()}")
    print("=" * 80)
    examples = load_attributionbench_split(split_name)
    y_true = np.array([ex.gold_label_binary for ex in examples])
    N = len(y_true)
    n_pos = int(np.sum(y_true == 1))
    n_neg = int(np.sum(y_true == 0))
    print(f"Total Examples: {N}, Gold Positive: {n_pos}, Gold Negative: {n_neg}")

    thresholds = json.load(open(OUTPUTS_DIR / "wice_thresholds.json"))
    clf_b3 = joblib.load(OUTPUTS_DIR / "models" / "b3_classifier.joblib")
    scaler_b4 = joblib.load(OUTPUTS_DIR / "models" / "b4_scaler.joblib")

    def load_c(path):
        recs = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
        return np.array([[r["p_entailment"], r["p_neutral"], r["p_contradiction"]] for r in recs])

    f_all_p = CACHE_DIR / "forward_nli" / f"attrbench_{split_name}_forward_all.jsonl"
    f_filt_p = CACHE_DIR / "forward_nli" / f"attrbench_{split_name}_forward_filt_0_20.jsonl"
    r_filt_p = CACHE_DIR / "reverse_nli" / f"attrbench_{split_name}_reverse_filt_0_20.jsonl"

    if not (f_all_p.exists() and f_filt_p.exists() and r_filt_p.exists()):
        print(f"Cache files for {split_name} not fully ready yet.")
        return None

    f_all = load_c(f_all_p)
    f_filt = load_c(f_filt_p)
    r_filt = load_c(r_filt_p)

    b0_pred = (f_all[:, 0] >= thresholds["b0_threshold"]).astype(int)
    b1_pred = (f_filt[:, 0] >= thresholds["b1_support_threshold"]).astype(int)
    X_6d = np.hstack([f_filt, r_filt])
    b3_pred = clf_b3.predict(X_6d)

    logits_b3 = clf_b3.decision_function(X_6d)
    p_cal = scaler_b4.predict_proba(logits_b3)[:, 1]
    t_low = thresholds["b4_t_low"]
    t_high = thresholds["b4_t_high"]
    b4_res = evaluate_selective_prediction(p_cal, y_true, t_low, t_high)

    methods = [("B0", b0_pred), ("B1", b1_pred), ("B3", b3_pred)]
    cm_rows = []
    for m_name, yp in methods:
        tn, fp, fn, tp = confusion_matrix(y_true, yp, labels=[0, 1]).ravel()
        acc = (tp + tn) / N
        sp = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        sr = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        sf1 = (2 * sp * sr) / (sp + sr) if (sp + sr) > 0 else 0.0
        fsr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        f1_neg = (2 * tn) / (2 * tn + fp + fn) if (2 * tn + fp + fn) > 0 else 0.0
        mf1 = (sf1 + f1_neg) / 2.0
        cm_rows.append({
            "Method": m_name,
            "TP": int(tp), "FP": int(fp), "TN": int(tn), "FN": int(fn),
            "Accuracy": acc, "Macro-F1": mf1, "Supp-F1": sf1, "FSR": fsr
        })
    df_cm = pd.DataFrame(cm_rows)
    print(df_cm.to_string(index=False))

    # B4 details
    pred_b4 = b4_res["predictions"]
    retained_mask = (pred_b4 != -1)
    n_ret = int(np.sum(retained_mask))
    n_abst = int(np.sum(~retained_mask))
    y_ret = y_true[retained_mask]
    p_ret = pred_b4[retained_mask]

    ret_tp = int(np.sum((p_ret == 1) & (y_ret == 1)))
    ret_fp = int(np.sum((p_ret == 1) & (y_ret == 0)))
    ret_tn = int(np.sum((p_ret == 0) & (y_ret == 0)))
    ret_fn = int(np.sum((p_ret == 0) & (y_ret == 1)))
    n_ret_neg = int(np.sum(y_ret == 0))

    ret_fsr = ret_fp / n_ret_neg if n_ret_neg > 0 else 0.0
    cp_low, cp_high = clopper_pearson_ci(ret_fp, n_ret_neg)
    rule_of_three = 3.0 / n_ret_neg if n_ret_neg > 0 else 1.0

    adm_count = int(np.sum(pred_b4 == 1))
    adm_rate = adm_count / N
    adm_prec = ret_tp / adm_count if adm_count > 0 else 0.0
    supp_adm_recall = ret_tp / n_pos

    print(f"\nB4 Retained Metrics on {split_name.upper()}:")
    print(f"Retained Count: {n_ret} ({n_ret/N:.4%}), Abstained: {n_abst} ({n_abst/N:.4%})")
    print(f"Retained CM: TP={ret_tp}, FP={ret_fp}, TN={ret_tn}, FN={ret_fn}")
    print(f"Selective Accuracy: {b4_res['selective_accuracy']:.4%}, Selective Risk: {b4_res['selective_risk']:.4%}")
    print(f"Retained False Support Rate: {ret_fsr:.4%}")
    print(f"Clopper-Pearson 95% CI on Retained FSR: [{cp_low:.4%}, {cp_high:.4%}]")
    print(f"Rule of Three Upper Bound: {rule_of_three:.4%}")
    print(f"Admission Count (pred=SUPPORTED): {adm_count}")
    print(f"Admission Rate: {adm_rate:.4%}")
    print(f"Admission Precision: {adm_prec:.4%}")
    print(f"Supported Admission Recall: {supp_adm_recall:.4%}")

    return {
        "split": split_name,
        "cm": cm_rows,
        "b4": {
            "n_retained": n_ret,
            "n_abstained": n_abst,
            "ret_tp": ret_tp, "ret_fp": ret_fp, "ret_tn": ret_tn, "ret_fn": ret_fn,
            "selective_acc": b4_res["selective_accuracy"],
            "selective_risk": b4_res["selective_risk"],
            "ret_fsr": ret_fsr,
            "cp_ci": [cp_low, cp_high],
            "rule_of_three": rule_of_three,
            "admission_count": adm_count,
            "admission_rate": adm_rate,
            "admission_precision": adm_prec,
            "supp_adm_recall": supp_adm_recall,
        }
    }

if __name__ == "__main__":
    audit_split("id")
    audit_split("ood")
