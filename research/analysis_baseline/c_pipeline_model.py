from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
BACKEND = HERE.parents[1] / "backend"
PRICES = {"google/gemini-2.5-flash-lite": {"input": 0.10e-6, "output": 0.40e-6}}


async def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", required=True)
    parser.add_argument("--stage", choices=("pilot", "main"), required=True)
    parser.add_argument("--cap-usd", type=float, required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--ids", default="")
    args = parser.parse_args()
    price = PRICES[args.model]
    os.environ.update(MITRE_GATE_MODE="never", MITRE_GATE_SHADOW="off", RAG_SERVICE_URL="http://127.0.0.1:9",
                      CASE_ANALYSIS_MODEL=args.model, CASE_ANALYSIS_PROVIDERS="")
    os.chdir(BACKEND)
    sys.path.insert(0, str(Path(args.backend).resolve()))
    sys.path.insert(0, str(HERE))
    import app.trace.bind as bind

    if not Path(bind.__file__).resolve().is_relative_to(Path(args.backend).resolve()):
        raise SystemExit(f"wrong backend: {bind.__file__}")
    from app.analysis.prompts import CASE_JUDGEMENT_SYSTEM_PROMPT, CASE_READING_JSON_PROMPT
    from app.analysis.write import checked_reading, reading_from, reading_payload, reading_request
    from app.config import settings
    from app.errors import CaseAnalysisFailure
    from app.llm import request as provider
    from app.llm.settings import configured_pipeline
    from app.sources.bundle import CaseSourceBundle, CaseSourceItem
    from app.trace.trace import CaseProviderJudgement, CaseProviderReadingReply
    from judgement_claims_only import CITED_RULE, NO_SOURCES_ITEM, SOURCES_ITEM, SUMMARY_RULE, replaced, sample

    if settings.case_analysis_model != args.model:
        raise SystemExit(f"model is {settings.case_analysis_model}")
    config = configured_pipeline().model_copy(update={"thinking_tokens": 0})
    system_c = replaced(replaced(replaced(CASE_JUDGEMENT_SYSTEM_PROMPT, SUMMARY_RULE, CITED_RULE), SOURCES_ITEM,
                                 NO_SOURCES_ITEM), "case_judgement_v1", "case_analysis_trace_v1")
    budget = {"spent": 0.0, "reserved": 0.0}
    limit = asyncio.Semaphore(int(os.environ.get("RUN_CONCURRENCY", "6")))
    original_post = provider.post_stage
    calls_by_task: dict[int, list] = {}

    async def metered(target, payload, *, stage, timeout):
        worst = provider.token_count(payload) * price["input"] + payload["max_tokens"] * price["output"]
        async with limit:
            if budget["spent"] + budget["reserved"] + worst > args.cap_usd:
                raise CaseAnalysisFailure("budget_cap", f"cap ${args.cap_usd:.2f} reached", 500)
            budget["reserved"] += worst
            started = time.monotonic()
            try:
                response = await original_post(target, payload, stage=stage, timeout=timeout)
            finally:
                budget["reserved"] -= worst
        body = provider.decode_response(response)
        usage = provider.usage_summary(body)
        charged = (body.get("usage") or {}).get("cost") if isinstance(body.get("usage"), dict) else None
        cost = float(charged) if isinstance(charged, (int, float)) else (usage["input_tokens"] or 0) * price["input"] + (
            (usage["output_tokens"] or 0) + (usage["thinking_tokens"] or 0)) * price["output"]
        budget["spent"] += cost
        calls_by_task.setdefault(id(asyncio.current_task()), []).append(
            {"stage": stage, "status": response.status_code, "ms": round((time.monotonic() - started) * 1000), **usage,
             "usd": cost, "provider": body.get("provider"), "stop_reason": body.get("stop_reason")})
        return response

    original_schema = provider.structured_output_schema

    def enum_for_const(node):
        if isinstance(node, dict):
            node = {k: enum_for_const(v) for k, v in node.items()}
            if "const" in node:
                node["enum"] = [node.pop("const")]
            return node
        if isinstance(node, list):
            return [enum_for_const(v) for v in node]
        return node

    provider.structured_output_schema = lambda schema: enum_for_const(original_schema(schema))
    provider.post_stage = metered
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    raw = HERE / "results" / f"raw_c_pipeline_{args.model.split('/')[-1]}_{args.stage}_{stamp}"
    raw.mkdir(parents=True)

    async def one(item: dict) -> dict:
        out: dict = {"key": item["key"], "language": item["language"], "arm": "C", "model": args.model}
        bundle = CaseSourceBundle(revision=1, sources=(
            CaseSourceItem(source_id="SRC-1", source_kind="narrative", text=item["text"]),))
        try:
            reply = await provider.request_stage(config=config, stage="case_reading", system=CASE_READING_JSON_PROMPT,
                                                 content=reading_request(bundle, item["language"], ()),
                                                 schema=CaseProviderReadingReply, grammar=False)
            reading, grounding = await checked_reading(reading_from(reply), bundle, ())
            payload = reading_payload(reading)
            for claim in payload["claims"]:
                for role in ("supporting_citations", "contradicting_citations"):
                    for citation in claim.get(role, []):
                        citation.pop("context", None)
            content = {"response_language": item["language"], "followup_history": [], "technical_context": None,
                       "reading": payload}
            judgement = await provider.request_stage(config=config, stage="case_judgement", system=system_c,
                                                     content=content, schema=CaseProviderJudgement)
            out.update({"judgement": judgement.model_dump(mode="json"), "reading": reading.model_dump(mode="json"),
                        "grounding": grounding.model_dump(mode="json")})
        except CaseAnalysisFailure as error:
            out["error"] = f"CaseAnalysisFailure: {getattr(error, 'code', '')} {error}"
        out["calls"] = calls_by_task.get(id(asyncio.current_task()), [])
        (raw / f"{item['key']}_C.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
        print(item["key"], "error " + out["error"][:90] if "error" in out else "ok", flush=True)
        return out

    chosen = [i for i in sample(args.stage) if not args.ids or i["key"] in args.ids.split(",")]
    results = await asyncio.gather(*(one(item) for item in chosen))
    report = {"stage": args.stage, "model": args.model, "backend": args.backend, "spent_usd": round(budget["spent"], 4),
              "calls": sum(len(r["calls"]) for r in results),
              "errors": [f"{r['key']}: {r['error']}" for r in results if "error" in r]}
    (raw / "run.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    asyncio.run(main())
