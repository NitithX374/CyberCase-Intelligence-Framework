from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from research.attribution_benchmark.data import cluster_key, read_split, sha256, verify_manifest

MAX_DRY_RUN_CLUSTERS = 5
SPLITS = ("dev", "test", "test_ood")


@dataclass(frozen=True)
class ResponseCluster:
    key: str
    rows: tuple[dict, ...]

    @property
    def assigned_rows(self) -> tuple[tuple[str, dict], ...]:
        return tuple((f"A-{index:02d}", row) for index, row in enumerate(self.rows, 1))


def select_clusters(rows: list[dict], limit: int) -> tuple[tuple[ResponseCluster, ...], dict]:
    if not 1 <= limit <= MAX_DRY_RUN_CLUSTERS:
        raise ValueError(f"Dry runs require 1..{MAX_DRY_RUN_CLUSTERS} clusters")
    if len({row["id"] for row in rows}) != len(rows):
        raise ValueError("Benchmark row IDs must be unique")
    grouped = defaultdict(list)
    for row in rows:
        grouped[cluster_key(row)].append(row)
    eligible = []
    exclusions = {"fewer_than_two_distinct_claims": 0, "empty_reference_bundle": 0}
    for key, members in sorted(grouped.items()):
        if len({row["claim"] for row in members}) < 2:
            exclusions["fewer_than_two_distinct_claims"] += 1
        elif any(not row["references"] for row in members):
            exclusions["empty_reference_bundle"] += 1
        else:
            eligible.append(ResponseCluster(key, tuple(sorted(members, key=lambda row: row["id"]))))
    if len(eligible) < limit:
        raise ValueError("Not enough eligible response clusters")
    return tuple(eligible[:limit]), {
        "total_clusters": len(grouped),
        "eligible_clusters": len(eligible),
        "excluded_clusters": exclusions,
        "selection": "first cluster hashes; >=2 distinct claim texts; all rows have references",
        "row_order": "original row ID ascending; A IDs assigned before admission",
        "duplicate_policy": "retain every original row and its separate evidence bundle",
    }


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_text_hash(path: Path, expected: str) -> dict:
    original = path.read_bytes()
    lf = original.replace(b"\r\n", b"\n")
    encodings = {"LF": lf, "CRLF": lf.replace(b"\n", b"\r\n")}
    matches = [
        name
        for name, content in encodings.items()
        if hashlib.sha256(content).hexdigest() == expected
    ]
    if not matches:
        raise ValueError(f"Frozen artifact hash mismatch: {path.name}")
    return {
        "physical_sha256": hashlib.sha256(original).hexdigest(),
        "lf_sha256": hashlib.sha256(lf).hexdigest(),
        "recorded_sha256": expected,
        "recorded_newlines": matches,
    }


@dataclass(frozen=True)
class FrozenVerifier:
    threshold: float
    scores: dict[str, dict]
    receipt: dict

    def accepts(self, row: dict) -> bool:
        return self.scores[row["id"]]["p_supported"] >= self.threshold


def load_verifier(run: Path, split: str, rows: list[dict], dataset: dict) -> FrozenVerifier:
    run = run.resolve()
    names = ("run_manifest.json", "summary.json", "selection.json", "verification.json")
    manifest, summary, selection, verification = (read_json(run / name) for name in names)
    if manifest["status"] != "complete" or verification["status"] != "passed":
        raise ValueError("Verifier run must be complete and independently verified")
    if manifest["summary_sha256"] != verification["summary_sha256"]:
        raise ValueError("Frozen verifier summary hash mismatch")
    frozen_hashes = {
        "summary.json": verify_text_hash(run / "summary.json", manifest["summary_sha256"])
    }
    for recorded in (manifest["dataset"], summary["dataset"]):
        if any(
            recorded[key] != dataset[key]
            for key in ("dataset", "configuration", "revision", "files")
        ):
            raise ValueError("Verifier dataset differs from pinned raw data")
    if manifest["model"] != summary["model"] or verification["model"] != manifest["model"]["key"]:
        raise ValueError("Frozen verifier model identity mismatch")
    if not manifest["model"]["revision"] or selection != summary["selection"]:
        raise ValueError("Frozen model revision/selection mismatch")
    threshold = selection["threshold"]
    if (
        isinstance(threshold, bool)
        or not isinstance(threshold, (int, float))
        or not 0 <= threshold <= 1
    ):
        raise ValueError("Invalid frozen threshold")
    if verification["threshold"] != threshold:
        raise ValueError("Verified threshold differs from selection")
    if not selection["selection"].startswith("EN dev only;"):
        raise ValueError("Threshold must have been selected on English dev only")
    hashes = {name: sha256(run / name) for name in names}
    for score_split in dict.fromkeys(("dev", split)):
        filename = f"scores_{score_split}.jsonl"
        hashes[filename] = sha256(run / filename)
        frozen_hashes[filename] = verify_text_hash(
            run / filename, summary["score_sha256"][score_split]
        )
    if summary["score_sha256"]["dev"] != selection["dev_scores_sha256"]:
        raise ValueError("Frozen dev selection hash mismatch")
    scores = {}
    score_rows = [
        json.loads(line)
        for line in (run / f"scores_{split}.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    if len(score_rows) != len(rows):
        raise ValueError("Frozen score row count mismatch")
    for index, (row, score) in enumerate(zip(rows, score_rows, strict=True)):
        expected = {
            "split": split,
            "row_index": index,
            "id": row["id"],
            "src_dataset": row["src_dataset"],
            "gold": row["attribution_label"],
            "cluster": cluster_key(row),
            "claim": row["claim"],
            "references": row["references"],
        }
        if any(score[key] != value for key, value in expected.items()):
            raise ValueError(f"Frozen score input identity mismatch: {row['id']}")
        probability = score["p_supported"]
        if (
            isinstance(probability, bool)
            or not isinstance(probability, (float, int))
            or not math.isfinite(probability)
            or not 0 <= probability <= 1
        ):
            raise ValueError(f"Invalid frozen probability: {row['id']}")
        if row["id"] in scores:
            raise ValueError("Duplicate frozen score row ID")
        scores[row["id"]] = score
    return FrozenVerifier(
        float(threshold),
        scores,
        {
            "path": str(run),
            "model": manifest["model"],
            "threshold": threshold,
            "selection_rule": selection["selection"],
            "artifact_sha256": hashes,
            "frozen_text_hashes": frozen_hashes,
            "text_hash_policy": "Only LF/CRLF file line endings are equivalent; file content and raw row fields unchanged",
            "admission_rule": "cached p_supported >= frozen threshold; no inference or tuning",
        },
    )


def load_inputs(split: str, limit: int, run: Path):
    if split not in SPLITS:
        raise ValueError("Use an existing dev/test/test_ood split")
    dataset = verify_manifest()
    rows = read_split(split)
    verifier = load_verifier(run, split, rows, dataset)
    clusters, selection = select_clusters(rows, limit)
    return dataset, verifier, clusters, selection
