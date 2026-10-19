"""Runaway screen (README.md, 2026-09-30): the reading call alone, four arms.

  python runaway_screen.py --pilot --cap-usd 0.05     3 pilot cases, every arm (mechanics)
  python runaway_screen.py --cap-usd 0.55             main cases 151-180, every arm

Arms: shipped (production reading), template_reorder (reorder schema with every key named in the prompt), nogrammar (the
same prompt, no response format, parsed and validated here), gptoss20b (production reading on openai/gpt-oss-20b).
Uses run.py for the pinned backend, the budget ledger and the call recorder. Writes results/screen_<stamp>.jsonl and .md.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import re
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent

import run as h  # noqa: E402

from pydantic import ValidationError  # noqa: E402

from app.analysis.prompts import CASE_READING_SYSTEM_PROMPT  # noqa: E402
from app.analysis.write import reading_request  # noqa: E402
from app.errors import CaseAnalysisFailure  # noqa: E402
from app.llm import request as provider  # noqa: E402
from app.llm.settings import AnalysisPipelineConfig  # noqa: E402
from app.trace.bind import resolve_case_trace  # noqa: E402
from app.trace.claims import CaseAnalysisClaim  # noqa: E402
from app.trace.trace import CaseAnalysisTrace, CaseProviderReading  # noqa: E402

ARMS = ("shipped", "template_reorder", "nogrammar", "gptoss20b", "g_template_reorder_noesc",
        "g_template_shipped_noesc")
GPTOSS = ("openai/gpt-oss-20b", ("deepinfra/bf16", "dekallm/bf16"))
TEMPLATE = """

Output format:
- Reply with one JSON object and nothing else. Write every key below, in exactly this order, even when a list is empty:
{"version": "case_analysis_trace_v1",
 "claims": [{"claim_id": "A-01", "claim_type": "reported", "text": "...", "epistemic_status": "reported",
   "supporting_source_ids": ["SRC-1"], "contradicting_source_ids": [],
   "reasoning_summary": "...",
   "supporting_citations": [{"source_id": "SRC-1", "exact_quote": "..."}],
   "contradicting_citations": []}],
 "involved_parties": [{"name": "...", "role": "...", "claim_ids": ["A-01"]}],
 "timeline": [{"time": "...", "event": "...", "claim_ids": ["A-01"]}],
 "impacts": [{"description": "...", "claim_ids": ["A-01"]}]}
- claim_type is one of "reported", "analytical_inference", "unknown". epistemic_status is one of "reported",
  "suspected", "contradicted", "not_established", "unknown".
- reasoning_summary is one short sentence saying why the quoted text supports the claim, or null.
- Inside any string, write a double quotation mark as \\" so the JSON stays valid."""
TEMPLATE_PROMPT = h.SLIM_READING_PROMPT + TEMPLATE
ESCAPE_LINE = '\n- Inside any string, write a double quotation mark as \\" so the JSON stays valid.'
TEMPLATE_NOESC = TEMPLATE.replace(ESCAPE_LINE, "")
TEMPLATE_SHIPPED_NOESC = TEMPLATE_NOESC.replace(
    """   "reasoning_summary": "...",
   "supporting_citations": [{"source_id": "SRC-1", "exact_quote": "..."}],
   "contradicting_citations": []}],""",
    """   "supporting_citations": [{"source_id": "SRC-1", "exact_quote": "...", "document_id": null,
     "filename": null, "page_numbers": []}],
   "contradicting_citations": [],
   "reasoning_summary": "..."}],""")
NOESC_REORDER_PROMPT = h.SLIM_READING_PROMPT + TEMPLATE_NOESC
NOESC_SHIPPED_PROMPT = CASE_READING_SYSTEM_PROMPT + TEMPLATE_SHIPPED_NOESC
FENCE = re.compile(r"^\s*```(?:json)?\s*|\s*```\s*$")
TASKS = asyncio.Semaphore(8)


def config_for(arm: str) -> AnalysisPipelineConfig:
    if arm == "gptoss20b":
        return AnalysisPipelineConfig(model=GPTOSS[0], providers=GPTOSS[1])
    return AnalysisPipelineConfig()


def as_reading(result) -> CaseProviderReading:
    if isinstance(result, CaseProviderReading):
        return result
    return CaseProviderReading.model_validate({
        **result.model_dump(),
        "claims": [CaseAnalysisClaim.model_validate(claim.model_dump()).model_dump() for claim in result.claims],
    })


async def read_free(config: AnalysisPipelineConfig, content: dict) -> tuple[object, list[str]]:
    payload = provider.stage_payload(config, TEMPLATE_PROMPT, content, h.CaseProviderReadingReorder)
    del payload["output_config"]
    target = provider.resolve_core_llm_target(config.model)
    problems: list[str] = []
    for _ in range(2):
        response = await provider.post_stage(target, payload, stage="case_reading", timeout=config.timeout_seconds)
        decoded = provider.decode_response(response)
        if decoded.get("stop_reason") in ("max_tokens", "length"):
            problems.append("ran_to_max_tokens")
            continue
        text = FENCE.sub("", provider.extract_visible_text(decoded).strip())
        try:
            return h.CaseProviderReadingReorder.model_validate_json(text), problems
        except ValidationError as error:
            problems.append(f"invalid: {error.errors()[0]['type']} at {'.'.join(map(str, error.errors()[0]['loc']))}"[:160])
    raise CaseAnalysisFailure("case_reading_invalid", "; ".join(problems))


async def read(arm: str, case: dict) -> tuple[CaseProviderReading, list[str]]:
    config = config_for(arm)
    content = reading_request(h.bundle(case["text"]), "english", ())
    if arm == "nogrammar":
        result, problems = await read_free(config, content)
        return as_reading(result), problems
    system, schema = {"template_reorder": (TEMPLATE_PROMPT, h.CaseProviderReadingReorder),
                      "g_template_reorder_noesc": (NOESC_REORDER_PROMPT, h.CaseProviderReadingReorder),
                      "g_template_shipped_noesc": (NOESC_SHIPPED_PROMPT, CaseProviderReading),
                      }.get(arm, (CASE_READING_SYSTEM_PROMPT, CaseProviderReading))
    result = await provider.request_stage(config=config, stage="case_reading", system=system, content=content,
                                          schema=schema)
    return as_reading(result), []


def runaway(call: dict) -> bool:
    return call.get("stop_reason") in ("max_tokens", "length") or (call.get("output_tokens") or 0) >= 40_800


async def screen(case: dict, arm: str, raw: Path) -> dict:
    async with TASKS:
        calls: list = []
        h.CALLS.set(calls)
        record = {"case": case["id"], "arm": arm}
        started = time.monotonic()
        try:
            reading, problems = await read(arm, case)
            trace = CaseAnalysisTrace.model_validate({**reading.model_dump(), "analysis_mode": "case_overview",
                                                      "summary": "Reading only."})
            bound = resolve_case_trace(trace, h.bundle(case["text"]))
            (raw / f"{case['id']}_{arm}.json").write_text(json.dumps(
                {"reading": reading.model_dump(mode="json"), "bound": bound.model_dump(mode="json")},
                ensure_ascii=False, indent=1), encoding="utf-8")
            record.update(claims=len(bound.claims), cited=bound.grounding.citations_claimed,
                          verified=bound.grounding.citations_verified, problems=problems)
        except h.BudgetStop as error:
            record.update(error=str(error), error_kind="budget")
        except (CaseAnalysisFailure, ValidationError, ValueError) as error:
            record.update(error=f"{type(error).__name__}: {str(error)[:300]}", error_kind="system")
        except Exception as error:  # noqa: BLE001
            record.update(error=f"{type(error).__name__}: {str(error)[:300]}", error_kind="harness")
        reading_calls = [c for c in calls if c["stage"] == "case_reading"]
        record.update(calls=calls, attempts=len(reading_calls),
                      first_runaway=bool(reading_calls) and runaway(reading_calls[0]),
                      runaways=sum(runaway(c) for c in reading_calls),
                      usd=sum(c["usd"] for c in calls), seconds=round(time.monotonic() - started, 1))
        return record


def report(records: list[dict], stamp: str, spent: float) -> str:
    lines = [f"# Runaway screen ({stamp})", "", f"Spent USD {spent:.4f}.", "",
             "| Arm | Cases | First-attempt runaways | Failed cases | Invalid replies | Empty cases | Claims per case | "
             "Verified quote share | USD | Median s |", "|---|---|---|---|---|---|---|---|---|---|"]
    for arm in ARMS:
        rows = [r for r in records if r["arm"] == arm and r.get("error_kind") not in ("budget", "harness")]
        if not rows:
            continue
        done = [r for r in rows if "error" not in r]
        invalid = sum(sum(p.startswith("invalid") for p in r.get("problems", [])) for r in rows)
        cited = sum(r["cited"] for r in done)
        seconds = sorted(r["seconds"] for r in rows)
        lines.append(
            f"| {arm} | {len(rows)} | {sum(r['first_runaway'] for r in rows)} | {len(rows) - len(done)} | {invalid} | "
            f"{sum(r['claims'] == 0 for r in done)} | {sum(r['claims'] for r in done) / max(1, len(done)):.1f} | "
            f"{sum(r['verified'] for r in done) / max(1, cited):.3f} | {sum(r['usd'] for r in rows):.4f} | "
            f"{seconds[len(seconds) // 2]:.0f} |")
    stops = Counter(f"{r['arm']}: {r.get('error_kind')}" for r in records if "error" in r)
    lines += ["", f"Errors by arm and kind: {dict(stops) or 'none'}.",
              "Providers of first reading calls: " + str(dict(Counter(
                  f"{r['arm']}/{(r['calls'][0].get('provider') if r['calls'] else '-')}" for r in records)))]
    return "\n".join(lines) + "\n"


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--cap-usd", type=float, required=True)
    parser.add_argument("--arms", default="shipped,template_reorder,nogrammar,gptoss20b")
    args = parser.parse_args()
    if not h.settings.openrouter_cybercase:
        raise SystemExit("OPENROUTER_CYBERCASE is not set")
    h.BUDGET["cap"] = args.cap_usd
    rows = [json.loads(line) for line in (HERE / "data" / "cases.jsonl").read_text(encoding="utf-8").splitlines()]
    cases = [r for r in rows if r["sample"] == "pilot"] if args.pilot else [
        r for r in rows if r["sample"] == "main"][150:180]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    name = f"screen_{'pilot' if args.pilot else 'main'}_{stamp}"
    raw = HERE / "results" / f"raw_{name}"
    raw.mkdir(parents=True, exist_ok=True)
    h.RAW_DIR.append(raw)
    arms = [arm for arm in args.arms.split(",") if arm in ARMS]
    tasks = [asyncio.create_task(screen(case, arm, raw)) for case in cases for arm in arms]
    records = []
    with (HERE / "results" / f"{name}.jsonl").open("w", encoding="utf-8") as handle:
        for task in asyncio.as_completed(tasks):
            record = await task
            records.append(record)
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            handle.flush()
            print(f"{record['arm']:17s} {record['case']:>6s} attempts {record['attempts']} "
                  f"runaways {record['runaways']} {record.get('error_kind') or 'ok'} "
                  f"claims {record.get('claims', '-')} usd {record['usd']:.4f}", flush=True)
    text = report(records, stamp, h.BUDGET["spent"])
    (HERE / "results" / f"{name}.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    asyncio.run(main())
