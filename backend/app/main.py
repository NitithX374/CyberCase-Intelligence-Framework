import logging
import os
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import settings
from app.database import engine
from app.routers import (
    analysis,
    auth,
    cases,
    chat,
    documents,
    health,
    reports,
    sources,
)
from app.services.auth.dependencies import get_current_user, guard_browser_request


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        validate_single_process_runtime()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
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
                f"{variable}={workers} is unsupported: the analysis runs in the request that asked "
                "for it, so there must be exactly one application worker"
            )


app = FastAPI(
    title="Cybercase Framework API",
    description="Case-owned analysis, chat, sources, and report APIs",
    version="1.0.0",
    lifespan=lifespan,
)

app.middleware("http")(guard_browser_request)
app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(cases.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1", dependencies=[Depends(get_current_user)])
app.include_router(sources.router, prefix="/api/v1", dependencies=[Depends(get_current_user)])
app.include_router(analysis.router, prefix="/api/v1", dependencies=[Depends(get_current_user)])
app.include_router(reports.router, prefix="/api/v1", dependencies=[Depends(get_current_user)])

app = CORSMiddleware(
    app,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
