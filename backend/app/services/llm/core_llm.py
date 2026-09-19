"""Resolve the production chat LLM target. One provider, no fallback."""

from __future__ import annotations

from dataclasses import dataclass

from app.config import Settings, settings
from app.services.llm.model_registry import resolve_openrouter_model


class CoreLlmConfigurationError(RuntimeError):
    """The production provider is missing required configuration."""

    def __init__(self, key_env_name: str) -> None:
        super().__init__(f"OpenRouter requires {key_env_name}; no provider fallback is configured")
        self.key_env_name = key_env_name


@dataclass(frozen=True)
class CoreLlmTarget:
    model: str
    api_key: str
    base_url: str
    messages_url: str
    headers: dict[str, str]


def resolve_core_llm_target(
    feature_model: str,
    *,
    require_key: bool = True,
    configured_settings: Settings | None = None,
) -> CoreLlmTarget:
    """Return the target for one feature's call, with its model resolved."""

    active_settings = configured_settings or settings
    api_key = active_settings.openrouter_cybercase.strip()
    if require_key and not api_key:
        raise CoreLlmConfigurationError("OPENROUTER_CYBERCASE")
    return CoreLlmTarget(
        model=resolve_openrouter_model(feature_model),
        api_key=api_key,
        base_url=active_settings.openrouter_base_url.rstrip("/"),
        messages_url=active_settings.openrouter_messages_url,
        headers={
            "Authorization": f"Bearer {api_key}",
            # The endpoint is OpenRouter's Anthropic-compatible /v1/messages,
            # which requires this header whatever model is behind it.
            "anthropic-version": "2023-06-01",
        },
    )


__all__ = [
    "CoreLlmConfigurationError",
    "CoreLlmTarget",
    "resolve_core_llm_target",
]
