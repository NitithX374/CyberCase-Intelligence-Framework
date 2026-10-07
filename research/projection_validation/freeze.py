from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone

from research.projection_validation.runtime import (
    HERE,
    digest,
    file_digest,
    initialize,
    write_json,
    write_rows,
)


def freeze() -> dict:
    from app.trace.trace import CaseProviderReadingReply

    from research.projection_validation.controlled import materialize
    from research.projection_validation.real_outputs import saved_cases
    from research.projection_validation.specifications import controlled_specs

    path = HERE / "data/benchmark.jsonl"
    manifest_path = HERE / "data/manifest.json"
    if path.exists() or manifest_path.exists():
        raise FileExistsError(
            "The frozen benchmark already exists; do not overwrite it."
        )
    rows = [materialize(spec) for spec in controlled_specs()] + saved_cases()
    for row in rows:
        CaseProviderReadingReply.model_validate(row["reading"])
        row["reading_sha256"] = digest(row["reading"])
    write_rows(path, rows)
    propagation = propagation_plan(rows)
    write_rows(HERE / "data/propagation_plan.jsonl", propagation)
    annotations = [annotation for row in rows for annotation in row["annotations"]]
    manifest = {
        "version": "projection_validation_benchmark_v1",
        "frozen_at": datetime.now(timezone.utc).isoformat(),
        "annotation_method": "Independent rule-based authoring before NLI inference; no NLI-generated gold; no second human adjudicator.",
        "benchmark_sha256": file_digest(path),
        "propagation_plan_sha256": file_digest(HERE / "data/propagation_plan.jsonl"),
        "cases": len(rows),
        "case_origins": dict(Counter(row["origin"] for row in rows)),
        "projection_gold": dict(
            Counter(annotation["gold"] for annotation in annotations)
        ),
        "projection_types": dict(
            Counter(annotation["type"] for annotation in annotations)
        ),
        "origins": {
            origin: dict(
                Counter(
                    a["gold"]
                    for r in rows
                    if r["origin"] == origin
                    for a in r["annotations"]
                )
            )
            for origin in ("controlled", "saved_output")
        },
        "source_preparation": "Historical canonical citations are mapped once to overlapping Evidence Units only when exact source containment holds. Missing mappings remain unbound. Quote matching is not an experimental condition or score.",
        "statistical_unit": "Case family; bilingual controlled contexts share a family. Perturbations are clustered, not treated as independent draws.",
        "propagation_cases": len(propagation),
        "source_code_sha256": {
            name: file_digest(HERE / name)
            for name in (
                "controlled.py",
                "specifications.py",
                "real_outputs.py",
                "freeze.py",
            )
        },
    }
    write_json(manifest_path, manifest)
    return manifest


def propagation_plan(rows: list[dict]) -> list[dict]:
    output = []
    for row in rows:
        if row["origin"] != "controlled" or int(row["case_id"][-2:]) > 3:
            continue
        for kind in ("involved_parties", "timeline", "impacts"):
            output.append(
                {
                    "replay_id": f"{row['case_id']}:{kind}",
                    "case_id": row["case_id"],
                    "family_id": row["family_id"],
                    "type": kind,
                    "target_index": 1,
                    "error_scope": "projection_only",
                    "target": row["reading"][kind][1],
                    "gold": "not_supported",
                }
            )
    for scope in ("claim_level", "both"):
        output.append(
            {
                "replay_id": f"contamination:{scope}",
                "case_id": "controlled-english-01",
                "family_id": "controlled-family-01",
                "type": "involved_parties",
                "target_index": 1 if scope == "both" else None,
                "error_scope": scope,
                "target": {
                    "name": "John",
                    "role": "the attacker",
                    "claim_ids": ["A-01"],
                },
                "claim_override": {
                    "A-01": "John is the attacker and reported the incident."
                },
                "gold": "not_supported_from_source",
            }
        )
    return output


if __name__ == "__main__":
    argparse.ArgumentParser(
        description="Freeze independent labels before inference."
    ).parse_args()
    initialize()
    print(freeze())
