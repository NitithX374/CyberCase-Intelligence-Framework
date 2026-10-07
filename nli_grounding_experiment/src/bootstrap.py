import numpy as np
from sklearn.metrics import accuracy_score, f1_score

def paired_bootstrap_test(y_true, y_a, y_b, n_bootstraps=1000, seed=42):
    """
    Computes paired bootstrap difference: y_a - y_b.
    Returns mean diff and 95% CI for accuracy, macro_f1, supported_f1, and fsr.
    """
    rng = np.random.default_rng(seed)
    n = len(y_true)
    d_acc, d_mf1, d_sf1, d_fsr = [], [], [], []
    for _ in range(n_bootstraps):
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
        "accuracy": {
            "mean_diff": float(np.mean(d_acc)),
            "ci_lower": float(np.percentile(d_acc, 2.5)),
            "ci_upper": float(np.percentile(d_acc, 97.5)),
        },
        "macro_f1": {
            "mean_diff": float(np.mean(d_mf1)),
            "ci_lower": float(np.percentile(d_mf1, 2.5)),
            "ci_upper": float(np.percentile(d_mf1, 97.5)),
        },
        "supported_f1": {
            "mean_diff": float(np.mean(d_sf1)),
            "ci_lower": float(np.percentile(d_sf1, 2.5)),
            "ci_upper": float(np.percentile(d_sf1, 97.5)),
        },
        "fsr": {
            "mean_diff": float(np.mean(d_fsr)),
            "ci_lower": float(np.percentile(d_fsr, 2.5)),
            "ci_upper": float(np.percentile(d_fsr, 97.5)),
        },
    }
