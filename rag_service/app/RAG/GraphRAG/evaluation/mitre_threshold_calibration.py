"""
MITRE Table Threshold Calibration
=================================
Which rule should decide whether an UNCITED vector hit becomes a
``retrieved_only`` row of the MITRE table — and what did removing the double
sigmoid do to it?

Why this exists
---------------
``MITRE_TABLE_SCORE_THRESHOLD`` (0.05) compares one absolute number across
rows, but every row was reranked against a different sub-query, and the scale
of a cross-encoder score varies wildly by query: on a traced case SSH scored
0.05 while ranking #2 of 697 for its own sub-query, and Pass the Hash scored
0.79 at #1. The value itself was never measured on today's scale: 0.62 was
calibrated on 2026-07-03 while the reranker applied sigmoid twice, the type
weights were added on 2026-07-17 on that same compressed scale, and on
2026-08-15 the double sigmoid was removed and 0.62 was translated to 0.05 by
hand ("re-run the sweep to settle the value").

The double sigmoid changed two things, so both are measured here:

- **Retrieval order.** ``sigmoid(p)`` squeezes every score into [0.5, 0.731],
  so after ``_TYPE_WEIGHTS`` any Technique (>= 0.6) outranks any Software
  (<= 0.585) — the weights acted as a hard tier. On the [0, 1] scale they are
  a nudge, which changes which hits win the per-sub-query quota.
- **The filter.** One threshold on the compressed scale is a different cut
  per node type; at 0.62 no uncited Software or Group could ever be kept.

Design
------
The cached ``gen_bench`` contexts cannot be reused as they are: their scores
are on the old scale (0.500 - 0.873). ``rerank`` therefore re-runs the
production query shape — the whole incident plus the cached decomposer
sub-queries — through ``search_all`` and the current reranker, and caches
each sub-query's ranked hits with the single-sigmoid score ``p``. That costs
Qdrant reads and local model time, and no LLM call.

``score`` is then offline. For each mode (``single``: p, as served today;
``double``: sigmoid(p), the pre-2026-08-15 behaviour) it applies the real
``HybridRetriever._reweight_by_type`` and merges through the real
``retrieve_multi_quota``, then builds the table with the real
``build_mitre_table`` against the cached answers — so no production logic is
re-implemented. Rules compared for uncited rows:

- ``absolute`` — the weighted score, as production does;
- ``relative`` — the weighted score over the top score of the same sub-query;
- ``rank``     — the hit's rank within its sub-query after reweighting.

Caveats, stated in the report too: 45 LLM-drafted incidents (not real CTI);
answers were generated in July from contexts retrieved under the double
sigmoid, which favours ``double`` wherever the two modes' tables are compared;
graph centres are rebuilt from the seeds but neighbours are not fetched, so a
cited neighbour row is missing in both modes. An ablation, not a headline
benchmark.

Usage (from rag_service/app):
    python -m RAG.GraphRAG.evaluation.mitre_threshold_calibration --phase rerank
    python -m RAG.GraphRAG.evaluation.mitre_threshold_calibration --phase score [--variant C]
"""

from __future__ import annotations

import argparse
import contextlib
import dataclasses
import io
import json
import math
from collections import Counter
from pathlib import Path

from ..config import VECTOR_TOP_K
from ..pipeline.mitre_table import build_mitre_table
from ..retrieval.graph_retriever import GraphNode, SubgraphResult
from ..retrieval.hybrid_retriever import GraphRAGResult, HybridRetriever
from ..retrieval.vector_retriever import VectorResult
from .attack_id_metrics import technique_set_score
from .crosslingual_generation_benchmark import (
    BENCH_DIR,
    CONTEXTS_PATH,
    GENERATIONS_PATH,
    RESULTS_DIR,
    _technique_ids_from_rows,
)

DATASET_PATH = BENCH_DIR.parent / "incident_draft.json"
CACHE_PATH = BENCH_DIR.parent / "threshold_calib" / "rerank.json"
REPORT_STEM = "mitre_threshold_calibration"  # one report per answer variant

PER_QUERY_K = 3  # retrieve_multi_quota's quota, as the agent calls it

# The value each mode shipped with when this was measured; single moved to 0.5 after.
SHIPPED = {"single": 0.05, "double": 0.62}

GRIDS = {
    ("absolute", "single"): [0.0, 0.01, 0.02, 0.03, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30, 0.50],
    ("absolute", "double"): [0.50, 0.55, 0.58, 0.60, 0.62, 0.65, 0.70, 0.75, 0.80],
    ("relative", "single"): [0.05, 0.10, 0.20, 0.30, 0.50, 0.70, 0.90],
    ("relative", "double"): [0.70, 0.75, 0.80, 0.85, 0.90, 0.95],
    ("rank", "single"): [1, 2],
    ("rank", "double"): [1, 2],
}

_TECHNIQUE_LABELS = {"Technique", "Subtechnique"}


def _all_queries(ctx: dict) -> list[str]:
    """The production query list: the whole incident, then its sub-queries."""
    queries: list[str] = []
    for q in [ctx["query"], *ctx.get("sub_queries", [])]:
        if q and q.strip() and q not in queries:
            queries.append(q)
    return queries


# ══════════════════════════════════════════════════════════════════════════════
# PHASE rerank — Qdrant reads + local models, no LLM
# ══════════════════════════════════════════════════════════════════════════════


def phase_rerank() -> None:
    from ..retrieval.reranker import Reranker
    from ..retrieval.vector_retriever import VectorRetriever

    with open(CONTEXTS_PATH, encoding="utf-8") as f:
        contexts = json.load(f)

    cache: dict = {}
    if CACHE_PATH.exists():
        cache = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    todo = [c for c in contexts if c["id"] not in cache]
    print(f"[RERANK] {len(contexts)} cases, {len(todo)} to do")
    if not todo:
        return

    vector = VectorRetriever()
    reranker = Reranker()
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)

    for i, ctx in enumerate(todo, 1):
        per_query = []
        for q in _all_queries(ctx):
            with contextlib.redirect_stdout(io.StringIO()):
                hits = reranker.rerank(q, vector.search_all(q, top_k=VECTOR_TOP_K))
            per_query.append({
                "query": q,
                "hits": [
                    {
                        "stix_id": h.stix_id,
                        "p": float(h.score),
                        "metadata": {
                            k: (h.metadata or {}).get(k, "")
                            for k in ("entity_type", "node_label", "name", "attack_id",
                                      "source_id", "target_id")
                        },
                    }
                    for h in hits
                ],
            })
        cache[ctx["id"]] = per_query
        CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
        print(f"  [{i}/{len(todo)}] {ctx['id']}: {len(per_query)} queries")


# ══════════════════════════════════════════════════════════════════════════════
# PHASE score — offline
# ══════════════════════════════════════════════════════════════════════════════


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def _merge(per_query: list[dict], mode: str, entities: dict) -> tuple[GraphRAGResult, dict]:
    """Reweight each sub-query's hits and merge them the way production does.

    Returns the merged result — vector hits with the weighted score in
    ``mode``'s scale, plus one centre-only subgraph per graph seed, capped and
    ordered by the real merge — and, per stix_id, where each vector hit came
    from: its sub-query's top score and its rank. Neighbours are not fetched,
    so a cited neighbour row is missing in both modes alike.
    """
    ranked: dict[str, list[VectorResult]] = {}
    for entry in per_query:
        hits = [
            VectorResult(
                document="",
                metadata=dict(h["metadata"]),
                score=h["p"] if mode == "single" else _sigmoid(h["p"]),
                stix_id=h["stix_id"],
            )
            for h in entry["hits"]
        ]
        ranked[entry["query"]] = HybridRetriever._reweight_by_type(hits)

    def centres(hits: list[VectorResult]) -> list[SubgraphResult]:
        # The seeds retrieve() would expand: the quota's hits, both ends of a relationship.
        return [
            SubgraphResult(center_node=GraphNode(sid, *entities[sid]))
            for sid in HybridRetriever._graph_seeds(hits, PER_QUERY_K)
            if sid in entities
        ]

    # The real merge, fed the lists above instead of live retrieval.
    retriever = HybridRetriever.__new__(HybridRetriever)
    retriever.retrieve = lambda query, **_: GraphRAGResult(
        vector_results=ranked[query], graph_results=centres(ranked[query])
    )
    with contextlib.redirect_stdout(io.StringIO()):
        result = retriever.retrieve_multi_quota(
            [e["query"] for e in per_query], per_query_k=PER_QUERY_K, top_k=VECTOR_TOP_K
        )
    merged = result.vector_results

    origin: dict[str, dict] = {}
    for hits in ranked.values():
        top = hits[0].score if hits else 0.0
        for rank, h in enumerate(hits[:PER_QUERY_K], 1):
            # First claim wins, as in the merge: identity picks the object that survived.
            if any(h is m for m in merged) and h.stix_id not in origin:
                origin[h.stix_id] = {"top": top, "rank": rank}
    return result, origin


def _rescored(merged: list[VectorResult], origin: dict, rule: str) -> list[VectorResult]:
    """The merged hits with ``score`` replaced by the value ``rule`` filters on."""
    out = []
    for h in merged:
        o = origin.get(h.stix_id, {"top": h.score, "rank": PER_QUERY_K})
        if rule == "absolute":
            value = h.score
        elif rule == "relative":
            value = h.score / o["top"] if o["top"] > 0 else 0.0
        else:  # rank: keep rank <= k  <=>  -rank >= -k
            value = -float(o["rank"])
        out.append(dataclasses.replace(h, score=value))
    return out


def _base(attack_id: str) -> str:
    return attack_id.upper().split(".")[0]


def _table_stats(result, origin, rule, threshold, answer, gold) -> dict:
    cut = -float(threshold) if rule == "rank" else threshold
    rows = build_mitre_table(
        GraphRAGResult(
            vector_results=_rescored(result.vector_results, origin, rule),
            graph_results=result.graph_results,
        ),
        answer,
        score_threshold=cut,
    )
    score = technique_set_score(_technique_ids_from_rows(rows), gold)
    gold_bases = {_base(g) for g in gold}
    kept = [r for r in rows if r.relevance == "retrieved_only"]
    tech = [r for r in kept if r.entity_type in _TECHNIQUE_LABELS and r.technique_id]
    return {
        "precision": score["precision"],
        "recall": score["recall"],
        "f1": score["f1"],
        "uncited_good": sum(1 for r in tech if _base(r.technique_id) in gold_bases),
        "uncited_noise": sum(1 for r in tech if _base(r.technique_id) not in gold_bases),
        "uncited_other": Counter(r.entity_type or "?" for r in kept if r not in tech),
    }


_LABEL_BY_TYPE = {
    "malware": "Software",
    "tool": "Software",
    "intrusion-set": "Group",
    "course-of-action": "Mitigation",
    "campaign": "Campaign",
    "x-mitre-tactic": "Tactic",
    "x-mitre-data-component": "DataComponent",
}


def _entities_by_stix() -> dict[str, tuple[str, str, str]]:
    """stix_id -> (name, node label, ATT&CK ID) across the current bundles.

    A relationship hit names its endpoints by stix_id only, yet both endpoints
    seed graph expansion, so a technique it points at can still become a
    table row (a graph centre, kept when the answer cites it).
    """
    root = Path(__file__).resolve().parents[5] / "Mitre_ATT&CK Doc"
    entities: dict[str, tuple[str, str, str]] = {}
    for domain in ("enterprise", "mobile", "ics"):
        bundle = json.loads((root / f"{domain}-attack" / f"{domain}-attack.json")
                            .read_text(encoding="utf-8"))
        for o in bundle["objects"]:
            if o.get("revoked"):
                continue
            if o.get("type") == "attack-pattern":
                label = "Subtechnique" if o.get("x_mitre_is_subtechnique") else "Technique"
            elif o.get("type") in _LABEL_BY_TYPE:
                label = _LABEL_BY_TYPE[o["type"]]
            else:
                continue
            attack_id = next(
                (r["external_id"].upper() for r in o.get("external_references") or []
                 if r.get("source_name", "").startswith("mitre-") and r.get("external_id")),
                "",
            )
            entities[o["id"]] = (o.get("name", ""), label, attack_id)
    return entities


def _retrieval_stats(merged: list[VectorResult], gold: set[str], by_stix: dict) -> dict:
    nodes = {
        (h.metadata.get("attack_id") or "").upper()
        for h in merged
        if h.metadata.get("entity_type") == "Node"
        and h.metadata.get("node_label") in _TECHNIQUE_LABELS
        and h.metadata.get("attack_id")
    }
    endpoints = {
        by_stix[sid][2]
        for h in merged
        if h.metadata.get("entity_type") == "Relationship"
        for sid in (h.metadata.get("source_id"), h.metadata.get("target_id"))
        if sid in by_stix and by_stix[sid][1] in _TECHNIQUE_LABELS and by_stix[sid][2]
    }
    s = technique_set_score(nodes, gold)
    types = Counter(
        h.metadata.get("node_label") or h.metadata.get("entity_type") or "?" for h in merged
    )
    return {
        "recall": s["recall"],
        "precision": s["precision"],
        "recall_with_edges": technique_set_score(nodes | endpoints, gold)["recall"],
        "types": types,
    }


def phase_score(variant: str) -> None:
    cache = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    gold = {
        s["id"]: set(s["gold_attack_ids"])
        for s in json.loads(DATASET_PATH.read_text(encoding="utf-8"))
        if s.get("gold_attack_ids")
    }
    answers = {}
    with open(GENERATIONS_PATH, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                g = json.loads(line)
                if g["variant"] == variant and g.get("answer"):
                    answers[g["sample_id"]] = g["answer"]

    cases = [cid for cid in cache if cid in gold and cid in answers]
    print(f"[SCORE] variant {variant}: {len(cases)} cases "
          f"(of {len(cache)} reranked, {len(answers)} with an answer)")

    entities = _entities_by_stix()
    results: dict = {}
    for mode in ("single", "double"):
        retrieval, tables = [], {}
        for cid in cases:
            merged, origin = _merge(cache[cid], mode, entities)
            retrieval.append(_retrieval_stats(merged.vector_results, gold[cid], entities))
            configs = [("cited_only", math.inf), ("keep_all", -math.inf)]
            for rule in ("absolute", "relative", "rank"):
                configs += [(rule, t) for t in GRIDS[(rule, mode)]]
            for rule, t in configs:
                real_rule = "absolute" if rule in ("cited_only", "keep_all") else rule
                tables.setdefault((rule, t), []).append(
                    _table_stats(merged, origin, real_rule, t, answers[cid], gold[cid])
                )
        results[mode] = {"retrieval": retrieval, "tables": tables}

    report = _render(results, variant, len(cases))
    path = RESULTS_DIR / f"{REPORT_STEM}_{variant}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8")
    print(report)
    print(f"\n[SCORE] report -> {path}")


def _mean(xs) -> float:
    xs = list(xs)
    return sum(xs) / len(xs) if xs else 0.0


def _render(results: dict, variant: str, n: int) -> str:
    out = [
        "# MITRE table threshold calibration",
        "",
        f"{n} incidents from `data/incident_draft.json` (LLM-drafted), answers from "
        f"gen_bench variant {variant}. Scores recomputed with today's reranker; "
        "`double` replays the pre-2026-08-15 double sigmoid on the same logits. "
        "Macro-averaged soft technique P/R/F1 (exact 1.0, same base 0.5). "
        "An ablation for choosing a rule, not a headline benchmark.",
        "",
        "Caveats: the incidents are LLM-drafted, not real CTI. The answers were "
        "generated in July from contexts retrieved under the double sigmoid, so any "
        "comparison of the two modes' tables favours `double`; compare rules within a "
        "mode. Graph centres are rebuilt from the seeds, but neighbours are not "
        "fetched, so a cited neighbour row is missing in both modes.",
        "",
        "## Retrieval: which hits win the per-sub-query quota",
        "",
        "Recall counts technique nodes among the merged vector hits; the second column "
        "adds the techniques at either end of a merged relationship hit, which reach "
        "the context through graph expansion but can never be an uncited table row.",
        "",
        "| mode | technique recall (nodes) | + relationship endpoints "
        "| technique precision (nodes) | quota slots by type |",
        "| --- | --- | --- | --- | --- |",
    ]
    for mode, r in results.items():
        types = sum((x["types"] for x in r["retrieval"]), Counter())
        mix = ", ".join(f"{k} {v}" for k, v in types.most_common())
        out.append(
            f"| {mode} | {_mean(x['recall'] for x in r['retrieval']):.3f} "
            f"| {_mean(x['recall_with_edges'] for x in r['retrieval']):.3f} "
            f"| {_mean(x['precision'] for x in r['retrieval']):.3f} | {mix} |"
        )

    out += [
        "",
        "## Filter: which uncited rows the table keeps",
        "",
        "`good` / `noise` count uncited technique rows whose base technique is / is not "
        "in gold, summed over all incidents; `other` counts uncited non-technique rows "
        "(Software, Group, Mitigation…), which gold cannot judge. ★ marks the value each "
        "mode shipped with.",
    ]
    for mode, r in results.items():
        out += [
            "",
            f"### {mode}",
            "",
            "| rule | cut | P | R | F1 | good | noise | other |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
        for (rule, t), stats in r["tables"].items():
            cut = {"cited_only": "—", "keep_all": "—"}.get(rule) or (
                f"rank ≤ {t}" if rule == "rank" else f"{t:g}"
            )
            star = " ★" if rule == "absolute" and t == SHIPPED[mode] else ""
            other = sum((s["uncited_other"] for s in stats), Counter())
            out.append(
                f"| {rule}{star} | {cut} "
                f"| {_mean(s['precision'] for s in stats):.3f} "
                f"| {_mean(s['recall'] for s in stats):.3f} "
                f"| {_mean(s['f1'] for s in stats):.3f} "
                f"| {sum(s['uncited_good'] for s in stats)} "
                f"| {sum(s['uncited_noise'] for s in stats)} "
                f"| {sum(other.values())} |"
            )
    return "\n".join(out) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--phase", choices=["rerank", "score"], required=True)
    parser.add_argument("--variant", default="C",
                        help="gen_bench answer variant for cited_in_answer (C = served path)")
    args = parser.parse_args()
    if args.phase == "rerank":
        phase_rerank()
    else:
        phase_score(args.variant)


if __name__ == "__main__":
    main()
