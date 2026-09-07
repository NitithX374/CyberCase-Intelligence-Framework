from typing import Literal

from pydantic import ConfigDict, TypeAdapter
from typing_extensions import TypedDict

from app.schemas.document_sources import CaseNarrativeDocumentPageSpan


class DocumentSourceMetadata(TypedDict, total=False):
    __pydantic_config__ = ConfigDict(extra="allow")
    document_id: str
    filename: str
    page_count: int
    extraction_method: str
    verification_status: str
    confidence_status: str
    minimum_confidence: float | None
    warnings: list[str]
    page_spans: list[CaseNarrativeDocumentPageSpan]


class ChatActionMetadata(TypedDict, total=False):
    __pydantic_config__ = ConfigDict(extra="allow")
    action: Literal["initial_analysis", "ask", "add_case_info"]
    route: str
    rag_invoked: bool
    retrieval_context_reused: bool
    analysis_mode: Literal["case_overview", "question_answer"]
    prompt_version: str


class RagAttemptMetadata(TypedDict, total=False):
    __pydantic_config__ = ConfigDict(extra="allow")
    status: Literal["used", "no_applicable_context", "unavailable"]
    failure_code: str | None


class FollowUpMetadata(TypedDict, total=False):
    __pydantic_config__ = ConfigDict(extra="allow")
    kind: Literal["clarification", "decision"]
    action: Literal["ask_followup", "proceed"]
    question: str
    reason_code: str
    source_run_id: str
    root_ordinal: int
    round: int
    prior_exchange_count: int
    followup_context: dict[str, str] | None
    gap_analysis: dict[str, object]
    rag_invoked: bool
    rag_skipped: bool
    failure_code: str | None


class MessageMetadata(TypedDict, total=False):
    __pydantic_config__ = ConfigDict(extra="allow")
    evidence_kind: Literal[
        "initial_case_narrative",
        "clarification_answer",
        "added_case_information",
        "analyst_question",
    ]
    document_sources: list[DocumentSourceMetadata]
    clarification_context: dict[str, str]
    analysis_kind: str
    analysis_state_scope: Literal["canonical_case_overview", "response_scoped"]
    canonical_case_state: bool
    evidence_sha256: str
    source_message_ids: list[str]
    analysis_trace: dict[str, object]
    analysis_trace_failure: dict[str, object]
    mitre_table: list[dict[str, object]]
    mitre_applicability: dict[str, object]
    chat_action: ChatActionMetadata
    chat_followup: FollowUpMetadata
    rag_attempt: RagAttemptMetadata


_metadata_adapter = TypeAdapter(MessageMetadata)


def serialize_message_metadata(value: dict[str, object]) -> dict[str, object]:
    validated = _metadata_adapter.validate_python(value)
    return _metadata_adapter.dump_python(validated, mode="json")
