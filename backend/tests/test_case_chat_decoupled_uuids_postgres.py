import asyncio
from uuid import uuid4

import pytest
from sqlalchemy import select

from app.models import Case, CaseAnalysisResult, CaseEvidenceSnapshot, CaseReport, CaseRun, ChatMessage, ChatThread
from app.models.caseClarification import CaseClarification
from app.schemas.caseRuns import CaseAnalysisCreate
from app.schemas.chat import ChatMessageCreate
from app.services.case_analysis.contracts import (
    CaseAnalysisClaim,
    CaseAnalysisResult as AnalysisOutput,
    CaseAnalysisTrace,
    CaseEvidenceCitation,
)
from app.services.case_materials import CaseMaterialsService
from app.services.cases.caseService import buildCaseWithChat
from app.services.chat.caseChat import createCaseChatMessageAndRun
from app.services.reports.case_report_persistence import CaseReportService
from app.services.workflow.caseAskCompletion import completeCaseAsk
from app.services.workflow.caseRunClaim import claimCaseRun
from app.services.workflow.caseRunCompletion import complete_case_run
from app.services.workflow.caseRunService import enqueue_case_analysis
from run_recovery_support import isolated_database


def _output(snapshot, source_id, *, mode="case_overview", followup=False, question="What colour?"):
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
        execution_receipt={"test": "decoupled-uuids"},
        followup_question=question if followup else None,
        followup_metadata=(
            {"gap_id": "G-01", "topic": "Vehicle colour", "gap_key": "vehicle_colour"}
            if followup
            else None
        ),
    )


def test_case_and_chat_thread_work_with_distinct_uuids():
    async def exercise():
        async with isolated_database() as factory:
            case, thread = buildCaseWithChat("Decoupled UUID Case", None)
            assert case.id != thread.id
            assert thread.case_id == case.id

            async with factory() as db, db.begin():
                db.add(case)
                db.add(thread)
                source = await CaseMaterialsService(db).admitText(
                    case_id=case.id,
                    user_id=None,
                    source_kind="narrative",
                    exact_text="The witness reported a blue vehicle.",
                    provenance_json={"origin": "analyst-authored"},
                )
                source_id = source.id

            # Initial analysis enqueued
            async with factory() as db, db.begin():
                initial_run = await enqueue_case_analysis(
                    db,
                    case_id=case.id,
                    user_id=None,
                    request=CaseAnalysisCreate(idempotency_key="init-analysis"),
                )
                initial_run_id = initial_run.id

            # Worker claims and completes initial analysis with a follow-up question
            async with factory() as db:
                claimed = await claimCaseRun(db, initial_run_id, "worker-1")
                assert claimed is not None
                snapshot = await db.get(CaseEvidenceSnapshot, claimed.snapshot_id)
            async with factory() as db:
                success = await complete_case_run(
                    db,
                    initial_run_id,
                    claimed.attempt_count,
                    _output(snapshot, source_id, followup=True, question="Which shade of blue?"),
                )
                assert success

            # Verify thread status updated and followup question message exists in the thread
            async with factory() as db:
                saved_thread = await db.scalar(
                    select(ChatThread).where(ChatThread.case_id == case.id)
                )
                assert saved_thread is not None
                assert saved_thread.id == thread.id
                assert saved_thread.id != case.id
                assert saved_thread.status == "awaiting_followup"

                clarification = await db.scalar(
                    select(CaseClarification).where(
                        CaseClarification.case_id == case.id,
                        CaseClarification.state == "pending",
                    )
                )
                assert clarification is not None

                messages = list((await db.scalars(
                    select(ChatMessage).where(ChatMessage.thread_id == thread.id)
                )).all())
                assert len(messages) == 1
                assert messages[0].message_kind == "followup_question"

            # Submit clarification answer via Chat message endpoint with explicit intent
            answer_request = ChatMessageCreate(
                content="It was navy blue.",
                idempotency_key="clarif-answer-1",
                intent="clarification_answer",
                clarification_id=clarification.id,
            )
            async with factory() as db, db.begin():
                ans_msg, next_run = await createCaseChatMessageAndRun(
                    db,
                    case_id=case.id,
                    user_id=None,
                    request=answer_request,
                )
                assert ans_msg.thread_id == thread.id
                assert next_run.operation == "analysis"
                next_run_id = next_run.id

            # Worker claims and completes re-analysis (no followup)
            async with factory() as db:
                claimed_2 = await claimCaseRun(db, next_run_id, "worker-2")
                assert claimed_2 is not None
                snapshot_2 = await db.get(CaseEvidenceSnapshot, claimed_2.snapshot_id)
            async with factory() as db:
                success_2 = await complete_case_run(
                    db,
                    next_run_id,
                    claimed_2.attempt_count,
                    _output(snapshot_2, source_id, followup=False),
                )
                assert success_2

            # Thread status should now be "answered"
            async with factory() as db:
                saved_thread = await db.scalar(
                    select(ChatThread).where(ChatThread.case_id == case.id)
                )
                assert saved_thread.status == "answered"

            # Now send a normal Q&A ask message with intent="ask"
            ask_request = ChatMessageCreate(
                content="What type of car was it?",
                idempotency_key="ask-q-1",
                intent="ask",
            )
            async with factory() as db, db.begin():
                ask_msg, ask_run = await createCaseChatMessageAndRun(
                    db,
                    case_id=case.id,
                    user_id=None,
                    request=ask_request,
                )
                assert ask_msg.thread_id == thread.id
                assert ask_run.operation == "ask"
                ask_run_id = ask_run.id

            # Worker claims and completes ask run
            async with factory() as db:
                claimed_ask = await claimCaseRun(db, ask_run_id, "worker-ask")
                assert claimed_ask is not None
                snapshot_ask = await db.get(CaseEvidenceSnapshot, claimed_ask.snapshot_id)
            async with factory() as db:
                success_ask = await completeCaseAsk(
                    db,
                    ask_run_id,
                    claimed_ask.attempt_count,
                    _output(snapshot_ask, source_id, mode="question_answer"),
                )
                assert success_ask

            # Generate report
            from app.schemas.reports import CaseReportCreate
            async with factory() as db:
                report_service = CaseReportService(db)
                report = await report_service.generate_report(
                    case_id=case.id,
                    request=CaseReportCreate(idempotency_key="report-key-1"),
                    user_id=None,
                )
                assert report.case_id == case.id
                assert report.version_number == 1

            # Final sanity assertions
            async with factory() as db:
                all_messages = list((await db.scalars(
                    select(ChatMessage).where(ChatMessage.thread_id == thread.id).order_by(ChatMessage.ordinal)
                )).all())
                assert len(all_messages) == 4
                assert all(msg.thread_id == thread.id for msg in all_messages)
                assert thread.id != case.id

    asyncio.run(exercise())
