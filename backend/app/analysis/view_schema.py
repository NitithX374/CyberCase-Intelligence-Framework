from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.trace.trace import ProviderImpactItem, ProviderParty, ProviderTimelineItem


class DerivedParty(ProviderParty):
    role: str | None = Field(min_length=1, max_length=500)
    claim_ids: list[str] = Field(min_length=1, max_length=64)

    @field_validator("name", "role")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        return None if value is None else super().normalize_text(value)


class DerivedTimelineEvent(ProviderTimelineItem):
    time: str | None = Field(min_length=1, max_length=500)
    claim_ids: list[str] = Field(min_length=1, max_length=64)

    @field_validator("time", "event")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        return None if value is None else super().normalize_text(value)


class DerivedImpact(ProviderImpactItem):
    claim_ids: list[str] = Field(min_length=1, max_length=64)


class DerivedCaseViewsReply(BaseModel):
    model_config = ConfigDict(extra="forbid")

    parties: list[DerivedParty] = Field(max_length=64)
    timeline: list[DerivedTimelineEvent] = Field(max_length=64)
    impacts: list[DerivedImpact] = Field(max_length=64)
