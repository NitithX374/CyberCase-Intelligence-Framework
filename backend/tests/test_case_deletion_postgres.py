import asyncio
from datetime import datetime, timezone
from uuid import uuid4

import httpx
from sqlalchemy import func, select

from app.config import settings
from app.database import get_db
from app.main import app
from app.models import (
    Case,
    CaseAnalysisResult,
    CaseClarification,
    CaseReport,
    CaseRun,
    ChatMessage,
    ChatThread,
    EvidenceSource,
)
from app.models.caseMaterials import CaseEvidenceSnapshot
from app.models.user import User
from app.services.auth.jwt import create_access_token
from app.services.case_materials import CaseMaterialsService
from app.services.cases import CaseService
from run_recovery_support import isolated_database


def test_delete_case_cascades_all_dependent_records_without_error(monkeypatch):
    async def exercise():
        async with isolated_database() as factory:
            owner_id = uuid4()
            case_id = uuid4()

            async with factory() as db:
                owner = User(
                    id=owner_id,
                    email="delete-test@example.com",
                    name="Delete Test User",
                    oauth_provider="test",
                    oauth_subject_id="delete-test-sub",
                )
                db.add(owner)
                case = Case(id=case_id, user_id=owner_id, title="Case to be deleted")
                db.add(case)
                thread = ChatThread(id=case_id, user_id=owner_id, title="Case to be deleted")
                db.add(thread)
                await db.commit()

            async with factory() as db, db.begin():
                source = await CaseMaterialsService(db).admitText(
                    case_id=case_id,
                    user_id=owner_id,
                    source_kind="narrative",
                    exact_text="The fraudulent invoice amounted to 50000 THB.",
                    provenance_json={"origin": "test"},
                )

            async with factory() as db:
                snapshot_id = uuid4()
                snapshot = CaseEvidenceSnapshot(
                    id=snapshot_id,
                    case_id=case_id,
                    evidence_revision=1,
                    format_version="v1",
                    manifest_json=[],
                    input_text="The fraudulent invoice amounted to 50000 THB.",
                    text_sha256="a" * 64,
                    manifest_sha256="b" * 64,
                )
                db.add(snapshot)
                await db.flush()

                run_id = uuid4()
                result_id = uuid4()
                run = CaseRun(
                    id=run_id,
                    case_id=case_id,
                    operation="analysis",
                    snapshot_id=snapshot_id,
                    idempotency_key="del-test-run-1",
                    request_fingerprint="f" * 64,
                    status="completed",
                )
                db.add(run)
                await db.flush()

                analysis_result = CaseAnalysisResult(
                    id=result_id,
                    case_id=case_id,
                    run_id=run_id,
                    snapshot_id=snapshot_id,
                    schema_version="case_analysis_trace_v1",
                    status="validated",
                    answer="## Case Overview\nFraudulent invoice detected.",
                    summary="Fraudulent invoice detected.",
                    trace_json={"claims": []},
                    execution_receipt_json={"calls": []},
                )
                db.add(analysis_result)

                msg = ChatMessage(
                    thread_id=case_id,
                    ordinal=1,
                    role="user",
                    content="Analyze this case",
                    message_kind="conversation",
                )
                db.add(msg)

                clarification = CaseClarification(
                    id=uuid4(),
                    case_id=case_id,
                    origin_analysis_result_id=result_id,
                    origin_snapshot_id=snapshot_id,
                    gap_key="test_gap",
                    gap_id="gap_1",
                    topic="Account Details",
                    question="Which account was used?",
                    state="pending",
                )
                db.add(clarification)

                report = CaseReport(
                    id=uuid4(),
                    case_id=case_id,
                    analysis_result_id=result_id,
                    evidence_snapshot_id=snapshot_id,
                    version_number=1,
                    idempotency_key="del-test-report-1",
                    source_snapshot_json={"text": "test"},
                    source_snapshot_hash="h" * 64,
                    prompt_version="v1",
                    provider="test",
                    model="test",
                    status="completed",
                    validation_status="validated",
                )
                db.add(report)
                await db.commit()

            # Verify all records exist prior to deletion
            async with factory() as db:
                assert await db.scalar(select(func.count()).select_from(Case)) == 1
                assert await db.scalar(select(func.count()).select_from(CaseRun)) == 1
                assert await db.scalar(select(func.count()).select_from(CaseAnalysisResult)) == 1
                assert await db.scalar(select(func.count()).select_from(CaseReport)) == 1
                assert await db.scalar(select(func.count()).select_from(CaseClarification)) == 1
                assert await db.scalar(select(func.count()).select_from(ChatMessage)) == 1
                assert await db.scalar(select(func.count()).select_from(CaseEvidenceSnapshot)) == 1

            # Delete case via service
            async with factory() as db:
                await CaseService(db).deleteCase(case_id, user_id=owner_id)

            # Verify complete cascade across all tables
            async with factory() as db:
                assert await db.scalar(select(func.count()).select_from(Case)) == 0
                assert await db.scalar(select(func.count()).select_from(CaseRun)) == 0
                assert await db.scalar(select(func.count()).select_from(CaseAnalysisResult)) == 0
                assert await db.scalar(select(func.count()).select_from(CaseReport)) == 0
                assert await db.scalar(select(func.count()).select_from(CaseClarification)) == 0
                assert await db.scalar(select(func.count()).select_from(ChatMessage)) == 0
                assert await db.scalar(select(func.count()).select_from(ChatThread)) == 0
                assert await db.scalar(select(func.count()).select_from(CaseEvidenceSnapshot)) == 0
                assert await db.scalar(select(func.count()).select_from(EvidenceSource)) == 0

    asyncio.run(exercise())


def test_delete_case_http_route_auth_and_status_codes(monkeypatch):
    async def exercise():
        async with isolated_database() as factory:
            async def database():
                async with factory() as db:
                    yield db

            owner_id = uuid4()
            case_id = uuid4()
            other_user_id = uuid4()

            async with factory() as db:
                owner = User(
                    id=owner_id,
                    email="route-owner@example.com",
                    name="Owner",
                    oauth_provider="test",
                    oauth_subject_id="route-owner",
                )
                db.add(owner)
                other_user = User(
                    id=other_user_id,
                    email="other@example.com",
                    name="Other",
                    oauth_provider="test",
                    oauth_subject_id="other-user",
                )
                db.add(other_user)
                case = Case(id=case_id, user_id=owner_id, title="Route Case")
                db.add(case)
                await db.commit()

            monkeypatch.setattr(settings, "jwt_secret_key", "case-deletion-test-secret-1234567890")
            owner_headers = {"Authorization": f"Bearer {create_access_token(owner_id, owner.email)}"}
            other_headers = {"Authorization": f"Bearer {create_access_token(other_user_id, 'other@example.com')}"}

            application = app.app
            original_overrides = dict(application.dependency_overrides)
            application.dependency_overrides[get_db] = database
            try:
                async with httpx.AsyncClient(
                    transport=httpx.ASGITransport(app=app), base_url="http://test"
                ) as client:
                    # Unauthenticated -> 401
                    resp = await client.delete(f"/api/v1/cases/{case_id}")
                    assert resp.status_code == 401

                    # Wrong user -> 404
                    resp = await client.delete(f"/api/v1/cases/{case_id}", headers=other_headers)
                    assert resp.status_code == 404

                    # Nonexistent case -> 404
                    resp = await client.delete(f"/api/v1/cases/{uuid4()}", headers=owner_headers)
                    assert resp.status_code == 404

                    # Authorized owner -> 204
                    resp = await client.delete(f"/api/v1/cases/{case_id}", headers=owner_headers)
                    assert resp.status_code == 204

                    # Subsequent get -> 404
                    resp = await client.get(f"/api/v1/cases/{case_id}", headers=owner_headers)
                    assert resp.status_code == 404
            finally:
                application.dependency_overrides = original_overrides

            async with factory() as db:
                assert await db.scalar(select(func.count()).select_from(Case)) == 0

    asyncio.run(exercise())
