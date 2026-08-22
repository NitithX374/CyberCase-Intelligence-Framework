"""
Qdrant Vector Retriever
==========================
Performs hybrid search (Dense + Sparse) over entity and relationship embeddings
using BGE-M3 and Qdrant's native RRF fusion.
"""

from dataclasses import dataclass
from typing import Optional, Sequence, Union

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Filter,
    FieldCondition,
    MatchValue,
    Prefetch,
    SparseVector,
    FusionQuery,
    Fusion,
)
from FlagEmbedding import BGEM3FlagModel

from ..config import (
    ATTACK_DOMAIN_FILTER,
    QDRANT_API_KEY,
    QDRANT_COLLECTION_ENTITIES,
    QDRANT_COLLECTION_RELATIONSHIPS,
    QDRANT_HOST,
    QDRANT_PORT,
    QDRANT_URL,
    EMBED_MODEL,
    USE_FP16,
    VECTOR_TOP_K,
    RRF_K,
    DENSE_WEIGHT,
    SPARSE_WEIGHT,
)


@dataclass
class VectorResult:
    """A single result from vector search."""

    document: str
    metadata: dict
    score: float
    stix_id: str


# How much a relationship hit is worth against an entity hit of the same rank
# when the two result lists are merged. An entity is the thing an incident
# question is usually asking about; a relationship is supporting context, so it
# enters the candidate pool but does not displace entities from the top. Stated
# as a constant because it is a policy choice - previously it was decided
# accidentally by score normalisation.
ENTITY_FUSION_WEIGHT = 1.0
RELATIONSHIP_FUSION_WEIGHT = 0.5


def _wanted_labels(
    node_label_filter: Optional[Union[str, Sequence[str]]],
) -> Optional[set[str]]:
    """Normalise the caller's label filter to a set, or None for "no filter"."""
    if not node_label_filter:
        return None
    if isinstance(node_label_filter, str):
        return {node_label_filter}
    labels = {str(label) for label in node_label_filter}
    return labels or None


class VectorRetriever:
    """Retrieves semantically similar ATT&CK documents from Qdrant using Hybrid Search."""

    def __init__(self, embed_model: Optional[BGEM3FlagModel] = None):
        if QDRANT_URL:
            print(f"[VECTOR] Using Qdrant Cloud at {QDRANT_URL}")
            self.client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        elif QDRANT_HOST:
            print(f"[VECTOR] Using local Qdrant at {QDRANT_HOST}:{QDRANT_PORT}")
            self.client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, api_key=QDRANT_API_KEY)
        else:
            print(f"[VECTOR] Using in-memory Qdrant (dev only)")
            self.client = QdrantClient(":memory:")

        if embed_model is None:
            print(f"[VECTOR] Loading {EMBED_MODEL}...")
            self.embed_model = BGEM3FlagModel(EMBED_MODEL, use_fp16=USE_FP16)
        else:
            self.embed_model = embed_model
            
        try:
            ent_count = self.client.count(QDRANT_COLLECTION_ENTITIES).count
            rel_count = self.client.count(QDRANT_COLLECTION_RELATIONSHIPS).count
            print(f"[VECTOR] Entity collection: {ent_count} docs")
            print(f"[VECTOR] Relationship collection: {rel_count} docs")
        except Exception as e:
            print(f"[VECTOR] Warning: Could not get collection counts ({e})")

    def _search_hybrid(self, collection_name: str, query: str, 
                       top_k: int, qdrant_filter: Optional[Filter] = None) -> list[VectorResult]:
        """Hybrid search: dense + sparse with RRF fusion natively in Qdrant."""
        
        # 1. Embed query (dense + sparse)
        query_output = self.embed_model.encode(
            [query], return_dense=True, return_sparse=True, return_colbert_vecs=False
        )
        dense_vec = query_output["dense_vecs"][0].tolist()
        sparse_dict = query_output["lexical_weights"][0]
        
        sparse_indices = [int(k) for k in sparse_dict.keys()]
        sparse_values = list(sparse_dict.values())
        
        # We handle empty sparse vectors gracefully just in case
        if not sparse_indices:
            sparse_indices = [0]
            sparse_values = [0.0]

        # 2. Execute Qdrant native hybrid search
        results = self.client.query_points(
            collection_name=collection_name,
            prefetch=[
                Prefetch(
                    query=dense_vec,
                    using="dense",
                    limit=max(top_k * 5, 50),
                    filter=qdrant_filter,
                ),
                Prefetch(
                    query=SparseVector(
                        indices=sparse_indices,
                        values=sparse_values,
                    ),
                    using="sparse",
                    limit=max(top_k * 5, 50),
                    filter=qdrant_filter,
                ),
            ],
            query=FusionQuery(
                fusion=Fusion.RRF,
            ),
            limit=top_k,
            with_payload=True,
        )

        # 3. Parse results
        parsed = []
        for point in results.points:
            payload = point.payload or {}
            
            # Weighted score approximation (since Qdrant abstracts RRF)
            # Actually, Qdrant returns a fused score, we'll just pass it through.
            
            parsed.append(
                VectorResult(
                    document=payload.get("document", ""),
                    metadata=payload,
                    score=point.score,
                    stix_id=payload.get("stix_id", str(point.id)),
                )
            )
            
        return parsed

    def search_entities(
        self,
        query: str,
        top_k: int = VECTOR_TOP_K,
        node_label_filter: Optional[Union[str, Sequence[str]]] = None,
    ) -> list[VectorResult]:
        """Search entity descriptions semantically.

        Restricts to ``ATTACK_DOMAIN_FILTER`` (e.g. enterprise) so mobile-only
        entities don't pollute enterprise incident analysis. We filter on the
        ``domain`` payload AFTER retrieval (over-fetch then trim) rather than via a
        Qdrant filter: the cloud collection has no payload index on ``domain``, and
        post-filtering avoids mutating shared infra (no index creation needed).

        ``node_label_filter`` takes one label or several — several is the useful
        case, since Technique and Subtechnique are separate labels and a caller
        that wants "techniques" almost always wants both. It is applied the same
        post-retrieval way as ``domain``, and for the same reason: the cloud
        collection carries no payload index, and Qdrant strict mode answers a
        filtered query on an unindexed key with 400 "Index required but not
        found". Over-fetching keeps that off shared infra.
        """
        wanted = _wanted_labels(node_label_filter)

        fetch_k = top_k
        if ATTACK_DOMAIN_FILTER:
            fetch_k *= 3
        if wanted:
            # Techniques and sub-techniques are ~37% of the entity collection,
            # so ask for roughly three times what we intend to keep.
            fetch_k *= 3

        results = self._search_hybrid(
            collection_name=QDRANT_COLLECTION_ENTITIES,
            query=query,
            top_k=fetch_k,
        )

        if ATTACK_DOMAIN_FILTER:
            results = [
                r
                for r in results
                if (r.metadata.get("domain") or "") == ATTACK_DOMAIN_FILTER
            ]
        if wanted:
            results = [r for r in results if r.metadata.get("node_label") in wanted]

        return results[:top_k]

    def search_relationships(
        self,
        query: str,
        top_k: int = VECTOR_TOP_K,
        edge_label_filter: Optional[str] = None,
    ) -> list[VectorResult]:
        """Search relationship descriptions semantically."""
        
        q_filter = None
        if edge_label_filter:
            q_filter = Filter(
                must=[
                    FieldCondition(
                        key="edge_label",
                        match=MatchValue(value=edge_label_filter)
                    )
                ]
            )

        return self._search_hybrid(
            collection_name=QDRANT_COLLECTION_RELATIONSHIPS,
            query=query,
            top_k=top_k,
            qdrant_filter=q_filter,
        )

    @staticmethod
    def _fuse_by_rank(results: list["VectorResult"], weight: float) -> None:
        """Replace each score with a weighted reciprocal rank, in place.

        Scores from the entity and relationship collections are not comparable:
        each is an RRF score computed over a different corpus, so their
        magnitudes say nothing about relative relevance.

        Min-max normalising each list separately - what this used to do - makes
        that worse rather than better. It pins the best item of EACH list to
        exactly 1.0 and the worst to 0.0, so a collection whose every hit is
        irrelevant still contributes an item scoring 1.0, tying with or beating
        a genuinely relevant hit from the other list. It also forces the lowest
        entity hit to 0.0 even when it was highly relevant. Measured effect: at
        top_k=20 only 7.9 of the 20 returned items were Technique/Subtechnique
        nodes, and six TRAM samples came back with no technique at all.

        Reciprocal rank keeps each list's own ordering, which is the only signal
        that is trustworthy, and makes the cross-collection trade-off an
        explicit weight rather than an artefact of normalisation.
        """
        for rank, result in enumerate(results, start=1):
            result.score = weight / (RRF_K + rank)

    def search_all(
        self,
        query: str,
        top_k: int = VECTOR_TOP_K,
        node_label_filter: Optional[Union[str, Sequence[str]]] = None,
    ) -> list[VectorResult]:
        """Search both entity and relationship collections.

        Entities receive the full top_k quota; relationships get half. The two
        lists are then merged by weighted reciprocal rank rather than by raw
        score - see _fuse_by_rank for why comparing the scores directly, or
        min-max normalising them, does not work.

        ``node_label_filter`` restricts the entity side to those node labels.
        Relationship points carry ``edge_label``, not ``node_label``, so asking
        for specific node labels also means skipping that collection — keeping
        them would silently readmit exactly what the caller filtered out.
        """
        entity_results = self.search_entities(
            query, top_k=top_k, node_label_filter=node_label_filter
        )
        if node_label_filter:
            # One list, already in order. Nothing to fuse.
            return entity_results[:top_k]

        rel_results = self.search_relationships(query, top_k=max(top_k // 2, 3))

        self._fuse_by_rank(entity_results, ENTITY_FUSION_WEIGHT)
        self._fuse_by_rank(rel_results, RELATIONSHIP_FUSION_WEIGHT)

        combined = entity_results + rel_results
        combined.sort(key=lambda r: r.score, reverse=True)
        return combined[:top_k]
