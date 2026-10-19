"""Schema-enforcement probe for the DeepInfra rerun (README, correction to the amendment, 2026-10-02). Paid; cap USD 0.02.

The 2026-10-01 probe (schema_probe2.py, another session's scratchpad), unchanged except: providers crusoe/bf16 and
deepinfra/bf16, and the status code, served provider and cost are recorded. Six calls, max_tokens 6,000 each.
"""
import asyncio, os, sys, json
from pathlib import Path
ROOT = Path("F:/Cybercase Framework")
PINNED = ROOT / "research" / "analysis_baseline" / "pinned" / "1e29bd3" / "backend"
os.chdir(ROOT / "backend")
sys.path.insert(0, str(PINNED))
from pydantic import ValidationError
from app.llm import request as provider
from app.llm.openrouter import resolve_core_llm_target
from app.llm.settings import AnalysisPipelineConfig
from app.trace.trace import CaseProviderJudgement, CaseProviderAnalysis, CaseProviderReading

PROMPT = ('Write a short JSON object about a phishing email received by an employee. '
          'Use the keys "headline", "facts" (a list of strings) and "risk".')
CAP_USD, WORST_OUT = 0.02, 0.19e-6
ROWS, SPENT = [], [0.0]


async def one(model, prov, schema):
    config = AnalysisPipelineConfig(model=model, providers=(prov,))
    payload = provider.stage_payload(config, "Answer in JSON.", PROMPT, schema)
    payload["max_tokens"] = 6000
    target = resolve_core_llm_target(config.model)
    resp = await provider.post_stage(target, payload, stage="probe", timeout=180)
    row = {"provider": prov, "schema": schema.__name__, "status": resp.status_code}
    try:
        body = provider.decode_response(resp)
        usage = body.get("usage") if isinstance(body.get("usage"), dict) else {}
        row.update(served=body.get("provider"), stop=body.get("stop_reason"), usd=usage.get("cost"))
        text = provider.extract_visible_text(body).strip()
        try:
            schema.model_validate_json(text)
            row["verdict"] = "VALID against schema"
        except ValidationError as e:
            row["verdict"] = f"INVALID ({e.error_count()} errors, first: {e.errors()[0]['loc']} {e.errors()[0]['type']})"
        try:
            row["keys"] = list(json.loads(text).keys())
        except Exception:
            row["keys"] = f"not JSON: {text[:60]!r}"
        row["schema_keys"] = list(schema.model_fields)
    except Exception as error:
        row["error"] = f"{type(error).__name__}: {str(error)[:120]}"
    SPENT[0] += row.get("usd") or 0.0
    ROWS.append(row)
    print(json.dumps(row, ensure_ascii=False))


async def main():
    assert 6 * 6000 * WORST_OUT < CAP_USD
    for prov in ("crusoe/bf16", "deepinfra/bf16"):
        for schema in (CaseProviderReading, CaseProviderJudgement, CaseProviderAnalysis):
            await one("openai/gpt-oss-120b", prov, schema)
    print("spent_usd", round(SPENT[0], 5))
    Path(__file__).with_name("results").joinpath("schema_probe_20261002.json").write_text(
        json.dumps({"rows": ROWS, "spent_usd": SPENT[0]}, indent=1), encoding="utf-8")


asyncio.run(main())
