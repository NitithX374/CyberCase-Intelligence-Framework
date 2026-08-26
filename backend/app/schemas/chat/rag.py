from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RagQueryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str
    use_agent: bool = True


class QueryRequest(RagQueryRequest):
    pass


class MitreTableRow(BaseModel):
    """One entry of the MITRE mapping table produced by the RAG service."""

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


class LegalSectionRef(BaseModel):
    """One statute section quoted verbatim, mirrored from the RAG service.

    The qualifiers travel with the text on purpose: a section that arrives
    without `verified_by_human` is indistinguishable from a checked one.
    """

    model_config = ConfigDict(extra="forbid")

    citation: str
    act_label: str
    section_number: str
    text: str
    hierarchy: list[str] = Field(default_factory=list)
    verified_by_human: bool = False
    verification: str = "current_unverified"
    penalties_quotable: bool = True
    effective_from: str | None = None
    effective_note: str = ""
    date_warning: str = ""
    source_url: str = ""


class LegalSuggestion(BaseModel):
    """A section an incident may fall under — a suggestion, never a finding."""

    model_config = ConfigDict(extra="forbid")

    headline: str
    section: LegalSectionRef
    reasoning: str = ""
    from_techniques: list[str] = Field(default_factory=list)
    related: list[LegalSectionRef] = Field(default_factory=list)


class LegalResult(BaseModel):
    """Statute suggestions, or an explanation of why there are none."""

    model_config = ConfigDict(extra="forbid")

    suggestions: list[LegalSuggestion] = Field(default_factory=list)
    degraded: str = ""
    contains_unverified: bool = True
    disclaimer: str = ""


class QueryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["completed"]
    retrieval_context_id: str | None
    context: str
    mitre_table: list[MitreTableRow] = Field(default_factory=list)
    # Must stay in step with rag_service/app/schemas/rag.py: both models set
    # extra="forbid", so a field added on one side alone turns every chat
    # request into a 422 here.
    legal: LegalResult = Field(default_factory=LegalResult)

    @field_validator("retrieval_context_id", mode="before")
    @classmethod
    def normalize_empty_retrieval_context_id(cls, value: Any) -> Any:
        """Treat the RAG service's empty-string sentinel as no frozen context."""

        return None if value == "" else value


__all__ = [
    "LegalResult",
    "LegalSectionRef",
    "LegalSuggestion",
    "MitreTableRow",
    "QueryRequest",
    "QueryResponse",
    "RagQueryRequest",
]
