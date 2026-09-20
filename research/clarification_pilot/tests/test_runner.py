"""The runner end to end, offline: paired design, budgets, and what it writes."""

from __future__ import annotations

import asyncio
import json

from clarification_pilot.arms import ArmConfig
from clarification_pilot.benchmarks.askbench import DEFAULT_PATH
from clarification_pilot.runner import jobs, parser, run

import pytest


def planned_for(arms, budgets, samples):
    return jobs(samples, arms, budgets, unknown_tolerance=2, separate_question_call=False)


def test_only_the_interactive_arm_repeats_per_budget(sample):
    planned = planned_for(["direct", "multi_stage", "gap_aware", "followup"], [1, 2, 3], [sample])
    counts: dict[str, int] = {}
    for _, arm, _ in planned:
        counts[arm] = counts.get(arm, 0) + 1
    assert counts == {"direct": 1, "multi_stage": 1, "gap_aware": 1, "followup": 3}


def test_every_arm_runs_on_every_sample(sample):
    import dataclasses

    second = dataclasses.replace(
        sample,
        candidate=dataclasses.replace(sample.candidate, sample_id="sample-2"),
        hidden=dataclasses.replace(sample.hidden, sample_id="sample-2"),
    )
    planned = planned_for(["direct", "followup"], [1], [sample, second])
    pairs = {(item[0].sample_id, item[1]) for item in planned}
    assert pairs == {
        ("sample-1", "direct"),
        ("sample-1", "followup"),
        ("sample-2", "direct"),
        ("sample-2", "followup"),
    }


def test_the_budgets_reach_the_arm_config(sample):
    planned = planned_for(["followup"], [1, 3], [sample])
    assert sorted(config.budget for _, _, config in planned) == [1, 3]
    assert all(isinstance(config, ArmConfig) for _, _, config in planned)


@pytest.mark.skipif(not DEFAULT_PATH.exists(), reason="AskMind data not downloaded")
def test_a_dry_run_writes_a_manifest_results_and_a_report(tmp_path, monkeypatch):
    from clarification_pilot import runner

    monkeypatch.setattr(runner, "RESULTS_DIR", tmp_path)
    args = parser().parse_args(
        ["--dry-run", "--limit", "4", "--budgets", "1", "2", "--concurrency", "2"]
    )
    report = asyncio.run(run(args))

    assert report.exists()
    written = sorted(path.name.split("_")[0] for path in tmp_path.iterdir())
    # The manifest and the two streamed .jsonl sinks land before and during the
    # run; the combined .json files and the report land at the end.
    assert written == ["manifest", "report", "run", "run", "scored", "scored"]

    streamed = (tmp_path / f"run_{report.stem.split('_', 1)[1]}.jsonl").read_text(encoding="utf-8")
    assert len(streamed.strip().splitlines()) == 20, "every finished run should be on disk already"

    payload = json.loads(next(tmp_path.glob("run_*.json")).read_text(encoding="utf-8"))
    manifest = payload["manifest"]
    assert manifest["dry_run"] is True
    assert manifest["temperature"] == 0.0
    assert manifest["seed"] == 42
    assert len(manifest["sample_ids"]) == 4
    assert manifest["dataset_sha256"]
    assert set(manifest["prompt_versions"]) >= {
        "sufficiency",
        "gap_selection",
        "question_generation",
        "state_update",
        "final_answer",
        "simulator",
        "judge",
    }

    scored = json.loads(next(tmp_path.glob("scored_*.json")).read_text(encoding="utf-8"))
    # Four arms, and the interactive one twice: 4 samples x 5 runs.
    assert len(scored) == 20

    by_arm: dict[str, set[str]] = {}
    for item in scored:
        by_arm.setdefault(item["arm"], set()).add(item["sample_id"])
    ids = set(manifest["sample_ids"])
    for arm, covered in by_arm.items():
        assert covered == ids, f"{arm} did not run on every sample; the pairing is broken"


@pytest.mark.skipif(not DEFAULT_PATH.exists(), reason="AskMind data not downloaded")
def test_a_dry_run_never_needs_a_key(monkeypatch, tmp_path):
    from clarification_pilot import runner

    monkeypatch.delenv("OPENROUTER_CYBERCASE", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setattr(runner, "RESULTS_DIR", tmp_path)
    args = parser().parse_args(["--dry-run", "--limit", "2", "--budgets", "1"])
    assert asyncio.run(run(args)).exists()
