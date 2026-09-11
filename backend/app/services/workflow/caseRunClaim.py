from __future__ import annotations

import hashlib
from copy import deepcopy
from datetime import datetime, timezone
from typing import Mapping
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case
from app.models.caseMaterials import CaseEvidenceSnapshot
from app.models.caseRun import CaseRun
from app.services.case_materials import canonicalJson
from app.services.workflow.caseRunService import ClaimedCaseRun


async def claimCaseRun(
    db: AsyncSession,
    run_id: UUID,
    _worker_id: str,
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
                lease_owner=None,
                lease_expires_at=None,
                updated_at=now,
            )
            .returning(
                CaseRun.id,
                CaseRun.case_id,
                CaseRun.snapshot_id,
                CaseRun.operation,
                CaseRun.attempt_count,
                CaseRun.pipeline_config,
                CaseRun.request_payload,
            )
        )
        row = claimed.mappings().one_or_none()
        if row is None:
            return None
        case = await db.scalar(select(Case).where(Case.id == row["case_id"]))
        if case is None:
            await _fail_claimed_run(db, row["id"], row["attempt_count"], now, "case_not_found", "Case is missing")
            return None
        snapshot = await db.get(CaseEvidenceSnapshot, row["snapshot_id"])
        if snapshot is None or snapshot.case_id != case.id:
            await _fail_claimed_run(
                db,
                row["id"],
                row["attempt_count"],
                now,
                "case_snapshot_missing",
                "Pinned Case evidence snapshot is missing",
            )
            return None
        try:
            manifest = validateSnapshotManifest(snapshot)
        except ValueError as error:
            await _fail_claimed_run(
                db,
                row["id"],
                row["attempt_count"],
                now,
                "case_snapshot_invalid",
                str(error),
            )
            return None
        return ClaimedCaseRun(
            id=row["id"],
            case_id=row["case_id"],
            snapshot_id=snapshot.id,
            attempt_count=row["attempt_count"],
            operation=row["operation"],
            input_text=snapshot.input_text,
            text_sha256=snapshot.text_sha256,
            manifest=manifest,
            source_ids=tuple(str(item["source_id"]) for item in manifest),
            source_text_by_id={str(item["source_id"]): str(item["exact_text"]) for item in manifest},
            pipeline_config=deepcopy(row["pipeline_config"]),
            request_payload=deepcopy(row["request_payload"]),
        )


def validateSnapshotManifest(snapshot: CaseEvidenceSnapshot) -> tuple[dict[str, object], ...]:
    if hashlib.sha256(snapshot.input_text.encode("utf-8")).hexdigest() != snapshot.text_sha256:
        raise ValueError("Pinned snapshot text hash is invalid")
    if hashlib.sha256(canonicalJson(snapshot.manifest_json).encode("utf-8")).hexdigest() != snapshot.manifest_sha256:
        raise ValueError("Pinned snapshot manifest hash is invalid")
    if not isinstance(snapshot.manifest_json, list) or not snapshot.manifest_json:
        raise ValueError("Pinned snapshot manifest is empty")
    manifest: list[dict[str, object]] = []
    source_ids: set[str] = set()
    for item in snapshot.manifest_json:
        if not isinstance(item, Mapping):
            raise ValueError("Pinned snapshot manifest entry is invalid")
        source_id = item.get("source_id")
        exact_text = item.get("exact_text")
        text_hash = item.get("text_sha256")
        if not all(isinstance(value, str) and value.strip() for value in (source_id, exact_text, text_hash)):
            raise ValueError("Pinned snapshot source reference is incomplete")
        if source_id in source_ids:
            raise ValueError("Pinned snapshot contains duplicate source IDs")
        if hashlib.sha256(exact_text.encode("utf-8")).hexdigest() != text_hash:
            raise ValueError("Pinned snapshot source text hash is invalid")
        source_ids.add(source_id)
        manifest.append(dict(item))
    return tuple(manifest)


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
            lease_owner=None,
            lease_expires_at=None,
            updated_at=finished_at,
        )
    )

__all__ = ["claimCaseRun", "validateSnapshotManifest"]
