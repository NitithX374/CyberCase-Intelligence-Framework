from io import BytesIO

from docx import Document
from fastapi.testclient import TestClient
from PIL import Image

from app import main as main_module
from app.routers import document_ingestion as ingestion_router
from app.services.document_ingestion.contracts import SourceType
from app.services.document_ingestion.recognition import RecognizedPage


def _docx_bytes(text: str) -> bytes:
    output = BytesIO()
    document = Document()
    document.add_paragraph(text)
    document.save(output)
    return output.getvalue()


def _png_bytes() -> bytes:
    output = BytesIO()
    Image.new("RGB", (120, 80), "white").save(output, format="PNG")
    return output.getvalue()


class StaticPageRecognizer:
    async def recognize_page(self, page) -> RecognizedPage:
        return RecognizedPage(
            text="recognized text",
            recognizer="test-ocr",
            source_type=SourceType.PRINTED,
        )


def test_preview_endpoint_is_independent_and_returns_structured_document() -> None:
    client = TestClient(main_module.app)
    response = client.post(
        "/api/v1/document-ingestion/preview",
        files={
            "file": (
                "case.docx",
                _docx_bytes("case evidence only"),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["extraction_method"] == "native_docx"
    assert payload["mode"] == "unified"
    assert payload["pages"][0]["blocks"][0]["text"] == "case evidence only"


def test_preview_endpoint_supports_unified_mode_and_segmentation_alias() -> None:
    client = TestClient(main_module.app)
    files = {
        "file": (
            "case.docx",
            _docx_bytes("case evidence only"),
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    }

    unified = client.post(
        "/api/v1/document-ingestion/preview?mode=unified", files=files
    )
    alias = client.post(
        "/api/v1/document-ingestion/preview?segmentation=false", files=files
    )

    assert unified.json()["mode"] == "unified"
    assert alias.json()["mode"] == "unified"


def test_preview_endpoint_rejects_unsupported_content() -> None:
    client = TestClient(main_module.app)
    response = client.post(
        "/api/v1/document-ingestion/preview",
        files={"file": ("case.txt", b"plain text", "text/plain")},
    )

    assert response.status_code == 415
    assert response.json()["detail"]["code"] == "unsupported_document_type"


def test_default_image_preview_does_not_require_google_configuration(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        ingestion_router,
        "_build_recognizer",
        lambda: StaticPageRecognizer(),
    )
    client = TestClient(main_module.app)
    response = client.post(
        "/api/v1/document-ingestion/preview",
        files={"file": ("page.png", _png_bytes(), "image/png")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "unified"
    assert payload["full_text"] == "recognized text"
    assert not any("GOOGLE_DOCUMENT_AI" in warning for warning in payload["warnings"])
