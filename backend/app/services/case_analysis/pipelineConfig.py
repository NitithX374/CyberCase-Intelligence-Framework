from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.config import settings
from app.services.llm.coreLlm import resolve_core_llm_target
from app.services.llm.modelRegistry import CURATED_MODEL_PRESETS


class AnalysisPipelineConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    pipeline: Literal["raw_direct", "claim_anchored"] = "raw_direct"
    version: Literal["main_case_analysis_v1", "claim_anchored_v1"] = (
        "main_case_analysis_v1"
    )
    extraction_version: Literal["claim_extraction_v1"] = "claim_extraction_v1"
    generation_version: Literal["claim_generation_v1"] = "claim_generation_v1"
    provider: Literal["openrouter", "anthropic"] = "openrouter"
    model: str = Field(default="openai/gpt-5.6-luna", min_length=1)
    context_tokens: int = Field(default=128_000, ge=1)
    input_tokens: int = Field(default=80_000, ge=1)
    output_tokens: int = Field(default=16_384, ge=16_384)
    safety_tokens: int = Field(default=4_000, ge=1)
    selection_tokens: int = Field(default=24_000, ge=1)
    max_claims: int = Field(default=64, ge=1, le=64)
    timeout_seconds: float = Field(default=120, gt=0)
    encoding: Literal["o200k_base"] = "o200k_base"

    @model_validator(mode="before")
    @classmethod
    def assign_version(cls, value: object) -> object:
        if isinstance(value, dict) and "version" not in value:
            value = dict(value)
            value["version"] = (
                "claim_anchored_v1"
                if value.get("pipeline") == "claim_anchored"
                else "main_case_analysis_v1"
            )
        return value

    @model_validator(mode="after")
    def validate_budget(self) -> "AnalysisPipelineConfig":
        expected = (
            "claim_anchored_v1"
            if self.pipeline == "claim_anchored"
            else "main_case_analysis_v1"
        )
        if self.version != expected:
            raise ValueError("Pipeline version does not match selected method")
        if self.output_tokens + self.safety_tokens >= self.context_tokens:
            raise ValueError("Analysis output and safety budgets exhaust context")
        if (
            self.model != self.model.strip()
            or "/" not in self.model
            and self.provider == "openrouter"
        ):
            raise ValueError("Use an explicit provider model identifier")
        return self


def configured_pipeline(
    *,
    pipeline: Literal["raw_direct", "claim_anchored"] | None = None,
) -> AnalysisPipelineConfig:
    selected_pipeline = (
        settings.case_analysis_pipeline if pipeline is None else pipeline
    )
    if selected_pipeline == "raw_direct":
        return AnalysisPipelineConfig()
    selected = settings.chat_ask_model.strip()
    aliases = {alias for preset in CURATED_MODEL_PRESETS for alias in preset.aliases}
    if (
        settings.core_llm_provider == "openrouter"
        and "/" not in selected
        and selected.lower() not in aliases
    ):
        raise ValueError(
            "Attribute-first requires a known alias or explicit model identifier"
        )
    target = resolve_core_llm_target(settings.chat_ask_model, require_key=False)
    return AnalysisPipelineConfig(
        pipeline=selected_pipeline,
        provider=target.provider,
        model=target.model,
        context_tokens=settings.chat_model_context_tokens,
        input_tokens=settings.claim_anchored_input_tokens,
        output_tokens=settings.claim_anchored_output_tokens,
        selection_tokens=settings.claim_anchored_selection_tokens,
        timeout_seconds=settings.chat_ask_timeout_seconds,
    )


def read_pipeline(value: object) -> AnalysisPipelineConfig:
    if value is None:
        return AnalysisPipelineConfig()
    if (
        isinstance(value, dict)
        and value.get("pipeline") == "raw_direct"
        and value.get("version") == "main_case_analysis_v10"
    ):
        value = {**value, "version": "main_case_analysis_v1"}
    return AnalysisPipelineConfig.model_validate(value)
