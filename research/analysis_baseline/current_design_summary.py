from __future__ import annotations

import argparse
import asyncio
import contextvars
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODEL, PROVIDERS = "google/gemma-4-26b-a4b-it", "nextbit/bf16,coreweave/bf16"
PRICE = {"input": 0.10e-6, "output": 0.30e-6}
CURRENT = contextvars.ContextVar("current_key", default="")
CALLS: list[dict] = []


def environment(reading_thinking: int) -> None:
    os.environ.update(
        CASE_ANALYSIS_MODEL=MODEL,
        CASE_ANALYSIS_PROVIDERS=PROVIDERS,
        CASE_READING_THINKING_TOKENS=str(reading_thinking),
        MITRE_GATE_MODE="never",
        MITRE_GATE_SHADOW="off",
        RAG_SERVICE_URL="http://127.0.0.1:9",
    )


async def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--items", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--cap-usd", type=float, required=True)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--reading-thinking", type=int, default=8192)
    parser.add_argument("--concurrency", type=int, default=6)
    parser.add_argument("--items-concurrency", type=int, default=6)
    parser.add_argument("--dry", action="store_true")
    args = parser.parse_args()
    environment(args.reading_thinking)
    sys.path.insert(0, str(HERE))
    import app

    if not Path(app.__file__).resolve().is_relative_to(HERE):
        raise SystemExit(f"wrong backend: {app.__file__}")

    from app.analysis.claim_gate import check_judgement_references, usable_reading
    from app.analysis.language import case_language
    from app.analysis.prompts import CASE_JUDGEMENT_SYSTEM_PROMPT, CASE_READING_JSON_PROMPT
    from app.analysis.reading_sources import ReadingSources
    from app.analysis.write import checked_reading, judgement_request, reading_from, reading_request
    from app.config import settings
    from app.llm import request as provider
    from app.llm.settings import configured_pipeline
    from app.sources.bundle import CaseSourceBundle, CaseSourceItem
    from app.trace.claim_validation import claim_blocker
    from app.trace.trace import CaseProviderJudgement, CaseProviderReadingReply

    if settings.case_analysis_model != MODEL:
        raise SystemExit(f"model is {settings.case_analysis_model}")
    config = configured_pipeline()
    items = json.loads(Path(args.items).read_text(encoding="utf-8"))
    if args.limit:
        items = items[: args.limit]
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    done = set()
    for path in out.glob("r*.json"):
        saved = json.loads(path.read_text(encoding="utf-8"))
        if saved.get("judgement") or saved.get("abstained"):
            done.add(saved["key"])
    todo = [item for item in items if item["key"] not in done]
    print(
        f"model {config.model} providers {config.providers} reading thinking "
        f"{config.for_reading().thinking_tokens} judgement thinking {config.thinking_tokens} "
        f"output {config.output_tokens} timeout {config.timeout_seconds}s; "
        f"{len(todo)} to run, {len(done)} already done",
        flush=True,
    )

    def bundle_for(item: dict) -> CaseSourceBundle:
        return CaseSourceBundle(
            revision=1,
            sources=(CaseSourceItem(source_id="SRC-1", source_kind="narrative", text=item["text"]),),
        )

    if args.dry:
        counts = []
        for item in todo:
            bundle = bundle_for(item)
            sources = await asyncio.to_thread(ReadingSources, tuple(bundle.sources))
            content = reading_request(bundle, case_language(bundle), (), reading_sources=sources)
            counts.append(provider.token_count({"system": CASE_READING_JSON_PROMPT, "content": content}))
        print("reader input tokens per item", counts)
        print("sum", sum(counts), "min", min(counts), "max", max(counts))
        return

    budget = {"spent": 0.0, "reserved": 0.0}
    limit = asyncio.Semaphore(args.concurrency)
    original_post = provider.post_stage

    async def metered(target, payload, *, stage, timeout):
        worst = provider.token_count(payload) * PRICE["input"] + payload["max_tokens"] * PRICE["output"]
        async with limit:
            if budget["spent"] + budget["reserved"] + worst > args.cap_usd:
                raise RuntimeError(f"cap ${args.cap_usd:.2f} reached")
            budget["reserved"] += worst
            started = time.monotonic()
            try:
                response = await original_post(target, payload, stage=stage, timeout=timeout)
            finally:
                budget["reserved"] -= worst
        try:
            body = provider.decode_response(response)
            usage = provider.usage_summary(body)
            charged = (body.get("usage") or {}).get("cost") if isinstance(body.get("usage"), dict) else None
            cost = float(charged) if isinstance(charged, (int, float)) else (
                (usage["input_tokens"] or 0) * PRICE["input"]
                + ((usage["output_tokens"] or 0) + (usage["thinking_tokens"] or 0)) * PRICE["output"]
            )
            entry = {**usage, "usd": cost, "provider": body.get("provider"), "stop_reason": body.get("stop_reason")}
        except Exception as error:
            cost = 0.0
            entry = {"usd": 0.0, "decode_error": type(error).__name__, "http": response.status_code}
        budget["spent"] += cost
        CALLS.append({"key": CURRENT.get(), "stage": stage, "ms": round((time.monotonic() - started) * 1000), **entry})
        return response

    provider.post_stage = metered

    item_limit = asyncio.Semaphore(args.items_concurrency)

    async def one(item: dict) -> dict:
        async with item_limit:
            return await work(item)

    async def work(item: dict) -> dict:
        key = item["key"]
        CURRENT.set(key)
        bundle = bundle_for(item)
        language = case_language(bundle)
        record = {"key": key, "language": language, "chars": len(item["text"])}
        started = time.monotonic()
        marks: dict[str, float] = {}

        def mark(name: str) -> None:
            marks[name] = round(time.monotonic() - started, 1)

        try:
            sources = await asyncio.to_thread(ReadingSources, tuple(bundle.sources))
            mark("segmented")
            reply = await provider.request_stage(
                config=config.for_reading(),
                stage="case_reading",
                system=CASE_READING_JSON_PROMPT,
                content=reading_request(bundle, language, (), reading_sources=sources),
                schema=CaseProviderReadingReply,
            )
            mark("reader_done")
            record["reply_claims"] = len(reply.claims)
            reading, grounding = await checked_reading(reading_from(reply, reading_sources=sources), bundle, ())
            mark("bound")
            judged = usable_reading(reading)
            record["claims"] = len(reading.claims)
            record["usable_claims"] = len(judged.claims)
            record["blockers"] = {c.claim_id: claim_blocker(c) for c in reading.claims if claim_blocker(c)}
            record["reading"] = reading.model_dump(mode="json")
            record["grounding"] = grounding.model_dump(mode="json")
            if not judged.claims:
                record["abstained"] = True
            else:
                judgement = await provider.request_stage(
                    config=config,
                    stage="case_judgement",
                    system=CASE_JUDGEMENT_SYSTEM_PROMPT,
                    content=judgement_request(judged, language, (), None),
                    schema=CaseProviderJudgement,
                )
                mark("judgement_done")
                check_judgement_references(judgement, judged)
                record["judgement"] = judgement.model_dump(mode="json")
        except Exception as error:
            record["error"] = f"{type(error).__name__}: {getattr(error, 'code', '')} {str(error)[:200]}"
        record["marks"] = marks
        record["seconds"] = round(time.monotonic() - started, 1)
        record["calls"] = [c for c in CALLS if c["key"] == key]
        record["usd"] = round(sum(c["usd"] for c in record["calls"]), 6)
        (out / f"{key}.json").write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
        print(
            key,
            "error " + record["error"] if "error" in record else ("abstained" if record.get("abstained") else "ok"),
            f"claims {record.get('usable_claims')}/{record.get('claims')} {record['seconds']}s ${record['usd']:.4f}",
            flush=True,
        )
        return record

    results = await asyncio.gather(*(one(item) for item in todo))
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    report = {
        "model": config.model,
        "providers": list(config.providers),
        "reading_thinking": config.for_reading().thinking_tokens,
        "judgement_thinking": config.thinking_tokens,
        "cap_usd": args.cap_usd,
        "spent_usd": round(budget["spent"], 4),
        "calls": len(CALLS),
        "items": [r["key"] for r in results],
        "abstained": [r["key"] for r in results if r.get("abstained")],
        "errors": [f"{r['key']}: {r['error']}" for r in results if "error" in r],
        "call_log": CALLS,
    }
    (out / f"run_{stamp}.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "call_log"}, indent=1))


if __name__ == "__main__":
    asyncio.run(main())
