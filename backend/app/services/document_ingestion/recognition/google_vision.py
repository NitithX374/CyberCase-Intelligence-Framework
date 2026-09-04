import asyncio
import base64
from functools import partial

import google.auth
import requests
from google.auth.exceptions import DefaultCredentialsError, GoogleAuthError
from google.auth.transport.requests import AuthorizedSession, Request

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
from app.services.document_ingestion.recognition.google_vision_response import (
    minimum_word_confidence,
    normalize_response,
)

VISION_ENDPOINT = "https://vision.googleapis.com/v1/images:annotate"
VISION_SCOPES = ["https://www.googleapis.com/auth/cloud-vision"]


class GoogleVisionDocumentRecognizer:
    def __init__(self, timeout_seconds: float = 60.0) -> None:
        self._timeout_seconds = timeout_seconds

    async def recognize_page(self, page: RenderedPage) -> RecognizedPage:
        payload = await self._request(page.image_bytes)
        text, words = normalize_response(payload)
        return RecognizedPage(
            text=text,
            recognizer="google_vision",
            confidence=minimum_word_confidence(words),
            words=words,
            raw_provider_output=payload,
        )

    async def recognize(self, region: RenderedRegion) -> RecognitionResult:
        payload = await self._request(region.image_bytes)
        text, words = normalize_response(payload)
        return RecognitionResult(
            text=text,
            recognition_method=RecognitionMethod.OCR,
            recognizer="google_vision",
            verification_status=VerificationStatus.MACHINE_READ,
            confidence=minimum_word_confidence(words),
            words=words,
            raw_provider_output=payload,
        )

    async def _request(self, image_bytes: bytes) -> object:
        try:
            return await asyncio.wait_for(
                asyncio.to_thread(self._post, image_bytes),
                timeout=self._timeout_seconds,
            )
        except DefaultCredentialsError as error:
            raise RecognitionConfigurationError(
                "Google Vision requires Application Default Credentials."
            ) from error
        except (TimeoutError, requests.exceptions.Timeout) as error:
            raise RecognitionTimeoutError("Google Vision timed out.") from error
        except requests.exceptions.JSONDecodeError as error:
            raise RecognitionResponseError(
                "Google Vision returned invalid JSON."
            ) from error
        except (GoogleAuthError, requests.exceptions.RequestException) as error:
            raise RecognitionProviderError(
                "Google Vision authentication or transport failed."
            ) from error
        except ValueError as error:
            raise RecognitionResponseError(
                "Google Vision returned invalid JSON."
            ) from error

    def _post(self, image_bytes: bytes) -> object:
        with requests.Session() as auth_session:
            auth_request = partial(
                Request(session=auth_session), timeout=self._timeout_seconds
            )
            credentials, _ = google.auth.default(
                scopes=VISION_SCOPES, request=auth_request
            )
            with AuthorizedSession(
                credentials,
                auth_request=auth_request,
                refresh_timeout=self._timeout_seconds,
                max_refresh_attempts=0,
            ) as session:
                response = session.post(
                    VISION_ENDPOINT,
                    json={
                        "requests": [
                            {
                                "image": {
                                    "content": base64.b64encode(image_bytes).decode(
                                        "ascii"
                                    )
                                },
                                "features": [{"type": "DOCUMENT_TEXT_DETECTION"}],
                            }
                        ]
                    },
                    timeout=self._timeout_seconds,
                    max_allowed_time=self._timeout_seconds,
                )
                response.raise_for_status()
                return response.json()
