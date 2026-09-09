from datetime import timedelta
from unittest.mock import patch
from uuid import uuid4

import pytest

from app.config import settings
from app.services.auth.jwt import create_access_token, decode_access_token


def test_create_and_decode_valid_access_token():
    user_id = uuid4()
    token = create_access_token(
        user_id=user_id,
        email="test@example.com",
        expires_delta=timedelta(minutes=15),
    )
    assert isinstance(token, str)

    payload = decode_access_token(token=token)
    assert payload is not None
    assert payload.get("sub") == str(user_id)
    assert payload.get("email") == "test@example.com"
    assert payload.get("exp") is not None


def test_decode_token_with_wrong_secret():
    user_id = uuid4()
    token = create_access_token(
        user_id=user_id,
        email="test@example.com",
    )

    with patch.object(settings, "jwt_secret_key", "different_secret_key_12345678901234567890"):
        payload = decode_access_token(token=token)
        assert payload is None


def test_decode_expired_token():
    user_id = uuid4()
    token = create_access_token(
        user_id=user_id,
        email="test@example.com",
        expires_delta=timedelta(seconds=-10),
    )

    payload = decode_access_token(token=token)
    assert payload is None


def test_decode_invalid_token_format():
    assert decode_access_token("not-a-valid-jwt") is None
    assert decode_access_token("") is None


@pytest.fixture(autouse=True)
def test_signing_key(monkeypatch):
    monkeypatch.setattr(settings, "jwt_secret_key", "test-secret-for-jwt-unit-tests-1234567890")
