from __future__ import annotations

import re

import pytest
from case_chat_support import NARRATIVE, seeded_case
from isolated_database import isolated_database
from sqlalchemy import event, inspect

from app.errors import AppError
from app.models.analysis import CaseAnalysisResult
from app.models.case import Case
from app.models.chat import ChatMessage
from app.models.user import User
from app.schemas.cases import CaseUpdate
from app.services.cases.case_service import CaseService
from app.services.cases.ownership import owned_case
from app.services.workflow.run_analysis import get_latest_case_analysis, read_case_for_analysis

pytestmark = pytest.mark.asyncio


async def seeded(session_factory):
    async with session_factory() as db, db.begin():
        owner = User(email="owner@example.com", name="Owner", password_hash="x")
        other = User(email="other@example.com", name="Other", password_hash="x")
        db.add_all([owner, other])
        await db.flush()
        case = Case(user_id=owner.id, title="Owned case", source_revision=1)
        db.add(case)
        await db.flush()
        analysis = CaseAnalysisResult(
            case_id=case.id,
            source_revision=1,
            summary="Read.",
            trace_json={},
            pipeline_config={},
            external_context_json={},
        )
        db.add(analysis)
        await db.flush()
        case.latest_analysis_result_id = analysis.id
        db.add(ChatMessage(case_id=case.id, ordinal=1, role="user", content="Hello"))
        return case.id, owner.id, other.id


async def test_a_case_is_found_only_for_its_owner():
    async with isolated_database() as session_factory:
        case_id, owner_id, other_id = await seeded(session_factory)

        async with session_factory() as db:
            case = await owned_case(db, case_id, owner_id, lock=True)
            assert "chat_messages" in inspect(case).unloaded

            for stranger in (other_id, None):
                with pytest.raises(AppError) as refused:
                    await owned_case(db, case_id, stranger)
                assert (refused.value.code, refused.value.status_code) == ("case_not_found", 404)


async def test_a_renamed_case_reads_back_with_its_analysis():
    async with isolated_database() as session_factory:
        case_id, owner_id, _ = await seeded(session_factory)

        async with session_factory() as db:
            renamed = await CaseService(db).update_case(
                case_id, CaseUpdate(title="Renamed"), user_id=owner_id
            )

        assert renamed.title == "Renamed"
        assert renamed.analysis_freshness == "current"


async def test_the_latest_analysis_is_read_only_by_the_case_owner():
    async with isolated_database() as session_factory:
        case_id, owner_id, other_id = await seeded(session_factory)

        async with session_factory() as db:
            case, latest = await get_latest_case_analysis(db, case_id=case_id, user_id=owner_id)
            assert latest.id == case.latest_analysis_result_id

            for stranger in (other_id, None):
                with pytest.raises(AppError) as refused:
                    await get_latest_case_analysis(db, case_id=case_id, user_id=stranger)
                assert (refused.value.code, refused.value.status_code) == ("case_not_found", 404)


async def test_an_analysis_reads_its_sources_from_the_case_it_locked_once():
    async with isolated_database() as session_factory:
        case_id, user_id, _ = await seeded_case(session_factory, trace=None)
        engine = session_factory.kw["bind"].sync_engine
        statements: list[str] = []

        def record(connection, cursor, statement, parameters, context, executemany):
            statements.append(statement)

        event.listen(engine, "before_cursor_execute", record)
        try:
            started = await read_case_for_analysis(
                session_factory, case_id=case_id, user_id=user_id
            )
        finally:
            event.remove(engine, "before_cursor_execute", record)

        case_locks = [
            statement
            for statement in statements
            if re.search(r"\bFROM cases\b", statement) and "FOR UPDATE" in statement
        ]
        assert len(case_locks) == 1
        assert [source.text for source in started.source_bundle.sources] == [NARRATIVE]
