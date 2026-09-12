"""Database schema parity integration tests: Alembic baseline vs PostgreSQL catalog vs Base.metadata."""

import asyncio
import importlib.util
import os
from uuid import uuid4

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import create_async_engine

from app.database import Base
import app.models  # Ensure all models are registered on Base.metadata

EXPECTED_CANONICAL_TABLES = {
    "cases",
    "users",
    "chat_threads",
    "chat_messages",
    "case_documents",
    "document_extractions",
    "case_evidence_sources",
    "case_evidence_revisions",
    "case_evidence_snapshots",
    "case_runs",
    "case_analysis_results",
    "rag_contexts",
    "case_reports",
}


def _load_migration_modules():
    names = (
        "0001_canonical_case_system.py",
        "0002_drop_chat_status_and_context_result.py",
        "0003_case_run_request_no_action.py",
    )
    modules = []
    for index, name in enumerate(names, start=1):
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../alembic/baseline_versions", name))
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
        engine = create_async_engine(
            url, connect_args={"server_settings": {"search_path": schema}}
        )
        migrations = _load_migration_modules()

        try:
            async with admin_engine.begin() as conn:
                await conn.execute(text(f'CREATE SCHEMA "{schema}"'))

            # Run Alembic upgrade in the schema
            async with engine.begin() as conn:
                def run_upgrade(sync_conn):
                    sync_conn.execute(text(f'SET search_path TO "{schema}"'))
                    ctx = MigrationContext.configure(sync_conn)
                    op = Operations(ctx)
                    for migration in migrations:
                        migration.op = op
                        migration.upgrade()

                await conn.run_sync(run_upgrade)

            # Inspect catalog using synchronous reflection
            async with engine.connect() as conn:
                def inspect_schema(sync_conn):
                    sync_conn.execute(text(f'SET search_path TO "{schema}"'))
                    inspector = inspect(sync_conn)
                    tables = set(inspector.get_table_names(schema=schema))
                    assert tables == EXPECTED_CANONICAL_TABLES, f"Tables mismatch: {tables ^ EXPECTED_CANONICAL_TABLES}"
                    assert "case_clarifications" not in tables
                    assert "case_state_versions" not in tables

                    # 1. Compare columns against Base.metadata
                    for table_name in EXPECTED_CANONICAL_TABLES:
                        orm_table = Base.metadata.tables[table_name]
                        db_columns = {c["name"]: c for c in inspector.get_columns(table_name, schema=schema)}
                        assert set(db_columns) == set(orm_table.c.keys())
                        for orm_col_name, orm_col in orm_table.c.items():
                            assert orm_col_name in db_columns, f"Column {table_name}.{orm_col_name} missing from DB"
                            db_col = db_columns[orm_col_name]
                            assert db_col["nullable"] == orm_col.nullable, (
                                f"Column {table_name}.{orm_col_name} nullable mismatch: DB={db_col['nullable']}, ORM={orm_col.nullable}"
                            )

                    # 2. Check foreign key cascade rules
                    # case_analysis_results.run_id -> CASCADE
                    run_fks = inspector.get_foreign_keys("case_analysis_results", schema=schema)
                    run_fk = next((fk for fk in run_fks if fk["referred_table"] == "case_runs" and "run_id" in fk["constrained_columns"]), None)
                    assert run_fk is not None, "FK from case_analysis_results to case_runs missing"
                    assert run_fk.get("options", {}).get("ondelete") == "CASCADE"

                    # rag_contexts.case_run_id -> CASCADE
                    rag_fks = inspector.get_foreign_keys("rag_contexts", schema=schema)
                    rag_run_fk = next((fk for fk in rag_fks if fk["referred_table"] == "case_runs"), None)
                    assert rag_run_fk is not None, "FK from rag_contexts to case_runs missing"
                    assert rag_run_fk.get("options", {}).get("ondelete") == "CASCADE"

                    # case_runs.snapshot_id -> RESTRICT
                    cr_fks = inspector.get_foreign_keys("case_runs", schema=schema)
                    snapshot_fk = next((fk for fk in cr_fks if fk["referred_table"] == "case_evidence_snapshots"), None)
                    assert snapshot_fk is not None
                    assert snapshot_fk.get("options", {}).get("ondelete") == "RESTRICT"

                    request_fk = next(
                        (fk for fk in cr_fks if fk["referred_table"] == "chat_messages"),
                        None,
                    )
                    assert request_fk is not None
                    assert request_fk.get("options", {}).get("ondelete") in (None, "NO ACTION")
                    constraint_state = sync_conn.execute(
                        text(
                            """
                            SELECT condeferrable, condeferred, confdeltype
                            FROM pg_constraint
                            JOIN pg_namespace ON pg_namespace.oid = pg_constraint.connamespace
                            WHERE conname = :constraint_name AND nspname = :schema
                            """
                        ),
                        {"constraint_name": "fk_case_runs_request_message_id", "schema": schema},
                    ).mappings().one()
                    assert constraint_state["condeferrable"] is False
                    assert constraint_state["condeferred"] is False
                    assert constraint_state["confdeltype"] in ("a", b"a")

                    # 3. Check unique constraints
                    rag_uniques = inspector.get_unique_constraints("rag_contexts", schema=schema)
                    assert any("case_run_id" in u["column_names"] for u in rag_uniques), "uq_rag_contexts_case_run_id missing"

                    res_uniques = inspector.get_unique_constraints("case_analysis_results", schema=schema)
                    assert any("run_id" in u["column_names"] for u in res_uniques), "uq_case_analysis_results_run_id missing"

                    # 4. Check chat_messages.in_reply_to_message_id exists
                    msg_cols = {c["name"] for c in inspector.get_columns("chat_messages", schema=schema)}
                    assert "in_reply_to_message_id" in msg_cols

                await conn.run_sync(inspect_schema)

            # Test downgrade
            async with engine.begin() as conn:
                def run_downgrade(sync_conn):
                    sync_conn.execute(text(f'SET search_path TO "{schema}"'))
                    ctx = MigrationContext.configure(sync_conn)
                    op = Operations(ctx)
                    for migration in reversed(migrations):
                        migration.op = op
                        migration.downgrade()

                await conn.run_sync(run_downgrade)

            async with engine.connect() as conn:
                def inspect_downgrade(sync_conn):
                    sync_conn.execute(text(f'SET search_path TO "{schema}"'))
                    inspector = inspect(sync_conn)
                    assert len(inspector.get_table_names(schema=schema)) == 0

                await conn.run_sync(inspect_downgrade)

        finally:
            await engine.dispose()
            async with admin_engine.begin() as conn:
                await conn.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
            await admin_engine.dispose()

    asyncio.run(exercise())
