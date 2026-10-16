from __future__ import annotations

from dataclasses import dataclass

from app.config import Settings, settings
from app.llm.registry import resolve_openrouter_model


class CoreLlmConfigurationError(RuntimeError):
    def __init__(self, key_env_name: str) -> None:
        super().__init__(f"OpenRouter requires {key_env_name}; no provider fallback is configured")
        self.key_env_name = key_env_name


@dataclass(frozen=True)
class CoreLlmTarget:
    model: str
    messages_url: str
    headers: dict[str, str]
    warmup_seconds: float = 0.0

    @property
    def health_url(self) -> str:
        return f"{self.messages_url.removesuffix('/v1/messages')}/health"


def resolve_core_llm_target(
    feature_model: str,
    *,
    configured_settings: Settings | None = None,
) -> CoreLlmTarget:
    active_settings = configured_settings or settings
    api_key = active_settings.openrouter_cybercase.strip()
    if not api_key:
        raise CoreLlmConfigurationError("OPENROUTER_CYBERCASE")
    return CoreLlmTarget(
        model=resolve_openrouter_model(feature_model),
        messages_url=active_settings.openrouter_messages_url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "anthropic-version": "2023-06-01",
        },
        warmup_seconds=(
            active_settings.case_analysis_warmup_seconds
            if active_settings.case_analysis_server == "vllm"
            else 0.0
        ),
    )


__all__ = [
    "CoreLlmConfigurationError",
    "CoreLlmTarget",
    "resolve_core_llm_target",
]
