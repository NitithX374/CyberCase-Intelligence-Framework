import asyncio
import base64
import threading
import time
from unittest.mock import MagicMock

import pytest
import requests
from google.auth.exceptions import DefaultCredentialsError, RefreshError, TransportError

from app.services.document_ingestion.errors import (
    RecognitionConfigurationError,
    RecognitionProviderError,
    RecognitionResponseError,
    RecognitionTimeoutError,
)
from app.services.document_ingestion.recognition import google_vision
from app.services.document_ingestion.recognition.base import (
    RenderedPage,
    RenderedRegion,
)
from test_document_ingestion_google_response import sample


def test_official_request_uses_adc_document_detection_image_bytes_and_timeouts(
    monkeypatch,
):
    credentials = object()
    adc = MagicMock(return_value=(credentials, None))
    session = MagicMock()
    session.__enter__.return_value = session
    session.post.return_value.json.return_value = sample()["provider_response"]
    factory = MagicMock(return_value=session)
    monkeypatch.setattr(google_vision.google.auth, "default", adc)
    monkeypatch.setattr(google_vision, "AuthorizedSession", factory)
    recognizer = google_vision.GoogleVisionDocumentRecognizer(timeout_seconds=7)

    result = asyncio.run(recognizer.recognize_page(RenderedPage("DOC", 1, b"png")))

    assert result.text == sample()["normalized"]["text"]
    assert result.confidence == 0.71
    assert result.raw_provider_output == sample()["provider_response"]
    assert adc.call_args.kwargs["scopes"] == google_vision.VISION_SCOPES
    assert factory.call_args.args == (credentials,)
    assert factory.call_args.kwargs["max_refresh_attempts"] == 0
    args, kwargs = session.post.call_args
    assert args == ("https://vision.googleapis.com/v1/images:annotate",)
    assert kwargs["json"] == {
        "requests": [
            {
                "image": {"content": base64.b64encode(b"png").decode("ascii")},
                "features": [{"type": "DOCUMENT_TEXT_DETECTION"}],
            }
        ]
    }
    assert kwargs["timeout"] == kwargs["max_allowed_time"] == 7
    session.post.return_value.raise_for_status.assert_called_once()
    session.__exit__.assert_called_once()


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (DefaultCredentialsError("private path"), RecognitionConfigurationError),
        (requests.exceptions.Timeout("private"), RecognitionTimeoutError),
        (requests.exceptions.ConnectionError("private"), RecognitionProviderError),
        (requests.exceptions.HTTPError("private"), RecognitionProviderError),
        (TransportError("private"), RecognitionProviderError),
        (RefreshError("private token"), RecognitionProviderError),
        (ValueError("private payload"), RecognitionResponseError),
        (
            requests.exceptions.JSONDecodeError("private", "", 0),
            RecognitionResponseError,
        ),
    ],
)
def test_transport_and_auth_errors_are_mapped_without_leaking_details(
    monkeypatch, error, expected
):
    recognizer = google_vision.GoogleVisionDocumentRecognizer()
    monkeypatch.setattr(recognizer, "_post", MagicMock(side_effect=error))
    with pytest.raises(expected) as raised:
        asyncio.run(recognizer.recognize_page(RenderedPage("DOC", 1, b"png")))
    assert "private" not in str(raised.value)


def test_network_work_runs_off_event_loop(monkeypatch):
    recognizer = google_vision.GoogleVisionDocumentRecognizer()
    released = threading.Event()
    caller_thread = threading.get_ident()

    def post(image_bytes):
        assert threading.get_ident() != caller_thread
        assert released.wait(timeout=1)
        return sample()["provider_response"]

    monkeypatch.setattr(recognizer, "_post", post)

    async def run():
        task = asyncio.create_task(
            recognizer.recognize_page(RenderedPage("DOC", 1, b"png"))
        )
        await asyncio.sleep(0.01)
        released.set()
        return await task

    assert asyncio.run(run()).confidence == 0.71


def test_coroutine_timeout_is_mapped(monkeypatch):
    recognizer = google_vision.GoogleVisionDocumentRecognizer(timeout_seconds=0.005)

    def delayed_post(image_bytes):
        time.sleep(0.05)
        return sample()["provider_response"]

    monkeypatch.setattr(recognizer, "_post", delayed_post)
    with pytest.raises(RecognitionTimeoutError):
        asyncio.run(recognizer.recognize_page(RenderedPage("DOC", 1, b"png")))


def test_region_recognition_preserves_words_and_low_measurements_without_threshold(
    monkeypatch,
):
    recognizer = google_vision.GoogleVisionDocumentRecognizer()
    payload = sample()["provider_response"]
    monkeypatch.setattr(recognizer, "_post", lambda image_bytes: payload)
    result = asyncio.run(recognizer.recognize(RenderedRegion("DOC", 1, "R1", b"png")))
    assert result.recognition_method == "ocr"
    assert result.verification_status == "machine_read"
    assert result.confidence == 0.71
    assert [word.text for word in result.words] == ["นาย", "ก.", "52,000", "บาท"]
