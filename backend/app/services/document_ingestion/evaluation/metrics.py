from collections import defaultdict
from typing import Any


CRITICAL_FIELD_NAMES = (
    "date",
    "time",
    "amount",
    "account_number",
    "transaction_id",
    "person_name",
    "case_number",
)


def _edit_distance(reference: list[str], prediction: list[str]) -> int:
    previous = list(range(len(prediction) + 1))
    for reference_index, reference_value in enumerate(reference, start=1):
        current = [reference_index]
        for prediction_index, prediction_value in enumerate(prediction, start=1):
            substitution_cost = int(reference_value != prediction_value)
            current.append(
                min(
                    previous[prediction_index] + 1,
                    current[prediction_index - 1] + 1,
                    previous[prediction_index - 1] + substitution_cost,
                )
            )
        previous = current
    return previous[-1]


def character_error_rate(ground_truth: str, prediction: str) -> float:
    return _edit_distance(list(ground_truth), list(prediction)) / max(
        1, len(ground_truth)
    )


def word_error_rate(ground_truth: str, prediction: str) -> float:
    reference_words = ground_truth.split()
    prediction_words = prediction.split()
    return _edit_distance(reference_words, prediction_words) / max(
        1, len(reference_words)
    )


def _expanded_samples(samples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    expanded = []
    for sample in samples:
        predictions = sample.get("predictions")
        if not isinstance(predictions, dict):
            expanded.append(sample)
            continue
        for mode, prediction in predictions.items():
            expanded.append({**sample, "mode": mode, "prediction": prediction})
    return expanded


def _critical_field_scores(sample: dict[str, Any]) -> dict[str, float]:
    ground_truth = sample.get("critical_fields") or {}
    prediction = sample.get("predicted_critical_fields") or {}
    scores = {}
    for name in CRITICAL_FIELD_NAMES:
        expected = ground_truth.get(name)
        if expected is None:
            continue
        scores[name] = float(prediction.get(name) == expected)
    return scores


def _score_sample(sample: dict[str, Any]) -> dict[str, Any]:
    ground_truth = str(sample["ground_truth"])
    prediction = str(sample["prediction"])
    region_type = str(sample.get("region_type", "unknown"))
    generated_count = int(sample.get("generated_content_count", 0))
    unsupported_count = int(sample.get("unsupported_generated_content_count", 0))
    return {
        "sample_id": str(sample["sample_id"]),
        "mode": str(sample.get("mode", "unspecified")),
        "region_type": region_type,
        "cer": character_error_rate(ground_truth, prediction),
        "wer": word_error_rate(ground_truth, prediction),
        "critical_field_exact_match": _critical_field_scores(sample),
        "handwriting_coverage": (
            float(bool(prediction.strip()))
            if region_type == "handwriting" and ground_truth.strip()
            else None
        ),
        "unsupported_generated_content_rate": (
            unsupported_count / generated_count if generated_count else 0.0
        ),
    }


def _average(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {
            "cer": 0.0,
            "wer": 0.0,
            "handwriting_coverage": None,
            "unsupported_generated_content_rate": 0.0,
            "critical_field_exact_match": {},
        }
    handwriting = [
        row["handwriting_coverage"]
        for row in rows
        if row["handwriting_coverage"] is not None
    ]
    field_values: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        for name, value in row["critical_field_exact_match"].items():
            field_values[name].append(value)
    return {
        "cer": sum(row["cer"] for row in rows) / len(rows),
        "wer": sum(row["wer"] for row in rows) / len(rows),
        "handwriting_coverage": (
            sum(handwriting) / len(handwriting) if handwriting else None
        ),
        "unsupported_generated_content_rate": sum(
            row["unsupported_generated_content_rate"] for row in rows
        )
        / len(rows),
        "critical_field_exact_match": {
            name: sum(values) / len(values) for name, values in field_values.items()
        },
    }


def evaluate(samples: list[dict[str, Any]]) -> dict[str, Any]:
    results = [_score_sample(sample) for sample in _expanded_samples(samples)]
    by_mode = {
        mode: _average([row for row in results if row["mode"] == mode])
        for mode in sorted({row["mode"] for row in results})
    }
    by_region_type = {
        region_type: _average(
            [row for row in results if row["region_type"] == region_type]
        )
        for region_type in sorted({row["region_type"] for row in results})
    }
    return {
        "samples": results,
        "overall": _average(results),
        "by_mode": by_mode,
        "by_region_type": by_region_type,
    }
