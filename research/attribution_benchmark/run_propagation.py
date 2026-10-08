from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY / "backend"))
sys.path.insert(0, str(REPOSITORY))

from app.analysis.prompts import CASE_JUDGEMENT_SYSTEM_PROMPT
from app.llm.settings import AnalysisPipelineConfig

from research.attribution_benchmark.champion import champion_inputs
from research.attribution_benchmark.receipts import (
    digest,
    git_receipt,
    now,
    save,
    source_receipt,
)
from research.attribution_benchmark.propagation_data import (
    MAX_DRY_RUN_CLUSTERS,
    SPLITS,
    load_inputs,
)
from research.attribution_benchmark.propagation_judgement import judge, prepare_payload
from research.attribution_benchmark.propagation_execution import (
    execute_arm,
    existing_outcome,
)
from research.attribution_benchmark.propagation_metrics import (
    admission_metrics,
)


def arguments(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bounded AttributionBench row-ID propagation dry run; offline by default"
    )
    verifier = parser.add_mutually_exclusive_group(required=True)
    verifier.add_argument(
        "--champion", action="store_true", help="Frozen WiCE TRAIN B1-LR"
    )
    verifier.add_argument(
        "--verifier-run",
        type=Path,
        help="Existing complete, independently verified candidate run",
    )
    parser.add_argument("--split", choices=SPLITS, default="dev")
    parser.add_argument("--limit", type=int, default=1)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Explicitly enable bounded live Judgement requests",
    )
    parser.add_argument(
        "--judgement-model",
        help="Explicit provider/model identifier; required with --execute",
    )
    parser.add_argument("--judgement-providers", default="")
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Retain every recorded arm, continue only missing arms",
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Record generation failures separately; never treat them as safe summaries",
    )
    args = parser.parse_args(argv)
    if args.execute and not args.judgement_model:
        parser.error("--execute requires --judgement-model")
    maximum = 100 if args.champion else MAX_DRY_RUN_CLUSTERS
    if not 1 <= args.limit <= maximum:
        parser.error(f"--limit must be 1..{maximum}")
    return args


async def run(args: argparse.Namespace) -> Path:
    if args.execute and not args.judgement_model:
        raise ValueError("Live Judgement requires an explicit model identifier")
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    output = (
        args.output or Path(__file__).resolve().parent / "propagation_runs" / timestamp
    )
    output = output.resolve()
    resume = getattr(args, "resume", False)
    output.mkdir(parents=True, exist_ok=resume)
    previous_manifest = (
        json.loads((output / "manifest.json").read_text(encoding="utf-8"))
        if resume
        else None
    )
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
    if not resume:
        save(output / "manifest.json", manifest)
    outcomes = []
    try:
        dataset, verifier, clusters, selection = (
            champion_inputs(args.split, args.limit)
            if getattr(args, "champion", False)
            else load_inputs(args.split, args.limit, args.verifier_run)
        )
        config = (
            AnalysisPipelineConfig(
                model=args.judgement_model,
                providers=tuple(
                    provider.strip()
                    for provider in getattr(args, "judgement_providers", "").split(",")
                    if provider.strip()
                ),
            )
            if args.judgement_model
            else None
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
        if previous_manifest:
            keys = (
                "dataset",
                "verifier",
                "cluster_keys",
                "judgement_config",
                "temperature",
                "prompt_sha256",
            )
            if any(previous_manifest[key] != manifest[key] for key in keys):
                raise ValueError(
                    "Resumed protocol differs from frozen original inputs/configuration"
                )
            save(output / "manifest_before_resume.json", previous_manifest)
            manifest["resumed_at"] = now()
        save(output / "manifest.json", manifest)
        (output / "judgement_prompt.txt").write_text(
            CASE_JUDGEMENT_SYSTEM_PROMPT, encoding="utf-8"
        )
        for cluster in clusters:
            directory = output / cluster.key
            directory.mkdir(exist_ok=resume)
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
                claim_id
                for claim_id, row in cluster.assigned_rows
                if verifier.accepts(row)
            }
            for arm, accepted in (("unfiltered", all_ids), ("verified", verified_ids)):
                arm_directory = directory / arm
                arm_directory.mkdir(exist_ok=resume)
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
                saved = existing_outcome(arm_directory, outcome) if resume else None
                if saved and saved["status"] != "prepared":
                    outcomes.append(saved)
                    continue
                outcomes.append(outcome)
                save(arm_directory / "outcome.json", outcome)
                if not accepted:
                    outcome["status"] = "no_accepted_claims"
                elif args.execute:
                    await execute_arm(
                        arm_directory,
                        cluster,
                        accepted,
                        payload,
                        config,
                        outcome,
                        save,
                        judge,
                        record_only=getattr(args, "continue_on_error", False),
                    )
                save(arm_directory / "outcome.json", outcome)
        manifest.update(
            {
                "status": (
                    "completed_with_failures"
                    if any(
                        outcome["status"] in ("failed", "protocol_violation", "running")
                        for outcome in outcomes
                    )
                    else "completed"
                )
                if args.execute
                else "prepared",
                "finished_at": now(),
            }
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
    print(
        json.dumps(
            {"output": str(output), "status": read_status(output)}, ensure_ascii=False
        )
    )


def read_status(output: Path) -> str:
    return json.loads((output / "manifest.json").read_text(encoding="utf-8"))["status"]


if __name__ == "__main__":
    main()
