from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar

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


__all__ = ["Listener", "announce", "listening"]
