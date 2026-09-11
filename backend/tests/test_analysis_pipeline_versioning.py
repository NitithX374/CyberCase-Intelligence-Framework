import pytest
from app.services.case_analysis.pipelineConfig import (
    AnalysisPipelineConfig,
    configured_pipeline,
    read_pipeline,
)
from pydantic import ValidationError


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


def test_missing_historical_configuration_uses_direct_analysis():
    assert read_pipeline(None).pipeline == "raw_direct"
    assert read_pipeline(None).version == "main_case_analysis_v1"


def test_new_runs_cannot_select_experimental_pipeline():
    assert configured_pipeline().pipeline == "raw_direct"
    with pytest.raises(TypeError):
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
    from app.services.case_analysis.prompts import (
        CASE_ANALYSIS_PROMPT_VERSION,
    )

    assert AnalysisPipelineConfig().version == CASE_ANALYSIS_PROMPT_VERSION
