"""The domain case study reads the repository's own cyber benchmark."""

from __future__ import annotations

import pytest

from clarification_pilot.benchmarks import adapter_for
from clarification_pilot.benchmarks.cybercase import DEFAULT_PATH, formatted, sample_from_item

ORIGINAL = {
    "id": "case_01_original",
    "base_case_id": "case_01",
    "condition": "ORIGINAL",
    "context_sentences": [
        {"id": "S1", "text": "PowerShell ran on WS-01."},
        {"id": "S2", "text": "The gateway recorded 1.4 GB outbound."},
    ],
    "question": "Did exfiltration occur?",
    "gold_attributes": {"answerability": "SUFFICIENT", "missing_information": []},
    "evaluation_notes": {"expected_behavior": "Confirm exfiltration.", "required_points": []},
}

REMOVED = {
    **ORIGINAL,
    "id": "case_01_removed",
    "condition": "REMOVED",
    "context_sentences": [
        {"id": "S1", "text": "PowerShell ran on WS-01."},
        {"id": "S2", "text": "No egress volume logs were captured."},
    ],
    "gold_attributes": {
        "answerability": "INSUFFICIENT",
        "missing_information": ["data transfer volume"],
    },
    "evaluation_notes": {
        "expected_behavior": "Abstain; transfer success is unestablished.",
        "required_points": ["volume unknown"],
    },
}


def test_the_candidate_sees_the_perturbed_case():
    sample = sample_from_item(REMOVED, ORIGINAL)
    assert "No egress volume logs" in sample.candidate.initial_input
    assert "1.4 GB" not in sample.candidate.initial_input


def test_the_unperturbed_case_is_the_simulator_reference():
    """The original supplies what was removed, so the simulator has something to reveal."""

    sample = sample_from_item(REMOVED, ORIGINAL)
    assert "1.4 GB" in sample.hidden.full_input


def test_answerability_is_the_ask_label():
    assert sample_from_item(REMOVED, ORIGINAL).hidden.should_ask is True
    assert sample_from_item(ORIGINAL, ORIGINAL).hidden.should_ask is False


def test_a_conflict_also_counts_as_worth_asking_about():
    conflicting = {
        **REMOVED,
        "gold_attributes": {"answerability": "CONFLICTING", "missing_information": ["which log"]},
    }
    assert sample_from_item(conflicting, ORIGINAL).hidden.should_ask is True


def test_missing_information_is_the_checkpoint_list():
    assert sample_from_item(REMOVED, ORIGINAL).hidden.required_points == ("data transfer volume",)
    assert sample_from_item(ORIGINAL, ORIGINAL).hidden.required_points == ()


def test_every_cyber_item_is_judge_scored():
    """Expectations are written as behaviour, so there is no deterministic subset."""

    assert sample_from_item(REMOVED, ORIGINAL).hidden.scoring == "judge"


def test_an_item_without_an_original_is_its_own_reference():
    sample = sample_from_item(REMOVED, None)
    assert sample.hidden.full_input == formatted(REMOVED)


@pytest.mark.skipif(not DEFAULT_PATH.exists(), reason="pilot benchmark not present")
def test_the_repository_benchmark_loads():
    samples = adapter_for("cybercase").load()
    assert len(samples) == 33
    assert sum(1 for s in samples if s.hidden.should_ask) == 9
    assert all(s.hidden.scoring == "judge" for s in samples)
    assert {s.hidden.source_task for s in samples} == {
        "cybercase_original",
        "cybercase_removed",
        "cybercase_contradiction",
        "cybercase_distractor",
        "cybercase_reorder",
    }
