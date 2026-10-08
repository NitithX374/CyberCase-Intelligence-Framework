from __future__ import annotations

import json
import re
from pathlib import Path

from app.trace.b1_verifier import (
    ARTIFACT,
    ARTIFACT_SHA256,
    THRESHOLD,
    supported_probability,
)

from research.attribution_benchmark.data import read_split, sha256, verify_manifest
from research.attribution_benchmark.propagation_data import (
    FrozenVerifier,
    select_clusters,
)

EXPERIMENT = Path(__file__).resolve().parents[2] / "nli_grounding_experiment"
CACHE_SPLITS = {"test": "id", "test_ood": "ood"}


def reference_units(text: str) -> list[str]:
    if not text.strip():
        return []
    units = [
        sentence.strip()
        for paragraph in text.split("\n")
        if paragraph.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", paragraph.strip())
        if len(sentence.strip()) > 3
    ]
    return units or [text.strip()]


def row_units(row: dict) -> list[str]:
    return [
        unit for reference in row["references"] for unit in reference_units(reference)
    ]


def load_champion(split: str, rows: list[dict]) -> FrozenVerifier:
    if split not in CACHE_SPLITS:
        raise ValueError("Frozen B1-LR transfer uses test and test_ood only")
    manifest = json.loads(
        Path(__file__).with_name("b1_cache_manifest.json").read_text(encoding="utf-8")
    )
    for filename, expected in manifest["files"].items():
        if sha256(EXPERIMENT / filename) != expected:
            raise ValueError(f"Frozen champion asset changed: {filename}")
    artifact = EXPERIMENT / "outputs/canonical/final_lr_coefficients.json"
    if sha256(artifact) != ARTIFACT["source_artifact_sha256"]:
        raise ValueError("Original frozen LR artifact changed")
    canonical = json.loads(artifact.read_text(encoding="utf-8"))["mdeberta_b1_lr"]
    if any(
        canonical[key] != ARTIFACT[key] for key in ("features", "weights", "intercept")
    ):
        raise ValueError("Production coefficients differ from the research champion")
    cache = (
        EXPERIMENT
        / f"cache/forward_nli/attrbench_{CACHE_SPLITS[split]}_forward_filt_0_20.jsonl"
    )
    records = [
        json.loads(line)
        for line in cache.read_text(encoding="utf-8").splitlines()
        if line
    ]
    if len(records) != len(rows):
        raise ValueError("Frozen feature count differs from original benchmark")
    scores = {}
    for row, record in zip(rows, records, strict=True):
        gold = int(row["attribution_label"] == "attributable")
        if record["example_id"] != row["id"] or record["gold_label_binary"] != gold:
            raise ValueError("Frozen feature identity/gold mismatch")
        if row["id"] in scores:
            raise ValueError("Duplicate benchmark row ID")
        vector = [
            record[f"p_{label}"] for label in ("entailment", "neutral", "contradiction")
        ]
        scores[row["id"]] = {
            "p_supported": supported_probability(vector),
            "lengths": {
                "tokens": record["num_tokens"],
                "truncated": record["truncated"],
            },
            "nli_probabilities": vector,
        }
    return FrozenVerifier(
        THRESHOLD,
        scores,
        {
            "method": ARTIFACT["method"],
            "artifact_sha256": ARTIFACT_SHA256,
            "source_artifact_sha256": sha256(artifact),
            "features_sha256": sha256(cache),
            "threshold": THRESHOLD,
            "fit": ARTIFACT["fit_dataset"],
            "admission_rule": "frozen WiCE TRAIN LR on cached ordered E/N/C features >= 0.50",
            "cache_input_validation": "Original corpus hash plus cached row IDs/gold; features lack claim/reference hashes",
        },
    )


def champion_inputs(split: str, limit: int):
    dataset = verify_manifest()
    rows = read_split(split)
    verifier = load_champion(split, rows)
    clusters, selection = select_clusters(rows, limit, maximum=100)
    return dataset, verifier, clusters, selection
