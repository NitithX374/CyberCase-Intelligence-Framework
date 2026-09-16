"""FastAPI application for the Case-owned API."""

import logging
import os
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import settings
from app.database import async_session, engine
from app.routers import (
    auth,
    case_analysis,
    case_followups,
    case_materials,
    case_reports,
    cases,
    health,
)
from app.services.auth.dependencies import get_current_user
from app.services.auth.request_guard import guard_browser_request
from app.services.workflow.case_run_service import cleanup_abandoned_case_runs


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        validate_single_process_runtime()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        await cleanup_abandoned_case_runs(async_session)
        yield
    finally:
        await engine.dispose()


def validate_single_process_runtime() -> None:
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
    description="Case-owned analysis, chat, evidence, and report APIs",
    version="1.0.0",
    lifespan=lifespan,
)

# ── Routers ──────────────────────────────────────────────────────────────────
app.middleware("http")(guard_browser_request)
app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(cases.router, prefix="/api/v1")
app.include_router(case_materials.router, prefix="/api/v1", dependencies=[Depends(get_current_user)])
app.include_router(case_analysis.router, prefix="/api/v1", dependencies=[Depends(get_current_user)])
app.include_router(case_followups.router, prefix="/api/v1", dependencies=[Depends(get_current_user)])
app.include_router(case_reports.router, prefix="/api/v1", dependencies=[Depends(get_current_user)])

# Wrap the full ASGI app so even unhandled 500 responses carry CORS headers.
app = CORSMiddleware(
    app,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
