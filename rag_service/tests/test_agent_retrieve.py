"""
Unit Tests for the retrieve node
================================
The incident is decomposed once per query, however many broaden rounds follow.
"""

import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent.parent / "app"
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

from RAG.GraphRAG.pipeline.agent_graph import GraphRAGAgent
from RAG.GraphRAG.retrieval.hybrid_retriever import GraphRAGResult


class _Decomposer:
    def __init__(self):
        self.calls = 0

    def decompose(self, incident, verbose=True):
        self.calls += 1
        return [f"sub {self.calls}a", f"sub {self.calls}b"]


class _Retriever:
    def __init__(self):
        self.channels = []

    def retrieve_multi_quota(self, queries, **_kwargs):
        self.channels.append(list(queries))
        return GraphRAGResult(vector_results=[], graph_results=[])


def _agent():
    agent = GraphRAGAgent.__new__(GraphRAGAgent)  # no models, no DB
    agent.decomposer = _Decomposer()
    agent.retriever = _Retriever()
    return agent


def test_a_broaden_round_reuses_the_first_decomposition():
    agent = _agent()
    state = {"original_query": "incident", "verbose": False, "broaden_count": 0, "rewritten_queries": []}

    first = agent._node_retrieve(state)
    state.update(first, broaden_count=1, rewritten_queries=["rewrite"])
    agent._node_retrieve(state)

    assert agent.decomposer.calls == 1
    assert first["sub_queries"] == ["sub 1a", "sub 1b"]
    assert agent.retriever.channels == [
        ["incident", "sub 1a", "sub 1b"],
        ["incident", "sub 1a", "sub 1b", "rewrite"],
    ]
