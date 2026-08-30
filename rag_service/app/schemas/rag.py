from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from RAG import MitreTableRow
from RAG.legal_reference import LegalReferenceResult


class QueryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str
    # Vestigial: GraphRAGAgent is the only pipeline, so this selects nothing.
    # It cannot be deleted unilaterally — extra="forbid" above means dropping
    # the field turns the backend's existing `use_agent: true` payload
    # (services/chat/rag_client.py) into a 422 on every chat request. Remove it
    # here and in backend/app/schemas/chat/rag.py in the same change, or not
    # at all.
    use_agent: bool = True


class QueryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # Always "completed" — the pipeline no longer pauses for clarification.
    status: Literal["completed"]
    retrieval_context_id: str | None
    context: str
    # MITRE ATT&CK mapping table selected inside rag-service. The generated
    # answer may be used internally for relevance, but never crosses this
    # response boundary.
    mitre_table: list[MitreTableRow] = Field(default_factory=list)
    # Thai provisions that may bear on the incident, from an external legal
    # service. A third output beside the context and the MITRE table, never a
    # replacement for either — and references rather than recommendations: the
    # service reports what may be relevant, and whether it applies is the
    # reader's judgement. Arrives empty with `degraded` set when the provider
    # is unset or unreachable, so a lookup failure cannot cost the MITRE table.
    legal_reference: LegalReferenceResult = Field(default_factory=LegalReferenceResult)

    @field_validator("retrieval_context_id", mode="before")
    @classmethod
    def normalize_empty_retrieval_context_id(cls, value: Any) -> Any:
        return None if value == "" else value


class RetrievalContextSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    retrieval_context_id: str
    query: str = ""
    context: str
    rag_result: dict[str, Any] = Field(default_factory=dict)
    mitre_table: list[MitreTableRow] = Field(default_factory=list)
