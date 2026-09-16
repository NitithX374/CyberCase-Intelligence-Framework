from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models.case import Case
from app.models.case_materials import CaseSource
from app.models.case_run import CaseAnalysisResult
from app.models.report import CaseReport
from app.schemas.reports import CaseReportCreate, CaseReportRead, StructuredReport
from app.services.reports.case_report_contracts import (
    CaseReportInput,
    ReportGenerationConflict,
    ReportNotFound,
    case_source_ids,
    validate_case_structured_report,
)
from app.services.reports.case_report_html import render_case_report_html
from app.services.reports.case_report_pdf import render_case_report_pdf
from app.services.reports.case_report_projection import build_case_report_input, serialize_case_report
from app.services.reports.case_report_template import run_case_report_generation


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
            raise ReportGenerationConflict("report_generation_disabled", "Report generation is disabled by backend configuration.")
        async with self.db.begin():
            case = await self.locked_case(case_id, user_id)
            result = await self.selected_result(case, request.analysis_result_id)
            report_input = build_case_report_input(case, result)
            idempotency_key = request.idempotency_key or f"report-{result.id}-{result.evidence_revision}"
            existing = await self.existing_report(case.id, idempotency_key)
            if existing is not None:
                return serialize_case_report(existing)
            generation = await run_case_report_generation(report_input)
            retrieval_id = getattr(result, "retrieval_context_id", None)
            report = CaseReport(
                case_id=case.id,
                analysis_result_id=result.id,
                version_number=await self.next_version(case.id),
                idempotency_key=idempotency_key,
                retrieval_context_id=retrieval_id,
                prompt_version=generation.prompt_version,
                status=generation.status,
                validation_status="validated" if generation.status == "completed" else "failed",
                validation_errors_json=list(generation.validation_errors),
                structured_report=generation.report.model_dump(mode="json") if generation.report else None,
                failure_code=generation.failure_code,
                failure_message=generation.failure_message,
                finished_at=datetime.now(timezone.utc),
                latency_ms=generation.latency_ms,
                input_tokens=generation.input_tokens,
                output_tokens=generation.output_tokens,
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
        report_input, structured, report = await self.validated_report_input(case_id, report_id, user_id)
        pdf_bytes = render_case_report_pdf(
            report_input,
            structured,
            report.id,
        )
        return pdf_bytes, f"case_report_v{report.version_number}.pdf"

    async def get_report_html(
        self,
        case_id: UUID,
        report_id: UUID,
        user_id: UUID | None,
    ) -> str:
        report_input, structured, _ = await self.validated_report_input(case_id, report_id, user_id)
        return render_case_report_html(report_input, structured)

    async def validated_report_input(
        self,
        case_id: UUID,
        report_id: UUID,
        user_id: UUID | None,
    ) -> tuple[CaseReportInput, StructuredReport, CaseReport]:
        case = await self.owned_case(case_id, user_id)
        report = await self.report(case_id, report_id)
        if report.status != "completed" or not isinstance(report.structured_report, dict):
            raise ReportGenerationConflict("report_requires_validated_report", "Only a completed validated report can be displayed or exported.")
        result = await self.selected_result(case, report.analysis_result_id)
        report_input = build_case_report_input(case, result)
        structured = StructuredReport.model_validate(report.structured_report)
        validate_case_structured_report(
            structured,
            allowed_source_ids=case_source_ids(report_input),
            mitre_ids={
                str(item["technique_id"])
                for item in report_input.analysis_trace.get("mitre_associations", [])
                if isinstance(item, dict) and item.get("technique_id")
            },
        )
        return report_input, structured, report

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

    async def selected_result(self, case: Case, analysis_result_id: UUID | None) -> CaseAnalysisResult:
        result_id = analysis_result_id or case.latest_analysis_result_id
        if result_id is None:
            raise ReportGenerationConflict("case_analysis_missing", "No Case analysis result is available")
        result = await self.db.execute(
            select(CaseAnalysisResult)
            .where(CaseAnalysisResult.id == result_id, CaseAnalysisResult.case_id == case.id)
        )
        persisted = result.scalar_one_or_none()
        if persisted is None:
            raise ReportNotFound("case_analysis_not_found", "The selected Case analysis result was not found")
        return persisted

    async def existing_report(self, case_id: UUID, idempotency_key: str) -> CaseReport | None:
        result = await self.db.execute(
            select(CaseReport).where(CaseReport.case_id == case_id, CaseReport.idempotency_key == idempotency_key)
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
            select(func.coalesce(func.max(CaseReport.version_number), 0)).where(CaseReport.case_id == case_id)
        )
        return int(result or 0) + 1


__all__ = [
    "CaseReportService",
    "build_case_report_input",
    "serialize_case_report",
]
