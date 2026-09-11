import asyncio
import hashlib
from uuid import uuid4

import pytest
from fastapi import status

from app.models import Case, CaseAnalysisResult, ChatThread
from app.models.caseMaterials import CaseEvidenceSnapshot
from app.routers.caseReports import _report_http_error
from app.schemas.caseRuns import CaseAnalysisCreate
from app.schemas.reports import CaseReportCreate
from app.services.case_analysis.contracts import (
    CaseAnalysisClaim,
    CaseAnalysisResult as AnalysisOutput,
    CaseAnalysisTrace,
    CaseEvidenceCitation,
)
from app.services.case_materials import CaseMaterialsService
from app.services.reports.case_report_persistence import (
    CaseReportService,
    build_case_report_snapshot,
)
from app.services.reports.report_contracts import ReportGenerationConflict
from app.services.workflow.caseRunClaim import claimCaseRun
from app.services.workflow.caseRunCompletion import complete_case_run
from app.services.workflow.caseRunService import enqueue_case_analysis
from run_recovery_support import isolated_database


def test_build_case_report_snapshot_rejects_stale_analysis() -> None:
    case_id = uuid4()
    thread_id = case_id
    analysis_id = uuid4()
    snapshot_id = uuid4()

    case = Case(
        id=case_id,
        title="Stale Report Test",
        evidence_revision=2,
        latest_analysis_result_id=analysis_id,
    )
    thread = ChatThread(id=thread_id, title="Thread")

    evidence_text = "[SOURCE s1]\nFact."
    evidence_sha = hashlib.sha256(evidence_text.encode()).hexdigest()
    stale_snapshot = CaseEvidenceSnapshot(
        id=snapshot_id,
        case_id=case_id,
        evidence_revision=1,  # Stale: revision 1 vs case revision 2
        format_version="case_evidence_snapshot_v1",
        input_text=evidence_text,
        text_sha256=evidence_sha,
        manifest_sha256="0" * 64,
        manifest_json=[
            {
                "source_id": "s1",
                "source_kind": "narrative",
                "revision_id": str(uuid4()),
                "revision": 1,
                "exact_text": "Fact.",
                "text_sha256": hashlib.sha256(b"Fact.").hexdigest(),
                "provenance": {},
            }
        ],
    )
    result = CaseAnalysisResult(
        id=analysis_id,
        case_id=case_id,
        snapshot_id=snapshot_id,
        status="validated",
        answer="Answer",
        summary="Summary",
        trace_json={
            "version": "case_analysis_trace_v1",
            "validation_status": "validated",
            "analysis_mode": "case_overview",
            "summary": "Summary",
            "claims": [],
            "gaps": [],
            "mitre_associations": [],
            "evidence_sha256": evidence_sha,
        },
    )
    result.snapshot = stale_snapshot

    with pytest.raises(ReportGenerationConflict) as exc_info:
        build_case_report_snapshot(case, result, thread)

    assert exc_info.value.code == "case_analysis_stale"
    assert "older evidence" in exc_info.value.message.lower()


def test_build_case_report_snapshot_allows_current_analysis() -> None:
    case_id = uuid4()
    thread_id = case_id
    analysis_id = uuid4()
    snapshot_id = uuid4()

    case = Case(
        id=case_id,
        title="Current Report Test",
        evidence_revision=1,
        latest_analysis_result_id=analysis_id,
    )
    thread = ChatThread(id=thread_id, title="Thread")

    source_uuid = uuid4()
    evidence_text = f"[SOURCE {source_uuid}]\nFact."
    evidence_sha = hashlib.sha256(evidence_text.encode()).hexdigest()
    manifest = [
        {
            "source_id": str(source_uuid),
            "source_kind": "narrative",
            "revision_id": str(uuid4()),
            "revision": 1,
            "exact_text": "Fact.",
            "text_sha256": hashlib.sha256(b"Fact.").hexdigest(),
            "provenance": {},
        }
    ]
    from app.services.case_materials import canonicalJson

    manifest_sha = hashlib.sha256(canonicalJson(manifest).encode()).hexdigest()

    current_snapshot = CaseEvidenceSnapshot(
        id=snapshot_id,
        case_id=case_id,
        evidence_revision=1,  # Current: revision 1 matches case revision 1
        format_version="case_evidence_snapshot_v1",
        input_text=evidence_text,
        text_sha256=evidence_sha,
        manifest_sha256=manifest_sha,
        manifest_json=manifest,
    )
    result = CaseAnalysisResult(
        id=analysis_id,
        case_id=case_id,
        snapshot_id=snapshot_id,
        status="validated",
        answer="Answer",
        summary="Summary",
        trace_json={
            "version": "case_analysis_trace_v1",
            "validation_status": "validated",
            "analysis_mode": "case_overview",
            "summary": "Summary",
            "claims": [],
            "gaps": [],
            "mitre_associations": [],
            "evidence_sha256": evidence_sha,
        },
    )
    result.snapshot = current_snapshot

    snapshot_report = build_case_report_snapshot(case, result, thread)
    assert snapshot_report.evidence_revision == 1
    assert snapshot_report.analysis_result_id == analysis_id


def test_stale_report_conflict_maps_to_http_409() -> None:
    error = ReportGenerationConflict(
        "case_analysis_stale",
        "The selected Case analysis is based on older evidence. Re-run analysis before generating a report.",
    )
    http_exc = _report_http_error(error)
    assert http_exc.status_code == status.HTTP_409_CONFLICT
    assert http_exc.detail == {
        "code": "case_analysis_stale",
        "message": "The selected Case analysis is based on older evidence. Re-run analysis before generating a report.",
    }


def test_stale_analysis_blocks_new_report_while_existing_reports_remain_readable_postgres():
    async def exercise():
        async with isolated_database() as factory:
            case_id = uuid4()
            async with factory() as db, db.begin():
                db.add(Case(id=case_id, title="Stale guard test case"))
                source = await CaseMaterialsService(db).admitText(
                    case_id=case_id,
                    user_id=None,
                    source_kind="narrative",
                    exact_text="Initial statement.",
                    provenance_json={"origin": "narrative"},
                )
                source_id = source.id

            # Complete analysis for revision 1
            async with factory() as db, db.begin():
                run = await enqueue_case_analysis(
                    db,
                    case_id=case_id,
                    user_id=None,
                    request=CaseAnalysisCreate(idempotency_key="run-1", expected_evidence_revision=1),
                )
                run_id = run.id

            async with factory() as db:
                claimed = await claimCaseRun(db, run_id, "worker-1")
            assert claimed is not None

            quote = "Initial statement."
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
                    evidence_sha256=claimed.text_sha256,
                ),
            )
            async with factory() as db:
                await complete_case_run(db, run_id, claimed.attempt_count, output)

            # Generate Report 1 from current analysis
            async with factory() as db:
                report1 = await CaseReportService(db).generate_report(
                    case_id,
                    CaseReportCreate(idempotency_key="report-1"),
                    user_id=None,
                )
                assert report1.version_number == 1
                report1_id = report1.report_id

            # Add new evidence to case -> case.evidence_revision becomes 2
            async with factory() as db, db.begin():
                await CaseMaterialsService(db).admitText(
                    case_id=case_id,
                    user_id=None,
                    source_kind="narrative",
                    exact_text="Second statement added later.",
                    provenance_json={"origin": "narrative"},
                )

            # Attempting to generate a new report from now-stale analysis must fail
            async with factory() as db:
                with pytest.raises(ReportGenerationConflict) as exc_info:
                    await CaseReportService(db).generate_report(
                        case_id,
                        CaseReportCreate(idempotency_key="report-2"),
                        user_id=None,
                    )
                assert exc_info.value.code == "case_analysis_stale"

            # Historical Report 1 remains readable!
            async with factory() as db:
                historical = await CaseReportService(db).get_report(
                    case_id=case_id,
                    report_id=report1_id,
                    user_id=None,
                )
                assert historical.report_id == report1_id
                assert historical.version_number == 1

                all_reports = await CaseReportService(db).list_reports(
                    case_id=case_id,
                    user_id=None,
                )
                assert len(all_reports) == 1
                assert all_reports[0].report_id == report1_id

    asyncio.run(exercise())
