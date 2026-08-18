"""Single-probe binary LLM judge for evaluation probes."""

from __future__ import annotations

import asyncio
import json
import time
from typing import Any
import httpx

from app.services.llm.core_llm import resolve_core_llm_target
from app.services.llm.structured_output_router import structured_output_schema
from evaluation.analysis_pilot.config import (
    DEFAULT_JUDGE_MODEL,
    JUDGE_MAX_OUTPUT_TOKENS,
    JUDGE_TEMPERATURE,
    JUDGE_TIMEOUT_SECONDS,
)
from evaluation.analysis_pilot.prompts import (
    JUDGE_SYSTEM_PROMPT,
    JUDGE_USER_TEMPLATE,
)
from evaluation.analysis_pilot.schemas import (
    CaseAnalysisOutput,
    JudgeResponse,
    ProbeJudgmentRecord,
    ProbeVerdict,
)


async def judge_single_probe(
    *,
    analysis_output: CaseAnalysisOutput | None,
    probe: dict[str, Any],
    case: dict[str, Any],
    condition: str,
    model: str = DEFAULT_JUDGE_MODEL,
    temperature: float = JUDGE_TEMPERATURE,
) -> ProbeJudgmentRecord:
    """Evaluate whether a generated case analysis semantically asserts/entails a single probe claim."""
    started = time.perf_counter()

    claim = probe["claim"]
    claim_id = probe.get("claim_id", "")
    label = probe.get("label", "SUPPORTED")
    error_type = probe.get("error_type", "none")
    source_fact_ids = probe.get("source_fact_ids", [])

    if analysis_output is None:
        # Generation failed -> claim cannot be present
        latency_ms = (time.perf_counter() - started) * 1000.0
        return ProbeJudgmentRecord(
            case_id=case["case_id"],
            language=case["language"],
            scenario_id=case["scenario_id"],
            condition=condition,  # type: ignore[arg-type]
            claim_id=claim_id,
            claim=claim,
            label=label,  # type: ignore[arg-type]
            error_type=error_type,
            source_fact_ids=source_fact_ids,
            judge_model=model,
            reasoning="Analysis output was missing or failed generation; claim is not present.",
            verdict="NOT_PRESENT",
            is_correct_detection=(label == "UNSUPPORTED"),
            latency_ms=latency_ms,
        )

    findings_text = "\n".join(
        f"- [{f.epistemic_status}] {f.text}" for f in analysis_output.findings
    )
    analysis_text = analysis_output.analysis_text

    user_content = JUDGE_USER_TEMPLATE.format(
        claim=claim,
        findings_text=findings_text,
        analysis_text=analysis_text,
    )

    target = resolve_core_llm_target(model)
    request_payload: dict[str, Any] = {
        "model": target.model,
        "max_tokens": JUDGE_MAX_OUTPUT_TOKENS,
        "temperature": temperature,
        "system": JUDGE_SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": user_content}],
        "output_config": {
            "format": {
                "type": "json_schema",
                "schema": structured_output_schema(
                    JudgeResponse,
                    provider=target.provider,
                ),
            }
        },
    }

    verdict: ProbeVerdict = "NOT_PRESENT"
    reasoning: str = ""
    max_retries = 2

    for attempt in range(max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=JUDGE_TIMEOUT_SECONDS) as client:
                resp = await client.post(
                    target.messages_url,
                    headers=target.headers,
                    json=request_payload,
                )

            if not 200 <= resp.status_code < 300:
                raise RuntimeError(f"Judge HTTP {resp.status_code}: {resp.text[:300]}")

            resp_payload = resp.json()
            content = resp_payload.get("content", [])
            raw_text = ""
            if isinstance(content, list):
                raw_text = "".join(
                    b.get("text", "")
                    for b in content
                    if isinstance(b, dict) and b.get("type") == "text"
                )
            elif isinstance(content, str):
                raw_text = content

            raw_clean = raw_text.strip()
            if raw_clean.startswith("```json"):
                raw_clean = raw_clean[7:]
            if raw_clean.startswith("```"):
                raw_clean = raw_clean[3:]
            if raw_clean.endswith("```"):
                raw_clean = raw_clean[:-3]
            raw_clean = raw_clean.strip()

            parsed = json.loads(raw_clean)
            validated = JudgeResponse.model_validate(parsed)
            verdict = validated.verdict
            reasoning = validated.reasoning
            break
        except Exception as exc:
            if attempt < max_retries:
                await asyncio.sleep(1.0)
                continue
            verdict = "NOT_PRESENT"
            reasoning = f"Judge evaluation encountered error after retries: {type(exc).__name__}: {exc}"

    latency_ms = (time.perf_counter() - started) * 1000.0
    is_correct = (verdict == "PRESENT") if label == "SUPPORTED" else (verdict == "NOT_PRESENT")

    return ProbeJudgmentRecord(
        case_id=case["case_id"],
        language=case["language"],
        scenario_id=case["scenario_id"],
        condition=condition,  # type: ignore[arg-type]
        claim_id=claim_id,
        claim=claim,
        label=label,  # type: ignore[arg-type]
        error_type=error_type,
        source_fact_ids=source_fact_ids,
        judge_model=model,
        reasoning=reasoning,
        verdict=verdict,
        is_correct_detection=is_correct,
        latency_ms=latency_ms,
    )


async def judge_all_case_probes(
    *,
    analysis_output: CaseAnalysisOutput | None,
    case: dict[str, Any],
    condition: str,
    model: str = DEFAULT_JUDGE_MODEL,
    temperature: float = JUDGE_TEMPERATURE,
    concurrency: int = 4,
) -> list[ProbeJudgmentRecord]:
    """Evaluate all verification pair probes for a single case under a given condition."""
    probes = case.get("verification_pairs", [])
    semaphore = asyncio.Semaphore(concurrency)

    async def _eval_one(probe: dict[str, Any]) -> ProbeJudgmentRecord:
        async with semaphore:
            return await judge_single_probe(
                analysis_output=analysis_output,
                probe=probe,
                case=case,
                condition=condition,
                model=model,
                temperature=temperature,
            )

    tasks = [_eval_one(p) for p in probes]
    return await asyncio.gather(*tasks)
