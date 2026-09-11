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
        res = client.get("/api/v1/auth/login/google?redirect=/case/test-123", follow_redirects=False)
        assert res.status_code == 302
        assert "accounts.google.com" in res.headers["location"]
        assert "client_id=test-google-id" in res.headers["location"]
        assert "oauth_state=" in res.headers.get("set-cookie", "")
        assert "oauth_redirect=" in res.headers.get("set-cookie", "")
        assert "/case/test-123" in res.headers.get("set-cookie", "")


def test_oauth_login_unconfigured_provider(client):
    with patch.object(settings, "oauth_google_client_id", ""):
        res = client.get("/api/v1/auth/login/google")
        assert res.status_code == 400
        assert "not configured" in res.json()["detail"]


def test_oauth_login_rejects_unsupported_provider(client):
    res = client.get("/api/v1/auth/login/github")
    assert res.status_code == 400
    assert "Unsupported OAuth provider" in res.json()["detail"]


def test_providers_endpoint(client):
    with patch.object(settings, "oauth_google_client_id", "id"), \
         patch.object(settings, "oauth_google_client_secret", "sec"):
        res = client.get("/api/v1/auth/providers")
        assert res.status_code == 200
        assert res.json() == ["google"]

    with patch.object(settings, "oauth_google_client_id", ""), \
         patch.object(settings, "oauth_google_client_secret", ""):
        res = client.get("/api/v1/auth/providers")
        assert res.status_code == 200
        assert res.json() == []


def test_oauth_callback_cancelled(client):
    res = client.get("/api/v1/auth/callback/google?error=access_denied", follow_redirects=False)
    assert res.status_code == 302
    assert res.headers["location"] == f"{settings.frontend_base_url}/login?error=cancelled"


def test_oauth_callback_invalid_state(client):
    client.cookies.set("oauth_state", "google:valid-state", path="/api/v1/auth")
    res = client.get("/api/v1/auth/callback/google?code=auth-code&state=wrong-state", follow_redirects=False)
    assert res.status_code == 400
    assert "Invalid OAuth state" in res.json()["detail"]


def test_oauth_callback_success(client, mock_db):
    from app.services.auth.oauthClients import OAuthUserProfile

    user = User(
        id=uuid4(),
        email="googler@example.com",
        name="Google User",
        avatar_url="https://example.com/avatar.jpg",
        oauth_provider="google",
        oauth_subject_id="google-sub-123",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    mock_profile = OAuthUserProfile(
        provider="google",
        subject_id="google-sub-123",
        email="googler@example.com",
        name="Google User",
        avatar_url="https://example.com/avatar.jpg",
    )

    with patch("app.routers.auth.get_oauth_client") as mock_get_client, \
         patch("app.routers.auth.get_or_create_oauth_user", new_callable=AsyncMock) as mock_create_user:
        mock_client = MagicMock()
        mock_client.exchange_code_for_profile = AsyncMock(return_value=mock_profile)
        mock_get_client.return_value = mock_client
        mock_create_user.return_value = user

        client.cookies.set("oauth_state", "google:state123", path="/api/v1/auth")
        client.cookies.set("oauth_redirect", "/case/abc-456", path="/api/v1/auth")

        res = client.get("/api/v1/auth/callback/google?code=code123&state=state123", follow_redirects=False)
        assert res.status_code == 302
        assert res.headers["location"] == f"{settings.frontend_base_url}/case/abc-456"
        assert settings.jwt_cookie_name in res.headers.get("set-cookie", "")
