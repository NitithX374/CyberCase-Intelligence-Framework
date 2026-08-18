"""Dataset loader and deterministic stratified sampling for the pilot."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from evaluation.analysis_pilot.config import DATASET_PATH, LANGUAGES, SCENARIOS


def load_all_cases(path: Path = DATASET_PATH) -> list[dict[str, Any]]:
    """Load all cases from the semantic verification JSONL file."""
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found at {path}")

    cases: list[dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if line_str:
                cases.append(json.loads(line_str))
    return cases


def select_stratified_pilot_cases(
    cases: list[dict[str, Any]] | None = None,
    count: int = 10,
) -> list[dict[str, Any]]:
    """Select stratified cases across scenarios and languages deterministically."""
    all_cases = cases if cases is not None else load_all_cases()

    selected: list[dict[str, Any]] = []
    taken_ids: set[str] = set()

    # Pass 1: 1 per (scenario, language) bucket
    for scenario in SCENARIOS:
        for lang in LANGUAGES:
            bucket = [
                c
                for c in all_cases
                if c.get("scenario_id") == scenario
                and c.get("language") == lang
                and c.get("case_id") not in taken_ids
            ]
            if bucket:
                bucket.sort(key=lambda x: x["case_id"])
                selected.append(bucket[0])
                taken_ids.add(bucket[0]["case_id"])

    # Pass 2: If count > 8, round-robin through scenarios/languages to maintain balance
    pass_idx = 1
    while len(selected) < count and pass_idx < 10:
        for scenario in SCENARIOS:
            if len(selected) >= count:
                break
            for lang in LANGUAGES:
                if len(selected) >= count:
                    break
                bucket = [
                    c
                    for c in all_cases
                    if c.get("scenario_id") == scenario
                    and c.get("language") == lang
                    and c.get("case_id") not in taken_ids
                ]
                if bucket:
                    bucket.sort(key=lambda x: x["case_id"])
                    selected.append(bucket[0])
                    taken_ids.add(bucket[0]["case_id"])
        pass_idx += 1

    return selected[:count]
