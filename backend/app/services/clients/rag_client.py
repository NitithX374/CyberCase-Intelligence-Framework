from __future__ import annotations

import httpx
from pydantic import ValidationError

from app.config import settings
from app.schemas.rag import QueryRequest, QueryResponse

RAG_HTTP_TIMEOUT_SECONDS = 300.0


class RagCallFailure(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


async def request_rag(
    content: str,
    *,
    client: httpx.AsyncClient | None = None,
) -> QueryResponse:
    payload = QueryRequest(query=content, use_agent=True).model_dump()
    url = f"{settings.rag_service_url.rstrip('/')}/query"
    if client is not None:
        return await post_and_validate(client, url, payload)

    async with httpx.AsyncClient(timeout=RAG_HTTP_TIMEOUT_SECONDS) as owned_client:
        return await post_and_validate(owned_client, url, payload)


async def post_and_validate(
    client: httpx.AsyncClient,
    url: str,
    payload: dict[str, object],
) -> QueryResponse:
    try:
        response = await client.post(url, json=payload)
    except httpx.TimeoutException as exc:
        raise RagCallFailure(
            "rag_timeout",
            "RAG service request timed out",
        ) from exc
    except httpx.RequestError as exc:
        raise RagCallFailure(
            "rag_service_error",
            "RAG service request failed",
        ) from exc

    if not 200 <= response.status_code < 300:
        raise RagCallFailure(
            "rag_service_error",
            "RAG service request failed",
        )

    try:
        response_payload = response.json()
        return QueryResponse.model_validate(response_payload)
    except (ValueError, ValidationError, TypeError) as exc:
        raise RagCallFailure(
            "rag_invalid_response",
            "RAG service returned an invalid response",
        ) from exc


__all__ = [
    "RAG_HTTP_TIMEOUT_SECONDS",
    "RagCallFailure",
    "request_rag",
]
