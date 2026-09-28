"""
HyDE Through the Served Agent
=============================
Does HyDE retrieval ("hyde_fuse_sub", see hyde_benchmark.py) improve the answer
the served agent gives, and does it keep that answer grounded?

hyde_benchmark.py measured retrieval alone. This streams the served LangGraph
agent end to end — route, decompose, retrieve, evaluate, broaden, reasoning —
and scores the answer against analyst-assigned gold on the real-CTI tier.

Arms (both GraphRAGAgent.query() as served, streamed via graph.stream):

  P  production    hyde_writer = None — what is deployed today
  H  + HyDE        hyde_writer set; P's decompositions are replayed

Why replay: the decomposer is not deterministic even at temperature 0, so a
fresh decomposition in H would change the sub-queries as well as the search
texts. H re-uses P's sub-queries, retrieval by retrieval, so the first
retrieval differs only by HyDE. What follows it — the evaluator's verdict, a
broaden round, the reasoning call — runs live in both arms, because those are
the effects to measure. If H broadens more often than P, the extra
decompositions run live.

Primary metric: technique F1 of cited IDs (agentic_ablation.score_answer).
Grounding: share of cited IDs absent from the context the answer was written
from. Context recall: gold IDs visible in that context.

Usage (from rag_service/app, PYTHONUTF8=1 on Windows):
    python -m RAG.GraphRAG.evaluation.hyde_agent_ablation --phase run --max-samples 2 --run-tag smoke
    python -m RAG.GraphRAG.evaluation.hyde_agent_ablation --phase all
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from .agentic_ablation import (
    DEFAULT_PRICE_IN,
    DEFAULT_PRICE_OUT,
    RESULTS_DIR,
    _append_row,
    _fmt_paired,
    _git_commit,
    _LlmMeter,
    _load_rows,
    _MeteredLlm,
    context_recall,
    paired,
    run_full_agent,
    score_answer,
)
from .crosslingual_generation_benchmark import DEFAULT_DATASET, LOOKUP_PATH, load_samples

ARMS = ("P", "H")
ARM_LABELS = {"P": "P  production", "H": "H  + HyDE (fuse_sub)"}


def _paths(run_tag: str) -> tuple[Path, Path]:
    stem = "hyde_agent_ablation" + (f"_{run_tag}" if run_tag else "")
    return RESULTS_DIR / f"{stem}.jsonl", RESULTS_DIR / f"{stem}.md"


# ══════════════════════════════════════════════════════════════════════════════
# PHASE RUN
# ══════════════════════════════════════════════════════════════════════════════


class _Replay:
    """Wrap the decomposer: log every decomposition, and when a replay queue is
    loaded, return its entries in order instead of calling the LLM."""

    def __init__(self, agent) -> None:
        self.log: list[list[str]] = []
        self.queue: list[list[str]] = []
        self.replayed = 0
        real = agent.decomposer.decompose

        def decompose(*args, **kwargs):
            if self.queue:
                subs = list(self.queue.pop(0))
                self.replayed += 1
            else:
                subs = real(*args, **kwargs)
            self.log.append(list(subs))
            return subs

        agent.decomposer.decompose = decompose


def _record_hyde(writer) -> list[list[dict | None]]:
    """Log what the writer produced for each retrieval; the node keeps it local."""
    log: list[list[dict | None]] = []
    real = writer.write

    def write(*args, **kwargs):
        passages = real(*args, **kwargs)
        log.append([{"name": p.name, "description": p.description} if p else None
                    for p in passages])
        return passages

    writer.write = write
    return log


def phase_run(samples: list[dict], runs_path: Path, max_failures: int) -> None:
    rows = _load_rows(runs_path)
    todo = [s for s in samples if any((s["id"], a) not in rows for a in ARMS)]
    print(f"[RUN] {len(samples)} samples, {len(todo)} with rows missing ({runs_path.name})")
    if not todo:
        return

    from ..config import LLM_MODEL
    from ..llm_provider import resolve_core_llm_target
    from ..pipeline.agent_graph import GraphRAGAgent
    from ..pipeline.hyde import HydeWriter

    target = resolve_core_llm_target(LLM_MODEL)
    meta = {"model": f"{target.provider}:{target.model}", "commit": _git_commit()}
    print(f"[RUN] Core LLM: {meta['model']}  commit: {meta['commit']}")

    agent = GraphRAGAgent()
    meter = _LlmMeter()
    meter.attach(agent)
    replay = _Replay(agent)

    writer = HydeWriter()
    if writer.llm is None:
        raise SystemExit("[RUN] no LLM for the HyDE writer")
    writer.llm = _MeteredLlm(writer.llm, meter, "hyde")
    hyde_log = _record_hyde(writer)

    failures = 0
    try:
        for i, sample in enumerate(todo, 1):
            sid, query = sample["id"], sample["query"]
            try:
                p_row = rows.get((sid, "P"))
                if p_row is None:
                    agent.hyde_writer = None
                    p_row = {"sample_id": sid, **meta,
                             **run_full_agent(agent, meter, replay.log, query), "arm": "P"}
                    if p_row["llm_errors"]:
                        raise RuntimeError(f"P: {p_row['llm_errors']} LLM call(s) failed")
                    _append_row(runs_path, p_row)
                    rows[(sid, "P")] = p_row

                if (sid, "H") not in rows:
                    agent.hyde_writer = writer
                    replay.queue = [t["sub_queries"] for t in p_row["trace"]
                                    if t["node"] == "retrieve"]
                    replay.replayed = 0
                    mark_h = len(hyde_log)
                    try:
                        h_run = run_full_agent(agent, meter, replay.log, query)
                    finally:
                        agent.hyde_writer = None
                        replay.queue = []
                    h_row = {"sample_id": sid, **meta, **h_run, "arm": "H",
                             "replayed_decompositions": replay.replayed,
                             "hyde_entries": hyde_log[mark_h:]}
                    if h_row["llm_errors"]:
                        raise RuntimeError(f"H: {h_row['llm_errors']} LLM call(s) failed")
                    _append_row(runs_path, h_row)
                    rows[(sid, "H")] = h_row

                h_row = rows[(sid, "H")]
                print(f"[RUN] [{i}/{len(todo)}] {sid}  "
                      f"P {p_row['latency_ms'] / 1000:.0f}s broaden={p_row['broaden_rounds']}  "
                      f"H {h_row['latency_ms'] / 1000:.0f}s broaden={h_row['broaden_rounds']}",
                      flush=True)
                failures = 0
            except Exception as e:  # noqa: BLE001 — keep going, resume later
                failures += 1
                print(f"[RUN] {sid} FAILED ({type(e).__name__}: {e}) — not saved "
                      f"[{failures}/{max_failures} consecutive]", flush=True)
                if failures >= max_failures:
                    print("[RUN] Too many consecutive failures — stopping. Rerun to resume.")
                    return
    finally:
        agent.close()


# ══════════════════════════════════════════════════════════════════════════════
# PHASE SCORE — deterministic, free
# ══════════════════════════════════════════════════════════════════════════════


def _context(row: dict) -> str:
    """The context the answer was written from: the last retrieval's."""
    return row.get("final_context") or row.get("first_context") or ""


def _mean(xs: list) -> float:
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else 0.0


def phase_score(samples: list[dict], runs_path: Path, report_path: Path,
                price_in: float, price_out: float) -> None:
    with open(LOOKUP_PATH, encoding="utf-8") as f:
        alias_map = json.load(f)["alias_map"]
    rows = _load_rows(runs_path)
    by_id = {s["id"]: s for s in samples}
    common = sorted(sid for sid in by_id if all((sid, a) in rows for a in ARMS))
    if not common:
        print("[SCORE] no paired rows yet")
        return

    per: dict[str, dict[str, dict]] = {a: {} for a in ARMS}
    for a in ARMS:
        for sid in common:
            row = rows[(sid, a)]
            ctx = _context(row)
            sc = score_answer(row["answer"], by_id[sid], alias_map, context=ctx)
            sc["described"] = (_mean(sc["step_recall"]["described"])
                               if sc["step_recall"].get("described") else None)
            sc["named"] = (_mean(sc["step_recall"]["named"])
                           if sc["step_recall"].get("named") else None)
            sc["context_recall"] = context_recall(ctx, by_id[sid])
            sc["cost"] = row["input_tokens"] / 1e6 * price_in + row["output_tokens"] / 1e6 * price_out
            per[a][sid] = sc

    def metric(a: str, key: str) -> dict[str, float]:
        return {sid: per[a][sid][key] for sid in common if per[a][sid].get(key) is not None}

    L: list[str] = ["# HyDE through the served agent — real-CTI tier\n"]
    commits = sorted({rows[(sid, a)]["commit"] for sid in common for a in ARMS})
    model = rows[(common[0], "P")]["model"]
    L.append(f"Samples: {len(common)} paired. Model: `{model}`. Commit(s): {', '.join(commits)}.")
    replayed = sum(rows[(sid, "H")].get("replayed_decompositions", 0) for sid in common)
    retrieves_p = sum(rows[(sid, "P")]["n_retrieves"] for sid in common)
    L.append(f"H replayed {replayed} of P's {retrieves_p} decompositions; "
             f"the rest ran live (H retrieved more often than P).\n")

    L.append("## Per-arm means\n")
    cols = [("F1", "f1"), ("Precision", "precision"), ("Recall", "recall"),
            ("Step recall, described", "described"), ("Step recall, named", "named"),
            ("Context gold recall", "context_recall"),
            ("Cited IDs not in context", "ungrounded_share")]
    L.append("| Metric | " + " | ".join(ARM_LABELS[a] for a in ARMS) + " |")
    L.append("|---|" + "---|" * len(ARMS))
    for label, key in cols:
        L.append(f"| {label} | " + " | ".join(
            f"{_mean(list(metric(a, key).values())):.3f}" for a in ARMS) + " |")
    for label, fn in (
        ("Correct IDs not in context (total)",
         lambda a: sum(per[a][s]["n_correct_ungrounded"] for s in common)),
        ("Broaden rounds (total)", lambda a: sum(rows[(s, a)]["broaden_rounds"] for s in common)),
        ("ACKNOWLEDGE_LIMIT answers", lambda a: sum(bool(rows[(s, a)]["ack_limit"]) for s in common)),
        ("LLM calls / sample", lambda a: _mean([rows[(s, a)]["llm_calls"] for s in common])),
        ("Latency s / sample", lambda a: _mean([rows[(s, a)]["latency_ms"] / 1000 for s in common])),
        ("Cost USD (total)", lambda a: sum(per[a][s]["cost"] for s in common)),
    ):
        vals = [fn(a) for a in ARMS]
        L.append(f"| {label} | " + " | ".join(
            f"{v:.3f}" if isinstance(v, float) else str(v) for v in vals) + " |")

    L.append("\n## Paired: H − P\n")
    L.append("Per-sample Δ; 95% CI paired bootstrap; p two-sided Wilcoxon; * = CI excludes 0.\n")
    L.append("| Metric | Δ mean | 95% CI | p | n | W/T/L |")
    L.append("|---|---|---|---|---|---|")
    for label, key in cols:
        left, right = metric("H", key), metric("P", key)
        ids = sorted(set(left) & set(right))
        L.append(_fmt_paired(label, paired(left, right, ids)))

    first_same = sum(
        rows[(s, "H")]["first_verdict"] == rows[(s, "P")]["first_verdict"] for s in common)
    L.append(f"\nFirst evaluator verdict identical in {first_same}/{len(common)} samples.")

    report_path.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    print(f"\n[SCORE] written to {report_path}")


def main() -> None:
    ap = argparse.ArgumentParser(description="HyDE through the served agent (P vs H)")
    ap.add_argument("--phase", choices=("run", "score", "all"), required=True)
    ap.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    ap.add_argument("--max-samples", type=int, default=0)
    ap.add_argument("--run-tag", default="")
    ap.add_argument("--max-consecutive-failures", type=int, default=3)
    ap.add_argument("--price-in", type=float, default=DEFAULT_PRICE_IN)
    ap.add_argument("--price-out", type=float, default=DEFAULT_PRICE_OUT)
    args = ap.parse_args()

    samples = load_samples(args.dataset, args.max_samples)
    runs_path, report_path = _paths(args.run_tag)
    if args.phase in ("run", "all"):
        phase_run(samples, runs_path, args.max_consecutive_failures)
    if args.phase in ("score", "all"):
        phase_score(samples, runs_path, report_path, args.price_in, args.price_out)


if __name__ == "__main__":
    main()
