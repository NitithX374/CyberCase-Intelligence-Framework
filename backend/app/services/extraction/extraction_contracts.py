from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.services.extraction.extraction_config import (
    BASELINE_EXTRACTION_MODE,
    BASELINE_EXTRACTION_PROMPT_VERSION,
    BASELINE_EXTRACTION_VERSION,
)

Confidence = Literal["high", "medium", "low", "unknown"]
ReportedStatus = Literal["reported", "unknown", "not_confirmed"]
RelationshipStatus = Literal[
    "reported",
    "suspected",
    "contradicted",
    "not_established",
]
FactCategory = Literal[
    "background",
    "observation",
    "action",
    "access",
    "technical",
    "impact",
    "response",
    "attribution",
    "other",
]
FactStatus = Literal[
    "reported",
    "suspected",
    "contradicted",
    "not_established",
    "unknown",
]
ImpactStatus = Literal[
    "reported",
    "suspected",
    "contradicted",
    "not_established",
    "unknown",
]
MissingImportance = Literal[
    "material",
    "important",
    "useful",
    "unknown",
]


class ExtractionSourceMessage(BaseModel):
    """One user-authored message authorized as extraction input."""

    model_config = ConfigDict(extra="forbid")

    message_id: UUID
    ordinal: int = Field(gt=0)
    source_type: Literal["user_case_statement", "clarification_answer"]
    content: str = Field(min_length=1)

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("source message content cannot be empty")
        return value


class ExtractionInput(BaseModel):
    """Ordered, provenance-bearing input packet for one extraction call."""

    model_config = ConfigDict(extra="forbid")

    thread_id: UUID
    messages: list[ExtractionSourceMessage] = Field(min_length=1)

    @field_validator("messages")
    @classmethod
    def validate_messages(
        cls,
        value: list[ExtractionSourceMessage],
    ) -> list[ExtractionSourceMessage]:
        message_ids = [message.message_id for message in value]
        ordinals = [message.ordinal for message in value]
        if len(set(message_ids)) != len(message_ids):
            raise ValueError("source message IDs must be unique")
        if len(set(ordinals)) != len(ordinals):
            raise ValueError("source message ordinals must be unique")
        if ordinals != sorted(ordinals):
            raise ValueError("source messages must be ordered by ordinal")
        return value


class ExtractedFact(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fact_id: str = Field(min_length=1)
    statement: str = Field(min_length=1)
    category: FactCategory
    status: FactStatus
    confidence: Confidence
    source_message_ids: list[UUID] = Field(min_length=1)


class ExtractedEntity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entity_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    entity_type: str = Field(min_length=1)
    reported_role: str | None = None
    confidence: Confidence
    source_message_ids: list[UUID] = Field(min_length=1)


class ExtractedRelationship(BaseModel):
    model_config = ConfigDict(extra="forbid")

    relationship_id: str = Field(min_length=1)
    subject_entity_id: str = Field(min_length=1)
    predicate: str = Field(
        min_length=1,
        max_length=80,
        pattern=r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$",
        description=(
            "Concise English lowercase ASCII snake_case relationship label; "
            "starts with a letter and uses only letters, digits, and underscores."
        ),
    )
    object_entity_id: str = Field(min_length=1)
    statement: str = Field(min_length=1)
    status: RelationshipStatus
    confidence: Confidence
    source_message_ids: list[UUID] = Field(min_length=1)


class ExtractedEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    artifact_type: str = Field(min_length=1)
    status: ReportedStatus
    confidence: Confidence
    source_type: Literal["user_reported"]
    source_message_ids: list[UUID] = Field(min_length=1)


class ExtractedTimelineEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(min_length=1)
    timestamp: datetime | None = None
    timestamp_text: str | None = None
    event: str = Field(min_length=1)
    actors: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    status: ReportedStatus
    confidence: Confidence
    source_message_ids: list[UUID] = Field(min_length=1)


class ExtractedImpact(BaseModel):
    model_config = ConfigDict(extra="forbid")

    impact_id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    impact_type: str = Field(min_length=1)
    affected_entity_ids: list[str] = Field(default_factory=list)
    status: ImpactStatus
    confidence: Confidence
    source_message_ids: list[UUID] = Field(min_length=1)


class ExtractedMissingInformation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    missing_id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    importance: MissingImportance
    source_message_ids: list[UUID] = Field(min_length=1)


class CaseState(BaseModel):
    """Canonical factual Case State stored in case_state_versions.state_json."""

    model_config = ConfigDict(extra="forbid")

    facts: list[ExtractedFact] = Field(default_factory=list)
    entities: list[ExtractedEntity] = Field(default_factory=list)
    relationships: list[ExtractedRelationship] = Field(default_factory=list)
    evidence: list[ExtractedEvidence] = Field(default_factory=list)
    timeline: list[ExtractedTimelineEvent] = Field(default_factory=list)
    impacts: list[ExtractedImpact] = Field(default_factory=list)
    missing_information: list[ExtractedMissingInformation] = Field(
        default_factory=list
    )
    warnings: list[str] = Field(default_factory=list)


BaselineExtraction = CaseState


class LegacyBaselineExtractionV1(BaseModel):
    """Read-only reader for persisted pre-v2 extraction rows."""

    model_config = ConfigDict(extra="forbid")

    version: Literal["baseline_extraction_v1"]
    mode: Literal["single_pass_llm"]
    status: Literal["candidate"]
    case_summary: str | None = None
    entities: list[ExtractedEntity] = Field(default_factory=list)
    relationships: list[ExtractedRelationship] = Field(default_factory=list)
    evidence: list[ExtractedEvidence] = Field(default_factory=list)
    timeline: list[ExtractedTimelineEvent] = Field(default_factory=list)
    missing_information: list[ExtractedMissingInformation] = Field(
        default_factory=list
    )
    warnings: list[str] = Field(default_factory=list)


class ExtractionValidationError(ValueError):
    """Raised when an otherwise parseable model response is not safe to use."""


class ExtractionFailure(Exception):
    """Safe failure with a stable code and no upstream response leakage."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        raw_response: str | None = None,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.raw_response = raw_response
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens


@dataclass(frozen=True)
class ExtractionModelResponse:
    """Provider-neutral model response used by production and fake adapters."""

    text: str
    input_tokens: int | None = None
    output_tokens: int | None = None


class ExtractionModelAdapter(Protocol):
    async def complete(
        self,
        *,
        system_prompt: str,
        input_payload: dict[str, object],
        model: str,
        max_output_tokens: int,
    ) -> ExtractionModelResponse | str | Mapping[str, object]:
        """Return the model's structured JSON response."""
