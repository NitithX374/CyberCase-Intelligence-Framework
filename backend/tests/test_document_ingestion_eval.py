import pytest

from tools.document_ingestion_eval import (
    character_error_rate,
    evaluate,
    word_error_rate,
)


def test_cer_and_wer_use_edit_distance() -> None:
    assert character_error_rate("case", "cases") == pytest.approx(0.25)
    assert word_error_rate("one two three", "one three") == pytest.approx(1 / 3)


def test_evaluation_compares_unified_and_routed_predictions() -> None:
    result = evaluate(
        [
            {
                "sample_id": "page-001",
                "ground_truth": "alpha beta",
                "predictions": {
                    "unified": "alpha",
                    "routed": "alpha beta",
                },
            }
        ]
    )

    assert len(result["samples"]) == 2
    assert result["by_mode"]["routed"]["cer"] == 0.0
    assert result["by_mode"]["unified"]["wer"] == pytest.approx(0.5)


def test_evaluation_reports_region_and_critical_field_metrics() -> None:
    result = evaluate(
        [
            {
                "sample_id": "case-001-page-03-region-04",
                "mode": "routed",
                "region_type": "handwriting",
                "ground_truth": "สมชาย 131000",
                "prediction": "สมชาย 131000",
                "critical_fields": {
                    "amount": "131000",
                    "person_name": "สมชาย",
                },
                "predicted_critical_fields": {
                    "amount": "131000",
                    "person_name": "สมชาย",
                },
                "generated_content_count": 2,
                "unsupported_generated_content_count": 1,
            }
        ]
    )

    handwriting = result["by_region_type"]["handwriting"]
    assert handwriting["cer"] == 0.0
    assert handwriting["handwriting_coverage"] == 1.0
    assert handwriting["unsupported_generated_content_rate"] == 0.5
    assert handwriting["critical_field_exact_match"] == {
        "amount": 1.0,
        "person_name": 1.0,
    }
