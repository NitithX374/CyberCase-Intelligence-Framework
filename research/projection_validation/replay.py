from __future__ import annotations

import argparse
import asyncio
import random
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from unittest.mock import patch

from research.projection_validation.runtime import (
    HERE,
    digest,
    file_digest,
    initialize,
    read_json,
    read_rows,
    write_json,
    write_rows,
)


async def execute(args) -> None:
    import httpx
    import torch

    from app.analysis.prompts import CASE_JUDGEMENT_SYSTEM_PROMPT
    from app.config import settings
    from app.llm import request as provider
    from app.llm.settings import configured_pipeline
    from app.trace import nli_model
    from app.trace.trace import CaseProviderJudgement

    from research.projection_validation.measurement import MeasuredScorer
    from research.projection_validation.provider_capture import Budget, recorded_post
    from research.projection_validation.replay_inputs import replay_input

    config = configured_pipeline()
    if config.model != "google/gemma-4-26b-a4b-it" or config.providers != (
        "nextbit/bf16",
        "coreweave/bf16",
    ):
        raise ValueError(
            "Configured Judgement model/providers differ from the frozen bounded replay protocol."
        )
    if args.output.exists():
        raise FileExistsError(args.output)
    manifest = read_json(HERE / "data/manifest.json")
    assert file_digest(HERE / "data/benchmark.jsonl") == manifest["benchmark_sha256"]
    assert (
        file_digest(HERE / "data/propagation_plan.jsonl")
        == manifest["propagation_plan_sha256"]
    )
    cases = {row["case_id"]: row for row in read_rows(HERE / "data/benchmark.jsonl")}
    grounded = {
        row["case_id"]: row
        for row in read_rows(args.local_results / "grounded_readings.jsonl")
    }
    plans = read_rows(HERE / "data/propagation_plan.jsonl")
    assert len(plans) == 20
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://openrouter.ai/api/v1/models/google/gemma-4-26b-a4b-it/endpoints",
            timeout=30,
        )
        response.raise_for_status()
        pricing = response.json()
    write_json(args.output / "provider_metadata.json", pricing)
    endpoints = pricing["data"]["endpoints"]
    selected = [
        endpoint for endpoint in endpoints if endpoint.get("tag") in config.providers
    ]
    if not selected:
        raise ValueError("Pinned provider endpoint prices could not be verified.")
    input_price = max(float(endpoint["pricing"]["prompt"]) for endpoint in selected)
    output_price = max(
        float(endpoint["pricing"]["completion"]) for endpoint in selected
    )
    budget = Budget(args.cap_usd, max(input_price, 0.10e-6), max(output_price, 0.30e-6))
    torch.set_num_threads(args.threads)
    settings.quote_meaning_pointer_path = str(args.nli_path)
    nli_model.forget()
    scorer = MeasuredScorer(nli_model.load_nli())
    inputs = [
        replay_input(
            cases[plan["case_id"]], plan, grounded[plan["case_id"]], lambda: scorer
        )
        for plan in plans
    ]
    write_rows(args.output / "inputs.jsonl", inputs)
    calls = []
    responses = []
    original = provider.post_stage
    order = random.Random(20261006)
    jobs = []
    for index, replay in enumerate(inputs):
        conditions = ["no_validation", "semantic"]
        order.shuffle(conditions)
        jobs.append((index, replay, conditions))
    write_json(
        args.output / "run.json",
        {
            "started_at": datetime.now(timezone.utc).isoformat(),
            "benchmark_sha256": manifest["benchmark_sha256"],
            "config": config.model_dump(mode="json"),
            "prompt_sha256": digest(CASE_JUDGEMENT_SYSTEM_PROMPT),
            "temperature": None,
            "condition_order": {
                replay["replay_id"]: conditions for _, replay, conditions in jobs
            },
            "input_price_per_token": budget.input_price,
            "output_price_per_token": budget.output_price,
            "cap_usd": args.cap_usd,
            "concurrency": 2,
            "seed_for_order_only": 20261006,
            "nli_model": scorer.name,
            "nli_path": str(args.nli_path),
        },
    )
    limit = asyncio.Semaphore(2)

    async def run_pair(index, replay, conditions):
        async with limit:
            for condition in conditions:
                stage = f"projection_eval_{index:02d}_{condition}"
                started = perf_counter()
                record = {
                    "replay_id": replay["replay_id"],
                    "condition": condition,
                    "stage": stage,
                    "input_sha256": digest(replay["conditions"][condition]),
                }
                try:
                    judgement = await provider.request_stage(
                        config=config,
                        stage=stage,
                        system=CASE_JUDGEMENT_SYSTEM_PROMPT,
                        content=replay["conditions"][condition],
                        schema=CaseProviderJudgement,
                        calls=calls,
                    )
                except Exception as error:
                    record.update(
                        status="failed",
                        error_type=type(error).__name__,
                        error=str(error),
                    )
                else:
                    record.update(
                        status="completed", judgement=judgement.model_dump(mode="json")
                    )
                record["seconds"] = perf_counter() - started
                record["responses"] = [
                    response for response in responses if response["stage"] == stage
                ]
                record["calls"] = [call for call in calls if call["stage"] == stage]
                write_json(
                    args.output / "outputs" / f"{index:02d}_{condition}.json", record
                )
                print(
                    stage,
                    record["status"],
                    round(record["seconds"], 2),
                    "seconds",
                    flush=True,
                )

    with patch.object(
        provider, "post_stage", recorded_post(original, budget, responses)
    ):
        await asyncio.gather(*(run_pair(*job) for job in jobs))
    write_json(
        args.output / "execution_summary.json",
        {
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "stages": len(calls),
            "post_stage_requests": budget.requests,
            "estimated_usd": budget.spent,
            "calls": calls,
            "failed_stages": sum(call.get("status") != "completed" for call in calls),
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--local-results", type=Path, default=HERE / "results/pinned_cpu"
    )
    parser.add_argument("--nli-path", type=Path, required=True)
    parser.add_argument("--threads", type=int, default=2)
    parser.add_argument("--cap-usd", type=float, default=1.0)
    parser.add_argument("--output", type=Path, default=HERE / "results/judgement")
    args = parser.parse_args()
    for name in ("local_results", "nli_path", "output"):
        setattr(args, name, getattr(args, name).resolve())
    initialize()
    asyncio.run(execute(args))


if __name__ == "__main__":
    main()
