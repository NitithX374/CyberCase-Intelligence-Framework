from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.guard import get_current_user
from app.database import get_db
from app.models.user import User
from app.reports.generate import CaseReportService
from app.reports.schemas import CaseReportCreate, CaseReportRead

router = APIRouter(prefix="/cases/{case_id}/reports", tags=["case-reports"])


@router.post("", response_model=CaseReportRead, status_code=status.HTTP_201_CREATED)
async def generate_case_report(
    case_id: UUID,
    request: CaseReportCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await CaseReportService(db).generate_report(case_id, request, user.id)


@router.get("", response_model=list[CaseReportRead], status_code=status.HTTP_200_OK)
async def list_case_reports(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await CaseReportService(db).list_reports(case_id, user.id)


@router.get("/{report_id}/pdf", response_class=Response, status_code=status.HTTP_200_OK)
async def download_case_report_pdf(
    case_id: UUID,
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    content, filename = await CaseReportService(db).get_report_pdf(case_id, report_id, user.id)
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
    content = await CaseReportService(db).get_report_html(case_id, report_id, user.id)
    return HTMLResponse(
        content=content,
        headers={"Cache-Control": "no-store"},
    )


__all__ = ["router"]
