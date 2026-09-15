from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case
from app.models.case_materials import CaseDocument
from app.services.case_materials.material_service import CaseMaterialsError


async def get_owned_document_content(
    db: AsyncSession,
    *,
    case_id: UUID,
    document_id: UUID,
    user_id: UUID | None,
) -> CaseDocument:
    result = await db.execute(
        select(CaseDocument)
        .join(Case, Case.id == CaseDocument.case_id)
        .where(
            CaseDocument.id == document_id,
            CaseDocument.case_id == case_id,
            Case.user_id == user_id,
        )
    )
    document = result.scalar_one_or_none()
    if document is None:
        raise CaseMaterialsError("document_not_found", "Document not found", 404)
    return document


__all__ = ["get_owned_document_content"]
