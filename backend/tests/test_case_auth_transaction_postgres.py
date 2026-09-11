import asyncio
from uuid import UUID

import httpx
from sqlalchemy import func, select

from app.config import settings
from app.database import get_db
from app.main import app
from app.models import CaseRun, ChatMessage, EvidenceSource
from app.models.user import User
from app.routers import chat
from app.services.auth.jwt import create_access_token
from run_recovery_support import isolated_database


def test_authenticated_case_chat_write_commits_after_real_user_lookup(monkeypatch):
    async def no_op_dispatch(_run_id):
        return None

    monkeypatch.setattr(chat, "process_case_run", no_op_dispatch)

    async def exercise():
        async with isolated_database() as factory:
            async def database():
                async with factory() as db:
                    yield db

            async with factory() as db:
                owner = User(
                    email="native-chat-auth@example.com",
                    name="Native Chat Auth",
                    oauth_provider="test",
                    oauth_subject_id="native-chat-auth",
                )
                db.add(owner)
                await db.commit()

            monkeypatch.setattr(settings, "jwt_secret_key", "case-auth-transaction-test-secret-1234567890")
            headers = {"Authorization": f"Bearer {create_access_token(owner.id, owner.email)}"}
            application = app.app
            original_overrides = dict(application.dependency_overrides)
            application.dependency_overrides[get_db] = database
            try:
                async with httpx.AsyncClient(
                    transport=httpx.ASGITransport(app=app), base_url="http://test"
                ) as client:
                    created = await client.post(
                        "/api/v1/cases", json={"title": "Authenticated Case Chat"}, headers=headers
                    )
                    assert created.status_code == 201
                    case_id = UUID(created.json()["id"])
                    evidence = await client.post(
                        f"/api/v1/cases/{case_id}/evidence",
                        json={
                            "exact_text": "The witness reported a blue vehicle.",
                            "source_kind": "narrative",
                            "provenance_json": {"origin": "test"},
                        },
                        headers=headers,
                    )
                    assert evidence.status_code == 201
                    opened = await client.post(f"/api/v1/cases/{case_id}/chat", headers=headers)
                    assert opened.status_code == 200
                    accepted = await client.post(
                        f"/api/v1/chats/{case_id}/messages",
                        json={
                            "content": "The witness identified the vehicle as blue.",
                            "idempotency_key": "native-chat-auth-write",
                            "action": "add_case_info",
                        },
                        headers=headers,
                    )
                    assert accepted.status_code == 202
            finally:
                application.dependency_overrides = original_overrides

            async with factory() as db:
                assert await db.scalar(select(func.count()).select_from(ChatMessage)) == 1
                assert await db.scalar(select(func.count()).select_from(CaseRun)) == 1
                assert await db.scalar(select(func.count()).select_from(EvidenceSource)) == 2

    asyncio.run(exercise())
