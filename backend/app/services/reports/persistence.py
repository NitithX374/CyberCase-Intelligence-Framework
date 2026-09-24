from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models.analysis import CaseAnalysisResult
from app.models.case import Case
from app.models.report import CaseReport
from app.models.sources import CaseSource
from app.schemas.reports import CaseReportCreate, CaseReportRead, StructuredReport
from app.services.reports.content import build_case_report
from app.services.reports.contracts import (
    CaseReportInput,
    ReportGenerationConflict,
    ReportNotFound,
)
from app.services.reports.display import ReportIssue
from app.services.reports.projection import build_case_report_input, serialize_case_report
from app.services.reports.render import render_case_report_html, render_case_report_pdf


class CaseReportService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def generate_report(
        self,
        case_id: UUID,
        request: CaseReportCreate,
        user_id: UUID | None,
    ) -> CaseReportRead:
        if not settings.chat_report_enabled:
            raise ReportGenerationConflict(
                "report_generation_disabled",
                "Report generation is disabled by backend configuration.",
            )
        async with self.db.begin():
            case = await self.locked_case(case_id, user_id)
            result = await self.selected_result(case, request.analysis_result_id)
            existing = await self.report_for_analysis(result.id)
            if existing is not None:
                return serialize_case_report(existing)
            structured = build_case_report(build_case_report_input(case, result))
            report = CaseReport(
                case_id=case.id,
                analysis_result_id=result.id,
                version_number=await self.next_version(case.id),
                structured_report=structured.model_dump(mode="json"),
            )
            self.db.add(report)
            await self.db.flush()
            return serialize_case_report(report)

    async def list_reports(self, case_id: UUID, user_id: UUID | None) -> list[CaseReportRead]:
        await self.owned_case(case_id, user_id)
        result = await self.db.execute(
            select(CaseReport)
            .where(CaseReport.case_id == case_id)
            .order_by(CaseReport.version_number.desc())
        )
        return [serialize_case_report(report) for report in result.scalars().all()]

    async def get_report_pdf(
        self,
        case_id: UUID,
        report_id: UUID,
        user_id: UUID | None,
    ) -> tuple[bytes, str]:
        report_input, structured, report = await self.stored_report(case_id, report_id, user_id)
        pdf_bytes = render_case_report_pdf(report_input, structured, report_issue(report))
        return pdf_bytes, f"case_report_v{report.version_number}.pdf"

    async def get_report_html(
        self,
        case_id: UUID,
        report_id: UUID,
        user_id: UUID | None,
    ) -> str:
        report_input, structured, report = await self.stored_report(case_id, report_id, user_id)
        return render_case_report_html(report_input, structured, report_issue(report))

    async def stored_report(
        self,
        case_id: UUID,
        report_id: UUID,
        user_id: UUID | None,
    ) -> tuple[CaseReportInput, StructuredReport, CaseReport]:
        case = await self.owned_case(case_id, user_id)
        report = await self.report(case_id, report_id)
        result = await self.selected_result(case, report.analysis_result_id)
        return (
            build_case_report_input(case, result),
            StructuredReport.model_validate(report.structured_report),
            report,
        )

    async def locked_case(self, case_id: UUID, user_id: UUID | None) -> Case:
        result = await self.db.execute(
            select(Case)
            .options(selectinload(Case.sources).selectinload(CaseSource.document))
            .where(Case.id == case_id)
            .with_for_update()
        )
        case = result.scalar_one_or_none()
        if case is None or case.user_id != user_id:
            raise ReportNotFound("case_not_found", "Case not found")
        return case

    async def owned_case(self, case_id: UUID, user_id: UUID | None) -> Case:
        result = await self.db.execute(
            select(Case)
            .options(selectinload(Case.sources).selectinload(CaseSource.document))
            .where(Case.id == case_id)
        )
        case = result.scalar_one_or_none()
        if case is None or case.user_id != user_id:
            raise ReportNotFound("case_not_found", "Case not found")
        return case

    async def selected_result(
        self, case: Case, analysis_result_id: UUID | None
    ) -> CaseAnalysisResult:
        result_id = analysis_result_id or case.latest_analysis_result_id
        if result_id is None:
            raise ReportGenerationConflict(
                "case_analysis_missing", "No Case analysis result is available"
            )
        result = await self.db.execute(
            select(CaseAnalysisResult).where(
                CaseAnalysisResult.id == result_id, CaseAnalysisResult.case_id == case.id
            )
        )
        persisted = result.scalar_one_or_none()
        if persisted is None:
            raise ReportNotFound(
                "case_analysis_not_found", "The selected Case analysis result was not found"
            )
        return persisted

    async def report_for_analysis(self, analysis_result_id: UUID) -> CaseReport | None:
        result = await self.db.execute(
            select(CaseReport).where(CaseReport.analysis_result_id == analysis_result_id)
        )
        return result.scalar_one_or_none()

    async def report(self, case_id: UUID, report_id: UUID) -> CaseReport:
        result = await self.db.execute(
            select(CaseReport).where(CaseReport.id == report_id, CaseReport.case_id == case_id)
        )
        report = result.scalar_one_or_none()
        if report is None:
            raise ReportNotFound("report_not_found", "Case report not found")
        return report

    async def next_version(self, case_id: UUID) -> int:
        result = await self.db.scalar(
            select(func.coalesce(func.max(CaseReport.version_number), 0)).where(
                CaseReport.case_id == case_id
            )
        )
        return int(result or 0) + 1


def report_issue(report: CaseReport) -> ReportIssue:
    return ReportIssue(version_number=report.version_number, created_at=report.created_at)


__all__ = [
    "CaseReportService",
    "build_case_report_input",
    "serialize_case_report",
]
