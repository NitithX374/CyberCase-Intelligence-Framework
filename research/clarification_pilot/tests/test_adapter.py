"""The AskMind adapter, against the published file and against synthetic rows."""

from __future__ import annotations

import pytest

from clarification_pilot.benchmarks import adapter_for, stratified
from clarification_pilot.benchmarks.askbench import DEFAULT_PATH, sample_from_row

ROW = {
    "id": "abc",
    "ori_question": "The radius is 30 meters. What Lorentz factor is needed?",
    "degraded_question": "The radius is a few tens of meters. What Lorentz factor is needed?",
    "degraded_info": "The radius was blurred.",
    "required_points": ["Exact value of the detector radius"],
    "expected_answer": "54",
    "source_task": "ask_mind_gpqade",
}


def test_fields_map_to_the_two_sides_of_the_boundary():
    sample = sample_from_row(ROW)
    assert sample.candidate.initial_input == ROW["degraded_question"]
    assert sample.hidden.full_input == ROW["ori_question"]
    assert sample.hidden.gold_answer == "54"
    assert sample.hidden.required_points == ("Exact value of the detector radius",)
    assert sample.hidden.hidden_summary == "The radius was blurred."


def test_a_degraded_question_means_the_system_should_ask():
    assert sample_from_row(ROW).hidden.should_ask is True


def test_an_undegraded_question_means_it_should_not():
    """53 of the 400 rows were never degraded. That is the ask label."""

    untouched = {**ROW, "degraded_question": ROW["ori_question"]}
    assert sample_from_row(untouched).hidden.should_ask is False


def test_the_rubric_is_not_the_ask_label():
    """Undegraded rows still carry required_points, so the rubric cannot be used."""

    untouched = {**ROW, "degraded_question": ROW["ori_question"]}
    sample = sample_from_row(untouched)
    assert sample.hidden.required_points
    assert sample.hidden.should_ask is False


def test_only_gpqa_is_routed_to_the_judge():
    assert sample_from_row(ROW).hidden.scoring == "judge"
    for task in ("ask_mind_medqade", "ask_mind_bbhde", "ask_mind_math500de"):
        assert sample_from_row({**ROW, "source_task": task}).hidden.scoring == "exact_match"


def test_optional_fields_are_read_defensively():
    """Three of the published key-sets differ; only five fields are required."""

    minimal = {
        key: ROW[key]
        for key in ("id", "ori_question", "degraded_question", "expected_answer", "source_task")
    }
    sample = sample_from_row(minimal)
    assert sample.hidden.required_points == ()
    assert sample.hidden.hidden_summary == ""


def test_a_missing_required_field_is_a_schema_change_not_a_default():
    with pytest.raises(ValueError, match="missing"):
        sample_from_row({key: value for key, value in ROW.items() if key != "expected_answer"})


@pytest.mark.skipif(not DEFAULT_PATH.exists(), reason="AskMind data not downloaded")
def test_the_published_file_reads_as_expected():
    samples = adapter_for("askmind").load()
    assert len(samples) == 400
    assert len({sample.sample_id for sample in samples}) == 400
    assert sum(1 for s in samples if s.hidden.should_ask) == 347
    assert sum(1 for s in samples if s.hidden.scoring == "exact_match") == 300
    assert sum(1 for s in samples if s.hidden.scoring == "judge") == 100


@pytest.mark.skipif(not DEFAULT_PATH.exists(), reason="AskMind data not downloaded")
def test_a_subset_is_stratified_and_reproducible():
    samples = adapter_for("askmind").load()
    first = stratified(samples, limit=40, seed=42)
    again = stratified(samples, limit=40, seed=42)
    assert [s.sample_id for s in first] == [s.sample_id for s in again]
    assert len(first) == 40
    tasks = {s.hidden.source_task for s in first}
    assert len(tasks) == 4, "every source task should survive the subset"
