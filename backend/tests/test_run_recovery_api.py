import asyncio
from datetime import datetime, timedelta, timezone

import httpx

from app.config import settings
from app.database import get_db
from app.main import app
from app.models import Case, CaseAnalysisResult, CaseRun, User
from app.services.auth.jwt import create_access_token
from app.routers import case_analysis, cases
from app.services.case_analysis.contracts import (
    CaseAnalysisClaim,
    CaseAnalysisTrace,
    CaseSourceCitation,
)
from app.services.case_materials import CaseMaterialsService
from app.services.case_analysis.pipeline_config import configured_pipeline
from app.services.workflow.case_ask_completion import complete_case_ask
from app.services.workflow.case_run_claim import claim_case_run
from app.services.workflow.case_run_service import cleanup_abandoned_case_runs
from run_recovery_support import isolated_database


def test_interrupted_request_can_be_read_and_retried_through_http(monkeypatch):
    dispatched = []

    async def record_dispatch(run_id):
        dispatched.append(str(run_id))

    monkeypatch.setattr(case_analysis, "process_case_run", record_dispatch)

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
                    assert await cleanup_abandoned_case_runs(factory) == 1
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


def test_case_ask_creates_and_completes_a_case_run_through_http(monkeypatch):
    async def exercise():
        async with isolated_database() as factory:
            async def database():
                async with factory() as db:
                    yield db

            async with factory() as db, db.begin():
                owner = User(
                    email="ask@example.com",
                    name="ASK user",
                    oauth_provider="test",
                    oauth_subject_id="ask",
                )
                db.add(owner)
                await db.flush()
                case = Case(user_id=owner.id, title="Case ASK")
                db.add(case)
                await db.flush()
                source = await CaseMaterialsService(db).add_text_source(
                    case_id=case.id,
                    user_id=owner.id,
                    source_kind="narrative",
                    text="The witness reported a blue vehicle.",
                    provenance_json={"origin": "test"},
                )
                analysis_run = CaseRun(
                    case_id=case.id,
                    operation="analysis",
                    evidence_revision=case.evidence_revision,
                    idempotency_key="analysis-for-ask",
                    request_payload={"operation": "analysis"},
                    pipeline_config=configured_pipeline().model_dump(mode="json"),
                    status="completed",
                    attempt_count=1,
                )
                db.add(analysis_run)
                await db.flush()
                trace = CaseAnalysisTrace(
                    analysis_mode="case_overview",
                    summary="The witness reported a blue vehicle.",
                    claims=[
                        CaseAnalysisClaim(
                            claim_id="A-01",
                            claim_type="reported",
                            text="The witness reported a blue vehicle.",
                            epistemic_status="reported",
                            supporting_source_ids=[str(source.id)],
                            supporting_citations=[
                                CaseSourceCitation(
                                    source_id=str(source.id),
                                    exact_quote="The witness reported a blue vehicle.",
                                )
                            ],
                        )
                    ],
                )
                result = CaseAnalysisResult(
                    case_id=case.id,
                    run_id=analysis_run.id,
                    evidence_revision=case.evidence_revision,
                    schema_version=trace.version,
                    status="validated",
                    answer=trace.summary,
                    summary=trace.summary,
                    trace_json=trace.model_dump(mode="json"),
                    execution_receipt_json={"calls": []},
                    pipeline_config=configured_pipeline().model_dump(mode="json"),
                    external_context_json={},
                )
                db.add(result)
                await db.flush()
                case.latest_analysis_result_id = result.id

            async def complete_ask(run_id):
                async with factory() as db:
                    claimed = await claim_case_run(db, run_id)
                assert claimed is not None
                ask_trace = CaseAnalysisTrace(
                    analysis_mode="question_answer",
                    summary="The answer is grounded in the reported vehicle description.",
                    claims=[
                        CaseAnalysisClaim(
                            claim_id="A-01",
                            claim_type="reported",
                            text="The witness reported a blue vehicle.",
                            epistemic_status="reported",
                            supporting_source_ids=[str(source.id)],
                            supporting_citations=[
                                CaseSourceCitation(
                                    source_id=str(source.id),
                                    exact_quote="The witness reported a blue vehicle.",
                                )
                            ],
                        )
                    ],
                )
                from app.services.case_analysis.contracts import CaseAnalysisOutput as AnalysisOutput

                async with factory() as db:
                    assert await complete_case_ask(
                        db,
                        run_id,
                        claimed.attempt_count,
                        AnalysisOutput(
                            answer="The answer is grounded in the reported vehicle description.",
                            trace=ask_trace,
                        ),
                    )

            monkeypatch.setattr(cases, "process_case_run", complete_ask)
            monkeypatch.setattr(settings, "jwt_secret_key", "test-secret-for-case-auth-1234567890")
            headers = {"Authorization": f"Bearer {create_access_token(owner.id, owner.email)}"}
            application = app.app
            original_overrides = dict(application.dependency_overrides)
            application.dependency_overrides[get_db] = database
            try:
                async with httpx.AsyncClient(
                    transport=httpx.ASGITransport(app=app), base_url="http://test"
                ) as client:
                    response = await client.post(
                        f"/api/v1/cases/{case.id}/chat/messages",
                        json={
                            "content": "What vehicle was reported?",
                            "idempotency_key": "ask-message",
                            "intent": "ask",
                            "response_language": "english",
                        },
                        headers=headers,
                    )
                    assert response.status_code == 202
                    payload = response.json()
                    assert payload["message"]["message_kind"] == "conversation"
                    assert payload["run"]["operation"] == "ask"

                    chat = await client.get(
                        f"/api/v1/cases/{case.id}/chat",
                        headers=headers,
                    )
                    assert chat.status_code == 200
                    assert chat.json()["messages"][-1]["content"] == (
                        "The answer is grounded in the reported vehicle description."
                    )
            finally:
                application.dependency_overrides = original_overrides

    asyncio.run(exercise())
