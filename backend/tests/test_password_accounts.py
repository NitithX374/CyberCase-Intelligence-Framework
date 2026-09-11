from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from app.config import settings
from app.database import get_db
from app.models.user import User
from app.routers import auth, chat, passwordAuth
from app.services.auth.passwords import hash_password, verify_password
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError


@pytest.fixture
def account_client(monkeypatch):
    monkeypatch.setattr(
        settings, "jwt_secret_key", "test-secret-for-account-tests-1234567890"
    )
    application = FastAPI()
    application.include_router(passwordAuth.router)
    application.include_router(auth.router)
    application.include_router(chat.router)
    db = AsyncMock()
    db.add = lambda user: None
    application.dependency_overrides[get_db] = lambda: db
    return TestClient(application), db


def user_record(verified=True):
    return User(
        id=uuid4(),
        email="analyst@example.com",
        name="Analyst",
        oauth_provider="password",
        oauth_subject_id="analyst@example.com",
        password_hash=hash_password("correct-password"),
        email_verified_at=datetime.now(timezone.utc) if verified else None,
        created_at=datetime.now(timezone.utc),
    )


def test_password_hash_salted_and_checked():
    first = hash_password("correct-password")
    assert first != hash_password("correct-password")
    assert verify_password("correct-password", first)
    assert not verify_password("wrong-password", first)


@pytest.mark.parametrize(
    "email,password", [("invalid", "correct-password"), ("a@example.com", "short")]
)
def test_registration_rejects_invalid_input(account_client, email, password):
    client, db = account_client
    assert (
        client.post(
            "/auth/register", json={"email": email, "password": password, "name": "A"}
        ).status_code
        == 422
    )
    db.commit.assert_not_called()


def test_registration_creates_session_without_email_verification(account_client):
    client, db = account_client
    saved = []
    db.add = saved.append
    db.refresh.side_effect = lambda user: setattr(user, "created_at", datetime.now(timezone.utc))
    result = client.post("/auth/register", json={
        "email": "Analyst@example.com", "password": "correct-password", "name": "A"
    })
    assert result.status_code == 201
    assert "HttpOnly" in result.headers["set-cookie"]
    assert result.json()["email"] == "analyst@example.com"
    assert saved[0].email_verified_at is None
    assert verify_password("correct-password", saved[0].password_hash)
    lookup = MagicMock()
    lookup.scalar_one_or_none.return_value = saved[0]
    db.execute.return_value = lookup
    session = client.get("/auth/me")
    assert session.status_code == 200
    assert session.json()["id"] == result.json()["id"]


def test_duplicate_registration_rolls_back_without_session(account_client):
    client, db = account_client
    db.commit.side_effect = IntegrityError("insert", {}, Exception("duplicate email"))
    result = client.post("/auth/register", json={
        "email": "analyst@example.com", "password": "correct-password", "name": "A"
    })
    assert result.status_code == 409
    assert "set-cookie" not in result.headers
    db.rollback.assert_awaited_once()


@pytest.mark.parametrize(
    "verified,password,status",
    [
        (True, "correct-password", 200),
        (False, "correct-password", 200),
        (True, "wrong", 401),
    ],
)
def test_login_requires_matching_credentials_without_verification(
    account_client, verified, password, status
):
    client, db = account_client
    db.scalar.return_value = user_record(verified)
    result = client.post(
        "/auth/login", json={"email": "analyst@example.com", "password": password}
    )
    assert result.status_code == status
    assert ("HttpOnly" in result.headers.get("set-cookie", "")) == (status == 200)


@pytest.mark.parametrize("path", ["/auth/verify-email", "/auth/resend-verification"])
def test_email_verification_endpoints_removed(account_client, path):
    client, _ = account_client
    assert client.post(path, json={"token": "a" * 32}).status_code == 404


def test_anonymous_chat_and_oauth_state_rejected(account_client):
    client, db = account_client
    assert client.get("/chats").status_code == 401
    assert client.post("/chats", json={"title": "Private"}).status_code == 401
    assert client.get("/auth/callback/google?code=bad&state=bad").status_code == 400
    db.commit.assert_not_called()


def test_anonymous_document_preview_is_rejected():
    from app.main import app

    result = TestClient(app).post(
        "/api/v1/document-ingestion/preview",
        files={"file": ("case.txt", b"private evidence", "text/plain")},
    )
    assert result.status_code == 401


def test_cross_origin_auth_request_is_rejected():
    from app.main import app

    result = TestClient(app).post(
        "/api/v1/auth/logout", headers={"Origin": "https://untrusted.example"}
    )
    assert result.status_code == 403
