import pytest
from pydantic import ValidationError

from app.config import DEFAULT_CASE_ANALYSIS_MODEL, Settings
from app.services.analysis.settings import AnalysisPipelineConfig, configured_pipeline
from app.services.llm.model_registry import DEFAULT_OPENROUTER_MODEL


def test_backend_case_analysis_has_one_exact_default_model(monkeypatch):
    monkeypatch.delenv("CASE_ANALYSIS_MODEL", raising=False)
    monkeypatch.delenv("CHAT_ASK_MODEL", raising=False)

    configured = Settings(_env_file=None)

    assert DEFAULT_CASE_ANALYSIS_MODEL == "deepseek/deepseek-v4.1-flash"
    assert DEFAULT_OPENROUTER_MODEL == DEFAULT_CASE_ANALYSIS_MODEL
    assert configured.case_analysis_model == DEFAULT_CASE_ANALYSIS_MODEL


def test_case_analysis_model_reads_the_single_environment_override(monkeypatch):
    monkeypatch.setenv("CASE_ANALYSIS_MODEL", "qwen/qwen3.8-27b:free")
    monkeypatch.setenv("CHAT_ASK_MODEL", "openai/gpt-4o")

    configured = Settings(_env_file=None)

    assert configured.case_analysis_model == "qwen/qwen3.8-27b:free"


def test_blank_model_selector_fails_instead_of_using_the_registry_default():
    with pytest.raises(ValidationError, match="CASE_ANALYSIS_MODEL must not be blank"):
        Settings(_env_file=None, case_analysis_model=" ")


@pytest.mark.parametrize(
    ("selector", "model"),
    [
        ("vendor/custom-model", "vendor/custom-model"),
        ("default", DEFAULT_CASE_ANALYSIS_MODEL),
    ],
)
def test_the_configured_pipeline_follows_the_model_setting(monkeypatch, selector, model):
    monkeypatch.setattr(
        "app.services.analysis.settings.settings.case_analysis_model",
        selector,
    )

    assert configured_pipeline().model == model


def test_a_context_budget_that_output_and_safety_exhaust_is_rejected():
    with pytest.raises(ValidationError, match="exhaust context"):
        AnalysisPipelineConfig(context_tokens=100)
