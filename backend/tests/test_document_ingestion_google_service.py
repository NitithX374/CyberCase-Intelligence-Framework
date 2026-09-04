import asyncio
from pathlib import Path
import subprocess
import sys
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app import main as main_module
from app.config import Settings
from app.routers import document_ingestion as router
from app.services.document_ingestion.contracts import IngestionMode, RegionType
from app.services.document_ingestion.errors import RecognitionProviderError
from app.services.document_ingestion.recognition.base import RenderedPage
from app.services.document_ingestion.recognition.google_vision import (
    GoogleVisionDocumentRecognizer,
)
from app.services.document_ingestion.recognition.typhoon import (
    TyphoonDocumentRecognizer,
)
from test_document_ingestion import _docx_bytes, _pdf_bytes, _png_bytes, _service
from test_document_ingestion_google_response import sample
from test_document_ingestion_routing import _pipeline, _region


def test_typhoon_router_loads_without_optional_google_packages(monkeypatch):
    monkeypatch.setenv("DOCUMENT_RECOGNIZER", "typhoon")
    script = """
import importlib.abc
import sys

class NoGooglePackages(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if fullname == "google" or fullname.startswith("google."):
            raise ModuleNotFoundError("Google packages intentionally unavailable")

sys.meta_path.insert(0, NoGooglePackages())
from app.routers.document_ingestion import _build_recognizer
from app.services.document_ingestion.recognition.typhoon import TyphoonDocumentRecognizer
assert isinstance(_build_recognizer(), TyphoonDocumentRecognizer)
"""
    backend_root = str(Path(__file__).resolve().parent.parent)
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=backend_root,
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("provider", ["typhoon", "google_vision"])
def test_provider_selection_from_environment_is_explicit_and_lazy(
    monkeypatch, provider
):
    monkeypatch.setenv("DOCUMENT_RECOGNIZER", provider)
    settings = Settings(_env_file=None)
    monkeypatch.setattr(router, "settings", settings)
    recognizer = router._build_recognizer()
    expected = (
        TyphoonDocumentRecognizer
        if provider == "typhoon"
        else GoogleVisionDocumentRecognizer
    )
    assert isinstance(recognizer, expected)


@pytest.mark.parametrize("kind", ["pdf", "image"])
def test_google_flows_through_service_without_llm_rag_or_persistence(monkeypatch, kind):
    calls = []

    async def forbidden(*args, **kwargs):
        calls.append(True)
        raise AssertionError("Ingestion crossed its boundary")

    for target in [
        "app.services.clients.rag_client.request_rag",
        "app.services.case_analysis.case_analysis_executor.request_case_analysis",
        "app.services.chat.chat_management.ChatService.create_thread",
    ]:
        monkeypatch.setattr(target, forbidden)
    recognizer = GoogleVisionDocumentRecognizer()
    post = MagicMock(return_value=sample()["provider_response"])
    monkeypatch.setattr(recognizer, "_post", post)
    content = _pdf_bytes([None]) if kind == "pdf" else _png_bytes()
    result = asyncio.run(_service(recognizer).ingest(content, f"synthetic.{kind}"))
    region = result.pages[0].regions[0]
    assert result.full_text == sample()["normalized"]["text"]
    assert region.recognition_confidence == 0.71
    assert region.segmentation_confidence is None
    assert len(region.words) == 4
    assert region.candidates[0].words == region.words
    assert result.pages[0].blocks[0].confidence == 0.71
    assert "confidence" not in region.model_dump()
    assert calls == []
    post.assert_called_once()
    assert post.call_args.args[0].startswith(b"\x89PNG")


@pytest.mark.parametrize("kind", ["pdf", "docx"])
def test_native_documents_bypass_google_and_have_no_ocr_measurements(monkeypatch, kind):
    text = (
        "Reliable native investigation narrative with details and numbers 123456. " * 6
    )
    content = _pdf_bytes([text]) if kind == "pdf" else _docx_bytes(text)
    recognizer = GoogleVisionDocumentRecognizer()
    post = MagicMock(side_effect=AssertionError("Native extraction called Google"))
    monkeypatch.setattr(recognizer, "_post", post)
    result = asyncio.run(_service(recognizer).ingest(content, f"native.{kind}"))
    assert result.extraction_method == f"native_{kind}"
    for region in result.pages[0].regions:
        assert region.verification_status == "native"
        assert region.recognition_confidence is None
        assert region.words == []
    post.assert_not_called()


@pytest.mark.parametrize("region_type", [RegionType.PRINTED_TEXT, RegionType.UNKNOWN])
def test_routed_ocr_keeps_segmentation_separate_and_preserves_words(
    monkeypatch, region_type
):
    recognizer = GoogleVisionDocumentRecognizer()
    monkeypatch.setattr(
        recognizer, "_post", lambda image: sample()["provider_response"]
    )
    segmented = _region("R1", region_type, (10, 10, 200, 80), page_number=1)
    page, _ = asyncio.run(
        _pipeline([segmented], ocr=recognizer).process(
            RenderedPage("DOC", 1, _png_bytes())
        )
    )
    region = page.regions[0]
    assert region.segmentation_confidence == 0.91
    assert region.recognition_confidence == 0.71
    assert region.candidates[0].confidence == 0.71
    assert page.blocks[0].confidence == 0.71
    assert region.words == region.candidates[0].words
    assert len(region.words) == 4


def test_typhoon_still_reports_no_recognition_confidence_in_both_modes(monkeypatch):
    monkeypatch.setattr(router.settings, "document_recognizer", "typhoon")
    recognizer = router._build_recognizer()
    monkeypatch.setattr(
        recognizer, "_request", AsyncMock(return_value=("Thai text", [], {}))
    )
    segmented = _region("R1", RegionType.PRINTED_TEXT, (0, 0, 100, 40), page_number=1)
    service = _service(recognizer)
    service._region_pipeline = _pipeline([segmented], ocr=recognizer)
    for mode in IngestionMode:
        result = asyncio.run(service.ingest(_png_bytes(), "synthetic.png", mode))
        region = result.pages[0].regions[0]
        assert region.recognition_confidence is None
        assert region.words == []
        assert region.candidates[0].confidence is None
        assert result.pages[0].blocks[0].confidence is None


@pytest.mark.parametrize("mode", ["unified", "routed"])
def test_google_preview_exposes_words_and_not_raw_provider_output(monkeypatch, mode):
    monkeypatch.setattr(router.settings, "document_recognizer", "google_vision")
    monkeypatch.setattr(
        GoogleVisionDocumentRecognizer,
        "_post",
        lambda self, image: sample()["provider_response"],
    )
    response = TestClient(main_module.app).post(
        f"/api/v1/document-ingestion/preview?mode={mode}",
        files={"file": ("synthetic.png", _png_bytes(), "image/png")},
    )
    assert response.status_code == 200
    payload = response.json()
    region = payload["pages"][0]["regions"][0]
    assert region["words"] == sample()["normalized"]["words"]
    assert region["recognition_confidence"] == 0.71
    assert "raw_provider_output" not in response.text
    assert payload["pages"][0]["routing_summary"]["htr"] == 0


def test_google_service_failure_retains_warning_and_no_false_measurement(monkeypatch):
    recognizer = GoogleVisionDocumentRecognizer()
    monkeypatch.setattr(
        recognizer,
        "_post",
        MagicMock(side_effect=RecognitionProviderError("unavailable")),
    )
    result = asyncio.run(_service(recognizer).ingest(_png_bytes(), "synthetic.png"))
    assert result.full_text == ""
    assert result.pages[0].regions == []
    assert "document_recognition_provider_error" in result.warnings[0]
