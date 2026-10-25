"""Availability of the model stages at temperature 0, on the clean arm of current_2026-10-25. Model calls; capped.

Arms, each over the first --articles clean articles:
  t0_think    every call temperature 0, judgement thinking 2,048 (the current thinking settings)
  t0_nothink  every call temperature 0, judgement thinking 0 (thinking off in every stage)
  t1_assess   the assessment call only, temperature not sent (the current setting)
  rule        judgement 1.0 with thinking 2,048; every other call 0 with thinking off
The t0 arms call the assessment, then write_trace (reading, views, judgement). The temperature-1 baseline of
reading, views and judgement is the clean arm of current_2026-10-25/results/run_20261024_222324.

  python run_temperature.py --articles 3 --cap-usd 0.10 --concurrency 3 --expect-segmenter sat --confirm-spend
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse  # noqa: E402
import asyncio  # noqa: E402
import contextvars  # noqa: E402
import json  # noqa: E402
import statistics  # noqa: E402
import time  # noqa: E402
from collections import Counter  # noqa: E402
from datetime import UTC, datetime  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "current_2026-10-25"))

import run_current as rc  # noqa: E402

from app.analysis.pipeline import assess_case  # noqa: E402
from app.errors import CaseAnalysisFailure  # noqa: E402
from app.llm.settings import AnalysisPipelineConfig  # noqa: E402
from app.sources.bundle import CaseSourceBundle, CaseSourceItem  # noqa: E402
from app.trace.bind import bound_references  # noqa: E402

ARMS = {"t0_think": (0.0, 2048, True), "t0_nothink": (0.0, 0, True), "t1_assess": (None, 2048, False),
        "rule": ({"case_judgement": 1.0, "*": 0.0}, 2048, True)}
TEMPERATURE: contextvars.ContextVar[float | dict | None] = contextvars.ContextVar("temperature", default=None)
sent_post = rc.original_post


async def tempered_post(target, payload, *, stage, timeout):
    temperature = TEMPERATURE.get()
    if isinstance(temperature, dict):
        temperature = temperature.get(stage, temperature["*"])
    if temperature is not None:
        payload["temperature"] = temperature
    return await sent_post(target, payload, stage=stage, timeout=timeout)


rc.original_post = tempered_post


def arm_config(judgement_thinking: int) -> AnalysisPipelineConfig:
    return AnalysisPipelineConfig(
        model=rc.MODEL,
        providers=rc.PROVIDERS,
        server="openrouter",
        reading_thinking_tokens=0,
        assess_thinking_tokens=0,
        judgement_thinking_tokens=judgement_thinking,
    )


async def run_one(article: dict, arm: str, limit) -> dict:
    temperature, judgement_thinking, write = ARMS[arm]
    async with limit:
        TEMPERATURE.set(temperature)
        calls: list = []
        rc.CALLS.set(calls)
        rc.REPLIES.set({})
        hits: list = []
        rc.BUDGET_HITS.set(hits)
        record = {"article": article["id"], "arm": arm, "stage_errors": {}}
        started = time.monotonic()
        if rc.STOP:
            record.update(stopped=rc.STOP[0], calls=[], seconds=0.0)
            return record
        config = arm_config(judgement_thinking)
        bundle = CaseSourceBundle(revision=1, sources=(
            CaseSourceItem(source_id="SRC-1", source_kind="narrative", text=article["clean"]),))
        language = rc.case_language(bundle)
        steps = [("assess", lambda: assess_case(source_bundle=bundle, followup_history=(), response_language=language,
                                                 config=config))]
        if write:
            steps.append(("write", lambda: rc.write_module.write_trace(sources=bundle, language=language,
                                                                        config=config)))
        for name, step in steps:
            try:
                result = await step()
                if hits:
                    raise rc.BudgetStop(hits[0]["reason"])
                if name == "write":
                    bound = bound_references(result, [])
                    record["claims"] = len(bound.claims)
                    record["views_failed"] = (bound.view_extraction is not None
                                              and bound.view_extraction.status == "failed")
                else:
                    record["gaps"] = len(result.gaps)
            except rc.BudgetStop as error:
                record["stage_errors"][name] = f"BudgetStop: {error}"
                break
            except CaseAnalysisFailure as error:
                record["stage_errors"][name] = f"CaseAnalysisFailure: {error.code}"
            except Exception as error:  # noqa: BLE001
                record["stage_errors"][name] = f"{type(error).__name__}: {error}"
                rc.STOP.append(f"harness error in {article['id']}/{arm}")
                break
        record.update(calls=calls, seconds=round(time.monotonic() - started, 1))
        return record


def stage_summary(calls: list) -> dict:
    out = {}
    for stage in sorted({c["stage"] for c in calls}):
        rows = [c for c in calls if c["stage"] == stage]
        thinking = [c["thinking_tokens"] for c in rows if c["thinking_tokens"] is not None]
        out[stage] = {"calls": len(rows), "temperatures": dict(Counter(str(c["temperature"]) for c in rows)),
                      "status_codes": dict(Counter(c["status_code"] for c in rows)),
                      "stop_reasons": dict(Counter(str(c["stop_reason"]) for c in rows)),
                      "thinking_tokens_median": statistics.median(thinking) if thinking else None,
                      "thinking_tokens_max": max(thinking) if thinking else None,
                      "seconds_median": round(statistics.median(c["ms"] for c in rows) / 1000, 1)}
    return out


async def main(argv: list[str] | None = None) -> dict:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arms", default=",".join(ARMS))
    parser.add_argument("--articles", type=int, default=50)
    parser.add_argument("--cap-usd", type=float, required=True)
    parser.add_argument("--confirm-spend", action="store_true")
    parser.add_argument("--concurrency", type=int, default=8)
    parser.add_argument("--results-dir", default=str(HERE / "results"))
    parser.add_argument("--expect-segmenter", choices=("sat", "crfcut"), required=True)
    parser.add_argument("--code-commit", default=None)
    parser.add_argument("--image-id", default=None)
    args = parser.parse_args(argv)
    if not args.confirm_spend:
        raise SystemExit("refusing to start: pass --confirm-spend to allow paid model calls")
    if not args.cap_usd > 0:
        raise SystemExit("--cap-usd must be positive")
    if not 1 <= args.articles <= rc.SAMPLE_SIZE:
        raise SystemExit(f"--articles must be 1..{rc.SAMPLE_SIZE}")
    if not rc.settings.openrouter_cybercase:
        raise SystemExit("OPENROUTER_CYBERCASE is not set")
    environment = rc.preflight()
    if environment["segmenter"].split(":")[0] != args.expect_segmenter:
        raise SystemExit(f"segmenter is {environment['segmenter']}, not {args.expect_segmenter}")
    environment.update(recorded_commit=args.code_commit, image_id=args.image_id)
    rc.BUDGET["cap"] = args.cap_usd
    arms = [arm for arm in args.arms.split(",") if arm in ARMS]
    articles = [json.loads(line) for line in (rc.EXPERIMENT / "data" / "articles.jsonl").read_text(encoding="utf-8")
                .split("\n") if line.strip()][: args.articles]
    results = Path(args.results_dir)
    results.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    limit = asyncio.Semaphore(args.concurrency)
    tasks = [asyncio.create_task(run_one(article, arm, limit)) for article in articles for arm in arms]
    records = []
    with (results / f"run_{stamp}.jsonl").open("w", encoding="utf-8") as handle:
        for task in asyncio.as_completed(tasks):
            record = await task
            records.append(record)
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            handle.flush()
    per_arm = {}
    for arm in arms:
        rows = [r for r in records if r["arm"] == arm]
        calls = [c for r in rows for c in r["calls"]]
        per_arm[arm] = {"runs": len(rows),
                        "stage_errors": dict(Counter(f"{k}: {v}" for r in rows for k, v in r["stage_errors"].items())),
                        "write_completed": sum("claims" in r for r in rows),
                        "assess_completed": sum("gaps" in r for r in rows),
                        "views_failed": sum(bool(r.get("views_failed")) for r in rows),
                        "stages": stage_summary(calls),
                        "usd": round(sum(c["usd"] for c in calls), 4),
                        "seconds_median": statistics.median(r["seconds"] for r in rows) if rows else None}
    report = {"code": environment, "model": rc.MODEL, "providers": rc.PROVIDERS,
              "articles": len(articles), "article_ids": [a["id"] for a in articles], "arms": per_arm,
              "cap_usd": args.cap_usd, "spent_usd": round(rc.BUDGET["spent"], 4), "stopped": rc.STOP}
    (results / f"run_{stamp}_summary.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    print(json.dumps(report, indent=1))
    return report


if __name__ == "__main__":
    asyncio.run(main())
