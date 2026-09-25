import asyncio
import threading

import pytest
from case_chat_support import NARRATIVE, SETTLED, seeded_case
from isolated_database import isolated_database
from sqlalchemy import select

from app.models.analysis import CaseAnalysisResult
from app.models.report import CaseReport
from app.schemas.reports import CaseReportCreate
from app.services.analysis.contracts import followup_snapshot
from app.services.cases.ownership import owned_case
from app.services.reports import persistence
from app.services.reports.contracts import ReportGenerationConflict
from app.services.reports.persistence import CaseReportService
from app.services.sources.case_source_bundle import WITH_SOURCES, analysable_bundle, sources_read


async def reported_case(session_factory):
    case_id, user_id, _ = await seeded_case(session_factory, trace=SETTLED, asking=False)
    async with session_factory() as db, db.begin():
        bundle = analysable_bundle(await owned_case(db, case_id, user_id, options=WITH_SOURCES))
        analysis = await db.scalar(
            select(CaseAnalysisResult).where(CaseAnalysisResult.case_id == case_id)
        )
        analysis.external_context_json = {
            "sources_read": sources_read(bundle),
            "followup_history": followup_snapshot(()),
        }
    async with session_factory() as db:
        report = await CaseReportService(db).generate_report(case_id, CaseReportCreate(), user_id)
    return case_id, user_id, report


def test_the_document_is_printed_from_what_was_stored_not_from_the_analysis_row():
    async def exercise():
        async with isolated_database() as session_factory:
            case_id, user_id, report = await reported_case(session_factory)
            assert report.report.title == "Seeded case"
            assert report.report.summary == NARRATIVE

            async with session_factory() as db, db.begin():
                analysis = await db.scalar(
                    select(CaseAnalysisResult).where(CaseAnalysisResult.case_id == case_id)
                )
                analysis.summary = "Rewritten after the report was issued."
                analysis.external_context_json = {}

            async with session_factory() as db:
                html = await CaseReportService(db).get_report_html(
                    case_id, report.report_id, user_id
                )
                [listed] = await CaseReportService(db).list_reports(case_id, user_id)

            assert NARRATIVE in html
            assert "Rewritten after the report was issued." not in html
            assert listed.report == report.report

    asyncio.run(exercise())


def test_the_pdf_is_laid_out_off_the_event_loop(monkeypatch):
    threads = []

    def render(report, issue):
        threads.append(threading.current_thread())
        return b"%PDF-"

    monkeypatch.setattr(persistence, "render_case_report_pdf", render)

    async def exercise():
        async with isolated_database() as session_factory:
            case_id, user_id, report = await reported_case(session_factory)
            async with session_factory() as db:
                content, filename = await CaseReportService(db).get_report_pdf(
                    case_id, report.report_id, user_id
                )
            assert (content, filename) == (b"%PDF-", "case_report_v1.pdf")

    asyncio.run(exercise())
    assert threads and threads[0] is not threading.main_thread()


def test_a_report_stored_in_the_old_shape_is_refused_with_a_code():
    async def exercise():
        async with isolated_database() as session_factory:
            case_id, user_id, report = await reported_case(session_factory)
            async with session_factory() as db, db.begin():
                stored = await db.get(CaseReport, report.report_id)
                stored.structured_report = {
                    "report_version": "preliminary_analysis_report_v1",
                    "status": "provisional_unverified",
                    "title": "Seeded case",
                    "sections": [],
                    "claims": [],
                    "limitations": [],
                }

            reads = (
                lambda service: service.list_reports(case_id, user_id),
                lambda service: service.get_report_html(case_id, report.report_id, user_id),
                lambda service: service.generate_report(case_id, CaseReportCreate(), user_id),
            )
            for read in reads:
                async with session_factory() as db:
                    with pytest.raises(ReportGenerationConflict) as refused:
                        await read(CaseReportService(db))
                assert refused.value.code == "case_report_outdated"
                assert refused.value.status_code == 409

    asyncio.run(exercise())
