import asyncio
from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.models import Case, CaseRun, ChatThread
from app.schemas.caseRuns import CaseAnalysisCreate
from app.schemas.chat import ChatMessageCreate
from app.services.case_materials import CaseMaterialsService
from app.services.chat import CaseChatError, createCaseChatMessageAndRun
from app.services.workflow.caseRunService import enqueue_case_analysis
from run_recovery_support import isolated_database


async def _case(factory):
    case_id = uuid4()
    async with factory() as db, db.begin():
        db.add(Case(id=case_id, title="Case Chat retry"))
        await CaseMaterialsService(db).admitText(
            case_id=case_id,
            user_id=None,
            source_kind="narrative",
            exact_text="The witness reported a blue vehicle.",
            provenance_json={"origin": "test"},
        )
        db.add(ChatThread(id=case_id, title="Case Chat retry", status="answered"))
    return case_id


async def _chat_run(factory, case_id, key):
    request = ChatMessageCreate(
        content="The witness identified the vehicle as blue.",
        idempotency_key=key,
        action="add_case_info",
    )
    async with factory() as db, db.begin():
        _, run = await createCaseChatMessageAndRun(
            db,
            case_id=case_id,
            user_id=None,
            request=request,
        )
        return run.id, request


async def _fail(factory, run_id):
    async with factory() as db, db.begin():
        run = await db.get(CaseRun, run_id, with_for_update=True)
        run.status = "failed"
        run.finished_at = datetime.now(timezone.utc)


async def _new_case_run(factory, case_id, key):
    async with factory() as db, db.begin():
        case = await db.get(Case, case_id)
        run = await enqueue_case_analysis(
            db,
            case_id=case_id,
            user_id=None,
            request=CaseAnalysisCreate(
                idempotency_key=key,
                expected_evidence_revision=case.evidence_revision,
            ),
        )
        return run.id


async def _replay(factory, case_id, request):
    async with factory() as db, db.begin():
        return await createCaseChatMessageAndRun(
            db,
            case_id=case_id,
            user_id=None,
            request=request,
        )


def test_case_chat_retry_reuses_centralized_guard_and_fingerprint():
    async def exercise():
        async with isolated_database() as factory:
            active_case = await _case(factory)
            active_id, active_request = await _chat_run(factory, active_case, "active-old")
            await _fail(factory, active_id)
            await _new_case_run(factory, active_case, "active-new")
            with pytest.raises(CaseChatError, match="active"):
                await _replay(factory, active_case, active_request)

            superseded_case = await _case(factory)
            old_id, old_request = await _chat_run(factory, superseded_case, "superseded-old")
            await _fail(factory, old_id)
            newer_id = await _new_case_run(factory, superseded_case, "superseded-new")
            await _fail(factory, newer_id)
            with pytest.raises(CaseChatError, match="superseded"):
                await _replay(factory, superseded_case, old_request)

            fingerprint_case = await _case(factory)
            fingerprint_id, fingerprint_request = await _chat_run(
                factory, fingerprint_case, "fingerprint"
            )
            await _fail(factory, fingerprint_id)
            async with factory() as db, db.begin():
                run = await db.get(CaseRun, fingerprint_id, with_for_update=True)
                run.request_fingerprint = "0" * 64
            with pytest.raises(CaseChatError, match="fingerprint"):
                await _replay(factory, fingerprint_case, fingerprint_request)

    asyncio.run(exercise())
