import asyncio

import httpx
import pytest

from app.sources.ingestion.contracts import (
    RecognitionProviderError,
    RecognitionResponseError,
    RecognitionTimeoutError,
)
from app.sources.ingestion.recognition import TyphoonDocumentRecognizer, TyphoonRecognizerConfig
from app.sources.ingestion.service import build_document_recognizer

NUL_LINE = "OCR line" + chr(0) + "one"
LONE_SURROGATE_LINE = "OCR line" + chr(0xD800) + "one"


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
        "app.sources.ingestion.recognition.prepare_messages",
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


@pytest.mark.parametrize("raw", [NUL_LINE, LONE_SURROGATE_LINE])
def test_recognized_text_never_carries_what_the_database_would_refuse(monkeypatch, raw):
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
        "app.sources.ingestion.recognition.prepare_messages",
        lambda image_bytes, target_image_dimension: [],
    )

    async def answered(messages):
        return {"choices": [{"finish_reason": "stop", "message": {"content": raw}}]}

    monkeypatch.setattr(recognizer, "post", answered)

    recognized = asyncio.run(recognizer.request(b"image-bytes"))

    assert recognized == "OCR lineone"
    assert recognized.encode("utf-8")


def retry_recognizer(client: httpx.AsyncClient) -> TyphoonDocumentRecognizer:
    return TyphoonDocumentRecognizer(
        TyphoonRecognizerConfig(
            api_key="test-key",
            base_url="https://ocr.test/v1",
            model="typhoon-ocr",
            timeout_seconds=10,
            target_image_dimension=1800,
            max_retries=3,
            retry_delay_seconds=2,
        ),
        client=client,
    )


@pytest.fixture
def delays(monkeypatch) -> list[float]:
    waited = []

    async def record_delay(seconds: float) -> None:
        waited.append(seconds)

    monkeypatch.setattr("app.sources.ingestion.recognition.asyncio.sleep", record_delay)
    return waited


@pytest.mark.parametrize("status", [408, 429, 500, 502, 503, 504])
async def test_transient_http_failure_retries_then_returns_original_response(status, delays):
    calls = []

    def respond(request):
        calls.append(request)
        return httpx.Response(status if len(calls) == 1 else 200, json={"text": "ต้นฉบับ"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        result = await retry_recognizer(client).post([])

    assert result == {"text": "ต้นฉบับ"}
    assert len(calls) == 2
    assert delays == [2]


@pytest.mark.parametrize("status", [429, 503])
async def test_transient_http_exhaustion_preserves_provider_error_and_cause(status, delays):
    calls = []

    def respond(request):
        calls.append(request)
        return httpx.Response(status)

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        with pytest.raises(RecognitionProviderError, match=f"returned HTTP {status}") as failure:
            await retry_recognizer(client).post([])

    assert isinstance(failure.value.__cause__, httpx.HTTPStatusError)
    assert len(calls) == 3
    assert delays == [2, 4]


@pytest.mark.parametrize("status", [400, 401, 403, 404])
async def test_terminal_http_failure_is_not_retried(status, delays):
    calls = []

    def respond(request):
        calls.append(request)
        return httpx.Response(status)

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        with pytest.raises(RecognitionProviderError, match=f"returned HTTP {status}"):
            await retry_recognizer(client).post([])

    assert len(calls) == 1
    assert delays == []


@pytest.mark.parametrize(
    ("make_error", "expected_type", "message"),
    [
        (lambda: httpx.ReadTimeout("slow"), RecognitionTimeoutError, "timed out after 3 attempts"),
        (lambda: httpx.ConnectError("offline"), RecognitionProviderError, "could not be reached"),
        (lambda: ValueError("invalid JSON"), RecognitionProviderError, "could not be reached"),
    ],
)
async def test_transport_and_decode_failures_are_bounded(
    make_error, expected_type, message, delays
):
    calls = []

    def respond(request):
        calls.append(request)
        raise make_error()

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        with pytest.raises(expected_type, match=message) as failure:
            await retry_recognizer(client).post([])

    assert isinstance(failure.value.__cause__, type(make_error()))
    assert len(calls) == 3
    assert delays == [2, 4]
