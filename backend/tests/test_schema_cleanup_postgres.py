import asyncio
from uuid import uuid4

import pytest
from isolated_database import isolated_database
from migration_support import migrate, schema_before
from sqlalchemy import func, inspect, select, text
from sqlalchemy.exc import DBAPIError

from app.models import (
    Case,
    CaseAnalysisResult,
    CaseDocument,
    CaseReport,
    CaseSource,
    ChatMessage,
)
from app.services.cases.case_service import CaseService

CLEANUP = "0015_schema_cleanup"
REPORT_ANALYSIS_FK = "fk_case_reports_analysis_result_id_case_analysis_results"


def shape(connection, schema):
    inspector = inspect(connection)
    user_columns = {column["name"] for column in inspector.get_columns("users", schema=schema)}
    indexes = {
        index["name"]
        for table in ("users", "cases", "chat_messages")
        for index in inspector.get_indexes(table, schema=schema)
    }
    report_fk = next(
        fk
        for fk in inspector.get_foreign_keys("case_reports", schema=schema)
        if fk["name"] == REPORT_ANALYSIS_FK
    )
    return user_columns, indexes, report_fk["options"].get("ondelete")


async def seed_case_with_report(connection, *, verification_hash=None):
    user_id, case_id, analysis_id = uuid4(), uuid4(), uuid4()
    await connection.execute(
        text(
            "INSERT INTO users (id, email, name, oauth_provider, oauth_subject_id, "
            "verification_hash) VALUES (:id, :email, 'Analyst', 'password', :email, :hash)"
        ),
        {"id": user_id, "email": f"{user_id.hex}@example.com", "hash": verification_hash},
    )
    await connection.execute(
        text("INSERT INTO cases (id, user_id, title) VALUES (:id, :user, 'Case')"),
        {"id": case_id, "user": user_id},
    )
    await connection.execute(
        text(
            "INSERT INTO case_analysis_results (id, case_id, source_revision, answer, summary) "
            "VALUES (:id, :case, 1, 'Summary', 'Summary')"
        ),
        {"id": analysis_id, "case": case_id},
    )
    await connection.execute(
        text(
            "INSERT INTO case_reports (id, case_id, analysis_result_id, version_number, "
            "structured_report) VALUES (:id, :case, :analysis, 1, '{}'::jsonb)"
        ),
        {"id": uuid4(), "case": case_id, "analysis": analysis_id},
    )
    return analysis_id


def test_cleanup_round_trips_and_a_report_goes_with_its_analysis() -> None:
    async def exercise() -> None:
        async with (
            schema_before(CLEANUP) as (engine, schema, cleanup),
            engine.begin() as connection,
        ):
            analysis_id = await seed_case_with_report(connection)
            await connection.run_sync(migrate, schema, (cleanup, "upgrade"))
            columns, indexes, ondelete = await connection.run_sync(shape, schema)

            assert {"verification_hash", "verification_expires_at"}.isdisjoint(columns)
            assert "ix_cases_user_id_updated_at" in indexes
            assert {
                "ix_users_email",
                "ix_chat_messages_case_id_ordinal",
                "ix_cases_user_id",
                "ix_cases_updated_at",
            }.isdisjoint(indexes)
            assert ondelete == "CASCADE"

            await connection.execute(
                text("DELETE FROM case_analysis_results WHERE id = :id"), {"id": analysis_id}
            )
            reports = await connection.scalar(text("SELECT count(*) FROM case_reports"))
            assert reports == 0

            await connection.run_sync(migrate, schema, (cleanup, "downgrade"))
            columns, indexes, ondelete = await connection.run_sync(shape, schema)
            assert {"verification_hash", "verification_expires_at"} <= columns
            assert {"ix_users_email", "ix_cases_user_id", "ix_cases_updated_at"} <= indexes
            assert "ix_cases_user_id_updated_at" not in indexes
            assert ondelete == "RESTRICT"

            await connection.run_sync(migrate, schema, (cleanup, "upgrade"))

    asyncio.run(exercise())


def test_cleanup_refuses_to_drop_verification_values() -> None:
    async def exercise() -> None:
        async with schema_before(CLEANUP) as (engine, schema, cleanup):
            async with engine.begin() as connection:
                await seed_case_with_report(connection, verification_hash="still-here")

            with pytest.raises(DBAPIError, match="verification"):
                async with engine.begin() as connection:
                    await connection.run_sync(migrate, schema, (cleanup, "upgrade"))

            async with engine.connect() as connection:
                columns, _, ondelete = await connection.run_sync(shape, schema)
            assert "verification_hash" in columns
            assert ondelete == "RESTRICT"

    asyncio.run(exercise())


def test_deleting_a_case_removes_everything_it_owns() -> None:
    async def exercise() -> None:
        async with isolated_database() as factory:
            case_id, other_case_id = uuid4(), uuid4()
            async with factory() as db, db.begin():
                db.add_all([Case(id=case_id, title="Doomed"), Case(id=other_case_id, title="Kept")])
                await db.flush()
                document = CaseDocument(
                    case_id=case_id,
                    filename="statement.pdf",
                    mime_type="application/pdf",
                    size_bytes=3,
                    content_bytes=b"pdf",
                )
                db.add(document)
                await db.flush()
                analysis = CaseAnalysisResult(case_id=case_id, source_revision=2, summary="Summary")
                db.add_all(
                    [
                        CaseSource(
                            case_id=case_id,
                            source_kind="document",
                            document_id=document.id,
                            exact_text="Text",
                        ),
                        CaseSource(case_id=case_id, source_kind="narrative", exact_text="Story"),
                        CaseSource(
                            case_id=other_case_id, source_kind="narrative", exact_text="Other"
                        ),
                        analysis,
                    ]
                )
                await db.flush()
                db.add_all(
                    [
                        ChatMessage(
                            case_id=case_id,
                            ordinal=1,
                            role="assistant",
                            content="When did it happen?",
                            message_kind="followup_question",
                            gap_key="topic:time",
                            analysis_result_id=analysis.id,
                        ),
                        CaseReport(
                            case_id=case_id,
                            analysis_result_id=analysis.id,
                            version_number=1,
                            structured_report={},
                        ),
                    ]
                )
                await db.execute(
                    Case.__table__.update()
                    .where(Case.id == case_id)
                    .values(latest_analysis_result_id=analysis.id)
                )

            async with factory() as db:
                await CaseService(db).delete_case(case_id, None)

            async with factory() as db:
                for model in (
                    Case,
                    CaseDocument,
                    CaseSource,
                    CaseAnalysisResult,
                    ChatMessage,
                    CaseReport,
                ):
                    remaining = await db.scalar(
                        select(func.count()).select_from(model).where(model.case_id == case_id)
                        if model is not Case
                        else select(func.count()).select_from(Case).where(Case.id == case_id)
                    )
                    assert remaining == 0, model.__tablename__
                kept = await db.scalar(
                    select(func.count())
                    .select_from(CaseSource)
                    .where(CaseSource.case_id == other_case_id)
                )
                assert kept == 1

    asyncio.run(exercise())
