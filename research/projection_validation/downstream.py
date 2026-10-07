from __future__ import annotations

import argparse
import random
from collections import Counter
from pathlib import Path

from research.projection_validation.metrics import (
    paired_outcomes,
    percentile,
    ratio,
    wilson,
)
from research.projection_validation.runtime import (
    HERE,
    digest,
    read_json,
    read_rows,
    write_json,
    write_rows,
)


def output_text(judgement: dict) -> str:
    def strings(value):
        if isinstance(value, str):
            return [value]
        if isinstance(value, list):
            return [text for item in value for text in strings(item)]
        if isinstance(value, dict):
            return [
                text
                for key, item in value.items()
                if key not in {"claim_ids", "version"}
                for text in strings(item)
            ]
        return []

    return "\n".join(strings(judgement))


def annotation_packet(directory: Path) -> None:
    inputs = {row["replay_id"]: row for row in read_rows(directory / "inputs.jsonl")}
    paths = sorted((directory / "outputs").glob("*.json"))
    random.Random(20261006).shuffle(paths)
    packet, mapping = [], []
    for index, path in enumerate(paths, 1):
        result = read_json(path)
        replay = inputs[result["replay_id"]]
        annotation_id = f"J{index:03d}"
        packet.append(
            {
                "annotation_id": annotation_id,
                "type": replay["type"],
                "language": replay["language"],
                "target_statement": replay["target_statement"],
                "status": result["status"],
                "judgement": result.get("judgement"),
                "judgement_sha256": digest(result.get("judgement")),
            }
        )
        mapping.append(
            {
                "annotation_id": annotation_id,
                "replay_id": replay["replay_id"],
                "condition": result["condition"],
                "output_path": str(path),
                "judgement_sha256": digest(result.get("judgement")),
            }
        )
    for name in ("annotation_packet.jsonl", "annotation_mapping.jsonl"):
        if (directory / name).exists():
            raise FileExistsError(directory / name)
    write_rows(directory / "annotation_packet.jsonl", packet)
    write_rows(directory / "annotation_mapping.jsonl", mapping)


def score(directory: Path, annotations: Path) -> dict:
    inputs = {row["replay_id"]: row for row in read_rows(directory / "inputs.jsonl")}
    packet = {
        row["annotation_id"]: row
        for row in read_rows(directory / "annotation_packet.jsonl")
    }
    mapping = {
        row["annotation_id"]: row
        for row in read_rows(directory / "annotation_mapping.jsonl")
    }
    labelled = read_rows(annotations)
    assert len({row["annotation_id"] for row in labelled}) == len(labelled)
    assert set(packet) == {row["annotation_id"] for row in labelled}
    paired = {}
    decisions = []
    for annotation in labelled:
        key = annotation["annotation_id"]
        observed = packet[key]
        location = mapping[key]
        assert (
            annotation["judgement_sha256"]
            == observed["judgement_sha256"]
            == location["judgement_sha256"]
        )
        replay = inputs[location["replay_id"]]
        if observed["status"] != "completed":
            assert annotation["unsupported_assertion"] is None
            continue
        assert isinstance(annotation["unsupported_assertion"], bool)
        assert annotation["rationale"]
        if annotation["unsupported_assertion"]:
            assert annotation["excerpt"] and annotation["excerpt"] in output_text(
                observed["judgement"]
            )
        paired.setdefault(replay["replay_id"], {})[location["condition"]] = annotation[
            "unsupported_assertion"
        ]
        decisions.append(
            {
                **annotation,
                **location,
                "error_scope": replay["error_scope"],
                "family_id": replay["family_id"],
            }
        )
    primary = {
        key: row
        for key, row in paired.items()
        if inputs[key]["error_scope"] == "projection_only"
        and set(row) == {"no_validation", "semantic"}
    }
    pairs = [(row["no_validation"], row["semantic"]) for row in primary.values()]
    result = paired_outcomes(pairs)
    result["primary_planned"] = sum(
        row["error_scope"] == "projection_only" for row in inputs.values()
    )
    result["primary_missing_pairs"] = result["primary_planned"] - len(primary)
    result["wilson_ci_descriptive"] = {
        condition: wilson(sum(row[condition] for row in primary.values()), len(primary))
        for condition in ("no_validation", "semantic")
    }
    result["cluster_bootstrap"] = propagation_bootstrap(primary, inputs)
    result["statistical_limit"] = (
        "Only three independent controlled families; exact McNemar and binomial intervals are descriptive/exploratory. Cluster intervals cannot establish broad population significance."
    )
    result["by_type"] = {
        kind: paired_outcomes(
            [
                (row["no_validation"], row["semantic"])
                for key, row in primary.items()
                if inputs[key]["type"] == kind
            ]
        )
        for kind in ("involved_parties", "timeline", "impacts")
    }
    result["contamination_diagnostics"] = {
        key: row
        for key, row in paired.items()
        if inputs[key]["error_scope"] != "projection_only"
    }
    result["annotator"] = (
        "AI-assisted independent target-assertion audit, blinded to condition/NLI verdict; no second human adjudication."
    )
    result["annotations_sha256"] = digest(labelled)
    result["target_mentions"] = dict(
        Counter(row["condition"] for row in decisions if row["target_mention"])
    )
    result["summary_change_pairs"] = sum(
        digest(
            next(
                row["judgement"]
                for key, row in packet.items()
                if mapping[key]["replay_id"] == replay_id
                and mapping[key]["condition"] == "no_validation"
            )
        )
        != digest(
            next(
                row["judgement"]
                for key, row in packet.items()
                if mapping[key]["replay_id"] == replay_id
                and mapping[key]["condition"] == "semantic"
            )
        )
        for replay_id in primary
    )
    result["admission_primary"] = {
        "total_projections": 3 * len(primary),
        "unsupported": len(primary),
        "supported": 2 * len(primary),
        "unsupported_admitted_baseline": len(primary),
        "unsupported_admitted_semantic": sum(
            inputs[key]["target_admitted"]["semantic"] for key in primary
        ),
        "supported_retained_semantic": sum(
            inputs[key]["projection_counts"]["admitted"]
            - inputs[key]["target_admitted"]["semantic"]
            for key in primary
        ),
        "withheld": sum(
            inputs[key]["projection_counts"]["withheld"] for key in primary
        ),
        "unassessed": sum(
            inputs[key]["projection_counts"]["unassessed"] for key in primary
        ),
    }
    write_rows(directory / "annotated_outcomes.jsonl", decisions)
    write_json(directory / "propagation_metrics.json", result)
    return result


def propagation_bootstrap(primary: dict, inputs: dict, samples: int = 2000) -> dict:
    families = sorted({inputs[key]["family_id"] for key in primary})
    if not families:
        return {"clusters": 0, "intervals": None}
    randomizer = random.Random(20261006)
    rates = {"no_validation": [], "semantic": [], "difference": []}
    for _ in range(samples):
        sample = [
            row
            for family in randomizer.choices(families, k=len(families))
            for key, row in primary.items()
            if inputs[key]["family_id"] == family
        ]
        baseline = ratio(sum(row["no_validation"] for row in sample), len(sample))
        semantic = ratio(sum(row["semantic"] for row in sample), len(sample))
        rates["no_validation"].append(baseline)
        rates["semantic"].append(semantic)
        rates["difference"].append(semantic - baseline)
    return {
        "clusters": len(families),
        "samples": samples,
        "seed": 20261006,
        "intervals": {
            key: [percentile(values, 0.025), percentile(values, 0.975)]
            for key, values in rates.items()
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("packet", "score"))
    parser.add_argument("--directory", type=Path, default=HERE / "results/judgement")
    parser.add_argument("--annotations", type=Path)
    args = parser.parse_args()
    if args.mode == "packet":
        annotation_packet(args.directory)
    else:
        if args.annotations is None:
            parser.error("score requires --annotations")
        print(score(args.directory, args.annotations))
