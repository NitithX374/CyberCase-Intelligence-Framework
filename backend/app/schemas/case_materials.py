"""HTTP contracts for Case materials and received Case sources."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DocumentExtractionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_id: UUID
    provider: str
    config_json: dict[str, object]
    extracted_text: str
    provenance_json: dict[str, object]
    warnings_json: list[object]
    created_at: datetime


class CaseDocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    case_id: UUID
    filename: str
    mime_type: str
    size_bytes: int
    archived_at: datetime | None
    created_at: datetime
    extractions: list[DocumentExtractionRead] = Field(default_factory=list)


class CaseEvidenceCreate(BaseModel):
    model_config = ConfigDict(title="CaseEvidenceCreate")

    exact_text: str = Field(min_length=1, max_length=400_000)
    provenance_json: dict[str, object] = Field(default_factory=dict)
    source_kind: Literal["narrative", "followup_answer"] = "narrative"
    source_metadata_json: dict[str, object] = Field(default_factory=dict)


class EvidenceSourceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, title="EvidenceSourceRead")

    id: UUID
    case_id: UUID
    source_kind: str
    document_id: UUID | None
    origin_message_id: UUID | None
    exact_text: str
    provenance_json: dict[str, object] = Field(default_factory=dict)
    source_metadata_json: dict[str, object] = Field(default_factory=dict)
    created_at: datetime
    archived_at: datetime | None


CaseSourceCreate = CaseEvidenceCreate
CaseSourceRead = EvidenceSourceRead


__all__ = [
    "CaseDocumentRead",
    "CaseEvidenceCreate",
    "CaseSourceCreate",
    "DocumentExtractionRead",
    "EvidenceSourceRead",
    "CaseSourceRead",
]
