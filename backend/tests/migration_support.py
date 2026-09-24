import importlib.util
import os
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

BASELINE = Path(__file__).parents[1] / "alembic" / "baseline_versions"


def load_migrations():
    modules = []
    for path in sorted(BASELINE.glob("[0-9]*.py")):
        spec = importlib.util.spec_from_file_location(f"migration_{path.stem}", path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        modules.append(module)
    return modules


def migrate(connection, schema, *steps):
    connection.execute(text(f'SET search_path TO "{schema}"'))
    op = Operations(MigrationContext.configure(connection))
    for module, direction in steps:
        module.op = op
        getattr(module, direction)()


@asynccontextmanager
async def schema_before(revision: str):
    url = os.environ.get("CYBERCASE_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set CYBERCASE_TEST_DATABASE_URL to run PostgreSQL tests")
    migrations = load_migrations()
    names = [module.revision for module in migrations]
    earlier = migrations[: names.index(revision)]
    target = migrations[names.index(revision)]
    schema = f"migration_{uuid4().hex[:8]}"
    admin = create_async_engine(url)
    engine = create_async_engine(url, connect_args={"server_settings": {"search_path": schema}})
    try:
        async with admin.begin() as connection:
            await connection.execute(text(f'CREATE SCHEMA "{schema}"'))
        async with engine.begin() as connection:
            await connection.run_sync(migrate, schema, *[(module, "upgrade") for module in earlier])
        yield engine, schema, target
    finally:
        await engine.dispose()
        async with admin.begin() as connection:
            await connection.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
        await admin.dispose()
