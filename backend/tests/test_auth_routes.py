from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from app.config import settings
from app.database import get_db
from app.main import app
from app.models.user import User
from app.services.auth.credentials import create_access_token, hash_password


def _fastapi_app() -> FastAPI:
    application = app
    while hasattr(application, "app") and not isinstance(application, FastAPI):
        application = application.app
    return application


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def client(mock_db, monkeypatch):
    monkeypatch.setattr(settings, "jwt_secret_key", "test-secret-for-auth-routes-1234567890")
    fastapi_app = _fastapi_app()
    fastapi_app.dependency_overrides[get_db] = lambda: mock_db
    yield TestClient(app)
    fastapi_app.dependency_overrides.clear()


def analyst(password_hash: str | None = None) -> User:
    return User(
        id=uuid4(),
        email="analyst@example.com",
        name="Analyst",
        password_hash=password_hash,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


def test_session_unauthenticated(client):
    response = client.get("/api/v1/auth/session")
    assert response.status_code == 200
    assert response.json() is None


def test_a_session_cookie_names_the_signed_in_user_and_ends_the_lookup(client, mock_db):
    user = analyst()
    mock_db.scalar = AsyncMock(return_value=user)
    client.cookies.set(settings.jwt_cookie_name, create_access_token(user.id, user.email))

    response = client.get("/api/v1/auth/session")

    assert response.status_code == 200
    assert response.json()["email"] == "analyst@example.com"
    assert "oauth_provider" not in response.json()
    mock_db.commit.assert_awaited_once()


def test_a_bearer_header_is_not_a_session(client, mock_db):
    user = analyst()
    mock_db.scalar = AsyncMock(return_value=user)

    response = client.get(
        "/api/v1/auth/session",
        headers={"Authorization": f"Bearer {create_access_token(user.id, user.email)}"},
    )

    assert response.status_code == 200
    assert response.json() is None


def test_login_sets_the_session_cookie(client, mock_db):
    user = analyst(hash_password("correct horse"))
    mock_db.scalar = AsyncMock(return_value=user)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "Analyst@Example.com", "password": "correct horse"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Analyst"
    assert settings.jwt_cookie_name in response.cookies


def test_a_wrong_password_is_refused_with_a_code(client, mock_db):
    mock_db.scalar = AsyncMock(return_value=analyst(hash_password("correct horse")))

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "analyst@example.com", "password": "wrong horse"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == {
        "code": "credentials_invalid",
        "message": "Incorrect email or password",
    }


def test_register_stores_a_lowercased_email_and_starts_a_session(client, mock_db):
    added: list[User] = []
    mock_db.add = MagicMock(side_effect=added.append)

    async def refresh(user: User) -> None:
        user.id = uuid4()
        user.created_at = datetime.now(UTC)

    mock_db.refresh = AsyncMock(side_effect=refresh)

    response = client.post(
        "/api/v1/auth/register",
        json={"email": "Analyst@Example.com", "name": "  Analyst ", "password": "correct horse"},
    )

    assert response.status_code == 201
    assert (added[0].email, added[0].name) == ("analyst@example.com", "Analyst")
    assert settings.jwt_cookie_name in response.cookies


class UniqueViolation(Exception):
    sqlstate = "23505"


def test_registering_a_taken_email_is_refused_with_a_code(client, mock_db):
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock(side_effect=IntegrityError("INSERT", {}, UniqueViolation("taken")))

    response = client.post(
        "/api/v1/auth/register",
        json={"email": "analyst@example.com", "name": "Analyst", "password": "correct horse"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == {
        "code": "account_exists",
        "message": "An account already exists for this email",
    }
    mock_db.rollback.assert_awaited_once()


def test_logout_clears_session(client, mock_db):
    logout_res = client.post("/api/v1/auth/logout")
    assert logout_res.status_code == 200
    assert logout_res.json()["message"] == "Logged out successfully"

    session_res = client.get("/api/v1/auth/session")
    assert session_res.status_code == 200
    assert session_res.json() is None
