"""FastAPI application for case and chat APIs plus document ingestion preview."""

import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import settings
from app.database import async_session, engine
from app.routers import (
    auth,
    caseAnalysis,
    caseClarifications,
    caseMaterials,
    caseReports,
    cases,
    chat,
    documentIngestion,
    health,
    passwordAuth,
)
from app.services.auth.dependencies import get_current_user
from app.services.auth.requestGuard import guard_browser_request
from app.services.workflow.caseRunService import cleanupAbandonedCaseRuns


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        validateSingleProcessRuntime()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        await cleanupAbandonedCaseRuns(async_session)
        yield
    finally:
        await engine.dispose()


def validateSingleProcessRuntime() -> None:
    for variable in ("WEB_CONCURRENCY", "UVICORN_WORKERS", "GUNICORN_WORKERS"):
        value = os.getenv(variable)
        if value is None:
            continue
        try:
            workers = int(value)
        except ValueError as error:
            raise RuntimeError(f"{variable} must be a positive integer") from error
        if workers != 1:
            raise RuntimeError(
                f"{variable}={workers} is unsupported for CaseRun processing; use exactly one application worker"
            )


app = FastAPI(
    title="Cybercase Framework API",
    description="Case-owned chat APIs and isolated document ingestion preview",
    version="1.0.0",
    lifespan=lifespan,
)

# ── Routers ──────────────────────────────────────────────────────────────────
app.middleware("http")(guard_browser_request)
app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(passwordAuth.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(cases.router, prefix="/api/v1")
app.include_router(caseMaterials.router, prefix="/api/v1", dependencies=[Depends(get_current_user)])
app.include_router(caseAnalysis.router, prefix="/api/v1", dependencies=[Depends(get_current_user)])
app.include_router(caseClarifications.router, prefix="/api/v1", dependencies=[Depends(get_current_user)])
app.include_router(caseReports.router, prefix="/api/v1", dependencies=[Depends(get_current_user)])
app.include_router(documentIngestion.router, prefix="/api/v1", dependencies=[Depends(get_current_user)])

# Wrap the full ASGI app so even unhandled 500 responses carry CORS headers.
app = CORSMiddleware(
    app,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
