import asyncio
from datetime import datetime, timedelta, timezone

import httpx

from app.config import settings
from app.database import get_db
from app.main import app
from app.models import CaseRun
from app.models.user import User
from app.services.auth.jwt import create_access_token
from app.routers import caseAnalysis
from app.services.workflow.caseRunService import cleanupAbandonedCaseRuns
from run_recovery_support import isolated_database


def test_interrupted_request_can_be_read_and_retried_through_http(monkeypatch):
    dispatched = []

    async def record_dispatch(run_id):
        dispatched.append(str(run_id))

    monkeypatch.setattr(caseAnalysis, "process_case_run", record_dispatch)

    async def exercise():
        async with isolated_database() as factory:

            async def database():
                async with factory() as db:
                    yield db

            async with factory() as db:
                owner = User(email="recovery@example.com", name="Recovery", oauth_provider="test", oauth_subject_id="recovery")
                db.add(owner)
                await db.commit()
            monkeypatch.setattr(settings, "jwt_secret_key", "test-secret-for-case-auth-1234567890")
            headers = {"Authorization": f"Bearer {create_access_token(owner.id, owner.email)}"}
            application = app.app
            original_overrides = dict(application.dependency_overrides)
            application.dependency_overrides[get_db] = database
            try:
                async with httpx.AsyncClient(
                    transport=httpx.ASGITransport(app=app), base_url="http://test"
                ) as client:
                    created = await client.post("/api/v1/cases", json={"title": "HTTP recovery"}, headers=headers)
                    assert created.status_code == 201
                    case_id = created.json()["id"]
                    evidence = await client.post(
                        f"/api/v1/cases/{case_id}/evidence",
                        json={
                            "exact_text": "Reported theft",
                            "source_kind": "narrative",
                            "provenance_json": {"origin": "test"},
                        },
                        headers=headers,
                    )
                    assert evidence.status_code == 201
                    payload = {"idempotency_key": "http-request", "response_language": "english"}
                    accepted = await client.post(
                        f"/api/v1/cases/{case_id}/analysis", json=payload, headers=headers
                    )
                    assert accepted.status_code == 202
                    receipt = accepted.json()
                    async with factory() as db, db.begin():
                        from uuid import UUID

                        run = await db.get(CaseRun, UUID(receipt["run"]["id"]))
                        run.updated_at = datetime.now(timezone.utc) - timedelta(
                            minutes=7
                        )
                    assert await cleanupAbandonedCaseRuns(factory) == 1
                    detail = (await client.get(f"/api/v1/cases/{case_id}/runs/{receipt['run']['id']}", headers=headers)).json()
                    assert detail["status"] == "failed"
                    assert detail["error_code"] == "case_run_interrupted"
                    retried = await client.post(f"/api/v1/cases/{case_id}/analysis", json=payload, headers=headers)
                    assert retried.status_code == 202
                    assert retried.json()["run"]["id"] == receipt["run"]["id"]
                    assert retried.json()["run"]["status"] == "queued"
                    assert dispatched == [receipt["run"]["id"]] * 2
            finally:
                application.dependency_overrides = original_overrides

    asyncio.run(exercise())
