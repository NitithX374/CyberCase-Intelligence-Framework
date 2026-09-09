import asyncio
import os
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import httpx
import pytest
from app.config import settings
from app.database import engine
from app.routers import auth, chat, password_auth
from fastapi import FastAPI


@pytest.mark.skipif(
    not os.environ.get("POSTGRES_DB", "").startswith("cybercase_auth_verification_"),
    reason="Requires the disposable migrated account verification database",
)
def test_registered_accounts_persist_private_chats(monkeypatch):
    monkeypatch.setattr(settings, "jwt_secret_key", "integration-test-key-12345678901234567890")

    async def exercise():
        application = FastAPI()
        for router in (auth.router, password_auth.router, chat.router):
            application.include_router(router)
        transport = httpx.ASGITransport(app=application)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            email = f"analyst-{uuid4().hex}@example.com"
            credentials = {"email": email, "password": "correct-password"}
            response = await client.post("/auth/register", json={**credentials, "name": "Analyst"})
            assert response.status_code == 201, response.text
            assert (await client.get("/auth/me")).status_code == 200
            created = await client.post("/chats", json={"title": "Persisted private case"})
            assert created.status_code == 201, created.text
            thread_id = created.json()["id"]
            with patch("app.routers.chat.process_chat_run", new=AsyncMock()):
                accepted = await client.post(f"/chats/{thread_id}/messages", json={
                    "content": "Saved incident evidence", "idempotency_key": "persisted-evidence"
                })
            assert accepted.status_code == 202, accepted.text
            await client.post("/auth/logout")
            assert (await client.get(f"/chats/{thread_id}")).status_code == 401
            assert (await client.post("/auth/login", json=credentials)).status_code == 200
            detail = await client.get(f"/chats/{thread_id}")
            assert detail.status_code == 200, detail.text
            assert detail.json()["messages"][0]["content"] == "Saved incident evidence"
            await client.post("/auth/logout")
            response = await client.post("/auth/register", json={"email": f"other-{uuid4().hex}@example.com", "password": "correct-password", "name": "Other"})
            assert response.status_code == 201, response.text
            assert (await client.get("/chats")).json() == []
            for path in (f"/chats/{thread_id}", f"/chats/{thread_id}/reports"):
                assert (await client.get(path)).status_code == 404
        await engine.dispose()

    asyncio.run(exercise())
