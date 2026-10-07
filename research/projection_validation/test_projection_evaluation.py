from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest
from fake_nli import FakeNli

from app.trace.nli_model import NliUnavailable

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def evaluation_modules(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT))
    return {
        name: importlib.import_module(f"research.projection_validation.{name}")
        for name in ("metrics", "runtime", "measurement", "structural", "replay_inputs")
    }


def scored_rows():
    return [
        {
            "gold": gold,
            "family_id": f"family-{index // 2}",
            "predictions": {"semantic": prediction},
        }
        for index, (gold, prediction) in enumerate(
            (
                ("supported", "supported"),
                ("supported", "not_supported"),
                ("supported", "unassessed"),
                ("not_supported", "supported"),
                ("not_supported", "not_supported"),
                ("not_supported", "unassessed"),
                ("ambiguous", "supported"),
            )
        )
    ]


def test_abstentions_do_not_become_semantic_negatives(evaluation_modules):
    result = evaluation_modules["metrics"].classification(scored_rows())
    assert (result["tp"], result["fp"], result["tn"], result["fn"]) == (1, 1, 1, 1)
    assert result["n"] == 6
    assert result["excluded_ambiguous"] == 1
    assert result["precision"] == result["recall_assessed"] == result["f1_assessed"] == 0.5
    assert result["accuracy_assessed"] == 0.5
    assert result["supported_retention_rate"] == pytest.approx(1 / 3)
    assert result["false_acceptance_rate"] == pytest.approx(1 / 3)
    assert result["false_rejection_rate"] == pytest.approx(1 / 3)
    assert result["unassessed_rate"] == pytest.approx(1 / 3)


def test_all_unassessed_has_no_classifier_accuracy(evaluation_modules):
    rows = scored_rows()
    for row in rows:
        row["predictions"]["semantic"] = "unassessed"
    result = evaluation_modules["metrics"].classification(rows)
    assert result["accuracy_assessed"] is None
    assert result["precision"] is None
    assert result["unassessed_rate"] == 1
    assert result["supported_retention_rate"] == 0
    assert result["unsupported_admission_rate"] == 0


def test_cluster_bootstrap_is_reproducible(evaluation_modules):
    metrics = evaluation_modules["metrics"]
    first = metrics.clustered_intervals(scored_rows(), "semantic", samples=100, seed=5)
    second = metrics.clustered_intervals(scored_rows(), "semantic", samples=100, seed=5)
    assert first == second
    assert first["clusters"] == 4
    assert (
        first["intervals"]["supported_retention_rate"][0]
        <= 1 / 3
        <= first["intervals"]["supported_retention_rate"][1]
    )


def test_exact_paired_test_and_nonzero_zero_event_interval(evaluation_modules):
    metrics = evaluation_modules["metrics"]
    result = metrics.paired_outcomes([(True, False)] * 4 + [(False, True)] + [(True, True)])
    assert result["prevented"] == 4
    assert result["introduced"] == 1
    assert result["exact_mcnemar_p"] == 0.375
    assert result["rate_difference_validation_minus_baseline"] == -0.5
    interval = metrics.wilson(0, 18)
    assert interval[0] == pytest.approx(0, abs=1e-12)
    assert interval[1] == pytest.approx(0.175879223646658, abs=1e-12)


def test_jsonl_preserves_unicode_line_separators(evaluation_modules, tmp_path):
    path = tmp_path / "rows.jsonl"
    rows = [{"text": "ไทย\u2028English\u2029"}, {"text": "next"}]
    evaluation_modules["runtime"].write_rows(path, rows)
    assert evaluation_modules["runtime"].read_rows(path) == rows


def test_frozen_gold_and_provider_inputs_are_intact(evaluation_modules):
    from app.trace.trace import CaseProviderReadingReply

    runtime = evaluation_modules["runtime"]
    path = ROOT / "research/projection_validation/data/benchmark.jsonl"
    manifest = runtime.read_json(path.parent / "manifest.json")
    assert runtime.file_digest(path) == manifest["benchmark_sha256"]
    cases = runtime.read_rows(path)
    assert len(cases) == 18
    assert sum(len(case["annotations"]) for case in cases) == 246
    for case in cases:
        CaseProviderReadingReply.model_validate(case["reading"])
        assert runtime.digest(case["reading"]) == case["reading_sha256"]
        assert len(case["annotations"]) == sum(
            len(case["reading"][kind]) for kind in ("involved_parties", "timeline", "impacts")
        )


def test_structural_trial_denominators_include_duplicates(evaluation_modules):
    result = evaluation_modules["structural"].structural_evaluation()
    assert result["invalid_reasons"]["duplicate_id"] == 1
    assert result["counts"]["evidence_ids_claimed"] == 17
    assert result["counts"]["evidence_ids_resolved"] == 8
    assert result["duplicate_reference_rate"] == pytest.approx(1 / 17)
    assert result["pointer_distribution"] == {"direct": 8, "recovered": 1, "unresolved": 10}
    assert result["local_collision_free"]
    assert all(row["exact_reconstruction"] for row in result["segmentation"])


def test_measuring_unavailable_does_not_recurse_or_change_binding(evaluation_modules):
    case = evaluation_modules["runtime"].read_rows(
        ROOT / "research/projection_validation/data/benchmark.jsonl"
    )[0]
    before = json.dumps(case, sort_keys=True)

    def unavailable():
        raise NliUnavailable("measurement_test")

    reading, receipt = evaluation_modules["measurement"].validate_reading(case, unavailable)
    assert len(reading.claims) == 4
    assert all(claim.supporting_citations for claim in reading.claims)
    assert all(
        item.projection_grounding.reason == "model_unavailable:measurement_test"
        for _, _, item in evaluation_modules["measurement"].checked_items(reading)
    )
    assert len(receipt["projection_checks"]) == 15
    assert json.dumps(case, sort_keys=True) == before


def test_replay_changes_only_structured_admission(evaluation_modules):
    runtime = evaluation_modules["runtime"]
    case = runtime.read_rows(ROOT / "research/projection_validation/data/benchmark.jsonl")[0]
    plan = runtime.read_rows(ROOT / "research/projection_validation/data/propagation_plan.jsonl")[0]
    reading, _ = evaluation_modules["measurement"].validate_reading(case, lambda: FakeNli())
    replay = evaluation_modules["replay_inputs"].replay_input(
        case, plan, {"reading": reading.model_dump(mode="json")}
    )
    baseline = replay["conditions"]["no_validation"]
    proposed = replay["conditions"]["semantic"]
    assert baseline["reading"]["claims"] == proposed["reading"]["claims"]
    assert baseline["followup_history"] == proposed["followup_history"] == []
    assert baseline["technical_context"] is proposed["technical_context"] is None
    assert (
        sum(len(baseline["reading"][kind]) for kind in ("involved_parties", "timeline", "impacts"))
        == 3
    )
    assert (
        sum(len(proposed["reading"][kind]) for kind in ("involved_parties", "timeline", "impacts"))
        == 0
    )
