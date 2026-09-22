from __future__ import annotations

import re
from dataclasses import dataclass
from math import ceil, floor
from statistics import mean, median
from typing import Any, Iterable

from .model import FrozenClassifier, predict_texts

ATTACK_TERM_PATTERN = re.compile(
    r"\b(?:T\d{4}(?:\.\d{3})?|ATT&CK|MITRE|C2|C&C|command[- ]and[- ]control)\b",
    re.IGNORECASE,
)
ACTION_PATTERN = re.compile(
    r"\b(?:execute|executed|executing|download|downloaded|upload|uploaded|"
    r"exfiltrate|exfiltrated|encrypt|encrypted|delete|deleted|dump|dumped|"
    r"steal|stole|stolen|connect|connected|install|installed|launch|launched|"
    r"spawn|spawned|run|ran|modify|modified|create|created|phish|phishing|"
    r"exploit|exploited|inject|injected|capture|captured|record|recorded|"
    r"scan|scanned|enumerate|enumerated|persist|persisted|disable|disabled|"
    r"clear|cleared|remove|removed)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class EvaluationResult:
    name: str
    records: tuple[dict[str, Any], ...]
    metrics: dict[str, Any]
    token_statistics: dict[str, Any]


def _percentile(values: list[int], percentage: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    position = (len(ordered) - 1) * percentage
    lower = floor(position)
    upper = ceil(position)
    if lower == upper:
        return float(ordered[lower])
    weight = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * weight


def _token_lengths(tokenizer: Any, texts: list[str], batch_size: int = 128) -> list[int]:
    lengths: list[int] = []
    for offset in range(0, len(texts), batch_size):
        encoded = tokenizer(
            texts[offset : offset + batch_size],
            add_special_tokens=False,
            truncation=False,
        )
        lengths.extend(len(ids) for ids in encoded["input_ids"])
    return lengths


def token_statistics(tokenizer: Any, texts: list[str], max_length: int) -> dict[str, Any]:
    lengths = _token_lengths(tokenizer, texts)
    special_tokens = tokenizer.num_special_tokens_to_add(pair=False)
    content_limit = max_length - special_tokens
    over_limit = sum(length > content_limit for length in lengths)
    return {
        "sample_count": len(lengths),
        "min": min(lengths),
        "mean": round(mean(lengths), 4),
        "median": float(median(lengths)),
        "p90": round(_percentile(lengths, 0.90), 4),
        "p95": round(_percentile(lengths, 0.95), 4),
        "max": max(lengths),
        "configured_max_length": max_length,
        "special_tokens": special_tokens,
        "content_token_limit": content_limit,
        "exceeding_configured_max_length_count": over_limit,
        "exceeding_configured_max_length_percentage": over_limit / len(lengths),
    }


def _confusion(labels: Iterable[int], predictions: Iterable[int]) -> dict[str, int]:
    values = list(zip(labels, predictions, strict=True))
    return {
        "true_negative": sum(label == 0 and prediction == 0 for label, prediction in values),
        "false_positive": sum(label == 0 and prediction == 1 for label, prediction in values),
        "false_negative": sum(label == 1 and prediction == 0 for label, prediction in values),
        "true_positive": sum(label == 1 and prediction == 1 for label, prediction in values),
    }


def _ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _class_metrics(matrix: dict[str, int], label: int) -> tuple[float, float, float]:
    if label == 1:
        tp, fp, fn = matrix["true_positive"], matrix["false_positive"], matrix["false_negative"]
    else:
        tp, fp, fn = matrix["true_negative"], matrix["false_negative"], matrix["false_positive"]
    precision = _ratio(tp, tp + fp)
    recall = _ratio(tp, tp + fn)
    f1 = _ratio(2 * precision * recall, precision + recall)
    return precision, recall, f1


def binary_metrics(labels: list[int], predictions: list[int], threshold: float) -> dict[str, Any]:
    matrix = _confusion(labels, predictions)
    positive = _class_metrics(matrix, 1)
    negative = _class_metrics(matrix, 0)
    macro = tuple((positive[index] + negative[index]) / 2 for index in range(3))
    total = len(labels)
    return {
        "sample_count": total,
        "threshold": threshold,
        "accuracy": _ratio(
            matrix["true_positive"] + matrix["true_negative"], total
        ),
        "precision": positive[0],
        "recall": positive[1],
        "f1": positive[2],
        "macro_precision": macro[0],
        "macro_recall": macro[1],
        "macro_f1": macro[2],
        "attack_relevant_recall": positive[1],
        "false_skip_rate": _ratio(
            matrix["false_negative"],
            matrix["true_positive"] + matrix["false_negative"],
        ),
        "false_invocation_rate": _ratio(
            matrix["false_positive"],
            matrix["true_negative"] + matrix["false_positive"],
        ),
        "confusion_matrix": matrix,
    }


def _record(
    row: dict[str, Any],
    prediction: int,
    score: float,
    token_length: int,
    truncated: bool,
) -> dict[str, Any]:
    text = str(row["text"])
    gold = int(row["gold_label"])
    return {
        "text": text,
        "document": str(row["document"]),
        "gold_label": gold,
        "predicted_label": prediction,
        "p_relevant": float(score),
        "correct": prediction == gold,
        "text_char_length": len(text),
        "token_length": token_length,
        "contains_attack_term": bool(ATTACK_TERM_PATTERN.search(text)),
        "contains_action_verb": bool(ACTION_PATTERN.search(text)),
        "truncated": bool(truncated),
    }


def evaluate_dataset(
    name: str,
    rows: list[dict[str, Any]],
    classifier: FrozenClassifier,
    batch_size: int,
) -> EvaluationResult:
    texts = [str(row["text"]) for row in rows]
    labels = [int(row["gold_label"]) for row in rows]
    scores, predictions, truncated = predict_texts(classifier, texts, batch_size)
    lengths = _token_lengths(classifier.resources.tokenizer, texts)
    records = tuple(
        _record(row, prediction, score, length, was_truncated)
        for row, prediction, score, length, was_truncated in zip(
            rows, predictions, scores, lengths, truncated, strict=True
        )
    )
    return EvaluationResult(
        name=name,
        records=records,
        metrics=binary_metrics(labels, predictions, classifier.threshold),
        token_statistics=token_statistics(
            classifier.resources.tokenizer,
            texts,
            classifier.resources.max_length,
        ),
    )


def error_rows(result: EvaluationResult, label: int, prediction: int) -> list[dict[str, Any]]:
    rows = [
        record
        for record in result.records
        if record["gold_label"] == label and record["predicted_label"] == prediction
    ]
    if label == 1 and prediction == 0:
        return sorted(rows, key=lambda record: (record["p_relevant"], record["document"]))
    return sorted(rows, key=lambda record: (-record["p_relevant"], record["document"]))
