"""Re-embed the ATT&CK corpus with multilingual-e5-large into its own Qdrant
collections, so arm C can be compared against the BGE-M3 arms.

Query and passage vectors must come from the same model, so the E5 arm cannot
reuse the BGE-M3 collections — the vectors live in different spaces.

Everything except the embedding model is held identical to
ingestion/vector_loader.py: same source bundles, same document text, same point
ids, same payload. E5 differs only where it must:
  - dense only (E5 has no lexical/sparse head), so the collection carries a
    single "dense" vector and no sparse config
  - "passage: " prefix on documents ("query: " at search time) — E5 was trained
    with these and scores markedly worse without them
  - 512-token window (the model's max_seq_length), vs 8192 for BGE-M3

Upserts are batched more coarsely than embedding (UPSERT_BATCH vs EMBED_BATCH)
because each upsert is a ~200 ms round trip to Qdrant Cloud; this only affects
how long ingestion takes, never what is stored or how it is searched.

Usage (from rag_service/app):
    python -m RAG.GraphRAG.evaluation.embed_ab.ingest_e5
    python -m RAG.GraphRAG.evaluation.embed_ab.ingest_e5 --dry-run
"""

from __future__ import annotations

import argparse
import sys
import time

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from ...config import (
    QDRANT_API_KEY,
    QDRANT_HOST,
    QDRANT_PORT,
    QDRANT_URL,
    sep,
)
from ...ingestion.vector_loader import uuid_from_stix_id
from .arms import (
    E5_COLLECTION_ENTITIES,
    E5_COLLECTION_RELATIONSHIPS,
    E5_EMBED_DIM,
    E5_MODEL,
    E5_PASSAGE_PREFIX,
    load_e5,
)

EMBED_BATCH = 16       # matches vector_loader.py so GPU behaviour is comparable
UPSERT_BATCH = 256     # coarser than embedding: amortises Qdrant Cloud RTT


def _client() -> QdrantClient:
    if QDRANT_URL:
        print(f"[QDRANT] Connecting to cloud: {QDRANT_URL}")
        return QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=120)
    if QDRANT_HOST:
        print(f"[QDRANT] Connecting to {QDRANT_HOST}:{QDRANT_PORT}")
        return QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, api_key=QDRANT_API_KEY, timeout=120)
    raise SystemExit("[QDRANT] No QDRANT_URL/QDRANT_HOST configured — refusing to build an in-memory corpus")


def _init_collection(client: QdrantClient, name: str) -> None:
    """Dense-only collection. Recreated from scratch so a partial earlier run
    can never leave stale points behind."""
    if client.collection_exists(name):
        print(f"[QDRANT] Dropping existing {name}")
        client.delete_collection(name)
    client.create_collection(
        collection_name=name,
        vectors_config={"dense": VectorParams(size=E5_EMBED_DIM, distance=Distance.COSINE)},
    )
    print(f"[QDRANT] Created {name} (dense {E5_EMBED_DIM}, cosine)")


def _entity_docs(entities) -> tuple[list[str], list[str], list[dict]]:
    """Identical text/payload construction to VectorLoader.load_entities."""
    ids, docs, metas = [], [], []
    for e in entities:
        if not e.description:
            continue
        text = f"{e.node_label}: {e.name}. {e.description}"[:8000]
        ids.append(e.stix_id)
        docs.append(text)
        metas.append({
            "stix_id": e.stix_id,
            "attack_id": e.attack_id,
            "entity_type": "Node",
            "node_label": e.node_label,
            "name": e.name,
            "domain": e.domain,
            "url": e.url,
            "document": text,
        })
    return ids, docs, metas


def _relationship_docs(relationships) -> tuple[list[str], list[str], list[dict]]:
    """Identical text/payload construction to VectorLoader.load_relationships."""
    ids, docs, metas = [], [], []
    for r in relationships:
        if not r.description:
            continue
        text = f"{r.source_name} {r.edge_label} {r.target_name}: {r.description}"[:8000]
        ids.append(r.stix_id)
        docs.append(text)
        metas.append({
            "stix_id": r.stix_id,
            "entity_type": "Relationship",
            "edge_label": r.edge_label,
            "source_id": r.source_ref,
            "target_id": r.target_ref,
            "source_name": r.source_name,
            "target_name": r.target_name,
            "document": text,
        })
    return ids, docs, metas


def _load(client, model, collection: str, ids, docs, metas, label: str) -> int:
    if not docs:
        print(f"[QDRANT] No {label} to embed")
        return 0

    _init_collection(client, collection)
    print(f"[QDRANT] Embedding {len(docs)} {label} documents with {E5_MODEL}...")

    started = time.perf_counter()
    pending: list[PointStruct] = []
    done = 0

    for i in range(0, len(docs), EMBED_BATCH):
        batch_docs = docs[i : i + EMBED_BATCH]
        vecs = model.encode(
            [E5_PASSAGE_PREFIX + d for d in batch_docs],
            batch_size=EMBED_BATCH,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        for j, vec in enumerate(vecs):
            pending.append(PointStruct(
                id=uuid_from_stix_id(ids[i + j]),
                vector={"dense": vec.tolist()},
                payload=metas[i + j],
            ))

        if len(pending) >= UPSERT_BATCH:
            client.upsert(collection_name=collection, points=pending)
            done += len(pending)
            pending = []
            elapsed = time.perf_counter() - started
            rate = done / elapsed if elapsed else 0
            eta = (len(docs) - done) / rate if rate else 0
            print(f"        {done}/{len(docs)} {label}  "
                  f"({rate:.0f} docs/s, ETA {eta/60:.1f} min)", flush=True)

    if pending:
        client.upsert(collection_name=collection, points=pending)
        done += len(pending)

    took = time.perf_counter() - started
    print(f"[QDRANT] Stored {done} {label} embeddings in {took/60:.1f} min")
    return done


def main() -> None:
    ap = argparse.ArgumentParser(description="Re-embed ATT&CK corpus with multilingual-e5-large")
    ap.add_argument("--dry-run", action="store_true",
                    help="Parse and report document counts, but do not touch Qdrant")
    args = ap.parse_args()

    sep("STIX PARSING")
    from ...ingestion.stix_parser import parse_all_domains
    parser = parse_all_domains()

    ent_ids, ent_docs, ent_metas = _entity_docs(parser.entities)
    rel_ids, rel_docs, rel_metas = _relationship_docs(parser.relationships)
    print(f"\n[PARSE] {len(ent_docs)} entity docs, {len(rel_docs)} relationship docs "
          f"({len(ent_docs) + len(rel_docs)} total)")

    if args.dry_run:
        print("[DRY-RUN] Stopping before any Qdrant write")
        return

    sep(f"EMBEDDING WITH {E5_MODEL}")
    model = load_e5()
    print(f"[EMBED] max_seq_length={model.max_seq_length}")

    client = _client()
    n_ent = _load(client, model, E5_COLLECTION_ENTITIES, ent_ids, ent_docs, ent_metas, "entities")
    n_rel = _load(client, model, E5_COLLECTION_RELATIONSHIPS, rel_ids, rel_docs, rel_metas, "relationships")

    sep("E5 INGESTION COMPLETE")
    print(f"  {E5_COLLECTION_ENTITIES}: {n_ent}")
    print(f"  {E5_COLLECTION_RELATIONSHIPS}: {n_rel}")
    print(f"  total: {n_ent + n_rel}")


if __name__ == "__main__":
    sys.exit(main())
