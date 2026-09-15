"""Case aggregate lifecycle and construction services."""

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.case import Case
from app.models.case_materials import (
    CaseDocument,
    CaseSource,
    DocumentExtraction,
)
from app.models.report import CaseReport
from app.models.case_run import CaseAnalysisResult, CaseRun
from app.models.chat import ChatMessage
from app.models.rag_context import RagContext
from app.schemas.cases import CaseCreate, CaseRead, CaseUpdate


def serialize_case(case: Case) -> CaseRead:
    analysis_runs = [run for run in case.case_runs if run.operation == "analysis"]
    latest_run = max(analysis_runs, key=lambda run: run.created_at, default=None)
    if latest_run is not None and latest_run.status in {"queued", "running"}:
        processing_status = latest_run.status
    elif latest_run is not None and latest_run.status == "failed":
        processing_status = "failed"
    else:
        processing_status = "idle"
    has_pending_clarification = False
    if case.chat_messages:
        answered_ids = {
            m.in_reply_to_message_id
            for m in case.chat_messages
            if m.in_reply_to_message_id is not None
        }
        has_pending_clarification = any(
            m.message_kind == "followup_question" and m.id not in answered_ids
            for m in case.chat_messages
        )
    status_value = "processing" if processing_status in {"queued", "running"} else (
        "failed" if processing_status == "failed" else
        "awaiting_followup" if has_pending_clarification else
        "answered" if case.latest_analysis_result is not None else
        "idle"
    )
    from app.services.workflow.case_run_service import analysis_freshness
    freshness = analysis_freshness(case, case.latest_analysis_result)
    return CaseRead(
        id=case.id,
        user_id=case.user_id,
        title=case.title,
        status=status_value,
        evidence_revision=case.evidence_revision,
        latest_analysis_result_id=case.latest_analysis_result_id,
        processing_status=processing_status,
        has_pending_clarification=has_pending_clarification,
        analysis_freshness=freshness,
        active_run_id=(latest_run.id if latest_run is not None and latest_run.status in {"queued", "running"} else None),
        latest_run_id=latest_run.id if latest_run is not None else None,
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
        statement = select(Case).options(
            selectinload(Case.chat_messages),
            selectinload(Case.case_runs),
            selectinload(Case.latest_analysis_result),
        ).order_by(Case.updated_at.desc())
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
        await self.db.execute(delete(CaseAnalysisResult).where(CaseAnalysisResult.case_id == case.id))
        await self.db.execute(delete(RagContext).where(RagContext.case_id == case.id))
        await self.db.execute(delete(CaseRun).where(CaseRun.case_id == case.id))
        await self.db.execute(delete(ChatMessage).where(ChatMessage.case_id == case.id))
        await self.db.execute(delete(CaseSource).where(CaseSource.case_id == case.id))

        doc_ids_subq = select(CaseDocument.id).where(CaseDocument.case_id == case.id)
        await self.db.execute(delete(DocumentExtraction).where(DocumentExtraction.document_id.in_(doc_ids_subq)))
        await self.db.execute(delete(CaseDocument).where(CaseDocument.case_id == case.id))

        self.db.expunge_all()
        await self.db.execute(delete(Case).where(Case.id == case.id))
        await self.db.commit()

    async def load_case(self, case_id: UUID, *, lock: bool = False) -> Case:
        statement = (
            select(Case)
            .options(
                selectinload(Case.chat_messages),
                selectinload(Case.case_runs),
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
