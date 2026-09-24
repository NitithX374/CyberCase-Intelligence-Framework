import asyncio
import json
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from migration_support import migrate, schema_before
from sqlalchemy import inspect, text
from sqlalchemy.exc import DBAPIError

FOLD = "0016_fold_extractions"
TEXT = "Page one of the statement."


def tables_and_columns(connection, schema):
    inspector = inspect(connection)
    tables = set(inspector.get_table_names(schema=schema))
    columns = {
        table: {column["name"] for column in inspector.get_columns(table, schema=schema)}
        for table in ("case_documents", "case_sources", "users", "case_analysis_results")
    }
    return tables, columns


async def seed(connection, *, extraction_text=TEXT, active_origin=False):
    ids = {name: uuid4() for name in ("user", "case", "doc", "extraction", "message", "analysis")}
    ids |= {"empty_case": uuid4(), "kept_case": uuid4(), "doc_source": uuid4(), "story": uuid4()}

    async def run(sql, **values):
        await connection.execute(text(sql), values)

    await run(
        "INSERT INTO users (id, email, name, oauth_provider, oauth_subject_id) "
        "VALUES (:id, :email, 'Analyst', 'password', :email)",
        id=ids["user"],
        email=f"{ids['user'].hex}@example.com",
    )
    await run(
        "INSERT INTO cases (id, user_id, title) VALUES (:case, :user, 'Owned'), "
        "(:empty, NULL, 'Empty'), (:kept, NULL, 'Kept')",
        case=ids["case"],
        user=ids["user"],
        empty=ids["empty_case"],
        kept=ids["kept_case"],
    )
    await run(
        "INSERT INTO case_documents (id, case_id, filename, mime_type, size_bytes, content_bytes) "
        "VALUES (:id, :case, 'statement.pdf', 'application/pdf', 3, 'pdf')",
        id=ids["doc"],
        case=ids["case"],
    )
    await run(
        "INSERT INTO document_extractions (id, document_id, provider, extracted_text) "
        "VALUES (:id, :doc, 'native', :text)",
        id=ids["extraction"],
        doc=ids["doc"],
        text=extraction_text,
    )
    await run(
        "INSERT INTO chat_messages (id, case_id, ordinal, role, content, message_kind, "
        "metadata_json) VALUES (:id, :case, 1, 'user', 'An old answer', 'followup_answer', "
        "CAST(:metadata AS jsonb))",
        id=ids["message"],
        case=ids["case"],
        metadata=json.dumps({"action": "follow_up"}),
    )
    await run(
        "INSERT INTO case_sources (id, case_id, source_kind, document_id, exact_text, "
        "provenance_json) VALUES (:id, :case, 'document', :doc, :text, CAST(:provenance AS jsonb))",
        id=ids["doc_source"],
        case=ids["case"],
        doc=ids["doc"],
        text=TEXT,
        provenance=json.dumps({"extraction_id": str(ids["extraction"]), "provider": "native"}),
    )
    await run(
        "INSERT INTO case_sources (id, case_id, source_kind, exact_text, source_metadata_json) "
        "VALUES (:id, :case, 'narrative', 'What happened.', CAST(:metadata AS jsonb))",
        id=ids["story"],
        case=ids["case"],
        metadata=json.dumps({"interface": "case_sources", "evidence_role": "narrative"}),
    )
    await run(
        "INSERT INTO case_sources (id, case_id, source_kind, origin_message_id, exact_text, "
        "archived_at) VALUES (:id, :case, 'followup_answer', :message, 'An old answer', :archived)",
        id=uuid4(),
        case=ids["case"],
        message=ids["message"],
        archived=None if active_origin else datetime.now(UTC),
    )
    await run(
        "INSERT INTO case_sources (id, case_id, source_kind, exact_text) "
        "VALUES (:id, :case, 'narrative', 'Not empty.')",
        id=uuid4(),
        case=ids["kept_case"],
    )
    await run(
        "INSERT INTO case_analysis_results (id, case_id, source_revision, answer, summary, "
        "external_context_json) VALUES (:id, :case, 1, 'Older prose', 'Summary', "
        "CAST(:context AS jsonb))",
        id=ids["analysis"],
        case=ids["case"],
        context=json.dumps(
            {
                "source_reference_type": "case_source",
                "source_revision": 1,
                "evidence_revision": 1,
                "technical_augmentation": {"status": "not_applicable"},
            }
        ),
    )
    return ids


def test_fold_keeps_the_text_and_drops_what_nothing_reads() -> None:
    async def exercise() -> None:
        async with (
            schema_before(FOLD) as (engine, schema, fold),
            engine.begin() as connection,
        ):
            ids = await seed(connection)
            await connection.run_sync(migrate, schema, (fold, "upgrade"))

            tables, columns = await connection.run_sync(tables_and_columns, schema)
            assert "document_extractions" not in tables
            assert "archived_at" not in columns["case_documents"]
            assert "origin_message_id" not in columns["case_sources"]
            assert "avatar_url" not in columns["users"]
            assert "answer" not in columns["case_analysis_results"]

            source = await connection.execute(
                text("SELECT exact_text, provenance_json FROM case_sources WHERE id = :id"),
                {"id": ids["doc_source"]},
            )
            exact_text, provenance = source.one()
            assert exact_text == TEXT
            assert provenance == {"provider": "native"}

            metadata = await connection.scalar(
                text("SELECT source_metadata_json FROM case_sources WHERE id = :id"),
                {"id": ids["story"]},
            )
            assert metadata == {"interface": "case_sources"}

            context = await connection.scalar(
                text("SELECT external_context_json FROM case_analysis_results WHERE id = :id"),
                {"id": ids["analysis"]},
            )
            assert context == {"technical_augmentation": {"status": "not_applicable"}}

            message_metadata = await connection.scalar(
                text("SELECT metadata_json FROM chat_messages WHERE id = :id"),
                {"id": ids["message"]},
            )
            assert message_metadata == {}

            remaining = set(await connection.scalars(text("SELECT id FROM cases")))
            assert remaining == {ids["case"], ids["kept_case"]}

            await connection.run_sync(migrate, schema, (fold, "downgrade"))
            tables, columns = await connection.run_sync(tables_and_columns, schema)
            assert "document_extractions" in tables
            assert "answer" in columns["case_analysis_results"]
            refilled = await connection.execute(
                text("SELECT document_id, extracted_text, provider FROM document_extractions")
            )
            assert refilled.all() == [(ids["doc"], TEXT, "native")]
            answer = await connection.scalar(
                text("SELECT answer FROM case_analysis_results WHERE id = :id"),
                {"id": ids["analysis"]},
            )
            assert answer == "Summary"

            await connection.run_sync(migrate, schema, (fold, "upgrade"))

    asyncio.run(exercise())


@pytest.mark.parametrize(
    ("seeding", "reason"),
    [
        ({"extraction_text": "Different text."}, "extraction holds text"),
        ({"active_origin": True}, "origin_message_id"),
    ],
)
def test_fold_refuses_when_something_would_be_lost(seeding, reason) -> None:
    async def exercise() -> None:
        async with schema_before(FOLD) as (engine, schema, fold):
            async with engine.begin() as connection:
                await seed(connection, **seeding)

            with pytest.raises(DBAPIError, match=reason):
                async with engine.begin() as connection:
                    await connection.run_sync(migrate, schema, (fold, "upgrade"))

            async with engine.connect() as connection:
                tables, _ = await connection.run_sync(tables_and_columns, schema)
            assert "document_extractions" in tables

    asyncio.run(exercise())
