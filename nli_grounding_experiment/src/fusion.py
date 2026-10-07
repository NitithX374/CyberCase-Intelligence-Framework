from typing import Any
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score

def tune_binary_threshold(
    y_true: list[int] | np.ndarray,
    scores: list[float] | np.ndarray,
    thresholds: np.ndarray | None = None,
) -> tuple[float, float]:
    """
    Sweeps thresholds on DEV to find the threshold that maximizes Macro-F1.
    Returns:
        best_threshold, best_macro_f1
    """
    if thresholds is None:
        thresholds = np.linspace(0.01, 0.99, 99)

    y_true = np.asarray(y_true)
    scores = np.asarray(scores)

    best_thresh = 0.5
    best_f1 = -1.0

    for thresh in thresholds:
        preds = (scores >= thresh).astype(int)
        macro_f1 = float(f1_score(y_true, preds, average="macro", zero_division=0))
        if macro_f1 > best_f1:
            best_f1 = macro_f1
            best_thresh = float(thresh)

    return best_thresh, best_f1

class FusionClassifier:
    """
    Lightweight Logistic Regression fusion classifier for NLI probability features.
    """
    def __init__(
        self,
        solver: str = "lbfgs",
        C: float = 1.0,
        class_weight: str | None = "balanced",
        max_iter: int = 1000,
        random_state: int = 42,
    ):
        self.model = LogisticRegression(
            solver=solver,
            C=C,
            class_weight=class_weight,
            max_iter=max_iter,
            random_state=random_state,
        )

    def fit(self, X: np.ndarray, y: np.ndarray) -> "FusionClassifier":
        self.model.fit(X, y)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)

    def decision_function(self, X: np.ndarray) -> np.ndarray:
        return self.model.decision_function(X)
