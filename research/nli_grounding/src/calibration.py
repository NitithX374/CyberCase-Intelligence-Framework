from typing import Any
import numpy as np
from scipy.optimize import minimize
from sklearn.metrics import log_loss, accuracy_score

from src.metrics import compute_aurc

class TemperatureScaler:
    """
    Temperature scaling for binary decision logits:
    p = sigmoid(z / T)
    Optimizes T on DEV by minimizing Binary Cross-Entropy (NLL).
    """
    def __init__(self):
        self.temperature = 1.0

    def fit(self, logits: np.ndarray, y_true: np.ndarray) -> "TemperatureScaler":
        logits = np.asarray(logits, dtype=np.float64)
        y_true = np.asarray(y_true, dtype=np.float64)

        def nll_objective(t_arr):
            t = t_arr[0]
            scaled = logits / max(t, 1e-6)
            # Clip for numerical stability
            scaled = np.clip(scaled, -30.0, 30.0)
            probs = 1.0 / (1.0 + np.exp(-scaled))
            probs = np.clip(probs, 1e-7, 1.0 - 1e-7)
            return log_loss(y_true, probs)

        res = minimize(nll_objective, x0=[1.0], bounds=[(0.01, 10.0)], method="L-BFGS-B")
        self.temperature = float(res.x[0])
        return self

    def predict_proba(self, logits: np.ndarray) -> np.ndarray:
        logits = np.asarray(logits, dtype=np.float64)
        scaled = logits / max(self.temperature, 1e-6)
        scaled = np.clip(scaled, -30.0, 30.0)
        p1 = 1.0 / (1.0 + np.exp(-scaled))
        return np.column_stack([1.0 - p1, p1])

def select_abstention_thresholds(
    p_support_dev: np.ndarray,
    y_dev: np.ndarray,
    target_risk: float = 0.05,
    min_retained: int = 30,
    resolution: int = 101,
) -> tuple[float, float, dict[str, Any]]:
    """
    Selects T_low and T_high on DEV to maximize coverage subject to selective error <= target_risk.
    
    Decision rule:
        p >= T_high -> 1 (SUPPORTED)
        p <= T_low  -> 0 (UNSUPPORTED)
        otherwise   -> ABSTAIN

    Requires at least min_retained examples (default 30) to prevent single-sample edge cases.
    If no threshold pair can achieve target_risk, falls back to the best achievable risk/coverage tradeoff.
    """
    threshold_grid = np.linspace(0.0, 1.0, resolution)
    best_coverage = -1.0
    best_pair = (0.5, 0.5)
    best_stats = {}

    lowest_risk = 1.0
    fallback_pair = (0.5, 0.5)
    fallback_stats = {}

    n = len(y_dev)

    for i, t_low in enumerate(threshold_grid):
        for t_high in threshold_grid[i:]:
            # Retained mask
            is_supp = p_support_dev >= t_high
            is_unsupp = p_support_dev <= t_low
            retained = is_supp | is_unsupp

            n_retained = int(np.sum(retained))
            if n_retained < min_retained:
                continue

            cov = n_retained / n
            y_ret = y_dev[retained]
            preds_ret = np.where(is_supp[retained], 1, 0)

            acc = float(accuracy_score(y_ret, preds_ret))
            risk = 1.0 - acc

            # False support rate among retained
            neg_mask = (y_ret == 0)
            n_neg = int(np.sum(neg_mask))
            fp = int(np.sum((preds_ret == 1) & neg_mask))
            fsr = (fp / n_neg) if n_neg > 0 else 0.0

            stats = {
                "coverage": cov,
                "selective_accuracy": acc,
                "selective_risk": risk,
                "false_support_rate": fsr,
                "n_retained": n_retained,
                "n_abstained": n - n_retained,
            }

            # Track lowest risk achievable as fallback (prefer higher coverage if risk is tied)
            if risk < lowest_risk or (risk == lowest_risk and cov > fallback_stats.get("coverage", 0)):
                lowest_risk = risk
                fallback_pair = (float(t_low), float(t_high))
                fallback_stats = stats

            # Primary objective: maximize coverage subject to risk <= target_risk
            if risk <= target_risk:
                if cov > best_coverage:
                    best_coverage = cov
                    best_pair = (float(t_low), float(t_high))
                    best_stats = stats

    if best_coverage >= 0.0:
        return best_pair[0], best_pair[1], best_stats
    else:
        # Fallback to best achievable risk/coverage tradeoff
        return fallback_pair[0], fallback_pair[1], fallback_stats

def evaluate_selective_prediction(
    p_support: np.ndarray,
    y_true: np.ndarray,
    t_low: float,
    t_high: float,
) -> dict[str, Any]:
    n = len(y_true)
    is_supp = p_support >= t_high
    is_unsupp = p_support <= t_low
    retained = is_supp | is_unsupp

    n_retained = int(np.sum(retained))
    n_abstained = n - n_retained
    coverage = n_retained / n if n > 0 else 0.0

    if n_retained > 0:
        y_ret = y_true[retained]
        preds_ret = np.where(is_supp[retained], 1, 0)
        acc = float(accuracy_score(y_ret, preds_ret))
        risk = 1.0 - acc

        neg_mask = (y_ret == 0)
        n_neg = int(np.sum(neg_mask))
        fp = int(np.sum((preds_ret == 1) & neg_mask))
        fsr = (fp / n_neg) if n_neg > 0 else 0.0
    else:
        acc = 0.0
        risk = 0.0
        fsr = 0.0

    # Predictions vector (-1 for ABSTAIN, 0 for UNSUPPORTED, 1 for SUPPORTED)
    preds_all = np.full(n, -1, dtype=int)
    preds_all[is_supp] = 1
    preds_all[is_unsupp] = 0

    return {
        "coverage": coverage,
        "selective_accuracy": acc,
        "selective_risk": risk,
        "false_support_rate": fsr,
        "n_retained": n_retained,
        "n_abstained": n_abstained,
        "abstained_percentage": (n_abstained / n * 100) if n > 0 else 0.0,
        "predictions": preds_all,
    }

def compute_risk_coverage_curve(
    p_support: np.ndarray,
    y_true: np.ndarray,
    num_points: int = 50,
) -> tuple[list[dict[str, float]], float]:
    """
    Computes risk-coverage curve by sweeping symmetrical confidence margin:
    retaining examples where |p - 0.5| >= margin.
    """
    margins = np.linspace(0.0, 0.499, num_points)
    points = []
    risks = []
    coverages = []

    for margin in margins:
        t_low = 0.5 - margin
        t_high = 0.5 + margin
        res = evaluate_selective_prediction(p_support, y_true, t_low, t_high)
        if res["n_retained"] > 0:
            points.append({
                "margin": float(margin),
                "t_low": float(t_low),
                "t_high": float(t_high),
                "coverage": res["coverage"],
                "selective_risk": res["selective_risk"],
                "selective_accuracy": res["selective_accuracy"],
                "false_support_rate": res["false_support_rate"],
            })
            risks.append(res["selective_risk"])
            coverages.append(res["coverage"])

    aurc = compute_aurc(risks, coverages)
    return points, aurc
