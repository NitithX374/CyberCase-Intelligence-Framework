import asyncio
import importlib.util
import os
from pathlib import Path
from uuid import uuid4

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import create_async_engine

import app.models  # noqa: F401
from app.database import Base

EXPECTED_CANONICAL_TABLES = {
    "cases",
    "users",
    "chat_messages",
    "case_documents",
    "case_sources",
    "case_analysis_results",
    "case_reports",
}


def _load_migration_modules():
    baseline = Path(__file__).parents[1] / "alembic" / "baseline_versions"
    names = [path.name for path in sorted(baseline.glob("[0-9]*.py"))]
    modules = []
    for index, name in enumerate(names, start=1):
        path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../alembic/baseline_versions", name)
        )
        spec = importlib.util.spec_from_file_location(f"alembic_{index}", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        modules.append(mod)
    return modules


def test_alembic_baseline_upgrade_matches_base_metadata():
    url = os.environ.get("CYBERCASE_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set CYBERCASE_TEST_DATABASE_URL to run PostgreSQL integration tests")

    async def exercise():
        schema = f"parity_test_{uuid4().hex[:8]}"
        admin_engine = create_async_engine(url)
        engine = create_async_engine(url, connect_args={"server_settings": {"search_path": schema}})
        migrations = _load_migration_modules()

        try:
            async with admin_engine.begin() as conn:
                await conn.execute(text(f'CREATE SCHEMA "{schema}"'))

            async with engine.begin() as conn:

                def run_upgrade(sync_conn):
                    sync_conn.execute(text(f'SET search_path TO "{schema}"'))
                    ctx = MigrationContext.configure(sync_conn)
                    op = Operations(ctx)
                    for migration in migrations:
                        migration.op = op
                        migration.upgrade()

                await conn.run_sync(run_upgrade)

            async with engine.connect() as conn:

                def inspect_schema(sync_conn):
                    sync_conn.execute(text(f'SET search_path TO "{schema}"'))
                    inspector = inspect(sync_conn)
                    tables = set(inspector.get_table_names(schema=schema))
                    assert tables == EXPECTED_CANONICAL_TABLES, (
                        f"Tables mismatch: {tables ^ EXPECTED_CANONICAL_TABLES}"
                    )
                    assert "case_clarifications" not in tables
                    assert "case_state_versions" not in tables
                    assert "chat_threads" not in tables
                    assert "case_evidence_snapshots" not in tables
                    assert "case_evidence_revisions" not in tables

                    for table_name in EXPECTED_CANONICAL_TABLES:
                        orm_table = Base.metadata.tables[table_name]
                        db_columns = {
                            c["name"]: c for c in inspector.get_columns(table_name, schema=schema)
                        }
                        assert set(db_columns) == set(orm_table.c.keys())
                        for orm_col_name, orm_col in orm_table.c.items():
                            assert orm_col_name in db_columns, (
                                f"Column {table_name}.{orm_col_name} missing from DB"
                            )
                            db_col = db_columns[orm_col_name]
                            assert db_col["nullable"] == orm_col.nullable, (
                                f"Column {table_name}.{orm_col_name} nullable mismatch: DB={db_col['nullable']}, ORM={orm_col.nullable}"
                            )

                    analysis_fks = inspector.get_foreign_keys(
                        "case_analysis_results", schema=schema
                    )
                    case_fk = next(fk for fk in analysis_fks if fk["referred_table"] == "cases")
                    assert case_fk.get("options", {}).get("ondelete") == "CASCADE"
                    assert not any(
                        fk["referred_table"] in {"case_runs", "rag_contexts"} for fk in analysis_fks
                    ), "the analysis still points at a removed table"

                    message_fks = inspector.get_foreign_keys("chat_messages", schema=schema)
                    analysis_link = next(
                        fk for fk in message_fks if fk["referred_table"] == "case_analysis_results"
                    )
                    assert analysis_link.get("options", {}).get("ondelete") == "SET NULL"

                    message_uniques = inspector.get_unique_constraints(
                        "chat_messages", schema=schema
                    )
                    assert any(
                        u["column_names"] == ["case_id", "ordinal"] for u in message_uniques
                    ), "uq_chat_messages_case_id_ordinal missing"

                    msg_cols = {
                        c["name"] for c in inspector.get_columns("chat_messages", schema=schema)
                    }
                    assert "in_reply_to_message_id" in msg_cols

                await conn.run_sync(inspect_schema)

        finally:
            await engine.dispose()
            async with admin_engine.begin() as conn:
                await conn.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
            await admin_engine.dispose()

    asyncio.run(exercise())
