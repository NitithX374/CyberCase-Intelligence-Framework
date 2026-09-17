from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from collections.abc import Mapping
from typing import Callable
from uuid import UUID

from app.database import async_session


class GapClarificationError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 409) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


_session_factory: ContextVar[Callable] = ContextVar(
    "gap_clarification_session_factory",
    default=async_session,
)


@contextmanager
def bind_session_factory(factory: Callable):
    token = _session_factory.set(factory)
    try:
        yield
    finally:
        _session_factory.reset(token)


def current_session_factory() -> Callable:
    return _session_factory.get()


def parse_uuid(value: str, field_name: str) -> UUID:
    try:
        return UUID(str(value))
    except (TypeError, ValueError) as error:
        raise GapClarificationError(
            "clarification_context_invalid",
            f"Invalid {field_name}",
        ) from error


def session_id_from_config(config: Mapping[str, object]) -> str:
    configurable = config.get("configurable")
    session_id = configurable.get("thread_id") if isinstance(configurable, Mapping) else None
    if not isinstance(session_id, str) or not session_id.strip():
        raise GapClarificationError(
            "clarification_session_missing",
            "Clarification session is missing from workflow configuration",
        )
    return session_id.strip()


__all__ = [
    "GapClarificationError",
    "bind_session_factory",
    "current_session_factory",
    "parse_uuid",
    "session_id_from_config",
]
