from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.config import settings
from app.llm.registry import resolve_openrouter_model

MIN_THINKING_TOKENS = 1_024
SOURCE_TOKEN_BUDGET = 40_000
SOURCE_OVERHEAD_TOKENS = 100


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
    reading_thinking_tokens: int | None = Field(default=None, ge=0)
    safety_tokens: int = Field(default=4_000, ge=1)
    timeout_seconds: float = Field(default=120, gt=0)

    @property
    def max_tokens(self) -> int:
        return self.output_tokens + self.thinking_tokens

    def for_reading(self) -> "AnalysisPipelineConfig":
        if self.reading_thinking_tokens is None:
            return self
        return type(self).model_validate(
            {
                **self.model_dump(),
                "thinking_tokens": self.reading_thinking_tokens,
                "reading_thinking_tokens": None,
            }
        )

    def for_views(self) -> "AnalysisPipelineConfig":
        return type(self).model_validate(
            {
                **self.model_dump(),
                "output_tokens": min(self.output_tokens, 4_096),
                "thinking_tokens": 0,
                "reading_thinking_tokens": None,
                "timeout_seconds": min(self.timeout_seconds, 60),
            }
        )

    @model_validator(mode="after")
    def validate_budget(self) -> "AnalysisPipelineConfig":
        for thinking in (self.thinking_tokens, self.reading_thinking_tokens):
            if thinking is None:
                continue
            if 0 < thinking < MIN_THINKING_TOKENS:
                raise ValueError("Thinking is off at 0 or budgeted with at least 1,024 tokens")
            if self.output_tokens + thinking + self.safety_tokens >= self.context_tokens:
                raise ValueError("Analysis output, thinking and safety budgets exhaust context")
        if self.model != self.model.strip() or "/" not in self.model:
            raise ValueError("Use an explicit provider model identifier")
        return self


def configured_pipeline() -> AnalysisPipelineConfig:
    return AnalysisPipelineConfig(reading_thinking_tokens=settings.case_reading_thinking_tokens)
