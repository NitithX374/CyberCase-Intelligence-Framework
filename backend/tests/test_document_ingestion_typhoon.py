import asyncio

import pytest

from app.services.document_ingestion.contracts import RecognitionResponseError
from app.services.document_ingestion.recognition import (
    TyphoonDocumentRecognizer,
    TyphoonRecognizerConfig,
)
from app.services.document_ingestion.service import build_document_recognizer

NUL_LINE = "OCR line" + chr(0) + "one"


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


def test_recognized_text_never_carries_a_nul_the_database_would_refuse(monkeypatch):
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

    async def answered(messages):
        return {"choices": [{"finish_reason": "stop", "message": {"content": NUL_LINE}}]}

    monkeypatch.setattr(recognizer, "post", answered)

    assert asyncio.run(recognizer.request(b"image-bytes")) == "OCR lineone"
