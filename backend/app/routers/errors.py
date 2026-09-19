"""Service errors, said in HTTP."""

from __future__ import annotations

from fastapi import HTTPException, status

from app.services.document_ingestion import DocumentIngestionError
from app.services.sources import SourceError


def source_http_error(error: SourceError) -> HTTPException:
    return HTTPException(
        status_code=error.status_code,
        detail={"code": error.code, "message": error.message},
    )


def ingestion_http_error(error: DocumentIngestionError) -> HTTPException:
    status_code = (
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        if error.code == "unsupported_document_type"
        else status.HTTP_413_CONTENT_TOO_LARGE
        if error.code.endswith("limit_exceeded")
        else status.HTTP_422_UNPROCESSABLE_CONTENT
    )
    return HTTPException(
        status_code=status_code,
        detail={"code": error.code, "message": error.message},
    )


__all__ = ["ingestion_http_error", "source_http_error"]
