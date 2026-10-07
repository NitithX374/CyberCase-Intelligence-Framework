from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY / "backend"))
sys.path.insert(0, str(REPOSITORY))

from app.analysis.prompts import CASE_JUDGEMENT_SYSTEM_PROMPT
from app.llm.settings import AnalysisPipelineConfig

from research.attribution_benchmark.data import sha256
from research.attribution_benchmark.propagation_data import (
    MAX_DRY_RUN_CLUSTERS,
    SPLITS,
    load_inputs,
)
from research.attribution_benchmark.propagation_judgement import judge, prepare_payload
from research.attribution_benchmark.propagation_metrics import (
    admission_metrics,
    propagation_metrics,
)


def now() -> str:
    return datetime.now(UTC).isoformat()


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()


def save(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def git_receipt() -> dict:
    def git(*args):
        return subprocess.check_output(
            ["git", *args], cwd=REPOSITORY, text=True, encoding="utf-8"
        ).strip()

    return {
        "head": git("rev-parse", "HEAD"),
        "branch": git("branch", "--show-current"),
        "status": git("status", "--short"),
    }


def source_receipt() -> dict:
    paths = [
        "research/attribution_benchmark/data.py",
        "research/attribution_benchmark/propagation_data.py",
        "research/attribution_benchmark/propagation_judgement.py",
        "research/attribution_benchmark/propagation_metrics.py",
        "research/attribution_benchmark/run_propagation.py",
        "backend/app/analysis/write.py",
        "backend/app/analysis/prompts.py",
        "backend/app/trace/claims.py",
        "backend/app/trace/citations.py",
        "backend/app/trace/evidence_binding.py",
        "backend/app/trace/trace.py",
        "backend/app/trace/summary.py",
        "backend/app/sources/evidence.py",
        "backend/app/llm/request.py",
        "backend/app/llm/settings.py",
    ]
    return {path: sha256(REPOSITORY / path) for path in paths}


def arguments(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bounded AttributionBench row-ID propagation dry run; offline by default"
    )
    parser.add_argument(
        "--verifier-run",
        type=Path,
        required=True,
        help="Existing complete, independently verified candidate run",
    )
    parser.add_argument("--split", choices=SPLITS, default="dev")
    parser.add_argument("--limit", type=int, choices=range(1, MAX_DRY_RUN_CLUSTERS + 1), default=1)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--execute", action="store_true", help="Explicitly enable bounded live Judgement requests"
    )
    parser.add_argument(
        "--judgement-model", help="Explicit provider/model identifier; required with --execute"
    )
    args = parser.parse_args(argv)
    if args.execute and not args.judgement_model:
        parser.error("--execute requires --judgement-model")
    return args


async def run(args: argparse.Namespace) -> Path:
    if args.execute and not args.judgement_model:
        raise ValueError("Live Judgement requires an explicit model identifier")
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    output = args.output or Path(__file__).resolve().parent / "propagation_runs" / timestamp
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    manifest = {
        "schema_version": "claim_propagation_dry_run_v1",
        "status": "preparing",
        "started_at": now(),
        "mode": "live_judgement" if args.execute else "offline_preparation",
        "split": args.split,
        "limit": args.limit,
        "maximum_judgement_stage_calls": 2 * args.limit if args.execute else 0,
        "scope": "Benchmark-labelled claim-evidence row citation propagation; semantic factuality unassessed",
        "command": sys.argv,
        "python": sys.version,
        "reader_requests": 0,
        "verifier_inference_requests": 0,
    }
    save(output / "manifest.json", manifest)
    outcomes = []
    try:
        dataset, verifier, clusters, selection = load_inputs(
            args.split, args.limit, args.verifier_run
        )
        config = (
            AnalysisPipelineConfig(model=args.judgement_model) if args.judgement_model else None
        )
        manifest.update(
            {
                "git": git_receipt(),
                "source_sha256": source_receipt(),
                "dataset": dataset,
                "verifier": verifier.receipt,
                "cluster_selection": selection,
                "cluster_keys": [cluster.key for cluster in clusters],
                "judgement_config": config.model_dump(mode="json") if config else None,
                "temperature": 0,
                "language": "en",
                "followup_history": [],
                "technical_context": None,
                "prompt_sha256": hashlib.sha256(
                    CASE_JUDGEMENT_SYSTEM_PROMPT.encode("utf-8")
                ).hexdigest(),
                "status": "running" if args.execute else "preparing",
            }
        )
        save(output / "manifest.json", manifest)
        (output / "judgement_prompt.txt").write_text(CASE_JUDGEMENT_SYSTEM_PROMPT, encoding="utf-8")
        for cluster in clusters:
            directory = output / cluster.key
            directory.mkdir()
            mapping = [
                {
                    "claim_id": claim_id,
                    "row_id": row["id"],
                    "src_dataset": row["src_dataset"],
                    "gold": row["attribution_label"],
                    "claim_sha256": digest(row["claim"]),
                    "references_sha256": digest(row["references"]),
                    "reference_source_ids": [
                        f"R-{row['id']}-ref-{index:02d}"
                        for index in range(1, len(row["references"]) + 1)
                    ],
                    "p_supported": verifier.scores[row["id"]]["p_supported"],
                    "verifier_input_lengths": verifier.scores[row["id"]]["lengths"],
                }
                for claim_id, row in cluster.assigned_rows
            ]
            save(directory / "row_mapping.json", mapping)
            all_ids = {claim_id for claim_id, _ in cluster.assigned_rows}
            verified_ids = {
                claim_id for claim_id, row in cluster.assigned_rows if verifier.accepts(row)
            }
            for arm, accepted in (("unfiltered", all_ids), ("verified", verified_ids)):
                arm_directory = directory / arm
                arm_directory.mkdir()
                payload = prepare_payload(cluster, accepted)
                save(arm_directory / "request.json", payload)
                outcome = {
                    "cluster": cluster.key,
                    "arm": arm,
                    "accepted_claim_ids": sorted(accepted),
                    "payload_sha256": digest(payload),
                    "admission": admission_metrics(cluster, accepted),
                    "propagation": None,
                    "status": "prepared",
                    "calls": [],
                }
                outcomes.append(outcome)
                save(arm_directory / "outcome.json", outcome)
                if not accepted:
                    outcome["status"] = "no_accepted_claims"
                elif args.execute:
                    outcome["status"] = "running"
                    try:
                        judgement = await judge(payload, config, outcome["calls"])
                        save(arm_directory / "judgement.json", judgement.model_dump(mode="json"))
                        outcome["propagation"] = propagation_metrics(
                            cluster, accepted, judgement.summary
                        )
                        outcome["status"] = (
                            "completed"
                            if outcome["propagation"]["protocol_valid"]
                            else "protocol_violation"
                        )
                        if outcome["status"] == "protocol_violation":
                            raise ValueError("Judgement citation protocol violation")
                    except BaseException as error:
                        outcome.update(
                            {
                                "error_type": type(error).__name__,
                                "error": str(error),
                            }
                        )
                        if outcome["status"] != "protocol_violation":
                            outcome["status"] = "failed"
                        raise
                    finally:
                        save(arm_directory / "outcome.json", outcome)
                save(arm_directory / "outcome.json", outcome)
        manifest.update(
            {"status": "completed" if args.execute else "prepared", "finished_at": now()}
        )
        save(output / "outcomes.json", outcomes)
        save(output / "manifest.json", manifest)
        return output
    except BaseException as error:
        manifest.update({"status": "failed", "finished_at": now()})
        save(output / "manifest.json", manifest)
        save(output / "outcomes.json", outcomes)
        save(
            output / "failure.json",
            {"error_type": type(error).__name__, "error": str(error), "at": now()},
        )
        raise


def main(argv=None) -> None:
    output = asyncio.run(run(arguments(argv)))
    print(json.dumps({"output": str(output), "status": read_status(output)}, ensure_ascii=False))


def read_status(output: Path) -> str:
    return json.loads((output / "manifest.json").read_text(encoding="utf-8"))["status"]


if __name__ == "__main__":
    main()
