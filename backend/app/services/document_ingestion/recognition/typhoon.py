import asyncio
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

from app.services.document_ingestion.contracts import (
    RecognitionMethod,
    VerificationStatus,
)
from app.services.document_ingestion.errors import (
    RecognitionConfigurationError,
    RecognitionProviderError,
    RecognitionResponseError,
    RecognitionTimeoutError,
)
from app.services.document_ingestion.recognition.base import (
    RecognizedPage,
    RecognitionResult,
    RenderedPage,
    RenderedRegion,
)
from app.services.document_ingestion.recognition.content_filter import (
    separate_generated_visual_descriptions,
)


@dataclass(frozen=True)
class TyphoonRecognizerConfig:
    api_key: str
    base_url: str
    model: str
    timeout_seconds: float
    target_image_dimension: int


def _prepare_messages(image_bytes: bytes, target_image_dimension: int):
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
    def __init__(self, config: TyphoonRecognizerConfig) -> None:
        self._config = config

    async def recognize_page(self, page: RenderedPage) -> RecognizedPage:
        text, descriptions, provider_output = await self._request(page.image_bytes)
        return RecognizedPage(
            text=text,
            recognizer=self._config.model,
            layout_markdown=text,
            generated_visual_descriptions=descriptions,
            raw_provider_output=provider_output,
        )

    async def recognize(self, region: RenderedRegion) -> RecognitionResult:
        text, descriptions, provider_output = await self._request(region.image_bytes)
        return RecognitionResult(
            text=text,
            recognition_method=RecognitionMethod.OCR,
            recognizer=self._config.model,
            verification_status=VerificationStatus.MACHINE_READ,
            generated_visual_descriptions=descriptions,
            raw_provider_output=provider_output,
        )

    async def _request(self, image_bytes: bytes) -> tuple[str, list[str], Any]:
        if not self._config.api_key:
            raise RecognitionConfigurationError(
                "TYPHOON_OCR_API_KEY is required for document recognition."
            )
        try:
            messages = await asyncio.to_thread(
                _prepare_messages,
                image_bytes,
                self._config.target_image_dimension,
            )
        except RecognitionConfigurationError:
            raise
        except Exception as error:
            raise RecognitionProviderError(
                "Typhoon OCR could not prepare the document image."
            ) from error

        provider_output = await self._post(messages)
        try:
            raw_text = provider_output["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError, ValueError, AttributeError) as error:
            raise RecognitionResponseError(
                "Typhoon OCR returned an invalid response."
            ) from error
        if not raw_text:
            raise RecognitionResponseError("Typhoon OCR returned no document text.")
        text, descriptions = separate_generated_visual_descriptions(raw_text)
        return text, descriptions, provider_output

    async def _post(self, messages: list[dict[str, Any]]) -> Any:
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
        try:
            async with httpx.AsyncClient(
                timeout=self._config.timeout_seconds
            ) as client:
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
