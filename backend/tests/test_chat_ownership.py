from datetime import datetime, timezone
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app
from app.models.chat import ChatThread
from app.models.user import User
from app.schemas.chat import ChatThreadCreate, ChatThreadUpdate
from app.services.auth.dependencies import get_optional_user
from app.services.chat.chatService import ChatService


def _fastapi_app() -> FastAPI:
    application = app
    while hasattr(application, "app") and not isinstance(application, FastAPI):
        application = application.app
    return application


class ChatOwnershipServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_chat_service_create_thread_guest_and_user(self):
        db = AsyncMock()
        db.add = MagicMock()
        service = ChatService(db)

        # 1. Guest creation
        guest_thread = await service.create_thread(ChatThreadCreate(title="Guest Thread"))
        self.assertEqual(guest_thread.title, "Guest Thread")
        self.assertIsNone(guest_thread.user_id)
        db.add.assert_called_with(guest_thread)

        # 2. User creation
        user_id = uuid4()
        user_thread = await service.create_thread(
            ChatThreadCreate(title="User Thread"),
            user_id=user_id,
        )
        self.assertEqual(user_thread.title, "User Thread")
        self.assertEqual(user_thread.user_id, user_id)

    async def test_chat_service_access_verification(self):
        db = AsyncMock()
        db.add = MagicMock()
        service = ChatService(db)

        user_a = uuid4()
        user_b = uuid4()

        thread_a = ChatThread(id=uuid4(), title="User A Thread", user_id=user_a)
        guest_thread = ChatThread(id=uuid4(), title="Guest Thread", user_id=None)

        # User A accessing own thread -> OK
        service._verify_thread_access(thread_a, user_a)

        # User B accessing User A thread -> 404
        with self.assertRaises(HTTPException) as exc:
            service._verify_thread_access(thread_a, user_b)
        self.assertEqual(exc.exception.status_code, 404)

        # Guest accessing User A thread -> 404
        with self.assertRaises(HTTPException) as exc:
            service._verify_thread_access(thread_a, None)
        self.assertEqual(exc.exception.status_code, 404)

        # Guest accessing Guest thread -> OK
        service._verify_thread_access(guest_thread, None)

        # User A accessing Guest thread -> 404 (strict scoping)
        with self.assertRaises(HTTPException) as exc:
            service._verify_thread_access(guest_thread, user_a)
        self.assertEqual(exc.exception.status_code, 404)

    async def test_chat_service_update_and_delete_ownership(self):
        db = AsyncMock()
        db.add = MagicMock()
        service = ChatService(db)

        user_a = uuid4()
        user_b = uuid4()
        thread_id = uuid4()
        thread_a = ChatThread(id=thread_id, title="User A Thread", user_id=user_a)

        db.get = AsyncMock(return_value=thread_a)

        # User B cannot update User A's thread
        with self.assertRaises(HTTPException) as exc:
            await service.update_thread(
                thread_id,
                ChatThreadUpdate(title="Hacked Title"),
                user_id=user_b,
            )
        self.assertEqual(exc.exception.status_code, 404)

        # User A can update own thread
        updated = await service.update_thread(
            thread_id,
            ChatThreadUpdate(title="Updated Title"),
            user_id=user_a,
        )
        self.assertEqual(updated.title, "Updated Title")

        # User B cannot delete User A's thread
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = thread_a
        db.execute = AsyncMock(return_value=result_mock)

        with self.assertRaises(HTTPException) as exc:
            await service.delete_thread(thread_id, user_id=user_b)
        self.assertEqual(exc.exception.status_code, 404)


@pytest.fixture
def mock_db():
    session = AsyncMock()
    return session


@pytest.fixture
def client(mock_db):
    fastapi_app = _fastapi_app()
    fastapi_app.dependency_overrides[get_db] = lambda: mock_db
    yield TestClient(app)
    fastapi_app.dependency_overrides.clear()


def test_api_chat_thread_ownership_routes(client, mock_db):
    fastapi_app = _fastapi_app()
    user_a = User(
        id=uuid4(),
        email="a@example.com",
        name="User A",
        oauth_provider="dev",
        oauth_subject_id="a",
    )
    user_b = User(
        id=uuid4(),
        email="b@example.com",
        name="User B",
        oauth_provider="dev",
        oauth_subject_id="b",
    )

    thread_a = ChatThread(
        id=uuid4(),
        title="Thread A",
        user_id=user_a.id,
        status="idle",
        next_message_ordinal=1,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    # Scenario 1: User B tries to get User A's thread -> 404
    fastapi_app.dependency_overrides[get_optional_user] = lambda: user_b
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = thread_a
    mock_db.execute = AsyncMock(return_value=result_mock)

    res = client.get(f"/api/v1/chats/{thread_a.id}")
    assert res.status_code == 404

    # Scenario 2: Unauthenticated requests require login
    fastapi_app.dependency_overrides[get_optional_user] = lambda: None
    res = client.get(f"/api/v1/chats/{thread_a.id}")
    assert res.status_code == 401

    # Scenario 3: User A gets their own thread -> 200
    fastapi_app.dependency_overrides[get_optional_user] = lambda: user_a
    with patch(
        "app.services.chat.chatService.findRetryRequest",
        new_callable=AsyncMock,
    ) as mock_retry:
        mock_retry.return_value = None
        res = client.get(f"/api/v1/chats/{thread_a.id}")
        assert res.status_code == 200
        assert res.json()["title"] == "Thread A"
        assert res.json()["user_id"] == str(user_a.id)
