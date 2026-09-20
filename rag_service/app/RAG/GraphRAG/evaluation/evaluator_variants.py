"""
Evaluator Prompt Variants
==========================
The agentic ablation showed the self-reflection loop fires on the wrong
samples: verdicts track the evaluator prompt's four fixed phases more than
the gold techniques the context is actually missing, and the evaluator reads
only the first 4000 of ~9300 context characters.

This probe tests prompt-side fixes WITHOUT re-running retrieval. Every variant
judges the first-pass contexts arm A already produced
(results/agentic_ablation.jsonl), so the only thing that changes is the
evaluator, and the verdicts are directly comparable to the served ones.

Variants:

  v0_served      the verdicts already in the ablation run — free, no calls.
  v1_full_ctx    served prompt, whole context instead of the first 4000 chars.
  v2_subqueries  whole context, and coverage judged against the incident's own
                 decomposed sub-queries (the ones retrieval used) instead of
                 the four fixed phases.

Scored as a detector: ground truth is whether the context really is missing
gold techniques, so a verdict is right when INSUFFICIENT coincides with
missing gold. Reports precision / recall / F1 of INSUFFICIENT at two
thresholds, verdict rates, and the flips against the served verdicts.

Usage (from rag_service/app; PYTHONUTF8=1 on Windows):
    python -m RAG.GraphRAG.evaluation.evaluator_variants --phase run --variants v1_full_ctx,v2_subqueries
    python -m RAG.GraphRAG.evaluation.evaluator_variants --phase score
"""

from __future__ import annotations

import argparse
import io
import json
import sys
import time
from pathlib import Path

if __package__ is None or __package__ == "evaluation":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    __package__ = "GraphRAG.evaluation"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from .agentic_ablation import RESULTS_DIR, context_recall
from .crosslingual_generation_benchmark import DEFAULT_DATASET, load_samples

ABLATION_PATH = RESULTS_DIR / "agentic_ablation.jsonl"
RUNS_PATH = RESULTS_DIR / "evaluator_variants.jsonl"
REPORT_PATH = RESULTS_DIR / "evaluator_variants.md"

VARIANTS = ("v0_served", "v1_full_ctx", "v2_subqueries")


# The served prompt judges coverage against four fixed phases. v2 keeps the
# answerability gate, the semantic-coverage rules and the strategy block, and
# replaces only the rubric: the attacker actions the decomposer extracted from
# this incident, which is what retrieval itself was aimed at.
V2_SYSTEM_PROMPT = """\
You are a context sufficiency evaluator for a MITRE ATT&CK incident analysis system.

Evaluate whether the retrieved context is sufficient to answer the incident query.

STEP 0 — ANSWERABILITY GATE (check this BEFORE judging the context):
An incident analysis needs an incident. If the query contains NO concrete
attacker action — e.g. it only refers to "this incident" / "the attack" without
describing what happened, or states only an outcome ("data leaked", "system was
hacked") with no HOW — the verdict is INSUFFICIENT no matter how relevant the
retrieved context looks. Topically related context can NEVER substitute for a
missing incident description. You cannot ask the user for the missing details,
so in this case set strategy to ACKNOWLEDGE_LIMIT and write a message stating
that the incident description is too vague to map to ATT&CK techniques and
naming what is needed (attack vector / attacker actions / affected systems).

RULES:
- Coverage is judged against the RETRIEVED CONTEXT only. Mark an attacker
  action covered only when the context contains a technique whose description
  matches that behavior.
- Judge the ATTACKER ACTIONS listed below — the actions this incident actually
  describes. Do NOT require phases the incident never mentions: an incident with
  no privilege escalation is not missing anything by having no privilege
  escalation technique in context.
- Ignore retrieved entries that do not match any described attacker action
  (unrelated threat groups, software, campaigns, mitigations) — they add no
  coverage even if they dominate the context.
- Judge based on SEMANTIC coverage, not exact keyword match. An action is
  "covered" if a technique's description matches it, even if not explicitly named.
- In `reason`, refer to the attacker actions in words. Do NOT cite numeric
  ATT&CK IDs (T#### or TA####) unless they appear VERBATIM in the RETRIEVED
  CONTEXT — invented IDs mislead the analyst.

Output JSON:
{
  "verdict": "SUFFICIENT" | "INSUFFICIENT",
  "covered_phases": [<attacker actions covered, in words>],
  "missing_phases": [<attacker actions with no matching technique in context>],
  "reason": "<brief explanation>",
  "strategy": "<BROADEN_SEARCH | PARTIAL_ANSWER | ACKNOWLEDGE_LIMIT or null>",
  "new_query": "<new query if BROADEN_SEARCH, else null>",
  "gap_warning": "<warning if PARTIAL_ANSWER, else null>",
  "message": "<message if ACKNOWLEDGE_LIMIT, else null>"
}

Threshold:
- If every attacker action listed has a matching technique in the context → SUFFICIENT
- If most actions are covered and only a minor one is missing → SUFFICIENT
- Only if a described attacker action central to the incident has NO matching
  technique in the context → INSUFFICIENT

STRATEGY — required whenever the verdict is INSUFFICIENT.
This is a fully automated retrieval loop. You CANNOT ask the user for more
information, and no further input will arrive: the incident description you
were given is all there will ever be. Recovery must come from re-querying the
knowledge base. You are on attempt {retry_hint} of {max_retries}.

Pick exactly ONE strategy:

1. BROADEN_SEARCH  ← prefer this while attempts remain
   Use when: the incident IS described but the context has no technique for one
             of the attacker actions listed
   Action: Re-query by describing THAT missing attacker action in plain
           language, in the language of the incident
   Output: { "strategy": "BROADEN_SEARCH", "new_query": "..." }
   The new_query is embedded verbatim for vector search, so write ONE plain
   sentence: no markdown, no ATT&CK ID numbers (T1110, TA0006), no bullet lists.
   It must differ meaningfully from the queries already tried.

2. PARTIAL_ANSWER
   Use when: only one minor action is missing
   Output: { "strategy": "PARTIAL_ANSWER", "gap_warning": "..." }

3. ACKNOWLEDGE_LIMIT
   Use when: the incident description is too vague to map (answerability gate above)
   Output: { "strategy": "ACKNOWLEDGE_LIMIT", "message": "..." }

Never use FORCE_SUFFICIENT — answering with known-incomplete context without flagging gaps misleads the analyst."""


def _build_user_prompt(query: str, context: str, sub_queries: list[str] | None) -> str:
    """Mirrors ContextEvaluator._build_prompt, minus the 4000-char cut."""
    parts = ["=== USER QUERY ===", f"Original : {query}"]
    if sub_queries:
        parts += ["", "=== ATTACKER ACTIONS IN THIS INCIDENT ==="]
        parts += [f"{i}. {q}" for i, q in enumerate(sub_queries, 1)]
    parts += ["", "=== RETRIEVED CONTEXT ===", context]
    return "\n".join(parts)


def _load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def _ablation_first_pass() -> dict[str, dict]:
    """sample_id -> {context, sub_queries, verdict} from arm A's first pass."""
    out: dict[str, dict] = {}
    for row in _load_jsonl(ABLATION_PATH):
        if row["arm"] != "A":
            continue
        retrieve = next(t for t in row["trace"] if t["node"] == "retrieve")
        evaluate = next(t for t in row["trace"] if t["node"] == "evaluate_context")
        out[row["sample_id"]] = {
            "context": row["first_context"],
            "sub_queries": retrieve["sub_queries"],
            "verdict": evaluate["verdict"],
            "strategy": evaluate["strategy"],
        }
    return out


# ══════════════════════════════════════════════════════════════════════════════
# RUN
# ══════════════════════════════════════════════════════════════════════════════


def phase_run(variants: list[str], max_samples: int) -> None:
    from langchain_core.messages import HumanMessage, SystemMessage

    from ..config import EVALUATOR_MAX_TOKENS, EVALUATOR_TEMPERATURE, LLM_MODEL
    from ..llm_provider import create_core_chat_model
    from ..pipeline.evaluator import EVALUATOR_SYSTEM_PROMPT, ContextEvaluator

    samples = {s["id"]: s for s in load_samples(DEFAULT_DATASET, max_samples)}
    first_pass = _ablation_first_pass()
    done = {(r["sample_id"], r["variant"]) for r in _load_jsonl(RUNS_PATH)}
    todo = [(sid, v) for sid in samples if sid in first_pass
            for v in variants if v != "v0_served" and (sid, v) not in done]
    print(f"[VARIANTS] {len(todo)} judgements to make")
    if not todo:
        return

    llm = create_core_chat_model(
        anthropic_model=LLM_MODEL,
        temperature=EVALUATOR_TEMPERATURE,
        max_tokens=EVALUATOR_MAX_TOKENS,
    )
    # Both variants are first-pass judgements: attempt 1 of MAX_RETRIES.
    served_prompt = EVALUATOR_SYSTEM_PROMPT.replace("{retry_hint}", "1").replace("{max_retries}", "2")
    v2_prompt = V2_SYSTEM_PROMPT.replace("{retry_hint}", "1").replace("{max_retries}", "2")

    for i, (sid, variant) in enumerate(todo, 1):
        entry = first_pass[sid]
        system = served_prompt if variant == "v1_full_ctx" else v2_prompt
        user = _build_user_prompt(
            samples[sid]["query"], entry["context"],
            entry["sub_queries"] if variant == "v2_subqueries" else None,
        )
        t0 = time.perf_counter()
        try:
            response = llm.invoke([SystemMessage(content=system), HumanMessage(content=user)])
        except Exception as e:  # noqa: BLE001 — resume on the next run
            print(f"[VARIANTS] [{i}/{len(todo)}] {sid} {variant} FAILED ({type(e).__name__}: {e})")
            continue
        result = ContextEvaluator._parse_response(
            response.content if isinstance(response.content, str)
            else "".join(b.get("text", "") for b in response.content if isinstance(b, dict))
        )
        usage = getattr(response, "usage_metadata", None) or {}
        row = {
            "sample_id": sid,
            "variant": variant,
            "verdict": result.verdict,
            "strategy": result.strategy or "",
            "reason": result.reason or "",
            "new_query": result.new_query or "",
            "missing_phases": list(result.missing_phases or []),
            "latency_ms": round((time.perf_counter() - t0) * 1000, 1),
            "input_tokens": usage.get("input_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0),
        }
        RUNS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(RUNS_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"[VARIANTS] [{i}/{len(todo)}] {sid} {variant} -> {result.verdict}")


# ══════════════════════════════════════════════════════════════════════════════
# SCORE
# ══════════════════════════════════════════════════════════════════════════════


def _detector_scores(judgements: list[tuple[str, float]], threshold: float) -> dict:
    """INSUFFICIENT as a detector of 'context recall below threshold'."""
    tp = sum(1 for v, r in judgements if v == "INSUFFICIENT" and r < threshold)
    fp = sum(1 for v, r in judgements if v == "INSUFFICIENT" and r >= threshold)
    fn = sum(1 for v, r in judgements if v != "INSUFFICIENT" and r < threshold)
    tn = sum(1 for v, r in judgements if v != "INSUFFICIENT" and r >= threshold)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "precision": precision,
            "recall": recall, "f1": f1, "accuracy": (tp + tn) / len(judgements)}


def phase_score(max_samples: int) -> None:
    samples = {s["id"]: s for s in load_samples(DEFAULT_DATASET, max_samples)}
    first_pass = _ablation_first_pass()
    rows = _load_jsonl(RUNS_PATH)

    verdicts: dict[str, dict[str, str]] = {"v0_served": {}}
    for sid, entry in first_pass.items():
        verdicts["v0_served"][sid] = entry["verdict"]
    for row in rows:
        verdicts.setdefault(row["variant"], {})[row["sample_id"]] = row["verdict"]

    present = [v for v in VARIANTS if verdicts.get(v)]
    common = sorted(set.intersection(*(set(verdicts[v]) for v in present)))
    if not common:
        print("[SCORE] No sample judged by every variant")
        return
    recall_of = {sid: context_recall(first_pass[sid]["context"], samples[sid]) for sid in common}
    tokens = {v: [r for r in rows if r["variant"] == v and r["sample_id"] in common]
              for v in present}

    lines = [
        "# Evaluator Prompt Variants — verdicts on arm A's first-pass contexts",
        "",
        f"- {len(common)} incidents, same contexts for every variant "
        f"(`{ABLATION_PATH.name}`), so only the evaluator changes.",
        "- `v0_served`: the verdicts the served evaluator produced during the ablation "
        "(first 4000 context chars, four fixed phases).",
        "- `v1_full_ctx`: served prompt, whole context.",
        "- `v2_subqueries`: whole context, coverage judged against the incident's own "
        "decomposed sub-queries.",
        "",
        "Ground truth is the context itself: how much of the sample's gold ATT&CK IDs it "
        "contains. INSUFFICIENT is treated as a detector of a context that is missing "
        "gold. Recall counts IDs only (a technique present by name alone counts as "
        "missing), so absolute rates are conservative — but identical across variants.",
        "",
        "## Verdicts",
        "",
        "| Variant | INSUFFICIENT | mean gold recall when SUFFICIENT | when INSUFFICIENT | "
        "flips vs served (S→I / I→S) |",
        "|---|---|---|---|---|",
    ]
    for v in present:
        vs = verdicts[v]
        insuff = [sid for sid in common if vs[sid] == "INSUFFICIENT"]
        suff = [sid for sid in common if vs[sid] != "INSUFFICIENT"]
        si = sum(1 for sid in common
                 if verdicts["v0_served"][sid] == "SUFFICIENT" and vs[sid] == "INSUFFICIENT")
        is_ = sum(1 for sid in common
                  if verdicts["v0_served"][sid] == "INSUFFICIENT" and vs[sid] == "SUFFICIENT")
        mean_s = sum(recall_of[s] for s in suff) / len(suff) if suff else 0.0
        mean_i = sum(recall_of[s] for s in insuff) / len(insuff) if insuff else 0.0
        lines.append(
            f"| {v} | {len(insuff)}/{len(common)} ({len(insuff) / len(common):.0%}) | "
            f"{mean_s:.3f} | {mean_i:.3f} | {si} / {is_} |"
        )

    for threshold, label in ((1.0, "context is missing ANY gold technique"),
                             (0.5, "context is missing MOST gold techniques")):
        lines += ["", f"## INSUFFICIENT as a detector of: {label} (recall < {threshold})", "",
                  "| Variant | precision | recall | F1 | accuracy | TP/FP/FN/TN |",
                  "|---|---|---|---|---|---|"]
        for v in present:
            d = _detector_scores([(verdicts[v][sid], recall_of[sid]) for sid in common], threshold)
            lines.append(
                f"| {v} | {d['precision']:.3f} | {d['recall']:.3f} | {d['f1']:.3f} | "
                f"{d['accuracy']:.3f} | {d['tp']}/{d['fp']}/{d['fn']}/{d['tn']} |"
            )

    lines += ["", "## Cost", "",
              "| Variant | calls | input tokens (mean) | output tokens (mean) | latency (s, mean) |",
              "|---|---|---|---|---|"]
    for v in present:
        rs = tokens.get(v) or []
        if not rs:
            lines.append(f"| {v} | 0 (reused from the ablation run) | — | — | — |")
            continue
        lines.append(
            f"| {v} | {len(rs)} | {sum(r['input_tokens'] for r in rs) / len(rs):.0f} | "
            f"{sum(r['output_tokens'] for r in rs) / len(rs):.0f} | "
            f"{sum(r['latency_ms'] for r in rs) / len(rs) / 1000:.1f} |"
        )

    report = "\n".join(lines) + "\n"
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(report)
    print(f"[SCORE] Report saved to {REPORT_PATH}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluator prompt variant probe")
    parser.add_argument("--phase", choices=["run", "score", "all"], required=True)
    parser.add_argument("--variants", default="v1_full_ctx,v2_subqueries")
    parser.add_argument("--max-samples", type=int, default=0)
    args = parser.parse_args()

    variants = [v.strip() for v in args.variants.split(",") if v.strip()]
    unknown = set(variants) - set(VARIANTS)
    if unknown:
        parser.error(f"unknown variant(s): {', '.join(sorted(unknown))}")

    if args.phase in ("run", "all"):
        phase_run(variants, args.max_samples)
    if args.phase in ("score", "all"):
        phase_score(args.max_samples)


if __name__ == "__main__":
    main()
