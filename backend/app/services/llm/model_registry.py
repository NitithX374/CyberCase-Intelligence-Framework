from __future__ import annotations

from app.config import DEFAULT_CASE_ANALYSIS_MODEL

DEFAULT_OPENROUTER_MODEL = DEFAULT_CASE_ANALYSIS_MODEL

MODEL_ALIASES: dict[str, tuple[str, ...]] = {
    "openai/gpt-5.6-luna": ("luna", "gpt-luna", "gpt-5.6-luna"),
    "openai/gpt-4o-mini": ("4o-mini", "gpt-4o-mini", "mini"),
    "openai/gpt-oss-120b": ("oss", "gpt-oss", "gpt-oss-120b", "oss-120b"),
    "anthropic/claude-3.5-sonnet": ("sonnet", "claude-sonnet", "claude-3.5-sonnet", "sonnet-3.5"),
    "anthropic/claude-3.5-haiku": ("haiku", "claude-haiku", "claude-3.5-haiku", "haiku-3.5"),
    "openai/gpt-4o": ("4o", "gpt-4o", "openai-4o"),
    "qwen/qwen3.8-27b": ("qwen3.8-27b", "qwen"),
    DEFAULT_OPENROUTER_MODEL: ("deepseek-v4.1-flash", "deepseek", "default"),
}

_ALIAS_MAP = {
    key.lower(): model_id
    for model_id, aliases in MODEL_ALIASES.items()
    for key in (model_id, *aliases)
}


def resolve_openrouter_model(model_name_or_alias: str | None) -> str:
    if not model_name_or_alias or not model_name_or_alias.strip():
        return DEFAULT_OPENROUTER_MODEL
    cleaned = model_name_or_alias.strip()
    if cleaned.lower().startswith("openrouter/"):
        cleaned = cleaned[len("openrouter/") :]
    if cleaned.lower() in _ALIAS_MAP:
        return _ALIAS_MAP[cleaned.lower()]
    if "/" in cleaned:
        return cleaned
    raise ValueError(f"Unknown OpenRouter model alias: {model_name_or_alias}")


__all__ = ["DEFAULT_OPENROUTER_MODEL", "MODEL_ALIASES", "resolve_openrouter_model"]
