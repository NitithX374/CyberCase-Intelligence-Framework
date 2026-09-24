from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.reports import CaseReportCreate, CaseReportRead
from app.services.auth.dependencies import get_current_user
from app.services.reports.contracts import ReportNotFound, ReportServiceError
from app.services.reports.persistence import CaseReportService

router = APIRouter(prefix="/cases/{case_id}/reports", tags=["case-reports"])


def report_http_error(error: ReportServiceError) -> HTTPException:
    return HTTPException(
        status_code=(
            status.HTTP_404_NOT_FOUND
            if isinstance(error, ReportNotFound)
            else status.HTTP_409_CONFLICT
        ),
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
        raise report_http_error(error) from error


@router.get("", response_model=list[CaseReportRead], status_code=status.HTTP_200_OK)
async def list_case_reports(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return await CaseReportService(db).list_reports(case_id, user.id)
    except ReportServiceError as error:
        raise report_http_error(error) from error


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
        raise report_http_error(error) from error
    return Response(
        content=content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store",
        },
    )


@router.get("/{report_id}/html", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def render_case_report_html(
    case_id: UUID,
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        content = await CaseReportService(db).get_report_html(case_id, report_id, user.id)
    except ReportServiceError as error:
        raise report_http_error(error) from error
    return HTMLResponse(
        content=content,
        headers={"Cache-Control": "no-store"},
    )


__all__ = ["router"]
