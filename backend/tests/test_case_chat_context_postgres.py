import asyncio

import httpx

from app.config import settings
from app.database import get_db
from app.main import app
from app.models import Case, CaseAnalysisResult, CaseRun, ChatMessage, RagContext, User
from app.services.auth.jwt import create_access_token
from app.services.case_analysis import case_analysis
from app.services.case_analysis.contracts import CaseQuestionAnswerResponse
from app.services.case_materials import CaseMaterialsService
from app.services.chat import case_chat
from run_recovery_support import isolated_database


def test_chat_uses_case_analysis_clarification_and_rag_context(monkeypatch):
    async def exercise():
        async with isolated_database() as factory:
            async def database():
                async with factory() as db:
                    yield db

            async with factory() as db, db.begin():
                owner = User(
                    email="chat-context@example.com",
                    name="Owner",
                    oauth_provider="test",
                    oauth_subject_id="chat-context",
                )
                db.add(owner)
                await db.flush()
                case = Case(user_id=owner.id, title="Chat context")
                db.add(case)
                await db.flush()
                source = await CaseMaterialsService(db).add_text_source(
                    case_id=case.id,
                    user_id=owner.id,
                    source_kind="narrative",
                    text="The report records a login at 22:30.",
                    provenance_json={"origin": "test"},
                )
                run = CaseRun(
                    case_id=case.id,
                    evidence_revision=case.evidence_revision,
                    idempotency_key="context-analysis",
                    request_payload={"operation": "analysis", "response_language": "english"},
                    pipeline_config=case_analysis.read_pipeline(None).model_dump(mode="json"),
                    status="completed",
                )
                db.add(run)
                await db.flush()
                rag = RagContext(
                    retrieval_context_id="context-retrieval",
                    case_id=case.id,
                    case_run_id=run.id,
                    query_text="login behavior",
                    context_text="ATT&CK describes credential access techniques.",
                    mitre_table=[{"technique_id": "T1059", "name": "Command and Scripting Interpreter"}],
                )
                db.add(rag)
                await db.flush()
                trace = {
                    "version": "case_analysis_trace_v1",
                    "validation_status": "validated",
                    "analysis_mode": "case_overview",
                    "summary": "A login was recorded.",
                    "involved_parties": [],
                    "timeline": [{"time": "22:30", "event": "A login was recorded.", "claim_ids": ["A-01"]}],
                    "claims": [{
                        "claim_id": "A-01",
                        "claim_type": "reported",
                        "text": "A login was recorded.",
                        "epistemic_status": "reported",
                        "supporting_source_ids": [str(source.id)],
                        "supporting_citations": [{"source_id": str(source.id), "exact_quote": source.exact_text}],
                    }],
                    "impacts": [],
                    "gaps": [{
                        "gap_id": "G-01",
                        "gap_key": "login_actor",
                        "topic": "Login actor",
                        "status": "NOT_PROVIDED",
                        "description": "The account owner is unknown.",
                        "reason": "Attribution is relevant.",
                        "priority": "high",
                        "askable": True,
                        "clarification_question": "Who used the account?",
                        "affected_claim_ids": ["A-01"],
                    }],
                    "mitre_associations": [],
                    "retrieval_context_id": "context-retrieval",
                }
                result = CaseAnalysisResult(
                    case_id=case.id,
                    run_id=run.id,
                    evidence_revision=case.evidence_revision,
                    answer="A login was recorded.",
                    summary="A login was recorded.",
                    trace_json=trace,
                    retrieval_context_id="context-retrieval",
                    pipeline_config=run.pipeline_config,
                    external_context_json={"source_reference_type": "case_source"},
                )
                db.add(result)
                await db.flush()
                case.latest_analysis_result_id = result.id
                question = ChatMessage(
                    case_id=case.id,
                    ordinal=1,
                    role="assistant",
                    content="Who used the account?",
                    message_kind="followup_question",
                    analysis_result_id=result.id,
                    metadata_json={"chat_followup": {
                        "source_analysis_id": str(result.id),
                        "source_revision": case.evidence_revision,
                        "clarification_session_id": "clarification-session",
                        "target_information": "Account owner",
                        "rationale_summary": "Attribution is relevant.",
                        "gap": {"gap_id": "G-01", "gap_key": "login_actor", "topic": "Login actor"},
                    }},
                )
                db.add(question)

            observed = []

            async def provider(**kwargs):
                observed.append(kwargs["content"])
                return CaseQuestionAnswerResponse(
                    answer="The case analysis says the account owner is unknown.",
                    cited_source_ids=[],
                )

            async def no_delay(_):
                return None

            monkeypatch.setattr(case_analysis, "request_stage", provider)
            monkeypatch.setattr(case_chat.asyncio, "sleep", no_delay)
            monkeypatch.setattr(settings, "openrouter_cybercase", "test-key")
            monkeypatch.setattr(settings, "jwt_secret_key", "case-reasoning-test-secret-1234567890")
            headers = {"Authorization": f"Bearer {create_access_token(owner.id, owner.email)}"}
            original_overrides = dict(app.app.dependency_overrides)
            app.app.dependency_overrides[get_db] = database
            try:
                async with httpx.AsyncClient(
                    transport=httpx.ASGITransport(app=app), base_url="http://test"
                ) as client:
                    response = await client.post(
                        f"/api/v1/cases/{case.id}/chat/messages",
                        json={"content": "What does the analysis say about the account?", "client_request_id": "context-ask", "intent": "ask"},
                        headers=headers,
                    )
                    assert response.status_code == 200, response.text
            finally:
                app.app.dependency_overrides = original_overrides

            content = observed[0]
            assert content["current_evidence_revision"] == 1
            assert content["analysis_evidence_revision"] == 1
            assert content["analysis_context"]["analysis_id"] == str(result.id)
            assert content["analysis_context"]["gaps"][0]["gap_id"] == "G-01"
            assert content["active_clarification"]["status"] == "current"
            assert content["active_clarification"]["question_message_id"] == str(question.id)
            assert content["technical_context"]["retrieval_context_id"] == "context-retrieval"
            assert content["technical_context"]["case_run_id"] == str(run.id)
            assert content["conversation_history"] == [{"role": "assistant", "content": "Who used the account?"}]

    asyncio.run(exercise())
