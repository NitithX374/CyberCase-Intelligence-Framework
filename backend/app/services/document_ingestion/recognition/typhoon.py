import asyncio
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

from app.services.document_ingestion.errors import (
    RecognitionConfigurationError,
    RecognitionProviderError,
    RecognitionResponseError,
    RecognitionTimeoutError,
)
from app.services.document_ingestion.recognition.base import (
    RecognizedPage,
    RenderedPage,
    separate_generated_visual_descriptions,
)


@dataclass(frozen=True)
class TyphoonRecognizerConfig:
    api_key: str
    base_url: str
    model: str
    timeout_seconds: float
    target_image_dimension: int


def prepare_messages(image_bytes: bytes, target_image_dimension: int):
    try:
        from typhoon_ocr import prepare_ocr_messages
    except ImportError as error:
        raise RecognitionConfigurationError(
            "The typhoon-ocr==0.4.1 package is not installed."
        ) from error

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as image_file:
        image_file.write(image_bytes)
        image_path = image_file.name
    try:
        return prepare_ocr_messages(
            pdf_or_image_path=image_path,
            task_type="v1.5",
            target_image_dim=target_image_dimension,
            page_num=1,
            figure_language="Thai",
        )
    finally:
        Path(image_path).unlink(missing_ok=True)


class TyphoonDocumentRecognizer:
    def __init__(
        self,
        config: TyphoonRecognizerConfig,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._config = config
        self._client = client
        self._owned_client = client is None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=self._config.timeout_seconds,
                limits=httpx.Limits(max_connections=4, max_keepalive_connections=4),
            )
            self._owned_client = True
        return self._client

    async def aclose(self) -> None:
        if self._client and not self._client.is_closed and self._owned_client:
            await self._client.aclose()

    async def recognize_page(self, page: RenderedPage) -> RecognizedPage:
        text, _provider_output = await self.request(page.image_bytes)
        return RecognizedPage(
            text=text,
            recognizer=self._config.model,
        )

    async def request(self, image_bytes: bytes) -> tuple[str, Any]:
        if not self._config.api_key:
            raise RecognitionConfigurationError(
                "TYPHOON_OCR_API_KEY is required for document recognition."
            )
        try:
            messages = await asyncio.to_thread(
                prepare_messages,
                image_bytes,
                self._config.target_image_dimension,
            )
        except RecognitionConfigurationError:
            raise
        except Exception as error:
            raise RecognitionProviderError(
                "Typhoon OCR could not prepare the document image."
            ) from error

        provider_output = await self.post(messages)
        try:
            raw_text = provider_output["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError, ValueError, AttributeError) as error:
            raise RecognitionResponseError(
                "Typhoon OCR returned an invalid response."
            ) from error
        if not raw_text:
            raise RecognitionResponseError("Typhoon OCR returned no document text.")
        transcription, _ = separate_generated_visual_descriptions(raw_text)
        return transcription, provider_output

    async def post(self, messages: list[dict[str, Any]]) -> Any:
        payload = {
            "model": self._config.model,
            "messages": messages,
            "max_tokens": 16_384,
            "repetition_penalty": 1.1,
            "temperature": 0.1,
            "top_p": 0.6,
        }
        endpoint = f"{self._config.base_url.rstrip('/')}/chat/completions"
        headers = {"Authorization": f"Bearer {self._config.api_key}"}
        client = self._get_client()
        try:
            response = await client.post(endpoint, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException as error:
            raise RecognitionTimeoutError("Typhoon OCR timed out.") from error
        except httpx.HTTPStatusError as error:
            raise RecognitionProviderError(
                f"Typhoon OCR returned HTTP {error.response.status_code}."
            ) from error
        except (httpx.RequestError, ValueError) as error:
            raise RecognitionProviderError(
                "Typhoon OCR could not be reached."
            ) from error


__all__ = [
    "TyphoonDocumentRecognizer",
    "TyphoonRecognizerConfig",
    "prepare_messages",
]
