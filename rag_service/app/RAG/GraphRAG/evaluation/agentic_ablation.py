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

Evaluator probe (no answer, not an arm):

  S  sensitivity       the served evaluator, unchanged, judging C's context —
                       a naturally weaker context for the same incident.

Fix arm:

  F  A + ACK fix       A's own retrieval, re-answered by the reasoning node
                       after ACKNOWLEDGE_LIMIT stopped replacing the analysis
                       (agent_graph honours it only on the first pass, where it
                       means the incident text has nothing to map; afterwards
                       the note rides along as a caveat). Identical to A wherever
                       A did not acknowledge, so F - A isolates that one change.
  M  F + merge         F, with the broaden round replayed the way the pipeline
                       now does it: the second retrieval is merged into the
                       first and the render budget grows by one BROADEN_* step,
                       instead of the two competing for one budget. Retrieval is
                       deterministic and the agent's own sub-queries and rewrite
                       are replayed, so M - F isolates that change; identical to
                       F wherever the agent never broadened.

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

Why S: if the evaluator says SUFFICIENT on (nearly) every sample, A - B is 0
and says only that the loop never acted, not whether it could. S asks whether
the evaluator can tell a weak context from a strong one at all: the same
incident judged on A's first-pass context and on C's. The score phase adds a
calibration table — verdict against the share of gold technique IDs actually
visible to the evaluator (it reads only the first 4000 characters).

Phases:

  run    paid. Per sample: A (+ derived B), then C, then S. Appends one JSON row per
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
from types import SimpleNamespace

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

ARM_GROUPS = {"agent": ("A", "B"), "fast": ("C",), "sensitivity": ("S",),
              "ackfix": ("F",), "mergefix": ("M",)}
ARM_LABELS = {
    "A": "A  full agent (headline)",
    "B": "B  agent - self-reflection",
    "C": "C  fast path",
    "F": "F  A + ACK fix",
    "M": "M  F + broaden merge",
}
SCORED_ARMS = ("A", "B", "C", "F", "M")

# ContextEvaluator._build_prompt shows the evaluator only this much context.
EVALUATOR_CONTEXT_CHARS = 4000

# The four phases EVALUATOR_SYSTEM_PROMPT checks, as ATT&CK tactic shortnames.
EVALUATOR_CHECKLIST_TACTICS = {
    "initial-access", "credential-access", "privilege-escalation", "impact",
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


def run_sensitivity(agent, meter: _LlmMeter, query: str, context: str) -> dict:
    """Probe S: the served evaluator, first-pass settings, on C's context.

    Same call ``_node_evaluate_context`` makes on the first pass
    (english_query mirrors the query, retry_count 0); only the context differs.
    """
    mark = len(meter.events)
    t0 = time.perf_counter()
    ev = agent.evaluator.evaluate(
        original_query=query, english_query=query, context=context,
        retry_count=0, verbose=False,
    )
    return {
        "arm": "S",
        "judged_context": "C",
        "verdict": ev.verdict,
        "strategy": ev.strategy or "",
        "reason": ev.reason or "",
        "new_query": ev.new_query or "",
        "missing_phases": list(ev.missing_phases or []),
        "latency_ms": round((time.perf_counter() - t0) * 1000, 1),
        **_summarise_events(meter.events[mark:]),
    }


def run_ack_fix(agent, meter: _LlmMeter, a_row: dict, query: str) -> dict:
    """Arm F: A re-answered with the ACKNOWLEDGE_LIMIT fix, same retrieval.

    Only A's acknowledged samples change; the rest are A's own row, so the
    comparison costs one reasoning call per affected sample and carries no
    rerun noise anywhere else.
    """
    if not a_row["ack_limit"]:
        return {
            "arm": "F", "derived_from": "A", "identical_to_A": True,
            "answer": a_row["answer"], "latency_ms": a_row["latency_ms"],
            "llm_calls": a_row["llm_calls"], "calls_by_stage": a_row["calls_by_stage"],
            "llm_errors": 0, "llm_ms": a_row["llm_ms"],
            "input_tokens": a_row["input_tokens"], "output_tokens": a_row["output_tokens"],
        }

    # A's answer IS the acknowledgement message — it replaced the analysis.
    last_eval = [t for t in a_row["trace"] if t["node"] == "evaluate_context"][-1]
    state = dict(agent.initial_state(query, verbose=False))
    state.update(agent._node_prepare(state))
    state.update(
        context=a_row["final_context"] or a_row["first_context"],
        strategy=last_eval["strategy"],
        acknowledgement_message=a_row["answer"],
        evaluation=SimpleNamespace(verdict=last_eval["verdict"]),
        broaden_count=a_row["broaden_rounds"],
    )

    mark = len(meter.events)
    t0 = time.perf_counter()
    state.update(agent._node_reasoning(state))
    if agent._edge_after_reasoning(state) == "translate":
        state.update(agent._node_translate_output(state))
    branch_ms = (time.perf_counter() - t0) * 1000
    branch = _summarise_events(meter.events[mark:])

    # A's own answer stage is replaced, so its reasoning/translate cost drops out.
    kept = [t for t in a_row["trace"] if t["node"] not in ("reasoning", "translate_output")]
    for t in kept:
        for stage in t["calls"]:
            branch["calls_by_stage"][stage] = branch["calls_by_stage"].get(stage, 0) + 1
    return {
        "arm": "F",
        "derived_from": "A",
        "identical_to_A": False,
        "answer": state.get("answer", ""),
        "latency_ms": round(sum(t["ms"] for t in kept) + branch_ms, 1),
        "llm_calls": sum(branch["calls_by_stage"].values()),
        "calls_by_stage": branch["calls_by_stage"],
        "llm_errors": branch["llm_errors"],
        "llm_ms": round(sum(t["llm_ms"] for t in kept) + branch["llm_ms"], 1),
        "input_tokens": sum(t["in"] for t in kept) + branch["input_tokens"],
        "output_tokens": sum(t["out"] for t in kept) + branch["output_tokens"],
    }


def run_merge_fix(agent, meter: _LlmMeter, a_row: dict, f_row: dict, query: str) -> dict:
    """Arm M: F with the broaden round merged instead of replaced.

    Replays the agent's own two query sets (recorded in A's trace) through
    retrieval, which is deterministic — the replay reproduces the stored
    contexts exactly (evaluation/results/broaden_merge_probe.md) — then answers
    once from the merged context.
    """
    if a_row["broaden_rounds"] == 0:
        return {**{k: v for k, v in f_row.items()
                   if k not in ("sample_id", "arm", "model", "commit")},
                "arm": "M", "derived_from": "F", "identical_to_F": True}

    from ..config import (
        AGENT_MAX_CONTEXT_CHARS, AGENT_MAX_GRAPH, AGENT_MAX_VECTOR,
        BROADEN_CONTEXT_CHARS_STEP, BROADEN_GRAPH_STEP, BROADEN_VECTOR_STEP,
        VECTOR_TOP_K,
    )
    from ..pipeline.context_builder import build_context
    from ..retrieval.hybrid_retriever import merge_results

    retrieves = [t for t in a_row["trace"] if t["node"] == "retrieve"][:2]
    query_sets = []
    for entry in retrieves:
        queries: list[str] = []
        for q in [query, *entry["sub_queries"], *entry["rewrites"]]:
            if q and q.strip() and q not in queries:
                queries.append(q)
        query_sets.append(queries)

    rounds = a_row["broaden_rounds"]
    wide_vector = AGENT_MAX_VECTOR + BROADEN_VECTOR_STEP * rounds
    wide_graph = AGENT_MAX_GRAPH + BROADEN_GRAPH_STEP * rounds
    wide_chars = AGENT_MAX_CONTEXT_CHARS + BROADEN_CONTEXT_CHARS_STEP * rounds

    t0 = time.perf_counter()
    first = agent.retriever.retrieve_multi_quota(
        query_sets[0], per_query_k=3, top_k=VECTOR_TOP_K,
        max_vector=AGENT_MAX_VECTOR, max_graph=AGENT_MAX_GRAPH,
    )
    broadened = agent.retriever.retrieve_multi_quota(
        query_sets[1], per_query_k=3, top_k=VECTOR_TOP_K,
        max_vector=wide_vector, max_graph=wide_graph,
    )
    context = build_context(
        merge_results(first, broadened), max_context_length=wide_chars,
        max_vector=wide_vector, max_graph=wide_graph,
    )
    retrieval_ms = (time.perf_counter() - t0) * 1000

    # Same answer stage as F, including the acknowledgement caveat where the
    # evaluator asked for one, so the context is the only thing that differs.
    last_eval = [t for t in a_row["trace"] if t["node"] == "evaluate_context"][-1]
    state = dict(agent.initial_state(query, verbose=False))
    state.update(agent._node_prepare(state))
    state.update(
        context=context,
        strategy=last_eval["strategy"] if a_row["ack_limit"] else "",
        acknowledgement_message=a_row["answer"] if a_row["ack_limit"] else "",
        evaluation=SimpleNamespace(verdict=last_eval["verdict"]),
        broaden_count=rounds,
    )

    mark = len(meter.events)
    t1 = time.perf_counter()
    state.update(agent._node_reasoning(state))
    if agent._edge_after_reasoning(state) == "translate":
        state.update(agent._node_translate_output(state))
    answer_ms = (time.perf_counter() - t1) * 1000
    branch = _summarise_events(meter.events[mark:])

    # Everything A spent before its final answer stage still applies.
    kept = [t for t in a_row["trace"] if t["node"] not in ("reasoning", "translate_output")]
    for t in kept:
        for stage in t["calls"]:
            branch["calls_by_stage"][stage] = branch["calls_by_stage"].get(stage, 0) + 1
    return {
        "arm": "M",
        "derived_from": "F",
        "identical_to_F": False,
        "answer": state.get("answer", ""),
        "context": context,
        # The replay reuses A's sub-queries, so it skips the decomposition call
        # each retrieve node paid for; add that LLM time back or M reads faster
        # than it would run.
        "latency_ms": round(
            retrieval_ms + answer_ms
            + sum(t["ms"] for t in kept if t["node"] != "retrieve")
            + sum(t["llm_ms"] for t in kept if t["node"] == "retrieve"), 1),
        "llm_calls": sum(branch["calls_by_stage"].values()),
        "calls_by_stage": branch["calls_by_stage"],
        "llm_errors": branch["llm_errors"],
        "llm_ms": round(sum(t["llm_ms"] for t in kept) + branch["llm_ms"], 1),
        "input_tokens": sum(t["in"] for t in kept) + branch["input_tokens"],
        "output_tokens": sum(t["out"] for t in kept) + branch["output_tokens"],
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
                    elif group == "sensitivity":
                        c_row = rows.get((sid, "C"))
                        if c_row is None:
                            print("[RUN]   S: skipped — needs this sample's C row first")
                            continue
                        s_row = {"sample_id": sid, **meta,
                                 **run_sensitivity(agent, meter, query, c_row["context"])}
                        if s_row["llm_errors"]:
                            raise RuntimeError(f"{s_row['llm_errors']} LLM call(s) failed")
                        _append_row(runs_path, s_row)
                        rows[(sid, "S")] = s_row
                        print(f"[RUN]   S: verdict on C context = {s_row['verdict']}")
                    elif group == "ackfix":
                        a_row = rows.get((sid, "A"))
                        if a_row is None:
                            print("[RUN]   F: skipped — needs this sample's A row first")
                            continue
                        f_row = {"sample_id": sid, **meta,
                                 **run_ack_fix(agent, meter, a_row, query)}
                        if f_row["llm_errors"]:
                            raise RuntimeError(f"{f_row['llm_errors']} LLM call(s) failed")
                        _append_row(runs_path, f_row)
                        rows[(sid, "F")] = f_row
                        print(f"[RUN]   F: {'unchanged (A did not acknowledge)' if f_row['identical_to_A'] else 're-answered from A context'}")
                    elif group == "mergefix":
                        a_row, f_row = rows.get((sid, "A")), rows.get((sid, "F"))
                        if a_row is None or f_row is None:
                            print("[RUN]   M: skipped — needs this sample's A and F rows first")
                            continue
                        m_row = {"sample_id": sid, **meta,
                                 **run_merge_fix(agent, meter, a_row, f_row, query)}
                        if m_row["llm_errors"]:
                            raise RuntimeError(f"{m_row['llm_errors']} LLM call(s) failed")
                        _append_row(runs_path, m_row)
                        rows[(sid, "M")] = m_row
                        print(f"[RUN]   M: {'unchanged (no broaden round)' if m_row['identical_to_F'] else 'answered from merged context'}")
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


def score_answer(
    answer: str, sample: dict, alias_map: dict, context: str | None = None
) -> dict:
    """Technique P/R/F1 of one answer, per-step recall by cue type, grounding.

    Primary prediction set = technique IDs the answer cites, rolled up to the
    parent. Name matching through ``alias_map`` is reported separately only:
    the exported map keeps one ID per lowercased name, and where an enterprise
    and a mobile technique share a name the mobile ID won ("screen capture" ->
    T1513, not T1113; "ingress tool transfer" -> T1544, not T1105), alongside
    revoked IDs ("data encrypted" -> T1022). On the smoke run every name-only
    prediction was one of these, so name matching added spurious IDs to answers
    that had already cited the right enterprise ID.
    """
    gold = {g.upper() for g in sample["gold_attack_ids"]}
    cited_raw = extract_technique_ids(answer)
    predicted = _roll_up(cited_raw)

    main = technique_set_score(predicted, gold)
    raw = technique_set_score(cited_raw, gold)
    with_names = technique_set_score(
        _roll_up(extract_all_techniques(answer, alias_map)), gold
    )

    step_recall: dict[str, list[float]] = {}
    for step in sample.get("attack_steps", []):
        step_gold = {g.upper() for g in step.get("gold_attack_ids", [])}
        if step_gold:
            step_recall.setdefault(step.get("cue_type", "unspecified"), []).append(
                technique_set_score(predicted, step_gold)["recall"]
            )

    out = {
        "precision": main["precision"],
        "recall": main["recall"],
        "f1": main["f1"],
        # micro-average ingredients: matched credit, |predicted|, |gold|
        "matched": main["recall"] * len(gold),
        "n_pred": len(predicted),
        "n_gold": len(gold),
        "f1_raw": raw["f1"],
        "f1_with_names": with_names["f1"],
        "step_recall": step_recall,
    }
    if context is not None:
        in_context = _roll_up(extract_technique_ids(context))
        correct = predicted & gold
        out.update(
            ungrounded_share=(len(predicted - in_context) / len(predicted)) if predicted else None,
            n_correct=len(correct),
            n_correct_ungrounded=len(correct - in_context),
        )
    return out


def context_recall(context: str, sample: dict) -> float:
    """Share of gold techniques whose ID appears in the rendered context.

    Vector-hit and subgraph headers carry the ATT&CK ID; relationship documents
    and subgraph neighbour lists carry names only, so this is a lower bound.
    """
    gold = {g.upper() for g in sample["gold_attack_ids"]}
    found = _roll_up(extract_technique_ids(context or ""))
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


def _mcnemar_p(b: int, c: int) -> float | None:
    """Exact two-sided McNemar p on the discordant counts (scipy if available)."""
    if b + c == 0:
        return None
    try:
        from scipy.stats import binomtest
        return float(binomtest(b, b + c, 0.5).pvalue)
    except ImportError:
        return None


def _evaluator_section(
    lines: list[str], common: list[str], rows: dict, by_id: dict,
    technique_to_tactics: dict[str, list[str]] | None = None,
) -> None:
    """Can the evaluator tell a weak context from a strong one?"""
    a_judged = []  # (sample_id, verdict, context) for A's first pass
    for sid in common:
        first = next(t for t in rows[(sid, "A")]["trace"] if t["node"] == "evaluate_context")
        a_judged.append((sid, first["verdict"], rows[(sid, "A")]["first_context"]))
    s_judged = [(sid, rows[(sid, "S")]["verdict"], rows[(sid, "C")]["context"])
                for sid in common if (sid, "S") in rows]

    def visible(ctx: str) -> str:
        return ctx[:EVALUATOR_CONTEXT_CHARS]

    lines += ["", "## 3b. Evaluator sensitivity and calibration", "",
              f"The evaluator reads only the first {EVALUATOR_CONTEXT_CHARS} characters of "
              "the context. \"Visible recall\" = share of gold technique IDs inside that "
              "window; \"full recall\" = in the whole context the reasoning LLM gets. Both "
              "count IDs only, so a technique present by name alone counts as missing.", "",
              "| Context judged | n | INSUFFICIENT | visible recall | full recall | mean context chars |",
              "|---|---|---|---|---|---|"]
    for label, judged in (("A first pass (served)", a_judged), ("C fast-path context (probe S)", s_judged)):
        if not judged:
            lines.append(f"| {label} | 0 | — | — | — | — |")
            continue
        insuff = sum(1 for _, v, _ in judged if v == "INSUFFICIENT")
        lines.append(
            f"| {label} | {len(judged)} | {insuff} ({insuff / len(judged):.1%}) | "
            f"{_mean([context_recall(visible(c), by_id[sid]) for sid, _, c in judged]):.3f} | "
            f"{_mean([context_recall(c, by_id[sid]) for sid, _, c in judged]):.3f} | "
            f"{_mean([len(c) for _, _, c in judged]):.0f} |"
        )

    if s_judged:
        a_verdict = {sid: v for sid, v, _ in a_judged}
        pairs = [(a_verdict[sid], v) for sid, v, _ in s_judged]
        ss = sum(1 for a, c in pairs if a == "SUFFICIENT" and c == "SUFFICIENT")
        si = sum(1 for a, c in pairs if a == "SUFFICIENT" and c == "INSUFFICIENT")
        is_ = sum(1 for a, c in pairs if a == "INSUFFICIENT" and c == "SUFFICIENT")
        ii = sum(1 for a, c in pairs if a == "INSUFFICIENT" and c == "INSUFFICIENT")
        p = _mcnemar_p(si, is_)
        lines += ["", "Same incident, two contexts (rows: verdict on A's first pass; columns: "
                  "verdict on C's context). A sensitive evaluator puts mass in the "
                  "SUFFICIENT → INSUFFICIENT cell.", "",
                  "| A \\ C | SUFFICIENT | INSUFFICIENT |", "|---|---|---|",
                  f"| SUFFICIENT | {ss} | {si} |",
                  f"| INSUFFICIENT | {is_} | {ii} |", "",
                  f"Exact McNemar p (discordant {si} vs {is_}): "
                  + (f"{p:.4f}" if p is not None else "n/a")]

    pooled = [(v, context_recall(visible(c), by_id[sid])) for sid, v, c in a_judged + s_judged]
    buckets = (("visible recall < 0.5", lambda r: r < 0.5),
               ("0.5 ≤ visible recall < 1", lambda r: 0.5 <= r < 1.0),
               ("visible recall = 1", lambda r: r >= 1.0))
    lines += ["", f"Calibration, pooled over all {len(pooled)} judgements. A SUFFICIENT "
              "verdict in the first row is a likely miss: most of the incident's gold "
              "techniques are not in what the evaluator read.", "",
              "| Visible gold recall | n | SUFFICIENT | INSUFFICIENT |", "|---|---|---|---|"]
    for label, test in buckets:
        in_bucket = [v for v, r in pooled if test(r)]
        suff = sum(1 for v in in_bucket if v == "SUFFICIENT")
        lines.append(f"| {label} | {len(in_bucket)} | {suff} | {len(in_bucket) - suff} |")

    if not technique_to_tactics:
        return
    # The evaluator prompt scores coverage against four fixed phases. An
    # incident whose techniques sit in other tactics (discovery, collection,
    # defense evasion, ...) reads as "phases missing" however good the context.
    s_verdict = {sid: v for sid, v, _ in s_judged}
    by_overlap: dict[int, list[tuple[str, str, str]]] = {}
    for sid, verdict, ctx in a_judged:
        tactics = {t for g in by_id[sid]["gold_attack_ids"]
                   for t in technique_to_tactics.get(g.upper(), [])}
        by_overlap.setdefault(len(tactics & EVALUATOR_CHECKLIST_TACTICS), []).append((sid, verdict, ctx))
    lines += ["", "Evaluator checklist vs the incident's own tactics. The prompt checks four "
              "fixed phases (Initial Access, Credential Access, Privilege Escalation, Impact); "
              "the column counts how many of them occur among the sample's gold tactics. "
              "If verdicts track this count rather than visible recall, the loop is "
              "triggered by the rubric, not by what the context is missing.", "",
              "| Checklist phases in gold | n | A first pass INSUFFICIENT | visible recall (A) "
              "| probe S INSUFFICIENT |", "|---|---|---|---|---|"]
    for k in sorted(by_overlap):
        group = by_overlap[k]
        insuff = sum(1 for _, v, _ in group if v == "INSUFFICIENT")
        s_group = [s_verdict[sid] for sid, _, _ in group if sid in s_verdict]
        s_insuff = sum(1 for v in s_group if v == "INSUFFICIENT")
        lines.append(
            f"| {k} | {len(group)} | {insuff} ({insuff / len(group):.0%}) | "
            f"{_mean([context_recall(visible(c), by_id[sid]) for sid, _, c in group]):.3f} | "
            + (f"{s_insuff}/{len(s_group)} ({s_insuff / len(s_group):.0%})" if s_group else "—")
            + " |"
        )


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
        lookup = json.load(f)
    alias_map = lookup["alias_map"]

    arms = [a for a in SCORED_ARMS if any(k[1] == a for k in rows)]
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
    # The context each arm's reasoning LLM actually saw.
    ctx_of = {
        "A": lambda sid: rows[(sid, "A")]["final_context"] or rows[(sid, "A")]["first_context"],
        "B": lambda sid: rows[(sid, "A")]["first_context"],
        "C": lambda sid: rows[(sid, "C")]["context"],
        "F": lambda sid: rows[(sid, "A")]["final_context"] or rows[(sid, "A")]["first_context"],
        "M": lambda sid: rows[(sid, "M")].get("context")
        or rows[(sid, "A")]["final_context"] or rows[(sid, "A")]["first_context"],
    }
    scores = {a: {sid: score_answer(rows[(sid, a)]["answer"], by_id[sid], alias_map,
                                    context=ctx_of[a](sid))
                  for sid in common} for a in arms}
    n_steps = {ct: sum(1 for sid in common for st in by_id[sid]["attack_steps"]
                       if st.get("cue_type") == ct) for ct in ("named", "described")}
    first = rows[(common[0], arms[0])]

    lines = [
        "# Agentic Ablation — ATT&CK Technique P / R / F1",
        "",
        f"- Dataset: real-CTI tier (`{DEFAULT_DATASET.name}`), {len(common)} samples "
        f"({n_steps['named']} named / {n_steps['described']} described steps)",
        f"- Core LLM: `{first.get('model', '?')}`; commit(s) "
        + ", ".join(f"`{c}`" for c in sorted({r.get("commit", "?") for r in rows.values()})),
        f"- Run file: `{runs_path.name}`",
        "- Arms: **A** full agent (headline) · **B** A without the evaluator/broaden "
        "loop (derived from A's first pass) · **C** `query_fast()`",
        "",
        "Scoring: technique IDs cited in the answer (`extract_technique_ids`), rolled "
        "up to the parent technique because all gold IDs are parent-level, then "
        "`technique_set_score` against the sample's `gold_attack_ids`. Macro = mean "
        "over samples; micro = pooled matches. Name matching is reported as a "
        "secondary row only — see §6.",
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
    row("Macro F1, + name matching (defective alias map, §6)",
        lambda a: f"{_mean([s['f1_with_names'] for s in scores[a].values()]):.3f}")
    row("Mean techniques cited", lambda a: f"{_mean([s['n_pred'] for s in scores[a].values()]):.2f}")
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
    comparisons = [(l, r) for l, r in (("A", "B"), ("B", "C"), ("A", "C"),
                                       ("F", "A"), ("F", "B"), ("M", "F"), ("M", "B"))
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
        partial = [t for t in judged if t["verdict"] == "SUFFICIENT"
                   and t["strategy"] == "PARTIAL_ANSWER"]
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
                  f"| … SUFFICIENT with strategy PARTIAL_ANSWER (gap warning never reaches the answer) | {len(partial)} |",
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
            if "M" in arms and fired:
                lines += ["", "With the broaden merge (arm M: the broadened samples "
                          "re-answered from the merged context):", "",
                          "| Subset | mean Δ F1 | 95% CI | Wilcoxon p | n | W/T/L |",
                          "|---|---|---|---|---|---|",
                          _fmt_paired("M − F, broadened samples",
                                      paired({s: scores["M"][s]["f1"] for s in fired},
                                             {s: scores["F"][s]["f1"] for s in fired}, fired))]
            if "F" in arms and acked:
                lines += ["", "With the ACK fix (arm F: the same samples re-answered from "
                          "A's own context, acknowledgement kept as a caveat):", "",
                          "| Subset | mean Δ F1 | 95% CI | Wilcoxon p | n | W/T/L |",
                          "|---|---|---|---|---|---|",
                          _fmt_paired("F − A, acknowledged samples",
                                      paired({s: scores["F"][s]["f1"] for s in acked},
                                             {s: scores["A"][s]["f1"] for s in acked}, acked)),
                          _fmt_paired("F − B, acknowledged samples",
                                      paired({s: scores["F"][s]["f1"] for s in acked},
                                             {s: scores["B"][s]["f1"] for s in acked}, acked))]

            if fired:
                ctx_first = {s: context_recall(a_rows[s]["first_context"], by_id[s]) for s in fired}
                ctx_final = {s: context_recall(a_rows[s]["final_context"] or a_rows[s]["first_context"],
                                               by_id[s]) for s in fired}
                st = paired(ctx_final, ctx_first, fired)
                lines += ["", "Did broadening put more gold techniques into the context? "
                          "(share of gold technique IDs appearing in the rendered context)", "",
                          "| Subset | first-pass ctx recall | final ctx recall | mean Δ | 95% CI | n |",
                          "|---|---|---|---|---|---|",
                          f"| broadening fired | {_mean(list(ctx_first.values())):.3f} | "
                          f"{_mean(list(ctx_final.values())):.3f} | {st['mean']:+.3f} | "
                          f"[{st['ci'][0]:+.3f}, {st['ci'][1]:+.3f}] | {st['n']} |"]

    # ── Evaluator sensitivity + calibration ───────────────────────────────
    if "A" in arms:
        _evaluator_section(lines, common, rows, by_id, lookup["technique_to_tactics"])

    # ── Grounding: what the context held vs what the answer cited ─────────
    lines += ["", "## 4. Grounding — context vs answer", "",
              "Context recall: share of gold technique IDs that appear in the context the "
              "reasoning LLM saw. Only vector-hit and subgraph headers carry IDs "
              "(relationship documents and neighbour lists carry names), so both context "
              "recall and \"absent from context\" are conservative: a technique present "
              "only by name counts as absent. Answer recall above context recall means the "
              "model cited techniques from its own parametric knowledge.", "",
              "| | " + " | ".join(arms) + " |", "|---|" + "---|" * len(arms)]
    row("Context recall", lambda a: f"{_mean([context_recall(ctx_of[a](s), by_id[s]) for s in common]):.3f}")
    row("Answer recall (macro)", lambda a: f"{_mean([s['recall'] for s in scores[a].values()]):.3f}")
    row("Cited IDs absent from context (mean share per answer)",
        lambda a: f"{_mean([s['ungrounded_share'] for s in scores[a].values() if s['ungrounded_share'] is not None]):.3f}")

    def _correct_ungrounded(a: str) -> str:
        hits = sum(s["n_correct"] for s in scores[a].values())
        off = sum(s["n_correct_ungrounded"] for s in scores[a].values())
        return f"{off}/{hits} ({off / hits:.1%})" if hits else "—"

    row("Correct (gold) citations absent from context", _correct_ungrounded)

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
              "- **Extraction.** Predictions are the technique IDs an answer cites. A "
              "technique described only in prose without its ID is not counted, and an ID "
              "mentioned in a negative sense counts as predicted. Name matching was the "
              "intended complement but is not used for the headline: `attack_lookup.json`'s "
              "alias map keeps one ID per name and resolves names shared by enterprise and "
              "mobile techniques to the mobile ID (e.g. \"screen capture\" → T1513, "
              "\"system information discovery\" → T1426), plus some revoked IDs "
              "(\"data encrypted\" → T1022). Found on the 5-sample smoke run, before the "
              "full run; the name-matched F1 is still reported for transparency.",
              "- **Evaluator probe.** S reuses C's context, so its verdicts share C's "
              "retrieval; calibration buckets use ID-visible recall, which undercounts "
              "techniques the context names without an ID and so overstates likely misses.",
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
    parser.add_argument("--arms", default="agent,fast,sensitivity",
                        help="agent (A + derived B), fast (C), sensitivity (S, needs C), "
                             "ackfix (F, needs A), mergefix (M, needs A and F); "
                             "default agent,fast,sensitivity")
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
