"""FastAPI application for chat APIs and document ingestion preview."""

import asyncio
from contextlib import asynccontextmanager, suppress

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import settings
from app.database import async_session, engine
from app.routers import auth, chat, document_ingestion, health, password_auth
from app.services.auth.dependencies import get_current_user
from app.services.auth.request_guard import guard_browser_request
from app.services.workflow.run_recovery import (
    monitor_interrupted_runs,
    recover_expired_runs,
)


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
app.middleware("http")(guard_browser_request)
app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(password_auth.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(document_ingestion.router, prefix="/api/v1", dependencies=[Depends(get_current_user)])

# Wrap the full ASGI app so even unhandled 500 responses carry CORS headers.
app = CORSMiddleware(
    app,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
