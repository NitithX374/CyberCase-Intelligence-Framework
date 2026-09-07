"""FastAPI application for chat APIs and document ingestion preview."""

import asyncio
from contextlib import asynccontextmanager, suppress
from sqlalchemy import text

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, async_session
from app.services.workflow.run_recovery import (
    monitor_interrupted_runs,
    recover_expired_runs,
)
from app.routers import chat, document_ingestion, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    recovery = None
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        await recover_expired_runs(async_session)
        recovery = asyncio.create_task(monitor_interrupted_runs(async_session))
        yield
    finally:
        if recovery is not None:
            recovery.cancel()
            with suppress(asyncio.CancelledError):
                await recovery
        await engine.dispose()


app = FastAPI(
    title="Cybercase Framework API",
    description="Persistent chat APIs and isolated document ingestion preview",
    version="1.0.0",
    lifespan=lifespan,
)

# ── Routers ──────────────────────────────────────────────────────────────────
app.include_router(health.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(document_ingestion.router, prefix="/api/v1")

# Wrap the full ASGI app so even unhandled 500 responses carry CORS headers.
app = CORSMiddleware(
    app,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
