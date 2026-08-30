"""POST /query must not block the event loop, so sessions run concurrently."""

import threading
import time
from types import SimpleNamespace

import anyio
import httpx
import pytest
from anyio import CapacityLimiter
from fastapi import FastAPI

from routers import rag as rag_router

QUERY_DURATION = 0.4  # seconds of simulated blocking pipeline work


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


class BlockingRagAgent:
    """Stands in for GraphRAGAgent: query() blocks the calling thread."""

    def __init__(self, duration: float = QUERY_DURATION) -> None:
        self.duration = duration
        self._lock = threading.Lock()
        self.in_flight = 0
        self.max_in_flight = 0
        self.seen_queries: list[str] = []

    def query(self, query: str, *, verbose: bool) -> SimpleNamespace:
        with self._lock:
            self.in_flight += 1
            self.max_in_flight = max(self.max_in_flight, self.in_flight)
            self.seen_queries.append(query)
        try:
            time.sleep(self.duration)  # blocking, exactly like the real pipeline
        finally:
            with self._lock:
                self.in_flight -= 1
        return SimpleNamespace(
            answer=f"answer for {query}",
            context=f"context for {query}",
            graphrag_result={"query": query},
        )


def _make_app(agent: BlockingRagAgent) -> FastAPI:
    app = FastAPI()
    app.state.rag_agent = agent
    app.state.retrieval_contexts = {}
    app.include_router(rag_router.router)
    return app


def _client(app: FastAPI) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://rag.test"
    )


@pytest.fixture(autouse=True)
def stub_mitre_table(monkeypatch) -> None:
    monkeypatch.setattr(rag_router, "build_mitre_table", lambda result, answer: [])


@pytest.mark.anyio
async def test_sessions_query_concurrently_and_keep_their_own_context() -> None:
    agent = BlockingRagAgent()
    app = _make_app(agent)
    sessions = ["session-a incident", "session-b incident", "session-c incident"]
    responses: dict[str, httpx.Response] = {}

    async with _client(app) as client:

        async def run(query: str) -> None:
            responses[query] = await client.post("/query", json={"query": query})

        started = time.monotonic()
        async with anyio.create_task_group() as tg:
            for query in sessions:
                tg.start_soon(run, query)
        elapsed = time.monotonic() - started

    assert agent.max_in_flight == 3, "sessions were serialized, not run in parallel"
    # Serialized execution would take 3x QUERY_DURATION.
    assert elapsed < QUERY_DURATION * 2
    assert sorted(agent.seen_queries) == sorted(sessions)

    context_ids = set()
    for query in sessions:
        response = responses[query]
        assert response.status_code == 200
        payload = response.json()
        # Each session gets its own answer, not another session's.
        assert payload["context"] == f"context for {query}"
        context_ids.add(payload["retrieval_context_id"])
    assert len(context_ids) == 3

    for query in sessions:
        context_id = responses[query].json()["retrieval_context_id"]
        assert app.state.retrieval_contexts[context_id]["query"] == query


@pytest.mark.anyio
async def test_event_loop_stays_responsive_while_a_query_runs() -> None:
    agent = BlockingRagAgent()
    app = _make_app(agent)

    async with _client(app) as client:
        async with anyio.create_task_group() as tg:
            tg.start_soon(
                lambda: client.post("/query", json={"query": "long incident"})
            )
            await anyio.sleep(QUERY_DURATION / 4)  # let the query get in flight
            assert agent.in_flight == 1

            started = time.monotonic()
            health = await client.get("/health")
            health_latency = time.monotonic() - started

    assert health.status_code == 200
    # A blocked event loop would hold /health until the query finished.
    assert health_latency < QUERY_DURATION / 4


@pytest.mark.anyio
async def test_capacity_limiter_caps_parallel_pipelines() -> None:
    agent = BlockingRagAgent(duration=0.15)
    app = _make_app(agent)
    app.state.query_limiter = CapacityLimiter(2)

    async with _client(app) as client:
        async with anyio.create_task_group() as tg:
            for index in range(5):
                tg.start_soon(
                    lambda i=index: client.post("/query", json={"query": f"case {i}"})
                )

    assert agent.max_in_flight == 2
    assert len(agent.seen_queries) == 5
