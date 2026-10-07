import pytest
from pydantic import ValidationError

from app.analysis import write
from app.config import settings
from app.llm.request import stage_payload
from app.llm.settings import AnalysisPipelineConfig, configured_pipeline
from app.sources.bundle import CaseSourceBundle, CaseSourceItem
from app.trace.trace import CaseProviderJudgement, CaseProviderReadingReply


def test_historical_configuration_inherits_the_original_shared_thinking_budget():
    historical = AnalysisPipelineConfig.model_validate(
        {"model": "test/model", "thinking_tokens": 4096}
    )
    assert historical.reading_thinking_tokens is None
    assert historical.for_reading() is historical


def test_reading_override_is_persisted_and_does_not_change_judgement_or_output_budget():
    config = AnalysisPipelineConfig(model="test/model", reading_thinking_tokens=0)
    restored = AnalysisPipelineConfig.model_validate_json(config.model_dump_json())
    assert restored == config
    assert restored.for_reading().thinking_tokens == 0
    assert restored.for_reading().output_tokens == restored.output_tokens == 32608
    assert restored.thinking_tokens == 8192
    payload = stage_payload(
        restored.for_reading(), "system", {}, CaseProviderReadingReply, grammar=False
    )
    assert payload["thinking"] == {"type": "disabled"}
    assert payload["max_tokens"] == restored.output_tokens


@pytest.mark.parametrize("thinking", [-1, 1, 512, 1023])
def test_invalid_reading_budgets_are_refused(thinking):
    with pytest.raises(ValidationError):
        AnalysisPipelineConfig(model="test/model", reading_thinking_tokens=thinking)


def test_reading_budget_cannot_exhaust_context_even_when_shared_budget_fits():
    with pytest.raises(ValidationError, match="exhaust context"):
        AnalysisPipelineConfig(
            model="test/model",
            context_tokens=48000,
            thinking_tokens=0,
            reading_thinking_tokens=16384,
        )


def test_configured_pipeline_records_the_reading_setting(monkeypatch):
    monkeypatch.setattr(settings, "case_reading_thinking_tokens", 0)
    config = configured_pipeline()
    assert config.reading_thinking_tokens == 0
    assert config.for_reading().thinking_tokens == 0
    assert config.thinking_tokens == 8192


async def test_only_reading_receives_its_stage_override(monkeypatch):
    seen = []

    async def request_stage(**kwargs):
        seen.append(kwargs)
        if kwargs["stage"] == "case_reading":
            return CaseProviderReadingReply(version="case_analysis_trace_v1", claims=[])
        return CaseProviderJudgement(version="case_analysis_trace_v1", summary="No claims.")

    monkeypatch.setattr(write, "request_stage", request_stage)
    config = AnalysisPipelineConfig(model="test/model", reading_thinking_tokens=0)
    await write.write_trace(
        sources=CaseSourceBundle(1, (CaseSourceItem("S1", "narrative", "No event."),)),
        language="english",
        config=config,
    )
    assert [(item["stage"], item["config"].thinking_tokens) for item in seen] == [
        ("case_reading", 0),
        ("case_judgement", 8192),
    ]
    assert seen[1]["config"] is config
