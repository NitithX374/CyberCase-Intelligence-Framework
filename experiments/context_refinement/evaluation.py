from __future__ import annotations

from typing import Any

from .dataset import gold_text
from .metrics import score_condition
from .protected_spans import compare_protected_spans


def _ratio(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 6) if denominator else 0.0


def evaluate_pairs(
    rows: list[dict[str, Any]],
    raw_contexts: dict[str, dict[str, Any]],
    refined_contexts: dict[str, dict[str, Any]],
    predictions: dict[tuple[str, str], dict[str, Any]],
    sbert_model: Any,
) -> list[dict[str, Any]]:
    expected_ids = {str(row["id"]) for row in rows}
    raw_predictions = {sample_id: predictions[(sample_id, "B0")] for sample_id in expected_ids}
    refined_predictions = {sample_id: predictions[(sample_id, "B1")] for sample_id in expected_ids}
    raw_scores = score_condition(rows, raw_predictions, "B0", sbert_model)
    refined_scores = score_condition(rows, refined_predictions, "B1", sbert_model)
    paired: list[dict[str, Any]] = []
    for row in rows:
        sample_id = str(row["id"])
        raw_context = raw_contexts[sample_id]["raw_context"]
        refined_record = refined_contexts[sample_id]
        refined_context = refined_record["refined_context"]
        raw_prediction = raw_predictions[sample_id]
        refined_prediction = refined_predictions[sample_id]
        paired.append(
            {
                "sample_id": sample_id,
                "category": row["category"],
                "language": "en",
                "format": "generation",
                "task": row["task"],
                "instruction": row["instruction"],
                "raw_context": raw_context,
                "refined_context": refined_context,
                "raw_context_chars": len(raw_context),
                "refined_context_chars": len(refined_context),
                "char_retention_ratio": _ratio(len(refined_context), len(raw_context)),
                "char_compression_ratio": _ratio(len(raw_context), len(refined_context)),
                "origin_tokens": refined_record.get("origin_tokens"),
                "refined_tokens": refined_record.get("refined_tokens"),
                "protected_span_diagnostics": refined_record["protected_span_diagnostics"],
                "gold_output": gold_text(row),
                "B0": {
                    "context_variant": "raw",
                    "prompt": raw_prediction["prompt"],
                    "output": raw_prediction["prediction_raw"],
                    "returned_model": raw_prediction["returned_model"],
                    **raw_scores[sample_id],
                },
                "B1": {
                    "context_variant": "refined",
                    "prompt": refined_prediction["prompt"],
                    "output": refined_prediction["prediction_raw"],
                    "returned_model": refined_prediction["returned_model"],
                    **refined_scores[sample_id],
                },
            }
        )
    return paired

