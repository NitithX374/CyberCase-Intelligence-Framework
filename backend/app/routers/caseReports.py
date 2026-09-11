from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.reports import CaseReportCreate, CaseReportRead
from app.services.auth.dependencies import get_current_user
from app.services.reports.case_report_persistence import CaseReportService
from app.services.reports.report_contracts import ReportServiceError

router = APIRouter(prefix="/cases/{case_id}/reports", tags=["case-reports"])


def _report_http_error(error: ReportServiceError) -> HTTPException:
    code_status = status.HTTP_404_NOT_FOUND if "not found" in error.message.lower() else status.HTTP_409_CONFLICT
    return HTTPException(
        status_code=code_status,
        detail={"code": error.code, "message": error.message},
    )


@router.post("", response_model=CaseReportRead, status_code=status.HTTP_201_CREATED)
async def generate_case_report(
    case_id: UUID,
    request: CaseReportCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        await db.commit()
        return await CaseReportService(db).generate_report(case_id, request, user.id)
    except ReportServiceError as error:
        raise _report_http_error(error) from error


@router.get("", response_model=list[CaseReportRead], status_code=status.HTTP_200_OK)
async def list_case_reports(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return await CaseReportService(db).list_reports(case_id, user.id)
    except ReportServiceError as error:
        raise _report_http_error(error) from error


@router.get("/{report_id}", response_model=CaseReportRead, status_code=status.HTTP_200_OK)
async def get_case_report(
    case_id: UUID,
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return await CaseReportService(db).get_report(case_id, report_id, user.id)
    except ReportServiceError as error:
        raise _report_http_error(error) from error


@router.get("/{report_id}/pdf", response_class=Response, status_code=status.HTTP_200_OK)
async def download_case_report_pdf(
    case_id: UUID,
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        content, filename = await CaseReportService(db).get_report_pdf(case_id, report_id, user.id)
    except ReportServiceError as error:
        raise _report_http_error(error) from error
    return Response(
        content=content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store",
        },
    )


__all__ = ["router"]
