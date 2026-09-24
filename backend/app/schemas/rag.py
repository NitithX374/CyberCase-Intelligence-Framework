from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class QueryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str
    use_agent: bool = True


class MitreTableRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    technique_id: str = ""
    name: str
    entity_type: str = ""
    tactic: str | None = None
    score: float | None = None
    source: Literal["vector", "graph"] = "vector"
    relevance: Literal["cited_in_answer", "retrieved_only"] = "retrieved_only"
    description: str = ""
    mitre_url: str | None = None


class LegalProvision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    citation: str = ""
    title: str = ""
    text: str = ""
    url: str = ""
    score: float | None = None


class LegalReferenceResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provisions: list[LegalProvision] = Field(default_factory=list)
    provider: str = ""
    query_sent: str = ""
    degraded: str = ""
    disclaimer: str = ""


class QueryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["completed"]
    retrieval_context_id: str | None
    context: str
    mitre_table: list[MitreTableRow] = Field(default_factory=list)
    legal_reference: LegalReferenceResult

    @field_validator("retrieval_context_id", mode="before")
    @classmethod
    def normalize_empty_retrieval_context_id(cls, value: Any) -> Any:
        return None if value == "" else value


__all__ = [
    "LegalProvision",
    "LegalReferenceResult",
    "MitreTableRow",
    "QueryRequest",
    "QueryResponse",
]
