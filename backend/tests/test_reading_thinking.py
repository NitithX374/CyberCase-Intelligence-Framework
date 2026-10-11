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
    payload = stage_payload(restored.for_reading(), "system", {}, CaseProviderReadingReply)
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


def test_historical_configuration_inherits_the_shared_budget_for_assessment():
    historical = AnalysisPipelineConfig.model_validate(
        {"model": "test/model", "thinking_tokens": 4096}
    )
    assert historical.assess_thinking_tokens is None
    assert historical.for_assess() is historical


def test_assess_override_is_persisted_and_changes_nothing_but_the_assessment():
    config = AnalysisPipelineConfig(model="test/model", assess_thinking_tokens=0)
    restored = AnalysisPipelineConfig.model_validate_json(config.model_dump_json())
    assert restored == config
    assert restored.for_assess().thinking_tokens == 0
    assert restored.for_assess().output_tokens == restored.output_tokens == 32608
    assert restored.thinking_tokens == 8192
    assert restored.for_reading().thinking_tokens == 8192
    payload = stage_payload(restored.for_assess(), "system", {}, CaseProviderJudgement)
    assert payload["thinking"] == {"type": "disabled"}
    assert payload["max_tokens"] == restored.output_tokens


@pytest.mark.parametrize("thinking", [-1, 1, 512, 1023])
def test_invalid_assess_budgets_are_refused(thinking):
    with pytest.raises(ValidationError):
        AnalysisPipelineConfig(model="test/model", assess_thinking_tokens=thinking)


def test_assess_budget_cannot_exhaust_context():
    with pytest.raises(ValidationError, match="exhaust context"):
        AnalysisPipelineConfig(
            model="test/model",
            context_tokens=48000,
            thinking_tokens=0,
            assess_thinking_tokens=16384,
        )


def test_configured_pipeline_records_the_assess_setting(monkeypatch):
    monkeypatch.setattr(settings, "case_assess_thinking_tokens", 0)
    monkeypatch.setattr(settings, "case_reading_thinking_tokens", None)
    config = configured_pipeline()
    assert config.assess_thinking_tokens == 0
    assert config.for_assess().thinking_tokens == 0
    assert config.reading_thinking_tokens is None
    assert config.thinking_tokens == 8192


def test_the_assessment_is_unchanged_when_no_assess_setting_is_given(monkeypatch):
    monkeypatch.setattr(settings, "case_assess_thinking_tokens", None)
    assert configured_pipeline().for_assess().thinking_tokens == 8192


async def test_only_the_assessment_receives_the_assess_override(monkeypatch):
    from app.analysis import pipeline
    from app.trace.claims import CaseAssessmentTrace

    seen = []

    async def request_stage(**kwargs):
        seen.append(kwargs)
        return CaseAssessmentTrace(gaps=[])

    monkeypatch.setattr(pipeline, "request_stage", request_stage)
    config = AnalysisPipelineConfig(model="test/model", assess_thinking_tokens=0)
    await pipeline.assess_case(
        source_bundle=CaseSourceBundle(1, (CaseSourceItem("S1", "narrative", "A text."),)),
        followup_history=(),
        response_language="english",
        config=config,
    )
    assert [(item["stage"], item["config"].thinking_tokens) for item in seen] == [("assess", 0)]
    assert config.thinking_tokens == 8192


def test_historical_configuration_inherits_the_shared_budget_for_judgement():
    historical = AnalysisPipelineConfig.model_validate(
        {"model": "test/model", "thinking_tokens": 4096}
    )
    assert historical.judgement_thinking_tokens is None
    assert historical.for_judgement() is historical


def test_judgement_override_is_persisted_and_changes_nothing_but_the_judgement():
    config = AnalysisPipelineConfig(model="test/model", judgement_thinking_tokens=2048)
    restored = AnalysisPipelineConfig.model_validate_json(config.model_dump_json())
    assert restored == config
    assert restored.for_judgement().thinking_tokens == 2048
    assert restored.for_judgement().output_tokens == restored.output_tokens == 32608
    assert restored.thinking_tokens == 8192
    assert restored.for_reading().thinking_tokens == 8192
    assert restored.for_assess().thinking_tokens == 8192
    payload = stage_payload(restored.for_judgement(), "system", {}, CaseProviderJudgement)
    assert payload["thinking"] == {"type": "enabled", "budget_tokens": 2048}
    assert payload["max_tokens"] == restored.output_tokens + 2048


@pytest.mark.parametrize("thinking", [-1, 1, 512, 1023])
def test_invalid_judgement_budgets_are_refused(thinking):
    with pytest.raises(ValidationError):
        AnalysisPipelineConfig(model="test/model", judgement_thinking_tokens=thinking)


def test_judgement_budget_cannot_exhaust_context():
    with pytest.raises(ValidationError, match="exhaust context"):
        AnalysisPipelineConfig(
            model="test/model",
            context_tokens=48000,
            thinking_tokens=0,
            judgement_thinking_tokens=16384,
        )


def test_configured_pipeline_records_the_judgement_setting(monkeypatch):
    monkeypatch.setattr(settings, "case_judgement_thinking_tokens", 4096)
    monkeypatch.setattr(settings, "case_reading_thinking_tokens", None)
    monkeypatch.setattr(settings, "case_assess_thinking_tokens", None)
    config = configured_pipeline()
    assert config.judgement_thinking_tokens == 4096
    assert config.for_judgement().thinking_tokens == 4096
    assert config.for_reading().thinking_tokens == 8192
    assert config.for_assess().thinking_tokens == 8192


async def test_only_the_judgement_receives_the_judgement_override(monkeypatch):
    from app.sources.evidence import evidence_units

    seen = []
    source = CaseSourceItem("S1", "narrative", "John sent an email.")

    async def request_stage(**kwargs):
        seen.append(kwargs)
        if kwargs["stage"] == "case_reading":
            return CaseProviderReadingReply.model_validate(
                {
                    "version": "case_analysis_trace_v1",
                    "claims": [
                        {
                            "claim_id": "A-01",
                            "claim_type": "reported",
                            "text": source.text,
                            "epistemic_status": "reported",
                            "supporting_citations": [
                                {
                                    "source_id": source.source_id,
                                    "evidence_unit_ids": [evidence_units(source)[0].unit_id],
                                }
                            ],
                        }
                    ],
                }
            )
        return CaseProviderJudgement(version="case_analysis_trace_v1", summary="No claims.")

    monkeypatch.setattr(write, "request_stage", request_stage)
    config = AnalysisPipelineConfig(
        model="test/model",
        assess_thinking_tokens=4096,
        reading_thinking_tokens=2048,
        judgement_thinking_tokens=1024,
    )
    await write.write_trace(
        sources=CaseSourceBundle(1, (source,)),
        language="english",
        config=config,
    )
    assert [(item["stage"], item["config"].thinking_tokens) for item in seen] == [
        ("case_reading", 2048),
        ("case_judgement", 1024),
    ]
    assert config.thinking_tokens == 8192


async def test_the_assess_override_reaches_no_other_stage_whatever_its_size(monkeypatch):
    from app.sources.evidence import evidence_units

    seen = []
    source = CaseSourceItem("S1", "narrative", "John sent an email.")

    async def request_stage(**kwargs):
        seen.append(kwargs)
        if kwargs["stage"] == "case_reading":
            return CaseProviderReadingReply.model_validate(
                {
                    "version": "case_analysis_trace_v1",
                    "claims": [
                        {
                            "claim_id": "A-01",
                            "claim_type": "reported",
                            "text": source.text,
                            "epistemic_status": "reported",
                            "supporting_citations": [
                                {
                                    "source_id": source.source_id,
                                    "evidence_unit_ids": [evidence_units(source)[0].unit_id],
                                }
                            ],
                        }
                    ],
                }
            )
        return CaseProviderJudgement(version="case_analysis_trace_v1", summary="No claims.")

    monkeypatch.setattr(write, "request_stage", request_stage)
    config = AnalysisPipelineConfig(
        model="test/model", assess_thinking_tokens=4096, reading_thinking_tokens=2048
    )
    await write.write_trace(
        sources=CaseSourceBundle(1, (source,)),
        language="english",
        config=config,
    )
    assert [(item["stage"], item["config"].thinking_tokens) for item in seen] == [
        ("case_reading", 2048),
        ("case_judgement", 8192),
    ]
    assert config.for_assess().thinking_tokens == 4096
    assert config.for_reading().thinking_tokens == 2048
    assert config.for_views().thinking_tokens == 0


async def test_only_reading_receives_its_stage_override(monkeypatch):
    from app.sources.evidence import evidence_units

    seen = []
    source = CaseSourceItem("S1", "narrative", "John sent an email.")

    async def request_stage(**kwargs):
        seen.append(kwargs)
        if kwargs["stage"] == "case_reading":
            return CaseProviderReadingReply.model_validate(
                {
                    "version": "case_analysis_trace_v1",
                    "claims": [
                        {
                            "claim_id": "A-01",
                            "claim_type": "reported",
                            "text": source.text,
                            "epistemic_status": "reported",
                            "supporting_citations": [
                                {
                                    "source_id": source.source_id,
                                    "evidence_unit_ids": [evidence_units(source)[0].unit_id],
                                }
                            ],
                        }
                    ],
                }
            )
        return CaseProviderJudgement(version="case_analysis_trace_v1", summary="No claims.")

    monkeypatch.setattr(write, "request_stage", request_stage)
    config = AnalysisPipelineConfig(model="test/model", reading_thinking_tokens=0)
    await write.write_trace(
        sources=CaseSourceBundle(1, (source,)),
        language="english",
        config=config,
    )
    assert [(item["stage"], item["config"].thinking_tokens) for item in seen] == [
        ("case_reading", 0),
        ("case_judgement", 8192),
    ]
    assert seen[1]["config"] is config
