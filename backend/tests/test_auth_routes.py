import pytest
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.config import settings
from app.database import get_db
from app.main import app
from app.models.user import User


def _fastapi_app() -> FastAPI:
    application = app
    while hasattr(application, "app") and not isinstance(application, FastAPI):
        application = application.app
    return application


@pytest.fixture
def mock_db():
    session = AsyncMock()
    return session


@pytest.fixture
def client(mock_db, monkeypatch):
    monkeypatch.setattr(settings, "jwt_secret_key", "test-secret-for-auth-routes-1234567890")
    fastapi_app = _fastapi_app()
    fastapi_app.dependency_overrides[get_db] = lambda: mock_db
    yield TestClient(app)
    fastapi_app.dependency_overrides.clear()


def test_session_unauthenticated(client):
    response = client.get("/api/v1/auth/session")
    assert response.status_code == 200
    assert response.json() is None


def test_me_unauthenticated_returns_401(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_dev_login_and_authenticated_session(client, mock_db, monkeypatch):
    monkeypatch.setattr(settings, "auth_dev_login_enabled", True)
    dev_user = User(
        id=uuid4(),
        email="dev@example.com",
        name="Dev User",
        avatar_url="https://example.com/avatar.png",
        oauth_provider="dev",
        oauth_subject_id="dev:dev@example.com",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    with patch(
        "app.routers.auth.get_or_create_dev_user",
        new_callable=AsyncMock,
    ) as mock_get_user:
        mock_get_user.return_value = dev_user

        # Perform dev login
        login_res = client.post(
            "/api/v1/auth/dev-login",
            json={"email": "dev@example.com", "name": "Dev User"},
        )
        assert login_res.status_code == 200
        token_data = login_res.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"
        assert token_data["user"]["email"] == "dev@example.com"

        token = token_data["access_token"]

        # Mock database lookup for user by ID
        exec_result = MagicMock()
        exec_result.scalar_one_or_none.return_value = dev_user
        mock_db.execute = AsyncMock(return_value=exec_result)

        # Test GET /api/v1/auth/me using Bearer token header
        me_res = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_res.status_code == 200
        assert me_res.json()["email"] == "dev@example.com"
        assert me_res.json()["name"] == "Dev User"

        # Test GET /api/v1/auth/session using session cookie
        session_res = client.get("/api/v1/auth/session")
        assert session_res.status_code == 200
        session_data = session_res.json()
        assert session_data is not None
        assert session_data["email"] == "dev@example.com"


def test_logout_clears_session(client, mock_db):
    logout_res = client.post("/api/v1/auth/logout")
    assert logout_res.status_code == 200
    assert logout_res.json()["message"] == "Logged out successfully"

    session_res = client.get("/api/v1/auth/session")
    assert session_res.status_code == 200
    assert session_res.json() is None


def test_oauth_login_redirect_google(client):
    with patch.object(settings, "oauth_google_client_id", "test-google-id"), \
         patch.object(settings, "oauth_google_client_secret", "test-secret"):
        res = client.get("/api/v1/auth/login/google", follow_redirects=False)
        assert res.status_code == 302
        assert "accounts.google.com" in res.headers["location"]
        assert "client_id=test-google-id" in res.headers["location"]


def test_oauth_login_unconfigured_provider(client):
    with patch.object(settings, "oauth_google_client_id", ""):
        res = client.get("/api/v1/auth/login/google")
        assert res.status_code == 400
        assert "not configured" in res.json()["detail"]
