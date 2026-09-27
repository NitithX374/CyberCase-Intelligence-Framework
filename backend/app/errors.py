from __future__ import annotations

from fastapi import status


class AppError(Exception):
    status_code: int = status.HTTP_409_CONFLICT

    def __init__(self, code: str, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        if status_code is not None:
            self.status_code = status_code


__all__ = ["AppError"]
