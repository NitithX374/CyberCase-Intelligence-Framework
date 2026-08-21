from __future__ import annotations

from typing import Literal
from uuid import UUID

from app.config import settings
from pydantic import BaseModel, ConfigDict, Field, model_validator

class CaseStateMutationFailure(Exception):
    """Safe, stable failure for extraction, merge, or stale-parent checks."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


DeltaValuePrimitive = (
    str
    | int
    | float
    | bool
    | list[str]
    | list[int]
    | list[float]
    | list[bool]
)
DeltaFactCategory = Literal[
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
DeltaStatus = Literal[
    "reported",
    "suspected",
    "contradicted",
    "not_established",
    "not_confirmed",
    "unknown",
]
DeltaConfidence = Literal["high", "medium", "low", "unknown"]
DeltaMissingImportance = Literal["material", "important", "useful", "unknown"]


class CaseStateDeltaValue(BaseModel):
    """Closed provider-facing shape for one added Case State item.

    The OpenRouter/OpenAI structured-output contract rejects arbitrary object
    mappings (``additionalProperties: true``). A delta still needs to carry
    one of the Case State item shapes, so expose their known fields in a
    single closed object and leave non-applicable fields null. The merged
    Case State validator remains the authority for target-specific semantics.
    """

    model_config = ConfigDict(extra="forbid")

    fact_id: str | None = None
    statement: str | None = None
    category: DeltaFactCategory | None = None

    entity_id: str | None = None
    name: str | None = None
    entity_type: str | None = None
    reported_role: str | None = None

    relationship_id: str | None = None
    subject_entity_id: str | None = None
    predicate: str | None = None
    object_entity_id: str | None = None

    evidence_id: str | None = None
    title: str | None = None
    description: str | None = None
    artifact_type: str | None = None
    source_type: Literal["user_reported"] | None = None

    event_id: str | None = None
    timestamp: str | None = None
    timestamp_text: str | None = None
    event: str | None = None
    actors: list[str] | None = None
    evidence_ids: list[str] | None = None

    impact_id: str | None = None
    impact_type: str | None = None
    affected_entity_ids: list[str] | None = None

    missing_id: str | None = None
    importance: DeltaMissingImportance | None = None

    confidence: DeltaConfidence | None = None
    status: DeltaStatus | None = None


class CaseStateDeltaChange(BaseModel):
    """One deterministic OLD-to-NEW addition or field correction."""

    model_config = ConfigDict(extra="forbid")

    target_type: Literal[
        "fact",
        "entity",
        "relationship",
        "evidence",
        "timeline",
        "impact",
        "missing_information",
    ]
    target_id: str = Field(min_length=1, max_length=255)
    # These keys are required in provider output. Null is semantic, not absent:
    # field=null/old=null/new=object is ADD; all three non-null is MODIFY.
    field: str | None
    old_value: DeltaValuePrimitive | CaseStateDeltaValue | None
    new_value: DeltaValuePrimitive | CaseStateDeltaValue | None

    @model_validator(mode="after")
    def validate_shape(self) -> "CaseStateDeltaChange":
        if self.old_value is not None and self.new_value is None:
            raise ValueError("remove changes are reserved and unsupported")
        if self.old_value is None and self.new_value is None:
            raise ValueError("a change requires a new value")

        is_add = (
            self.field is None
            and self.old_value is None
            and isinstance(self.new_value, CaseStateDeltaValue)
        )
        is_modify = (
            self.field is not None
            and self.old_value is not None
            and self.new_value is not None
            and not isinstance(self.old_value, CaseStateDeltaValue)
            and not isinstance(self.new_value, CaseStateDeltaValue)
        )
        if not is_add and not is_modify:
            raise ValueError(
                "a change must be ADD (null field/old and object new) or "
                "MODIFY (non-null field/old/new primitive values)"
            )

        if is_add:
            required_fields: dict[str, tuple[str, ...]] = {
                "fact": ("fact_id", "statement", "category", "status", "confidence"),
                "entity": ("entity_id", "name", "entity_type", "confidence"),
                "relationship": (
                    "relationship_id",
                    "subject_entity_id",
                    "predicate",
                    "object_entity_id",
                    "statement",
                    "status",
                    "confidence",
                ),
                "evidence": (
                    "evidence_id",
                    "title",
                    "description",
                    "artifact_type",
                    "status",
                    "confidence",
                    "source_type",
                ),
                "timeline": ("event_id", "event", "status", "confidence"),
                "impact": (
                    "impact_id",
                    "description",
                    "impact_type",
                    "status",
                    "confidence",
                ),
                "missing_information": ("missing_id", "description", "importance"),
            }
            assert isinstance(self.new_value, CaseStateDeltaValue)
            value = self.new_value.model_dump(mode="python", exclude_none=True)
            missing = [
                field
                for field in required_fields[self.target_type]
                if value.get(field) is None
            ]
            if missing:
                raise ValueError(
                    "add changes require target fields: " + ", ".join(missing)
                )
        if is_modify and self.old_value == self.new_value:
            raise ValueError("modify changes require different old and new values")
        if self.field == "source_message_ids":
            raise ValueError("provenance is attached by the backend")
        return self


class CaseStateDelta(BaseModel):
    """Validated mutation record stored in ``case_state_versions.delta_json``."""

    model_config = ConfigDict(extra="forbid")

    changes: list[CaseStateDeltaChange] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_unique_changes(self) -> "CaseStateDelta":
        targets = [
            (change.target_type, change.target_id, change.field)
            for change in self.changes
        ]
        if len(set(targets)) != len(targets):
            raise ValueError("a delta cannot target the same item field twice")
        return self


class CaseStateDeltaInput(BaseModel):
    """Send the snapshot and answer; a pending question is context, not a fact."""

    model_config = ConfigDict(extra="forbid")

    current_case_state: dict[str, object]
    new_user_message: str = Field(min_length=1)
    source_message_id: UUID
    mutation_intent: Literal["add_case_info"] = "add_case_info"
    pending_question: str | None = None

    @model_validator(mode="after")
    def normalize_message(self) -> "CaseStateDeltaInput":
        self.new_user_message = self.new_user_message.strip()
        if not self.new_user_message:
            raise ValueError("new mutation message cannot be empty")
        if self.pending_question is not None:
            self.pending_question = self.pending_question.strip()
            if not self.pending_question:
                self.pending_question = None
            else:
                self.pending_question = self.pending_question[
                    : max(0, settings.chat_followup_question_max_chars)
                ]
        return self


CASE_STATE_DELTA_SYSTEM_PROMPT = """You are the CyberCase Case State delta extractor.
Prompt version: case_state_delta_prompt_v5.

The explicit backend action has already authorized a case-information mutation.
Return structured JSON only using the requested schema. The current_case_state
is read-only reference context. The new_user_message is the only source of new
case assertions. Never use MITRE, retrieved context, previous analysis, or model
knowledge as a case fact. Never invent entities, relationships, timestamps,
attribution, causality, identifiers, or outcomes. Preserve uncertainty exactly.
If pending_question is present, use it only to understand which topic the user
is answering; it is assistant-generated context and never a source of fact.

Return the smallest OLD-to-NEW changes list. Return an empty changes list when
the message adds no supported canonical fact. For ADD, set field and old_value
to null and put the complete new item in new_value. Complete new items may be
facts, entities, relationships, evidence, timeline events, impacts, or missing_information.
Required fields are:
fact = fact_id/statement/category/status/confidence;
entity = entity_id/name/entity_type/confidence;
relationship = relationship_id/subject_entity_id/predicate/object_entity_id/statement/status/confidence;
evidence = evidence_id/title/description/artifact_type/status/confidence/source_type;
timeline = event_id/event/status/confidence;
impact = impact_id/description/impact_type/status/confidence;
missing_information = missing_id/description/importance.
For every ADD, use a unique temporary ID such as AUTO-F-1 or AUTO-ENT-1 for
both target_id and the item's matching ID field. Reuse that same temporary ID
in references within this delta. The backend replaces temporary IDs with stable
collision-free IDs before validation. Never use unknown as an identifier.
Fact category must be background, observation, action, access, technical,
impact, response, attribution, or other. Use other when no narrower category
applies. Status may use unknown only when the user's epistemic qualification is
unresolved. A direct assertion in new_user_message uses status reported unless
the user expresses uncertainty; reported records provenance, not verification.
Confidence may use unknown when confidence is not supplied.
Evidence source_type must be user_reported.
Never set a required field to null.
The value object is closed: use only the known Case State field names and set unrelated fields to null.
For MODIFY, provide one existing stable target ID and field, copy the exact current field
value into old_value, and put the corrected primitive or primitive-list value in new_value.
Do not remove items or fields. Do not return provenance or a complete Case State.
Return only the delta supported by the new_user_message.
"""
