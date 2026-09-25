from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.case import Case
from app.models.report import CaseReport
from app.schemas.cases import CaseCreate, CaseRead, CaseUpdate
from app.services.cases.ownership import owned_case
from app.services.workflow.run_analysis import analysis_freshness

WITH_LATEST_ANALYSIS = (selectinload(Case.latest_analysis_result),)


def serialize_case(case: Case) -> CaseRead:
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
        statement = select(Case).options(*WITH_LATEST_ANALYSIS).order_by(Case.updated_at.desc())
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
        case = await owned_case(self.db, case_id, user_id, options=WITH_LATEST_ANALYSIS)
        return serialize_case(case)

    async def update_case(
        self,
        case_id: UUID,
        request: CaseUpdate,
        user_id: UUID | None = None,
    ) -> CaseRead:
        case = await owned_case(self.db, case_id, user_id, lock=True)
        case.title = request.title
        await self.db.commit()
        return await self.get_case(case_id, user_id=user_id)

    async def delete_case(
        self,
        case_id: UUID,
        user_id: UUID | None = None,
    ) -> None:
        case = await owned_case(self.db, case_id, user_id, lock=True)
        await self.db.execute(delete(CaseReport).where(CaseReport.case_id == case.id))
        self.db.expunge_all()
        await self.db.execute(delete(Case).where(Case.id == case.id))
        await self.db.commit()


__all__ = ["CaseService", "serialize_case"]
