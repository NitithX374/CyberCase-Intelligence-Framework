from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from fastapi import status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.case import Case
from app.models.case_run import CaseAnalysisResult, CaseRun
from app.schemas.case_runs import CaseAnalysisCreate
from app.services.case_materials import (
    CaseSourceBundle,
    CaseMaterialsError,
    load_case_source_bundle,
)
from app.services.case_analysis.pipeline_config import configured_pipeline


class CaseRunError(Exception):
    def __init__(self, code: str, message: str, status_code: int = status.HTTP_409_CONFLICT) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


async def enqueue_case_analysis(
    db: AsyncSession,
    *,
    case_id: UUID,
    user_id: UUID | None,
    request: CaseAnalysisCreate,
    request_payload_extra: dict[str, object] | None = None,
) -> CaseRun:
    case = await locked_case(db, case_id, user_id)
    saved_payload = {
        "operation": "analysis",
        "response_language": request.response_language,
        "expected_evidence_revision": request.expected_evidence_revision,
        **(request_payload_extra or {}),
    }
    existing = await db.scalar(
        select(CaseRun)
        .where(CaseRun.case_id == case.id, CaseRun.idempotency_key == request.idempotency_key)
        .with_for_update()
    )
    if existing is not None:
        if not await existing_request_matches(existing, saved_payload):
            raise CaseRunError(
                "idempotency_conflict",
                "Idempotency key was already used with different analysis intent",
            )
        if existing.status == "failed":
            await requeue_failed_case_run(db, case, existing)
        return existing
    if (
        request.expected_evidence_revision is not None
        and request.expected_evidence_revision != case.evidence_revision
    ):
        raise CaseRunError(
            "evidence_revision_conflict",
            "Case evidence changed; reload the Case before starting analysis",
        )

    await load_case_source_bundle(db, case_id=case.id, user_id=user_id)
    pipeline = configured_pipeline().model_dump(mode="json")
    run = CaseRun(
        case_id=case.id,
        evidence_revision=case.evidence_revision,
        idempotency_key=request.idempotency_key,
        request_payload={
            **saved_payload,
        },
        pipeline_config=pipeline,
    )
    db.add(run)
    await db.flush()
    return run


async def get_owned_case_run(
    db: AsyncSession,
    *,
    case_id: UUID,
    run_id: UUID,
    user_id: UUID | None,
) -> CaseRun:
    result = await db.execute(
        select(CaseRun)
        .join(Case, Case.id == CaseRun.case_id)
        .where(CaseRun.id == run_id, CaseRun.case_id == case_id, Case.user_id == user_id)
    )
    run = result.scalar_one_or_none()
    if run is None:
        raise CaseRunError("case_run_not_found", "Case run not found", status.HTTP_404_NOT_FOUND)
    return run


async def get_latest_case_analysis(
    db: AsyncSession,
    *,
    case_id: UUID,
    user_id: UUID | None,
) -> tuple[Case, CaseAnalysisResult | None]:
    result = await db.execute(
        select(Case)
        .options(
            selectinload(Case.latest_analysis_result),
        )
        .where(Case.id == case_id, Case.user_id == user_id)
    )
    case = result.scalar_one_or_none()
    if case is None:
        raise CaseRunError("case_not_found", "Case not found", status.HTTP_404_NOT_FOUND)
    analysis = case.latest_analysis_result
    return case, analysis


def analysis_freshness(case: Case, result: CaseAnalysisResult | None) -> str:
    if result is None:
        return "missing"
    rev = getattr(result, "evidence_revision", None)
    if rev is None:
        return "missing"
    return "current" if rev == case.evidence_revision else "stale"


async def locked_case(db: AsyncSession, case_id: UUID, user_id: UUID | None) -> Case:
    result = await db.execute(select(Case).where(Case.id == case_id).with_for_update())
    case = result.scalar_one_or_none()
    if case is None or case.user_id != user_id:
        raise CaseMaterialsError("case_not_found", "Case not found", status.HTTP_404_NOT_FOUND)
    return case


async def requeue_failed_case_run(
    db: AsyncSession,
    case: Case,
    run: CaseRun,
) -> CaseRun:
    if run.status != "failed":
        return run
    if run.evidence_revision != case.evidence_revision:
        raise CaseRunError(
            "case_run_superseded",
            "This failed analysis was superseded by newer Case evidence",
        )
    newer_run = await db.scalar(
        select(CaseRun.id)
        .where(
            CaseRun.case_id == case.id,
            CaseRun.id != run.id,
            CaseRun.created_at >= run.created_at,
        )
        .order_by(CaseRun.created_at.desc(), CaseRun.id.desc())
        .limit(1)
        .with_for_update()
    )
    if newer_run is not None:
        raise CaseRunError(
            "case_run_superseded",
            "This failed analysis was superseded by newer Case work",
        )
    run.status = "queued"
    run.error_code = None
    run.error_message = None
    run.started_at = None
    run.finished_at = None
    return run


async def existing_request_matches(
    run: CaseRun,
    request_payload: dict[str, object],
) -> bool:
    return run.request_payload == request_payload


@dataclass(frozen=True)
class ClaimedCaseRun:
    id: UUID
    case_id: UUID
    source_bundle: CaseSourceBundle
    attempt_count: int
    pipeline_config: dict[str, object]
    request_payload: dict[str, object]

    @property
    def source_revision(self) -> int:
        return self.source_bundle.revision


async def fail_case_run(
    db: AsyncSession,
    run_id: UUID,
    claimed_attempt: int,
    error_code: str,
    error_message: str,
) -> bool:
    now = datetime.now(timezone.utc)
    async with db.begin():
        result = await db.execute(
            update(CaseRun)
            .where(
                CaseRun.id == run_id,
                CaseRun.status == "running",
                CaseRun.attempt_count == claimed_attempt,
            )
            .values(
                status="failed",
                error_code=error_code,
                error_message=error_message,
                finished_at=now,
                updated_at=now,
            )
        )
        return bool(result.rowcount)


CASE_RUN_RECOVERY_CODE = "case_run_interrupted"


async def cleanup_abandoned_case_runs(session_factory: Callable[[], AsyncSession]) -> int:
    now = datetime.now(timezone.utc)
    async with session_factory() as db, db.begin():
        result = await db.execute(
            update(CaseRun)
            .where(CaseRun.status.in_(("queued", "running")))
            .values(
                status="failed",
                error_code=CASE_RUN_RECOVERY_CODE,
                error_message="Case processing was interrupted by application restart. Retry analysis.",
                finished_at=now,
                updated_at=now,
            )
        )
        return int(result.rowcount or 0)


__all__ = [
    "CASE_RUN_RECOVERY_CODE",
    "CaseRunError",
    "ClaimedCaseRun",
    "analysis_freshness",
    "cleanup_abandoned_case_runs",
    "enqueue_case_analysis",
    "fail_case_run",
    "get_latest_case_analysis",
    "get_owned_case_run",
    "requeue_failed_case_run",
]
