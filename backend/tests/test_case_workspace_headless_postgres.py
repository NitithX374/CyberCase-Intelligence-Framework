"""Regression test verifying pure Case Workspace operations execute with zero Chat mutations."""

import asyncio
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.models import Case, CaseRun, CaseAnalysisResult, ChatMessage, ChatThread
from app.models.caseMaterials import CaseDocument, CaseEvidenceSnapshot, EvidenceRevision, EvidenceSource
from app.models.report import CaseReport
from app.schemas.caseRuns import CaseAnalysisCreate
from app.schemas.reports import CaseReportCreate
from app.services.case_materials import CaseMaterialsService
from app.services.reports.case_report_persistence import CaseReportService
from app.services.workflow.caseRunCompletion import complete_case_run
from app.services.workflow.caseRunExecution import claimCaseRun
from app.services.workflow.caseRunService import enqueue_case_analysis
from run_recovery_support import isolated_database
from test_case_chat_postgres import _output


def test_headless_case_workspace_never_instantiates_chat():
    """Verify that document ingestion, evidence admission, analysis, report generation,

    and clarification queries run end-to-end without creating any ChatThread or ChatMessage rows.
    """
    async def exercise():
        async with isolated_database() as factory:
            case_id = uuid4()
            user_id = None

            # 1. Create Case
            async with factory() as db, db.begin():
                db.add(Case(id=case_id, title="Headless Workspace Investigation", user_id=user_id))

            # 2. Add Document & Admit Evidence
            async with factory() as db, db.begin():
                materials = CaseMaterialsService(db)
                doc = await materials.addDocument(
                    case_id=case_id,
                    user_id=user_id,
                    filename="incident_report.txt",
                    mime_type="text/plain",
                    content=b"The witness reported a blue vehicle.",
                    extraction={
                        "provider": "test",
                        "config_json": {},
                        "extracted_text": "The witness reported a blue vehicle.",
                        "provenance_json": {"pages": [{"page_number": 1}]},
                        "warnings_json": [],
                    },
                )
                source = await materials.admitExtraction(
                    case_id=case_id,
                    user_id=user_id,
                    extraction_id=doc.extractions[0].id,
                )
                assert source is not None

            # 3. Enqueue Case Analysis
            async with factory() as db, db.begin():
                run = await enqueue_case_analysis(
                    db,
                    case_id=case_id,
                    user_id=user_id,
                    request=CaseAnalysisCreate(idempotency_key="headless-analysis-1"),
                )
                assert run.operation == "analysis"
                assert run.request_message_id is None

            # 4. Worker claims and completes Analysis (headless, no follow-up)
            async with factory() as db:
                claimed = await claimCaseRun(db, run.id, "worker-headless")
                assert claimed is not None

            async with factory() as db:
                snapshot = await db.get(CaseEvidenceSnapshot, claimed.snapshot_id)
                output = _output(snapshot, str(source.id), mode="case_overview", followup=False)

            async with factory() as db:
                completed = await complete_case_run(
                    db,
                    run.id,
                    claimed.attempt_count,
                    output,
                )
                assert completed is True

            # 5. Generate Preliminary Report & PDF
            async with factory() as db:
                report_service = CaseReportService(db)
                report_read = await report_service.generate_report(
                    case_id,
                    CaseReportCreate(idempotency_key="headless-report-1"),
                    user_id,
                )
                assert report_read.persistence_status == "completed"
                pdf_bytes, filename = await report_service.get_report_pdf(
                    case_id,
                    report_read.report_id,
                    user_id,
                )
                assert len(pdf_bytes) > 0
                assert filename.endswith(".pdf")

            # 6. Verify Database Invariants: ChatThread and ChatMessage remain strictly ZERO
            async with factory() as db:
                thread_count = await db.scalar(
                    select(func.count()).select_from(ChatThread).where(ChatThread.case_id == case_id)
                )
                message_count = await db.scalar(
                    select(func.count()).select_from(ChatMessage)
                )
                report_count = await db.scalar(
                    select(func.count()).select_from(CaseReport).where(CaseReport.case_id == case_id)
                )
                analysis_count = await db.scalar(
                    select(func.count()).select_from(CaseAnalysisResult).where(CaseAnalysisResult.case_id == case_id)
                )

                assert thread_count == 0, f"Expected 0 ChatThreads, found {thread_count}"
                assert message_count == 0, f"Expected 0 ChatMessages, found {message_count}"
                assert report_count == 1, f"Expected 1 CaseReport, found {report_count}"
                assert analysis_count == 1, f"Expected 1 CaseAnalysisResult, found {analysis_count}"

    asyncio.run(exercise())


def test_case_analysis_followup_creates_thread_and_binds_question():
    """Verify cases B, D, E, F:
    B. Analysis with followup=True and no existing Chat:
       -> 1 ChatThread created
       -> 1 followup_question ChatMessage created immediately
       -> question.analysis_result_id == AnalysisResult.id
    E. Re-opening Chat after follow-up creation:
       -> must NOT create duplicate follow-up questions
    F. Clarification IDs remain stable and correspond to real persisted question messages.
    D. Submitting follow-up answer:
       -> answer.in_reply_to_message_id == followup_question.id
       -> answer.analysis_result_id == followup_question.analysis_result_id
       -> answer admitted as Case Evidence
       -> new evidence revision
       -> new analysis run
    """
    from app.models.caseMaterials import EvidenceSource
    from app.schemas.caseClarifications import CaseClarificationAnswer
    from app.services.chat.chatService import ChatService
    from app.services.followup.caseClarification import get_owned_clarifications, submit_clarification_answer

    async def exercise():
        async with isolated_database() as factory:
            case_id = uuid4()
            user_id = None

            # 1. Create Case
            async with factory() as db, db.begin():
                db.add(Case(id=case_id, title="Workspace with Followup", user_id=user_id))

            # 2. Add Document & Admit Evidence
            async with factory() as db, db.begin():
                materials = CaseMaterialsService(db)
                doc = await materials.addDocument(
                    case_id=case_id,
                    user_id=user_id,
                    filename="incident_report.txt",
                    mime_type="text/plain",
                    content=b"The witness reported a blue vehicle.",
                    extraction={
                        "provider": "test",
                        "config_json": {},
                        "extracted_text": "The witness reported a blue vehicle.",
                        "provenance_json": {"pages": [{"page_number": 1}]},
                        "warnings_json": [],
                    },
                )
                source = await materials.admitExtraction(
                    case_id=case_id,
                    user_id=user_id,
                    extraction_id=doc.extractions[0].id,
                )
                assert source is not None

            # 3. Enqueue Case Analysis
            async with factory() as db, db.begin():
                run = await enqueue_case_analysis(
                    db,
                    case_id=case_id,
                    user_id=user_id,
                    request=CaseAnalysisCreate(idempotency_key="analysis-followup-b"),
                )

            # 4. Worker claims and completes Analysis WITH follow-up
            async with factory() as db:
                claimed = await claimCaseRun(db, run.id, "worker-followup")
                assert claimed is not None

            async with factory() as db:
                snapshot = await db.get(CaseEvidenceSnapshot, claimed.snapshot_id)
                output = _output(snapshot, str(source.id), mode="case_overview", followup=True)

            async with factory() as db:
                completed = await complete_case_run(
                    db,
                    run.id,
                    claimed.attempt_count,
                    output,
                )
                assert completed is True

            # Case B Assertions:
            # - exactly 1 ChatThread created
            # - exactly 1 followup_question ChatMessage created immediately
            # - question.analysis_result_id == analysis.id
            async with factory() as db:
                analysis = await db.scalar(
                    select(CaseAnalysisResult).where(CaseAnalysisResult.case_id == case_id)
                )
                assert analysis is not None

                thread = await db.scalar(
                    select(ChatThread).where(ChatThread.case_id == case_id)
                )
                assert thread is not None

                messages = list((await db.scalars(
                    select(ChatMessage).where(ChatMessage.thread_id == thread.id).order_by(ChatMessage.ordinal)
                )).all())
                assert len(messages) == 1
                question = messages[0]
                assert question.message_kind == "followup_question"
                assert question.role == "assistant"
                assert question.analysis_result_id == analysis.id
                assert question.content == output.followup_question.strip()

                # Case F: Clarification IDs remain stable and correspond to real persisted question messages
                clarifications = await get_owned_clarifications(db, case_id=case_id)
                assert len(clarifications) == 1
                assert clarifications[0].id == question.id
                assert clarifications[0].question_message_id == question.id
                assert clarifications[0].origin_analysis_result_id == analysis.id
                assert clarifications[0].state == "pending"

                # Case E: Re-opening Chat after follow-up creation must NOT create duplicate follow-up questions
                reopened_thread = await ChatService(db).ensureThreadForCase(case_id, user_id)
                assert reopened_thread.id == thread.id
                messages_after_reopen = list((await db.scalars(
                    select(ChatMessage).where(ChatMessage.thread_id == thread.id).order_by(ChatMessage.ordinal)
                )).all())
                assert len(messages_after_reopen) == 1

            # Case D: Submitting follow-up answer
            async with factory() as db, db.begin():
                clarification_read, answer_run = await submit_clarification_answer(
                    db,
                    case_id=case_id,
                    clarification_id=question.id,
                    user_id=user_id,
                    request=CaseClarificationAnswer(
                        answer="The suspect was wearing a dark jacket.",
                        idempotency_key="clarification-answer-1",
                    ),
                )
                assert clarification_read is not None
                assert clarification_read.state == "answered"
                assert answer_run.status == "queued"
                assert answer_run.operation == "analysis"

            async with factory() as db:
                # Answer message checks:
                answer_message = await db.get(ChatMessage, clarification_read.answer_message_id)
                assert answer_message is not None
                assert answer_message.message_kind in ("followup_answer", "clarification_answer")
                assert answer_message.in_reply_to_message_id == question.id
                assert answer_message.analysis_result_id == question.analysis_result_id

                # Answer admitted as Case Evidence:
                case = await db.get(Case, case_id)
                assert case.evidence_revision == 2

                evidence = await db.scalar(
                    select(EvidenceSource)
                    .options(selectinload(EvidenceSource.revisions))
                    .where(EvidenceSource.id == clarification_read.answer_evidence_source_id)
                )
                assert evidence is not None
                assert evidence.source_kind == "followup_answer"
                assert len(evidence.revisions) == 1
                assert evidence.revisions[0].exact_text == "The suspect was wearing a dark jacket."

    asyncio.run(exercise())


def test_case_analysis_followup_reuses_existing_thread():
    """Verify Case C:
    C. Analysis with followup=True and existing Chat:
       -> reuse existing ChatThread
       -> append exactly one followup_question
    """
    async def exercise():
        async with isolated_database() as factory:
            case_id = uuid4()
            user_id = None

            # 1. Create Case and pre-existing ChatThread
            async with factory() as db, db.begin():
                case = Case(id=case_id, title="Pre-existing Thread Case", user_id=user_id)
                db.add(case)
                await db.flush()
                thread = ChatThread(case_id=case_id, title=case.title, user_id=user_id)
                db.add(thread)
                await db.flush()
                thread_id = thread.id

            # 2. Add Document & Admit Evidence
            async with factory() as db, db.begin():
                materials = CaseMaterialsService(db)
                doc = await materials.addDocument(
                    case_id=case_id,
                    user_id=user_id,
                    filename="incident_report.txt",
                    mime_type="text/plain",
                    content=b"The witness reported a blue vehicle.",
                    extraction={
                        "provider": "test",
                        "config_json": {},
                        "extracted_text": "The witness reported a blue vehicle.",
                        "provenance_json": {"pages": [{"page_number": 1}]},
                        "warnings_json": [],
                    },
                )
                source = await materials.admitExtraction(
                    case_id=case_id,
                    user_id=user_id,
                    extraction_id=doc.extractions[0].id,
                )
                assert source is not None

            # 3. Enqueue Case Analysis
            async with factory() as db, db.begin():
                run = await enqueue_case_analysis(
                    db,
                    case_id=case_id,
                    user_id=user_id,
                    request=CaseAnalysisCreate(idempotency_key="analysis-followup-c"),
                )

            # 4. Worker claims and completes Analysis WITH follow-up
            async with factory() as db:
                claimed = await claimCaseRun(db, run.id, "worker-followup-c")
                assert claimed is not None

            async with factory() as db:
                snapshot = await db.get(CaseEvidenceSnapshot, claimed.snapshot_id)
                output = _output(snapshot, str(source.id), mode="case_overview", followup=True)

            async with factory() as db:
                completed = await complete_case_run(
                    db,
                    run.id,
                    claimed.attempt_count,
                    output,
                )
                assert completed is True

            # Assertions for Case C:
            # - ChatThread count is still 1
            # - the thread is the pre-existing thread
            # - exactly one followup_question appended
            async with factory() as db:
                thread_count = await db.scalar(
                    select(func.count()).select_from(ChatThread).where(ChatThread.case_id == case_id)
                )
                assert thread_count == 1

                analysis = await db.scalar(
                    select(CaseAnalysisResult).where(CaseAnalysisResult.case_id == case_id)
                )
                messages = list((await db.scalars(
                    select(ChatMessage).where(ChatMessage.thread_id == thread_id).order_by(ChatMessage.ordinal)
                )).all())
                assert len(messages) == 1
                assert messages[0].message_kind == "followup_question"
                assert messages[0].analysis_result_id == analysis.id

    asyncio.run(exercise())
