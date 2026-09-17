"""
Agentic Ablation Benchmark
===========================
How much do the agentic parts of the served pipeline change the answer?
Scored as ATT&CK technique precision / recall / F1 against analyst-assigned
gold IDs on the real-CTI tier (100 Thai incidents, 347 attack steps).

Arms:

  A  full agent        GraphRAGAgent.query() as served: route -> decompose ->
                       retrieve_multi_quota -> evaluator -> broaden (<= 2) ->
                       reasoning. HEADLINE arm.
  B  - self-reflection A with the evaluator / broaden loop removed: reasoning
                       on A's first-pass context. Derived inside A's run, not
                       a separate run (see below). Ablation.
  C  fast path         GraphRAGAgent.query_fast(): one hybrid retrieve on the
                       raw query, no decomposition / quota, no evaluator.
                       Ablation.

A - B isolates the self-reflection loop. B - C isolates decomposition + quota,
together with the smaller context query_fast renders (build_context defaults:
5 vector hits and 3 subgraphs, against the agent's 15 and 8). That context-size
difference is part of what query_fast is, and is reported as a confound.

Why B is a branch of A, not its own run: up to the first evaluation the served
graph has already done everything B does — route, prepare, one decomposed quota
retrieval. The evaluator writes nothing the reasoning node reads except the
ACKNOWLEDGE_LIMIT fields. So when the loop does not fire, B's reasoning input is
A's reasoning input and B's answer IS A's answer. Only when the loop fires
(a second retrieval, or the ACKNOWLEDGE_LIMIT message replacing the answer) does
B need its own call: the served reasoning node, run on A's first-pass context.
A - B is then exactly the loop's effect, with no rerun noise on the samples
where the loop did nothing. The served graph is streamed node by node
(graph.stream) from GraphRAGAgent.initial_state(), so A is production, not a
re-implementation of it.

Phases:

  run    paid. Per sample: A (+ derived B), then C. Appends one JSON row per
         (sample, arm) to results/agentic_ablation[_tag].jsonl; rerunning
         resumes. Rows whose run hit an LLM exception are NOT written, so a
         resume retries them.
  score  free. Deterministic metrics + paired statistics
         -> results/agentic_ablation[_tag].md

Usage (from rag_service/app; PYTHONUTF8=1 on Windows):
    python -m RAG.GraphRAG.evaluation.agentic_ablation --phase run --max-samples 5 --run-tag smoke
    python -m RAG.GraphRAG.evaluation.agentic_ablation --phase score --run-tag smoke
    python -m RAG.GraphRAG.evaluation.agentic_ablation --phase all
"""

from __future__ import annotations

import argparse
import io
import json
import statistics
import subprocess
import sys
import time
from pathlib import Path

# Fix relative imports when run directly
if __package__ is None or __package__ == "evaluation":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    __package__ = "GraphRAG.evaluation"

# UTF-8 fix for Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from .attack_id_metrics import (
    extract_all_techniques,
    extract_technique_ids,
    technique_set_score,
)
from .crosslingual_generation_benchmark import (
    DEFAULT_DATASET,
    LOOKUP_PATH,
    _bootstrap_ci,
    _wilcoxon_p,
    load_samples,
)

RESULTS_DIR = Path(__file__).resolve().parent / "results"

ARM_GROUPS = {"agent": ("A", "B"), "fast": ("C",)}
ARM_LABELS = {
    "A": "A  full agent (headline)",
    "B": "B  agent - self-reflection",
    "C": "C  fast path",
}

# OpenRouter list price for openai/gpt-5.6-luna, USD per 1M tokens, read from
# https://openrouter.ai/api/v1/models on 2026-09-17. Override with --price-*.
DEFAULT_PRICE_IN = 0.20
DEFAULT_PRICE_OUT = 1.20


def _paths(run_tag: str) -> tuple[Path, Path]:
    stem = "agentic_ablation" + (f"_{run_tag}" if run_tag else "")
    return RESULTS_DIR / f"{stem}.jsonl", RESULTS_DIR / f"{stem}.md"


def _load_rows(path: Path) -> dict[tuple[str, str], dict]:
    rows: dict[tuple[str, str], dict] = {}
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    row = json.loads(line)
                    rows[(row["sample_id"], row["arm"])] = row
    return rows


def _append_row(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


# ══════════════════════════════════════════════════════════════════════════════
# INSTRUMENTATION — observe the served agent without changing what it does
# ══════════════════════════════════════════════════════════════════════════════


class _LlmMeter:
    """Every core-LLM call the agent makes, in call order, tagged by stage."""

    def __init__(self) -> None:
        self.events: list[dict] = []

    def attach(self, agent) -> None:
        for owner, attr, stage in (
            (agent.router, "llm", "router"),
            (agent.decomposer, "llm", "decompose"),
            (agent.evaluator, "llm", "evaluate"),
            (agent, "reasoning_llm", "reasoning"),
            (agent, "translation_llm", "translate"),
        ):
            llm = getattr(owner, attr, None)
            if llm is not None:
                setattr(owner, attr, _MeteredLlm(llm, self, stage))


class _MeteredLlm:
    """Pass-through proxy: the pipeline only ever calls ``.invoke``.

    A call that raises is still recorded (``error``): the decomposer and the
    evaluator swallow exceptions and fall back silently, so without this an
    outage would read as "the loop never fired".
    """

    def __init__(self, llm, meter: _LlmMeter, stage: str) -> None:
        self._llm = llm
        self._meter = meter
        self._stage = stage

    def invoke(self, *args, **kwargs):
        t0 = time.perf_counter()
        event = {"stage": self._stage, "ms": 0.0, "in": 0, "out": 0, "error": False}
        try:
            response = self._llm.invoke(*args, **kwargs)
            usage = getattr(response, "usage_metadata", None) or {}
            event["in"] = usage.get("input_tokens", 0)
            event["out"] = usage.get("output_tokens", 0)
            return response
        except Exception:
            event["error"] = True
            raise
        finally:
            event["ms"] = round((time.perf_counter() - t0) * 1000, 1)
            self._meter.events.append(event)

    def __getattr__(self, name):
        return getattr(self._llm, name)


def _record_decompositions(agent) -> list[list[str]]:
    """Log each decomposition; _node_retrieve keeps the sub-queries local."""
    log: list[list[str]] = []
    original = agent.decomposer.decompose

    def recording(*args, **kwargs):
        subs = original(*args, **kwargs)
        log.append(list(subs))
        return subs

    agent.decomposer.decompose = recording
    return log


def _summarise_events(events: list[dict]) -> dict:
    stages: dict[str, int] = {}
    for e in events:
        if not e["error"]:
            stages[e["stage"]] = stages.get(e["stage"], 0) + 1
    return {
        "llm_calls": sum(stages.values()),
        "calls_by_stage": stages,
        "llm_errors": sum(1 for e in events if e["error"]),
        "llm_ms": round(sum(e["ms"] for e in events), 1),
        "input_tokens": sum(e["in"] for e in events),
        "output_tokens": sum(e["out"] for e in events),
    }


def _git_commit() -> str:
    try:
        sha = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
            cwd=Path(__file__).resolve().parent, check=True,
        ).stdout.strip()
        dirty = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=no"], capture_output=True,
            text=True, cwd=Path(__file__).resolve().parent, check=True,
        ).stdout.strip()
        return sha + ("-dirty" if dirty else "")
    except Exception:  # noqa: BLE001 — provenance is best-effort
        return "unknown"


# ══════════════════════════════════════════════════════════════════════════════
# PHASE RUN
# ══════════════════════════════════════════════════════════════════════════════


def run_full_agent(agent, meter: _LlmMeter, decomp_log: list, query: str) -> dict:
    """Arm A: stream the served graph, recording what every node did."""
    state = dict(agent.initial_state(query, verbose=False))
    trace: list[dict] = []
    first_context: str | None = None
    final_context = ""

    start = mark_t = time.perf_counter()
    start_e = mark_e = len(meter.events)
    mark_d = len(decomp_log)

    for chunk in agent.graph.stream(state, stream_mode="updates"):
        now = time.perf_counter()
        for node, update in chunk.items():
            update = update or {}
            state.update(update)
            events = meter.events[mark_e:]
            mark_e = len(meter.events)
            entry = {
                "node": node,
                "ms": round((now - mark_t) * 1000, 1),
                "calls": [e["stage"] for e in events if not e["error"]],
                "errors": sum(1 for e in events if e["error"]),
                "in": sum(e["in"] for e in events),
                "out": sum(e["out"] for e in events),
                "llm_ms": round(sum(e["ms"] for e in events), 1),
            }
            if node == "retrieve":
                subs = decomp_log[mark_d:]
                mark_d = len(decomp_log)
                result = update.get("graphrag_result")
                final_context = update.get("context", "")
                if first_context is None:
                    first_context = final_context
                entry.update(
                    sub_queries=subs[-1] if subs else [],
                    rewrites=list(state.get("rewritten_queries") or []),
                    n_vector=len(result.vector_results) if result else 0,
                    n_graph=len(result.graph_results) if result else 0,
                    context_chars=len(final_context),
                )
            elif node == "evaluate_context":
                ev = update.get("evaluation")
                entry.update(
                    verdict=getattr(ev, "verdict", ""),
                    strategy=getattr(ev, "strategy", "") or "",
                    reason=getattr(ev, "reason", "") or "",
                    new_query=getattr(ev, "new_query", "") or "",
                    missing_phases=list(getattr(ev, "missing_phases", None) or []),
                    llm_judged="evaluate" in entry["calls"],
                )
            elif node == "broaden_search":
                entry["broaden_count"] = update.get("broaden_count", 0)
            trace.append(entry)
        mark_t = now

    retrieves = [t for t in trace if t["node"] == "retrieve"]
    evaluations = [t for t in trace if t["node"] == "evaluate_context"]
    reasoning = next((t for t in trace if t["node"] == "reasoning"), None)
    # Standard reasoning always calls the reasoning LLM; the ACKNOWLEDGE_LIMIT
    # fast path returns the evaluator's message without one.
    ack_limit = reasoning is not None and "reasoning" not in reasoning["calls"]

    return {
        "arm": "A",
        "answer": state.get("answer", ""),
        "latency_ms": round((time.perf_counter() - start) * 1000, 1),
        **_summarise_events(meter.events[start_e:]),
        "broaden_rounds": sum(1 for t in trace if t["node"] == "broaden_search"),
        "n_retrieves": len(retrieves),
        "first_verdict": evaluations[0]["verdict"] if evaluations else "",
        "first_strategy": evaluations[0]["strategy"] if evaluations else "",
        "ack_limit": ack_limit,
        "b_identical": len(retrieves) == 1 and not ack_limit,
        "trace": trace,
        "first_context": first_context or "",
        # Only stored when it differs — otherwise it is first_context again.
        "final_context": final_context if len(retrieves) > 1 else None,
    }


def derive_b(agent, meter: _LlmMeter, a_row: dict, query: str) -> dict:
    """Arm B from A's run: served reasoning on A's first-pass context."""
    trace = a_row["trace"]
    first_retrieve = next(i for i, t in enumerate(trace) if t["node"] == "retrieve")
    shared = trace[: first_retrieve + 1]  # route_query, prepare, first retrieve

    if a_row["b_identical"]:
        tail = [t for t in trace if t["node"] in ("reasoning", "translate_output")]
        parts = shared + tail
        calls: dict[str, int] = {}
        for t in parts:
            for stage in t["calls"]:
                calls[stage] = calls.get(stage, 0) + 1
        return {
            "arm": "B",
            "derived_from": "A",
            "identical_to_A": True,
            "answer": a_row["answer"],
            "latency_ms": round(sum(t["ms"] for t in parts), 1),
            "llm_calls": sum(calls.values()),
            "calls_by_stage": calls,
            "llm_errors": 0,
            "llm_ms": round(sum(t["llm_ms"] for t in parts), 1),
            "input_tokens": sum(t["in"] for t in parts),
            "output_tokens": sum(t["out"] for t in parts),
        }

    # The loop changed A's answer path: run the served reasoning (and, if the
    # served edge asks for it, translation) nodes on the first-pass context.
    state = dict(agent.initial_state(query, verbose=False))
    state.update(agent._node_prepare(state))
    state["context"] = a_row["first_context"]

    mark = len(meter.events)
    t0 = time.perf_counter()
    state.update(agent._node_reasoning(state))
    if agent._edge_after_reasoning(state) == "translate":
        state.update(agent._node_translate_output(state))
    branch_ms = (time.perf_counter() - t0) * 1000
    branch = _summarise_events(meter.events[mark:])

    for t in shared:
        for stage in t["calls"]:
            branch["calls_by_stage"][stage] = branch["calls_by_stage"].get(stage, 0) + 1
    return {
        "arm": "B",
        "derived_from": "A",
        "identical_to_A": False,
        "answer": state.get("answer", ""),
        "latency_ms": round(sum(t["ms"] for t in shared) + branch_ms, 1),
        "llm_calls": sum(branch["calls_by_stage"].values()),
        "calls_by_stage": branch["calls_by_stage"],
        "llm_errors": branch["llm_errors"],
        "llm_ms": round(sum(t["llm_ms"] for t in shared) + branch["llm_ms"], 1),
        "input_tokens": sum(t["in"] for t in shared) + branch["input_tokens"],
        "output_tokens": sum(t["out"] for t in shared) + branch["output_tokens"],
    }


def run_fast(agent, meter: _LlmMeter, query: str) -> dict:
    """Arm C: the served fast path, untouched."""
    mark = len(meter.events)
    t0 = time.perf_counter()
    response = agent.query_fast(query, verbose=False)
    return {
        "arm": "C",
        "answer": response.answer,
        "latency_ms": round((time.perf_counter() - t0) * 1000, 1),
        **_summarise_events(meter.events[mark:]),
        "context": response.context,
    }


def phase_run(
    samples: list[dict], groups: list[str], runs_path: Path, max_failures: int
) -> None:
    rows = _load_rows(runs_path)
    wanted = [(s["id"], arm) for s in samples for g in groups for arm in ARM_GROUPS[g]]
    missing = [key for key in wanted if key not in rows]
    print(f"[RUN] {len(samples)} samples, arms {groups} -> {len(missing)} of "
          f"{len(wanted)} rows to produce ({runs_path.name})")
    if not missing:
        return

    from ..config import LLM_MODEL
    from ..llm_provider import resolve_core_llm_target
    from ..pipeline.agent_graph import GraphRAGAgent

    target = resolve_core_llm_target(LLM_MODEL)
    meta = {"model": f"{target.provider}:{target.model}", "commit": _git_commit()}
    print(f"[RUN] Core LLM: {meta['model']}  commit: {meta['commit']}")

    agent = GraphRAGAgent()
    meter = _LlmMeter()
    meter.attach(agent)
    decomp_log = _record_decompositions(agent)

    failures = 0
    try:
        for i, sample in enumerate(samples, 1):
            sid, query = sample["id"], sample["query"]
            for group in groups:
                if all((sid, arm) in rows for arm in ARM_GROUPS[group]):
                    continue
                print(f"\n[RUN] [{i}/{len(samples)}] {sid} :: {group}")
                try:
                    if group == "agent":
                        a_row = rows.get((sid, "A"))
                        if a_row is None:
                            a_row = {"sample_id": sid, **meta,
                                     **run_full_agent(agent, meter, decomp_log, query)}
                            if a_row["llm_errors"]:
                                raise RuntimeError(f"{a_row['llm_errors']} LLM call(s) failed")
                            _append_row(runs_path, a_row)
                            rows[(sid, "A")] = a_row
                        if (sid, "B") not in rows:
                            b_row = {"sample_id": sid, **meta,
                                     **derive_b(agent, meter, a_row, query)}
                            _append_row(runs_path, b_row)
                            rows[(sid, "B")] = b_row
                        print(f"[RUN]   A: {a_row['latency_ms'] / 1000:.1f}s "
                              f"{a_row['llm_calls']} calls, first={a_row['first_verdict']} "
                              f"broaden={a_row['broaden_rounds']} ack={a_row['ack_limit']}")
                    elif group == "fast":
                        c_row = {"sample_id": sid, **meta, **run_fast(agent, meter, query)}
                        if c_row["llm_errors"]:
                            raise RuntimeError(f"{c_row['llm_errors']} LLM call(s) failed")
                        _append_row(runs_path, c_row)
                        rows[(sid, "C")] = c_row
                        print(f"[RUN]   C: {c_row['latency_ms'] / 1000:.1f}s "
                              f"{c_row['llm_calls']} calls")
                    failures = 0
                except Exception as e:  # noqa: BLE001 — keep going, resume later
                    failures += 1
                    print(f"[RUN]   FAILED ({type(e).__name__}: {e}) — not saved, "
                          f"rerun to retry [{failures}/{max_failures} consecutive]")
                    if failures >= max_failures:
                        print("[RUN] Too many consecutive failures — stopping "
                              "(credits / rate limit?). Rerun the same command to resume.")
                        return
    finally:
        agent.close()


# ══════════════════════════════════════════════════════════════════════════════
# PHASE SCORE — deterministic, free
# ══════════════════════════════════════════════════════════════════════════════


def _roll_up(ids: set[str]) -> set[str]:
    """T1566.002 -> T1566.

    Every gold ID in the real-CTI tier is parent-granular (0 of 366 has a
    sub-technique), so an answer citing the correct sub-technique would score
    only the 0.5 same-family credit against its own parent. Rolling predictions
    up compares the two at the gold's granularity; duplicates collapse, so two
    sub-techniques of one parent still claim one gold ID.
    """
    return {i.split(".")[0] for i in ids}


def score_answer(answer: str, sample: dict, alias_map: dict) -> dict:
    """Technique P/R/F1 of one answer, plus per-step recall by cue type."""
    gold = {g.upper() for g in sample["gold_attack_ids"]}
    predicted_raw = extract_all_techniques(answer, alias_map)
    predicted = _roll_up(predicted_raw)

    main = technique_set_score(predicted, gold)
    raw = technique_set_score(predicted_raw, gold)
    ids_only = technique_set_score(_roll_up(extract_technique_ids(answer)), gold)

    step_recall: dict[str, list[float]] = {}
    for step in sample.get("attack_steps", []):
        step_gold = {g.upper() for g in step.get("gold_attack_ids", [])}
        if step_gold:
            step_recall.setdefault(step.get("cue_type", "unspecified"), []).append(
                technique_set_score(predicted, step_gold)["recall"]
            )

    return {
        "precision": main["precision"],
        "recall": main["recall"],
        "f1": main["f1"],
        # micro-average ingredients: matched credit, |predicted|, |gold|
        "matched": main["recall"] * len(gold),
        "n_pred": len(predicted),
        "n_gold": len(gold),
        "f1_raw": raw["f1"],
        "f1_ids_only": ids_only["f1"],
        "step_recall": step_recall,
    }


def context_recall(context: str, sample: dict, alias_map: dict) -> float:
    """Share of gold techniques mentioned anywhere in the rendered context."""
    gold = {g.upper() for g in sample["gold_attack_ids"]}
    found = _roll_up(extract_all_techniques(context or "", alias_map))
    return technique_set_score(found, gold)["recall"]


def _mean(vals: list[float]) -> float:
    return sum(vals) / len(vals) if vals else 0.0


def _micro(scores: list[dict]) -> tuple[float, float, float]:
    matched = sum(s["matched"] for s in scores)
    n_pred = sum(s["n_pred"] for s in scores)
    n_gold = sum(s["n_gold"] for s in scores)
    p = matched / n_pred if n_pred else 0.0
    r = matched / n_gold if n_gold else 0.0
    return p, r, (2 * p * r / (p + r) if p + r else 0.0)


def paired(left: dict[str, float], right: dict[str, float], ids: list[str]) -> dict:
    """Mean paired delta (left - right), bootstrap 95% CI, Wilcoxon, W/T/L."""
    deltas = [left[i] - right[i] for i in ids]
    lo, hi = _bootstrap_ci(deltas)
    return {
        "n": len(deltas),
        "mean": _mean(deltas),
        "ci": (lo, hi),
        "p": _wilcoxon_p(deltas),
        "wins": sum(1 for d in deltas if d > 1e-9),
        "ties": sum(1 for d in deltas if abs(d) <= 1e-9),
        "losses": sum(1 for d in deltas if d < -1e-9),
    }


def _fmt_paired(label: str, st: dict) -> str:
    if not st["n"]:
        return f"| {label} | — | — | — | 0 | — |"
    p = f"{st['p']:.4f}" if st["p"] is not None else "n/a"
    lo, hi = st["ci"]
    sig = " *" if lo > 0 or hi < 0 else ""
    return (f"| {label} | {st['mean']:+.3f}{sig} | [{lo:+.3f}, {hi:+.3f}] | {p} | "
            f"{st['n']} | {st['wins']}/{st['ties']}/{st['losses']} |")


def _pct(xs: list[float], q: float) -> float:
    if not xs:
        return 0.0
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(round(q * (len(xs) - 1))))]


def phase_score(
    samples: list[dict], runs_path: Path, report_path: Path,
    price_in: float, price_out: float,
) -> None:
    by_id = {s["id"]: s for s in samples}
    rows = _load_rows(runs_path)
    with open(LOOKUP_PATH, "r", encoding="utf-8") as f:
        alias_map = json.load(f)["alias_map"]

    arms = [a for a in ("A", "B", "C") if any(k[1] == a for k in rows)]
    if not arms:
        print(f"[SCORE] No rows in {runs_path}")
        return

    # Only samples every present arm has, so every column is the same population.
    common = sorted(
        sid for sid in by_id if all((sid, a) in rows for a in arms)
    )
    if not common:
        print(f"[SCORE] No sample has a row for every arm in {arms}")
        return
    scores = {a: {sid: score_answer(rows[(sid, a)]["answer"], by_id[sid], alias_map)
                  for sid in common} for a in arms}
    n_steps = {ct: sum(1 for sid in common for st in by_id[sid]["attack_steps"]
                       if st.get("cue_type") == ct) for ct in ("named", "described")}
    first = rows[(common[0], arms[0])]

    lines = [
        "# Agentic Ablation — ATT&CK Technique P / R / F1",
        "",
        f"- Dataset: real-CTI tier (`{DEFAULT_DATASET.name}`), {len(common)} samples "
        f"({n_steps['named']} named / {n_steps['described']} described steps)",
        f"- Core LLM: `{first.get('model', '?')}`; commit `{first.get('commit', '?')}`",
        f"- Run file: `{runs_path.name}`",
        "- Arms: **A** full agent (headline) · **B** A without the evaluator/broaden "
        "loop (derived from A's first pass) · **C** `query_fast()`",
        "",
        "Scoring: techniques cited in the answer by ID or canonical English name "
        "(`extract_all_techniques`), rolled up to the parent technique because all "
        "gold IDs are parent-level, then `technique_set_score` against the sample's "
        "`gold_attack_ids`. Macro = mean over samples; micro = pooled matches.",
        "",
        "## 1. Technique precision / recall / F1",
        "",
        "| Metric | " + " | ".join(ARM_LABELS[a] for a in arms) + " |",
        "|---|" + "---|" * len(arms),
    ]

    def row(name: str, fn) -> None:
        lines.append(f"| {name} | " + " | ".join(fn(a) for a in arms) + " |")

    for key in ("precision", "recall", "f1"):
        row(f"Macro {key}", lambda a, k=key: f"{_mean([s[k] for s in scores[a].values()]):.3f}")
    micro = {a: _micro(list(scores[a].values())) for a in arms}
    for idx, key in enumerate(("precision", "recall", "f1")):
        row(f"Micro {key}", lambda a, i=idx: f"{micro[a][i]:.3f}")
    row("Macro F1, no parent roll-up", lambda a: f"{_mean([s['f1_raw'] for s in scores[a].values()]):.3f}")
    row("Macro F1, cited IDs only (no name match)",
        lambda a: f"{_mean([s['f1_ids_only'] for s in scores[a].values()]):.3f}")
    row("Mean techniques predicted", lambda a: f"{_mean([s['n_pred'] for s in scores[a].values()]):.2f}")
    row("Answers citing no technique",
        lambda a: f"{sum(1 for s in scores[a].values() if s['n_pred'] == 0)}")

    lines += ["", "### Step recall by cue type", "",
              "Precision cannot be split by cue type — a predicted technique belongs to "
              "the answer, not to a step — so the split is recall only: the share of "
              "steps whose gold technique the answer cites.", "",
              "| Cue type (steps) | " + " | ".join(arms) + " |", "|---|" + "---|" * len(arms)]
    for ct in ("named", "described"):
        cells = []
        for a in arms:
            vals = [v for s in scores[a].values() for v in s["step_recall"].get(ct, [])]
            cells.append(f"{_mean(vals):.3f}")
        lines.append(f"| {ct} ({n_steps[ct]}) | " + " | ".join(cells) + " |")

    # ── Paired comparisons ────────────────────────────────────────────────
    comparisons = [(l, r) for l, r in (("A", "B"), ("B", "C"), ("A", "C"))
                   if l in arms and r in arms]
    if comparisons:
        lines += ["", "## 2. Paired comparisons (same samples)", "",
                  "Δ = left − right, per-sample macro metric. 95% CI: paired bootstrap "
                  "(10k resamples). p: two-sided Wilcoxon signed-rank on non-zero Δ "
                  "(n/a below 6 non-zero pairs). `*` = CI excludes 0. W/T/L = samples "
                  "where left is better / equal / worse.", "",
                  "| Comparison | mean Δ | 95% CI | Wilcoxon p | n | W/T/L |",
                  "|---|---|---|---|---|---|"]
        for l, r in comparisons:
            for key in ("f1", "precision", "recall"):
                st = paired({s: scores[l][s][key] for s in common},
                            {s: scores[r][s][key] for s in common}, common)
                lines.append(_fmt_paired(f"{l} − {r} {key}", st))

    # ── Loop diagnostics ──────────────────────────────────────────────────
    if "A" in arms:
        a_rows = {sid: rows[(sid, "A")] for sid in common}
        n = len(common)
        first_insuff = [sid for sid, r in a_rows.items() if r["first_verdict"] == "INSUFFICIENT"]
        fired = [sid for sid, r in a_rows.items() if r["broaden_rounds"] > 0]
        acked = [sid for sid, r in a_rows.items() if r["ack_limit"]]
        changed = [sid for sid, r in a_rows.items() if not r["b_identical"]]
        rounds = {k: sum(1 for r in a_rows.values() if r["broaden_rounds"] == k) for k in (0, 1, 2)}
        evals = [t for r in a_rows.values() for t in r["trace"] if t["node"] == "evaluate_context"]
        judged = [t for t in evals if t["llm_judged"]]
        insuff_judged = [t for t in judged if t["verdict"] == "INSUFFICIENT"]
        parse_fallback = [t for t in judged if t["reason"].startswith("Could not parse")
                          or "fell back to sufficient" in t["reason"]]
        strategies: dict[str, int] = {}
        for t in insuff_judged:
            strategies[t["strategy"] or "(none)"] = strategies.get(t["strategy"] or "(none)", 0) + 1

        lines += ["", "## 3. Self-reflection loop diagnostics (arm A)", "",
                  "| Diagnostic | Value |", "|---|---|",
                  f"| First-pass verdict INSUFFICIENT | {len(first_insuff)}/{n} ({len(first_insuff) / n:.1%}) |",
                  f"| Broaden rounds used: 0 / 1 / 2 | {rounds[0]} / {rounds[1]} / {rounds[2]} |",
                  f"| Answer replaced by ACKNOWLEDGE_LIMIT | {len(acked)}/{n} ({len(acked) / n:.1%}) |",
                  f"| Samples where the loop changed the answer path (B ≠ A) | {len(changed)}/{n} |",
                  f"| LLM-judged evaluations (excl. forced SUFFICIENT at max retries) | {len(judged)} |",
                  f"| … of which INSUFFICIENT | {len(insuff_judged)} |",
                  f"| … INSUFFICIENT strategies | "
                  + (", ".join(f"{k} {v}" for k, v in sorted(strategies.items())) or "—") + " |",
                  f"| … evaluator parse / exception fallbacks to SUFFICIENT | {len(parse_fallback)} |"]

        if "B" in arms:
            lines += ["", "### A − B restricted to samples where the loop acted", "",
                      "On every other sample B ≡ A by construction (Δ = 0), so the "
                      "all-sample A − B above is this subset's effect diluted by "
                      "the samples the loop never touched.", "",
                      "| Subset | mean Δ F1 | 95% CI | Wilcoxon p | n | W/T/L |",
                      "|---|---|---|---|---|---|"]
            for label, ids in (("broadening fired (≥1 round)", fired),
                               ("ACKNOWLEDGE_LIMIT returned", acked),
                               ("loop changed answer path (any)", changed)):
                st = paired({s: scores["A"][s]["f1"] for s in ids},
                            {s: scores["B"][s]["f1"] for s in ids}, ids)
                lines.append(_fmt_paired(label, st))

            if fired:
                ctx_first = {s: context_recall(a_rows[s]["first_context"], by_id[s], alias_map) for s in fired}
                ctx_final = {s: context_recall(a_rows[s]["final_context"] or a_rows[s]["first_context"],
                                               by_id[s], alias_map) for s in fired}
                st = paired(ctx_final, ctx_first, fired)
                lines += ["", "Did broadening put more gold techniques into the context? "
                          "(gold techniques mentioned anywhere in the rendered context, by ID "
                          "or canonical name — includes subgraph neighbour lists)", "",
                          "| Subset | first-pass ctx recall | final ctx recall | mean Δ | 95% CI | n |",
                          "|---|---|---|---|---|---|",
                          f"| broadening fired | {_mean(list(ctx_first.values())):.3f} | "
                          f"{_mean(list(ctx_final.values())):.3f} | {st['mean']:+.3f} | "
                          f"[{st['ci'][0]:+.3f}, {st['ci'][1]:+.3f}] | {st['n']} |"]

    # ── Context recall vs answer recall, all arms ─────────────────────────
    ctx_of = {
        "A": lambda r: r["final_context"] or r["first_context"],
        "B": lambda r: rows[(r["sample_id"], "A")]["first_context"],
        "C": lambda r: r["context"],
    }
    lines += ["", "## 4. Context recall vs answer recall", "",
              "Context recall: share of gold techniques mentioned anywhere in the context "
              "the reasoning LLM saw (ID or canonical name, subgraph neighbour lists "
              "included, so it is an upper-bound-style measure). The gap to answer recall "
              "is what generation did not carry through.", "",
              "| | " + " | ".join(arms) + " |", "|---|" + "---|" * len(arms)]
    ctx_recall = {a: _mean([context_recall(ctx_of[a](rows[(s, a)]), by_id[s], alias_map)
                            for s in common]) for a in arms}
    lines.append("| Context recall | " + " | ".join(f"{ctx_recall[a]:.3f}" for a in arms) + " |")
    lines.append("| Answer recall (macro) | " + " | ".join(
        f"{_mean([s['recall'] for s in scores[a].values()]):.3f}" for a in arms) + " |")

    # ── Cost ──────────────────────────────────────────────────────────────
    lines += ["", "## 5. Latency and LLM cost per sample", "",
              f"Cost at OpenRouter list price ${price_in:.2f} / ${price_out:.2f} per 1M "
              "input / output tokens. B's latency is reconstructed (A's shared node "
              "timings + its own reasoning), not measured end-to-end. Non-LLM time is "
              "local BGE-M3 / reranker / Neo4j / Qdrant on the benchmark machine and "
              "does not transfer to production hardware.", "",
              "| Metric | " + " | ".join(arms) + " |", "|---|" + "---|" * len(arms)]

    def stat(a: str, key: str) -> list[float]:
        return [rows[(s, a)][key] for s in common]

    row("Latency mean (s)", lambda a: f"{_mean(stat(a, 'latency_ms')) / 1000:.1f}")
    row("Latency median (s)", lambda a: f"{statistics.median(stat(a, 'latency_ms')) / 1000:.1f}")
    row("Latency p90 (s)", lambda a: f"{_pct(stat(a, 'latency_ms'), 0.9) / 1000:.1f}")
    row("… of which LLM (s, mean)", lambda a: f"{_mean(stat(a, 'llm_ms')) / 1000:.1f}")
    row("LLM calls mean", lambda a: f"{_mean(stat(a, 'llm_calls')):.2f}")
    row("LLM calls min–max", lambda a: f"{min(stat(a, 'llm_calls'))}–{max(stat(a, 'llm_calls'))}")
    row("Input tokens mean", lambda a: f"{_mean(stat(a, 'input_tokens')):.0f}")
    row("Output tokens mean", lambda a: f"{_mean(stat(a, 'output_tokens')):.0f}")
    row("Cost per sample (USD)", lambda a: f"{_mean(stat(a, 'input_tokens')) * price_in / 1e6 + _mean(stat(a, 'output_tokens')) * price_out / 1e6:.4f}")

    lines += ["", "## 6. Limitations", "",
              "- **B is a counterfactual branch of A**, not an independent run. That is what "
              "makes A − B exactly the loop's effect, but B ≡ A on samples where the loop "
              "did not act, so the all-sample A − B is necessarily diluted.",
              "- **B − C is not decomposition + quota alone.** `query_fast` also renders a "
              "smaller context (5 vector hits / 3 subgraphs vs 15 / 8) and skips the router "
              "call; the difference bundles all of these.",
              "- **One run per arm.** The core LLM is sampled at temperature 0 but is not "
              "guaranteed deterministic; comparisons involving an independent generation "
              "(B − C, A − C, and A − B on the loop subset) include run-to-run variance, "
              "which the paired CI reflects but cannot separate out.",
              "- **Extraction.** Techniques are found by ID or canonical English name; a "
              "technique described only in Thai without its name or ID is not counted, and "
              "a name mentioned in a negative sense counts as predicted.",
              "- **Gold coverage.** One gold ID (T0827) is ICS, which is not ingested, so it "
              "is unreachable for every arm. The ATT&CK version of the index (v19) differs "
              "from the source advisories' version; drifted IDs penalise all arms equally.",
              ]

    report = "\n".join(lines) + "\n"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    print(report)
    print(f"[SCORE] Report saved to {report_path}")


# ══════════════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════════════


def main() -> None:
    parser = argparse.ArgumentParser(description="Agentic ablation benchmark (A / B / C)")
    parser.add_argument("--phase", choices=["run", "score", "all"], required=True)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--max-samples", type=int, default=0)
    parser.add_argument("--arms", default="agent,fast",
                        help="agent (A + derived B), fast (C); default both")
    parser.add_argument("--run-tag", default="",
                        help="suffix for the results files, e.g. 'smoke'")
    parser.add_argument("--max-consecutive-failures", type=int, default=3)
    parser.add_argument("--price-in", type=float, default=DEFAULT_PRICE_IN)
    parser.add_argument("--price-out", type=float, default=DEFAULT_PRICE_OUT)
    args = parser.parse_args()

    groups = [g.strip() for g in args.arms.split(",") if g.strip()]
    unknown = set(groups) - set(ARM_GROUPS)
    if unknown:
        parser.error(f"unknown arm group(s): {', '.join(sorted(unknown))}")

    samples = load_samples(args.dataset, args.max_samples)
    runs_path, report_path = _paths(args.run_tag)

    if args.phase in ("run", "all"):
        phase_run(samples, groups, runs_path, args.max_consecutive_failures)
    if args.phase in ("score", "all"):
        phase_score(samples, runs_path, report_path, args.price_in, args.price_out)


if __name__ == "__main__":
    main()
