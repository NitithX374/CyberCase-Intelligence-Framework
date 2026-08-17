"""The three retrieval arms of the embedding-model comparison.

All three run the *same* search topology as the production retriever
(retrieval/vector_retriever.py): entities get the full top-K quota,
relationships get half, each collection is min-max normalised before the two
are merged, and the enterprise domain filter is applied post-retrieval. Only
the vector query itself differs:

  A  bge-m3-hybrid   dense + sparse prefetch, fused by Qdrant RRF
  B  bge-m3-dense    dense only  — same model, same collection, sparse removed
  C  e5-dense        dense only  — multilingual-e5-large, own collections

Holding the topology fixed is what makes B vs C a statement about the
embedding model rather than about the surrounding stack.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

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
    QDRANT_COLLECTION_ENTITIES,
    QDRANT_COLLECTION_RELATIONSHIPS,
    QDRANT_HOST,
    QDRANT_PORT,
    QDRANT_URL,
    USE_FP16,
    VECTOR_TOP_K,
)

# ── Arm C model/collection constants ─────────────────────────────────────────
E5_MODEL = "intfloat/multilingual-e5-large"
E5_EMBED_DIM = 1024
E5_COLLECTION_ENTITIES = "mitre_entities_e5"
E5_COLLECTION_RELATIONSHIPS = "mitre_relationships_e5"

# E5 was trained with these prefixes; omitting them costs several points of
# nDCG and would silently handicap arm C.
E5_QUERY_PREFIX = "query: "
E5_PASSAGE_PREFIX = "passage: "


def make_client() -> QdrantClient:
    if QDRANT_URL:
        return QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=120)
    if QDRANT_HOST:
        return QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, api_key=QDRANT_API_KEY, timeout=120)
    raise SystemExit("[ARMS] No QDRANT_URL/QDRANT_HOST configured")


def load_bge():
    from FlagEmbedding import BGEM3FlagModel
    print(f"[ARMS] Loading {EMBED_MODEL} (fp16={USE_FP16})...")
    return BGEM3FlagModel(EMBED_MODEL, use_fp16=USE_FP16)


def load_e5():
    from sentence_transformers import SentenceTransformer
    from ...config import DEVICE
    print(f"[ARMS] Loading {E5_MODEL} on {DEVICE} (fp16={USE_FP16})...")
    m = SentenceTransformer(E5_MODEL, device=DEVICE)
    if USE_FP16:
        m.half()
    return m


@dataclass
class Hit:
    stix_id: str
    score: float
    metadata: dict


class _ArmBase:
    """Shared search topology. Subclasses implement _query_collection only."""

    name = "base"
    label = "base"

    def __init__(self, client: Optional[QdrantClient] = None):
        self.client = client or make_client()

    # -- subclass hook --------------------------------------------------------
    def _query_collection(self, collection: str, query: str, top_k: int,
                          qdrant_filter: Optional[Filter]) -> list[Hit]:
        raise NotImplementedError

    # -- shared topology (mirrors retrieval/vector_retriever.py) --------------
    @staticmethod
    def _normalize(hits: list[Hit]) -> None:
        if len(hits) < 2:
            return
        scores = [h.score for h in hits]
        lo, hi = min(scores), max(scores)
        if hi == lo:
            return
        for h in hits:
            h.score = (h.score - lo) / (hi - lo)

    def search_entities(self, query: str, top_k: int) -> list[Hit]:
        fetch_k = top_k * 3 if ATTACK_DOMAIN_FILTER else top_k
        hits = self._query_collection(self.entities_collection, query, fetch_k, None)
        if ATTACK_DOMAIN_FILTER:
            hits = [h for h in hits
                    if (h.metadata.get("domain") or "") == ATTACK_DOMAIN_FILTER][:top_k]
        return hits

    def search_relationships(self, query: str, top_k: int) -> list[Hit]:
        return self._query_collection(self.relationships_collection, query, top_k, None)

    def search_all(self, query: str, top_k: int = VECTOR_TOP_K) -> list[Hit]:
        ents = self.search_entities(query, top_k=top_k)
        rels = self.search_relationships(query, top_k=max(top_k // 2, 3))
        self._normalize(ents)
        self._normalize(rels)
        combined = ents + rels
        combined.sort(key=lambda h: h.score, reverse=True)
        return combined[:top_k]

    def retrieve_ids(self, query: str, top_k: int = VECTOR_TOP_K) -> list[str]:
        return [h.stix_id for h in self.search_all(query, top_k=top_k)]

    @staticmethod
    def _parse(points) -> list[Hit]:
        out = []
        for p in points:
            payload = p.payload or {}
            out.append(Hit(
                stix_id=payload.get("stix_id", str(p.id)),
                score=p.score,
                metadata=payload,
            ))
        return out


class BgeHybridArm(_ArmBase):
    """Arm A — the deployed stack: BGE-M3 dense + sparse, Qdrant native RRF."""

    name = "A"
    label = "bge-m3 dense+sparse (RRF)"
    entities_collection = QDRANT_COLLECTION_ENTITIES
    relationships_collection = QDRANT_COLLECTION_RELATIONSHIPS

    def __init__(self, model, client=None):
        super().__init__(client)
        self.model = model

    def _encode(self, query: str):
        out = self.model.encode([query], return_dense=True, return_sparse=True,
                                return_colbert_vecs=False)
        dense = out["dense_vecs"][0].tolist()
        sparse = out["lexical_weights"][0]
        idx = [int(k) for k in sparse.keys()]
        val = list(sparse.values())
        if not idx:
            idx, val = [0], [0.0]
        return dense, idx, val

    def _query_collection(self, collection, query, top_k, qdrant_filter):
        dense, idx, val = self._encode(query)
        res = self.client.query_points(
            collection_name=collection,
            prefetch=[
                Prefetch(query=dense, using="dense",
                         limit=max(top_k * 5, 50), filter=qdrant_filter),
                Prefetch(query=SparseVector(indices=idx, values=val), using="sparse",
                         limit=max(top_k * 5, 50), filter=qdrant_filter),
            ],
            query=FusionQuery(fusion=Fusion.RRF),
            limit=top_k,
            with_payload=True,
        )
        return self._parse(res.points)


class BgeDenseArm(_ArmBase):
    """Arm B — BGE-M3 with the sparse component removed.

    Same model and same collection as arm A, so the delta A-B is exactly the
    contribution of lexical matching.
    """

    name = "B"
    label = "bge-m3 dense only"
    entities_collection = QDRANT_COLLECTION_ENTITIES
    relationships_collection = QDRANT_COLLECTION_RELATIONSHIPS

    def __init__(self, model, client=None):
        super().__init__(client)
        self.model = model

    def _query_collection(self, collection, query, top_k, qdrant_filter):
        out = self.model.encode([query], return_dense=True, return_sparse=False,
                                return_colbert_vecs=False)
        dense = out["dense_vecs"][0].tolist()
        res = self.client.query_points(
            collection_name=collection,
            query=dense,
            using="dense",
            limit=top_k,
            query_filter=qdrant_filter,
            with_payload=True,
        )
        return self._parse(res.points)


class E5DenseArm(_ArmBase):
    """Arm C — multilingual-e5-large, dense only (the model has no sparse head)."""

    name = "C"
    label = "multilingual-e5-large dense"
    entities_collection = E5_COLLECTION_ENTITIES
    relationships_collection = E5_COLLECTION_RELATIONSHIPS

    def __init__(self, model, client=None):
        super().__init__(client)
        self.model = model

    def _query_collection(self, collection, query, top_k, qdrant_filter):
        vec = self.model.encode(
            [E5_QUERY_PREFIX + query],
            normalize_embeddings=True,
            show_progress_bar=False,
        )[0].tolist()
        res = self.client.query_points(
            collection_name=collection,
            query=vec,
            using="dense",
            limit=top_k,
            query_filter=qdrant_filter,
            with_payload=True,
        )
        return self._parse(res.points)
