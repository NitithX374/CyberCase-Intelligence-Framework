"""Build a Qdrant index of the ATT&CK corpus with a chosen embedding backend.

Two things changed at once in this experiment - the corpus (the STIX parser now
keeps detection analytics, restores DETECTS, and carries ATT&CK ids on
relationships) and, optionally, the embedding model. Running both backends over
the *same* parse is what lets the two be told apart afterwards:

    corpus v1 + bge-m3   already indexed (mitre_entities)          - baseline
    corpus v2 + bge-m3   --embedder bge   -> mitre_entities_v2     - parser only
    corpus v2 + jina     --embedder jina  -> mitre_entities_jina   - + model

Nothing here touches the collections the service reads. Production keeps
serving from mitre_entities/mitre_relationships until a swap is decided.

Usage (from rag_service/app):
    python -m RAG.GraphRAG.evaluation.published.ingest_corpus --embedder bge
    python -m RAG.GraphRAG.evaluation.published.ingest_corpus --embedder jina
    python -m RAG.GraphRAG.evaluation.published.ingest_corpus --embedder harrier
    python -m RAG.GraphRAG.evaluation.published.ingest_corpus --embedder jina --dry-run
"""

from __future__ import annotations

import argparse
import sys
import time
from dataclasses import dataclass, field

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    SparseIndexParams,
    SparseVector,
    SparseVectorParams,
    VectorParams,
)

from ...config import (
    EMBED_DIM,
    EMBED_MODEL,
    QDRANT_API_KEY,
    QDRANT_HOST,
    QDRANT_PORT,
    QDRANT_URL,
    USE_FP16,
    sep,
)
from ...ingestion.stix_parser import parse_all_domains
from ...ingestion.vector_loader import (
    build_entity_document,
    build_relationship_document,
    uuid_from_stix_id,
)

UPSERT_BATCH = 256     # coarser: amortises the Qdrant Cloud round trip
UPSERT_RETRIES = 9     # cloud drops connections mid-run, and so does the local
UPSERT_MAX_WAIT = 60   # link. Capped backoff rides out ~4 minutes of downtime
                       # (1+2+4+8+16+32+60+60+60s) instead of the ~30s that an
                       # uncapped doubling over 6 attempts would have given.

# Every sentence-transformers model here is capped at 512 tokens and batch 16.
# Measured on this corpus: median 110 tokens, p90 299, max 661 - so 512
# truncates almost nothing, while a model's 32768 default reserves attention
# memory a 4 GB card does not have. Batch 32 peaks at 4.22 GB and spills into
# shared system memory, which costs two thirds of the throughput (3.3 doc/s
# against 9.1), so the ceiling here is memory rather than compute.
ST_MAX_TOKENS = 512
ST_BATCH = 16


@dataclass(frozen=True)
class STSpec:
    """A sentence-transformers embedding backend.

    Query and document prompts are part of how these models were trained, not
    decoration. Encoding both sides the same way, or dropping the instruction a
    model expects, handicaps it for reasons that have nothing to do with the
    corpus - which would then be misread as the model being weak.
    """

    model_id: str
    suffix: str
    dim: int
    doc_prompt: str | None = None     # prompt_name for documents, None = plain
    query_prompt: str | None = None   # prompt_name for queries
    encode_kwargs: dict = field(default_factory=dict)
    dtype: str = "auto"


SPECS = {
    "jina": STSpec(
        model_id="jinaai/jina-embeddings-v5-text-small",
        suffix="jina",
        dim=1024,
        doc_prompt="document",
        query_prompt="query",
        encode_kwargs={"task": "retrieval"},  # selects the retrieval LoRA adapter
        dtype="bfloat16",
    ),
    "harrier": STSpec(
        model_id="microsoft/harrier-oss-v1-0.6b",
        suffix="harrier",
        dim=1024,
        doc_prompt=None,  # documents are encoded bare; only queries are prefixed
        query_prompt="web_search_query",
    ),
}

# Kept for callers that imported these before the registry existed.
JINA_MODEL = SPECS["jina"].model_id
JINA_MAX_TOKENS = ST_MAX_TOKENS
JINA_BATCH = ST_BATCH


# ── backends ────────────────────────────────────────────────────────────────
class BgeBackend:
    """BGE-M3: dense + lexical sparse from a single encode call."""

    name = "bge"
    suffix = "v2"
    dim = EMBED_DIM
    has_sparse = True
    chunk = 16  # what ingestion/vector_loader.py feeds it, kept identical

    def __init__(self):
        from FlagEmbedding import BGEM3FlagModel
        print(f"[EMBED] Loading {EMBED_MODEL} (fp16={USE_FP16})")
        self.model = BGEM3FlagModel(EMBED_MODEL, use_fp16=USE_FP16)

    def encode_documents(self, texts: list[str]):
        out = self.model.encode(
            texts, return_dense=True, return_sparse=True, return_colbert_vecs=False
        )
        return out["dense_vecs"].tolist(), out["lexical_weights"]


class STBackend:
    """Any sentence-transformers dense encoder, driven by an STSpec."""

    has_sparse = False
    # Fed in large chunks on purpose: sentence-transformers sorts a chunk by
    # length before batching, so padding waste collapses. Handing it 16 at a
    # time defeats that and costs most of the throughput (1.0 doc/s vs 9.1).
    chunk = 256

    def __init__(self, spec: STSpec):
        from sentence_transformers import SentenceTransformer

        self.spec = spec
        self.name = spec.suffix
        self.suffix = spec.suffix
        self.dim = spec.dim
        print(f"[EMBED] Loading {spec.model_id} (dtype={spec.dtype})")
        self.model = SentenceTransformer(
            spec.model_id,
            trust_remote_code=True,
            model_kwargs={"dtype": spec.dtype},
        )
        self.model.max_seq_length = ST_MAX_TOKENS

    def _encode(self, texts: list[str], prompt: str | None):
        kwargs = dict(self.spec.encode_kwargs)
        if prompt:
            kwargs["prompt_name"] = prompt
        return self.model.encode(
            texts,
            batch_size=ST_BATCH,
            normalize_embeddings=True,
            show_progress_bar=False,
            **kwargs,
        )

    def encode_documents(self, texts: list[str]):
        return self._encode(texts, self.spec.doc_prompt).tolist(), None

    def encode_query(self, text: str):
        return self._encode([text], self.spec.query_prompt)[0].tolist(), None


def make_backend(name: str):
    if name == "bge":
        return BgeBackend()
    return STBackend(SPECS[name])


BACKENDS = ["bge", *SPECS]


# ── qdrant ──────────────────────────────────────────────────────────────────
def make_client() -> QdrantClient:
    if QDRANT_URL:
        print(f"[QDRANT] Cloud: {QDRANT_URL}")
        return QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=180)
    if QDRANT_HOST:
        print(f"[QDRANT] {QDRANT_HOST}:{QDRANT_PORT}")
        return QdrantClient(
            host=QDRANT_HOST, port=QDRANT_PORT, api_key=QDRANT_API_KEY, timeout=180
        )
    raise SystemExit("[QDRANT] No QDRANT_URL/QDRANT_HOST - refusing an in-memory corpus")


def wait_for_qdrant(client: QdrantClient, budget_s: int) -> None:
    """Block until Qdrant answers, or give up after budget_s.

    Worth doing before the encoder is loaded rather than after: a dead endpoint
    otherwise costs a GPU model load and a full parse before anyone finds out,
    and the run dies holding a collection it has already emptied.
    """
    started = time.time()
    attempt = 0
    while True:
        try:
            client.get_collections()
            if attempt:
                print(f"[QDRANT] Reachable after {time.time() - started:.0f}s")
            return
        except Exception as exc:
            waited = time.time() - started
            if waited >= budget_s:
                raise SystemExit(
                    f"[QDRANT] Unreachable after {waited:.0f}s ({type(exc).__name__}). "
                    "Check the cluster status at cloud.qdrant.io - a timeout with no "
                    "HTTP status is the endpoint not answering at all, not an auth "
                    "or key problem."
                )
            attempt += 1
            wait = min(2 ** min(attempt, 5), UPSERT_MAX_WAIT)
            print(
                f"[QDRANT] Not reachable ({type(exc).__name__}); "
                f"waited {waited:.0f}s/{budget_s}s, retrying in {wait}s",
                flush=True,
            )
            time.sleep(wait)


def init_collection(client: QdrantClient, name: str, backend) -> None:
    """Recreated from scratch so a partial earlier run leaves no stale points."""
    if client.collection_exists(name):
        print(f"[QDRANT] Dropping existing {name}")
        client.delete_collection(name)

    kwargs = {
        "vectors_config": {"dense": VectorParams(size=backend.dim, distance=Distance.COSINE)}
    }
    if backend.has_sparse:
        kwargs["sparse_vectors_config"] = {"sparse": SparseVectorParams(index=SparseIndexParams())}

    client.create_collection(collection_name=name, **kwargs)
    extra = ", sparse" if backend.has_sparse else ""
    print(f"[QDRANT] Created {name} (dense {backend.dim}{extra})")


def embed_and_store(client, collection, backend, ids, docs, metas, label) -> int:
    """Embed in backend-sized chunks, flushing to Qdrant every UPSERT_BATCH.

    Flushed as it goes rather than accumulated: 21k relationship vectors held
    as Python float lists is well over half a gigabyte of resident memory, on a
    machine that is also holding the encoder on a 4 GB card.
    """
    print(f"[QDRANT] Embedding {len(docs)} {label} documents...")
    pending: list[PointStruct] = []
    stored = 0
    started = time.time()

    def flush():
        """Upsert with backoff.

        Qdrant Cloud drops the occasional connection mid-run - twice in one
        30-minute ingest here, once at 83% - and the local link drops too.
        Without a retry the whole embedding pass is thrown away for a fault
        that usually clears on its own.

        Retrying is safe to the point of being boring: point ids come from
        uuid_from_stix_id, so re-sending a batch that did land overwrites it
        rather than duplicating it.
        """
        nonlocal pending, stored
        if not pending:
            return
        for attempt in range(UPSERT_RETRIES):
            try:
                client.upsert(collection_name=collection, points=pending)
                break
            except Exception as exc:
                if attempt == UPSERT_RETRIES - 1:
                    raise
                wait = min(2 ** attempt, UPSERT_MAX_WAIT)
                print(
                    f"        [RETRY] upsert failed ({type(exc).__name__}), "
                    f"retrying in {wait}s",
                    flush=True,
                )
                time.sleep(wait)
        stored += len(pending)
        pending = []

    step = backend.chunk
    for i in range(0, len(docs), step):
        batch_docs = docs[i : i + step]
        dense, sparse = backend.encode_documents(batch_docs)

        for j, vec in enumerate(dense):
            n = i + j
            vectors = {"dense": vec}
            if sparse is not None:
                weights = sparse[j]
                vectors["sparse"] = SparseVector(
                    indices=[int(k) for k in weights.keys()],
                    values=[float(v) for v in weights.values()],
                )
            pending.append(
                PointStruct(id=uuid_from_stix_id(ids[n]), vector=vectors, payload=metas[n])
            )

        if len(pending) >= UPSERT_BATCH:
            flush()

        done = min(i + step, len(docs))
        if done % 1600 < step or done == len(docs):
            rate = done / max(time.time() - started, 1e-6)
            eta = (len(docs) - done) / max(rate, 1e-6)
            print(
                f"        {done}/{len(docs)}  {rate:.1f} doc/s  eta {eta / 60:.1f} min",
                flush=True,
            )

    flush()
    print(f"[QDRANT] Stored {stored} points in {collection}")
    return stored


# ── document assembly ───────────────────────────────────────────────────────
def entity_rows(entities):
    ids, docs, metas = [], [], []
    for e in entities:
        text = build_entity_document(e)
        if not text:
            continue
        ids.append(e.stix_id)
        docs.append(text)
        metas.append(
            {
                "stix_id": e.stix_id,
                "attack_id": getattr(e, "detects_attack_id", "") or e.attack_id,
                "entity_type": "Node",
                "node_label": e.node_label,
                "name": e.name,
                "domain": e.domain,
                "url": e.url,
                "document": text,
            }
        )
    return ids, docs, metas


def relationship_rows(relationships):
    ids, docs, metas = [], [], []
    for r in relationships:
        text = build_relationship_document(r)
        if not text:
            continue
        ids.append(r.stix_id)
        docs.append(text)
        metas.append(
            {
                "stix_id": r.stix_id,
                "entity_type": "Relationship",
                "edge_label": r.edge_label,
                "source_id": r.source_ref,
                "target_id": r.target_ref,
                "source_name": r.source_name,
                "target_name": r.target_name,
                "attack_id": r.target_attack_id or r.source_attack_id,
                "source_attack_id": r.source_attack_id,
                "target_attack_id": r.target_attack_id,
                "document": text,
            }
        )
    return ids, docs, metas


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--embedder", choices=BACKENDS, required=True)
    ap.add_argument("--suffix", default=None, help="Collection suffix (default: the backend's own)")
    ap.add_argument("--limit", type=int, default=0, help="Index only the first N of each kind")
    ap.add_argument("--entities-only", action="store_true")
    ap.add_argument(
        "--wait",
        type=int,
        default=0,
        metavar="SECONDS",
        help="Poll Qdrant until it answers before doing any work (0 = fail fast)",
    )
    ap.add_argument("--dry-run", action="store_true", help="Parse and report counts, embed nothing")
    args = ap.parse_args()

    sep(f"Corpus ingest - embedder={args.embedder}")

    parser = parse_all_domains()
    e_ids, e_docs, e_metas = entity_rows(parser.entities)
    r_ids, r_docs, r_metas = relationship_rows(parser.relationships)

    if args.limit:
        e_ids, e_docs, e_metas = e_ids[: args.limit], e_docs[: args.limit], e_metas[: args.limit]
        r_ids, r_docs, r_metas = r_ids[: args.limit], r_docs[: args.limit], r_metas[: args.limit]

    n_analytic = sum(1 for m in e_metas if m["node_label"] == "Analytic")
    n_rel_id = sum(1 for m in r_metas if m["attack_id"])
    print(
        f"\n[DOCS] entities {len(e_docs)} (Analytic {n_analytic}), "
        f"relationships {len(r_docs)} ({n_rel_id} carry an ATT&CK id)"
    )

    if args.dry_run:
        for m in e_metas:
            if m["node_label"] == "Analytic":
                print(f"\n[DOCS] sample analytic -> {m['attack_id']}\n  {m['document'][:420]}")
                break
        for m in r_metas:
            if m["edge_label"] == "USES" and m["attack_id"]:
                print(f"\n[DOCS] sample procedure -> {m['attack_id']}\n  {m['document'][:280]}")
                break
        return 0

    client = make_client()
    wait_for_qdrant(client, args.wait)

    backend = make_backend(args.embedder)
    suffix = args.suffix or backend.suffix

    ent_col = f"mitre_entities_{suffix}"
    rel_col = f"mitre_relationships_{suffix}"

    init_collection(client, ent_col, backend)
    embed_and_store(client, ent_col, backend, e_ids, e_docs, e_metas, "entity")

    if not args.entities_only:
        init_collection(client, rel_col, backend)
        embed_and_store(client, rel_col, backend, r_ids, r_docs, r_metas, "relationship")

    sep("Ingest complete")
    print(f"  {ent_col}")
    if not args.entities_only:
        print(f"  {rel_col}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
