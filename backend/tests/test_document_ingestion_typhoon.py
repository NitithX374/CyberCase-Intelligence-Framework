import asyncio
import subprocess
import sys
from pathlib import Path

import pytest

from app.services.document_ingestion.contracts import RecognitionResponseError
from app.services.document_ingestion.recognition import (
    TyphoonDocumentRecognizer,
    TyphoonRecognizerConfig,
)
from app.services.document_ingestion.service import build_document_recognizer


def test_typhoon_recognizer_loads_without_optional_google_packages():
    script = """
import importlib.abc
import sys

class NoGooglePackages(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if fullname == "google" or fullname.startswith("google."):
            raise ModuleNotFoundError("Google packages intentionally unavailable")

sys.meta_path.insert(0, NoGooglePackages())
from app.services.document_ingestion.service import build_document_recognizer
from app.services.document_ingestion.recognition import TyphoonDocumentRecognizer
assert isinstance(build_document_recognizer(), TyphoonDocumentRecognizer)
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


def test_recognizer_is_typhoon():
    recognizer = build_document_recognizer()
    assert isinstance(recognizer, TyphoonDocumentRecognizer)


def test_recognizer_rejects_length_terminated_output(monkeypatch):
    recognizer = TyphoonDocumentRecognizer(
        TyphoonRecognizerConfig(
            api_key="test-key",
            base_url="https://example.test/v1",
            model="typhoon-ocr",
            timeout_seconds=10,
            target_image_dimension=1800,
        )
    )
    monkeypatch.setattr(
        "app.services.document_ingestion.recognition.prepare_messages",
        lambda image_bytes, target_image_dimension: [],
    )

    async def truncated_post(messages):
        return {
            "choices": [
                {
                    "finish_reason": "length",
                    "message": {"content": "partial document text"},
                }
            ]
        }

    monkeypatch.setattr(recognizer, "post", truncated_post)

    with pytest.raises(
        RecognitionResponseError,
        match="finish_reason='length'",
    ):
        asyncio.run(recognizer.request(b"image-bytes"))
