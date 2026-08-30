from __future__ import annotations

import os
from typing import Any

import httpx

from research.sevenllm_preflight.run_openrouter_b0 import (
    DEFAULT_BASE_URL,
    GENERATION_CONFIG,
    MODEL,
    RequestFailure,
    request_prediction,
)


class OpenRouterPilotClient:
    provider = "openrouter"
    model = MODEL
    generation_config = GENERATION_CONFIG

    def __init__(
        self,
        api_key_env: str = "OPENROUTER_API_KEY",
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 120.0,
        max_attempts: int = 5,
        backoff_base: float = 1.0,
    ) -> None:
        api_key = os.getenv(api_key_env, "").strip()
        if not api_key:
            raise RuntimeError(f"Missing OpenRouter key in {api_key_env}")
        if max_attempts < 1 or backoff_base < 0:
            raise ValueError("Invalid OpenRouter retry configuration")
        self.api_key_env = api_key_env
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_attempts = max_attempts
        self.backoff_base = backoff_base
        self._client: httpx.Client | None = None

    def __enter__(self) -> "OpenRouterPilotClient":
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {os.environ[self.api_key_env]}",
                "Content-Type": "application/json",
                "X-OpenRouter-Metadata": "enabled",
                "HTTP-Referer": "https://github.com/CyberCase-Intelligence-Framework",
                "X-Title": "CyberCase SEvenLLM Context Refinement",
            },
            timeout=self.timeout,
        )
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    def predict(self, prompt: str, sample_id: str, condition: str) -> dict[str, Any]:
        if self._client is None:
            raise RuntimeError("OpenRouterPilotClient must be used as a context manager")
        request_key = f"{sample_id}:{condition}"
        try:
            raw, returned_model, request_timestamp, metadata = request_prediction(
                self._client,
                prompt,
                request_key,
                self.max_attempts,
                self.backoff_base,
            )
        except RequestFailure as exc:
            attempts = exc.metadata.get("attempts", [])
            raise RuntimeError(
                f"OpenRouter prediction failed for sample={sample_id} condition={condition}: {exc}; attempts={attempts}"
            ) from exc
        return {
            "sample_id": sample_id,
            "condition": condition,
            "provider": self.provider,
            "requested_model": self.model,
            "returned_model": returned_model,
            "generation_config": self.generation_config,
            "api_config": {
                "base_url": self.base_url,
                "api_key_env": self.api_key_env,
            },
            "request_timestamp": request_timestamp,
            "request_metadata": metadata,
            "prediction_raw": raw,
            "prediction_normalized": raw.strip(),
            "error": None,
        }
