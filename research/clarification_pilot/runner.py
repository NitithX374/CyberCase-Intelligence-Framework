"""Run the four arms over one sample list and write what happened.

The sample list is drawn once and every arm runs over it, so the paired
analysis is a property of the runner rather than something the analysis has to
hope for. The three non-interactive arms run once; only bounded follow-up
repeats, once per budget, because that is the only arm a budget changes.

    python -m clarification_pilot.runner --dry-run --limit 8

from the ``research/`` directory. ``--dry-run`` needs no API key and touches no
network, which is also how the tests drive it.
"""

from __future__ import annotations

import argparse
import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path

from .arms import ARMS, INTERACTIVE_ARMS, ArmConfig
from .benchmarks import adapter_for, file_sha256, stratified
from .contracts import (
    ArmResult,
    ClarificationBenchmarkSample,
    RunManifest,
    RunOutput,
    ScoredResult,
)
from .metrics import compare, render_markdown, summarise
from .prompts import PROMPT_VERSIONS
from .provider import DEFAULT_MODEL, ModelSpec, Provider
from .scoring import score_result
from .simulator import SilentSimulator, UserSimulator

RESULTS_DIR = Path(__file__).resolve().parent / "results"
ARM_ORDER = ("direct", "multi_stage", "gap_aware", "followup")


async def run_one(
    sample: ClarificationBenchmarkSample,
    arm: str,
    provider: Provider,
    config: ArmConfig,
) -> ArmResult:
    """One arm on one sample. Only the interactive arm is given a real simulator."""

    simulator = (
        UserSimulator(provider=provider, hidden=sample.hidden)
        if arm in INTERACTIVE_ARMS
        else SilentSimulator()
    )
    try:
        return await ARMS[arm](sample.candidate, provider, simulator, config)
    except Exception as error:  # a crashed arm is a recorded result, not a lost run
        return ArmResult(
            sample_id=sample.sample_id,
            arm=arm,
            budget=config.budget,
            stop_reason="error",
            error=f"{type(error).__name__}: {error}",
        )


def jobs(
    samples: list[ClarificationBenchmarkSample],
    arms: list[str],
    budgets: list[int],
    unknown_tolerance: int,
    separate_question_call: bool,
) -> list[tuple[ClarificationBenchmarkSample, str, ArmConfig]]:
    """Every (sample, arm, budget) the run will execute, in a stable order."""

    planned = []
    for sample in samples:
        for arm in arms:
            arm_budgets = budgets if arm in INTERACTIVE_ARMS else [0]
            for budget in arm_budgets:
                planned.append(
                    (
                        sample,
                        arm,
                        ArmConfig(
                            budget=budget,
                            unknown_tolerance=unknown_tolerance,
                            separate_question_call=separate_question_call,
                        ),
                    )
                )
    return planned


def append_jsonl(path: Path, payload: dict) -> None:
    """One finished row, on disk before the next one starts.

    A run that only writes at the end is a run you lose entirely to a stopped
    process, a dropped connection or a closed laptop -- which is exactly what
    happened to a 35-minute run that was 91% done. Every row is flushed as it
    completes, so an interrupted run is a short run rather than no run.
    """

    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
        handle.flush()


async def execute(
    planned: list[tuple[ClarificationBenchmarkSample, str, ArmConfig]],
    provider: Provider,
    concurrency: int,
    sink: Path | None = None,
) -> list[ArmResult]:
    limit = asyncio.Semaphore(concurrency)
    done = 0
    total = len(planned)

    async def one(sample, arm, config):
        nonlocal done
        async with limit:
            result = await run_one(sample, arm, provider, config)
            done += 1
            if sink is not None:
                append_jsonl(sink, result.model_dump(mode="json"))
            print(
                f"  [{done}/{total}] {arm:<12} budget={config.budget} "
                f"{sample.sample_id[:12]} stop={result.stop_reason}"
                + (f" ERROR {result.error}" if result.error else ""),
                flush=True,
            )
            return result

    return list(await asyncio.gather(*(one(*job) for job in planned)))


async def score_all(
    results: list[ArmResult],
    samples: list[ClarificationBenchmarkSample],
    provider: Provider,
    *,
    judge_fallback: bool,
    measure_coverage: bool,
    concurrency: int,
    sink: Path | None = None,
) -> list[ScoredResult]:
    hidden = {sample.sample_id: sample.hidden for sample in samples}
    limit = asyncio.Semaphore(concurrency)
    done = 0
    total = len(results)

    async def one(result: ArmResult) -> ScoredResult:
        nonlocal done
        async with limit:
            scored = await score_result(
                result,
                hidden[result.sample_id],
                provider,
                judge_fallback=judge_fallback,
                measure_coverage=measure_coverage,
            )
            done += 1
            if sink is not None:
                append_jsonl(sink, scored.model_dump(mode="json"))
            if done % 25 == 0 or done == total:
                print(f"  scored {done}/{total}", flush=True)
            return scored

    return list(await asyncio.gather(*(one(result) for result in results)))


async def run(args: argparse.Namespace) -> Path:
    adapter = adapter_for(args.benchmark)
    data_path = Path(args.data) if args.data else adapter.default_path
    samples = stratified(adapter.load(data_path), limit=args.limit, seed=args.seed or 42)

    provider = Provider(
        candidate=ModelSpec(
            model=args.model,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            seed=args.seed,
        ),
        simulator=ModelSpec(
            model=args.simulator_model or args.model,
            temperature=0.0,
            max_tokens=512,
            seed=args.seed,
        ),
        judge=ModelSpec(
            model=args.judge_model or args.model,
            temperature=0.0,
            max_tokens=512,
            seed=args.seed,
        ),
        dry_run=args.dry_run,
        log_prompts=args.log_prompts,
    )

    planned = jobs(
        samples, args.arms, args.budgets, args.unknown_tolerance, args.separate_question_call
    )
    started = datetime.now(UTC)
    stamp = started.strftime("%Y%m%d_%H%M%S")
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    manifest = RunManifest(
        timestamp=started.isoformat(),
        benchmark=args.benchmark,
        dataset_path=str(data_path),
        dataset_sha256=file_sha256(data_path),
        sample_ids=[sample.sample_id for sample in samples],
        arms=list(args.arms),
        budgets=list(args.budgets),
        candidate_model=provider.candidate.model,
        simulator_model=provider.simulator.model,
        judge_model=provider.judge.model,
        temperature=provider.candidate.temperature,
        max_tokens=provider.candidate.max_tokens,
        seed=args.seed,
        prompt_versions=dict(PROMPT_VERSIONS),
        dry_run=args.dry_run,
    )
    # Written before the first call, so an interrupted run still says what it was.
    (RESULTS_DIR / f"manifest_{stamp}.json").write_text(
        manifest.model_dump_json(indent=2), encoding="utf-8"
    )
    run_sink = RESULTS_DIR / f"run_{stamp}.jsonl"
    scored_sink = RESULTS_DIR / f"scored_{stamp}.jsonl"

    print(f"benchmark      {args.benchmark} ({data_path})")
    print(f"samples        {len(samples)}")
    print(f"arms           {', '.join(args.arms)}")
    print(f"budgets        {args.budgets} (bounded follow-up only)")
    print(f"candidate      {provider.candidate.model} @ T={provider.candidate.temperature}")
    print(f"simulator      {provider.simulator.model}")
    print(f"judge          {provider.judge.model}")
    print(f"runs           {len(planned)}")
    print(f"mode           {'DRY RUN' if args.dry_run else 'LIVE'}")
    print(f"streaming to   {run_sink.name}")
    print("-" * 70)

    results = await execute(planned, provider, args.concurrency, sink=run_sink)

    print("-" * 70)
    print("scoring")
    scored = await score_all(
        results,
        samples,
        provider,
        judge_fallback=args.judge_fallback,
        measure_coverage=not args.no_coverage,
        concurrency=args.concurrency,
        sink=scored_sink,
    )

    run_path = RESULTS_DIR / f"run_{stamp}.json"
    run_path.write_text(
        RunOutput(manifest=manifest, results=results).model_dump_json(indent=2),
        encoding="utf-8",
    )

    scored_path = RESULTS_DIR / f"scored_{stamp}.json"
    scored_path.write_text(
        json.dumps([row.model_dump(mode="json") for row in scored], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    summaries = summarise(scored, results)
    comparisons = [
        found
        for budget in args.budgets
        for baseline in ("direct", "multi_stage", "gap_aware")
        if baseline in args.arms and "followup" in args.arms
        for found in [compare(scored, treatment="followup", baseline=baseline, budget=budget)]
        if found is not None
    ]
    report_path = RESULTS_DIR / f"report_{stamp}.md"
    report_path.write_text(
        render_markdown(
            summaries,
            comparisons,
            title=f"Clarification pilot — {args.benchmark} — {stamp}",
        ),
        encoding="utf-8",
    )

    print("-" * 70)
    print(f"run      {run_path}")
    print(f"scored   {scored_path}")
    print(f"report   {report_path}")
    return report_path


def parser() -> argparse.ArgumentParser:
    parsed = argparse.ArgumentParser(
        prog="clarification_pilot.runner",
        description="Does bounded clarification improve the final answer, and what does it cost?",
    )
    parsed.add_argument("--benchmark", default="askmind")
    parsed.add_argument("--data", default=None, help="Override the dataset path")
    parsed.add_argument("--limit", type=int, default=None, help="Stratified subset size")
    parsed.add_argument("--arms", nargs="+", default=list(ARM_ORDER), choices=list(ARM_ORDER))
    parsed.add_argument("--budgets", nargs="+", type=int, default=[1, 2, 3])
    parsed.add_argument("--model", default=DEFAULT_MODEL)
    parsed.add_argument("--simulator-model", default=None)
    parsed.add_argument("--judge-model", default=None)
    parsed.add_argument("--temperature", type=float, default=0.0)
    parsed.add_argument("--max-tokens", type=int, default=1024)
    parsed.add_argument("--seed", type=int, default=42)
    parsed.add_argument("--unknown-tolerance", type=int, default=2)
    parsed.add_argument("--concurrency", type=int, default=4)
    parsed.add_argument(
        "--separate-question-call",
        action="store_true",
        help="Split gap selection from question writing into two calls",
    )
    parsed.add_argument(
        "--judge-fallback",
        action="store_true",
        help="Send exact-match misses to the judge, marked scored_by=judge",
    )
    parsed.add_argument("--no-coverage", action="store_true", help="Skip judge-scored coverage")
    parsed.add_argument("--log-prompts", action="store_true")
    parsed.add_argument("--dry-run", action="store_true", help="No network, no API key")
    return parsed


def main() -> None:
    asyncio.run(run(parser().parse_args()))


if __name__ == "__main__":
    main()
