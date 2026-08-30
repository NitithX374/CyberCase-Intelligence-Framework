from __future__ import annotations

from pathlib import Path

from research.sevenllm_preflight.b2_config import FIXED_BENCHMARK_IDS
from research.sevenllm_preflight.b2_leakage import check_leakage, load_fixed_benchmark_ids
from research.sevenllm_preflight.b2_records import build_example, filter_english_training_rows
from research.sevenllm_preflight.b2_split import category_counts, split_examples


def row(category: str, source_line: int, language: str = "en") -> dict[str, object]:
    return {
        "category": category,
        "instruction": "Explain the reported incident.",
        "input": f"Incident {source_line} contains a suspicious event.",
        "thought": "This field must not enter B2.",
        "output": f"The incident response for {source_line} is recorded.",
        "task": f"train-{language}-gen",
    }


def test_b2_input_and_target_exclude_thought() -> None:
    example = build_example(row("Threat Analysis", 1), 1)
    assert example["input_text"] == (
        "task: Threat Analysis\n"
        "instruction: Explain the reported incident.\n"
        "context: Incident 1 contains a suspicious event."
    )
    assert example["target_text"] == "The incident response for 1 is recorded."
    assert "thought" not in example


def test_filter_keeps_exact_categories_and_english_only() -> None:
    rows = [
        row("Threat Analysis", 1),
        row("Threat Analysis", 2, "zh"),
        row("Unapproved Category", 3),
    ]
    selected, invalid = filter_english_training_rows(rows)
    assert invalid == []
    assert len(selected) == 1
    assert selected[0]["language"] == "en"


def test_split_is_deterministic_and_category_stratified() -> None:
    categories = ["Threat Analysis", "Risk Assessment"]
    examples = [build_example(row(category, index), index) for category in categories for index in range(1, 11)]
    first = split_examples(examples, 0.2, 42)
    second = split_examples(examples, 0.2, 42)
    assert [[item["source_line"] for item in split] for split in first] == [
        [item["source_line"] for item in split] for split in second
    ]
    assert category_counts(first[0]) == {category: 8 if category in categories else 0 for category in categories + [
        "Protection Strategy Research",
        "Summary Generation",
        "Incident Response Planning",
        "Impact Scope",
    ]}
    assert category_counts(first[1])["Threat Analysis"] == 2
    assert category_counts(first[1])["Risk Assessment"] == 2


def test_fixed_selection_matches_existing_manifest() -> None:
    path = Path(__file__).parents[1] / "results" / "pilot_1_en" / "pilot_1_en_50_selection.json"
    assert set(load_fixed_benchmark_ids(path)) == set(FIXED_BENCHMARK_IDS)


def test_leakage_check_fails_on_prompt_overlap() -> None:
    training = build_example(row("Threat Analysis", 1), 1)
    benchmark = {**row("Threat Analysis", 99), "id": "9901", "input": training["input_text"].split("context: ", 1)[1]}
    result = check_leakage({"train": [training], "validation": []}, [benchmark], ["9901"])
    assert result["passed"] is False
    assert result["splits"]["train"]["benchmark_prompt_fingerprint_overlap"] == [training["example_id"]]
