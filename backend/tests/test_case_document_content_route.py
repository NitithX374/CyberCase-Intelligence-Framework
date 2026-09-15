import asyncio
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.routers import caseMaterials
from app.services.case_materials import CaseMaterialsError


def test_document_content_response_preserves_original_bytes(monkeypatch) -> None:
    case_id = uuid4()
    document_id = uuid4()
    user_id = uuid4()

    async def get_document(db, **kwargs):
        assert kwargs == {
            "case_id": case_id,
            "document_id": document_id,
            "user_id": user_id,
        }
        return SimpleNamespace(
            content_bytes=b"original-pdf",
            mime_type="application/pdf",
            filename="case file.pdf",
        )

    monkeypatch.setattr(caseMaterials, "get_owned_document_content", get_document)
    response = asyncio.run(
        caseMaterials.get_case_document_content(
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
    async def reject_document(db, **kwargs):
        raise CaseMaterialsError("document_not_found", "Document not found", 404)

    monkeypatch.setattr(caseMaterials, "get_owned_document_content", reject_document)

    with pytest.raises(HTTPException) as error:
        asyncio.run(
            caseMaterials.get_case_document_content(
                uuid4(),
                uuid4(),
                db=object(),
                user=SimpleNamespace(id=uuid4()),
            )
        )

    assert error.value.status_code == 404
