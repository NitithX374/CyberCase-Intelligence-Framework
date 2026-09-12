from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from fastapi import status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.case import Case
from app.models.caseMaterials import CaseEvidenceSnapshot
from app.models.caseRun import CaseAnalysisResult, CaseRun
from app.schemas.caseRuns import CaseAnalysisCreate
from app.services.case_materials import (
    CaseMaterialsError,
    buildCaseEvidenceSnapshot,
)
from app.services.case_analysis.pipelineConfig import configured_pipeline


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
    clarification_id: UUID | None = None,
    request_message_id: UUID | None = None,
    request_payload_extra: dict[str, object] | None = None,
) -> CaseRun:
    case = await _locked_case(db, case_id, user_id)
    saved_payload = {
        "operation": "analysis",
        "response_language": request.response_language,
        "expected_evidence_revision": request.expected_evidence_revision,
        "clarification_id": str(clarification_id) if clarification_id else None,
        **(request_payload_extra or {}),
    }
    existing = await db.scalar(
        select(CaseRun)
        .where(CaseRun.case_id == case.id, CaseRun.idempotency_key == request.idempotency_key)
        .with_for_update()
    )
    if existing is not None:
        if not await _existing_request_matches(db, existing, saved_payload):
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

    active = await db.scalar(
        select(CaseRun.id)
        .where(CaseRun.case_id == case.id, CaseRun.status.in_(("queued", "running")))
        .with_for_update()
    )
    if active is not None:
        raise CaseRunError("case_run_active", "Case already has an active analysis run")

    snapshot = await buildCaseEvidenceSnapshot(db, case_id=case.id, user_id=user_id)
    pipeline = configured_pipeline().model_dump(mode="json")
    fingerprint = case_run_fingerprint(
        {
            "operation": "analysis",
            "response_language": request.response_language,
            "expected_evidence_revision": request.expected_evidence_revision,
            "clarification_id": str(clarification_id) if clarification_id else None,
            "snapshot_id": str(snapshot.id),
            "manifest_sha256": snapshot.manifest_sha256,
            "pipeline": pipeline,
            "request": saved_payload,
        }
    )
    run = CaseRun(
        case_id=case.id,
        operation="analysis",
        snapshot_id=snapshot.id,
        request_message_id=request_message_id,
        idempotency_key=request.idempotency_key,
        request_fingerprint=fingerprint,
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
            selectinload(Case.latest_analysis_result).selectinload(CaseAnalysisResult.snapshot),
        )
        .where(Case.id == case_id, Case.user_id == user_id)
    )
    case = result.scalar_one_or_none()
    if case is None:
        raise CaseRunError("case_not_found", "Case not found", status.HTTP_404_NOT_FOUND)
    analysis = case.latest_analysis_result
    return case, analysis


def analysis_freshness(case: Case, result: CaseAnalysisResult) -> str:
    if result.snapshot is None:
        return "missing"
    return "current" if result.snapshot.evidence_revision == case.evidence_revision else "stale"


async def _locked_case(db: AsyncSession, case_id: UUID, user_id: UUID | None) -> Case:
    result = await db.execute(select(Case).where(Case.id == case_id).with_for_update())
    case = result.scalar_one_or_none()
    if case is None or case.user_id != user_id:
        raise CaseMaterialsError("case_not_found", "Case not found", status.HTTP_404_NOT_FOUND)
    return case


def case_run_fingerprint(value: dict[str, object]) -> str:
    serialized = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


async def requeue_failed_case_run(
    db: AsyncSession,
    case: Case,
    run: CaseRun,
) -> CaseRun:
    if run.status != "failed":
        return run
    active = await db.scalar(
        select(CaseRun.id)
        .where(
            CaseRun.case_id == case.id,
            CaseRun.id != run.id,
            CaseRun.status.in_(("queued", "running")),
        )
        .with_for_update()
    )
    if active is not None:
        raise CaseRunError("case_run_active", "Case already has an active analysis run")
    snapshot_revision = await db.scalar(
        select(CaseEvidenceSnapshot.evidence_revision).where(
            CaseEvidenceSnapshot.id == run.snapshot_id,
            CaseEvidenceSnapshot.case_id == case.id,
        )
    )
    if snapshot_revision != case.evidence_revision:
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
    run.lease_owner = None
    run.lease_expires_at = None
    run.started_at = None
    run.finished_at = None
    return run


async def _existing_request_matches(
    db: AsyncSession,
    run: CaseRun,
    request_payload: dict[str, object],
) -> bool:
    if run.request_payload != request_payload:
        return False
    return await case_run_fingerprint_matches(db, run)


async def case_run_fingerprint_matches(
    db: AsyncSession,
    run: CaseRun,
) -> bool:
    snapshot = await db.get(CaseEvidenceSnapshot, run.snapshot_id)
    if snapshot is None:
        return False
    if run.operation == "analysis":
        expected = case_run_fingerprint(
            {
                "operation": "analysis",
                "response_language": run.request_payload.get("response_language"),
                "expected_evidence_revision": run.request_payload.get("expected_evidence_revision"),
                "clarification_id": run.request_payload.get("clarification_id"),
                "snapshot_id": str(snapshot.id),
                "manifest_sha256": snapshot.manifest_sha256,
                "pipeline": run.pipeline_config,
                "request": run.request_payload,
            }
        )
    elif run.operation == "ask":
        expected = case_run_fingerprint(
            {
                "request": run.request_payload,
                "snapshot_id": str(snapshot.id),
                "pipeline": run.pipeline_config,
            }
        )
    else:
        return False
    return run.request_fingerprint == expected


@dataclass(frozen=True)
class ClaimedCaseRun:
    id: UUID
    case_id: UUID
    snapshot_id: UUID
    attempt_count: int
    operation: str
    input_text: str
    text_sha256: str
    manifest: tuple[dict[str, object], ...]
    source_ids: tuple[str, ...]
    source_text_by_id: dict[str, str]
    pipeline_config: dict[str, object]
    request_payload: dict[str, object]


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
                lease_owner=None,
                lease_expires_at=None,
                updated_at=now,
            )
        )
        return bool(result.rowcount)


analysisFreshness = analysis_freshness
caseRunFingerprint = case_run_fingerprint
caseRunFingerprintMatches = case_run_fingerprint_matches
enqueueCaseAnalysis = enqueue_case_analysis
failCaseRun = fail_case_run
getLatestCaseAnalysis = get_latest_case_analysis
getOwnedCaseRun = get_owned_case_run
requeueFailedCaseRun = requeue_failed_case_run

CASE_RUN_RECOVERY_CODE = "case_run_interrupted"


async def cleanupAbandonedCaseRuns(session_factory: Callable[[], AsyncSession]) -> int:
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
                lease_owner=None,
                lease_expires_at=None,
                updated_at=now,
            )
        )
        return int(result.rowcount or 0)


__all__ = [
    "CASE_RUN_RECOVERY_CODE",
    "CaseRunError",
    "ClaimedCaseRun",
    "analysisFreshness",
    "analysis_freshness",
    "caseRunFingerprint",
    "caseRunFingerprintMatches",
    "case_run_fingerprint",
    "case_run_fingerprint_matches",
    "cleanupAbandonedCaseRuns",
    "enqueueCaseAnalysis",
    "enqueue_case_analysis",
    "failCaseRun",
    "fail_case_run",
    "getLatestCaseAnalysis",
    "get_latest_case_analysis",
    "getOwnedCaseRun",
    "get_owned_case_run",
    "requeueFailedCaseRun",
    "requeue_failed_case_run",
]
