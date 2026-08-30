from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from backend.experiments.ctinexus.schemas import PredictedGraph


class TypedEntityPrediction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1)
    entity_type: str = Field(min_length=1)
    start: int | None = None
    end: int | None = None
    confidence: float | None = None


class TypedRelationPrediction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subject: str = Field(min_length=1)
    relation: str = Field(min_length=1)
    object: str = Field(min_length=1)
    subject_start: int | None = None
    subject_end: int | None = None
    relation_start: int | None = None
    relation_end: int | None = None
    object_start: int | None = None
    object_end: int | None = None
    confidence: float | None = None


class ExtractorPrediction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    condition: str
    doc_id: str
    narrative_sha256: str
    model: str
    status: str
    graph: PredictedGraph
    typed_entities: list[TypedEntityPrediction] = Field(default_factory=list)
    typed_relations: list[TypedRelationPrediction] = Field(default_factory=list)
    diagnostics: dict[str, Any] = Field(default_factory=dict)
    contract: dict[str, Any] = Field(default_factory=dict)
