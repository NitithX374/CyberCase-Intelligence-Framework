from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.config import settings
from app.services.llm.model_registry import resolve_openrouter_model


class AnalysisPipelineConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    model: str = Field(
        default_factory=lambda: resolve_openrouter_model(settings.case_analysis_model),
        min_length=1,
    )
    context_tokens: int = Field(default=128_000, ge=1)
    input_tokens: int = Field(default=80_000, ge=1)
    output_tokens: int = Field(default=16_384, ge=16_384)
    safety_tokens: int = Field(default=4_000, ge=1)
    timeout_seconds: float = Field(default=120, gt=0)

    @model_validator(mode="after")
    def validate_budget(self) -> "AnalysisPipelineConfig":
        if self.output_tokens + self.safety_tokens >= self.context_tokens:
            raise ValueError("Analysis output and safety budgets exhaust context")
        if self.model != self.model.strip() or "/" not in self.model:
            raise ValueError("Use an explicit provider model identifier")
        return self


def configured_pipeline() -> AnalysisPipelineConfig:
    return AnalysisPipelineConfig()
