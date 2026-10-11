from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator
from RAG import MitreTableRow
from RAG.legal_reference import LegalReferenceResult


def _not_blank(value: str) -> str:
    if not value.strip():
        raise ValueError("must not be blank")
    return value


class OpenConversationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # The case file: the incident as the reader has it, in Thai or English.
    case_file: str = Field(max_length=60_000)

    _case_file_not_blank = field_validator("case_file")(_not_blank)


class MessageRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(max_length=20_000)
    # The reader says which it is. A question is answered from the analysis
    # that exists; facts are appended to the case file, which is then analysed
    # again — a minute of work that also rewrites the table, so it is never
    # inferred from the wording.
    kind: Literal["question", "facts"] = "question"

    _text_not_blank = field_validator("text")(_not_blank)


class TurnView(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: Literal["user", "assistant"]
    kind: Literal["case", "facts", "question", "analysis", "answer"]
    text: str
    created_at: float
    seconds: float = 0.0
    # What an answer rests on beyond the case's own analysis: searches of the
    # ATT&CK knowledge base, and entities read by the ID the reader named.
    # Both empty means it was answered from the case file and its analysis.
    lookup_queries: list[str] = Field(default_factory=list)
    lookup_ids: list[str] = Field(default_factory=list)
    # A repeated analysis: rows of the table that came and went.
    rows_added: list[str] = Field(default_factory=list)
    rows_removed: list[str] = Field(default_factory=list)


class AnalysisView(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # The text that was analysed — the case file plus any added facts. Each
    # row's evidence offsets index into this string.
    case_text: str
    # Unlike POST /query, the written analysis is returned: here the reader is
    # the one who asked for it, there is no backend writing its own.
    answer: str
    mitre_table: list[MitreTableRow] = Field(default_factory=list)
    legal_reference: LegalReferenceResult | None = None


class ConversationView(BaseModel):
    model_config = ConfigDict(extra="forbid")

    conversation_id: str
    created_at: float
    analysis: AnalysisView
    turns: list[TurnView]


class MessageResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    conversation_id: str
    reply: TurnView
    # Set when the message changed the analysis (added facts); absent for a
    # question, which leaves the analysis and the table as they were.
    analysis: AnalysisView | None = None
