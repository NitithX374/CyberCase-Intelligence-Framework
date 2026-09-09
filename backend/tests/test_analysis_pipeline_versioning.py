import asyncio
from types import SimpleNamespace
from uuid import uuid4

import pytest
from app.config import settings
from app.services.case_analysis.pipeline_config import (
    AnalysisPipelineConfig,
    configured_pipeline,
    read_pipeline,
)
from app.services.chat.analysis_run_config import pipeline_for_new_run
from pydantic import ValidationError


class RootDb:
    def __init__(self, config):
        self.root = SimpleNamespace(request_payload={"analysis_pipeline": config})

    async def execute(self, statement):
        return SimpleNamespace(scalar_one_or_none=lambda: self.root)


@pytest.mark.parametrize(
    "payload",
    [
        {"pipeline": "unknown"},
        {"pipeline": "claim_anchored", "version": "v12"},
        {"pipeline": "claim_anchored", "version": "main_case_analysis_v1"},
        {"pipeline": "claim_anchored", "max_claims": 65},
        {"pipeline": "claim_anchored", "context_tokens": 100},
    ],
)
def test_invalid_configuration_fails(payload):
    with pytest.raises(ValidationError):
        read_pipeline(payload)


def test_missing_historical_configuration_means_legacy_even_after_setting_change(
    monkeypatch,
):
    monkeypatch.setattr(settings, "case_analysis_pipeline", "claim_anchored")
    assert read_pipeline(None).pipeline == "raw_direct"
    assert read_pipeline(None).version == "main_case_analysis_v1"


def test_clarification_inherits_root_config_and_ask_stays_legacy(monkeypatch):
    pinned = AnalysisPipelineConfig(
        pipeline="claim_anchored", model="openai/gpt-4o", selection_tokens=9000
    )
    monkeypatch.setattr(settings, "case_analysis_pipeline", "raw_direct")
    monkeypatch.setattr(settings, "chat_ask_model", "openai/gpt-5.6-luna")

    async def exercise():
        result = await pipeline_for_new_run(
            RootDb(pinned.model_dump()),
            thread_id=uuid4(),
            root_ordinal=1,
            action="add_case_info",
            clarification_answer=True,
        )
        assert result == pinned.model_dump()
        legacy = await pipeline_for_new_run(
            RootDb(None),
            thread_id=uuid4(),
            root_ordinal=1,
            action="add_case_info",
            clarification_answer=True,
        )
        assert legacy["pipeline"] == "raw_direct"
        ask = await pipeline_for_new_run(
            RootDb(pinned.model_dump()),
            thread_id=uuid4(),
            root_ordinal=3,
            action="ask",
            clarification_answer=False,
        )
        assert ask["pipeline"] == "raw_direct"

    asyncio.run(exercise())


def test_unknown_model_alias_cannot_silently_select_default(monkeypatch):
    monkeypatch.setattr(settings, "core_llm_provider", "openrouter")
    monkeypatch.setattr(settings, "chat_ask_model", "misspelled-model")
    with pytest.raises(ValueError, match="known alias"):
        configured_pipeline(pipeline="claim_anchored")


def test_historical_raw_direct_version_reads_without_mutating_saved_payload():
    payload = AnalysisPipelineConfig().model_dump()
    payload["version"] = "main_case_analysis_v10"
    assert read_pipeline(payload).version == "main_case_analysis_v1"
    assert payload["version"] == "main_case_analysis_v10"


def test_historical_version_cannot_select_claim_anchored():
    with pytest.raises(ValidationError):
        read_pipeline({"pipeline": "claim_anchored", "version": "main_case_analysis_v10"})


def test_raw_direct_pipeline_matches_current_prompt_version():
    from app.services.case_analysis.case_analysis_prompt_config import (
        CASE_ANALYSIS_PROMPT_VERSION,
    )

    assert AnalysisPipelineConfig().version == CASE_ANALYSIS_PROMPT_VERSION
