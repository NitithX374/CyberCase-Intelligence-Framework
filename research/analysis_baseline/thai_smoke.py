"""Thai smoke through the production code (README.md, 2026-10-01). A production safety check, not evidence for the book.

  python thai_smoke.py --cap-usd 0.10

Calls origin/main 8750cbc's write path (reading without the grammar, then judgement) and binder directly, on the
fictional cases in data/thai_smoke_cases.jsonl. Writes results/thai_smoke_<stamp>.json and .md.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRODUCTION = Path("F:/cc-worktrees/smoke-8750cbc/backend")
os.chdir(HERE.parents[1] / "backend")
sys.path.insert(0, str(PRODUCTION))

from app.analysis.language import case_language, has_thai  # noqa: E402
from app.analysis.write import write_trace  # noqa: E402
from app.errors import CaseAnalysisFailure  # noqa: E402
from app.llm import request as provider  # noqa: E402
from app.llm.settings import AnalysisPipelineConfig  # noqa: E402
from app.sources.bundle import CaseSourceBundle, CaseSourceItem  # noqa: E402
from app.trace.bind import resolve_case_trace  # noqa: E402

MODEL, PROVIDERS = "google/gemma-4-26b-a4b-it", ("coreweave/bf16", "nextbit/bf16")
CAP_TOKENS = 40_800
BAD = re.compile(r"[\x00-\x08\x0b-\x1f\ufffd]")
CALLS: list[dict] = []
original_post = provider.post_stage


async def recorded_post(target, payload, *, stage, timeout):
    started = time.monotonic()
    response = await original_post(target, payload, stage=stage, timeout=timeout)
    try:
        body = provider.decode_response(response)
        usage = provider.usage_summary(body)
        cost = (body.get("usage") or {}).get("cost") if isinstance(body.get("usage"), dict) else None
        CALLS.append({"stage": stage, "seconds": round(time.monotonic() - started, 1), "usd": cost,
                      "stop_reason": body.get("stop_reason"), "output_tokens": usage.get("output_tokens"),
                      "provider": body.get("provider")})
    except Exception as error:  # noqa: BLE001
        CALLS.append({"stage": stage, "seconds": round(time.monotonic() - started, 1), "error": type(error).__name__})
    return response


provider.post_stage = recorded_post


async def one(case: dict, config: AnalysisPipelineConfig) -> dict:
    bundle = CaseSourceBundle(revision=1, sources=(CaseSourceItem(source_id="SRC-1", source_kind="narrative",
                                                                  text=case["text"]),))
    first = len(CALLS)
    started = time.monotonic()
    record = {"case": case["id"], "kind": case["kind"], "language": case_language(bundle)}
    try:
        trace = await write_trace(sources=bundle, language=record["language"], config=config)
        bound = resolve_case_trace(trace, bundle)
        quotes = [q.exact_quote for c in bound.claims for q in c.supporting_citations + c.contradicting_citations]
        grounding = bound.grounding
        record.update(
            completed=True, claims=len(bound.claims), quotes_written=grounding.citations_claimed,
            quotes_verified=grounding.citations_verified, quotes_with_bad_characters=sum(bool(BAD.search(q)) for q in quotes),
            thai_quotes=sum(has_thai(q) for q in quotes), summary_is_thai=has_thai(bound.summary),
            summary=bound.summary[:160])
    except CaseAnalysisFailure as error:
        record.update(completed=False, error=getattr(error, "code", str(error)))
    calls = CALLS[first:]
    record.update(seconds=round(time.monotonic() - started, 1), calls=calls,
                  usd=sum(c.get("usd") or 0 for c in calls),
                  calls_to_cap=sum(c.get("stop_reason") in ("max_tokens", "length")
                                   or (c.get("output_tokens") or 0) >= CAP_TOKENS for c in calls))
    return record


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cap-usd", type=float, required=True)
    args = parser.parse_args()
    config = AnalysisPipelineConfig(model=MODEL, providers=PROVIDERS)
    cases = [json.loads(line) for line in (HERE / "data" / "thai_smoke_cases.jsonl").read_text(encoding="utf-8").splitlines()
             if line.strip()]
    records, spent = [], 0.0
    for case in cases:
        if spent >= args.cap_usd - 0.03:
            records.append({"case": case["id"], "completed": False, "error": "budget stop before the case"})
            continue
        record = await one(case, config)
        spent += record["usd"]
        records.append(record)
        print(f"{record['case']}: completed {record.get('completed')} quotes {record.get('quotes_verified')}/"
              f"{record.get('quotes_written')} bad {record.get('quotes_with_bad_characters')} thai summary "
              f"{record.get('summary_is_thai')} usd {record['usd']:.4f} s {record['seconds']}", flush=True)
    done = [r for r in records if r.get("completed")]
    written = sum(r["quotes_written"] for r in done)
    verified = sum(r["quotes_verified"] for r in done)
    checks = {
        "1_all_complete": len(done) == len(cases),
        "2_verified_share": verified / max(1, written),
        "2_pass": verified / max(1, written) >= 0.95,
        "3_no_bad_characters": sum(r["quotes_with_bad_characters"] for r in done) == 0,
        "4_thai_summaries": all(r["summary_is_thai"] for r in done) and bool(done),
    }
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out = {"code": "origin/main 8750cbc", "model": MODEL, "providers": PROVIDERS, "spent_usd": spent,
           "checks": checks, "records": records}
    (HERE / "results" / f"thai_smoke_{stamp}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1),
                                                               encoding="utf-8")
    lines = [f"# Thai smoke ({stamp})", "", f"Code origin/main 8750cbc, {MODEL}, {', '.join(PROVIDERS)}. "
             f"Spent USD {spent:.4f}.", "",
             "| Case | Kind | Completed | Quotes verified | Bad characters | Thai quotes | Thai summary | Calls to cap | s | USD |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for r in records:
        lines.append(f"| {r['case']} | {r.get('kind', '')} | {r.get('completed')} {r.get('error', '')} | "
                     f"{r.get('quotes_verified', '-')}/{r.get('quotes_written', '-')} | "
                     f"{r.get('quotes_with_bad_characters', '-')} | {r.get('thai_quotes', '-')} | "
                     f"{r.get('summary_is_thai', '-')} | {r.get('calls_to_cap', '-')} | {r.get('seconds', '-')} | "
                     f"{r.get('usd', 0):.4f} |")
    lines += ["", "**Pass criteria (fixed in README before any call):**",
              f"1. 5 of 5 complete: {checks['1_all_complete']}",
              f"2. Verified quotes ≥ 0.95: {verified}/{written} = {checks['2_verified_share']:.3f} -> {checks['2_pass']}",
              f"3. No control or replacement characters in stored quotes: {checks['3_no_bad_characters']}",
              f"4. Every summary in Thai: {checks['4_thai_summaries']}"]
    (HERE / "results" / f"thai_smoke_{stamp}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    asyncio.run(main())
