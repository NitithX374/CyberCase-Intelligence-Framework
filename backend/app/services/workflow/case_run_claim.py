from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case
from app.models.case_run import CaseRun
from app.services.case_materials import CaseMaterialsError, load_case_source_bundle
from app.services.workflow.case_run_service import ClaimedCaseRun


async def claim_case_run(
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
            await fail_claimed_run(db, row["id"], row["attempt_count"], now, "case_not_found", "Case is missing")
            return None
        if case.evidence_revision != row["evidence_revision"]:
            await fail_claimed_run(
                db,
                row["id"],
                row["attempt_count"],
                now,
                "case_run_superseded",
                "Case evidence changed before this run started. Retry analysis.",
            )
            return None
        try:
            source_bundle = await load_case_source_bundle(db, case_id=row["case_id"], user_id=None)
        except CaseMaterialsError as error:
            await fail_claimed_run(db, row["id"], row["attempt_count"], now, error.code, error.message)
            return None

        return ClaimedCaseRun(
            id=row["id"],
            case_id=row["case_id"],
            source_bundle=source_bundle,
            attempt_count=row["attempt_count"],
            pipeline_config=deepcopy(row["pipeline_config"]),
            request_payload=deepcopy(row["request_payload"]),
        )


async def fail_claimed_run(
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
    "claim_case_run",
]
