import asyncio
import importlib.util
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from isolated_database import isolated_database
from sqlalchemy import select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import selectinload

from app.models import Case, CaseAnalysisResult, CaseSource, ChatMessage
from app.services.sources import SourceService
from app.services.sources.case_source_bundle import (
    case_source_bundle_for_analysis,
    case_source_bundle_from_case,
)


def apply_archive_migration(connection) -> None:
    migration_path = (
        Path(__file__).parents[1]
        / "alembic"
        / "baseline_versions"
        / "0014_archive_legacy_followup_sources.py"
    )
    spec = importlib.util.spec_from_file_location("archive_legacy_followup_sources", migration_path)
    assert spec is not None and spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    migration.op = Operations(MigrationContext.configure(connection))
    migration.upgrade()


def test_archive_migration_preserves_history_and_hides_old_sources() -> None:
    async def exercise() -> None:
        async with isolated_database() as factory:
            case_id = uuid4()
            other_case_id = uuid4()
            narrative_id = uuid4()
            first_source_id = uuid4()
            second_source_id = uuid4()
            archived_source_id = uuid4()
            first_message_id = uuid4()
            second_message_id = uuid4()
            historical_time = datetime.now(UTC) - timedelta(days=1)
            prior_archive_time = historical_time + timedelta(hours=2)

            async with factory() as db, db.begin():
                db.add_all(
                    [
                        Case(id=case_id, title="Legacy follow-up", source_revision=3),
                        Case(id=other_case_id, title="Other case", source_revision=2),
                    ]
                )
                await db.flush()
                db.add_all(
                    [
                        ChatMessage(
                            id=first_message_id,
                            case_id=case_id,
                            ordinal=1,
                            role="user",
                            content="First answer",
                            message_kind="conversation",
                        ),
                        ChatMessage(
                            id=second_message_id,
                            case_id=case_id,
                            ordinal=2,
                            role="user",
                            content="Second answer",
                            message_kind="followup_answer",
                        ),
                    ]
                )
                await db.flush()
                db.add_all(
                    [
                        CaseSource(
                            id=narrative_id,
                            case_id=case_id,
                            source_kind="narrative",
                            exact_text="Original narrative",
                            created_at=historical_time,
                        ),
                        CaseSource(
                            id=first_source_id,
                            case_id=case_id,
                            source_kind="followup_answer",
                            origin_message_id=first_message_id,
                            exact_text="First answer",
                            created_at=historical_time,
                        ),
                        CaseSource(
                            id=second_source_id,
                            case_id=case_id,
                            source_kind="followup_answer",
                            origin_message_id=second_message_id,
                            exact_text="Second answer",
                            created_at=historical_time,
                        ),
                        CaseSource(
                            id=archived_source_id,
                            case_id=other_case_id,
                            source_kind="followup_answer",
                            exact_text="Already archived",
                            archived_at=prior_archive_time,
                            created_at=historical_time,
                        ),
                        CaseAnalysisResult(
                            case_id=case_id,
                            source_revision=3,
                            answer="Old answer",
                            summary="Old summary",
                            trace_json={},
                            created_at=historical_time + timedelta(hours=1),
                        ),
                    ]
                )

            async with factory() as db, db.begin():
                connection = await db.connection()
                await connection.run_sync(apply_archive_migration)

            async with factory() as db:
                case = await db.get(Case, case_id)
                other_case = await db.get(Case, other_case_id)
                assert case is not None and case.source_revision == 4
                assert other_case is not None and other_case.source_revision == 2

                sources = list(
                    (
                        await db.execute(
                            select(CaseSource)
                            .options(selectinload(CaseSource.document))
                            .where(CaseSource.case_id == case_id)
                        )
                    )
                    .scalars()
                    .all()
                )
                by_id = {source.id: source for source in sources}
                assert by_id[first_source_id].archived_at is not None
                assert by_id[second_source_id].archived_at is not None
                assert by_id[first_source_id].origin_message_id == first_message_id
                assert by_id[second_source_id].origin_message_id == second_message_id
                assert by_id[first_source_id].exact_text == "First answer"
                assert by_id[second_source_id].exact_text == "Second answer"

                visible_sources = await SourceService(db).list_sources(case_id, None)
                assert {source.id for source in visible_sources} == {narrative_id}
                archived_source = await db.get(CaseSource, archived_source_id)
                assert archived_source is not None
                assert archived_source.archived_at == prior_archive_time

                analysis = (
                    await db.execute(
                        select(CaseAnalysisResult).where(CaseAnalysisResult.case_id == case_id)
                    )
                ).scalar_one()
                assert analysis.source_revision == 3
                assert analysis.summary == "Old summary"

                case_snapshot = SimpleNamespace(
                    sources=sources, source_revision=case.source_revision
                )
                current = case_source_bundle_from_case(case_snapshot)
                historical = case_source_bundle_for_analysis(case_snapshot, analysis)
                assert {item.source_id for item in current.sources} == {str(narrative_id)}
                assert {item.source_id for item in historical.sources} == {
                    str(narrative_id),
                    str(first_source_id),
                    str(second_source_id),
                }

    asyncio.run(exercise())


def test_archive_migration_rejects_unmatched_followup_source() -> None:
    async def exercise() -> None:
        async with isolated_database() as factory:
            case_id = uuid4()
            source_id = uuid4()
            async with factory() as db, db.begin():
                db.add(Case(id=case_id, title="Unmatched follow-up", source_revision=5))
                await db.flush()
                db.add(
                    CaseSource(
                        id=source_id,
                        case_id=case_id,
                        source_kind="followup_answer",
                        exact_text="Unique answer",
                    )
                )

            with pytest.raises(DBAPIError, match="Unmatched active follow-up sources"):
                async with factory() as db, db.begin():
                    connection = await db.connection()
                    await connection.run_sync(apply_archive_migration)

            async with factory() as db:
                case = await db.get(Case, case_id)
                source = await db.get(CaseSource, source_id)
                assert case is not None and case.source_revision == 5
                assert source is not None and source.archived_at is None

    asyncio.run(exercise())
