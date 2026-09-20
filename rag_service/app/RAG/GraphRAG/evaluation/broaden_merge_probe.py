"""
Broaden Merge Probe
====================
Does a broaden round add to the context, or just reshuffle it?

In the ablation the second retrieval replaced the first: same 15-vector /
8-subgraph caps, same 10000-character budget, which the first pass already
fills (mean 9258). Over the 25 broadened samples that lost gold techniques on
6 and gained on 6 — a wash bought with two extra LLM calls.

This probe re-runs ONLY retrieval for those samples, reusing the sub-queries
and the rewrite the agent produced at the time (both recorded in
results/agentic_ablation.jsonl), and compares the context the broaden round
would render under:

  replace   what the pipeline did: second retrieval, first-pass budget
  merge     what it does now: union with the first pass, budget raised by one
            BROADEN_* step per round

No LLM calls — retrieval only, so this costs nothing but time.

Usage (from rag_service/app; PYTHONUTF8=1 on Windows):
    python -m RAG.GraphRAG.evaluation.broaden_merge_probe
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
REPORT_PATH = RESULTS_DIR / "broaden_merge_probe.md"


def _broadened_rows() -> list[dict]:
    rows = []
    with open(ABLATION_PATH, "r", encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            if row["arm"] == "A" and row["broaden_rounds"] > 0:
                rows.append(row)
    return rows


def _queries(row: dict) -> tuple[list[str], list[str]]:
    """The two query sets the agent actually used, first pass then broaden."""
    retrieves = [t for t in row["trace"] if t["node"] == "retrieve"]
    original = row.get("query") or ""
    out = []
    for entry in retrieves[:2]:
        queries: list[str] = []
        for q in [original, *entry["sub_queries"], *entry["rewrites"]]:
            if q and q.strip() and q not in queries:
                queries.append(q)
        out.append(queries)
    return out[0], out[1]


def _trim(result, max_vector: int, max_graph: int):
    """The same result as retrieving with the smaller caps: the merge inside
    retrieve_multi_quota orders first and truncates last."""
    from ..retrieval.hybrid_retriever import GraphRAGResult

    return GraphRAGResult(
        vector_results=result.vector_results[:max_vector],
        graph_results=result.graph_results[:max_graph],
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Broaden merge probe (retrieval only)")
    parser.add_argument("--max-samples", type=int, default=0)
    args = parser.parse_args()

    from ..config import (
        AGENT_MAX_CONTEXT_CHARS,
        AGENT_MAX_GRAPH,
        AGENT_MAX_VECTOR,
        BROADEN_CONTEXT_CHARS_STEP,
        BROADEN_GRAPH_STEP,
        BROADEN_VECTOR_STEP,
        VECTOR_TOP_K,
    )
    from ..pipeline.context_builder import build_context
    from ..retrieval.hybrid_retriever import HybridRetriever, merge_results

    samples = {s["id"]: s for s in load_samples(DEFAULT_DATASET)}
    rows = _broadened_rows()
    for row in rows:
        row["query"] = samples[row["sample_id"]]["query"]
    if args.max_samples:
        rows = rows[: args.max_samples]
    print(f"[PROBE] {len(rows)} broadened samples, retrieval only (no LLM calls)")

    wide_vector = AGENT_MAX_VECTOR + BROADEN_VECTOR_STEP
    wide_graph = AGENT_MAX_GRAPH + BROADEN_GRAPH_STEP
    wide_chars = AGENT_MAX_CONTEXT_CHARS + BROADEN_CONTEXT_CHARS_STEP

    retriever = HybridRetriever()
    per_sample = []
    try:
        for i, row in enumerate(rows, 1):
            sid = row["sample_id"]
            sample = samples[sid]
            first_queries, broaden_queries = _queries(row)
            t0 = time.perf_counter()

            first = retriever.retrieve_multi_quota(
                first_queries, per_query_k=3, top_k=VECTOR_TOP_K,
                max_vector=AGENT_MAX_VECTOR, max_graph=AGENT_MAX_GRAPH,
            )
            wide = retriever.retrieve_multi_quota(
                broaden_queries, per_query_k=3, top_k=VECTOR_TOP_K,
                max_vector=wide_vector, max_graph=wide_graph,
            )

            ctx_first = build_context(
                first, max_context_length=AGENT_MAX_CONTEXT_CHARS,
                max_vector=AGENT_MAX_VECTOR, max_graph=AGENT_MAX_GRAPH,
            )
            ctx_replace = build_context(
                _trim(wide, AGENT_MAX_VECTOR, AGENT_MAX_GRAPH),
                max_context_length=AGENT_MAX_CONTEXT_CHARS,
                max_vector=AGENT_MAX_VECTOR, max_graph=AGENT_MAX_GRAPH,
            )
            ctx_merge = build_context(
                merge_results(first, wide), max_context_length=wide_chars,
                max_vector=wide_vector, max_graph=wide_graph,
            )

            entry = {
                "sample_id": sid,
                "stored_first": context_recall(row["first_context"], sample),
                "stored_final": context_recall(row["final_context"] or "", sample),
                "first": context_recall(ctx_first, sample),
                "replace": context_recall(ctx_replace, sample),
                "merge": context_recall(ctx_merge, sample),
                "chars_replace": len(ctx_replace),
                "chars_merge": len(ctx_merge),
                "seconds": round(time.perf_counter() - t0, 1),
            }
            per_sample.append(entry)
            print(f"[PROBE] [{i}/{len(rows)}] {sid} first {entry['first']:.2f} "
                  f"-> replace {entry['replace']:.2f} / merge {entry['merge']:.2f} "
                  f"({entry['seconds']}s)")
    finally:
        retriever.close()

    def mean(key: str) -> float:
        return sum(e[key] for e in per_sample) / len(per_sample) if per_sample else 0.0

    better = sum(1 for e in per_sample if e["merge"] > e["replace"])
    same = sum(1 for e in per_sample if e["merge"] == e["replace"])
    worse = sum(1 for e in per_sample if e["merge"] < e["replace"])
    lost_replace = sum(1 for e in per_sample if e["replace"] < e["first"])
    lost_merge = sum(1 for e in per_sample if e["merge"] < e["first"])

    lines = [
        "# Broaden Merge Probe — does the broaden round add context or reshuffle it?",
        "",
        f"- {len(per_sample)} samples: every incident where the served agent broadened "
        f"(`{ABLATION_PATH.name}`).",
        "- Retrieval only, reusing the sub-queries and rewrite the agent produced at the "
        "time. No LLM calls.",
        "- `replace`: second retrieval under the first pass's budget — what the pipeline "
        "did. `merge`: union with the first pass, budget raised one BROADEN_* step.",
        "- Recall = share of the sample's gold ATT&CK IDs appearing in the rendered "
        "context (IDs only, so conservative but identical across columns).",
        "",
        "| Context | mean gold recall | mean chars |",
        "|---|---|---|",
        f"| first pass | {mean('first'):.3f} | — |",
        f"| after broaden, replace | {mean('replace'):.3f} | {mean('chars_replace'):.0f} |",
        f"| after broaden, merge | {mean('merge'):.3f} | {mean('chars_merge'):.0f} |",
        "",
        f"- merge vs replace: better on {better}, equal on {same}, worse on {worse}",
        f"- lost ground against the first pass: replace {lost_replace}, merge {lost_merge}",
        "",
        "Stored columns re-check the probe against the run it replays "
        f"(stored first pass {mean('stored_first'):.3f}, stored final "
        f"{mean('stored_final'):.3f}); retrieval is deterministic, so a gap here would "
        "mean the replay is not faithful.",
        "",
        "| sample | first | replace | merge |",
        "|---|---|---|---|",
    ]
    for e in per_sample:
        lines.append(f"| {e['sample_id']} | {e['first']:.2f} | {e['replace']:.2f} | "
                     f"{e['merge']:.2f} |")

    report = "\n".join(lines) + "\n"
    REPORT_PATH.write_text(report, encoding="utf-8")
    print("\n" + report)
    print(f"[PROBE] Report saved to {REPORT_PATH}")


if __name__ == "__main__":
    main()
