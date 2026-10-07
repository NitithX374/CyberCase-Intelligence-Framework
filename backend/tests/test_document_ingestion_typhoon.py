import asyncio

import pytest

from app.sources.ingestion.contracts import RecognitionResponseError
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


def test_recognizer_retries_on_timeout_and_succeeds():
    import httpx

    attempts = 0

    class MockClient:
        is_closed = False

        async def post(self, *args, **kwargs):
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                raise httpx.ReadTimeout("timed out")
            request = httpx.Request("POST", "https://example.test")
            return httpx.Response(
                200,
                request=request,
                json={"choices": [{"finish_reason": "stop", "message": {"content": "page text"}}]},
            )

    recognizer = TyphoonDocumentRecognizer(
        TyphoonRecognizerConfig(
            api_key="test-key",
            base_url="https://example.test/v1",
            model="typhoon-ocr",
            timeout_seconds=10,
            target_image_dimension=1800,
            max_retries=3,
            retry_delay_seconds=0.001,
        ),
        client=MockClient(),
    )

    data = asyncio.run(recognizer.post([]))
    assert attempts == 2
    assert data["choices"][0]["message"]["content"] == "page text"


def test_recognizer_raises_after_max_retries_exhausted():
    import httpx
    from app.sources.ingestion.contracts import RecognitionTimeoutError

    attempts = 0

    class MockClient:
        is_closed = False

        async def post(self, *args, **kwargs):
            nonlocal attempts
            attempts += 1
            raise httpx.ReadTimeout("timed out")

    recognizer = TyphoonDocumentRecognizer(
        TyphoonRecognizerConfig(
            api_key="test-key",
            base_url="https://example.test/v1",
            model="typhoon-ocr",
            timeout_seconds=10,
            target_image_dimension=1800,
            max_retries=3,
            retry_delay_seconds=0.001,
        ),
        client=MockClient(),
    )

    with pytest.raises(RecognitionTimeoutError, match="timed out after 3 attempts"):
        asyncio.run(recognizer.post([]))

    assert attempts == 3
