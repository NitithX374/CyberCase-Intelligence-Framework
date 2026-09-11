import asyncio
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.models import Case, CaseRun
from app.schemas.caseRuns import CaseAnalysisCreate
from app.services.case_materials import CaseMaterialsService
from app.services.workflow.caseRunService import (
    CaseRunError,
    enqueue_case_analysis,
)
from run_recovery_support import isolated_database


async def _case_with_source(factory: async_sessionmaker):
    case_id = uuid4()
    async with factory() as db, db.begin():
        db.add(Case(id=case_id, title="Retry safeguards"))
        await CaseMaterialsService(db).admitText(
            case_id=case_id,
            user_id=None,
            source_kind="narrative",
            exact_text="The witness reported a blue vehicle.",
            provenance_json={"origin": "test"},
        )
    return case_id


async def _enqueue(factory, case_id, key, response_language="english"):
    async with factory() as db, db.begin():
        run = await enqueue_case_analysis(
            db,
            case_id=case_id,
            user_id=None,
            request=CaseAnalysisCreate(
                idempotency_key=key,
                response_language=response_language,
                expected_evidence_revision=1,
            ),
        )
        return run.id


async def _fail(factory, run_id):
    async with factory() as db, db.begin():
        run = await db.get(CaseRun, run_id, with_for_update=True)
        run.status = "failed"
        run.finished_at = datetime.now(timezone.utc)


def test_failed_case_retry_rejects_newer_work_and_active_work():
    async def exercise():
        async with isolated_database() as factory:
            case_id = await _case_with_source(factory)
            old_run = await _enqueue(factory, case_id, "old-run")
            await _fail(factory, old_run)
            with pytest.raises(CaseRunError) as conflict:
                await _enqueue(factory, case_id, "old-run", response_language="thai")
            assert conflict.value.code == "idempotency_conflict"
            new_run = await _enqueue(factory, case_id, "new-run")
            await _fail(factory, new_run)
            with pytest.raises(CaseRunError, match="superseded") as superseded:
                await _enqueue(factory, case_id, "old-run")
            assert superseded.value.code == "case_run_superseded"

            active_case = await _case_with_source(factory)
            active_old = await _enqueue(factory, active_case, "active-old")
            await _fail(factory, active_old)
            await _enqueue(factory, active_case, "active-new")
            with pytest.raises(CaseRunError, match="active") as active:
                await _enqueue(factory, active_case, "active-old")
            assert active.value.code == "case_run_active"

    asyncio.run(exercise())
