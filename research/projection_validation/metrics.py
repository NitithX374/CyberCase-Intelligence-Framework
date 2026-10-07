from __future__ import annotations

import math
import random
from collections import Counter, defaultdict


def ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def classification(rows: list[dict], prediction: str = "semantic") -> dict:
    included = [row for row in rows if row["gold"] in {"supported", "not_supported"}]
    counts = Counter()
    for row in included:
        gold = row["gold"] == "supported"
        verdict = row["predictions"][prediction]
        if verdict == "unassessed":
            counts["unassessed_positive" if gold else "unassessed_negative"] += 1
        else:
            counts[
                ("tp" if gold else "fp")
                if verdict == "supported"
                else ("fn" if gold else "tn")
            ] += 1
    tp, fp, tn, fn = (counts[key] for key in ("tp", "fp", "tn", "fn"))
    up, un = counts["unassessed_positive"], counts["unassessed_negative"]
    positive, negative = tp + fn + up, fp + tn + un
    precision = ratio(tp, tp + fp)
    recall = ratio(tp, tp + fn)
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision is not None and recall is not None and precision + recall
        else 0.0
        if tp + fp + fn
        else None
    )
    return {
        "n": len(included),
        "excluded_ambiguous": len(rows) - len(included),
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "unassessed_positive": up,
        "unassessed_negative": un,
        "gold_positive": positive,
        "gold_negative": negative,
        "precision": precision,
        "recall_assessed": recall,
        "f1_assessed": f1,
        "accuracy_assessed": ratio(tp + tn, tp + fp + tn + fn),
        "correct_fraction_all_attempts": ratio(tp + tn, len(included)),
        "false_acceptance_rate": ratio(fp, negative),
        "false_acceptance_rate_assessed": ratio(fp, fp + tn),
        "false_rejection_rate": ratio(fn, positive),
        "false_rejection_rate_assessed": ratio(fn, tp + fn),
        "unassessed_rate": ratio(up + un, len(included)),
        "supported_retention_rate": ratio(tp, positive),
        "unsupported_admission_rate": ratio(fp, negative),
        "admitted": tp + fp,
        "withheld": fn + tn + up + un,
        "rejection_rate": ratio(fn + tn, len(included)),
        "admission_rate": ratio(tp + fp, len(included)),
    }


def percentile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    values = sorted(values)
    position = (len(values) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(values) - 1)
    return values[lower] + (values[upper] - values[lower]) * (position - lower)


def clustered_intervals(
    rows: list[dict], prediction: str, samples: int = 2000, seed: int = 20261006
) -> dict:
    families = defaultdict(list)
    for row in rows:
        families[row["family_id"]].append(row)
    keys = sorted(families)
    metrics = (
        "precision",
        "recall_assessed",
        "f1_assessed",
        "accuracy_assessed",
        "unsupported_admission_rate",
        "supported_retention_rate",
    )
    draws = defaultdict(list)
    randomizer = random.Random(seed)
    for _ in range(samples):
        sample = [
            row
            for key in randomizer.choices(keys, k=len(keys))
            for row in families[key]
        ]
        result = classification(sample, prediction)
        for metric in metrics:
            if result[metric] is not None:
                draws[metric].append(result[metric])
    return {
        "method": "Case-family percentile cluster bootstrap",
        "clusters": len(keys),
        "samples": samples,
        "seed": seed,
        "intervals": {
            metric: [percentile(draws[metric], 0.025), percentile(draws[metric], 0.975)]
            for metric in metrics
        },
    }


def wilson(successes: int, attempts: int) -> list[float] | None:
    if not attempts:
        return None
    z = 1.959963984540054
    proportion = successes / attempts
    denominator = 1 + z * z / attempts
    center = (proportion + z * z / (2 * attempts)) / denominator
    half = (
        z
        * math.sqrt(
            proportion * (1 - proportion) / attempts + z * z / (4 * attempts * attempts)
        )
        / denominator
    )
    return [center - half, center + half]


def paired_outcomes(pairs: list[tuple[bool, bool]]) -> dict:
    cells = Counter(pairs)
    prevented = cells[(True, False)]
    introduced = cells[(False, True)]
    discordant = prevented + introduced
    p = (
        min(
            1.0,
            2
            * sum(
                math.comb(discordant, k) for k in range(min(prevented, introduced) + 1)
            )
            / 2**discordant,
        )
        if discordant
        else 1.0
    )
    return {
        "n": len(pairs),
        "both": cells[(True, True)],
        "neither": cells[(False, False)],
        "prevented": prevented,
        "introduced": introduced,
        "exact_mcnemar_p": p,
        "discordant_pairs": discordant,
        "baseline_rate": ratio(sum(first for first, _ in pairs), len(pairs)),
        "validation_rate": ratio(sum(second for _, second in pairs), len(pairs)),
        "rate_difference_validation_minus_baseline": ratio(
            introduced - prevented, len(pairs)
        ),
    }


def summary_tables(rows: list[dict]) -> dict:
    labelled = [row for row in rows if row["gold"] != "ambiguous"]
    conditions = ("no_validation", "claim_link", "semantic")
    return {
        "quality": {
            kind: classification(
                [row for row in rows if kind == "overall" or row["type"] == kind]
            )
            for kind in ("involved_parties", "timeline", "impacts", "overall")
        },
        "baselines": {
            condition: classification(rows, condition) for condition in conditions
        },
        "intervals": {
            condition: clustered_intervals(labelled, condition)
            for condition in conditions
        },
        "language": {
            language: classification(
                [row for row in rows if row["language"] == language]
            )
            for language in ("english", "thai")
        },
        "origin": {
            origin: classification([row for row in rows if row["origin"] == origin])
            for origin in ("controlled", "saved_output")
        },
        "verdicts_all": dict(Counter(row["predictions"]["semantic"] for row in rows)),
        "unassessed_reasons": dict(
            Counter(
                row["grounding"]["reason"]
                for row in rows
                if row["grounding"]["verdict"] == "unassessed"
            )
        ),
        "failure_ids": {
            "false_accepts": [
                row["projection_id"]
                for row in rows
                if row["gold"] == "not_supported"
                and row["predictions"]["semantic"] == "supported"
            ],
            "false_rejects": [
                row["projection_id"]
                for row in rows
                if row["gold"] == "supported"
                and row["predictions"]["semantic"] == "not_supported"
            ],
            "unassessed_positive": [
                row["projection_id"]
                for row in rows
                if row["gold"] == "supported"
                and row["predictions"]["semantic"] == "unassessed"
            ],
        },
    }
