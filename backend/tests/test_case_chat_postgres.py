import asyncio
from unittest.mock import Mock

import httpx
import pytest
from sqlalchemy import func, select

from app.config import settings
from app.database import get_db
from app.main import app
from app.models import Case, CaseAnalysisResult, CaseRun, CaseSource, ChatMessage, User
from app.services.auth.jwt import create_access_token
from app.services.case_analysis import case_analysis
from app.services.case_analysis.contracts import CaseQuestionAnswerResponse
from app.services.case_materials import CaseMaterialsService
from app.routers import cases
from app.services.chat import case_chat
from run_recovery_support import isolated_database
@pytest.mark.parametrize("unknown_citation", [False, True])
def test_ask_without_analysis_uses_current_sources_and_creates_no_run(monkeypatch, unknown_citation):
    async def exercise():
        async with isolated_database() as factory:
            sessions = []

            async def database():
                async with factory() as db:
                    sessions.append(db)
                    yield db

            async with factory() as db, db.begin():
                owner = User(email="reasoning@example.com", name="Owner", oauth_provider="test", oauth_subject_id="reasoning")
                db.add(owner)
                await db.flush()
                case = Case(user_id=owner.id, title="Case without analysis")
                db.add(case)
                await db.flush()
                source = await CaseMaterialsService(db).add_text_source(
                    case_id=case.id, user_id=owner.id, source_kind="narrative",
                    text="ผู้เสียหายชื่อสมชาย", provenance_json={"origin": "test"},
                )
                db.add_all([
                    ChatMessage(case_id=case.id, ordinal=i + 1, role="assistant", content="Old answer is not evidence")
                    for i in range(14)
                ])

            observed = []
            timing = []

            async def hold_before_reasoning(delay):
                timing.append(delay)

            monkeypatch.setattr(case_chat.asyncio, "sleep", hold_before_reasoning)

            async def provider(**kwargs):
                timing.append("provider")
                assert all(not session.in_transaction() for session in sessions)
                assert kwargs["schema"] is CaseQuestionAnswerResponse
                observed.append(kwargs["content"])
                return CaseQuestionAnswerResponse(
                    answer=f"ผู้เสียหายชื่อสมชาย [{source.id}]",
                    cited_source_ids=["does-not-exist" if unknown_citation else str(source.id)],
                    clarification_question=None,
                )

            forbidden = Mock(side_effect=AssertionError("Ordinary Ask must not invoke Main Analysis or retrieval"))
            for name in ("validate_direct_trace", "validate_case_trace", "CaseAnalysisTrace"):
                monkeypatch.setattr(case_analysis, name, forbidden)
            monkeypatch.setattr(cases, "process_case_run", forbidden)
            monkeypatch.setattr("app.services.clients.rag_client.request_rag", forbidden)
            monkeypatch.setattr(case_analysis, "request_stage", provider)
            monkeypatch.setattr(settings, "openrouter_cybercase", "test-key")
            monkeypatch.setattr(settings, "jwt_secret_key", "case-reasoning-test-secret-1234567890")
            headers = {"Authorization": f"Bearer {create_access_token(owner.id, owner.email)}"}
            application = app.app
            original_overrides = dict(application.dependency_overrides)
            application.dependency_overrides[get_db] = database
            try:
                async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                    payload = {"content": "ผู้เสียหายชื่ออะไร", "client_request_id": "ask-id", "intent": "ask"}
                    response = await client.post(f"/api/v1/cases/{case.id}/chat/messages", json=payload, headers=headers)
                    assert response.status_code == (422 if unknown_citation else 200)
                    if unknown_citation:
                        assert response.json()["detail"]["code"] == "case_question_answer_unknown_source"
                    else:
                        receipt = response.json()
                        assert receipt["run"] is None
                        assert receipt["assistant_message"]["content"] == f"ผู้เสียหายชื่อสมชาย [{source.id}]"
                        assert receipt["message"]["analysis_result_id"] is None
                        assert receipt["assistant_message"]["analysis_result_id"] is None
                        retry = await client.post(f"/api/v1/cases/{case.id}/chat/messages", json=payload, headers=headers)
                        assert retry.status_code == 200
                        assert retry.json()["assistant_message"]["id"] == receipt["assistant_message"]["id"]
                assert len(observed) == 1
                assert observed[0]["analysis_mode"] == "question_answer"
                assert observed[0]["response_language"] == "thai"
                assert observed[0]["case_sources"] == [{
                    "source_id": str(source.id), "source_kind": "narrative", "text": "ผู้เสียหายชื่อสมชาย",
                }]
                assert len(observed[0]["conversation_history"]) == 12
                assert observed[0]["technical_context"] is None
                assert observed[0]["analysis_context"] is None
                assert observed[0]["active_clarification"] is None
                assert observed[0]["current_evidence_revision"] == 1
                assert observed[0]["analysis_evidence_revision"] is None
                assert timing == [settings.chat_ask_start_delay_seconds, "provider"]
                async with factory() as db:
                    assert await db.scalar(select(func.count()).select_from(CaseRun)) == 0
                    assert await db.scalar(select(func.count()).select_from(CaseAnalysisResult)) == 0
                    assert await db.scalar(select(func.count()).select_from(CaseSource)) == 1
                    assert (await db.get(Case, case.id)).evidence_revision == 1
                    messages = list((await db.scalars(
                        select(ChatMessage).where(ChatMessage.ordinal > 14).order_by(ChatMessage.ordinal)
                    )).all())
                    assert [message.role for message in messages] == (["user"] if unknown_citation else ["user", "assistant"])
                    assert all(message.message_kind == "conversation" for message in messages)
                forbidden.assert_not_called()
            finally:
                application.dependency_overrides = original_overrides

    asyncio.run(exercise())

def test_ordinary_clarification_stays_in_chat_without_evidence_promotion(monkeypatch):
    async def exercise():
        async with isolated_database() as factory:
            async def database():
                async with factory() as db:
                    yield db

            async with factory() as db, db.begin():
                owner = User(email="clarification@example.com", name="Owner", oauth_provider="test", oauth_subject_id="clarification")
                db.add(owner)
                await db.flush()
                case = Case(user_id=owner.id, title="Ordinary clarification")
                db.add(case)
                await db.flush()
                await CaseMaterialsService(db).add_text_source(
                    case_id=case.id, user_id=owner.id, source_kind="narrative",
                    text="มีหลายบัญชีในเหตุการณ์", provenance_json={"origin": "test"},
                )

            calls = []

            async def provider(**kwargs):
                calls.append(kwargs["content"])
                return CaseQuestionAnswerResponse(
                    answer="ยังระบุบัญชีไม่ได้จากข้อมูลปัจจุบัน",
                    cited_source_ids=[],
                    clarification_question=(
                        "คุณหมายถึงบัญชีต้นทางหรือบัญชีปลายทาง?"
                        if len(calls) == 1 else None
                    ),
                )

            monkeypatch.setattr(case_analysis, "request_stage", provider)
            monkeypatch.setattr(settings, "openrouter_cybercase", "test-key")
            monkeypatch.setattr(settings, "jwt_secret_key", "case-reasoning-test-secret-1234567890")
            headers = {"Authorization": f"Bearer {create_access_token(owner.id, owner.email)}"}
            application = app.app
            original_overrides = dict(application.dependency_overrides)
            application.dependency_overrides[get_db] = database
            try:
                async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                    first = await client.post(
                        f"/api/v1/cases/{case.id}/chat/messages",
                        json={"content": "บัญชีไหนเกี่ยวข้อง", "client_request_id": "clarification-1", "intent": "ask"},
                        headers=headers,
                    )
                    assert first.status_code == 200, first.text
                    assert first.json()["assistant_message"]["content"] == (
                        "ยังระบุบัญชีไม่ได้จากข้อมูลปัจจุบัน\n\nคุณหมายถึงบัญชีต้นทางหรือบัญชีปลายทาง?"
                    )
                    assert first.json()["assistant_message"]["message_kind"] == "conversation"
                    assert first.json()["run"] is None

                    second = await client.post(
                        f"/api/v1/cases/{case.id}/chat/messages",
                        json={"content": "บัญชีต้นทาง", "client_request_id": "clarification-2", "intent": "ask"},
                        headers=headers,
                    )
                    assert second.status_code == 200, second.text
                    assert second.json()["assistant_message"]["content"] == "ยังระบุบัญชีไม่ได้จากข้อมูลปัจจุบัน"
                    assert second.json()["assistant_message"]["message_kind"] == "conversation"
                    assert second.json()["run"] is None
            finally:
                application.dependency_overrides = original_overrides

            assert len(calls) == 2
            async with factory() as db:
                assert await db.scalar(select(func.count()).select_from(CaseRun)) == 0
                assert await db.scalar(select(func.count()).select_from(CaseAnalysisResult)) == 0
                assert await db.scalar(select(func.count()).select_from(CaseSource)) == 1
                assert (await db.get(Case, case.id)).evidence_revision == 1
                messages = list((await db.scalars(
                    select(ChatMessage).where(ChatMessage.case_id == case.id).order_by(ChatMessage.ordinal)
                )).all())
                assert [message.message_kind for message in messages] == [
                    "conversation", "conversation", "conversation", "conversation",
                ]

    asyncio.run(exercise())


def test_ask_without_case_material_asks_for_missing_context(monkeypatch):
    async def exercise():
        async with isolated_database() as factory:
            async def database():
                async with factory() as db:
                    yield db

            async with factory() as db, db.begin():
                owner = User(email="empty-chat@example.com", name="Owner", oauth_provider="test", oauth_subject_id="empty-chat")
                db.add(owner)
                await db.flush()
                case = Case(user_id=owner.id, title="Empty Case Chat")
                db.add(case)
                await db.flush()

            observed = []

            async def provider(**kwargs):
                observed.append(kwargs["content"])
                assert kwargs["schema"] is CaseQuestionAnswerResponse
                return CaseQuestionAnswerResponse(
                    answer="I need more case context before I can answer.",
                    cited_source_ids=[],
                    clarification_question="What event or fact should I investigate first?",
                )

            monkeypatch.setattr(case_analysis, "request_stage", provider)
            monkeypatch.setattr(settings, "openrouter_cybercase", "test-key")
            monkeypatch.setattr(settings, "jwt_secret_key", "case-reasoning-test-secret-1234567890")
            headers = {"Authorization": f"Bearer {create_access_token(owner.id, owner.email)}"}
            application = app.app
            original_overrides = dict(application.dependency_overrides)
            application.dependency_overrides[get_db] = database
            try:
                async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                    response = await client.post(
                        f"/api/v1/cases/{case.id}/chat/messages",
                        json={"content": "Please investigate this case", "client_request_id": "empty-chat-1", "intent": "ask"},
                        headers=headers,
                    )
                    assert response.status_code == 200, response.text
                    assert response.json()["assistant_message"]["content"] == (
                        "I need more case context before I can answer.\n\n"
                        "What event or fact should I investigate first?"
                    )
                    assert response.json()["run"] is None
            finally:
                application.dependency_overrides = original_overrides

            assert observed[0]["case_sources"] == []
            async with factory() as db:
                assert await db.scalar(select(func.count()).select_from(CaseSource)) == 0
                assert (await db.get(Case, case.id)).evidence_revision == 0

    asyncio.run(exercise())
