from __future__ import annotations

import json
import re
from collections import defaultdict
from typing import Any

from rouge import Rouge

from .protocol import format_for, normalize_choice_output


def prediction_text(record: dict[str, Any]) -> str:
    value = record.get("prediction_raw")
    if not isinstance(value, str):
        raise ValueError(f"Prediction is not textual for {record.get('sample_id')}")
    return value


def parse_json_prediction(raw: str) -> Any | None:
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE | re.DOTALL).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end < start:
        return None
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None


def flatten_values(value: Any) -> list[str]:
    if isinstance(value, dict):
        return [item for child in value.values() for item in flatten_values(child)]
    if isinstance(value, list):
        return [item for child in value for item in flatten_values(child)]
    return [str(value)]


def extraction_scores(gold: Any, prediction: Any | None) -> tuple[float, float, float]:
    if prediction is None:
        return 0.0, 0.0, 0.0
    gold_values = flatten_values(gold)
    prediction_values = flatten_values(prediction)
    overlap = sum(
        min(gold_values.count(value), prediction_values.count(value))
        for value in set(gold_values) & set(prediction_values)
    )
    precision = overlap / len(prediction_values) if prediction_values else 0.0
    recall = overlap / len(gold_values) if gold_values else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1


def rouge_l(gold: str, prediction: str) -> float:
    if not gold.strip() or not prediction.strip():
        return 0.0
    return float(Rouge().get_scores(gold, prediction)[0]["rouge-l"]["f"])


def mean(records: list[dict[str, Any]], field: str) -> float:
    return round(sum(float(record[field]) for record in records) / len(records), 6) if records else 0.0


def grouped_mean(records: list[dict[str, Any]], group_field: str, metric_field: str) -> dict[str, float]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        groups[str(record[group_field])].append(record)
    return {key: mean(items, metric_field) for key, items in sorted(groups.items())}


def score_rows(rows: list[dict[str, Any]], predictions: dict[str, dict[str, Any]]) -> dict[str, Any]:
    generation: list[dict[str, Any]] = []
    choice: list[dict[str, Any]] = []
    extraction: list[dict[str, Any]] = []
    for row in rows:
        sample_id = str(row["id"])
        raw = prediction_text(predictions[sample_id])
        output_format = format_for(row)
        item = {"sample_id": sample_id, "category": row["category"], "format": output_format}
        if output_format == "generation":
            generation.append({**item, "rouge_l": rouge_l(str(row["output"]), raw)})
        elif output_format == "choice":
            normalized = normalize_choice_output(raw)
            choice.append({**item, "normalized": normalized, "correct": int(normalized == row["output"])})
        else:
            parsed = parse_json_prediction(raw)
            precision, recall, f1 = extraction_scores(row["output"], parsed)
            extraction.append(
                {
                    **item,
                    "json_parse_success": parsed is not None,
                    "precision": precision,
                    "recall": recall,
                    "f1": f1,
                }
            )
    return {
        "generation": {
            "count": len(generation),
            "rouge_l_mean": mean(generation, "rouge_l"),
            "by_category": grouped_mean(generation, "category", "rouge_l"),
            "records": generation,
        },
        "choice": {
            "count": len(choice),
            "correct": sum(item["correct"] for item in choice),
            "accuracy": mean(choice, "correct"),
            "by_category": grouped_mean(choice, "category", "correct"),
            "records": choice,
        },
        "extraction": {
            "count": len(extraction),
            "precision": mean(extraction, "precision"),
            "recall": mean(extraction, "recall"),
            "f1": mean(extraction, "f1"),
            "records": extraction,
        },
        "official_primary_metrics": {
            "generation": "ROUGE-L",
            "choice": "exact match after strict A/B/C/D normalization",
            "extraction": "flattened-leaf precision/recall/F1",
        },
    }
