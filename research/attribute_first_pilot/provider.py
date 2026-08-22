"""LLM Provider wrapper for the Attribute-First Reasoning Pilot.

Connects to OpenRouter (defaulting to meta-llama/llama-3.1-8b-instruct)
with strict temperature=0.0, latency tracking, token usage tracking, and
strict JSON parsing for attribute contracts without silent fallback.
"""

from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import Any

import httpx

from .contracts import (
    AttributeContract,
    AttributePredictionResult,
    GenerationResult,
    ModelCallUsage,
)

DEFAULT_MODEL = "meta-llama/llama-3.1-8b-instruct"
DEFAULT_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def get_api_key() -> str:
    """Retrieve the OpenRouter API key from environment variables or .env."""
    key = os.getenv("OPENROUTER_CYBERCASE") or os.getenv("OPENROUTER_API_KEY")
    if key and key.strip():
        return key.strip()

    # Try loading from .env in workspace root
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'\"")
                if k in ("OPENROUTER_CYBERCASE", "OPENROUTER_API_KEY") and v:
                    return v

    return ""


def clean_json_text(text: str) -> str:
    """Strip markdown code fences and whitespace from model JSON output."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    return cleaned


class AttributePredictionError(Exception):
    """Raised when the model output fails strict attribute JSON validation."""
    def __init__(self, message: str, raw_text: str):
        super().__init__(f"{message}\nRaw text:\n{raw_text}")
        self.raw_text = raw_text


class PilotLlmProvider:
    """OpenRouter provider for the pilot experiment."""

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        api_key: str | None = None,
        base_url: str = DEFAULT_OPENROUTER_BASE_URL,
        timeout: float = 60.0,
        temperature: float = 0.0,
        dry_run: bool = False,
    ):
        self.model = model
        self.api_key = api_key or get_api_key()
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.temperature = temperature
        self.dry_run = dry_run

        if not self.dry_run and not self.api_key:
            raise ValueError(
                "OpenRouter API key is missing. Set OPENROUTER_CYBERCASE or OPENROUTER_API_KEY in environment or .env."
            )

    async def _call_chat_completions(
        self,
        messages: list[dict[str, str]],
        max_tokens: int = 1024,
        response_format: dict[str, str] | None = None,
    ) -> tuple[str, float, ModelCallUsage]:
        """Execute chat completion and track latency + usage."""
        if self.dry_run:
            # Deterministic mock response for dry-run testing
            is_json = response_format and response_format.get("type") == "json_object"
            if is_json or "JSON" in messages[0].get("content", ""):
                mock_text = json.dumps({
                    "answerability": "SUFFICIENT",
                    "question_type": "IMPACT",
                    "relevant_evidence_ids": ["S1"],
                    "epistemic_state": "SUPPORTED",
                    "missing_information": []
                })
            else:
                mock_text = "[DRY RUN] Based on the context, the analytical question is supported by evidence S1."
            return mock_text, 5.0, ModelCallUsage(prompt_tokens=50, completion_tokens=20, total_tokens=70)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/CyberCase-Intelligence-Framework",
            "X-Title": "CyberCase Attribute First Pilot",
        }

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": max_tokens,
            "seed": 42,
        }
        if response_format:
            payload["response_format"] = response_format

        t0 = time.perf_counter()
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        if resp.status_code != 200:
            raise RuntimeError(
                f"OpenRouter API error {resp.status_code}: {resp.text}"
            )

        data = resp.json()
        choice = data.get("choices", [{}])[0]
        content = choice.get("message", {}).get("content", "")
        usage_data = data.get("usage", {})
        usage = ModelCallUsage(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0),
        )

        return content, elapsed_ms, usage

    async def generate_answer(
        self,
        messages: list[dict[str, str]],
        max_tokens: int = 1024,
    ) -> GenerationResult:
        """Generate text answer for direct or attribute-first condition."""
        try:
            content, latency_ms, usage = await self._call_chat_completions(
                messages, max_tokens=max_tokens
            )
            return GenerationResult(
                answer=content.strip(),
                latency_ms=latency_ms,
                usage=usage,
                model=self.model,
                raw_response=content,
            )
        except Exception as e:
            return GenerationResult(
                answer="",
                latency_ms=0.0,
                usage=ModelCallUsage(),
                model=self.model,
                error=str(e),
            )

    async def predict_attributes(
        self,
        messages: list[dict[str, str]],
        max_tokens: int = 512,
    ) -> AttributePredictionResult:
        """Predict structured attributes with strict validation."""
        try:
            content, latency_ms, usage = await self._call_chat_completions(
                messages,
                max_tokens=max_tokens,
                response_format={"type": "json_object"},
            )
            cleaned = clean_json_text(content)
            try:
                parsed = json.loads(cleaned)
            except json.JSONDecodeError as jde:
                raise AttributePredictionError(f"Malformed JSON: {jde}", content) from jde

            attributes = AttributeContract.model_validate(parsed)
            return AttributePredictionResult(
                attributes=attributes,
                latency_ms=latency_ms,
                usage=usage,
                model=self.model,
                raw_response=content,
            )
        except Exception as e:
            return AttributePredictionResult(
                attributes=None,
                latency_ms=0.0,
                usage=ModelCallUsage(),
                model=self.model,
                error=str(e),
                raw_response=getattr(e, "raw_text", str(e)),
            )
