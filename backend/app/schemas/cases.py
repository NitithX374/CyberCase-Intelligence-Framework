from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import AfterValidator, BaseModel, ConfigDict, Field

from app.schemas.analysis import AnalysisFreshness


def without_nul(title: str) -> str:
    title = title.replace("\x00", "")
    if not title:
        raise ValueError("A case title needs at least one character")
    return title


CaseTitle = Annotated[str, Field(min_length=1, max_length=255), AfterValidator(without_nul)]


class CaseCreate(BaseModel):
    title: CaseTitle = "New case"


class CaseUpdate(BaseModel):
    title: CaseTitle


class CaseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID | None = None
    title: str
    source_revision: int = 0
    latest_analysis_result_id: UUID | None = None
    analysis_freshness: AnalysisFreshness = "missing"
    created_at: datetime
    updated_at: datetime


__all__ = [
    "CaseCreate",
    "CaseRead",
    "CaseUpdate",
]
