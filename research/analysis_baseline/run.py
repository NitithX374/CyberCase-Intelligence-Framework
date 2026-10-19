"""Runs the arms of README.md on CASIE cases through CyberCase's own code and scores them without a judge.

  python run.py --sample pilot --runs 3 --cap-usd 0.50
  python run.py --sample main --cases 50 --runs 1 --cap-usd 0.60

Runs from anywhere; it switches to backend/ so the backend settings read their .env files. The MITRE gate is off and
the RAG URL points at a closed local port, so no retrieval request can leave this machine.
"""
from __future__ import annotations

import argparse
import asyncio
import contextvars
import itertools
import json
import os
import re
import subprocess
import sys
import time
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
BACKEND = HERE.parents[1] / "backend"
CODE = Path(os.environ.get("ANALYSIS_CODE", BACKEND)).resolve()
os.environ["MITRE_GATE_MODE"] = "never"
os.environ["MITRE_GATE_SHADOW"] = "off"
os.environ["RAG_SERVICE_URL"] = "http://127.0.0.1:9"
os.chdir(BACKEND)
sys.path.insert(0, str(CODE))

from pydantic import BaseModel  # noqa: E402

from app.analysis.pipeline import (  # noqa: E402
    AnalysisInput,
    bind_to_case,
    retrieve_technical_context,
    write_analysis,
)
from app.analysis.prompts import CASE_JUDGEMENT_SYSTEM_PROMPT, CASE_READING_SYSTEM_PROMPT  # noqa: E402
from app.analysis.write import joined_trace, reading_payload, reading_request, write_request  # noqa: E402
from app.config import settings  # noqa: E402
from app.errors import CaseAnalysisFailure  # noqa: E402
from app.llm import request as provider  # noqa: E402
from app.llm.settings import AnalysisPipelineConfig, configured_pipeline  # noqa: E402
from app.sources.bundle import CaseSourceBundle, CaseSourceItem  # noqa: E402
from app.trace.claims import (  # noqa: E402
    CaseAnalysisClaim,
    CaseClaimFields,
    CaseProviderCitation,
    CaseProviderClaim,
    ReasoningSummary,
)
from app.trace.trace import CaseProviderAnalysis, CaseProviderJudgement, CaseProviderReading  # noqa: E402
from app.analysis.prompts import case_system_prompt  # noqa: E402
from experiments.analysis_arms import ArmArtifacts, direct, single, written_trace  # noqa: E402
from pydantic import Field, ValidationError, create_model  # noqa: E402

WORST_PRICE_PER_TOKEN = {
    "deepseek/deepseek-v4.1-flash": {"input": 0.30e-6, "output": 1.20e-6},
    "qwen/qwen3.6-35b-a3b": {"input": 0.25e-6, "output": 1.25e-6},
    "google/gemma-4-26b-a4b-it": {"input": 0.10e-6, "output": 0.30e-6},
    "openai/gpt-oss-120b": {"input": 0.04e-6, "output": 0.19e-6},
}
PRICE = WORST_PRICE_PER_TOKEN[settings.case_analysis_model]
ARMS = ("prose", "cybercase", "single")
EXPLORATORY_ARMS = ("cybercase_nothink", "single_late", "cybercase_slim", "cybercase_nonull", "cybercase_reorder",
                    "cybercase_nogrammar", "single_nogrammar")
LOCATOR_SENTENCE = (" Leave document_id and filename null and page_numbers empty so the\n"
                    "  backend can attach document locations.")
MAIN_RUN_COMMIT = "1e29bd3ae0112e44cb4abb782aff7d00523de659"
LATE_ORDER = ("version", "claims", "involved_parties", "timeline", "impacts", "summary", "gaps", "mitre_associations")
BASELINE_PROMPT = (HERE / "baseline_prompt.md").read_text(encoding="utf-8").strip()
IDENTIFIER_PATTERNS = {
    "url": re.compile(r"\bhttps?://[^\s<>\"'()\[\]{}]+", re.IGNORECASE),
    "ip": re.compile(r"(?<![\d.])(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.){3}(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(?!\.?\d)"),
    "hash": re.compile(r"\b(?:[a-f0-9]{64}|[a-f0-9]{40}|[a-f0-9]{32})\b", re.IGNORECASE),
    "attack": re.compile(r"\b(?:TA|T|S|G|M)\d{4}(?:\.\d{3})?\b"),
    "domain": re.compile(r"\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+(?:com|net|org|info|io|gov|edu|co|uk|ru|cn)\b",
                         re.IGNORECASE),
}
NUMBER = re.compile(r"(?<![\w.])\d[\d,]*(?:\.\d+)?")
MONTHS = {name: number for number, names in enumerate((
    ("january", "jan"), ("february", "feb"), ("march", "mar"), ("april", "apr"), ("may",), ("june", "jun"),
    ("july", "jul"), ("august", "aug"), ("september", "sept", "sep"), ("october", "oct"), ("november", "nov"),
    ("december", "dec")), 1) for name in names}
MONTH_WORD = "|".join(sorted(MONTHS, key=len, reverse=True))
DATE_PATTERNS = (
    ("ymd", re.compile(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b")),
    ("mdy", re.compile(rf"\b({MONTH_WORD})\.? (\d{{1,2}})(?:st|nd|rd|th)?,? (\d{{4}})\b", re.IGNORECASE)),
    ("dmy", re.compile(rf"\b(\d{{1,2}})(?:st|nd|rd|th)?(?: of)? ({MONTH_WORD})\.?,? (\d{{4}})\b", re.IGNORECASE)),
    ("ym", re.compile(r"\b(\d{4})-(\d{1,2})\b(?!-)")),
    ("my", re.compile(rf"\b({MONTH_WORD})\.?,? (\d{{4}})\b", re.IGNORECASE)),
)
RAW_DIR: list[Path] = []
CALLS: contextvars.ContextVar[list] = contextvars.ContextVar("calls")
PROBLEMS: contextvars.ContextVar[list] = contextvars.ContextVar("problems")
BUDGET = {"cap": 0.0, "spent": 0.0, "reserved": 0.0}
LIMIT = asyncio.Semaphore(int(os.environ.get("RUN_CONCURRENCY", "8")))
TASK_LIMIT = asyncio.Semaphore(int(os.environ.get("RUN_CONCURRENCY", "8")))
original_post = provider.post_stage


class BudgetStop(Exception):
    pass


class ProseAnalysis(BaseModel):
    analysis: str


def worst_case_usd(payload) -> float:
    return provider.token_count(payload) * PRICE["input"] + payload["max_tokens"] * PRICE["output"]


async def recorded_post(target, payload, *, stage, timeout):
    worst = await asyncio.to_thread(worst_case_usd, payload)
    async with LIMIT:
        if BUDGET["spent"] + BUDGET["reserved"] + worst > BUDGET["cap"]:
            raise BudgetStop(f"cap ${BUDGET['cap']:.2f} reached")
        BUDGET["reserved"] += worst
        started = time.monotonic()
        try:
            response = await original_post(target, payload, stage=stage, timeout=timeout)
        finally:
            BUDGET["reserved"] -= worst
        if response.status_code == 402:
            raise BudgetStop("provider credit limit reached (HTTP 402)")
        elapsed = round((time.monotonic() - started) * 1000)
        return record_call(response, stage, elapsed)


def record_call(response, stage, elapsed):
    charged = None
    served = {"generation_id": None, "provider": None, "stop_reason": None}
    try:
        body = provider.decode_response(response)
        usage = provider.usage_summary(body)
        charged = body.get("usage", {}).get("cost") if isinstance(body.get("usage"), dict) else None
        served = {"generation_id": body.get("id"), "provider": body.get("provider"), "stop_reason": body.get("stop_reason")}
        if body.get("stop_reason") == "max_tokens" and RAW_DIR:
            text = provider.extract_visible_text(body)
            (RAW_DIR[0] / f"max_tokens_{stage}_{body.get('id') or time.time_ns()}.txt").write_text(
                f"chars {len(text)}\n--- head\n{text[:1500]}\n--- tail\n{text[-3000:]}\n--- before the trailing "
                f"whitespace ({len(text) - len(text.rstrip())} chars of it)\n{text.rstrip()[-800:]}", encoding="utf-8")
    except (CaseAnalysisFailure, ValueError):
        usage = {"input_tokens": None, "output_tokens": None, "thinking_tokens": None}
    if isinstance(charged, (int, float)):
        cost, basis = float(charged), "provider_reported"
    else:
        cost = (usage["input_tokens"] or 0) * PRICE["input"] + (
            (usage["output_tokens"] or 0) + (usage["thinking_tokens"] or 0)
        ) * PRICE["output"]
        basis = "worst_case"
    BUDGET["spent"] += cost
    CALLS.get().append({"stage": stage, "ms": elapsed, **usage, "usd": cost, "usd_basis": basis, **served})
    return response


provider.post_stage = recorded_post


def norm(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", unicodedata.normalize("NFKC", text).lower()))


def contains(haystack: str, needle: str) -> bool:
    return f" {needle} " in f" {haystack} "


def numbers(text: str) -> set[str]:
    found = set()
    for match in NUMBER.finditer(unicodedata.normalize("NFKC", text)):
        value = match.group(0).replace(",", "").rstrip(".")
        if len(value.split(".")[0]) >= 2:
            found.add(value)
    return found


def dates(text: str) -> tuple[set[str], str]:
    keys: set[str] = set()
    text = unicodedata.normalize("NFKC", text)
    for kind, pattern in DATE_PATTERNS:
        for match in pattern.finditer(text):
            g = match.groups()
            if kind == "ymd":
                year, month, day = int(g[0]), int(g[1]), int(g[2])
            elif kind == "mdy":
                year, month, day = int(g[2]), MONTHS[g[0].lower()], int(g[1])
            elif kind == "dmy":
                year, month, day = int(g[2]), MONTHS[g[1].lower()], int(g[0])
            elif kind == "ym":
                year, month, day = int(g[0]), int(g[1]), 0
            else:
                year, month, day = int(g[1]), MONTHS[g[0].lower()], 0
            if 1 <= month <= 12 and 0 <= day <= 31:
                keys.add(f"{year:04d}-{month:02d}" + (f"-{day:02d}" if day else ""))
        text = pattern.sub(" ", text)
    return keys, text


def identifier_check(written: str, source: str) -> dict:
    written_dates, rest = dates(written)
    source_dates, _ = dates(source)
    widened = source_dates | {key[:7] for key in source_dates}
    items = ([("date", key, key in widened) for key in sorted(written_dates)]
             + [("number", value, value in numbers(source)) for value in sorted(numbers(rest))]
             + [("identifier", value, value in identifiers(source)) for value in sorted(identifiers(rest))])
    return {"written": len(items), "supported": sum(ok for _, _, ok in items),
            "unsupported": [f"{kind}:{value}" for kind, value, ok in items if not ok]}


def identifiers(text: str) -> set[str]:
    text = unicodedata.normalize("NFKC", text)
    return {f"{kind}:{m.group(0).lower().rstrip('.,;:')}" for kind, p in IDENTIFIER_PATTERNS.items() for m in p.finditer(text)}


def own_text(trace) -> str:
    parts = [trace.summary]
    parts += [f"{p.name} {p.role}" for p in trace.involved_parties]
    parts += [f"{t.time} {t.event}" for t in trace.timeline]
    parts += [f"{c.text} {c.reasoning_summary or ''}" for c in trace.claims]
    parts += [i.description for i in trace.impacts]
    parts += [f"{g.topic} {g.description}" for g in trace.gaps]
    return "\n".join(parts)


def quote_spans(trace, source: str) -> list[tuple[int, int]]:
    spans = []
    for claim in trace.claims:
        for citation in [*claim.supporting_citations, *claim.contradicting_citations]:
            start = source.find(citation.exact_quote)
            while start >= 0:
                spans.append((start, start + len(citation.exact_quote)))
                start = source.find(citation.exact_quote, start + 1)
    return spans


def fact_key(fact: dict) -> str:
    return f"{fact['role']}|{fact['text']}"


def score(case: dict, text: str, trace=None) -> dict:
    written = norm(text)
    source = case["text"]
    result = {
        "gold": len(case["gold"]),
        "gold_lead": sum(f["lead"] for f in case["gold"]),
        "stated": sorted(fact_key(f) for f in case["gold"] if contains(written, f["text"])),
        "stated_lead": sorted(fact_key(f) for f in case["gold"] if f["lead"] and contains(written, f["text"])),
        "words": len(text.split()),
        "identifiers": identifier_check(text, source),
    }
    if trace is not None:
        spans = quote_spans(trace, source)
        grounded = [
            f for f in case["gold"]
            if any(start < q_end and end > q_start for start, end in f["spans"] for q_start, q_end in spans)
        ]
        result["grounded"] = sorted(fact_key(f) for f in grounded)
        result["grounded_lead"] = sorted(fact_key(f) for f in grounded if f["lead"])
        result["statuses"] = dict(Counter(claim.epistemic_status for claim in trace.claims))
        result["grounding"] = trace.grounding.model_dump() if trace.grounding else None
    return result


def binder_delta(written, bound) -> dict:
    def quotes(trace) -> int:
        return sum(len(c.supporting_citations) + len(c.contradicting_citations) for c in trace.claims)

    before = {c.claim_id: c.epistemic_status for c in written.claims}
    return {
        "quotes_written": quotes(written),
        "quotes_kept": quotes(bound),
        "statuses_changed": sum(before.get(c.claim_id) != c.epistemic_status for c in bound.claims),
    }


def check_scorer() -> None:
    case = {"text": "On 14th of February 2014 Chicago Public Schools lost 80,000 records to a phishing email from "
                    "evil.com.",
            "gold": [{"role": "Victim", "text": "chicago public schools", "spans": [[25, 47]], "lead": True},
                     {"role": "Number-of-Data", "text": "80 000", "spans": [[53, 59]], "lead": False}]}
    scored = score(case, "On 2014-02-14 the Chicago Public Schools (CPS) lost 80,000 records; 2,000 more at bad.com "
                         "in March 2015.")
    assert scored["stated"] == ["Number-of-Data|80 000", "Victim|chicago public schools"], scored
    assert scored["stated_lead"] == ["Victim|chicago public schools"], scored
    check = scored["identifiers"]
    assert check["unsupported"] == ["date:2015-03", "number:2000", "identifier:domain:bad.com"], check
    assert (check["written"], check["supported"]) == (5, 2), check
    assert score(case, "A school was attacked.")["stated"] == []


def code_version() -> dict:
    def git(*args: str) -> str:
        return subprocess.run(["git", *args], cwd=BACKEND, capture_output=True, text=True).stdout.strip()

    if CODE != BACKEND.resolve():
        return {"commit": (CODE.parent / "COMMIT").read_text(encoding="utf-8").strip(), "exported_to": str(CODE)}
    changed = [line for line in git("status", "--porcelain", "--untracked-files=no").splitlines() if line.strip()]
    return {"commit": git("rev-parse", "HEAD"), "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
            "tracked_changes": changed}


def bundle(text: str) -> CaseSourceBundle:
    return CaseSourceBundle(revision=1, sources=(CaseSourceItem(source_id="SRC-1", source_kind="narrative", text=text),))


async def prose(data: AnalysisInput) -> str:
    parsed = await provider.request_stage(
        config=configured_pipeline(),
        stage="prose_baseline",
        system=BASELINE_PROMPT,
        content=write_request(data.sources, data.response_language, (), None),
        schema=ProseAnalysis,
    )
    return parsed.analysis


def main_run_prompt() -> str:
    source = subprocess.run(["git", "show", f"{MAIN_RUN_COMMIT}:backend/app/analysis/prompts.py"], cwd=BACKEND,
                            capture_output=True, text=True, encoding="utf-8", check=True).stdout
    namespace: dict = {}
    exec(compile(source, "prompts_at_main_run.py", "exec"), namespace)
    return namespace["MAIN_CASE_ANALYSIS_SYSTEM_PROMPT"]


def summary_last(prompt: str) -> str:
    head, rest = prompt.split("Case Structure, written after the claims:\n", 1)
    section, tail = rest.split("\n\nMITRE ATT&CK Associations:", 1)
    bullets = re.split(r"\n(?=- )", section)
    moved = [b for b in bullets if b.startswith("- summary:")]
    kept = [b for b in bullets if not b.startswith("- summary:")]
    if len(moved) != 1 or len(kept) != 3:
        raise SystemExit("the main run's Case Structure section no longer has the expected four bullets")
    return (f"{head}Case Structure, written after the claims:\n" + "\n".join(kept + moved)
            + "\n\nMITRE ATT&CK Associations:" + tail)


if set(LATE_ORDER) != set(CaseProviderAnalysis.model_fields):
    raise SystemExit("LATE_ORDER no longer covers CaseProviderAnalysis")
LATE_PROMPT = summary_last(main_run_prompt())
CaseProviderAnalysisLate = create_model(
    "CaseProviderAnalysis", __config__=CaseProviderAnalysis.model_config,
    **{name: (CaseProviderAnalysis.model_fields[name].annotation, CaseProviderAnalysis.model_fields[name])
       for name in LATE_ORDER})


async def write_single_call_late(*, sources, language, followup_history=(), technical_context=None, config):
    parsed = await provider.request_stage(
        config=config,
        stage="case_direct",
        system=LATE_PROMPT,
        content=write_request(sources, language, followup_history, technical_context),
        schema=CaseProviderAnalysisLate,
    )
    return written_trace(parsed, technical_context)


async def single_late(data: AnalysisInput) -> ArmArtifacts:
    artifacts = await retrieve_technical_context(data, ArmArtifacts())
    artifacts = await write_analysis(data, artifacts, request=write_single_call_late)
    return await bind_to_case(data, artifacts)


if CASE_READING_SYSTEM_PROMPT.count(LOCATOR_SENTENCE) != 1:
    raise SystemExit("the reading prompt no longer holds the locator sentence")
SLIM_READING_PROMPT = CASE_READING_SYSTEM_PROMPT.replace(LOCATOR_SENTENCE, "")
CaseProviderReadingSlim = create_model(
    "CaseProviderReading", __config__=CaseProviderReading.model_config,
    **{name: ((list[CaseProviderClaim], Field(max_length=64)) if name == "claims" else (field.annotation, field))
       for name, field in CaseProviderReading.model_fields.items()})


async def write_trace_slim(*, sources, language, followup_history=(), technical_context=None, config):
    slim = await provider.request_stage(
        config=config,
        stage="case_reading",
        system=SLIM_READING_PROMPT,
        content=reading_request(sources, language, followup_history),
        schema=CaseProviderReadingSlim,
    )
    reading = CaseProviderReading.model_validate({
        **slim.model_dump(),
        "claims": [CaseAnalysisClaim.model_validate(claim.model_dump()).model_dump() for claim in slim.claims],
    })
    judgement = await provider.request_stage(
        config=config,
        stage="case_judgement",
        system=CASE_JUDGEMENT_SYSTEM_PROMPT,
        content={**write_request(sources, language, followup_history, technical_context),
                 "reading": reading_payload(reading)},
        schema=CaseProviderJudgement,
    )
    return joined_trace(reading, judgement, technical_context)


CaseProviderClaimNoNull = create_model(
    "CaseProviderClaim", __base__=CaseClaimFields,
    supporting_citations=(list[CaseProviderCitation], Field(default_factory=list, max_length=64)),
    contradicting_citations=(list[CaseProviderCitation], Field(default_factory=list, max_length=64)),
    reasoning_summary=(str, Field(max_length=1_000)))
CaseProviderReadingNoNull = create_model(
    "CaseProviderReading", __config__=CaseProviderReading.model_config,
    **{name: ((list[CaseProviderClaimNoNull], Field(max_length=64)) if name == "claims" else (field.annotation, field))
       for name, field in CaseProviderReading.model_fields.items()})


async def write_trace_nonull(*, sources, language, followup_history=(), technical_context=None, config):
    written = await provider.request_stage(
        config=config,
        stage="case_reading",
        system=SLIM_READING_PROMPT,
        content=reading_request(sources, language, followup_history),
        schema=CaseProviderReadingNoNull,
    )
    reading = CaseProviderReading.model_validate({
        **written.model_dump(),
        "claims": [CaseAnalysisClaim.model_validate(claim.model_dump()).model_dump() for claim in written.claims],
    })
    judgement = await provider.request_stage(
        config=config,
        stage="case_judgement",
        system=CASE_JUDGEMENT_SYSTEM_PROMPT,
        content={**write_request(sources, language, followup_history, technical_context),
                 "reading": reading_payload(reading)},
        schema=CaseProviderJudgement,
    )
    return joined_trace(reading, judgement, technical_context)


async def direct_nonull(data: AnalysisInput) -> ArmArtifacts:
    artifacts = await retrieve_technical_context(data, ArmArtifacts())
    return await write_analysis(data, artifacts, request=write_trace_nonull)


CaseProviderClaimReorder = create_model(
    "CaseProviderClaim", __base__=CaseClaimFields,
    reasoning_summary=(ReasoningSummary, Field(default=None, max_length=1_000)),
    supporting_citations=(list[CaseProviderCitation], Field(default_factory=list, max_length=64)),
    contradicting_citations=(list[CaseProviderCitation], Field(default_factory=list, max_length=64)))
CaseProviderReadingReorder = create_model(
    "CaseProviderReading", __config__=CaseProviderReading.model_config,
    **{name: ((list[CaseProviderClaimReorder], Field(max_length=64)) if name == "claims" else (field.annotation, field))
       for name, field in CaseProviderReading.model_fields.items()})


async def write_trace_reorder(*, sources, language, followup_history=(), technical_context=None, config):
    written = await provider.request_stage(
        config=config,
        stage="case_reading",
        system=SLIM_READING_PROMPT,
        content=reading_request(sources, language, followup_history),
        schema=CaseProviderReadingReorder,
    )
    reading = CaseProviderReading.model_validate({
        **written.model_dump(),
        "claims": [CaseAnalysisClaim.model_validate(claim.model_dump()).model_dump() for claim in written.claims],
    })
    judgement = await provider.request_stage(
        config=config,
        stage="case_judgement",
        system=CASE_JUDGEMENT_SYSTEM_PROMPT,
        content={**write_request(sources, language, followup_history, technical_context),
                 "reading": reading_payload(reading)},
        schema=CaseProviderJudgement,
    )
    return joined_trace(reading, judgement, technical_context)


async def direct_reorder(data: AnalysisInput) -> ArmArtifacts:
    artifacts = await retrieve_technical_context(data, ArmArtifacts())
    return await write_analysis(data, artifacts, request=write_trace_reorder)


NOGRAMMAR_TEMPLATE = """

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
NOGRAMMAR_PROMPT = SLIM_READING_PROMPT + NOGRAMMAR_TEMPLATE
FENCE = re.compile(r"^\s*```(?:json)?\s*|\s*```\s*$")


async def read_without_grammar(config, content: dict):
    payload = provider.stage_payload(config, NOGRAMMAR_PROMPT, content, CaseProviderReadingReorder)
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
            return CaseProviderReadingReorder.model_validate_json(text), problems
        except ValidationError as error:
            first = error.errors()[0]
            problems.append(f"invalid: {first['type']} at {'.'.join(map(str, first['loc']))}"[:160])
    raise CaseAnalysisFailure("case_reading_invalid", "; ".join(problems))


async def write_trace_nogrammar(*, sources, language, followup_history=(), technical_context=None, config):
    written, problems = await read_without_grammar(config, reading_request(sources, language, followup_history))
    PROBLEMS.get().extend(problems)
    reading = CaseProviderReading.model_validate({
        **written.model_dump(),
        "claims": [CaseAnalysisClaim.model_validate(claim.model_dump()).model_dump() for claim in written.claims],
    })
    judgement = await provider.request_stage(
        config=config,
        stage="case_judgement",
        system=CASE_JUDGEMENT_SYSTEM_PROMPT,
        content={**write_request(sources, language, followup_history, technical_context),
                 "reading": reading_payload(reading)},
        schema=CaseProviderJudgement,
    )
    return joined_trace(reading, judgement, technical_context)


async def direct_nogrammar(data: AnalysisInput) -> ArmArtifacts:
    artifacts = await retrieve_technical_context(data, ArmArtifacts())
    return await write_analysis(data, artifacts, request=write_trace_nogrammar)


SINGLE_NOGRAMMAR_TEMPLATE = """

Output format:
- Reply with one JSON object and nothing else. Write every key below, in exactly this order, even when a list is empty:
{"version": "case_analysis_trace_v1",
 "claims": [{"claim_id": "A-01", "claim_type": "reported", "text": "...", "epistemic_status": "reported",
   "supporting_source_ids": ["SRC-1"], "contradicting_source_ids": [],
   "supporting_citations": [{"source_id": "SRC-1", "exact_quote": "..."}],
   "contradicting_citations": [],
   "reasoning_summary": "..."}],
 "summary": "...",
 "involved_parties": [{"name": "...", "role": "...", "claim_ids": ["A-01"]}],
 "timeline": [{"time": "...", "event": "...", "claim_ids": ["A-01"]}],
 "impacts": [{"description": "...", "claim_ids": ["A-01"]}],
 "gaps": [{"gap_id": "G-01", "gap_key": "when", "topic": "...", "status": "NOT_PROVIDED", "description": "...",
   "affected_claim_ids": ["A-01"], "reason": "...", "priority": "high", "askable": true,
   "clarification_question": "..."}],
 "mitre_associations": []}
- claim_type is one of "reported", "analytical_inference", "unknown". epistemic_status is one of "reported",
  "suspected", "contradicted", "not_established", "unknown".
- A gap's status is one of "NOT_PROVIDED", "EXPLICITLY_UNKNOWN", "AMBIGUOUS", "CONFLICTING"; priority is one of
  "high", "medium", "low"; clarification_question is a string or null.
- mitre_associations stays an empty list when no technical_context is supplied.
- reasoning_summary is one short sentence saying why the quoted text supports the claim, or null.
- Inside any string, write a double quotation mark as \\" so the JSON stays valid."""
SINGLE_NOGRAMMAR_PROMPT = case_system_prompt() + SINGLE_NOGRAMMAR_TEMPLATE


async def single_call_without_grammar(config, content: dict):
    payload = provider.stage_payload(config, SINGLE_NOGRAMMAR_PROMPT, content, CaseProviderAnalysis)
    del payload["output_config"]
    target = provider.resolve_core_llm_target(config.model)
    problems: list[str] = []
    for _ in range(2):
        response = await provider.post_stage(target, payload, stage="case_direct", timeout=config.timeout_seconds)
        decoded = provider.decode_response(response)
        if decoded.get("stop_reason") in ("max_tokens", "length"):
            problems.append("ran_to_max_tokens")
            continue
        text = FENCE.sub("", provider.extract_visible_text(decoded).strip())
        try:
            return CaseProviderAnalysis.model_validate_json(text), problems
        except ValidationError as error:
            first = error.errors()[0]
            problems.append(f"invalid: {first['type']} at {'.'.join(map(str, first['loc']))}"[:160])
    PROBLEMS.get().extend(problems)
    raise CaseAnalysisFailure("case_direct_invalid", "; ".join(problems))


async def write_single_call_nogrammar(*, sources, language, followup_history=(), technical_context=None, config):
    parsed, problems = await single_call_without_grammar(
        config, write_request(sources, language, followup_history, technical_context))
    PROBLEMS.get().extend(problems)
    return written_trace(parsed, technical_context)


async def single_nogrammar(data: AnalysisInput) -> ArmArtifacts:
    artifacts = await retrieve_technical_context(data, ArmArtifacts())
    artifacts = await write_analysis(data, artifacts, request=write_single_call_nogrammar)
    return await bind_to_case(data, artifacts)


async def direct_slim(data: AnalysisInput) -> ArmArtifacts:
    artifacts = await retrieve_technical_context(data, ArmArtifacts())
    return await write_analysis(data, artifacts, request=write_trace_slim)


async def direct_without_thinking(data: AnalysisInput) -> ArmArtifacts:
    artifacts = await retrieve_technical_context(data, ArmArtifacts())
    return await write_analysis(data, artifacts, config=lambda: AnalysisPipelineConfig(thinking_tokens=0))


async def run_limited(case: dict, arm: str, run: int, raw: Path) -> dict:
    async with TASK_LIMIT:
        return await run_arm(case, arm, run, raw)


async def run_arm(case: dict, arm: str, run: int, raw: Path) -> dict:
    calls: list = []
    CALLS.set(calls)
    problems: list = []
    PROBLEMS.set(problems)
    record = {"case": case["id"], "sample": case["sample"], "arm": arm, "run": run}
    data = AnalysisInput(sources=bundle(case["text"]), response_language="english")
    started = time.monotonic()
    stem = raw / f"{case['id']}_{arm}_{run}"
    try:
        if arm == "prose":
            text = await prose(data)
            stem.with_suffix(".txt").write_text(text, encoding="utf-8")
            record.update(score(case, text))
        elif arm in ("cybercase", "cybercase_nothink", "cybercase_slim", "cybercase_nonull", "cybercase_reorder",
                     "cybercase_nogrammar"):
            written = await {"cybercase": direct, "cybercase_nothink": direct_without_thinking,
                             "cybercase_slim": direct_slim, "cybercase_nonull": direct_nonull,
                             "cybercase_reorder": direct_reorder, "cybercase_nogrammar": direct_nogrammar}[arm](data)
            bound = await bind_to_case(data, written)
            stem.with_suffix(".json").write_text(json.dumps(
                {"written": written.trace.model_dump(mode="json"), "bound": bound.trace.model_dump(mode="json")},
                ensure_ascii=False), encoding="utf-8")
            record.update(score(case, own_text(bound.trace), bound.trace), binder=binder_delta(written.trace, bound.trace))
        else:
            bound = await {"single": single, "single_late": single_late, "single_nogrammar": single_nogrammar}[arm](data)
            stem.with_suffix(".json").write_text(json.dumps(
                {"bound": bound.trace.model_dump(mode="json")}, ensure_ascii=False), encoding="utf-8")
            record.update(score(case, own_text(bound.trace), bound.trace))
    except BudgetStop as error:
        record.update(error=f"BudgetStop: {error}", error_kind="budget")
    except CaseAnalysisFailure as error:
        record.update(error=f"CaseAnalysisFailure: {error.code}", error_kind="system")
    except Exception as error:
        record.update(error=f"{type(error).__name__}: {error}", error_kind="harness")
    record.update(calls=calls, seconds=round(time.monotonic() - started, 1))
    if problems:
        record["problems"] = problems
    return record


def jaccard(a: set, b: set) -> float:
    return 1.0 if not a and not b else len(a & b) / len(a | b)


def mean(values: list[float]) -> float | None:
    return round(sum(values) / len(values), 3) if values else None


def stability(done: list[dict], field: str) -> float | None:
    by_case: dict[str, list[set]] = {}
    for r in done:
        by_case.setdefault(r["case"], []).append(set(r[field]))
    return mean([jaccard(a, b) for sets in by_case.values() for a, b in itertools.combinations(sets, 2)])


def share(r: dict, field: str, gold: str) -> float:
    return 0.0 if "error" in r else len(r[field]) / r[gold]


def recalls(rows: list[dict], traced: bool) -> dict:
    return {
        "recall_lead": mean([share(r, "stated_lead", "gold_lead") for r in rows]),
        "recall_all": mean([share(r, "stated", "gold") for r in rows]),
        "grounded_recall_lead": mean([share(r, "grounded_lead", "gold_lead") for r in rows]) if traced else None,
        "grounded_recall_all": mean([share(r, "grounded", "gold") for r in rows]) if traced else None,
    }


def summary(records: list[dict]) -> dict:
    out = {}
    for arm in [*ARMS, *(a for a in EXPLORATORY_ARMS if any(r["arm"] == a for r in records))]:
        rows = [r for r in records if r["arm"] == arm]
        ran = [r for r in rows if r.get("error_kind") not in ("budget", "harness")]
        done = [r for r in ran if "error" not in r]
        calls = [c for r in rows for c in r["calls"]]
        written = sum(r["identifiers"]["written"] for r in done)
        traced = [r for r in done if "grounded" in r]
        claimed = sum((r["grounding"] or {}).get("citations_claimed", 0) for r in traced)
        out[arm] = {
            "runs": len(rows), "ran": len(ran), "completed": len(done),
            "failures": dict(Counter(r["error"] for r in ran if "error" in r)),
            "budget_stopped": sum(r.get("error_kind") == "budget" for r in rows),
            "harness_errors": sum(r.get("error_kind") == "harness" for r in rows),
            **recalls(ran, arm != "prose"),
            "completed_only": recalls(done, arm != "prose"),
            "identifier_precision": round(sum(r["identifiers"]["supported"] for r in done) / written, 3)
            if written else None,
            "identifiers_written": written,
            "verbatim_rate": round(sum((r["grounding"] or {}).get("citations_verified", 0) for r in traced) / claimed, 3)
            if claimed else None,
            "stability_lead": stability(done, "stated_lead"),
            "stability_all": stability(done, "stated"),
            "words_per_run": round(sum(r["words"] for r in done) / max(1, len(done))),
            "calls": len(calls), "usd": round(sum(c["usd"] for c in calls), 4),
            "model_seconds": round(sum(c["ms"] for c in calls) / 1000, 1),
        }
    return out


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", choices=("pilot", "main"), required=True)
    parser.add_argument("--runs", type=int, required=True)
    parser.add_argument("--cap-usd", type=float, required=True)
    parser.add_argument("--arms", default=",".join(ARMS))
    parser.add_argument("--cases", type=int, default=None)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--ids", default=None)
    args = parser.parse_args()
    check_scorer()
    if not settings.openrouter_cybercase:
        raise SystemExit("OPENROUTER_CYBERCASE is not set")
    BUDGET["cap"] = args.cap_usd
    arms = [arm for arm in args.arms.split(",") if arm in (*ARMS, *EXPLORATORY_ARMS)]
    cases = [json.loads(line) for line in (HERE / "data" / "cases.jsonl").read_text(encoding="utf-8").splitlines()]
    cases = [c for c in cases if c["sample"] == args.sample][args.offset:][: args.cases] if not args.ids else [
        next(c for c in cases if c["id"] == case_id) for case_id in args.ids.split(",")]
    code = code_version()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    raw = HERE / "results" / f"raw_{args.sample}_{stamp}"
    raw.mkdir(parents=True, exist_ok=True)
    RAW_DIR.append(raw)
    tasks = [asyncio.create_task(run_limited(case, arm, run, raw))
             for case in cases for arm in arms for run in range(1, args.runs + 1)]
    out = HERE / "results" / f"{args.sample}_{stamp}.jsonl"
    records = []
    with out.open("w", encoding="utf-8") as handle:
        for task in asyncio.as_completed(tasks):
            record = await task
            records.append(record)
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            handle.flush()
    report = {"model": settings.case_analysis_model, "providers": settings.case_analysis_providers, "code": code,
              "cases": len(cases), "case_ids": [c["id"] for c in cases], "runs": args.runs,
              "cap_usd": args.cap_usd, "spent_usd": round(BUDGET["spent"], 4),
              "arms": summary(records),
              "errors": [f"{r['case']}/{r['arm']}/{r['run']} ({r['error_kind']}): {r['error']}"
                         for r in records if "error" in r]}
    (HERE / "results" / f"{args.sample}_{stamp}_summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
