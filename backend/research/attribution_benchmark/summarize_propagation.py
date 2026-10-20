from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np

from research.attribution_benchmark.paired_statistics import (
    cluster_interval,
    mcnemar,
    paired_cluster_delta,
)
from research.attribution_benchmark.propagation_metrics import ratio
from research.attribution_benchmark.receipts import digest, save

ARMS = ("unfiltered", "verified")
TERMINAL = {"completed", "failed", "protocol_violation", "no_accepted_claims"}


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_run(directory: Path):
    manifest = read(directory / "manifest.json")
    records = []
    for key in manifest["cluster_keys"]:
        mapping = read(directory / key / "row_mapping.json")
        arms = {}
        for arm in ARMS:
            root = directory / key / arm
            outcome = read(root / "outcome.json")
            if outcome["status"] not in TERMINAL:
                raise ValueError(f"Incomplete experiment arm: {key}/{arm}")
            payload = read(root / "request.json")
            if digest(payload) != outcome["payload_sha256"]:
                raise ValueError("Recorded Judgement input changed")
            accepted = set(outcome["accepted_claim_ids"])
            expected = {
                row["claim_id"]
                for row in mapping
                if arm == "unfiltered" or row["p_supported"] >= 0.5
            }
            if accepted != expected:
                raise ValueError("Recorded admission differs from frozen policy")
            claims = {
                claim["claim_id"]: claim["text"]
                for claim in payload["reading"]["claims"]
            }
            if set(claims) != accepted:
                raise ValueError("Judgement payload bypasses recorded admission")
            outcomes = [read(path) for path in root.glob("provider_response_*.json")]
            arms[arm] = {**outcome, "payload_claims": claims, "raw_responses": outcomes}
        if any(
            arms["unfiltered"]["payload_claims"].get(key) != value
            for key, value in arms["verified"]["payload_claims"].items()
        ):
            raise ValueError("Paired Judgement arms changed original Claims")
        records.append(
            {"key": key, "split": manifest["split"], "mapping": mapping, "arms": arms}
        )
    return manifest, records


def aggregate(values):
    numerators = [value["numerator"] for value in values]
    denominators = [value["denominator"] for value in values]
    return {
        **ratio(sum(numerators), sum(denominators)),
        "cluster_bootstrap95": cluster_interval(numerators, denominators),
    }


def observed(outcome):
    return outcome["status"] == "no_accepted_claims" or (
        outcome["status"] in ("completed", "protocol_violation")
        and outcome["propagation"] is not None
    )


def exposure(outcome):
    if outcome["status"] == "no_accepted_claims":
        return ratio(
            0, outcome["admission"]["non_attributable_admission"]["denominator"]
        )
    return outcome["propagation"][
        "non_attributable_citation_exposure_including_rejected"
    ]


def summarize(records):
    paired = [
        record
        for record in records
        if all(observed(record["arms"][arm]) for arm in ARMS)
    ]
    result = {
        "clusters": len(records),
        "rows": sum(len(record["mapping"]) for record in records),
        "observable_pairs": len(paired),
    }
    for arm in ARMS:
        outcomes = [record["arms"][arm] for record in records]
        calls = [call for outcome in outcomes for call in outcome["calls"]]
        elapsed = [
            call["elapsed_ms"] for call in calls if call.get("elapsed_ms") is not None
        ]
        responses = [
            response for outcome in outcomes for response in outcome["raw_responses"]
        ]
        result[arm] = {
            "status_counts": dict(Counter(outcome["status"] for outcome in outcomes)),
            "unsupported_admission": aggregate(
                [
                    outcome["admission"]["non_attributable_admission"]
                    for outcome in outcomes
                ]
            ),
            "supported_retention": aggregate(
                [
                    outcome["admission"]["attributable_admission_retention"]
                    for outcome in outcomes
                ]
            ),
            "admitted_rows": sum(
                outcome["admission"]["accepted_rows"] for outcome in outcomes
            ),
            "withheld_rows": sum(
                outcome["admission"]["original_rows"]
                - outcome["admission"]["accepted_rows"]
                for outcome in outcomes
            ),
            "paired_unsupported_citation_utilization": aggregate(
                [exposure(record["arms"][arm]) for record in paired]
            )
            if paired
            else None,
            "paired_supported_citation_utilization": aggregate(
                [
                    ratio(
                        0,
                        record["arms"][arm]["admission"][
                            "attributable_admission_retention"
                        ]["denominator"],
                    )
                    if record["arms"][arm]["status"] == "no_accepted_claims"
                    else record["arms"][arm]["propagation"][
                        "attributable_downstream_retention"
                    ]
                    for record in paired
                ]
            )
            if paired
            else None,
            "paired_clusters_with_unsupported_citation": sum(
                exposure(record["arms"][arm])["numerator"] > 0 for record in paired
            ),
            "stage_calls_recorded": len(calls),
            "captured_http_responses": len(responses),
            "captured_cost_usd": sum(
                response.get("usage", {}).get("cost", 0) or 0 for response in responses
            ),
            "stage_mean_ms": float(np.mean(elapsed)) if elapsed else None,
            "stage_p95_ms": float(np.quantile(elapsed, 0.95)) if elapsed else None,
        }
    if paired:
        first = [exposure(record["arms"]["unfiltered"]) for record in paired]
        second = [exposure(record["arms"]["verified"]) for record in paired]
        result["paired_test"] = mcnemar(
            [item["numerator"] > 0 for item in first],
            [item["numerator"] > 0 for item in second],
        )
        result["utilization_delta_cluster_bootstrap95"] = paired_cluster_delta(
            [item["numerator"] for item in first],
            [item["numerator"] for item in second],
            [item["denominator"] for item in first],
        )
    result["excluded_pairs"] = [
        {
            "cluster": record["key"],
            "split": record["split"],
            "statuses": {arm: record["arms"][arm]["status"] for arm in ARMS},
        }
        for record in records
        if record not in paired
    ]
    return result


def run(directories: list[Path], output: Path):
    loaded = [load_run(directory) for directory in directories]
    manifest = loaded[0][0]
    for other, _ in loaded[1:]:
        for key in ("judgement_config", "temperature", "prompt_sha256", "language"):
            if manifest[key] != other[key]:
                raise ValueError("Combined runs have different Judgement protocols")
    records = [record for _, items in loaded for record in items]
    if len({record["key"] for record in records}) != len(records):
        raise ValueError("Duplicate cluster in combined result")
    result = {
        "scope": "Benchmark row-local attribution admission and summary Claim ID utilization; final semantic factuality unassessed",
        "input_directories": [str(directory.resolve()) for directory in directories],
        "protocol": {
            key: manifest[key]
            for key in ("judgement_config", "temperature", "prompt_sha256", "language")
        },
        "overall": summarize(records),
        "splits": {
            split: summarize([record for record in records if record["split"] == split])
            for split in sorted({record["split"] for record in records})
        },
        "uncertainty": "2000 cluster bootstrap samples, seed 20261007; exact paired McNemar on observable output/abstention pairs; failed generations excluded, not scored safe",
        "limitations": [
            "Small label-blind cluster sample; no claim of population representativeness",
            "Gold is Claim/reference-row-local, including duplicate wording",
            "Some initial calls predate raw response capture; captured HTTP count and cost are lower bounds",
            "Classifier caches reused; this run does not measure verifier latency",
            "Admitted Claims retain original citation passages; excluded unit text or another Claim can expose the same proposition",
            "No Reader, final-summary verifier, gap or MITRE semantic evaluation",
        ],
    }
    output.mkdir(parents=True, exist_ok=True)
    save(output / "summary.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Matched B1-LR downstream receipts; incomplete arms fail"
    )
    parser.add_argument("--runs", nargs="+", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.runs, args.output)))


if __name__ == "__main__":
    main()
