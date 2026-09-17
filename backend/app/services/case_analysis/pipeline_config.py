from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class AnalysisPipelineConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    pipeline: Literal["raw_direct"] = "raw_direct"
    version: Literal["main_case_analysis_v1"] = "main_case_analysis_v1"
    provider: Literal["openrouter", "anthropic"] = "openrouter"
    model: str = Field(default="openai/gpt-5.6-luna", min_length=1)
    context_tokens: int = Field(default=128_000, ge=1)
    input_tokens: int = Field(default=80_000, ge=1)
    output_tokens: int = Field(default=16_384, ge=16_384)
    safety_tokens: int = Field(default=4_000, ge=1)
    timeout_seconds: float = Field(default=120, gt=0)
    encoding: Literal["o200k_base"] = "o200k_base"

    @field_validator("model")
    @classmethod
    def normalize_model(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("model identifier must be non-empty")
        return trimmed

    @model_validator(mode="after")
    def validate_budget(self) -> "AnalysisPipelineConfig":
        if self.output_tokens + self.safety_tokens >= self.context_tokens:
            raise ValueError("Analysis output and safety budgets exhaust context")
        if "/" not in self.model and self.provider == "openrouter":
            raise ValueError("Use an explicit provider model identifier")
        return self


def configured_pipeline() -> AnalysisPipelineConfig:
    return AnalysisPipelineConfig()


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
