from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.config import settings
from app.services.llm.model_registry import resolve_openrouter_model

MIN_THINKING_TOKENS = 1_024


def provider_order(value: str) -> tuple[str, ...]:
    return tuple(dict.fromkeys(name.strip() for name in value.split(",") if name.strip()))


class AnalysisPipelineConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    model: str = Field(
        default_factory=lambda: resolve_openrouter_model(settings.case_analysis_model),
        min_length=1,
    )
    providers: tuple[str, ...] = Field(
        default_factory=lambda: provider_order(settings.case_analysis_providers)
    )
    context_tokens: int = Field(default=128_000, ge=1)
    input_tokens: int = Field(default=80_000, ge=1)
    output_tokens: int = Field(default=32_608, ge=1)
    thinking_tokens: int = Field(default=8_192, ge=0)
    safety_tokens: int = Field(default=4_000, ge=1)
    timeout_seconds: float = Field(default=120, gt=0)

    @property
    def max_tokens(self) -> int:
        return self.output_tokens + self.thinking_tokens

    @model_validator(mode="after")
    def validate_budget(self) -> "AnalysisPipelineConfig":
        if self.max_tokens + self.safety_tokens >= self.context_tokens:
            raise ValueError("Analysis output, thinking and safety budgets exhaust context")
        if 0 < self.thinking_tokens < MIN_THINKING_TOKENS:
            raise ValueError("Thinking is off at 0 or budgeted with at least 1,024 tokens")
        if self.model != self.model.strip() or "/" not in self.model:
            raise ValueError("Use an explicit provider model identifier")
        return self


def configured_pipeline() -> AnalysisPipelineConfig:
    return AnalysisPipelineConfig()
