from __future__ import annotations

from math import ceil, floor
from statistics import fmean
from typing import Iterable


def percentile(values: list[int], probability: float) -> float:
    if not values:
        raise ValueError("Cannot calculate a percentile for an empty sequence")
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = floor(position)
    upper = ceil(position)
    if lower == upper:
        return float(ordered[lower])
    fraction = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def distribution(values: Iterable[int], thresholds: Iterable[int]) -> dict[str, object]:
    ordered = sorted(int(value) for value in values)
    if not ordered:
        return {"count": 0, "mean": None, "p50": None, "p75": None, "p90": None, "p95": None, "p99": None, "maximum": None, "exceeding": {}}
    count = len(ordered)
    return {
        "count": count,
        "mean": round(fmean(ordered), 3),
        "p50": round(percentile(ordered, 0.50), 3),
        "p75": round(percentile(ordered, 0.75), 3),
        "p90": round(percentile(ordered, 0.90), 3),
        "p95": round(percentile(ordered, 0.95), 3),
        "p99": round(percentile(ordered, 0.99), 3),
        "maximum": ordered[-1],
        "exceeding": {
            str(threshold): {
                "count": sum(value > threshold for value in ordered),
                "percentage": round(100 * sum(value > threshold for value in ordered) / count, 3),
            }
            for threshold in thresholds
        },
    }


def grouped_distributions(records: list[dict[str, object]], field: str, thresholds: Iterable[int]) -> dict[str, dict[str, object]]:
    groups: dict[str, list[int]] = {}
    for record in records:
        key = str(record[field])
        groups.setdefault(key, []).append(int(record["input_tokens"]))
    return {key: distribution(values, thresholds) for key, values in sorted(groups.items())}


def grouped_output_distributions(records: list[dict[str, object]], field: str) -> dict[str, dict[str, object]]:
    groups: dict[str, list[int]] = {}
    for record in records:
        key = str(record[field])
        groups.setdefault(key, []).append(int(record["output_tokens"]))
    return {key: distribution(values, ()) for key, values in sorted(groups.items())}
