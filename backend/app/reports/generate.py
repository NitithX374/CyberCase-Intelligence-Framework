from __future__ import annotations

import asyncio
from uuid import UUID

from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.analysis.technical_context.contracts import CaseTechnicalAugmentation
from app.cases.ownership import owned_case
from app.config import settings
from app.models.analysis_result import CaseAnalysisResult
from app.models.case import Case
from app.models.report import CaseReport
from app.models.source import CaseSource
from app.reports.contracts import CaseReportInput, ReportGenerationConflict, ReportNotFound
from app.reports.display import build_case_report_content
from app.reports.render import ReportIssue, render_case_report_html, render_case_report_pdf
from app.reports.schemas import CaseReportContent, CaseReportCreate, CaseReportRead
from app.sources.bundle import (
    CaseSourceBundle,
    case_source_bundle_for_analysis,
    source_ids_of_sources_read,
)
from app.trace.claims import CaseFollowupExchange, followup_history_of_snapshot
from app.trace.trace import CaseAnalysisTrace


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
            case = await owned_case(
                self.db,
                case_id,
                user_id,
                lock=True,
                options=(selectinload(Case.sources).selectinload(CaseSource.document),),
            )
            result = await self.selected_result(case, request.analysis_result_id)
            existing = await self.report_for_analysis(result.id)
            if existing is not None:
                return serialize_case_report(existing)
            content = build_case_report_content(build_case_report_input(case, result))
            report = CaseReport(
                case_id=case.id,
                analysis_result_id=result.id,
                version_number=await self.next_version(case.id),
                structured_report=content.model_dump(mode="json"),
            )
            self.db.add(report)
            await self.db.flush()
            return serialize_case_report(report)

    async def list_reports(self, case_id: UUID, user_id: UUID | None) -> list[CaseReportRead]:
        await owned_case(self.db, case_id, user_id)
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
        content, report = await self.stored_report(case_id, report_id, user_id)
        pdf_bytes = await asyncio.to_thread(render_case_report_pdf, content, report_issue(report))
        return pdf_bytes, f"case_report_v{report.version_number}.pdf"

    async def get_report_html(
        self,
        case_id: UUID,
        report_id: UUID,
        user_id: UUID | None,
    ) -> str:
        content, report = await self.stored_report(case_id, report_id, user_id)
        return render_case_report_html(content, report_issue(report))

    async def stored_report(
        self,
        case_id: UUID,
        report_id: UUID,
        user_id: UUID | None,
    ) -> tuple[CaseReportContent, CaseReport]:
        await owned_case(self.db, case_id, user_id)
        report = await self.report(case_id, report_id)
        return stored_content(report), report

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


def serialize_case_report(report: CaseReport) -> CaseReportRead:
    return CaseReportRead(
        report_id=report.id,
        version_number=report.version_number,
        case_id=report.case_id,
        analysis_result_id=report.analysis_result_id,
        report=stored_content(report),
        created_at=report.created_at,
    )


def stored_content(report: CaseReport) -> CaseReportContent:
    try:
        return CaseReportContent.model_validate(report.structured_report)
    except ValidationError as error:
        raise ReportGenerationConflict(
            "case_report_outdated",
            "This report was stored in an older format and can no longer be shown",
        ) from error


def build_case_report_input(
    case: Case,
    result: CaseAnalysisResult,
) -> CaseReportInput:
    if result.case_id != case.id:
        raise ReportGenerationConflict(
            "case_analysis_mismatch", "Analysis result does not belong to this Case"
        )
    if result.status != "validated":
        raise ReportGenerationConflict(
            "case_analysis_unavailable", "Only a validated Case analysis can produce a report"
        )
    source_bundle = recorded_source_bundle(case, result)
    if not source_bundle.sources:
        raise ReportGenerationConflict(
            "case_report_input_invalid", "The Case has no active sources"
        )
    trace = validated_trace(result)
    return CaseReportInput(
        case_id=case.id,
        case_title=case.title or "CyberCase Investigation",
        analysis_result_id=result.id,
        analysis_created_at=result.created_at,
        source_bundle=source_bundle,
        analysis_summary=result.summary,
        analysis_trace=trace,
        technical_augmentation=recorded_augmentation(result),
        followup_history=recorded_followup_history(result),
    )


def recorded(result: CaseAnalysisResult) -> dict[str, object]:
    return result.external_context_json if isinstance(result.external_context_json, dict) else {}


def recorded_source_bundle(case: Case, result: CaseAnalysisResult) -> CaseSourceBundle:
    context = recorded(result)
    if "sources_read" not in context:
        raise ReportGenerationConflict(
            "analysis_source_snapshot_missing",
            "The analysis did not record the sources it read",
        )
    try:
        return case_source_bundle_for_analysis(
            case, result, source_ids_of_sources_read(context["sources_read"])
        )
    except ValueError as error:
        raise ReportGenerationConflict(
            "analysis_source_snapshot_invalid",
            "The sources recorded by the analysis are invalid or no longer exist",
        ) from error


def recorded_followup_history(result: CaseAnalysisResult) -> tuple[CaseFollowupExchange, ...]:
    context = recorded(result)
    if "followup_history" not in context:
        raise ReportGenerationConflict(
            "analysis_followup_snapshot_missing",
            "The analysis did not record the follow-up answers it read",
        )
    try:
        return followup_history_of_snapshot(context["followup_history"])
    except ValueError as error:
        raise ReportGenerationConflict(
            "analysis_followup_snapshot_invalid",
            "The follow-up answers recorded by the analysis are invalid",
        ) from error


def validated_trace(
    result: CaseAnalysisResult,
) -> CaseAnalysisTrace:
    if not isinstance(result.trace_json, dict):
        raise ReportGenerationConflict(
            "case_analysis_trace_missing", "The selected analysis has no validated trace"
        )
    try:
        trace = CaseAnalysisTrace.model_validate(result.trace_json)
        if trace.analysis_mode != "case_overview":
            raise ValueError("analysis trace mode is not case_overview")
        return trace
    except ValueError as error:
        raise ReportGenerationConflict(
            "case_analysis_trace_invalid", "The selected analysis trace is invalid"
        ) from error


def recorded_augmentation(result: CaseAnalysisResult) -> CaseTechnicalAugmentation | None:
    raw = recorded(result).get("technical_augmentation")
    if raw is None:
        return None
    try:
        return CaseTechnicalAugmentation.model_validate(raw)
    except ValidationError as error:
        raise ReportGenerationConflict(
            "case_technical_augmentation_invalid",
            "The persisted Case technical augmentation outcome is invalid",
        ) from error


__all__ = [
    "CaseReportService",
    "build_case_report_input",
    "recorded",
    "recorded_augmentation",
    "recorded_followup_history",
    "recorded_source_bundle",
    "serialize_case_report",
    "stored_content",
    "validated_trace",
]
