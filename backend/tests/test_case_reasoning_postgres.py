import asyncio
from uuid import UUID

import httpx
from sqlalchemy import select

from app.config import settings
from app.database import get_db
from app.main import app
from app.models import Case, CaseAnalysisResult, CaseRun, CaseSource, ChatMessage, User
from app.services.auth.jwt import create_access_token
from app.services.case_analysis import case_analysis
from app.services.case_analysis.contracts import CaseAnalysisGap, CaseProviderAnalysis
from app.services.gap_clarification.contracts import GapAnswerInterpretation, GapNextStep
from app.services.case_materials import CaseMaterialsService
from app.services.workflow.case_run_execution import execute_case_run
from app.services.workflow import case_run_execution
from app.routers import cases
from run_recovery_support import isolated_database
def test_formal_followup_answer_reaches_real_reanalysis_with_bounded_provenance(monkeypatch):
    async def exercise():
        async with isolated_database() as factory:
            async def database():
                async with factory() as db:
                    yield db

            async with factory() as db, db.begin():
                owner = User(email="followup@example.com", name="Owner", oauth_provider="test", oauth_subject_id="followup")
                db.add(owner)
                await db.flush()
                case = Case(user_id=owner.id, title="Formal follow-up")
                db.add(case)
                await db.flush()
                await CaseMaterialsService(db).add_text_source(
                    case_id=case.id, user_id=owner.id, source_kind="narrative",
                    text="มีเหตุเกิดขึ้น แต่ยังไม่ระบุเวลา", provenance_json={"origin": "test"},
                )
                run = CaseRun(
                    case_id=case.id, evidence_revision=case.evidence_revision, idempotency_key="first-analysis",
                    request_payload={"operation": "analysis", "response_language": "thai"},
                    pipeline_config=case_analysis.read_pipeline(None).model_dump(mode="json"), status="queued",
                )
                db.add(run)
                await db.flush()

            observed = []

            async def provider(**kwargs):
                if kwargs["schema"] is GapNextStep:
                    return GapNextStep(
                        action="ask",
                        question="เหตุเกิดเวลาประมาณเท่าใด?",
                        target_information="เวลาเกิดเหตุ",
                    )
                if kwargs["schema"] is GapAnswerInterpretation:
                    return GapAnswerInterpretation(
                        response_type="case_fact",
                        normalized_fact=kwargs["content"]["answer"]["content"],
                        gap_resolution="resolved",
                    )
                assert kwargs["schema"] is CaseProviderAnalysis
                content = kwargs["content"]
                observed.append(content)
                answer_sources = [source for source in content["case_sources"] if source["source_kind"] == "followup_answer"]
                claims = [{
                    "claim_id": f"A-{index + 1:02d}", "claim_type": "reported", "text": source["text"],
                    "epistemic_status": "reported", "supporting_source_ids": [source["source_id"]],
                    "supporting_citations": [{"source_id": source["source_id"], "exact_quote": source["text"]}],
                } for index, source in enumerate(content["case_sources"])]
                return CaseProviderAnalysis(
                    version="case_analysis_trace_v1", answer="ผลการวิเคราะห์", summary="ผลการวิเคราะห์",
                    involved_parties=[], timeline=[], impacts=[], claims=claims,
                    gaps=[] if answer_sources else [CaseAnalysisGap(
                        gap_id="G-03", gap_key="incident_time", topic="เวลาเกิดเหตุ", status="NOT_PROVIDED",
                        description="ยังไม่ระบุเวลา", reason="เวลามีผลต่อการวิเคราะห์", priority="high", askable=True,
                        clarification_question="เหตุเกิดเวลาประมาณเท่าใด?", affected_claim_ids=["A-01"],
                    )],
                )

            monkeypatch.setattr(case_analysis, "request_stage", provider)
            monkeypatch.setattr(settings, "openrouter_cybercase", "test-key")
            monkeypatch.setattr(settings, "jwt_secret_key", "case-reasoning-test-secret-1234567890")
            monkeypatch.setattr(settings, "chat_followup_enabled", True)
            clarification_run_statuses = []
            original_start_gap = case_run_execution.start_gap_clarification_for_run

            async def start_gap_and_capture(*, run_id, session_factory):
                async with factory() as inspect_db:
                    clarification_run_statuses.append(
                        await inspect_db.scalar(
                            select(CaseRun.status).where(CaseRun.id == run_id)
                        )
                    )
                return await original_start_gap(
                    run_id=run_id,
                    session_factory=session_factory,
                )

            monkeypatch.setattr(
                case_run_execution,
                "start_gap_clarification_for_run",
                start_gap_and_capture,
            )
            await execute_case_run(run.id, session_factory=factory)
            assert clarification_run_statuses == ["running"]
            async with factory() as db:
                question = await db.scalar(select(ChatMessage).where(ChatMessage.message_kind == "followup_question"))
                assert question is not None
                assert question.content == "เหตุเกิดเวลาประมาณเท่าใด?"
                old_result_id = question.analysis_result_id

            dispatched = []

            async def execute_queued(run_id):
                dispatched.append(run_id)
                await execute_case_run(run_id, session_factory=factory)

            monkeypatch.setattr(cases, "process_case_run", execute_queued)
            headers = {"Authorization": f"Bearer {create_access_token(owner.id, owner.email)}"}
            application = app.app
            original_overrides = dict(application.dependency_overrides)
            application.dependency_overrides[get_db] = database
            try:
                async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                    response = await client.post(f"/api/v1/cases/{case.id}/chat/messages", headers=headers, json={
                        "intent": "followup_answer", "client_request_id": "formal-answer", "response_language": "thai",
                        "in_reply_to_message_id": str(question.id),
                        "followup": {"gap_id": "G-03", "answer": "22:30", "disposition": "answered"},
                    })
                    assert response.status_code == 200, response.text
                    assert response.json()["message"]["message_kind"] == "followup_answer"
                    assert response.json()["reply_message"]["content"] == "รับทราบข้อมูลเพิ่มเติมแล้วครับ"
                    queued_id = UUID(response.json()["run"]["id"])
                    assert response.json()["run"]["evidence_revision"] == 2
                    assert dispatched == [queued_id]
                assert len(observed) == 2
                serialized_answer = next(source for source in observed[1]["case_sources"] if source["source_kind"] == "followup_answer")
                assert serialized_answer["text"] == "22:30"
                assert serialized_answer["followup_context"] == {
                    "gap_id": "G-03", "gap_key": "incident_time", "topic": "เวลาเกิดเหตุ",
                    "clarification_question": "เหตุเกิดเวลาประมาณเท่าใด?",
                }
                assert observed[1]["conversation_history"] == []
                assert set(observed[1]) == {
                    "response_language", "analysis_mode", "case_sources", "technical_context", "question", "conversation_history",
                }
                async with factory() as db:
                    source = await db.scalar(select(CaseSource).where(CaseSource.source_kind == "followup_answer"))
                    assert str(source.id) == serialized_answer["source_id"]
                    assert source.exact_text == "22:30"
                    assert source.provenance_json["source_analysis_id"] == str(old_result_id)
                    assert source.provenance_json["source_revision"] == 1
                    assert source.provenance_json["question_message_id"] == str(question.id)
                    assert (await db.get(Case, case.id)).evidence_revision == 2
                    assert (await db.get(CaseRun, queued_id)).status == "completed"
                    result = await db.scalar(select(CaseAnalysisResult).where(CaseAnalysisResult.run_id == queued_id))
                    assert result.evidence_revision == 2
                    assert result.trace_json["gaps"] == []
            finally:
                application.dependency_overrides = original_overrides

    asyncio.run(exercise())
