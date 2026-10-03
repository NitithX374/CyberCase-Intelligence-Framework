from __future__ import annotations

from collections import Counter
from collections.abc import Iterator
from contextlib import contextmanager
from uuid import UUID

from fastapi import status

from app.errors import AppError

_running: Counter[UUID] = Counter()


@contextmanager
def analysing(case_id: UUID) -> Iterator[None]:
    _running[case_id] += 1
    try:
        yield
    finally:
        _running[case_id] -= 1
        if _running[case_id] <= 0:
            del _running[case_id]


def analysis_running(case_id: UUID) -> bool:
    return _running[case_id] > 0


@contextmanager
def sole_analysis(case_id: UUID) -> Iterator[None]:
    if analysis_running(case_id):
        raise AppError(
            "analysis_in_progress",
            "The case is already being analysed",
            status.HTTP_409_CONFLICT,
        )
    with analysing(case_id):
        yield


__all__ = ["analysing", "analysis_running", "sole_analysis"]
