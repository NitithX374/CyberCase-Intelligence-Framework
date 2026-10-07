from __future__ import annotations

import asyncio
import json
import logging
import time
from collections.abc import AsyncIterator, Awaitable, Callable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.errors import AppError

logger = logging.getLogger(__name__)

Listener = Callable[[str], None]

_listener: ContextVar[Listener | None] = ContextVar("analysis_progress", default=None)


def announce(step: str) -> None:
    listener = _listener.get()
    if listener is not None:
        listener(step)


@contextmanager
def listening(listener: Listener) -> Iterator[None]:
    token = _listener.set(listener)
    try:
        yield
    finally:
        _listener.reset(token)


HEARTBEAT_SECONDS = 15.0
STREAMED_RESPONSE = {200: {"content": {"text/event-stream": {}}}}

_unfinished: set[asyncio.Task] = set()


def wants_progress(request: Request) -> bool:
    return "text/event-stream" in request.headers.get("accept", "")


def progress_response(work: Callable[[], Awaitable[BaseModel]]) -> StreamingResponse:
    return StreamingResponse(
        progress_events(work),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


async def progress_events(
    work: Callable[[], Awaitable[BaseModel]],
    heartbeat: float = HEARTBEAT_SECONDS,
) -> AsyncIterator[str]:
    events: asyncio.Queue[str | None] = asyncio.Queue()
    started = time.monotonic()

    def reached(step: str) -> None:
        elapsed = round(time.monotonic() - started, 1)
        events.put_nowait(sse("step", {"step": step, "elapsed": elapsed}))

    async def run() -> BaseModel:
        with listening(reached):
            return await work()

    task = asyncio.create_task(run())
    _unfinished.add(task)
    task.add_done_callback(settled)
    task.add_done_callback(lambda _: events.put_nowait(None))
    while True:
        try:
            item = await asyncio.wait_for(events.get(), heartbeat)
        except TimeoutError:
            yield ": heartbeat\n\n"
            continue
        if item is None:
            break
        yield item
    yield outcome(task)


def settled(task: asyncio.Task) -> None:
    _unfinished.discard(task)
    if task.cancelled():
        return
    error = task.exception()
    if isinstance(error, AppError):
        logger.warning(
            "A streamed request failed: %s (HTTP %d) %s",
            error.code,
            error.status_code,
            error.message,
        )
    elif error is not None:
        logger.error("A streamed request failed", exc_info=error)


def outcome(task: asyncio.Task) -> str:
    try:
        result = task.result()
    except AppError as error:
        return failure(error.status_code, error.code, error.message)
    except Exception:
        return failure(500, "internal_error", "The request failed")
    return sse("result", jsonable_encoder(result))


def failure(status_code: int, code: str, message: str) -> str:
    return sse("error", {"status": status_code, "detail": {"code": code, "message": message}})


def sse(name: str, data: object) -> str:
    return f"event: {name}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


__all__ = [
    "HEARTBEAT_SECONDS",
    "Listener",
    "STREAMED_RESPONSE",
    "announce",
    "listening",
    "progress_events",
    "progress_response",
    "wants_progress",
]
