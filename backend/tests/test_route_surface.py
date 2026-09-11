import asyncio
import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app import main as main_module


def _fastapi_app() -> FastAPI:
    application = main_module.app
    while not isinstance(application, FastAPI):
        application = application.app
    return application


def test_health_chat_and_nested_report_api_routes_are_registered() -> None:
    openapi_paths = _fastapi_app().openapi()["paths"]
    api_routes = {
        (method.upper(), path)
        for path, operations in openapi_paths.items()
        if path.startswith("/api/")
        for method in operations
        if method not in {"parameters"}
    }

    assert api_routes == {
        ("GET", "/api/v1/health"),
        ("POST", "/api/v1/document-ingestion/preview"),
        ("GET", "/api/v1/auth/login/{provider}"),
        ("GET", "/api/v1/auth/callback/{provider}"),
        ("GET", "/api/v1/auth/me"),
        ("GET", "/api/v1/auth/providers"),
        ("POST", "/api/v1/auth/register"),
        ("POST", "/api/v1/auth/login"),
        ("GET", "/api/v1/auth/session"),
        ("POST", "/api/v1/auth/logout"),
        ("POST", "/api/v1/auth/dev-login"),
        ("GET", "/api/v1/cases"),
        ("POST", "/api/v1/cases"),
        ("GET", "/api/v1/cases/{case_id}"),
        ("PATCH", "/api/v1/cases/{case_id}"),
        ("DELETE", "/api/v1/cases/{case_id}"),
        ("GET", "/api/v1/cases/{case_id}/chat"),
        ("POST", "/api/v1/cases/{case_id}/chat"),
        ("POST", "/api/v1/cases/{case_id}/chat/messages"),
        ("GET", "/api/v1/cases/{case_id}/chat/runs/{run_id}"),
        ("GET", "/api/v1/cases/{case_id}/documents"),
        ("POST", "/api/v1/cases/{case_id}/documents"),
        ("POST", "/api/v1/cases/{case_id}/documents/{document_id}/admit"),
        ("GET", "/api/v1/cases/{case_id}/evidence"),
        ("POST", "/api/v1/cases/{case_id}/evidence"),
        ("POST", "/api/v1/cases/{case_id}/evidence/{source_id}/revisions"),
        ("POST", "/api/v1/cases/{case_id}/evidence/{source_id}/archive"),
        ("POST", "/api/v1/cases/{case_id}/evidence/snapshot"),
        ("GET", "/api/v1/cases/{case_id}/evidence/snapshots/{snapshot_id}"),
        ("GET", "/api/v1/cases/{case_id}/analysis"),
        ("POST", "/api/v1/cases/{case_id}/analysis"),
        ("GET", "/api/v1/cases/{case_id}/runs/{run_id}"),
        ("GET", "/api/v1/cases/{case_id}/clarifications"),
        ("POST", "/api/v1/cases/{case_id}/clarifications/{clarification_id}/answers"),
        ("GET", "/api/v1/chats"),
        ("POST", "/api/v1/chats"),
        ("GET", "/api/v1/chats/{thread_id}/case-link"),
        ("GET", "/api/v1/chats/{thread_id}"),
        ("PATCH", "/api/v1/chats/{thread_id}"),
        ("DELETE", "/api/v1/chats/{thread_id}"),
        ("POST", "/api/v1/chats/{thread_id}/messages"),
        ("GET", "/api/v1/chats/{thread_id}/runs/{run_id}"),
        ("POST", "/api/v1/chats/{thread_id}/reports"),
        ("GET", "/api/v1/chats/{thread_id}/reports"),
        ("GET", "/api/v1/chats/{thread_id}/reports/{report_id}"),
        ("GET", "/api/v1/chats/{thread_id}/reports/{report_id}/pdf"),
        ("POST", "/api/v1/cases/{case_id}/reports"),
        ("GET", "/api/v1/cases/{case_id}/reports"),
        ("GET", "/api/v1/cases/{case_id}/reports/{report_id}"),
        ("GET", "/api/v1/cases/{case_id}/reports/{report_id}/pdf"),
    }


def test_legacy_route_prefixes_return_not_found_without_startup() -> None:
    client = TestClient(main_module.app)

    for path in (
        "/api/v1/users",
        "/api/v1/rag",
        "/api/v1/reports",
    ):
        assert client.get(path).status_code == 404


def test_startup_fails_when_database_is_unavailable(
    monkeypatch,
) -> None:
    class _FailingConnection:
        async def __aenter__(self):
            raise OSError("database intentionally unavailable")

        async def __aexit__(self, exc_type, exc, traceback):
            return False

    class _FakeEngine:
        def __init__(self) -> None:
            self.disposed = False

        def connect(self) -> _FailingConnection:
            return _FailingConnection()

        async def dispose(self) -> None:
            self.disposed = True

    fake_engine = _FakeEngine()
    monkeypatch.setattr(main_module, "engine", fake_engine)

    async def exercise_lifespan() -> None:
        async with main_module.lifespan(_fastapi_app()):
            pass

    with pytest.raises(OSError, match="database intentionally unavailable"):
        asyncio.run(exercise_lifespan())

    assert fake_engine.disposed is True
