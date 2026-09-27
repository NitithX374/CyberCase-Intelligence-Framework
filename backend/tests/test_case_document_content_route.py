import asyncio
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.errors import AppError
from app.sources import routes
from app.sources.service import SourceError, SourceService


def test_document_content_response_preserves_original_bytes(monkeypatch) -> None:
    case_id = uuid4()
    document_id = uuid4()
    user_id = uuid4()

    async def get_document(self, *args):
        assert args == (case_id, document_id, user_id)
        return SimpleNamespace(
            content_bytes=b"original-pdf",
            mime_type="application/pdf",
            filename="case file.pdf",
        )

    monkeypatch.setattr(SourceService, "document_content", get_document)
    response = asyncio.run(
        routes.get_case_document_content(
            case_id,
            document_id,
            db=object(),
            user=SimpleNamespace(id=user_id),
        )
    )

    assert response.body == b"original-pdf"
    assert response.media_type == "application/pdf"
    assert response.headers["content-disposition"] == "inline; filename*=UTF-8''case%20file.pdf"
    assert response.headers["x-content-type-options"] == "nosniff"


def test_document_content_route_hides_unowned_documents(monkeypatch) -> None:
    async def reject_document(self, *args):
        raise SourceError("document_not_found", "Document not found", 404)

    monkeypatch.setattr(SourceService, "document_content", reject_document)

    with pytest.raises(AppError) as error:
        asyncio.run(
            routes.get_case_document_content(
                uuid4(),
                uuid4(),
                db=object(),
                user=SimpleNamespace(id=uuid4()),
            )
        )

    assert error.value.status_code == 404
    assert error.value.code == "document_not_found"
