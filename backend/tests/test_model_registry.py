import pytest

from app.services.llm.model_registry import (
    DEFAULT_OPENROUTER_MODEL,
    resolve_openrouter_model,
)


def test_default_model():
    assert DEFAULT_OPENROUTER_MODEL == "deepseek/deepseek-v4.1-flash"
    assert resolve_openrouter_model(None) == DEFAULT_OPENROUTER_MODEL
    assert resolve_openrouter_model("") == DEFAULT_OPENROUTER_MODEL
    assert resolve_openrouter_model("default") == DEFAULT_OPENROUTER_MODEL


@pytest.mark.parametrize(
    ("alias", "expected_canonical_id"),
    [
        ("4o-mini", "openai/gpt-4o-mini"),
        ("gpt-4o-mini", "openai/gpt-4o-mini"),
        ("mini", "openai/gpt-4o-mini"),
        ("luna", "openai/gpt-5.6-luna"),
        ("gpt-luna", "openai/gpt-5.6-luna"),
        ("gpt-5.6-luna", "openai/gpt-5.6-luna"),
        ("gpt-oss-120b", "openai/gpt-oss-120b"),
        ("gpt-oss", "openai/gpt-oss-120b"),
        ("oss-120b", "openai/gpt-oss-120b"),
        ("oss", "openai/gpt-oss-120b"),
        ("sonnet", "anthropic/claude-3.5-sonnet"),
        ("claude-sonnet", "anthropic/claude-3.5-sonnet"),
        ("claude-3.5-sonnet", "anthropic/claude-3.5-sonnet"),
        ("haiku", "anthropic/claude-3.5-haiku"),
        ("claude-haiku", "anthropic/claude-3.5-haiku"),
        ("4o", "openai/gpt-4o"),
        ("qwen3.8-27b", "qwen/qwen3.8-27b"),
        ("qwen", "qwen/qwen3.8-27b"),
        ("deepseek", "deepseek/deepseek-v4.1-flash"),
        ("deepseek-v4.1-flash", "deepseek/deepseek-v4.1-flash"),
        ("gpt-4o", "openai/gpt-4o"),
    ],
)
def test_curated_aliases_resolution(alias: str, expected_canonical_id: str):
    assert resolve_openrouter_model(alias) == expected_canonical_id
    assert resolve_openrouter_model(alias.upper()) == expected_canonical_id
    assert resolve_openrouter_model(f"openrouter/{alias}") == expected_canonical_id


def test_custom_model_passthrough():
    custom = "mistralai/mistral-large-2411"
    assert resolve_openrouter_model(custom) == custom
    assert resolve_openrouter_model(f"openrouter/{custom}") == custom


def test_unknown_alias_fails_clearly():
    with pytest.raises(ValueError, match="Unknown OpenRouter model alias"):
        resolve_openrouter_model("not-a-configured-model")
