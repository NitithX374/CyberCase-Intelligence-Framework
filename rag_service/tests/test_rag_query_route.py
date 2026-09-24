from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError
from RAG.legal_reference import LegalProvision, LegalReferenceResult
from routers import rag as rag_router
from schemas.rag import QueryResponse


class FakeRagAgent:
    def __init__(self) -> None:
        self.query_calls: list[tuple[str, bool]] = []
        self.retrieve_with_details_calls = 0

    def query(self, query: str, *, verbose: bool) -> SimpleNamespace:
        self.query_calls.append((query, verbose))
        return SimpleNamespace(
            answer="SENTINEL_THROWAWAY_ANSWER",
            context="retrieved MITRE context",
            graphrag_result={"sentinel": "raw retrieval"},
        )

    def retrieve_with_details(self, query: str) -> None:
        self.retrieve_with_details_calls += 1
        raise AssertionError(f"direct retrieval called for {query}")


def test_query_runs_full_agent_pipeline_without_exposing_generated_answer(
    monkeypatch,
) -> None:
    app = FastAPI()
    agent = FakeRagAgent()
    app.state.rag_agent = agent
    app.state.retrieval_contexts = {}
    legal_result = LegalReferenceResult(
        provisions=[LegalProvision(citation="Section 1", title="Example law")],
        provider="thanoy",
        query_sent="incident summary",
    )
    app.include_router(rag_router.router)
    builder_calls: list[tuple[object, str]] = []

    def build_table(result: object, answer: str, **_: object) -> list[object]:
        builder_calls.append((result, answer))
        return []

    monkeypatch.setattr(rag_router, "build_mitre_table", build_table)

    async def _legal_result(_req, _query):
        return legal_result

    monkeypatch.setattr(rag_router, "_legal_reference", _legal_result)

    response = TestClient(app).post("/query", json={"query": "incident summary"})

    assert response.status_code == 200
    assert agent.query_calls == [("incident summary", False)]
    assert agent.retrieve_with_details_calls == 0
    assert builder_calls == [({"sentinel": "raw retrieval"}, "SENTINEL_THROWAWAY_ANSWER")]

    payload = response.json()
    assert payload == {
        "status": "completed",
        "retrieval_context_id": payload["retrieval_context_id"],
        "context": "retrieved MITRE context",
        "mitre_table": [],
        "legal_reference": legal_result.model_dump(mode="json"),
    }
    assert payload["retrieval_context_id"]
    assert "SENTINEL_THROWAWAY_ANSWER" not in response.text

    with pytest.raises(ValidationError):
        QueryResponse.model_validate({**payload, "answer": "forbidden"})

    cached = app.state.retrieval_contexts[payload["retrieval_context_id"]]
    assert cached["context"] == "retrieved MITRE context"
    assert cached["rag_result"] == {"sentinel": "raw retrieval"}
    assert cached["mitre_table"] == []
    assert cached["legal_reference"] == legal_result
    assert "answer" not in cached

    snapshot = TestClient(app).get(f"/retrieval-contexts/{payload['retrieval_context_id']}")
    assert snapshot.status_code == 200
    assert snapshot.json()["legal_reference"] == legal_result.model_dump(mode="json")


def test_entity_lookup_is_skipped_for_an_agent_without_a_graph() -> None:
    assert rag_router._entity_details_lookup(FakeRagAgent()) is None


def test_degraded_legal_lookup_is_saved_with_retrieved_context(monkeypatch) -> None:
    app = FastAPI()
    app.state.rag_agent = FakeRagAgent()
    app.state.retrieval_contexts = {}
    app.include_router(rag_router.router)
    monkeypatch.setattr(rag_router, "build_mitre_table", lambda *_args, **_kwargs: [])

    response = TestClient(app).post("/query", json={"query": "incident summary"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["legal_reference"]["degraded"]
    snapshot = app.state.retrieval_contexts[payload["retrieval_context_id"]]
    assert snapshot["legal_reference"].degraded == payload["legal_reference"]["degraded"]


def test_entity_lookup_failure_costs_the_enrichment_not_the_request() -> None:
    class BrokenGraph:
        def entity_details(self, stix_ids: list[str]) -> dict:
            raise ConnectionError("neo4j unreachable")

    agent = SimpleNamespace(retriever=SimpleNamespace(graph_retriever=BrokenGraph()))
    lookup = rag_router._entity_details_lookup(agent)

    assert lookup is not None
    assert lookup(["attack-pattern--1"]) == {}
