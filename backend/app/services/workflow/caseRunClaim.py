from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case
from app.models.caseRun import CaseRun
from app.services.case_materials import CaseMaterialsError, assembleCaseEvidence
from app.services.workflow.caseRunService import ClaimedCaseRun


async def claimCaseRun(
    db: AsyncSession,
    run_id: UUID,
) -> ClaimedCaseRun | None:
    now = datetime.now(timezone.utc)
    async with db.begin():
        claimed = await db.execute(
            update(CaseRun)
            .where(CaseRun.id == run_id, CaseRun.status == "queued")
            .values(
                status="running",
                attempt_count=CaseRun.attempt_count + 1,
                started_at=now,
                finished_at=None,
                error_code=None,
                error_message=None,
                updated_at=now,
            )
            .returning(
                CaseRun.id,
                CaseRun.case_id,
                CaseRun.evidence_revision,
                CaseRun.operation,
                CaseRun.attempt_count,
                CaseRun.pipeline_config,
                CaseRun.request_payload,
            )
        )
        row = claimed.mappings().one_or_none()
        if row is None:
            return None
        case = await db.scalar(
            select(Case).where(Case.id == row["case_id"]).with_for_update()
        )
        if case is None:
            await _fail_claimed_run(db, row["id"], row["attempt_count"], now, "case_not_found", "Case is missing")
            return None
        if case.evidence_revision != row["evidence_revision"]:
            await _fail_claimed_run(
                db,
                row["id"],
                row["attempt_count"],
                now,
                "case_run_superseded",
                "Case evidence changed before this run started. Retry analysis.",
            )
            return None
        try:
            assembled = await assembleCaseEvidence(db, case_id=row["case_id"], user_id=None)
        except CaseMaterialsError as error:
            await _fail_claimed_run(db, row["id"], row["attempt_count"], now, error.code, error.message)
            return None

        manifest = tuple(
            {
                "source_id": str(s.id),
                "exact_text": s.exact_text,
                "provenance": s.provenance_json,
                "source_kind": s.source_kind,
                "document_id": str(s.document_id) if s.document_id else None,
                "filename": s.document.filename if s.document else None,
            }
            for s in assembled.active_sources
        )
        source_ids = tuple(str(s.id) for s in assembled.active_sources)
        source_text_by_id = {str(s.id): s.exact_text for s in assembled.active_sources}

        return ClaimedCaseRun(
            id=row["id"],
            case_id=row["case_id"],
            evidence_revision=row["evidence_revision"],
            attempt_count=row["attempt_count"],
            operation=row["operation"],
            input_text=assembled.input_text,
            manifest=manifest,
            source_ids=source_ids,
            source_text_by_id=source_text_by_id,
            pipeline_config=deepcopy(row["pipeline_config"]),
            request_payload=deepcopy(row["request_payload"]),
        )


async def _fail_claimed_run(
    db: AsyncSession,
    run_id: UUID,
    attempt_count: int,
    finished_at: datetime,
    error_code: str,
    error_message: str,
) -> None:
    await db.execute(
        update(CaseRun)
        .where(
            CaseRun.id == run_id,
            CaseRun.status == "running",
            CaseRun.attempt_count == attempt_count,
        )
        .values(
            status="failed",
            error_code=error_code,
            error_message=error_message,
            finished_at=finished_at,
            updated_at=finished_at,
        )
    )


__all__ = [
    "claimCaseRun",
]
