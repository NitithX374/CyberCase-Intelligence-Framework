from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.analysis import routes as analysis
from app.auth.guard import get_current_user
from app.chat import routes as chat
from app.database import get_db
from app.errors import AppError, CaseAnalysisFailure, CaseWorkflowError
from app.main import app
from app.reports.contracts import ReportGenerationConflict, ReportNotFound
from app.sources.ingestion.contracts import (
    DocumentLimitError,
    InvalidDocumentError,
    UnsupportedDocumentError,
)
from app.sources.service import SourceError


def _fastapi_app() -> FastAPI:
    application = app
    while not isinstance(application, FastAPI):
        application = application.app
    return application


@pytest.fixture
def signed_in():
    db = AsyncMock()
    fastapi_app = _fastapi_app()
    fastapi_app.dependency_overrides[get_db] = lambda: db
    fastapi_app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=uuid4())
    yield TestClient(app), db
    fastapi_app.dependency_overrides.clear()


@pytest.mark.parametrize(
    ("error", "status_code"),
    [
        (CaseWorkflowError("case_sources_changed", "Changed"), 409),
        (CaseWorkflowError("case_not_found", "Case not found", 404), 404),
        (CaseAnalysisFailure("analysis_invalid", "Invalid"), 409),
        (CaseAnalysisFailure("chat_answer_timeout", "Timed out", 502), 502),
        (SourceError("source_text_empty", "Empty"), 422),
        (ReportGenerationConflict("case_analysis_missing", "Missing"), 409),
        (ReportNotFound("report_not_found", "Not found"), 404),
        (UnsupportedDocumentError("Only PDF"), 415),
        (DocumentLimitError("document_size_limit_exceeded", "Too large"), 413),
        (InvalidDocumentError("Broken"), 422),
    ],
)
def test_each_service_error_carries_its_status(error: AppError, status_code: int) -> None:
    assert isinstance(error, AppError)
    assert error.status_code == status_code


@pytest.mark.parametrize(
    ("router", "entry", "path", "body"),
    [
        (analysis, "run_case_analysis", "analysis", {}),
        (chat, "send_case_message", "chat/messages", {"content": "What happened?"}),
    ],
)
def test_an_analysis_failure_reaches_the_client_as_a_coded_conflict(
    signed_in, monkeypatch, router, entry, path, body
):
    client, _ = signed_in

    async def refuse(**_kwargs):
        raise CaseAnalysisFailure("analysis_invalid", "Analysis stage violated its schema")

    monkeypatch.setattr(router, entry, refuse)

    response = client.post(f"/api/v1/cases/{uuid4()}/{path}", json=body)

    assert response.status_code == 409
    assert response.json() == {
        "detail": {"code": "analysis_invalid", "message": "Analysis stage violated its schema"}
    }


def test_a_case_someone_else_owns_is_not_found_with_a_code(signed_in):
    client, db = signed_in
    db.scalar = AsyncMock(return_value=SimpleNamespace(user_id=uuid4()))

    response = client.get(f"/api/v1/cases/{uuid4()}")

    assert response.status_code == 404
    assert response.json() == {"detail": {"code": "case_not_found", "message": "Case not found"}}
