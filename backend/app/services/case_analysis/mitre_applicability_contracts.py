from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


MITRE_APPLICABILITY_GATE_VERSION = "mitre_applicability_v1"
MitreApplicabilityDecision = Literal["SKIP", "RETRIEVE"]


class ProviderMitreApplicability(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: MitreApplicabilityDecision
    source_message_ids: list[str] = Field(default_factory=list, max_length=64)
    trigger_text: list[str] = Field(default_factory=list, max_length=16)

    @field_validator("source_message_ids")
    @classmethod
    def normalize_source_ids(cls, value: list[str]) -> list[str]:
        normalized = [item.strip() for item in value]
        if any(not item for item in normalized) or len(set(normalized)) != len(
            normalized
        ):
            raise ValueError("source message IDs must be non-empty and unique")
        return normalized

    @field_validator("trigger_text")
    @classmethod
    def normalize_trigger_text(cls, value: list[str]) -> list[str]:
        normalized = [item.strip() for item in value]
        if any(not item or len(item) > 500 for item in normalized) or len(
            set(normalized)
        ) != len(normalized):
            raise ValueError("trigger text must be non-empty, bounded, and unique")
        return normalized


class MitreApplicabilityRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal["mitre_applicability_v1"] = MITRE_APPLICABILITY_GATE_VERSION
    decision: MitreApplicabilityDecision
    source_message_ids: list[str] = Field(default_factory=list, max_length=64)
    trigger_text: list[str] = Field(default_factory=list, max_length=16)
    failure_code: str | None = Field(default=None, max_length=120)

    @model_validator(mode="after")
    def validate_routing_record(self) -> "MitreApplicabilityRecord":
        if self.decision == "SKIP":
            if self.source_message_ids or self.trigger_text:
                raise ValueError("SKIP records cannot retain trigger evidence")
            return self
        if not self.source_message_ids or not self.trigger_text or self.failure_code:
            raise ValueError("RETRIEVE requires grounded trigger evidence")
        return self


def skipped_mitre_applicability(
    failure_code: str | None = None,
) -> MitreApplicabilityRecord:
    return MitreApplicabilityRecord(
        decision="SKIP",
        source_message_ids=[],
        trigger_text=[],
        failure_code=failure_code,
    )


__all__ = [
    "MITRE_APPLICABILITY_GATE_VERSION",
    "MitreApplicabilityDecision",
    "MitreApplicabilityRecord",
    "ProviderMitreApplicability",
    "skipped_mitre_applicability",
]
