from __future__ import annotations

import json
from pathlib import Path

from .b2_config import FIXED_BENCHMARK_IDS
from .b2_records import benchmark_id_for, example_fingerprint, prompt_fingerprint


def load_fixed_benchmark_ids(path: Path) -> list[str]:
    with path.open(encoding="utf-8") as handle:
        manifest = json.load(handle)
    ids = [str(value) for value in manifest.get("sample_ids", [])]
    if len(ids) != 50 or len(set(ids)) != 50:
        raise ValueError(f"Fixed benchmark selection must contain 50 unique IDs: {path}")
    if set(ids) != set(FIXED_BENCHMARK_IDS):
        raise ValueError("Fixed benchmark selection does not match the existing 50 benchmark IDs")
    return sorted(ids, key=int)


def benchmark_reference(rows: list[dict[str, Any]], fixed_ids: list[str]) -> dict[str, Any]:
    ids = [benchmark_id_for(row) for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Benchmark IDs are not unique")
    id_set = set(ids)
    missing_fixed = sorted(set(fixed_ids) - id_set, key=int)
    if missing_fixed:
        raise ValueError(f"Fixed benchmark IDs are missing from the benchmark file: {missing_fixed}")
    return {
        "all_ids": id_set,
        "fixed_ids": set(fixed_ids),
        "prompt_fingerprints": {prompt_fingerprint(row) for row in rows},
        "example_fingerprints": {example_fingerprint(row) for row in rows},
        "fixed_prompt_fingerprints": {
            prompt_fingerprint(row) for row in rows if benchmark_id_for(row) in set(fixed_ids)
        },
        "fixed_example_fingerprints": {
            example_fingerprint(row) for row in rows if benchmark_id_for(row) in set(fixed_ids)
        },
    }


def _overlap_details(examples: list[dict[str, Any]], reference: dict[str, Any]) -> dict[str, Any]:
    source_ids = {str(row["source_id"]) for row in examples if row.get("source_id") is not None}
    benchmark_ids = sorted(source_ids & reference["all_ids"], key=int)
    fixed_source_ids = sorted(source_ids & reference["fixed_ids"], key=int)
    prompt_matches = [
        row["example_id"] for row in examples if row["prompt_fingerprint"] in reference["prompt_fingerprints"]
    ]
    example_matches = [
        row["example_id"] for row in examples if row["example_fingerprint"] in reference["example_fingerprints"]
    ]
    fixed_prompt_matches = [
        row["example_id"] for row in examples if row["prompt_fingerprint"] in reference["fixed_prompt_fingerprints"]
    ]
    fixed_example_matches = [
        row["example_id"] for row in examples if row["example_fingerprint"] in reference["fixed_example_fingerprints"]
    ]
    return {
        "benchmark_source_id_overlap": benchmark_ids,
        "fixed_benchmark_source_id_overlap": fixed_source_ids,
        "benchmark_prompt_fingerprint_overlap": sorted(prompt_matches),
        "benchmark_example_fingerprint_overlap": sorted(example_matches),
        "fixed_benchmark_prompt_fingerprint_overlap": sorted(fixed_prompt_matches),
        "fixed_benchmark_example_fingerprint_overlap": sorted(fixed_example_matches),
    }


def check_leakage(
    splits: dict[str, list[dict[str, Any]]],
    benchmark_rows: list[dict[str, Any]],
    fixed_ids: list[str],
) -> dict[str, Any]:
    reference = benchmark_reference(benchmark_rows, fixed_ids)
    split_results: dict[str, Any] = {}
    all_passed = True
    for split_name, examples in splits.items():
        details = _overlap_details(examples, reference)
        passed = not any(details.values())
        split_results[split_name] = {"passed": passed, **details}
        all_passed = all_passed and passed
    return {
        "passed": all_passed,
        "benchmark_is_test_only": True,
        "benchmark_count": len(reference["all_ids"]),
        "fixed_benchmark_count": len(reference["fixed_ids"]),
        "fixed_benchmark_ids": sorted(reference["fixed_ids"], key=int),
        "splits": split_results,
    }
