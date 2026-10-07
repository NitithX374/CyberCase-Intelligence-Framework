from __future__ import annotations

import argparse
import hashlib
from collections import Counter
from pathlib import Path

from research.projection_validation.metrics import (
    classification,
    paired_outcomes,
    wilson,
)
from research.projection_validation.runtime import (
    HERE,
    ROOT,
    file_digest,
    read_json,
    read_rows,
    write_json,
)


def verify(directory: Path) -> dict:
    from scipy.stats import binomtest
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support

    manifest = read_json(HERE / "data/manifest.json")
    assert file_digest(HERE / "data/benchmark.jsonl") == manifest["benchmark_sha256"]
    assert (
        file_digest(HERE / "data/propagation_plan.jsonl")
        == manifest["propagation_plan_sha256"]
    )
    cases = read_rows(HERE / "data/benchmark.jsonl")
    rows = read_rows(directory / "predictions.jsonl")
    stored = read_json(directory / "metrics.json")
    assert len(rows) == sum(len(case["annotations"]) for case in cases) == 246
    assert Counter(row["gold"] for row in rows) == manifest["projection_gold"]
    for kind in ("involved_parties", "timeline", "impacts", "overall"):
        selected = [row for row in rows if kind == "overall" or row["type"] == kind]
        calculated = classification(selected)
        assert calculated == stored["quality"][kind]
        assessed = [
            row
            for row in selected
            if row["gold"] != "ambiguous"
            and row["predictions"]["semantic"] != "unassessed"
        ]
        actual = [row["gold"] == "supported" for row in assessed]
        predicted = [row["predictions"]["semantic"] == "supported" for row in assessed]
        precision, recall, f1, _ = precision_recall_fscore_support(
            actual, predicted, average="binary", zero_division=0
        )
        assert abs(precision - calculated["precision"]) < 1e-12
        assert abs(recall - calculated["recall_assessed"]) < 1e-12
        assert abs(f1 - calculated["f1_assessed"]) < 1e-12
        assert (
            abs(accuracy_score(actual, predicted) - calculated["accuracy_assessed"])
            < 1e-12
        )
    for successes, attempts in ((0, 18), (9, 18), (18, 18), (62, 66), (12, 165)):
        expected = binomtest(successes, attempts).proportion_ci(method="wilson")
        actual = wilson(successes, attempts)
        assert (
            abs(actual[0] - expected.low) < 1e-12
            and abs(actual[1] - expected.high) < 1e-12
        )
    paired = paired_outcomes([(True, False)] * 4 + [(False, True)])
    assert abs(paired["exact_mcnemar_p"] - binomtest(1, 5, 0.5).pvalue) < 1e-12
    grounded = read_rows(directory / "grounded_readings.jsonl")
    by_case = {row["case_id"]: row for row in cases}
    direct = 0
    for reading in grounded:
        sources = {
            source["source_id"]: source
            for source in by_case[reading["case_id"]]["sources"]
        }
        for claim in reading["reading"]["claims"]:
            for citation in (
                claim["supporting_citations"] + claim["contradicting_citations"]
            ):
                assert citation["pointer_state"] == "direct"
                source = sources[citation["source_id"]]
                assert (
                    citation["exact_quote"]
                    == source["text"][citation["start"] : citation["end"]]
                )
                direct += 1
    baseline = read_json(ROOT / "tmp/projection-validation/baseline.json")
    changed = [
        path
        for path, checksum in baseline["hashes"].items()
        if not (ROOT / path).is_file()
        or hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != checksum
    ]
    assert not changed, changed
    result = {
        "benchmark_hash_verified": True,
        "propagation_plan_hash_verified": True,
        "rows": len(rows),
        "gold_counts_verified": True,
        "metrics_match_sklearn": True,
        "intervals_match_scipy": True,
        "paired_test_matches_scipy": True,
        "direct_citations_exactly_reproduced": direct,
        "preexisting_production_and_test_hashes_unchanged": len(baseline["hashes"]),
        "summary": "All independent arithmetic, source-span and production-preservation checks passed.",
    }
    write_json(directory / "verification.json", result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, default=HERE / "results/pinned_cpu")
    args = parser.parse_args()
    print(verify(args.directory.resolve()))
