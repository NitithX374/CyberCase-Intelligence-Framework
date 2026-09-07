import os
from contextlib import asynccontextmanager
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database import Base
from app.models import ChatThread
from app.schemas.chat import ChatMessageCreate
from app.services.chat.chat_run_creation import create_message_and_run


@asynccontextmanager
async def isolated_database():
    url = os.environ.get("CYBERCASE_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set CYBERCASE_TEST_DATABASE_URL to run PostgreSQL recovery tests")
    schema = f"refactor_test_{uuid4().hex}"
    administration = create_async_engine(url)
    engine = create_async_engine(
        url, connect_args={"server_settings": {"search_path": schema}}
    )
    try:
        async with administration.begin() as connection:
            await connection.execute(text(f'CREATE SCHEMA "{schema}"'))
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        yield async_sessionmaker(engine, expire_on_commit=False)
    finally:
        await engine.dispose()
        async with administration.begin() as connection:
            await connection.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
        await administration.dispose()


async def create_request(factory):
    async with factory() as db:
        thread = ChatThread(title="Recovery test")
        db.add(thread)
        await db.commit()
        thread_id = thread.id
    request = ChatMessageCreate(
        content="A witness reported a missing bicycle.", idempotency_key="saved-request"
    )
    async with factory() as db:
        message, run = await create_message_and_run(db, thread_id, request)
    return thread_id, message, run, request
