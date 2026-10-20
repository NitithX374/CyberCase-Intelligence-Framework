"""Runs the arms of README.md through production's write path (pinned origin/main 969d61a). Model calls; capped.

  python run.py --articles 3 --arms clean,targeted,realistic --cap-usd 0.10 --concurrency 3
  python run.py --arms clean,targeted --cap-usd 1.90

Writes results/run_<stamp>.jsonl, results/raw_<stamp>/<article>_<arm>.json and results/run_<stamp>_summary.json.
The MITRE gate is off, no technical context is passed and the RAG URL points at a closed port.
"""
from __future__ import annotations

import argparse
import asyncio
import contextvars
import json
import os
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
CODE = HERE / "pinned" / "969d61a" / "backend"
os.environ["MITRE_GATE_MODE"] = "never"
os.environ["MITRE_GATE_SHADOW"] = "off"
os.environ["RAG_SERVICE_URL"] = "http://127.0.0.1:9"
os.chdir(HERE.parents[2] / "backend")
sys.path.insert(0, str(CODE))

import app.analysis.write as write_module  # noqa: E402
from app.analysis.language import case_language  # noqa: E402
from app.config import settings  # noqa: E402
from app.errors import CaseAnalysisFailure  # noqa: E402
from app.llm import request as provider  # noqa: E402
from app.llm.settings import AnalysisPipelineConfig  # noqa: E402
from app.sources.bundle import CaseSourceBundle, CaseSourceItem  # noqa: E402
from app.trace.bind import bound_references  # noqa: E402

MODEL, PROVIDERS = "google/gemma-4-26b-a4b-it", ("coreweave/bf16", "nextbit/bf16")
PRICE = {"input": 0.10e-6, "output": 0.30e-6}
ARMS = ("clean", "targeted", "realistic")
MAX_SYSTEM_FAILURES = 10
CALLS: contextvars.ContextVar[list] = contextvars.ContextVar("calls")
READING: contextvars.ContextVar[list] = contextvars.ContextVar("reading")
BUDGET = {"cap": 0.0, "spent": 0.0, "reserved": 0.0}
FAILURES: Counter = Counter()
STOP: list[str] = []
original_post = provider.post_stage
original_request_stage = write_module.request_stage


class BudgetStop(Exception):
    pass


def worst_case_usd(payload) -> float:
    return provider.token_count(payload) * PRICE["input"] + payload["max_tokens"] * PRICE["output"]


async def recorded_post(target, payload, *, stage, timeout):
    worst = await asyncio.to_thread(worst_case_usd, payload)
    if BUDGET["spent"] + BUDGET["reserved"] + worst > BUDGET["cap"]:
        raise BudgetStop(f"cap ${BUDGET['cap']:.2f} reached")
    BUDGET["reserved"] += worst
    started = time.monotonic()
    try:
        response = await original_post(target, payload, stage=stage, timeout=timeout)
    finally:
        BUDGET["reserved"] -= worst
    elapsed = round((time.monotonic() - started) * 1000)
    if response.status_code == 402:
        raise BudgetStop("provider credit limit reached (HTTP 402)")
    record = {"stage": stage, "ms": elapsed, "status_code": response.status_code, "provider": None,
              "stop_reason": None, "input_tokens": None, "output_tokens": None, "thinking_tokens": None,
              "usd": 0.0, "usd_basis": None}
    try:
        body = provider.decode_response(response)
        usage = provider.usage_summary(body)
        charged = body.get("usage", {}).get("cost") if isinstance(body.get("usage"), dict) else None
        if isinstance(charged, (int, float)):
            cost, basis = float(charged), "provider_reported"
        else:
            cost = (usage["input_tokens"] or 0) * PRICE["input"] + (
                (usage["output_tokens"] or 0) + (usage["thinking_tokens"] or 0)) * PRICE["output"]
            basis = "worst_case"
        record.update(provider=body.get("provider"), stop_reason=body.get("stop_reason"), usd=cost, usd_basis=basis,
                      **usage)
    except (CaseAnalysisFailure, ValueError):
        pass
    BUDGET["spent"] += record["usd"]
    CALLS.get().append(record)
    return response


async def capturing_request_stage(**kwargs):
    result = await original_request_stage(**kwargs)
    if kwargs.get("stage") == "case_reading":
        READING.get().append(result.model_dump(mode="json"))
    return result


provider.post_stage = recorded_post
write_module.request_stage = capturing_request_stage


async def run_one(article: dict, arm: str, config: AnalysisPipelineConfig, raw: Path, limit) -> dict:
    async with limit:
        calls: list = []
        CALLS.set(calls)
        reading: list = []
        READING.set(reading)
        record = {"article": article["id"], "arm": arm}
        started = time.monotonic()
        if STOP:
            record.update(error=f"stopped: {STOP[0]}", error_kind="stopped", calls=[], seconds=0.0)
            return record
        bundle = CaseSourceBundle(revision=1, sources=(
            CaseSourceItem(source_id="SRC-1", source_kind="narrative", text=article[arm]),))
        record["language"] = case_language(bundle)
        try:
            trace = await write_module.write_trace(sources=bundle, language=record["language"], config=config)
            bound = bound_references(trace)
            (raw / f"{article['id']}_{arm}.json").write_text(json.dumps(
                {"reading": reading[-1] if reading else None, "bound": bound.model_dump(mode="json")},
                ensure_ascii=False), encoding="utf-8")
            record["grounding"] = bound.grounding.model_dump() if bound.grounding else None
        except BudgetStop as error:
            record.update(error=f"BudgetStop: {error}", error_kind="budget")
        except CaseAnalysisFailure as error:
            record.update(error=f"CaseAnalysisFailure: {error.code}", error_kind="system")
            FAILURES[arm] += 1
            if FAILURES[arm] > MAX_SYSTEM_FAILURES:
                STOP.append(f"more than {MAX_SYSTEM_FAILURES} failures in arm {arm}")
        except Exception as error:  # noqa: BLE001
            record.update(error=f"{type(error).__name__}: {error}", error_kind="harness")
            STOP.append(f"harness error in {article['id']}/{arm}")
        record.update(calls=calls, seconds=round(time.monotonic() - started, 1))
        return record


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arms", default=",".join(ARMS))
    parser.add_argument("--articles", type=int, default=None)
    parser.add_argument("--cap-usd", type=float, required=True)
    parser.add_argument("--concurrency", type=int, default=8)
    args = parser.parse_args()
    if not settings.openrouter_cybercase:
        raise SystemExit("OPENROUTER_CYBERCASE is not set")
    BUDGET["cap"] = args.cap_usd
    arms = [arm for arm in args.arms.split(",") if arm in ARMS]
    articles = [json.loads(line) for line in (HERE / "data" / "articles.jsonl").read_text(encoding="utf-8").split("\n")
                if line.strip()]
    articles = articles[: args.articles] if args.articles else articles
    config = AnalysisPipelineConfig(model=MODEL, providers=PROVIDERS)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    raw = HERE / "results" / f"raw_{stamp}"
    raw.mkdir(parents=True, exist_ok=True)
    limit = asyncio.Semaphore(args.concurrency)
    tasks = [asyncio.create_task(run_one(article, arm, config, raw, limit)) for article in articles for arm in arms]
    records = []
    with (HERE / "results" / f"run_{stamp}.jsonl").open("w", encoding="utf-8") as handle:
        for task in asyncio.as_completed(tasks):
            record = await task
            records.append(record)
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            handle.flush()
    per_arm = {}
    for arm in arms:
        rows = [r for r in records if r["arm"] == arm]
        calls = [c for r in rows for c in r["calls"]]
        per_arm[arm] = {"runs": len(rows), "completed": sum("error" not in r for r in rows),
                        "errors": dict(Counter(r["error"] for r in rows if "error" in r)),
                        "calls": len(calls), "usd": round(sum(c["usd"] for c in calls), 4),
                        "usd_per_article": round(sum(c["usd"] for c in calls) / max(1, len(rows)), 5),
                        "model_seconds": round(sum(c["ms"] for c in calls) / 1000, 1),
                        "status_codes": dict(Counter(c["status_code"] for c in calls))}
    report = {"code": (CODE.parent / "COMMIT").read_text(encoding="utf-8").strip(), "model": MODEL,
              "providers": PROVIDERS, "articles": len(articles), "arms": per_arm, "cap_usd": args.cap_usd,
              "spent_usd": round(BUDGET["spent"], 4), "stopped": STOP}
    (HERE / "results" / f"run_{stamp}_summary.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    asyncio.run(main())
