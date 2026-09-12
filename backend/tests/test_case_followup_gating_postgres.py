from __future__ import annotations

import asyncio
from uuid import UUID

from sqlalchemy import select

from app.models.case import Case
from app.models.caseMaterials import CaseEvidenceSnapshot
from app.models.caseRun import CaseAnalysisResult, CaseRun
from app.models.chat import ChatMessage, ChatThread
from app.schemas.caseRuns import CaseAnalysisCreate
from app.schemas.caseClarifications import CaseClarificationAnswer
from app.services.case_analysis.contracts import (
    CaseAnalysisClaim,
    CaseAnalysisGap,
    CaseAnalysisResult as AnalysisOutput,
    CaseAnalysisTrace,
    CaseEvidenceCitation,
)
from app.services.case_materials import CaseMaterialsService
from app.services.followup.caseClarification import (
    get_owned_clarifications,
    submit_clarification_answer,
)
from app.services.workflow.caseRunClaim import claimCaseRun
from app.services.workflow.caseRunCompletion import complete_case_run
from app.services.workflow.caseRunService import enqueue_case_analysis
from run_recovery_support import isolated_database


async def _setup_case(factory) -> tuple[UUID, UUID]:
    async with factory() as db, db.begin():
        case = Case(title="Followup Gating Case", user_id=None)
        db.add(case)
        await db.flush()
        source = await CaseMaterialsService(db).admitText(
            case_id=case.id,
            user_id=None,
            source_kind="narrative",
            exact_text="The security team detected unauthorized access from an unknown IP.",
            provenance_json={"origin": "test"},
        )
        return case.id, source.id


def _make_trace(snapshot, source_id, *, with_gap: bool) -> CaseAnalysisTrace:
    quote = "The security team detected unauthorized access from an unknown IP."
    gaps = []
    if with_gap:
        gaps.append(
            CaseAnalysisGap(
                gap_id="G-01",
                topic="External IP Address",
                status="NOT_PROVIDED",
                description="The external IP address communicating with the host is unknown.",
                affected_claim_ids=["A-01"],
                reason="The IP address is necessary to establish technical attribution.",
                priority="high",
                askable=True,
            )
        )
    return CaseAnalysisTrace(
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
        gaps=gaps,
        evidence_sha256=snapshot.text_sha256,
    )


def test_followup_gates_analysis_result_message_and_attaches_gap_why():
    async def exercise():
        async with isolated_database() as factory:
            case_id, source_id = await _setup_case(factory)

            # Step 1: Run initial analysis that produces a follow-up question
            async with factory() as db, db.begin():
                run = await enqueue_case_analysis(
                    db,
                    case_id=case_id,
                    user_id=None,
                    request=CaseAnalysisCreate(
                        idempotency_key="initial-run",
                        response_language="english",
                        expected_evidence_revision=1,
                    ),
                )
                run_id = run.id

            async with factory() as db:
                claimed = await claimCaseRun(db, run_id, "worker-1")
                assert claimed is not None
                snapshot = await db.get(CaseEvidenceSnapshot, claimed.snapshot_id)

            trace_with_gap = _make_trace(snapshot, source_id, with_gap=True)
            output_with_followup = AnalysisOutput(
                answer="Preliminary analysis: unauthorized access detected.",
                trace=trace_with_gap,
                execution_receipt={"test": "followup-gating"},
                followup_question="What was the external IP address?",
                followup_metadata={"gap_id": "G-01", "topic": "External IP Address", "gap_key": "G-01:external_ip"},
            )

            async with factory() as db:
                assert await complete_case_run(db, run_id, claimed.attempt_count, output_with_followup)

            # Assertions after initial run with follow-up:
            async with factory() as db:
                thread = await db.scalar(select(ChatThread).where(ChatThread.case_id == case_id))
                assert thread is not None
                assert thread.status == "awaiting_followup"
                messages = list((await db.scalars(select(ChatMessage).where(ChatMessage.thread_id == thread.id).order_by(ChatMessage.ordinal))).all())
                # Analysis result message MUST NOT be posted yet
                assert len(messages) == 1
                assert messages[0].message_kind == "followup_question"
                assert messages[0].content == "What was the external IP address?"
                # Chat followup metadata must contain complete gap explanation
                chat_followup = messages[0].metadata_json.get("chat_followup")
                assert chat_followup is not None
                assert chat_followup["kind"] == "clarification"
                detail = chat_followup["selected_gap_detail"]
                assert detail["topic"] == "External IP Address"
                assert detail["status"] == "NOT_PROVIDED"
                assert "unknown" in detail["description"]
                assert "technical attribution" in detail["reason"]
                assert "A-01" in detail["affects"]
                assert detail["priority"] == "high"
                assert detail["askable"] is True

                clarifications = await get_owned_clarifications(db, case_id)
                assert len(clarifications) == 1
                clarification = clarifications[0]
                assert clarification.state == "pending"

            # Step 2: Analyst submits clarification answer
            request = CaseClarificationAnswer(
                answer="The external IP address was 198.51.100.24.",
                idempotency_key="answer-ip",
                response_language="english",
            )
            async with factory() as db, db.begin():
                answered_clarification, next_run = await submit_clarification_answer(
                    db,
                    case_id=case_id,
                    clarification_id=clarification.id,
                    user_id=None,
                    request=request,
                )
                assert answered_clarification.state == "answered"
                next_run_id = next_run.id

            # Step 3: Worker executes subsequent analysis run, which succeeds without follow-up
            async with factory() as db:
                claimed_next = await claimCaseRun(db, next_run_id, "worker-2")
                assert claimed_next is not None
                next_snapshot = await db.get(CaseEvidenceSnapshot, claimed_next.snapshot_id)

            trace_complete = _make_trace(next_snapshot, source_id, with_gap=False)
            output_completed = AnalysisOutput(
                answer="Final complete analysis: unauthorized access confirmed from 198.51.100.24.",
                trace=trace_complete,
                execution_receipt={"test": "followup-complete"},
                followup_question=None,
                followup_metadata=None,
            )

            async with factory() as db:
                assert await complete_case_run(db, next_run_id, claimed_next.attempt_count, output_completed)

            # Assertions after final run:
            async with factory() as db:
                thread = await db.scalar(select(ChatThread).where(ChatThread.case_id == case_id))
                assert thread is not None
                assert thread.status == "answered"
                final_messages = list((await db.scalars(select(ChatMessage).where(ChatMessage.thread_id == thread.id).order_by(ChatMessage.ordinal))).all())
                # Should have 2 messages in order:
                # 1. followup_question (assistant)
                # 2. followup_answer (user clarification answer)
                assert len(final_messages) == 2
                assert [m.message_kind for m in final_messages] == ["followup_question", "followup_answer"]
                assert [m.role for m in final_messages] == ["assistant", "user"]

    asyncio.run(exercise())
