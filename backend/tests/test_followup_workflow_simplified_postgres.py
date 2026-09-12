"""Integration test: Simplified Follow-up Question & Answer Workflow without case_clarifications table.

Verifies:
1. The case_clarifications table does NOT exist in the database catalog.
2. An analysis run emitting a gap produces a ChatMessage(message_kind="followup_question") with analysis_result_id.
3. get_owned_clarifications reconstructs the clarification from ChatMessage without reading from any clarification table.
4. Answering via ChatMessageCreate(intent="clarification_answer", clarification_id=...) produces:
   - ChatMessage(message_kind="followup_answer", in_reply_to_message_id=question.id)
   - EvidenceSource(source_kind="followup_answer", origin_message_id=answer_msg.id)
   - An enqueued CaseRun(operation="analysis")
5. The subsequent analysis run snapshot admits the newly answered evidence.
6. Answering via submit_clarification_answer operates equivalently through the unified ChatMessage/EvidenceSource pipeline.
"""

import asyncio
import os
from uuid import uuid4

import pytest
from sqlalchemy import func, select, text

from app.models import Case, CaseAnalysisResult, CaseEvidenceSnapshot, CaseRun, ChatMessage, ChatThread
from app.models.caseMaterials import EvidenceSource
from app.schemas.caseClarifications import CaseClarificationAnswer
from app.schemas.caseRuns import CaseAnalysisCreate
from app.schemas.chat import ChatMessageCreate
from app.services.case_analysis.contracts import (
    CaseAnalysisClaim,
    CaseAnalysisResult as AnalysisOutput,
    CaseAnalysisTrace,
    CaseEvidenceCitation,
)
from app.services.case_materials import CaseMaterialsService
from app.services.chat.caseChat import createCaseChatMessageAndRun
from app.services.followup.caseClarification import (
    get_owned_clarifications,
    submit_clarification_answer,
)
from app.services.workflow.caseRunClaim import claimCaseRun
from app.services.workflow.caseRunCompletion import complete_case_run
from app.services.workflow.caseRunService import enqueue_case_analysis
from run_recovery_support import isolated_database


def _make_output(snapshot, source_id, exact_text="Initial investigation statement.", *, followup_question=None):
    quote = exact_text
    trace = CaseAnalysisTrace(
        analysis_mode="case_overview",
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
        execution_receipt={"calls": []},
        followup_question=followup_question,
        followup_metadata=(
            {"gap_id": "G-01", "topic": "Suspect Vehicle", "gap_key": "suspect_vehicle"}
            if followup_question
            else None
        ),
    )


def test_followup_workflow_via_chat_message_without_clarification_table():
    url = os.environ.get("CYBERCASE_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set CYBERCASE_TEST_DATABASE_URL to run PostgreSQL integration tests")

    async def exercise():
        async with isolated_database() as factory:
            case_id = uuid4()

            # 1. Verify case_clarifications table does NOT exist
            async with factory() as db:
                tbl_exists = await db.scalar(
                    text("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'case_clarifications'")
                )
                assert tbl_exists == 0, "case_clarifications table must NOT exist in the database"

            # 2. Setup initial case and evidence
            async with factory() as db, db.begin():
                case = Case(id=case_id, title="Follow-up Workflow Case")
                db.add(case)
                db.add(ChatThread(id=case_id, case_id=case_id, title=case.title))
                source = await CaseMaterialsService(db).admitText(
                    case_id=case_id,
                    user_id=None,
                    source_kind="narrative",
                    exact_text="Initial investigation statement.",
                    provenance_json={"origin": "investigator"},
                )
                source_id = source.id

            # 3. Enqueue and complete Run 1 with a follow-up question
            async with factory() as db, db.begin():
                run_1 = await enqueue_case_analysis(
                    db,
                    case_id=case_id,
                    user_id=None,
                    request=CaseAnalysisCreate(idempotency_key="run-1-followup"),
                )
                run_1_id = run_1.id

            async with factory() as db:
                claimed_1 = await claimCaseRun(db, run_1_id, "worker-1")
                snapshot_1 = await db.get(CaseEvidenceSnapshot, claimed_1.snapshot_id)

            async with factory() as db:
                output_1 = _make_output(
                    snapshot_1,
                    source_id,
                    followup_question="What was the license plate number of the vehicle?",
                )
                assert await complete_case_run(db, run_1_id, claimed_1.attempt_count, output_1)

            # 4. Verify ChatMessage was created with message_kind="followup_question"
            async with factory() as db:
                thread = await db.scalar(select(ChatThread).where(ChatThread.case_id == case_id))
                assert thread.status == "awaiting_followup"

                q_msg = await db.scalar(
                    select(ChatMessage).where(
                        ChatMessage.thread_id == case_id,
                        ChatMessage.message_kind == "followup_question",
                    )
                )
                assert q_msg is not None
                assert q_msg.content == "What was the license plate number of the vehicle?"
                assert q_msg.analysis_result_id is not None

                # Verify dynamic reconstruction via get_owned_clarifications
                clarifications = await get_owned_clarifications(db, case_id)
                assert len(clarifications) == 1
                assert clarifications[0].id == q_msg.id
                assert clarifications[0].state == "pending"
                assert clarifications[0].question == q_msg.content

            # 5. Answer via ChatMessageCreate with intent="clarification_answer"
            answer_request = ChatMessageCreate(
                content="License plate was 9XYZ-1234.",
                idempotency_key="answer-msg-1",
                intent="clarification_answer",
                clarification_id=q_msg.id,
            )
            async with factory() as db, db.begin():
                answer_msg, run_2 = await createCaseChatMessageAndRun(
                    db,
                    case_id=case_id,
                    user_id=None,
                    request=answer_request,
                )
                assert answer_msg.message_kind == "followup_answer"
                assert answer_msg.in_reply_to_message_id == q_msg.id
                assert run_2.operation == "analysis"
                run_2_id = run_2.id

            # 6. Verify EvidenceSource with source_kind="followup_answer" was created
            async with factory() as db:
                new_source = await db.scalar(
                    select(EvidenceSource).where(
                        EvidenceSource.case_id == case_id,
                        EvidenceSource.source_kind == "followup_answer",
                    )
                )
                assert new_source is not None
                assert new_source.origin_message_id == answer_msg.id

                # Clarification state is now "answered"
                clarifs_answered = await get_owned_clarifications(db, case_id)
                assert len(clarifs_answered) == 1
                assert clarifs_answered[0].state == "answered"
                assert clarifs_answered[0].answer_message_id == answer_msg.id
                assert clarifs_answered[0].answer_evidence_source_id == new_source.id

            # 7. Execute Run 2 - verify it admitted the new evidence
            async with factory() as db:
                claimed_2 = await claimCaseRun(db, run_2_id, "worker-2")
                assert "9XYZ-1234" in claimed_2.input_text

            async with factory() as db:
                snapshot_2 = await db.get(CaseEvidenceSnapshot, claimed_2.snapshot_id)
                output_2 = _make_output(snapshot_2, source_id, followup_question=None)

            async with factory() as db:
                assert await complete_case_run(db, run_2_id, claimed_2.attempt_count, output_2)

            # 8. Post-completion verification: thread is ready, both messages linked
            async with factory() as db:
                completed_run_2 = await db.get(CaseRun, run_2_id)
                assert completed_run_2.status == "completed"

                final_thread = await db.scalar(select(ChatThread).where(ChatThread.case_id == case_id))
                assert final_thread.status == "answered"

                total_sources = await db.scalar(
                    select(func.count()).select_from(EvidenceSource).where(EvidenceSource.case_id == case_id)
                )
                assert total_sources == 2

    asyncio.run(exercise())


def test_followup_workflow_via_dedicated_endpoint_helper():
    url = os.environ.get("CYBERCASE_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set CYBERCASE_TEST_DATABASE_URL to run PostgreSQL integration tests")

    async def exercise():
        async with isolated_database() as factory:
            case_id = uuid4()

            async with factory() as db, db.begin():
                case = Case(id=case_id, title="Dedicated Endpoint Case")
                db.add(case)
                db.add(ChatThread(id=case_id, case_id=case_id, title=case.title))
                source = await CaseMaterialsService(db).admitText(
                    case_id=case_id,
                    user_id=None,
                    source_kind="narrative",
                    exact_text="Server compromised via SSH.",
                    provenance_json={"origin": "analyst"},
                )
                source_id = source.id

            async with factory() as db, db.begin():
                run_1 = await enqueue_case_analysis(
                    db,
                    case_id=case_id,
                    user_id=None,
                    request=CaseAnalysisCreate(idempotency_key="run-ssh-followup"),
                )
                run_1_id = run_1.id

            async with factory() as db:
                claimed_1 = await claimCaseRun(db, run_1_id, "worker-ssh")

            async with factory() as db:
                snapshot_1 = await db.get(CaseEvidenceSnapshot, claimed_1.snapshot_id)
                output_1 = _make_output(
                    snapshot_1,
                    source_id,
                    "Server compromised via SSH.",
                    followup_question="Which user account was accessed?",
                )

            async with factory() as db:
                assert await complete_case_run(db, run_1_id, claimed_1.attempt_count, output_1)

            # Retrieve pending clarification
            async with factory() as db:
                clarifications = await get_owned_clarifications(db, case_id)
                assert len(clarifications) == 1
                q_id = clarifications[0].id

            # Answer via submit_clarification_answer
            async with factory() as db, db.begin():
                result_read, clarif_run = await submit_clarification_answer(
                    db,
                    case_id=case_id,
                    clarification_id=q_id,
                    user_id=None,
                    request=CaseClarificationAnswer(
                        answer="Account was root.",
                        idempotency_key="ssh-root-answer",
                    ),
                )
                assert result_read.id == q_id
                assert result_read.state == "answered"
                assert result_read.answer_message_id is not None
                assert clarif_run.operation == "analysis"

            # Verify underlying ChatMessage and EvidenceSource
            async with factory() as db:
                ans_msg = await db.scalar(
                    select(ChatMessage).where(
                        ChatMessage.thread_id == case_id,
                        ChatMessage.message_kind == "followup_answer",
                    )
                )
                assert ans_msg is not None
                assert ans_msg.content == "Account was root."
                assert ans_msg.in_reply_to_message_id == q_id

                ev_src = await db.scalar(
                    select(EvidenceSource).where(
                        EvidenceSource.case_id == case_id,
                        EvidenceSource.source_kind == "followup_answer",
                    )
                )
                assert ev_src is not None
                assert ev_src.origin_message_id == ans_msg.id

    asyncio.run(exercise())
