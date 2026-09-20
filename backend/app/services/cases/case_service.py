"""Case aggregate lifecycle and construction services."""

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.analysis import CaseAnalysisResult
from app.models.case import Case
from app.models.chat import ChatMessage
from app.models.report import CaseReport
from app.models.sources import (
    CaseDocument,
    CaseSource,
    DocumentExtraction,
)
from app.schemas.cases import CaseCreate, CaseRead, CaseUpdate
from app.services.workflow import analysis_freshness


def serialize_case(case: Case) -> CaseRead:
    """A case is waiting on the user, has an analysis, or has neither.

    There is no "processing" state: an analysis runs inside the request that
    asked for it, so by the time a case is serialised it has either finished or
    failed with an error the caller already saw.
    """

    status_value = "answered" if case.latest_analysis_result is not None else "idle"
    freshness = analysis_freshness(case, case.latest_analysis_result)
    return CaseRead(
        id=case.id,
        user_id=case.user_id,
        title=case.title,
        status=status_value,
        source_revision=case.source_revision,
        latest_analysis_result_id=case.latest_analysis_result_id,
        analysis_freshness=freshness,
        created_at=case.created_at,
        updated_at=case.updated_at,
    )


class CaseService:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def verify_case_access(case: Case, user_id: UUID | None) -> None:
        if case.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found",
            )

    async def create_case(
        self,
        request: CaseCreate,
        user_id: UUID | None = None,
    ) -> CaseRead:
        case = Case(title=request.title, user_id=user_id)
        self.db.add(case)
        await self.db.commit()
        return await self.get_case(case.id, user_id=user_id)

    async def list_cases(self, user_id: UUID | None = None) -> list[CaseRead]:
        statement = (
            select(Case)
            .options(
                selectinload(Case.chat_messages),
                selectinload(Case.latest_analysis_result),
            )
            .order_by(Case.updated_at.desc())
        )
        if user_id is None:
            statement = statement.where(Case.user_id.is_(None))
        else:
            statement = statement.where(Case.user_id == user_id)
        result = await self.db.execute(statement)
        return [serialize_case(case) for case in result.scalars().all()]

    async def get_case(
        self,
        case_id: UUID,
        user_id: UUID | None = None,
    ) -> CaseRead:
        case = await self.load_case(case_id)
        self.verify_case_access(case, user_id)
        return serialize_case(case)

    async def update_case(
        self,
        case_id: UUID,
        request: CaseUpdate,
        user_id: UUID | None = None,
    ) -> CaseRead:
        case = await self.load_case(case_id, lock=True)
        self.verify_case_access(case, user_id)
        case.title = request.title
        await self.db.commit()
        return await self.get_case(case_id, user_id=user_id)

    async def delete_case(
        self,
        case_id: UUID,
        user_id: UUID | None = None,
    ) -> None:
        case = await self.load_case(case_id, lock=True)
        self.verify_case_access(case, user_id)

        # Delete case-owned entities in dependency order within transaction
        await self.db.execute(delete(CaseReport).where(CaseReport.case_id == case.id))

        await self.db.execute(
            update(Case).where(Case.id == case.id).values(latest_analysis_result_id=None)
        )
        await self.db.execute(
            delete(CaseAnalysisResult).where(CaseAnalysisResult.case_id == case.id)
        )
        await self.db.execute(delete(ChatMessage).where(ChatMessage.case_id == case.id))
        await self.db.execute(delete(CaseSource).where(CaseSource.case_id == case.id))

        doc_ids_subq = select(CaseDocument.id).where(CaseDocument.case_id == case.id)
        await self.db.execute(
            delete(DocumentExtraction).where(DocumentExtraction.document_id.in_(doc_ids_subq))
        )
        await self.db.execute(delete(CaseDocument).where(CaseDocument.case_id == case.id))

        self.db.expunge_all()
        await self.db.execute(delete(Case).where(Case.id == case.id))
        await self.db.commit()

    async def load_case(self, case_id: UUID, *, lock: bool = False) -> Case:
        statement = (
            select(Case)
            .options(
                selectinload(Case.chat_messages),
                selectinload(Case.latest_analysis_result),
            )
            .where(Case.id == case_id)
        )
        if lock:
            statement = statement.with_for_update()
        result = await self.db.execute(statement)
        case = result.scalar_one_or_none()
        if case is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found",
            )
        return case


__all__ = ["CaseService", "serialize_case"]
