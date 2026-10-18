from typing import Any
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix

def compute_classification_metrics(y_true: list[int] | np.ndarray, y_pred: list[int] | np.ndarray) -> dict[str, Any]:
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    
    acc = float(accuracy_score(y_true, y_pred))
    macro_f1 = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
    supp_p = float(precision_score(y_true, y_pred, pos_label=1, zero_division=0))
    supp_r = float(recall_score(y_true, y_pred, pos_label=1, zero_division=0))
    supp_f1 = float(f1_score(y_true, y_pred, pos_label=1, zero_division=0))
    
    # Confusion matrix
    # Format: [[TN, FP], [FN, TP]]
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    
    # False Support Rate = FP / (TN + FP)
    # The proportion of actual negative examples that were falsely predicted as SUPPORTED (1)
    neg_total = tn + fp
    fsr = float(fp / neg_total) if neg_total > 0 else 0.0

    return {
        "accuracy": acc,
        "macro_f1": macro_f1,
        "supported_precision": supp_p,
        "supported_recall": supp_r,
        "supported_f1": supp_f1,
        "false_support_rate": fsr,
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
        "total": len(y_true),
    }

def compute_bootstrap_ci(
    y_true: list[int] | np.ndarray,
    y_pred: list[int] | np.ndarray,
    metric_fn,
    n_bootstraps: int = 1000,
    seed: int = 42,
    alpha: float = 0.05,
) -> tuple[float, float]:
    rng = np.random.RandomState(seed)
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    n = len(y_true)
    
    boot_scores: list[float] = []
    for _ in range(n_bootstraps):
        indices = rng.randint(0, n, size=n)
        score = metric_fn(y_true[indices], y_pred[indices])
        boot_scores.append(score)
        
    lower = float(np.percentile(boot_scores, 100 * (alpha / 2)))
    upper = float(np.percentile(boot_scores, 100 * (1 - alpha / 2)))
    return lower, upper

def compute_evidence_retrieval_metrics(
    gold_indices_list: list[list[int]],
    selected_indices_list: list[list[int]],
) -> dict[str, float]:
    """
    Computes precision, recall, and F1 over retrieved/filtered evidence units
    for examples that have gold supporting sentence IDs.
    """
    precisions: list[float] = []
    recalls: list[float] = []
    f1s: list[float] = []
    
    for gold, selected in zip(gold_indices_list, selected_indices_list):
        if not gold:
            continue
        gold_set = set(gold)
        sel_set = set(selected)
        
        tp = len(gold_set.intersection(sel_set))
        p = tp / len(sel_set) if len(sel_set) > 0 else 0.0
        r = tp / len(gold_set) if len(gold_set) > 0 else 0.0
        f1 = (2 * p * r) / (p + r) if (p + r) > 0 else 0.0
        
        precisions.append(p)
        recalls.append(r)
        f1s.append(f1)
        
    return {
        "evidence_precision": float(np.mean(precisions)) if precisions else 0.0,
        "evidence_recall": float(np.mean(recalls)) if recalls else 0.0,
        "evidence_f1": float(np.mean(f1s)) if f1s else 0.0,
    }

def compute_aurc(risks: list[float], coverages: list[float]) -> float:
    """
    Area Under Risk-Coverage curve.
    Uses trapezoidal integration over coverages sorted ascendingly.
    """
    if len(coverages) < 2:
        return 0.0
    # Sort by coverage ascending
    sorted_pairs = sorted(zip(coverages, risks), key=lambda x: x[0])
    covs = [p[0] for p in sorted_pairs]
    rs = [p[1] for p in sorted_pairs]
    return float(np.trapezoid(rs, covs))
