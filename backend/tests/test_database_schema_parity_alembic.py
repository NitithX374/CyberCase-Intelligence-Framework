import os
import subprocess
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

import pytest
from isolated_database import isolated_database
from sqlalchemy import inspect, text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine

import app.models  # noqa: F401
from app.database import Base

BACKEND = Path(__file__).parents[1]

pytestmark = pytest.mark.asyncio


@asynccontextmanager
async def scratch_database():
    url = os.environ.get("CYBERCASE_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set CYBERCASE_TEST_DATABASE_URL to run PostgreSQL tests")
    name = f"migration_{uuid4().hex}"
    administration = create_async_engine(url, isolation_level="AUTOCOMMIT")
    async with administration.connect() as connection:
        await connection.execute(text(f'CREATE DATABASE "{name}"'))
    engine = create_async_engine(make_url(url).set(database=name))
    try:
        yield engine
    finally:
        await engine.dispose()
        async with administration.connect() as connection:
            await connection.execute(text(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)'))
        await administration.dispose()


def alembic(engine, *arguments):
    completed = subprocess.run(
        [sys.executable, "-m", "alembic", *arguments],
        cwd=BACKEND,
        env={**os.environ, "DATABASE_URL": engine.url.render_as_string(hide_password=False)},
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr


def by_name(items):
    return {item["name"]: item for item in items}


def described(connection):
    inspector = inspect(connection)
    return {
        table: {
            "columns": {
                column["name"]: {**column, "type": repr(column["type"])}
                for column in inspector.get_columns(table)
            },
            "primary_key": inspector.get_pk_constraint(table),
            "foreign_keys": by_name(inspector.get_foreign_keys(table)),
            "unique_constraints": by_name(inspector.get_unique_constraints(table)),
            "check_constraints": by_name(inspector.get_check_constraints(table)),
            "indexes": by_name(inspector.get_indexes(table)),
        }
        for table in inspector.get_table_names()
        if table != "alembic_version"
    }


async def test_upgrade_head_builds_exactly_the_schema_the_models_declare():
    async with scratch_database() as migrated, isolated_database() as declared:
        alembic(migrated, "upgrade", "head")
        async with migrated.connect() as connection:
            built = await connection.run_sync(described)
        async with declared.kw["bind"].connect() as connection:
            expected = await connection.run_sync(described)

    assert set(expected) == set(Base.metadata.tables)
    assert set(built) == set(expected)
    for table, sections in expected.items():
        for section, declared_shape in sections.items():
            assert built[table][section] == declared_shape, f"{table}.{section}"


async def test_downgrade_base_removes_everything_upgrade_head_built():
    async with scratch_database() as migrated:
        alembic(migrated, "upgrade", "head")
        alembic(migrated, "downgrade", "base")
        async with migrated.connect() as connection:
            tables = await connection.run_sync(lambda sync: inspect(sync).get_table_names())
            versions = await connection.scalar(text("SELECT count(*) FROM alembic_version"))

    assert tables == ["alembic_version"]
    assert versions == 0
