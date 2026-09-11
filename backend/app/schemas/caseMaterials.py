"""HTTP contracts for Case materials and admitted evidence."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DocumentExtractionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_id: UUID
    revision: int
    provider: str
    config_json: dict[str, object]
    extracted_text: str
    text_sha256: str
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
    content_sha256: str
    archived_at: datetime | None
    created_at: datetime
    extractions: list[DocumentExtractionRead] = Field(default_factory=list)


class AdmitExtractionRequest(BaseModel):
    extraction_id: UUID


class EvidenceRevisionCreate(BaseModel):
    exact_text: str = Field(min_length=1, max_length=400_000)
    provenance_json: dict[str, object] = Field(default_factory=dict)


class CaseEvidenceCreate(EvidenceRevisionCreate):
    source_kind: Literal["narrative", "clarification_answer", "explicit_chat_addition"] = "narrative"
    source_metadata_json: dict[str, object] = Field(default_factory=dict)


class EvidenceRevisionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source_id: UUID
    revision: int
    exact_text: str
    text_sha256: str
    provenance_json: dict[str, object]
    extraction_id: UUID | None
    admitted_at: datetime
    archived_at: datetime | None


class EvidenceSourceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    case_id: UUID
    source_kind: str
    document_id: UUID | None
    origin_message_id: UUID | None
    source_metadata_json: dict[str, object]
    created_at: datetime
    archived_at: datetime | None
    revisions: list[EvidenceRevisionRead] = Field(default_factory=list)


class CaseEvidenceSnapshotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    case_id: UUID
    evidence_revision: int
    format_version: str
    manifest_json: list[object]
    input_text: str
    text_sha256: str
    manifest_sha256: str
    created_at: datetime


__all__ = [
    "AdmitExtractionRequest",
    "CaseEvidenceCreate",
    "CaseDocumentRead",
    "CaseEvidenceSnapshotRead",
    "DocumentExtractionRead",
    "EvidenceRevisionCreate",
    "EvidenceRevisionRead",
    "EvidenceSourceRead",
]
