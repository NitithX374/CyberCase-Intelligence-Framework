from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.schemas.reports import StructuredReport


class ReportServiceError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class ReportGenerationConflict(ReportServiceError):
    pass


class ReportNotFound(ReportServiceError):
    pass


class ReportValidationError(ValueError):
    pass


@dataclass(frozen=True)
class ReportRunResult:
    status: Literal["completed", "failed"]
    report: StructuredReport | None
    prompt_version: str
    provider: str
    model: str
    validation_errors: tuple[str, ...] = ()
    failure_code: str | None = None
    failure_message: str | None = None
    latency_ms: float | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None


__all__ = [
    "ReportGenerationConflict",
    "ReportNotFound",
    "ReportRunResult",
    "ReportServiceError",
    "ReportValidationError",
]
