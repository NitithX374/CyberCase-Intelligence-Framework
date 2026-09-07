import asyncio
from datetime import datetime, timedelta, timezone

import httpx

from app.database import get_db
from app.main import app
from app.models import ChatRun
from app.routers import chat
from app.services.workflow.run_recovery import recover_expired_runs
from run_recovery_support import isolated_database


def test_interrupted_request_can_be_read_and_retried_through_http(monkeypatch):
    dispatched = []

    async def record_dispatch(run_id):
        dispatched.append(str(run_id))

    monkeypatch.setattr(chat, "process_chat_run", record_dispatch)

    async def exercise():
        async with isolated_database() as factory:

            async def database():
                async with factory() as db:
                    yield db

            application = app.app
            original_overrides = dict(application.dependency_overrides)
            application.dependency_overrides[get_db] = database
            try:
                async with httpx.AsyncClient(
                    transport=httpx.ASGITransport(app=app), base_url="http://test"
                ) as client:
                    created = await client.post(
                        "/api/v1/chats", json={"title": "HTTP recovery"}
                    )
                    assert created.status_code == 201
                    thread_id = created.json()["id"]
                    payload = {
                        "content": "Reported theft",
                        "idempotency_key": "http-request",
                    }
                    accepted = await client.post(
                        f"/api/v1/chats/{thread_id}/messages", json=payload
                    )
                    assert accepted.status_code == 202
                    receipt = accepted.json()
                    async with factory() as db, db.begin():
                        from uuid import UUID

                        run = await db.get(ChatRun, UUID(receipt["run"]["id"]))
                        run.updated_at = datetime.now(timezone.utc) - timedelta(
                            minutes=7
                        )
                    assert await recover_expired_runs(factory) == 1
                    detail = (await client.get(f"/api/v1/chats/{thread_id}")).json()
                    assert detail["status"] == "failed"
                    assert detail["retry_request"]["idempotency_key"] == "http-request"
                    assert detail["retry_request"]["document_sources"] == []
                    retried = await client.post(
                        f"/api/v1/chats/{thread_id}/messages", json=payload
                    )
                    assert retried.status_code == 202
                    assert retried.json()["run"]["id"] == receipt["run"]["id"]
                    assert retried.json()["message"]["id"] == receipt["message"]["id"]
                    assert retried.json()["run"]["status"] == "queued"
                    assert dispatched == [receipt["run"]["id"]] * 2
            finally:
                application.dependency_overrides = original_overrides

    asyncio.run(exercise())
