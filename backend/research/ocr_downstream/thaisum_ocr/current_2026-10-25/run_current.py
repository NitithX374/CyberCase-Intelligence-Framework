"""Runs the arms of PROTOCOL.md through the CURRENT backend's write path (app.analysis.write.write_trace). Model calls;
capped. It refuses to start without --cap-usd and --confirm-spend.

  python run_current.py --articles 3 --cap-usd 0.10 --concurrency 3 --expect-segmenter sat --confirm-spend
  python run_current.py --cap-usd <rest of the cap> --expect-segmenter sat --confirm-spend

Writes results/run_<stamp>.jsonl, results/raw_<stamp>/<article>_<arm>.json and results/run_<stamp>_summary.json.
The raw files and the jsonl hold article text; they stay out of git (.gitignore in this folder).
No MITRE gate, no technical context, no RAG: write_trace is called directly and the RAG URL points at a closed port.
The claim verifier is disabled by pointing its two model folders at a folder that does not exist, so every Claim comes
out unassessed (verifier_unavailable or a structural reason) and the analysis continues.
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse  # noqa: E402
import asyncio  # noqa: E402
import contextvars  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import subprocess  # noqa: E402
import time  # noqa: E402
from collections import Counter  # noqa: E402
from datetime import UTC, datetime  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
EXPERIMENT = HERE.parent
BACKEND = Path(os.environ.get("CYBERCASE_BACKEND", HERE.parents[3]))
NO_VERIFIER = HERE / "verifier_disabled__this_folder_must_not_exist"
os.environ["MITRE_GATE_MODE"] = "never"
os.environ["RAG_SERVICE_URL"] = "http://127.0.0.1:9"
os.environ["CASE_ANALYSIS_SERVER"] = "openrouter"
os.environ["CASE_ANALYSIS_WARMUP_SECONDS"] = "0"
os.environ.setdefault("CLAIM_NLI_PATH", str(NO_VERIFIER / "nli_mdeberta"))
os.environ.setdefault("CLAIM_SELECTOR_PATH", str(NO_VERIFIER / "source_selector_mpnet"))
os.environ["WARMUP_MODELS"] = "false"
os.environ["HF_HOME"] = str(BACKEND / "models" / "hf")
os.environ["TIKTOKEN_CACHE_DIR"] = str(BACKEND / "models" / "tiktoken")
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.chdir(BACKEND)
sys.path.insert(0, str(BACKEND))

import app.analysis.views as views_module  # noqa: E402
import app.analysis.write as write_module  # noqa: E402
from app.analysis.language import case_language  # noqa: E402
from app.config import settings  # noqa: E402
from app.errors import CaseAnalysisFailure  # noqa: E402
from app.llm import request as provider  # noqa: E402
from app.llm.openrouter import resolve_core_llm_target  # noqa: E402
from app.llm.settings import AnalysisPipelineConfig  # noqa: E402
from app.sources.bundle import CaseSourceBundle, CaseSourceItem  # noqa: E402
from app.trace.bind import bound_references  # noqa: E402
from app.trace.sentences import get_sat_segmenter, segmenter_identity  # noqa: E402

MODEL = "google/gemma-4-26b-a4b-it"
PROVIDERS = ("nextbit/bf16", "coreweave/bf16")
READING_THINKING_TOKENS = 0
JUDGEMENT_THINKING_TOKENS = 2048
PRICE = {"input": 0.10e-6, "output": 0.30e-6}
ARMS = ("clean", "targeted", "realistic")
SAMPLE_SIZE = 100
MAX_SYSTEM_FAILURES = 10
CALLS: contextvars.ContextVar[list] = contextvars.ContextVar("calls")
REPLIES: contextvars.ContextVar[dict] = contextvars.ContextVar("replies")
BUDGET_HITS: contextvars.ContextVar[list] = contextvars.ContextVar("budget_hits")
BUDGET = {"cap": 0.0, "spent": 0.0, "reserved": 0.0}
FAILURES: Counter = Counter()
VIEW_FAILURES: Counter = Counter()
STOP: list[str] = []
original_post = provider.post_stage
original_write_request_stage = write_module.request_stage
original_views_request_stage = views_module.request_stage


class BudgetStop(Exception):
    pass


def worst_case_usd(payload) -> float:
    return provider.token_count(payload) * PRICE["input"] + payload["max_tokens"] * PRICE["output"]


async def recorded_post(target, payload, *, stage, timeout):
    worst = await asyncio.to_thread(worst_case_usd, payload)
    if STOP or BUDGET["spent"] + BUDGET["reserved"] + worst > BUDGET["cap"]:
        reason = STOP[0] if STOP else f"cap ${BUDGET['cap']:.2f} would be passed"
        BUDGET_HITS.get().append({"stage": stage, "reason": reason})
        if not STOP:
            STOP.append(f"budget: {reason}")
        raise BudgetStop(reason)
    BUDGET["reserved"] += worst
    started = time.monotonic()
    try:
        response = await original_post(target, payload, stage=stage, timeout=timeout)
    finally:
        BUDGET["reserved"] -= worst
    elapsed = round((time.monotonic() - started) * 1000)
    if response.status_code == 402:
        BUDGET_HITS.get().append({"stage": stage, "reason": "HTTP 402"})
        STOP.append("provider credit limit reached (HTTP 402)")
        raise BudgetStop("provider credit limit reached (HTTP 402)")
    record = {"stage": stage, "ms": elapsed, "status_code": response.status_code, "provider": None,
              "stop_reason": None, "input_tokens": None, "output_tokens": None, "thinking_tokens": None,
              "request_max_tokens": payload["max_tokens"], "thinking": payload.get("thinking"),
              "temperature": payload.get("temperature"), "usd": 0.0, "usd_basis": None}
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


async def capturing_write_request_stage(**kwargs):
    result = await original_write_request_stage(**kwargs)
    REPLIES.get()[kwargs.get("stage")] = result.model_dump(mode="json")
    return result


async def capturing_views_request_stage(**kwargs):
    result = await original_views_request_stage(**kwargs)
    REPLIES.get()[kwargs.get("stage")] = result.model_dump(mode="json")
    return result


provider.post_stage = recorded_post
write_module.request_stage = capturing_write_request_stage
views_module.request_stage = capturing_views_request_stage


def pipeline_config() -> AnalysisPipelineConfig:
    return AnalysisPipelineConfig(
        model=MODEL,
        providers=PROVIDERS,
        server="openrouter",
        reading_thinking_tokens=READING_THINKING_TOKENS,
        judgement_thinking_tokens=JUDGEMENT_THINKING_TOKENS,
    )


def run_facts(bound) -> dict:
    claims = bound.claims
    return {
        "claims": len(claims),
        "bound_statuses": dict(Counter(c.epistemic_status for c in claims)),
        "verdicts": dict(Counter(f"{c.semantic_grounding.verdict}:{c.semantic_grounding.reason}"
                                 for c in claims if c.semantic_grounding is not None)),
        "judged_claims": len(bound.view_extraction.input_claim_ids) if bound.view_extraction else 0,
        "bound_citations": sum(len(c.supporting_citations) + len(c.contradicting_citations) for c in claims),
        "invalid_evidence": dict(Counter(i.reason for c in claims for i in c.invalid_evidence)),
        "views": {"status": bound.view_extraction.status, "warning": bound.view_extraction.warning,
                  "items_dropped": bound.view_extraction.items_dropped} if bound.view_extraction else None,
        "parties": len(bound.involved_parties), "timeline": len(bound.timeline), "impacts": len(bound.impacts),
        "gaps": len(bound.gaps), "summary_units": len(bound.summary_units),
    }


def stop_kind(reason: str) -> str:
    return "budget" if reason.startswith(("cap ", "budget", "provider credit")) else "stopped"


async def run_one(article: dict, arm: str, config: AnalysisPipelineConfig, raw: Path, limit) -> dict:
    async with limit:
        calls: list = []
        CALLS.set(calls)
        replies: dict = {}
        REPLIES.set(replies)
        hits: list = []
        BUDGET_HITS.set(hits)
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
            bound = bound_references(trace, [])
            if hits:
                raise BudgetStop(hits[0]["reason"])
            (raw / f"{article['id']}_{arm}.json").write_text(json.dumps(
                {"reading": replies.get("case_reading"), "judgement": replies.get("case_judgement"),
                 "views_reply": replies.get("case_views"), "bound": bound.model_dump(mode="json")},
                ensure_ascii=False), encoding="utf-8")
            record["facts"] = run_facts(bound)
            if bound.view_extraction is not None and bound.view_extraction.status == "failed":
                VIEW_FAILURES[arm] += 1
        except BudgetStop as error:
            record.update(error=f"BudgetStop: {error}", error_kind=stop_kind(str(error)))
        except CaseAnalysisFailure as error:
            if hits:
                record.update(error=f"BudgetStop: {hits[0]['reason']}", error_kind=stop_kind(hits[0]["reason"]))
            else:
                record.update(error=f"CaseAnalysisFailure: {error.code}", error_kind="system")
                FAILURES[arm] += 1
                if FAILURES[arm] > MAX_SYSTEM_FAILURES:
                    STOP.append(f"more than {MAX_SYSTEM_FAILURES} failures in arm {arm}")
        except Exception as error:  # noqa: BLE001
            record.update(error=f"{type(error).__name__}: {error}", error_kind="harness")
            STOP.append(f"harness error in {article['id']}/{arm}")
        record.update(calls=calls, seconds=round(time.monotonic() - started, 1))
        return record


def sat_device() -> str | None:
    model = get_sat_segmenter()
    if model is None:
        return None
    try:
        return str(next(model.model.model.parameters()).device)
    except Exception as error:  # noqa: BLE001
        return f"unknown ({type(error).__name__})"


def preflight() -> dict:
    for path in (settings.claim_nli_path, settings.claim_selector_path):
        if Path(path).exists():
            raise SystemExit(f"verifier folder {path} exists; the protocol needs it absent")
    if settings.mitre_gate_mode != "never":
        raise SystemExit("MITRE_GATE_MODE is not never")
    target = resolve_core_llm_target(MODEL)
    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=BACKEND,
                                check=True).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain", "--", "app"], capture_output=True, text=True,
                               cwd=BACKEND, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        commit, dirty = "unknown", None
    return {"commit": commit, "app_dirty": None if dirty is None else bool(dirty), "messages_url": target.messages_url,
            "segmenter": segmenter_identity(), "sat_device": sat_device(), "python": sys.version.split()[0],
            "claim_nli_path": settings.claim_nli_path, "claim_selector_path": settings.claim_selector_path}


async def main(argv: list[str] | None = None) -> dict:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arms", default=",".join(ARMS))
    parser.add_argument("--articles", type=int, default=SAMPLE_SIZE)
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
    if not 1 <= args.articles <= SAMPLE_SIZE:
        raise SystemExit(f"--articles must be 1..{SAMPLE_SIZE}: the sample is the {SAMPLE_SIZE} articles in file order")
    if not settings.openrouter_cybercase:
        raise SystemExit("OPENROUTER_CYBERCASE is not set")
    environment = preflight()
    if environment["segmenter"].split(":")[0] != args.expect_segmenter:
        raise SystemExit(f"segmenter is {environment['segmenter']}, not {args.expect_segmenter}")
    environment.update(recorded_commit=args.code_commit, image_id=args.image_id)
    BUDGET["cap"] = args.cap_usd
    arms = [arm for arm in args.arms.split(",") if arm in ARMS]
    articles = [json.loads(line) for line in (EXPERIMENT / "data" / "articles.jsonl").read_text(encoding="utf-8")
                .split("\n") if line.strip()]
    articles = articles[:SAMPLE_SIZE][: args.articles]
    config = pipeline_config()
    results = Path(args.results_dir)
    stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    raw = results / f"raw_{stamp}"
    raw.mkdir(parents=True, exist_ok=True)
    limit = asyncio.Semaphore(args.concurrency)
    tasks = [asyncio.create_task(run_one(article, arm, config, raw, limit)) for article in articles for arm in arms]
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
        per_arm[arm] = {"runs": len(rows), "completed": sum("error" not in r for r in rows),
                        "errors": dict(Counter(r["error"] for r in rows if "error" in r)),
                        "view_failures": VIEW_FAILURES[arm],
                        "verdicts": dict(sum((Counter(r["facts"]["verdicts"]) for r in rows if "facts" in r),
                                             Counter())),
                        "calls": len(calls), "calls_by_stage": dict(Counter(c["stage"] for c in calls)),
                        "usd": round(sum(c["usd"] for c in calls), 4),
                        "usd_per_article": round(sum(c["usd"] for c in calls) / max(1, len(rows)), 5),
                        "model_seconds": round(sum(c["ms"] for c in calls) / 1000, 1),
                        "status_codes": dict(Counter(c["status_code"] for c in calls)),
                        "providers": dict(Counter(str(c["provider"]) for c in calls))}
    report = {"code": environment, "model": MODEL, "providers": PROVIDERS, "config": config.model_dump(mode="json"),
              "reading_max_tokens": config.for_reading().max_tokens,
              "judgement_max_tokens": config.for_judgement().max_tokens,
              "views_max_tokens": config.for_views().max_tokens,
              "articles": len(articles), "article_ids": [a["id"] for a in articles], "arms": per_arm,
              "cap_usd": args.cap_usd, "spent_usd": round(BUDGET["spent"], 4), "stopped": STOP}
    (results / f"run_{stamp}_summary.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    print(json.dumps(report, indent=1))
    return report


if __name__ == "__main__":
    asyncio.run(main())
