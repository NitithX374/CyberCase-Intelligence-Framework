import asyncio
import logging
import threading

import pytest
from case_chat_support import NARRATIVE, SETTLED, seeded_case
from isolated_database import isolated_database
from sqlalchemy import select

from app.cases.ownership import owned_case
from app.models.analysis_result import CaseAnalysisResult
from app.models.report import CaseReport
from app.reports import generate as persistence
from app.reports.contracts import ReportGenerationConflict
from app.reports.generate import CaseReportService
from app.reports.schemas import CaseReportCreate
from app.sources.bundle import WITH_SOURCES, analysable_bundle, sources_read
from app.trace.claims import followup_snapshot


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


OLD_SHAPE = {
    "report_version": "preliminary_analysis_report_v1",
    "status": "provisional_unverified",
    "title": "Seeded case",
    "sections": [],
    "claims": [],
    "limitations": [],
}


def test_a_report_stored_in_the_old_shape_is_refused_with_a_code():
    async def exercise():
        async with isolated_database() as session_factory:
            case_id, user_id, report = await reported_case(session_factory)
            async with session_factory() as db, db.begin():
                stored = await db.get(CaseReport, report.report_id)
                stored.structured_report = OLD_SHAPE

            reads = (
                lambda service: service.get_report_html(case_id, report.report_id, user_id),
                lambda service: service.generate_report(case_id, CaseReportCreate(), user_id),
            )
            for read in reads:
                async with session_factory() as db:
                    with pytest.raises(ReportGenerationConflict) as refused:
                        await read(CaseReportService(db))
                assert refused.value.code == "case_report_outdated"
                assert refused.value.status_code == 409

            async with session_factory() as db:
                assert await CaseReportService(db).list_reports(case_id, user_id) == []

    asyncio.run(exercise())


def test_a_report_in_the_old_shape_does_not_hide_the_reports_beside_it(caplog):
    async def exercise():
        async with isolated_database() as session_factory:
            case_id, user_id, old = await reported_case(session_factory)
            async with session_factory() as db, db.begin():
                first = await db.scalar(
                    select(CaseAnalysisResult).where(CaseAnalysisResult.case_id == case_id)
                )
                second = CaseAnalysisResult(
                    case_id=case_id,
                    source_revision=first.source_revision,
                    summary=first.summary,
                    trace_json=first.trace_json,
                    pipeline_config={},
                    external_context_json=first.external_context_json,
                )
                db.add(second)
                await db.flush()
                db.add(
                    CaseReport(
                        case_id=case_id,
                        analysis_result_id=second.id,
                        version_number=2,
                        structured_report=old.report.model_dump(mode="json"),
                    )
                )
                stored = await db.get(CaseReport, old.report_id)
                stored.structured_report = OLD_SHAPE

            async with session_factory() as db:
                listed = await CaseReportService(db).list_reports(case_id, user_id)
                with pytest.raises(ReportGenerationConflict) as refused:
                    await CaseReportService(db).get_report_html(case_id, old.report_id, user_id)
            return listed, old.report_id, refused.value

    with caplog.at_level(logging.WARNING):
        listed, old_id, refused = asyncio.run(exercise())

    assert [report.version_number for report in listed] == [2]
    assert refused.code == "case_report_outdated"
    skipped = [record for record in caplog.records if record.name == "app.reports.generate"]
    assert [str(old_id) in record.getMessage() for record in skipped] == [True]
