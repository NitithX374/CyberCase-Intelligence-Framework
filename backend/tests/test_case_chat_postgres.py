import asyncio
from uuid import uuid4

import pytest
from sqlalchemy import func, select

from app.models import Case, CaseAnalysisResult, CaseRun, ChatMessage, ChatThread
from app.models.caseMaterials import CaseEvidenceSnapshot, EvidenceSource
from app.schemas.caseClarifications import CaseClarificationAnswer
from app.schemas.caseRuns import CaseAnalysisCreate
from app.schemas.chat import ChatMessageCreate
from app.services.case_analysis.contracts import (
    CaseAnalysisClaim,
    CaseAnalysisTrace,
    CaseEvidenceCitation,
)
from app.services.case_materials import CaseMaterialsService
from app.services.chat import CaseChatError, ChatService, createCaseChatMessageAndRun
from app.services.followup.caseClarification import (
    CaseClarificationError,
    get_owned_clarifications,
    submit_clarification_answer,
)
from app.services.workflow.caseAskCompletion import completeCaseAsk
from app.services.workflow.caseRunClaim import claimCaseRun
from app.services.workflow.caseRunCompletion import complete_case_run
from app.services.workflow.caseRunService import enqueue_case_analysis
from app.services.case_analysis.contracts import CaseAnalysisResult as AnalysisOutput
from run_recovery_support import isolated_database


async def _case_with_source(factory):
    case_id = uuid4()
    async with factory() as db, db.begin():
        db.add(Case(id=case_id, title="Case Chat"))
        source = await CaseMaterialsService(db).admitText(
            case_id=case_id,
            user_id=None,
            source_kind="narrative",
            exact_text="The witness reported a blue vehicle.",
            provenance_json={"origin": "analyst-authored"},
        )
        return case_id, source.id


async def _enqueue(factory, case_id, key):
    async with factory() as db, db.begin():
        run = await enqueue_case_analysis(
            db,
            case_id=case_id,
            user_id=None,
            request=CaseAnalysisCreate(
                idempotency_key=key,
                response_language="english",
                expected_evidence_revision=1,
            ),
        )
        return run.id


def _output(snapshot, source_id, *, mode="case_overview", followup=False):
    quote = "The witness reported a blue vehicle."
    trace = CaseAnalysisTrace(
        analysis_mode=mode,
        summary=quote,
        claims=[
            CaseAnalysisClaim(
                claim_id="A-01",
                claim_type="reported",
                text=quote,
                epistemic_status="reported",
                supporting_source_ids=[str(source_id)],
                supporting_citations=[
                    CaseEvidenceCitation(
                        source_id=str(source_id),
                        source_revision=1,
                        exact_quote=quote,
                    )
                ],
            )
        ],
        evidence_sha256=snapshot.text_sha256,
    )
    return AnalysisOutput(
        answer=quote,
        trace=trace,
        execution_receipt={"test": "case-chat"},
        followup_question="Which vehicle colour was recorded?" if followup else None,
        followup_metadata=(
            {"gap_id": "G-01", "topic": "Vehicle colour", "gap_key": "vehicle_colour"}
            if followup
            else None
        ),
    )


async def _complete_initial(factory, case_id, source_id, *, followup=True):
    run_id = await _enqueue(factory, case_id, "initial-analysis")
    async with factory() as db:
        claimed = await claimCaseRun(db, run_id, "initial-worker")
    assert claimed is not None
    async with factory() as db:
        snapshot = await db.get(CaseEvidenceSnapshot, claimed.snapshot_id)
    async with factory() as db:
        assert await complete_case_run(
            db,
            run_id,
            claimed.attempt_count,
            _output(snapshot, source_id, followup=followup),
        )
    return run_id


def test_case_publication_and_clarification_are_separate_and_idempotent():
    async def exercise():
        async with isolated_database() as factory:
            case_id, source_id = await _case_with_source(factory)
            async with factory() as db, db.begin():
                db.add(ChatThread(case_id=case_id))
            await _complete_initial(factory, case_id, source_id)
            async with factory() as db:
                clarifications = await get_owned_clarifications(db, case_id)
                assert len(clarifications) == 1
                clarification = clarifications[0]
                messages = list((await db.scalars(select(ChatMessage).order_by(ChatMessage.ordinal))).all())
                assert clarification is not None
                assert [message.ordinal for message in messages] == [1]
                assert [message.message_kind for message in messages] == ["followup_question"]
                assert messages[0].metadata_json.get("chat_followup") is not None
                gap_detail = messages[0].metadata_json["chat_followup"]["selected_gap_detail"]
                assert gap_detail["topic"] == "Vehicle colour"
                assert bool(gap_detail["reason"])
                assert bool(gap_detail["affects"])
                result_id = messages[0].analysis_result_id
            request = CaseClarificationAnswer(
                answer="The colour was blue.",
                idempotency_key="clarification-answer",
                response_language="english",
            )
            async with factory() as db, db.begin():
                answered, run = await submit_clarification_answer(
                    db,
                    case_id=case_id,
                    clarification_id=clarification.id,
                    user_id=None,
                    request=request,
                )
                assert answered.answer_message_id is not None
                assert run.operation == "analysis"
                first_run_id = run.id
            async with factory() as db, db.begin():
                repeated, same_run = await submit_clarification_answer(
                    db,
                    case_id=case_id,
                    clarification_id=clarification.id,
                    user_id=None,
                    request=request,
                )
                assert repeated.answer_evidence_source_id == answered.answer_evidence_source_id
                assert same_run.id == first_run_id
            async with factory() as db:
                assert await db.scalar(select(func.count()).select_from(EvidenceSource)) == 2
                assert await db.scalar(select(func.count()).select_from(CaseRun)) == 2
                assert await db.scalar(select(func.count()).select_from(ChatMessage)) == 2
                assert await db.scalar(select(CaseAnalysisResult.id).where(CaseAnalysisResult.id == result_id)) is not None
            async with factory() as db, db.begin():
                case = await db.get(Case, case_id)
                snapshot_id = await db.scalar(select(CaseAnalysisResult.snapshot_id).where(CaseAnalysisResult.id == result_id))
                new_run_id = uuid4()
                new_result_id = uuid4()
                db.add(
                    CaseRun(
                        id=new_run_id,
                        case_id=case_id,
                        operation="analysis",
                        snapshot_id=snapshot_id,
                        idempotency_key="stale-test-run",
                        request_fingerprint="f" * 64,
                        status="completed",
                    )
                )
                await db.flush()
                db.add(
                    CaseAnalysisResult(
                        id=new_result_id,
                        case_id=case_id,
                        run_id=new_run_id,
                        snapshot_id=snapshot_id,
                        schema_version="case_analysis_trace_v1",
                        status="validated",
                        answer="New analysis",
                        summary="New analysis",
                    )
                )
                await db.flush()
                case.latest_analysis_result_id = new_result_id
                thread = await db.scalar(select(ChatThread).where(ChatThread.case_id == case_id))
                unanswered_old_q = ChatMessage(
                    thread_id=thread.id,
                    ordinal=thread.next_message_ordinal,
                    role="assistant",
                    content="What was the vehicle model?",
                    message_kind="followup_question",
                    analysis_result_id=result_id,
                )
                db.add(unanswered_old_q)
                thread.next_message_ordinal += 1
            async with factory() as db, db.begin():
                with pytest.raises(CaseClarificationError, match="older analysis"):
                    await submit_clarification_answer(
                        db,
                        case_id=case_id,
                        clarification_id=unanswered_old_q.id,
                        user_id=None,
                        request=CaseClarificationAnswer(
                            answer="A stale answer.",
                            idempotency_key="stale-answer",
                        ),
                    )

    asyncio.run(exercise())


def test_case_ask_uses_case_run_without_new_result_or_evidence():
    async def exercise():
        async with isolated_database() as factory:
            case_id, source_id = await _case_with_source(factory)
            await _complete_initial(factory, case_id, source_id, followup=False)
            async with factory() as db:
                case = await db.get(Case, case_id)
                result_id = case.latest_analysis_result_id
            async with factory() as db, db.begin():
                db.add(ChatThread(id=case_id, title="Case Chat"))
            request = ChatMessageCreate(
                content="What vehicle was reported?",
                idempotency_key="case-ask",
                action="ask",
            )
            async with factory() as db, db.begin():
                message, run = await createCaseChatMessageAndRun(
                    db,
                    case_id=case_id,
                    user_id=None,
                    request=request,
                )
                assert message.role == "user"
                assert run.operation == "ask"
                assert message.analysis_result_id == result_id
                assert run.request_message_id == message.id
            async with factory() as db:
                claimed = await claimCaseRun(db, run.id, "ask-worker")
            assert claimed is not None
            async with factory() as db:
                snapshot = await db.get(CaseEvidenceSnapshot, claimed.snapshot_id)
            async with factory() as db:
                assert await completeCaseAsk(
                    db,
                    run.id,
                    claimed.attempt_count,
                    _output(snapshot, source_id, mode="question_answer"),
                )
            async with factory() as db:
                case = await db.get(Case, case_id)
                messages = list((await db.scalars(select(ChatMessage).order_by(ChatMessage.ordinal))).all())
                saved_run = await db.get(CaseRun, run.id)
                assert case.latest_analysis_result_id == result_id
                assert await db.scalar(select(func.count()).select_from(CaseAnalysisResult)) == 1
                assert await db.scalar(select(func.count()).select_from(EvidenceSource)) == 1
                assert saved_run.status == "completed"
                assert [message.role for message in messages] == ["user", "assistant"]
                assert messages[1].metadata_json["analysis_state_scope"] == "response_scoped"
                assert messages[1].analysis_result_id == result_id
                assert messages[0].metadata_json["analysis_freshness"] == "current"
                assert messages[1].metadata_json["analysis_freshness"] == "current"
                assert messages[1].metadata_json["has_newer_evidence"] is False
                from app.services.cases.caseService import CaseService
                serialized = await CaseService(db).getCase(case_id, user_id=None)
                assert serialized.processing_status == "idle"

    asyncio.run(exercise())


@pytest.mark.parametrize("action", ["ask", None])
def test_first_case_chat_ask_requires_completed_analysis(action):
    async def exercise():
        async with isolated_database() as factory:
            case_id, _ = await _case_with_source(factory)
            async with factory() as db, db.begin():
                db.add(ChatThread(id=case_id, title="Case Chat"))
            async with factory() as db, db.begin():
                with pytest.raises(CaseChatError, match="Analyze the Case"):
                    await createCaseChatMessageAndRun(
                        db,
                        case_id=case_id,
                        user_id=None,
                        request=ChatMessageCreate(
                            content="Can you analyze this?",
                            idempotency_key="first-ask",
                            action=action,
                        ),
                    )
            async with factory() as db:
                assert await db.scalar(select(func.count()).select_from(CaseRun)) == 0
                assert await db.scalar(select(func.count()).select_from(ChatMessage)) == 0
                assert await db.scalar(select(func.count()).select_from(EvidenceSource)) == 1

    asyncio.run(exercise())


def test_removing_chat_preserves_case_history():
    async def exercise():
        async with isolated_database() as factory:
            case_id, source_id = await _case_with_source(factory)
            async with factory() as db, db.begin():
                db.add(ChatThread(case_id=case_id))
            await _complete_initial(factory, case_id, source_id)
            async with factory() as db:
                result = await db.scalar(select(CaseAnalysisResult).where(CaseAnalysisResult.case_id == case_id))
                snapshot = await db.get(CaseEvidenceSnapshot, result.snapshot_id)
            async with factory() as db:
                await ChatService(db).delete_thread(case_id, user_id=None)
            async with factory() as db:
                assert await db.get(Case, case_id) is not None
                assert await db.get(CaseAnalysisResult, result.id) is not None
                assert await db.get(CaseEvidenceSnapshot, snapshot.id) is not None
                assert await db.scalar(select(ChatThread).where(ChatThread.case_id == case_id)) is None
                assert await db.scalar(select(func.count()).select_from(ChatMessage)) == 0

    asyncio.run(exercise())
