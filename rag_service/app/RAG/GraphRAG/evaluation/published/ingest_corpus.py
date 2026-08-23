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
    python -m RAG.GraphRAG.evaluation.published.ingest_corpus --embedder jina --dry-run
"""

from __future__ import annotations

import argparse
import sys
import time

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

JINA_MODEL = "jinaai/jina-embeddings-v5-text-small"
JINA_DIM = 1024        # hidden_size in the published config
JINA_MAX_TOKENS = 512  # measured on this corpus: median 110 tokens, p90 299,
                       # max 661. 512 truncates almost nothing, while the 32768
                       # default reserves attention memory this 4 GB card does
                       # not have.
JINA_BATCH = 16        # 32 peaks at 4.22 GB and thrashes: 3.3 doc/s vs 9.1

UPSERT_BATCH = 256     # coarser: amortises the Qdrant Cloud round trip


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


class JinaBackend:
    """jina-embeddings-v5-text-small: dense only, task-adapted, prompt-prefixed.

    The model ships LoRA adapters per task and separate query/document prompts;
    both are part of how it was trained, so omitting either would handicap it
    for reasons that have nothing to do with the corpus.
    """

    name = "jina"
    suffix = "jina"
    dim = JINA_DIM
    has_sparse = False
    # Fed in large chunks on purpose: sentence-transformers sorts a chunk by
    # length before batching, so padding waste collapses. Handing it 16 at a
    # time defeats that and costs most of the throughput (1.0 doc/s vs 9.1).
    chunk = 256

    def __init__(self):
        from sentence_transformers import SentenceTransformer
        print(f"[EMBED] Loading {JINA_MODEL}")
        self.model = SentenceTransformer(
            JINA_MODEL,
            trust_remote_code=True,
            model_kwargs={"torch_dtype": "bfloat16"},
        )
        self.model.max_seq_length = JINA_MAX_TOKENS

    def encode_documents(self, texts: list[str]):
        vecs = self.model.encode(
            texts,
            prompt_name="document",
            task="retrieval",
            batch_size=JINA_BATCH,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return vecs.tolist(), None


BACKENDS = {"bge": BgeBackend, "jina": JinaBackend}


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
        nonlocal pending, stored
        if pending:
            client.upsert(collection_name=collection, points=pending)
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
    ap.add_argument("--embedder", choices=sorted(BACKENDS), required=True)
    ap.add_argument("--suffix", default=None, help="Collection suffix (default: the backend's own)")
    ap.add_argument("--limit", type=int, default=0, help="Index only the first N of each kind")
    ap.add_argument("--entities-only", action="store_true")
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

    backend = BACKENDS[args.embedder]()
    suffix = args.suffix or backend.suffix
    client = make_client()

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
