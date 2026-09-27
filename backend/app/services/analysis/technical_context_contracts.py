from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.rag import LegalReferenceResult

MITRE_APPLICABILITY_GATE_VERSION = "mitre_applicability_v1"


MitreApplicabilityDecision = Literal["SKIP", "RETRIEVE"]


class MitreApplicabilityRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal["mitre_applicability_v1"] = MITRE_APPLICABILITY_GATE_VERSION
    decision: MitreApplicabilityDecision
    source_message_ids: list[str] = Field(default_factory=list, max_length=64)
    trigger_text: list[str] = Field(default_factory=list, max_length=16)
    failure_code: str | None = Field(default=None, max_length=120)
    input_truncated: bool = False

    @model_validator(mode="after")
    def validate_routing_record(self) -> MitreApplicabilityRecord:
        if self.decision == "SKIP":
            if self.source_message_ids or self.trigger_text:
                raise ValueError("SKIP records cannot retain a trigger")
            return self
        if not self.source_message_ids or not self.trigger_text or self.failure_code:
            raise ValueError("RETRIEVE requires a trigger grounded in a source")
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


CASE_MITRE_AUGMENTATION_VERSION = "case_mitre_augmentation_v1"


CaseTechnicalAugmentationStatus = Literal[
    "not_applicable",
    "insufficient_context",
    "retrieved_from_rag",
    "retrieved_with_matches",
    "failed",
]


class CaseTechnicalAugmentation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal["case_mitre_augmentation_v1"] = CASE_MITRE_AUGMENTATION_VERSION
    status: CaseTechnicalAugmentationStatus
    applicability: MitreApplicabilityRecord
    retrieval_context_id: str | None = None
    retrieval_context_reused: bool = False
    mitre_table: list[dict[str, object]] = Field(default_factory=list)
    association_ids: list[str] = Field(default_factory=list)
    failure_code: str | None = None


@dataclass(frozen=True)
class CaseRagContextPayload:
    retrieval_context_id: str | None
    context: str
    mitre_table: tuple[dict[str, object], ...]
    legal_relevance: LegalReferenceResult


__all__ = [
    "CASE_MITRE_AUGMENTATION_VERSION",
    "CaseRagContextPayload",
    "CaseTechnicalAugmentation",
    "CaseTechnicalAugmentationStatus",
    "MITRE_APPLICABILITY_GATE_VERSION",
    "MitreApplicabilityDecision",
    "MitreApplicabilityRecord",
    "skipped_mitre_applicability",
]
