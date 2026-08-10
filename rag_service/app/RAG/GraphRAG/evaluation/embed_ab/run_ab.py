"""Run the embedding-model A/B/C comparison and write a report.

Every arm sees the same corpus, the same query set, and the same retrieval
topology, so the only thing that moves between arms is the embedding model
(and, for A vs B, whether its sparse component is used).

Queries are evaluated as Thai/English *pairs* carrying identical gold IDs:
the Thai score answers "how well does this model serve our users", and the
Thai-minus-English delta isolates the cross-lingual penalty, which is the
quantity no public benchmark reports for this setting.

Usage (from rag_service/app):
    python -m RAG.GraphRAG.evaluation.embed_ab.run_ab
    python -m RAG.GraphRAG.evaluation.embed_ab.run_ab --max-pairs 0        # all pairs
    python -m RAG.GraphRAG.evaluation.embed_ab.run_ab --arms A,B
"""

from __future__ import annotations

import argparse
import collections
import gc
import json
import random
import sys
import time
from dataclasses import replace
from pathlib import Path

from ..ground_truth import EvalSample, load_ground_truth
from ..retriever_metrics import evaluate_retriever
from .arms import (
    BgeDenseArm,
    BgeHybridArm,
    E5DenseArm,
    load_bge,
    load_e5,
    make_client,
)

_HERE = Path(__file__).resolve().parent
DEFAULT_DATASET = _HERE / "dataset_parallel.json"
DEFAULT_OUTPUT = _HERE / "results"

# Pinned to the production constants each cutoff corresponds to, so a reported
# number always maps to something the deployed system actually does:
#   5  = FINAL_TOP_K   (seeds handed to graph expansion)
#   10 = VECTOR_TOP_K  (pulled from Qdrant before reranking)
#   15 = max_vector    (ceiling on vector hits entering the LLM context)
# 20 and 50 are diagnostic: they separate "the gold was never retrieved" from
# "it was retrieved but ranked too low to be used". Never report them as the
# system's score. Fixed rather than a CLI flag so every run's report has the
# same columns and stays comparable.
K_VALUES = [1, 3, 5, 10, 15, 20, 50]


def _pair_key(s: EvalSample) -> tuple:
    """Thai variants copy their source sample's gold IDs verbatim, so
    (category, gold set) identifies a translation pair."""
    return (s.category, tuple(sorted(s.relevant_stix_ids)))


def build_pairs(samples: list[EvalSample], max_pairs: int, seed: int = 42):
    """Return [(th_sample, en_sample)], stratified across categories."""
    th = [s for s in samples if s.language == "th" and s.relevant_stix_ids]
    en_by_key: dict[tuple, EvalSample] = {}
    for s in samples:
        if s.language == "en" and s.relevant_stix_ids:
            en_by_key.setdefault(_pair_key(s), s)

    # Datasets built as one record per incident (real_cti) carry the English
    # parallel inline instead of as a separate "en" sample. Synthesise the twin
    # so those datasets are comparable here rather than silently unusable.
    for s in th:
        key = _pair_key(s)
        if key not in en_by_key and s.query_en:
            en_by_key[key] = replace(s, query=s.query_en, language="en")

    pairs = [(t, en_by_key[_pair_key(t)]) for t in th if _pair_key(t) in en_by_key]
    print(f"[AB] {len(th)} Thai samples, {len(pairs)} with an English twin")

    if max_pairs and len(pairs) > max_pairs:
        by_cat: dict[str, list] = collections.defaultdict(list)
        for p in pairs:
            by_cat[p[0].category].append(p)
        rng = random.Random(seed)
        for v in by_cat.values():
            rng.shuffle(v)
        selected, cats = [], sorted(by_cat)
        while len(selected) < max_pairs and any(by_cat[c] for c in cats):
            for c in cats:
                if by_cat[c] and len(selected) < max_pairs:
                    selected.append(by_cat[c].pop())
        pairs = selected
        print(f"[AB] Stratified down to {len(pairs)} pairs "
              f"({len(set(p[0].category for p in pairs))} categories)")

    return pairs


def gold_coverage(client, pairs, collections_pair) -> dict:
    """What fraction of gold STIX IDs actually exist as points in the corpus?

    Gold comes from Neo4j; the vector corpus drops entities/relationships that
    have no description. Unreachable gold caps recall for *every* arm equally,
    so it does not bias the comparison — but it does explain why absolute
    recall looks low, and the thesis should quote the figure.
    """
    from ...ingestion.vector_loader import uuid_from_stix_id

    gold = {i for th, _ in pairs for i in th.relevant_stix_ids}
    found = set()
    ids = [uuid_from_stix_id(g) for g in gold]
    lookup = dict(zip(ids, gold))
    for coll in collections_pair:
        for i in range(0, len(ids), 256):
            chunk = ids[i : i + 256]
            try:
                pts = client.retrieve(collection_name=coll, ids=chunk, with_payload=False)
            except Exception:
                continue
            found |= {lookup[str(p.id)] for p in pts if str(p.id) in lookup}
    return {"gold_total": len(gold), "gold_in_corpus": len(found),
            "coverage": len(found) / len(gold) if gold else 0.0}


def run_arm(arm, pairs, lang_label: str) -> dict:
    samples = [p[0] if lang_label == "th" else p[1] for p in pairs]
    fn = lambda q: arm.retrieve_ids(q, top_k=10)
    res = evaluate_retriever(fn, samples, k_values=K_VALUES,
                             retriever_name=f"{arm.name} {arm.label} [{lang_label}]")
    print(res.to_table())
    return {
        "arm": arm.name, "label": arm.label, "lang": lang_label,
        "n": len(samples),
        "hit": res.hit_at_k, "recall": res.recall_at_k,
        "precision": res.precision_at_k, "ndcg": res.ndcg_at_k,
        "mrr": res.mrr, "map": res.map_score,
        "latency_ms": res.avg_latency_ms,
    }


def _fmt(v) -> str:
    return f"{v:.3f}" if isinstance(v, float) else str(v)


def write_report(rows: list[dict], coverage: dict, out_dir: Path, meta: dict) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "results.json").write_text(
        json.dumps({"meta": meta, "coverage": coverage, "rows": rows},
                   indent=2, ensure_ascii=False), encoding="utf-8")

    by = {(r["arm"], r["lang"]): r for r in rows}
    arms = sorted({r["arm"] for r in rows})
    L = []
    L.append("# Embedding model comparison — retrieval (vector-only)\n")
    L.append(f"- corpus: {meta['corpus']}")
    L.append(f"- query pairs: {meta['n_pairs']} Thai/English, identical gold IDs")
    L.append(f"- gold reachable in vector corpus: {coverage['gold_in_corpus']}/"
             f"{coverage['gold_total']} ({coverage['coverage']*100:.1f}%) "
             f"— caps recall equally for all arms")
    L.append(f"- top-K = 10, metrics @ {K_VALUES}\n")

    for lang, title in (("th", "Thai queries (primary)"), ("en", "English queries")):
        L.append(f"\n## {title}\n")
        L.append("| Arm | Model | Hit@5 | Recall@5 | NDCG@5 | MRR | MAP | Latency (ms) |")
        L.append("|---|---|---|---|---|---|---|---|")
        for a in arms:
            r = by.get((a, lang))
            if not r:
                continue
            L.append(f"| {a} | {r['label']} | {_fmt(r['hit'].get(5))} | "
                     f"{_fmt(r['recall'].get(5))} | {_fmt(r['ndcg'].get(5))} | "
                     f"{_fmt(r['mrr'])} | {_fmt(r['map'])} | {r['latency_ms']:.0f} |")

    L.append("\n## Cross-lingual penalty (Thai − English, same gold)\n")
    L.append("| Arm | Model | ΔHit@5 | ΔNDCG@5 | ΔMRR |")
    L.append("|---|---|---|---|---|")
    for a in arms:
        t, e = by.get((a, "th")), by.get((a, "en"))
        if not (t and e):
            continue
        L.append(f"| {a} | {t['label']} | {t['hit'][5]-e['hit'][5]:+.3f} | "
                 f"{t['ndcg'][5]-e['ndcg'][5]:+.3f} | {t['mrr']-e['mrr']:+.3f} |")

    if ("A", "th") in by and ("B", "th") in by:
        a, b = by[("A", "th")], by[("B", "th")]
        L.append("\n## Sparse ablation (A − B, Thai)\n")
        L.append(f"Adding BGE-M3's lexical/sparse component to the same dense model "
                 f"moves NDCG@5 by **{a['ndcg'][5]-b['ndcg'][5]:+.3f}** and MRR by "
                 f"**{a['mrr']-b['mrr']:+.3f}**. Public leaderboards evaluate the "
                 f"dense vector alone, i.e. arm B.")

    path = out_dir / "report.md"
    path.write_text("\n".join(L) + "\n", encoding="utf-8")
    return path


def main() -> int:
    ap = argparse.ArgumentParser(description="Embedding-model A/B/C retrieval comparison")
    ap.add_argument("--dataset", default=str(DEFAULT_DATASET))
    ap.add_argument("--max-pairs", type=int, default=400,
                    help="Stratified pair cap; 0 = use every pair")
    ap.add_argument("--arms", default="A,B,C", help="Comma-separated subset of A,B,C")
    ap.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = ap.parse_args()

    wanted = {a.strip().upper() for a in args.arms.split(",") if a.strip()}
    samples = load_ground_truth(args.dataset)
    pairs = build_pairs(samples, args.max_pairs)
    if not pairs:
        print("[AB] No Thai/English pairs found — nothing to do")
        return 1

    client = make_client()
    from ...config import QDRANT_COLLECTION_ENTITIES, QDRANT_COLLECTION_RELATIONSHIPS
    coverage = gold_coverage(client, pairs,
                             [QDRANT_COLLECTION_ENTITIES, QDRANT_COLLECTION_RELATIONSHIPS])
    print(f"[AB] Gold reachable in corpus: {coverage['gold_in_corpus']}/"
          f"{coverage['gold_total']} ({coverage['coverage']*100:.1f}%)")

    rows: list[dict] = []
    started = time.perf_counter()

    # BGE-M3 arms share one model instance; E5 is loaded after they are freed
    # so the two large encoders never sit in VRAM at the same time.
    if wanted & {"A", "B"}:
        bge = load_bge()
        for cls in ([BgeHybridArm] if "A" in wanted else []) + \
                   ([BgeDenseArm] if "B" in wanted else []):
            arm = cls(bge, client)
            for lang in ("th", "en"):
                rows.append(run_arm(arm, pairs, lang))
        del bge
        gc.collect()
        try:
            import torch; torch.cuda.empty_cache()
        except Exception:
            pass

    if "C" in wanted:
        e5 = load_e5()
        arm = E5DenseArm(e5, client)
        for lang in ("th", "en"):
            rows.append(run_arm(arm, pairs, lang))

    meta = {
        "corpus": "MITRE ATT&CK (Neo4j-grounded gold, Qdrant vector corpus)",
        "n_pairs": len(pairs),
        "arms": sorted(wanted),
        "k_values": K_VALUES,
        "runtime_min": round((time.perf_counter() - started) / 60, 1),
    }
    path = write_report(rows, coverage, Path(args.output), meta)
    print(f"\n[AB] Wrote {path}  ({meta['runtime_min']} min)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
