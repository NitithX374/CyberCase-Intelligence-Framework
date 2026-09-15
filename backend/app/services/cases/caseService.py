"""Case aggregate lifecycle and construction services."""

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.case import Case
from app.models.caseMaterials import (
    CaseDocument,
    DocumentExtraction,
    EvidenceSource,
)
from app.models.report import CaseReport
from app.models.caseRun import CaseAnalysisResult, CaseRun
from app.models.chat import ChatMessage
from app.models.ragContext import RagContext
from app.schemas.cases import CaseCreate, CaseRead, CaseUpdate


def serializeCase(case: Case) -> CaseRead:
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
    from app.services.workflow.caseRunService import analysis_freshness
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
    def _verifyCaseAccess(case: Case, user_id: UUID | None) -> None:
        if case.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found",
            )

    async def createCase(
        self,
        request: CaseCreate,
        user_id: UUID | None = None,
    ) -> CaseRead:
        case = Case(title=request.title, user_id=user_id)
        self.db.add(case)
        await self.db.commit()
        return await self.getCase(case.id, user_id=user_id)

    async def listCases(self, user_id: UUID | None = None) -> list[CaseRead]:
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
        return [serializeCase(case) for case in result.scalars().all()]

    async def getCase(
        self,
        case_id: UUID,
        user_id: UUID | None = None,
    ) -> CaseRead:
        case = await self._loadCase(case_id)
        self._verifyCaseAccess(case, user_id)
        return serializeCase(case)

    async def updateCase(
        self,
        case_id: UUID,
        request: CaseUpdate,
        user_id: UUID | None = None,
    ) -> CaseRead:
        case = await self._loadCase(case_id, lock=True)
        self._verifyCaseAccess(case, user_id)
        case.title = request.title
        await self.db.commit()
        return await self.getCase(case_id, user_id=user_id)

    async def deleteCase(
        self,
        case_id: UUID,
        user_id: UUID | None = None,
    ) -> None:
        case = await self._loadCase(case_id, lock=True)
        self._verifyCaseAccess(case, user_id)

        # Delete case-owned entities in dependency order within transaction
        await self.db.execute(delete(CaseReport).where(CaseReport.case_id == case.id))

        await self.db.execute(
            update(Case).where(Case.id == case.id).values(latest_analysis_result_id=None)
        )
        await self.db.execute(delete(CaseAnalysisResult).where(CaseAnalysisResult.case_id == case.id))
        await self.db.execute(delete(RagContext).where(RagContext.case_id == case.id))
        await self.db.execute(delete(CaseRun).where(CaseRun.case_id == case.id))
        await self.db.execute(delete(ChatMessage).where(ChatMessage.case_id == case.id))
        await self.db.execute(delete(EvidenceSource).where(EvidenceSource.case_id == case.id))

        doc_ids_subq = select(CaseDocument.id).where(CaseDocument.case_id == case.id)
        await self.db.execute(delete(DocumentExtraction).where(DocumentExtraction.document_id.in_(doc_ids_subq)))
        await self.db.execute(delete(CaseDocument).where(CaseDocument.case_id == case.id))

        self.db.expunge_all()
        await self.db.execute(delete(Case).where(Case.id == case.id))
        await self.db.commit()

    async def _loadCase(self, case_id: UUID, *, lock: bool = False) -> Case:
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


__all__ = ["CaseService", "serializeCase"]
