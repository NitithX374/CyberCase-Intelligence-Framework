"""Retrieval-only comparison of corpus versions and embedding backends.

Two things were changed together - the STIX parser (which decides what is in the
corpus at all) and, optionally, the embedding model. This scores four configs so
each change can be attributed on its own:

    v1-bge-hybrid   mitre_entities        dense+sparse   what production serves
    v2-bge-hybrid   mitre_entities_v2     dense+sparse   parser change alone
    v2-bge-dense    mitre_entities_v2     dense only     control for the next row
    v2-jina-dense   mitre_entities_jina   dense only     model change alone

jina has no lexical head, so comparing it against a hybrid arm would credit the
model for losing sparse retrieval. v2-bge-dense exists purely so that
v2-jina-dense has something it can be honestly subtracted from.

No LLM is called: this measures whether the right document is reachable, not
what a model does with it. That makes the whole sweep free and repeatable, and
it is an ABLATION - the headline number for any winning config still has to come
from the served agent graph via run_benchmark.py.

Usage (from rag_service/app):
    python -m RAG.GraphRAG.evaluation.published.compare_corpus --dataset thai-cti
    python -m RAG.GraphRAG.evaluation.published.compare_corpus --dataset tram --max-samples 200
    python -m RAG.GraphRAG.evaluation.published.compare_corpus --dataset thai-cti --configs v2-bge-dense,v2-jina-dense
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import (
    FieldCondition,
    Filter,
    Fusion,
    FusionQuery,
    MatchValue,
    Prefetch,
    SparseVector,
)

from ...config import (
    ATTACK_DOMAIN_FILTER,
    EMBED_MODEL,
    QDRANT_API_KEY,
    QDRANT_HOST,
    QDRANT_PORT,
    QDRANT_URL,
    USE_FP16,
    sep,
)
from .attack_version_map import VersionMap
from .ingest_corpus import JINA_BATCH, JINA_MAX_TOKENS, JINA_MODEL
from .run_benchmark import load_dataset

RESULTS_DIR = Path(__file__).resolve().parent / "data" / "runs"


# ── query encoders ──────────────────────────────────────────────────────────
class BgeQuery:
    """BGE-M3, exactly as retrieval/vector_retriever.py calls it."""

    def __init__(self):
        from FlagEmbedding import BGEM3FlagModel
        print(f"[EMBED] Loading {EMBED_MODEL} (fp16={USE_FP16})")
        self.model = BGEM3FlagModel(EMBED_MODEL, use_fp16=USE_FP16)

    def encode(self, query: str):
        out = self.model.encode(
            [query], return_dense=True, return_sparse=True, return_colbert_vecs=False
        )
        weights = out["lexical_weights"][0]
        indices = [int(k) for k in weights.keys()] or [0]
        values = [float(v) for v in weights.values()] or [0.0]
        return out["dense_vecs"][0].tolist(), (indices, values)


class JinaQuery:
    """jina v5 with the query prompt and the retrieval adapter it was trained
    with. Documents were indexed under prompt_name="document"; using the same
    prompt on both sides would be measuring the wrong model."""

    def __init__(self):
        from sentence_transformers import SentenceTransformer
        print(f"[EMBED] Loading {JINA_MODEL}")
        self.model = SentenceTransformer(
            JINA_MODEL, trust_remote_code=True, model_kwargs={"torch_dtype": "bfloat16"}
        )
        self.model.max_seq_length = JINA_MAX_TOKENS

    def encode(self, query: str):
        vec = self.model.encode(
            [query],
            prompt_name="query",
            task="retrieval",
            batch_size=JINA_BATCH,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return vec[0].tolist(), None


# ── configs ─────────────────────────────────────────────────────────────────
@dataclass
class Config:
    name: str
    suffix: str          # "" for the v1 collections
    encoder: str         # "bge" | "jina"
    hybrid: bool
    note: str

    @property
    def entities(self) -> str:
        return "mitre_entities" + (f"_{self.suffix}" if self.suffix else "")

    @property
    def relationships(self) -> str:
        return "mitre_relationships" + (f"_{self.suffix}" if self.suffix else "")


CONFIGS = {
    c.name: c
    for c in [
        Config("v1-bge-hybrid", "", "bge", True, "production today"),
        Config("v2-bge-hybrid", "v2", "bge", True, "parser change"),
        Config("v2-bge-dense", "v2", "bge", False, "control for jina"),
        Config("v2-jina-dense", "jina", "jina", False, "model change"),
    ]
}


# ── retrieval ───────────────────────────────────────────────────────────────
def make_client() -> QdrantClient:
    if QDRANT_URL:
        return QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=120)
    if QDRANT_HOST:
        return QdrantClient(
            host=QDRANT_HOST, port=QDRANT_PORT, api_key=QDRANT_API_KEY, timeout=120
        )
    raise SystemExit("[QDRANT] No QDRANT_URL/QDRANT_HOST configured")


def domain_filter() -> Filter | None:
    if not ATTACK_DOMAIN_FILTER:
        return None
    return Filter(
        must=[FieldCondition(key="domain", match=MatchValue(value=ATTACK_DOMAIN_FILTER))]
    )


def search(client, collection, cfg, dense, sparse, top_k, qfilter):
    """One collection, one query. Hybrid mirrors the production prefetch+RRF."""
    if cfg.hybrid and sparse is not None:
        indices, values = sparse
        res = client.query_points(
            collection_name=collection,
            prefetch=[
                Prefetch(query=dense, using="dense", limit=max(top_k * 5, 50), filter=qfilter),
                Prefetch(
                    query=SparseVector(indices=indices, values=values),
                    using="sparse",
                    limit=max(top_k * 5, 50),
                    filter=qfilter,
                ),
            ],
            query=FusionQuery(fusion=Fusion.RRF),
            limit=top_k,
            with_payload=True,
        )
    else:
        res = client.query_points(
            collection_name=collection,
            query=dense,
            using="dense",
            limit=top_k,
            query_filter=qfilter,
            with_payload=True,
        )
    return [p.payload or {} for p in res.points]


def ranked_ids(payloads: list[dict]) -> list[str]:
    """Retrieved ATT&CK ids in rank order, first occurrence wins.

    Deduplicated because a technique, one of its procedure examples and one of
    its analytics are three documents pointing at the same answer; counting them
    three times would flatter recall without retrieving anything new.
    """
    seen: list[str] = []
    for p in payloads:
        aid = (p.get("attack_id") or "").strip().upper()
        if aid.startswith("T") and aid not in seen:
            seen.append(aid)
    return seen


def interleave(a: list[str], b: list[str]) -> list[str]:
    """Round-robin entity/relationship hits, as the hybrid retriever does, so
    neither collection can crowd the other out of the top of the list."""
    out: list[str] = []
    for i in range(max(len(a), len(b))):
        for src in (a, b):
            if i < len(src) and src[i] not in out:
                out.append(src[i])
    return out


# ── scoring ─────────────────────────────────────────────────────────────────
@dataclass
class Score:
    n: int = 0
    recall_sum: float = 0.0
    p_at_1: int = 0
    rr_sum: float = 0.0
    hit_any: int = 0
    depths: list[int] = field(default_factory=list)

    def add(self, preds: list[str], gold: list[str]) -> None:
        gold_set = {g.upper() for g in gold}
        self.n += 1
        found = [p for p in preds if p in gold_set]
        self.recall_sum += len(set(found)) / max(len(gold_set), 1)
        if preds and preds[0] in gold_set:
            self.p_at_1 += 1
        for rank, p in enumerate(preds, 1):
            if p in gold_set:
                self.rr_sum += 1.0 / rank
                self.hit_any += 1
                self.depths.append(rank)
                break

    def row(self) -> dict:
        n = max(self.n, 1)
        med = sorted(self.depths)[len(self.depths) // 2] if self.depths else 0
        return {
            "n": self.n,
            "recall": self.recall_sum / n,
            "p@1": self.p_at_1 / n,
            "mrr": self.rr_sum / n,
            "hit": self.hit_any / n,
            "median_rank": med,
        }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="thai-cti")
    ap.add_argument("--configs", default=",".join(CONFIGS))
    ap.add_argument("--top-k", type=int, default=20)
    ap.add_argument("--max-samples", type=int, default=0)
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    names = [c.strip() for c in args.configs.split(",") if c.strip()]
    unknown = [c for c in names if c not in CONFIGS]
    if unknown:
        raise SystemExit(f"unknown config(s): {unknown}. known: {sorted(CONFIGS)}")

    vmap = VersionMap.load()
    samples, unscoreable = load_dataset(args.dataset, vmap)
    if args.max_samples:
        samples = samples[: args.max_samples]

    sep(f"Corpus/embedder comparison - {args.dataset}")
    print(f"  {len(samples)} samples, top_k={args.top_k}, {unscoreable} unscoreable")

    client = make_client()
    qfilter = domain_filter()
    encoders: dict[str, object] = {}
    results: dict[str, dict] = {}

    for name in names:
        cfg = CONFIGS[name]
        for coll in (cfg.entities, cfg.relationships):
            if not client.collection_exists(coll):
                print(f"\n[SKIP] {name}: {coll} does not exist yet")
                break
        else:
            if cfg.encoder not in encoders:
                encoders[cfg.encoder] = BgeQuery() if cfg.encoder == "bge" else JinaQuery()
            enc = encoders[cfg.encoder]

            print(f"\n[RUN] {name} ({cfg.note}) -> {cfg.entities}")
            score = Score()
            started = time.time()
            for i, s in enumerate(samples, 1):
                dense, sparse = enc.encode(s["input"])
                ent = ranked_ids(search(client, cfg.entities, cfg, dense, sparse, args.top_k, qfilter))
                rel = ranked_ids(
                    search(client, cfg.relationships, cfg, dense, sparse, args.top_k, None)
                )
                score.add(interleave(ent, rel), s["gold"])
                if i % 25 == 0:
                    print(f"      {i}/{len(samples)}  {i / (time.time() - started):.1f} q/s", flush=True)
            results[name] = score.row()

    sep("Results")
    print(f"{'config':<16} {'note':<18} {'recall':>7} {'P@1':>7} {'MRR':>7} {'hit':>7} {'rank':>5}")
    for name in names:
        if name not in results:
            continue
        r = results[name]
        print(
            f"{name:<16} {CONFIGS[name].note:<18} {r['recall']:7.3f} {r['p@1']:7.3f} "
            f"{r['mrr']:7.3f} {r['hit']:7.3f} {r['median_rank']:5d}"
        )

    out = Path(args.out) if args.out else RESULTS_DIR / f"compare__{args.dataset}__k{args.top_k}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            {"dataset": args.dataset, "top_k": args.top_k, "n": len(samples), "results": results},
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\n[OUT] {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
