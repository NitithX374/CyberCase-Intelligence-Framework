import asyncio
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest
from migration_support import migrate, schema_before
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import selectinload

from app.models import Case, CaseAnalysisResult, CaseSource
from app.services.sources.case_source_bundle import (
    case_source_bundle_for_analysis,
    case_source_bundle_from_case,
)
from app.services.sources.source_service import SourceService

ARCHIVE = "0014_archive_followup_sources"


def test_archive_migration_preserves_history_and_hides_old_sources() -> None:
    async def exercise() -> None:
        async with schema_before(ARCHIVE) as (engine, schema, archive):
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

            async with engine.begin() as connection:
                await connection.execute(
                    text(
                        "INSERT INTO cases (id, title, source_revision) "
                        "VALUES (:case, 'Legacy follow-up', 3), (:other, 'Other case', 2)"
                    ),
                    {"case": case_id, "other": other_case_id},
                )
                await connection.execute(
                    text(
                        "INSERT INTO chat_messages (id, case_id, ordinal, role, content, "
                        "message_kind) VALUES "
                        "(:first, :case, 1, 'user', 'First answer', 'conversation'), "
                        "(:second, :case, 2, 'user', 'Second answer', 'followup_answer')"
                    ),
                    {"first": first_message_id, "second": second_message_id, "case": case_id},
                )
                await connection.execute(
                    text(
                        "INSERT INTO case_sources (id, case_id, source_kind, origin_message_id, "
                        "exact_text, archived_at, created_at) VALUES "
                        "(:narrative, :case, 'narrative', NULL, 'Original narrative', NULL, :then), "
                        "(:first_source, :case, 'followup_answer', :first, 'First answer', "
                        "NULL, :then), "
                        "(:second_source, :case, 'followup_answer', :second, 'Second answer', "
                        "NULL, :then), "
                        "(:archived, :other, 'followup_answer', NULL, 'Already archived', "
                        ":archived_at, :then)"
                    ),
                    {
                        "narrative": narrative_id,
                        "first_source": first_source_id,
                        "second_source": second_source_id,
                        "archived": archived_source_id,
                        "case": case_id,
                        "other": other_case_id,
                        "first": first_message_id,
                        "second": second_message_id,
                        "archived_at": prior_archive_time,
                        "then": historical_time,
                    },
                )
                await connection.execute(
                    text(
                        "INSERT INTO case_analysis_results (id, case_id, source_revision, answer, "
                        "summary, trace_json, created_at) VALUES "
                        "(:id, :case, 3, 'Old answer', 'Old summary', '{}'::jsonb, :at)"
                    ),
                    {"id": uuid4(), "case": case_id, "at": historical_time + timedelta(hours=1)},
                )

            async with engine.begin() as connection:
                await connection.run_sync(migrate, schema, (archive, "upgrade"))
                origins = await connection.execute(
                    text(
                        "SELECT id, origin_message_id FROM case_sources "
                        "WHERE source_kind = 'followup_answer' AND case_id = :case"
                    ),
                    {"case": case_id},
                )
                assert dict(origins.all()) == {
                    first_source_id: first_message_id,
                    second_source_id: second_message_id,
                }

            async with async_sessionmaker(engine)() as db:
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
        async with schema_before(ARCHIVE) as (engine, schema, archive):
            case_id = uuid4()
            source_id = uuid4()
            async with engine.begin() as connection:
                await connection.execute(
                    text(
                        "INSERT INTO cases (id, title, source_revision) "
                        "VALUES (:id, 'Unmatched follow-up', 5)"
                    ),
                    {"id": case_id},
                )
                await connection.execute(
                    text(
                        "INSERT INTO case_sources (id, case_id, source_kind, exact_text) "
                        "VALUES (:id, :case, 'followup_answer', 'Unique answer')"
                    ),
                    {"id": source_id, "case": case_id},
                )

            with pytest.raises(DBAPIError, match="Unmatched active follow-up sources"):
                async with engine.begin() as connection:
                    await connection.run_sync(migrate, schema, (archive, "upgrade"))

            async with async_sessionmaker(engine)() as db:
                case = await db.get(Case, case_id)
                source = await db.get(CaseSource, source_id)
                assert case is not None and case.source_revision == 5
                assert source is not None and source.archived_at is None

    asyncio.run(exercise())
