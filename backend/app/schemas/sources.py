from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CaseDocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    case_id: UUID
    filename: str
    mime_type: str
    size_bytes: int
    created_at: datetime


class CaseSourceCreate(BaseModel):
    exact_text: str = Field(min_length=1, max_length=400_000)
    provenance_json: dict[str, object] = Field(default_factory=dict)
    source_kind: Literal["narrative"] = "narrative"
    source_metadata_json: dict[str, object] = Field(default_factory=dict)


class CaseSourceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    case_id: UUID
    source_kind: str
    document_id: UUID | None
    filename: str | None = None
    exact_text: str
    provenance_json: dict[str, object] = Field(default_factory=dict)
    source_metadata_json: dict[str, object] = Field(default_factory=dict)
    created_at: datetime
    archived_at: datetime | None


__all__ = [
    "CaseDocumentRead",
    "CaseSourceCreate",
    "CaseSourceRead",
]
