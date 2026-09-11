import asyncio
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from sqlalchemy import select

from app.models import Case, CaseRun, ChatMessage, ChatRun, ChatThread
from app.schemas.caseRuns import CaseAnalysisCreate
from app.services.case_materials import CaseMaterialsService
from app.services.workflow.caseRunService import cleanupAbandonedCaseRuns
from app.services.workflow.caseRunService import enqueue_case_analysis
from run_recovery_support import isolated_database


async def _legacy_run(factory, status: str) -> tuple[UUID, UUID]:
    case_id = uuid4()
    run_id = uuid4()
    async with factory() as db, db.begin():
        db.add(Case(id=case_id, title=f"Legacy {status}"))
        db.add(ChatThread(id=case_id, title=f"Legacy {status}", status="failed" if status == "failed" else "idle"))
        message = ChatMessage(
            id=uuid4(),
            thread_id=case_id,
            ordinal=1,
            role="user",
            content="Historical execution fixture",
            metadata_json={},
        )
        db.add(message)
        await db.flush()
        db.add(
            ChatRun(
                id=run_id,
                thread_id=case_id,
                request_message_id=message.id,
                status=status,
                idempotency_key=f"legacy-{status}",
                request_fingerprint="0" * 64,
                request_payload={},
                lease_expires_at=(
                    datetime.now(timezone.utc) - timedelta(seconds=1)
                    if status == "running"
                    else None
                ),
            )
        )
        if status == "queued":
            run = await db.get(ChatRun, run_id)
            run.updated_at = datetime.now(timezone.utc) - timedelta(minutes=7)
    return case_id, run_id


async def _case_run(factory) -> tuple[UUID, UUID]:
    case_id = uuid4()
    async with factory() as db, db.begin():
        db.add(Case(id=case_id, title="Native drain fixture"))
        await CaseMaterialsService(db).admitText(
            case_id=case_id,
            user_id=None,
            source_kind="narrative",
            exact_text="The native Case evidence remains isolated.",
            provenance_json={"origin": "drain-rehearsal"},
        )
        run = await enqueue_case_analysis(
            db,
            case_id=case_id,
            user_id=None,
            request=CaseAnalysisCreate(
                idempotency_key="native-drain",
                expected_evidence_revision=1,
            ),
        )
        run.updated_at = datetime.now(timezone.utc) - timedelta(minutes=7)
        return case_id, run.id


async def _retire_legacy_runs(factory) -> int:
    async with factory() as db, db.begin():
        runs = list(
            (
                await db.scalars(
                    select(ChatRun).where(ChatRun.status.in_(("queued", "running")))
                )
            ).all()
        )
        for run in runs:
            run.status = "failed"
            run.error_code = "chat_run_interrupted"
            run.error_message = "Legacy execution retired before this run started."
        return len(runs)


def test_disposable_drain_rehearsal_separates_legacy_and_case_workers():
    async def exercise():
        async with isolated_database() as factory:
            queued_case_id, queued_id = await _legacy_run(factory, "queued")
            running_case_id, running_id = await _legacy_run(factory, "running")
            failed_case_id, failed_id = await _legacy_run(factory, "failed")
            native_case_id, native_id = await _case_run(factory)

            legacy_retired, native_recovered = await asyncio.gather(
                _retire_legacy_runs(factory),
                cleanupAbandonedCaseRuns(factory),
            )

            assert legacy_retired == 2
            assert native_recovered == 1
            async with factory() as db:
                legacy_runs = list(
                    (
                        await db.scalars(
                            select(ChatRun).where(
                                ChatRun.id.in_((queued_id, running_id, failed_id))
                            )
                        )
                    ).all()
                )
                native_run = await db.get(CaseRun, native_id)
                legacy_by_id = {run.id: run for run in legacy_runs}
                assert {run.status for run in legacy_runs} == {"failed"}
                assert legacy_by_id[queued_id].error_code == "chat_run_interrupted"
                assert legacy_by_id[running_id].error_code == "chat_run_interrupted"
                assert legacy_by_id[failed_id].error_code is None
                assert native_run.status == "failed"
                assert native_run.error_code == "case_run_interrupted"
                assert await db.scalar(
                    select(ChatRun.id).where(ChatRun.thread_id == native_case_id)
                ) is None
                assert {queued_case_id, running_case_id, failed_case_id} == {
                    run.thread_id for run in legacy_runs
                }

    asyncio.run(exercise())
