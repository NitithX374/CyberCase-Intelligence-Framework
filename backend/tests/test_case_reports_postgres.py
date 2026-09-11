import asyncio
from uuid import uuid4

import pytest
from sqlalchemy import func, select

from app.models import Case, CaseAnalysisResult, ChatMessage, ChatReport
from app.models.caseMaterials import CaseEvidenceSnapshot
from app.schemas.caseRuns import CaseAnalysisCreate
from app.schemas.reports import CaseReportCreate
from app.services.case_analysis.contracts import (
    CaseAnalysisClaim,
    CaseAnalysisResult as AnalysisOutput,
    CaseAnalysisTrace,
    CaseEvidenceCitation,
)
from app.services.case_materials import CaseMaterialsService
from app.services.chat import ChatService
from app.services.reports.case_report_persistence import CaseReportService
from app.services.reports.report_contracts import ReportGenerationConflict
from app.services.workflow.caseRunClaim import claimCaseRun
from app.services.workflow.caseRunCompletion import complete_case_run
from app.services.workflow.caseRunService import enqueue_case_analysis
from run_recovery_support import isolated_database


async def _case_with_source(factory):
    case_id = uuid4()
    async with factory() as db, db.begin():
        db.add(Case(id=case_id, title="Report case"))
        source = await CaseMaterialsService(db).admitText(
            case_id=case_id,
            user_id=None,
            source_kind="narrative",
            exact_text="The witness reported a blue vehicle.",
            provenance_json={"origin": "analyst-authored"},
        )
        return case_id, source.id


async def _complete(factory, case_id, source_id, key):
    async with factory() as db, db.begin():
        run = await enqueue_case_analysis(
            db,
            case_id=case_id,
            user_id=None,
            request=CaseAnalysisCreate(idempotency_key=key, expected_evidence_revision=1),
        )
        run_id = run.id
    async with factory() as db:
        claimed = await claimCaseRun(db, run_id, f"worker-{key}")
    assert claimed is not None
    async with factory() as db:
        snapshot = await db.get(CaseEvidenceSnapshot, claimed.snapshot_id)
    quote = "The witness reported a blue vehicle."
    output = AnalysisOutput(
        answer=quote,
        trace=CaseAnalysisTrace(
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
        ),
    )
    async with factory() as db:
        assert await complete_case_run(db, run_id, claimed.attempt_count, output)
    async with factory() as db:
        return await db.scalar(select(CaseAnalysisResult).where(CaseAnalysisResult.run_id == run_id))


def test_case_report_is_bound_to_selected_native_result_and_snapshot():
    async def exercise():
        async with isolated_database() as factory:
            case_id, source_id = await _case_with_source(factory)
            result = await _complete(factory, case_id, source_id, "report-result")
            async with factory() as db:
                service = CaseReportService(db)
                report = await service.generate_report(
                    case_id,
                    CaseReportCreate(idempotency_key="report-idempotency"),
                    None,
                )
                repeated = await service.generate_report(
                    case_id,
                    CaseReportCreate(idempotency_key="report-idempotency"),
                    None,
                )
                pdf, filename = await service.get_report_pdf(case_id, report.report_id, None)
            assert result is not None
            assert report.report is not None
            assert filename.endswith(".pdf")
            assert pdf.startswith(b"%PDF")
            assert len(pdf) > 512
            assert report.source_reference_type == "case_evidence"
            assert report.analysis_result_id == result.id
            assert report.evidence_snapshot_id == result.snapshot_id
            assert report.analysis_message_id is None
            assert report.report.claims[0].source_message_ids == []
            assert report.report.claims[0].source_evidence_ids == [str(source_id)]
            assert repeated.report_id == report.report_id
            async with factory() as db:
                stored = await db.get(ChatReport, report.report_id)
                assert stored is not None
                assert stored.case_id == case_id
                assert stored.analysis_result_id == result.id
                assert stored.evidence_snapshot_id == result.snapshot_id
                assert await db.scalar(select(func.count()).select_from(ChatReport)) == 1

    asyncio.run(exercise())


def test_case_report_reuses_old_result_snapshot_after_new_evidence():
    async def exercise():
        async with isolated_database() as factory:
            case_id, source_id = await _case_with_source(factory)
            result = await _complete(factory, case_id, source_id, "old-result")
            # Generate report from current analysis
            async with factory() as db:
                report = await CaseReportService(db).generate_report(
                    case_id,
                    CaseReportCreate(analysis_result_id=result.id, idempotency_key="old-result-report"),
                    None,
                )
            # Admit new evidence, bumping evidence revision
            async with factory() as db, db.begin():
                await CaseMaterialsService(db).admitText(
                    case_id=case_id,
                    user_id=None,
                    source_kind="narrative",
                    exact_text="A second document mentions a red bicycle.",
                    provenance_json={"origin": "analyst-authored"},
                )
            # Attempting to generate a new report from now-stale analysis must be rejected
            async with factory() as db:
                with pytest.raises(ReportGenerationConflict) as exc_info:
                    await CaseReportService(db).generate_report(
                        case_id,
                        CaseReportCreate(analysis_result_id=result.id, idempotency_key="stale-report-attempt"),
                        None,
                    )
                assert exc_info.value.code == "case_analysis_stale"

            # Historical report generated before new evidence remains readable
            snapshot = report.source_snapshot
            assert snapshot is not None
            assert report.analysis_result_id == result.id
            assert report.evidence_snapshot_id == result.snapshot_id
            assert len(snapshot["sources"]) == 1
            assert snapshot["sources"][0]["source_id"] == str(source_id)
            assert report.report is not None
            assert all(
                claim.source_message_ids == [] for claim in report.report.claims
            )

    asyncio.run(exercise())


def test_chat_removal_preserves_case_report_and_history():
    async def exercise():
        async with isolated_database() as factory:
            case_id, source_id = await _case_with_source(factory)
            result = await _complete(factory, case_id, source_id, "delete-report")
            async with factory() as db:
                report = await CaseReportService(db).generate_report(
                    case_id,
                    CaseReportCreate(idempotency_key="delete-report"),
                    None,
                )
            async with factory() as db:
                await ChatService(db).delete_thread(case_id, user_id=None)
            async with factory() as db:
                saved = await CaseReportService(db).get_report(case_id, report.report_id, None)
                assert saved.thread_id is None
                assert saved.analysis_result_id == result.id
                assert saved.evidence_snapshot_id == result.snapshot_id
                assert await db.get(Case, case_id) is not None
                assert await db.get(CaseAnalysisResult, result.id) is not None
                assert await db.scalar(select(func.count()).select_from(ChatMessage)) == 0

    asyncio.run(exercise())
