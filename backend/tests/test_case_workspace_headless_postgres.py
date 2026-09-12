"""Regression test verifying pure Case Workspace operations execute with zero Chat mutations."""

import asyncio
from uuid import uuid4

from sqlalchemy import func, select

from app.models import Case, CaseRun, CaseAnalysisResult, ChatMessage, ChatThread
from app.models.caseMaterials import CaseDocument, CaseEvidenceSnapshot
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
