from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CaseDocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    case_id: UUID
    filename: str
    mime_type: str
    size_bytes: int
    created_at: datetime


def contains_nul(value: object) -> bool:
    if isinstance(value, str):
        return "\x00" in value
    if isinstance(value, dict):
        return any(contains_nul(key) or contains_nul(item) for key, item in value.items())
    if isinstance(value, list):
        return any(contains_nul(item) for item in value)
    return False


class CaseSourceCreate(BaseModel):
    exact_text: str = Field(min_length=1, max_length=250_000)
    provenance_json: dict[str, object] = Field(default_factory=dict)
    source_kind: Literal["narrative"] = "narrative"
    source_metadata_json: dict[str, object] = Field(default_factory=dict)

    @model_validator(mode="after")
    def refuse_nul_in_records(self) -> CaseSourceCreate:
        if contains_nul(self.provenance_json) or contains_nul(self.source_metadata_json):
            raise ValueError("provenance_json and source_metadata_json cannot contain NUL")
        return self


class CaseSourceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    case_id: UUID
    source_kind: str
    document_id: UUID | None
    filename: str | None = None
    mime_type: str | None = None
    size_bytes: int | None = None
    exact_text: str
    provenance_json: dict[str, object] = Field(default_factory=dict)
    source_metadata_json: dict[str, object] = Field(default_factory=dict)
    created_at: datetime


__all__ = [
    "CaseDocumentRead",
    "CaseSourceCreate",
    "CaseSourceRead",
]
