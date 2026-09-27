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


def test_health_case_and_nested_report_api_routes_are_registered() -> None:
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
        ("POST", "/api/v1/auth/register"),
        ("POST", "/api/v1/auth/login"),
        ("GET", "/api/v1/auth/session"),
        ("POST", "/api/v1/auth/logout"),
        ("GET", "/api/v1/cases"),
        ("POST", "/api/v1/cases"),
        ("GET", "/api/v1/cases/{case_id}"),
        ("PATCH", "/api/v1/cases/{case_id}"),
        ("DELETE", "/api/v1/cases/{case_id}"),
        ("GET", "/api/v1/cases/{case_id}/chat"),
        ("POST", "/api/v1/cases/{case_id}/chat/messages"),
        ("POST", "/api/v1/cases/{case_id}/documents"),
        ("GET", "/api/v1/cases/{case_id}/documents/{document_id}/content"),
        ("GET", "/api/v1/cases/{case_id}/sources"),
        ("POST", "/api/v1/cases/{case_id}/sources"),
        ("GET", "/api/v1/cases/{case_id}/analysis"),
        ("POST", "/api/v1/cases/{case_id}/analysis"),
        ("POST", "/api/v1/cases/{case_id}/reports"),
        ("GET", "/api/v1/cases/{case_id}/reports"),
        ("GET", "/api/v1/cases/{case_id}/reports/{report_id}/pdf"),
        ("GET", "/api/v1/cases/{case_id}/reports/{report_id}/html"),
    }


def test_the_backend_decides_the_language_and_sends_no_derived_case_status() -> None:
    openapi = _fastapi_app().openapi()
    schemas = openapi["components"]["schemas"]

    assert "requestBody" not in openapi["paths"]["/api/v1/cases/{case_id}/analysis"]["post"]
    assert "CaseAnalysisCreate" not in schemas
    assert "response_language" not in schemas["ChatMessageCreate"]["properties"]
    assert "status" not in schemas["CaseRead"]["properties"]
    assert "status" not in schemas["CaseChatRead"]["properties"]


def test_documents_are_listed_through_their_sources() -> None:
    documents = _fastapi_app().openapi()["paths"]["/api/v1/cases/{case_id}/documents"]
    source = _fastapi_app().openapi()["components"]["schemas"]["CaseSourceRead"]

    assert set(documents) == {"post"}
    assert {"filename", "mime_type", "size_bytes"} <= set(source["properties"])


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
