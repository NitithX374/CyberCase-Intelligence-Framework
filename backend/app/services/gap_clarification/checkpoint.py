from __future__ import annotations

from contextlib import asynccontextmanager
import asyncio
from typing import AsyncIterator

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from sqlalchemy.engine import URL

from app.config import settings


_checkpoint_setup_lock = asyncio.Lock()
_checkpoint_setup_complete = False


def checkpoint_database_url() -> str:
    configured = settings.langgraph_checkpoint_database_url.strip()
    if configured:
        value = configured
    elif settings.database_url:
        value = settings.database_url
    else:
        value = URL.create(
            drivername="postgresql",
            username=settings.postgres_user,
            password=settings.postgres_password,
            host=settings.postgres_host,
            port=int(settings.postgres_port),
            database=settings.postgres_db,
        ).render_as_string(hide_password=False)
    if value.startswith("postgresql+asyncpg://"):
        return value.replace("postgresql+asyncpg://", "postgresql://", 1)
    if value.startswith("postgres+asyncpg://"):
        return value.replace("postgres+asyncpg://", "postgresql://", 1)
    return value


@asynccontextmanager
async def open_checkpointer() -> AsyncIterator[AsyncPostgresSaver]:
    global _checkpoint_setup_complete
    async with AsyncPostgresSaver.from_conn_string(checkpoint_database_url()) as saver:
        if not _checkpoint_setup_complete:
            async with _checkpoint_setup_lock:
                if not _checkpoint_setup_complete:
                    await saver.setup()
                    _checkpoint_setup_complete = True
        yield saver


def graph_config(session_id: str) -> dict[str, dict[str, str]]:
    return {"configurable": {"thread_id": session_id}}


__all__ = ["checkpoint_database_url", "graph_config", "open_checkpointer"]
