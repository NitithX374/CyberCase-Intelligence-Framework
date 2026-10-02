"""
Unit Tests for VectorRetriever.search_all
=========================================
One query, two collections, one embedding pass.
"""

import sys
from pathlib import Path
from types import SimpleNamespace

_APP_DIR = Path(__file__).resolve().parent.parent / "app"
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

from RAG.GraphRAG.retrieval import vector_retriever as vr_module
from RAG.GraphRAG.retrieval.vector_retriever import VectorRetriever


class _CountingEmbedder:
    def __init__(self):
        self.calls = []

    def encode(self, texts, **_kwargs):
        self.calls.append(list(texts))
        return {
            "dense_vecs": [SimpleNamespace(tolist=lambda: [0.1, 0.2])],
            "lexical_weights": [{"7": 0.5}],
        }


class _RecordingClient:
    def __init__(self):
        self.queries = []

    def query_points(self, collection_name, prefetch, query, limit, with_payload):
        self.queries.append((collection_name, prefetch[0].query, prefetch[1].query.indices))
        domain = {"domain": "enterprise"} if "entities" in collection_name else {}
        return SimpleNamespace(points=[
            SimpleNamespace(id=f"{collection_name}-{i}", score=1.0 - i / 10,
                            payload={"stix_id": f"{collection_name}-{i}", "document": "doc", **domain})
            for i in range(limit)
        ])


def _retriever():
    r = VectorRetriever.__new__(VectorRetriever)  # no model, no Qdrant
    r.embed_model = _CountingEmbedder()
    r.client = _RecordingClient()
    return r


def test_search_all_embeds_the_query_once(monkeypatch):
    monkeypatch.setattr(vr_module, "ATTACK_DOMAIN_FILTER", "enterprise")
    r = _retriever()

    results = r.search_all("ผู้โจมตีส่งอีเมล Phishing", top_k=10)

    assert r.embed_model.calls == [["ผู้โจมตีส่งอีเมล Phishing"]]
    # both collections were searched, with the same vectors
    assert [q[0] for q in r.client.queries] == [
        vr_module.QDRANT_COLLECTION_ENTITIES, vr_module.QDRANT_COLLECTION_RELATIONSHIPS]
    assert r.client.queries[0][1:] == r.client.queries[1][1:] == ([0.1, 0.2], [7])
    assert len(results) == 10


def test_a_single_collection_search_still_embeds_for_itself():
    r = _retriever()
    r.search_relationships("query", top_k=3)
    assert r.embed_model.calls == [["query"]]
