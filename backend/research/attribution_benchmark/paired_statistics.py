from __future__ import annotations

import math

import numpy as np


def wilson(successes: int, total: int) -> list[float] | None:
    if not total:
        return None
    z = 1.959963984540054
    p = successes / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    margin = (
        z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    )
    return [max(0, center - margin), min(1, center + margin)]


def confusion(gold: list[int], prediction: list[bool]) -> dict:
    if len(gold) != len(prediction) or not gold:
        raise ValueError("Require aligned nonempty gold and predictions")
    tp = sum(label == 1 and pred for label, pred in zip(gold, prediction, strict=True))
    fp = sum(label == 0 and pred for label, pred in zip(gold, prediction, strict=True))
    tn = sum(
        label == 0 and not pred for label, pred in zip(gold, prediction, strict=True)
    )
    fn = len(gold) - tp - fp - tn
    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    return {
        "n": len(gold),
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "accuracy": (tp + tn) / len(gold),
        "precision": precision,
        "recall": recall,
        "f1": 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0,
        "false_acceptance_rate": fp / (fp + tn) if fp + tn else None,
        "false_rejection_rate": fn / (tp + fn) if tp + fn else None,
        "false_acceptance_wilson95": wilson(fp, fp + tn),
        "supported_retention_wilson95": wilson(tp, tp + fn),
    }


def mcnemar(first: list[bool], second: list[bool]) -> dict:
    if len(first) != len(second):
        raise ValueError("Paired binary outcomes must align")
    decreased = sum(a and not b for a, b in zip(first, second, strict=True))
    increased = sum(b and not a for a, b in zip(first, second, strict=True))
    discordant = decreased + increased
    probability = (
        min(
            1.0,
            2
            * sum(
                math.comb(discordant, k) for k in range(min(decreased, increased) + 1)
            )
            / 2**discordant,
        )
        if discordant
        else 1.0
    )
    return {
        "pairs": len(first),
        "baseline_only": decreased,
        "gate_only": increased,
        "exact_two_sided_p": probability,
        "test": "Exact paired McNemar/binomial on discordant pairs",
    }


def cluster_interval(
    numerators: list[int], denominators: list[int], *, seed=20261007
) -> list[float] | None:
    if len(numerators) != len(denominators) or not numerators:
        raise ValueError("Aligned cluster counts required")
    numerator = np.asarray(numerators)
    denominator = np.asarray(denominators)
    if denominator.sum() == 0:
        return None
    indices = np.random.default_rng(seed).integers(
        len(numerator), size=(2000, len(numerator))
    )
    bottoms = denominator[indices].sum(axis=1)
    rates = numerator[indices].sum(axis=1)[bottoms > 0] / bottoms[bottoms > 0]
    return np.quantile(rates, [0.025, 0.975]).tolist()


def paired_cluster_delta(
    first: list[int], second: list[int], denominators: list[int], *, seed=20261007
):
    if len(first) != len(second) or len(first) != len(denominators) or not first:
        raise ValueError("Aligned paired cluster counts required")
    return cluster_interval(
        [b - a for a, b in zip(first, second, strict=True)], denominators, seed=seed
    )
