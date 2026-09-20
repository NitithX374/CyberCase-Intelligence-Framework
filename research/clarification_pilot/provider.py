"""One way to call a model, and one place every call is recorded.

Each call appends a ``CallRecord`` carrying its role. That is what lets the
report say what the candidate cost without counting the simulator and the judge,
which are apparatus rather than system.

``dry_run`` answers from a scripted responder instead of the network, so the
whole harness -- loop, stop conditions, scoring, statistics -- is exercisable
offline and in tests without an API key.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, TypeVar

import httpx
from pydantic import BaseModel, ValidationError

from .contracts import CallRecord, CallRole

Parsed = TypeVar("Parsed", bound=BaseModel)

DEFAULT_MODEL = "openai/gpt-5.6-luna"
DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class ModelSpec:
    """A model and the settings a rerun has to match to mean anything."""

    model: str = DEFAULT_MODEL
    temperature: float = 0.0
    max_tokens: int = 1_024
    seed: int | None = 42


class ProviderError(RuntimeError):
    pass


KEY_NAMES = ("OPENROUTER_CYBERCASE", "OPENROUTER_API_KEY")


def dotenv_values() -> dict[str, str]:
    """The repository .env, parsed. Absent file is an empty mapping, not an error."""

    env_file = REPO_ROOT / ".env"
    if not env_file.exists():
        return {}
    values: dict[str, str] = {}
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, _, value = line.partition("=")
        values[name.strip()] = value.strip().strip("'\"")
    return values


def api_key_from_environment() -> str:
    """The OpenRouter key, preferring this project's name over a generic one.

    The name matters more than where it came from. A machine can carry an
    ambient ``OPENROUTER_API_KEY`` for something else entirely, and checking
    every environment variable before looking at ``.env`` lets that stale key
    shadow the project's own ``OPENROUTER_CYBERCASE`` -- which fails as a 401
    after the run has already started.
    """

    values = dotenv_values()
    for name in KEY_NAMES:
        for candidate in (os.getenv(name), values.get(name)):
            if candidate and candidate.strip():
                return candidate.strip()
    return ""


def strip_fences(text: str) -> str:
    """JSON as the model actually returns it, fences and preamble and all."""

    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    if cleaned.startswith("{") or cleaned.startswith("["):
        return cleaned
    # A model that wrote a sentence before the object: take the widest brace span.
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    return match.group(0) if match else cleaned


ScriptedResponder = Callable[[str, list[dict[str, str]]], str]


def default_script(prompt_version: str, messages: list[dict[str, str]]) -> str:
    """What a dry run answers. Enough shape for every parser downstream."""

    if prompt_version.startswith("sufficiency"):
        return json.dumps(
            {
                "status": "NEED_CLARIFICATION",
                "reason": "dry run",
                "gaps": [{"id": "gap_1", "description": "a missing value", "priority": 0.9}],
            }
        )
    if prompt_version.startswith("gap_selection"):
        return json.dumps({"selected_gap_id": "gap_1", "question": "What is the missing value?"})
    if prompt_version.startswith("question_generation"):
        return json.dumps({"question": "What is the missing value?"})
    if prompt_version.startswith("simulator"):
        return json.dumps({"answer": "It is 30 meters.", "knew": True})
    if prompt_version.startswith("judge"):
        return json.dumps({"correct": True, "reason": "dry run"})
    if prompt_version.startswith("coverage"):
        return json.dumps({"covered": [0]})
    if prompt_version.startswith("understanding") or prompt_version.startswith("state_update"):
        return "Dry-run notes about the task."
    return "The answer is A."


# Rate limiting and gateway hiccups are infrastructure, not results. Recorded
# as failures they would bias whichever arm happened to hit them, so these are
# retried -- and only these. A refused key, a bad request or an unparseable
# answer is a real outcome and is recorded as one.
RETRY_STATUS = (408, 429, 500, 502, 503, 504)
MAX_ATTEMPTS = 4
BACKOFF_SECONDS = 2.0


class RetryableStatus(RuntimeError):
    def __init__(self, status: int, body: str) -> None:
        super().__init__(f"OpenRouter {status}: {body[:200]}")
        self.status = status


@dataclass
class Provider:
    """Every model call in the experiment goes through here."""

    candidate: ModelSpec = field(default_factory=ModelSpec)
    simulator: ModelSpec = field(default_factory=ModelSpec)
    judge: ModelSpec = field(default_factory=ModelSpec)
    base_url: str = DEFAULT_BASE_URL
    api_key: str | None = None
    timeout: float = 120.0
    dry_run: bool = False
    log_prompts: bool = False
    script: ScriptedResponder = default_script
    client: httpx.AsyncClient | None = None
    max_attempts: int = MAX_ATTEMPTS

    def __post_init__(self) -> None:
        if self.api_key is None:
            self.api_key = api_key_from_environment()
        if not self.dry_run and not self.api_key:
            raise ProviderError(
                "No OpenRouter key. Set OPENROUTER_CYBERCASE or OPENROUTER_API_KEY, "
                "or pass --dry-run."
            )

    def spec_for(self, role: CallRole) -> ModelSpec:
        return {"candidate": self.candidate, "simulator": self.simulator, "judge": self.judge}[role]

    async def call(
        self,
        *,
        messages: list[dict[str, str]],
        stage: str,
        role: CallRole,
        prompt_version: str,
        sink: list[CallRecord],
        json_mode: bool = False,
    ) -> str:
        """One model call, recorded whether it succeeded or not."""

        spec = self.spec_for(role)
        record = CallRecord(
            stage=stage,
            role=role,
            prompt_version=prompt_version,
            model=spec.model,
        )
        if self.log_prompts:
            record.prompt = json.dumps(messages, ensure_ascii=False)
        sink.append(record)

        started = time.perf_counter()
        try:
            if self.dry_run:
                text = self.script(prompt_version, messages)
            else:
                text = await self.request_with_retry(messages, spec, json_mode, record)
            if self.log_prompts:
                record.response = text
            return text
        except Exception as error:  # recorded, not raised: one bad call is data
            record.error = f"{type(error).__name__}: {error}"
            return ""
        finally:
            record.latency_ms = round((time.perf_counter() - started) * 1000, 2)

    async def request_with_retry(
        self,
        messages: list[dict[str, str]],
        spec: ModelSpec,
        json_mode: bool,
        record: CallRecord,
    ) -> str:
        """Retry only what is worth retrying, with a widening wait."""

        for attempt in range(1, self.max_attempts + 1):
            try:
                return await self.request(messages, spec, json_mode, record)
            except (RetryableStatus, httpx.TimeoutException, httpx.TransportError) as error:
                if attempt == self.max_attempts:
                    raise ProviderError(f"{error} (after {attempt} attempts)") from error
                record.retries = attempt
                await asyncio.sleep(BACKOFF_SECONDS * attempt)
        raise ProviderError("unreachable")

    async def request(
        self,
        messages: list[dict[str, str]],
        spec: ModelSpec,
        json_mode: bool,
        record: CallRecord,
    ) -> str:
        payload: dict[str, object] = {
            "model": spec.model,
            "messages": messages,
            "temperature": spec.temperature,
            "max_tokens": spec.max_tokens,
        }
        if spec.seed is not None:
            payload["seed"] = spec.seed
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Title": "CyberCase Clarification Pilot",
        }

        if self.client is not None:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )
        else:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions", headers=headers, json=payload
                )

        if response.status_code in RETRY_STATUS:
            raise RetryableStatus(response.status_code, response.text)
        if response.status_code != 200:
            raise ProviderError(f"OpenRouter {response.status_code}: {response.text[:400]}")

        body = response.json()
        usage = body.get("usage") or {}
        record.input_tokens = int(usage.get("prompt_tokens") or 0)
        record.output_tokens = int(usage.get("completion_tokens") or 0)
        choices = body.get("choices") or [{}]
        return str((choices[0].get("message") or {}).get("content") or "")

    async def structured(
        self,
        *,
        messages: list[dict[str, str]],
        schema: type[Parsed],
        stage: str,
        role: CallRole,
        prompt_version: str,
        sink: list[CallRecord],
    ) -> Parsed | None:
        """A parsed object, or None with the reason recorded on the call.

        None is a fatal parsing error for the arm that asked, which is one of
        the stop conditions. Nothing is retried and nothing is guessed.
        """

        text = await self.call(
            messages=messages,
            stage=stage,
            role=role,
            prompt_version=prompt_version,
            sink=sink,
            json_mode=True,
        )
        if not text:
            return None
        try:
            return schema.model_validate_json(strip_fences(text))
        except ValidationError as error:
            # Which fields, never what was in them: the values are model output
            # over benchmark text. Without this a parse failure is undiagnosable
            # after the fact, which is how a 2.7% failure rate stays a mystery.
            where = "; ".join(
                f"{'.'.join(str(part) for part in item['loc']) or '(root)'}: {item['type']}"
                for item in error.errors()[:5]
            )
            sink[-1].error = f"parse: ValidationError [{where}]"
            return None
        except ValueError as error:
            sink[-1].error = f"parse: {type(error).__name__}"
            return None


__all__ = [
    "DEFAULT_BASE_URL",
    "DEFAULT_MODEL",
    "KEY_NAMES",
    "ModelSpec",
    "Provider",
    "ProviderError",
    "ScriptedResponder",
    "api_key_from_environment",
    "dotenv_values",
    "default_script",
    "strip_fences",
]
