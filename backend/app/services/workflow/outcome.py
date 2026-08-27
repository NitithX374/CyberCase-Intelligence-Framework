from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, replace
from uuid import UUID

from app.services.case_analysis import CASE_ANALYSIS_PROMPT_VERSION
from app.services.case_analysis.contracts import (
    AnalysisTraceFailure,
    ValidatedAnalysisTrace,
)
from app.schemas.rag import QueryResponse


@dataclass(frozen=True)
class RagContextPayload:
    retrieval_context_id: str
    context: str
    mitre_table: tuple[dict[str, object], ...]

    def to_analysis_context(self) -> dict[str, object]:
        return {
            "retrieved_context": self.context,
            "retrieval_context_id": self.retrieval_context_id,
            "mitre_table": deepcopy(list(self.mitre_table)),
        }


@dataclass(frozen=True)
class AssistantOutcome:
    content: str
    retrieval_context_id: str | None
    metadata_json: dict[str, object]
    thread_status: str
    rag_context_payload: RagContextPayload | None = None
    analysis_trace_draft: ValidatedAnalysisTrace | None = None
    analysis_trace_failure: AnalysisTraceFailure | None = None
    evidence_sha256: str | None = None
    source_message_ids: tuple[UUID, ...] = ()


def map_rag_response(response: QueryResponse) -> dict[str, object]:
    return {
        "retrieved_context": response.context,
        "retrieval_context_id": response.retrieval_context_id,
        "mitre_table": [row.model_dump(mode="json") for row in response.mitre_table],
        "previous_analysis": None,
    }


def validated_rag_context_payload(response: QueryResponse) -> RagContextPayload:
    retrieval_id = response.retrieval_context_id
    context = response.context
    mitre_table = response.mitre_table
    if not isinstance(retrieval_id, str) or not retrieval_id.strip():
        raise ValueError("RAG response has no retrieval context identifier")
    if not isinstance(context, str):
        raise ValueError("RAG response context is invalid")
    if not isinstance(mitre_table, list):
        raise ValueError("RAG response MITRE table is invalid")
    normalized_rows = [
        row if isinstance(row, dict) else row.model_dump(mode="json")
        for row in mitre_table
    ]
    return RagContextPayload(
        retrieval_context_id=retrieval_id.strip(),
        context=context,
        mitre_table=tuple(deepcopy(normalized_rows)),
    )


_validated_rag_context_payload = validated_rag_context_payload


def fresh_analysis_outcome(
    answer: str,
    *,
    action: str,
    rag_context: RagContextPayload,
    evidence_sha256: str,
    source_message_ids: tuple[UUID, ...],
    followup_metadata: dict[str, object],
    trace: ValidatedAnalysisTrace | None,
    trace_failure: AnalysisTraceFailure | None,
) -> AssistantOutcome:
    metadata = deepcopy(followup_metadata)
    metadata.update(
        {
            "analysis_kind": "grounded_main_analysis",
            "mitre_table": deepcopy(list(rag_context.mitre_table)),
            "evidence_sha256": evidence_sha256,
            "source_message_ids": [str(value) for value in source_message_ids],
            "chat_action": {
                "action": action,
                "route": "analysis",
                "rag_invoked": True,
                "retrieval_context_reused": False,
                "analysis_mode": "case_overview",
                "prompt_version": CASE_ANALYSIS_PROMPT_VERSION,
            },
        }
    )
    return AssistantOutcome(
        content=answer.strip(),
        retrieval_context_id=rag_context.retrieval_context_id,
        metadata_json=metadata,
        thread_status="answered",
        rag_context_payload=rag_context,
        analysis_trace_draft=trace,
        analysis_trace_failure=trace_failure,
        evidence_sha256=evidence_sha256,
        source_message_ids=source_message_ids,
    )


def question_outcome(
    answer: str,
    *,
    analysis_context: dict[str, object],
    evidence_sha256: str,
    source_message_ids: tuple[UUID, ...],
    trace: ValidatedAnalysisTrace | None,
    trace_failure: AnalysisTraceFailure | None,
) -> AssistantOutcome:
    retrieval_id = analysis_context.get("retrieval_context_id")
    if not isinstance(retrieval_id, str) or not retrieval_id:
        raise ValueError("ASK requires a retrieval context identifier")
    mitre_table = analysis_context.get("mitre_table", [])
    return AssistantOutcome(
        content=answer.strip(),
        retrieval_context_id=retrieval_id,
        metadata_json={
            "mitre_table": deepcopy(mitre_table if isinstance(mitre_table, list) else []),
            "evidence_sha256": evidence_sha256,
            "source_message_ids": [str(value) for value in source_message_ids],
            "chat_action": {
                "action": "ask",
                "route": "analysis",
                "rag_invoked": False,
                "retrieval_context_reused": True,
                "analysis_mode": "question_answer",
                "prompt_version": CASE_ANALYSIS_PROMPT_VERSION,
            },
        },
        thread_status="answered",
        analysis_trace_draft=trace,
        analysis_trace_failure=trace_failure,
        evidence_sha256=evidence_sha256,
        source_message_ids=source_message_ids,
    )


def bind_followup_question(
    outcome: AssistantOutcome,
    *,
    rag_context: RagContextPayload,
    evidence_sha256: str,
    source_message_ids: tuple[UUID, ...],
) -> AssistantOutcome:
    metadata = deepcopy(outcome.metadata_json)
    metadata.update(
        {
            "mitre_table": deepcopy(list(rag_context.mitre_table)),
            "evidence_sha256": evidence_sha256,
            "source_message_ids": [str(value) for value in source_message_ids],
        }
    )
    return replace(
        outcome,
        retrieval_context_id=rag_context.retrieval_context_id,
        metadata_json=metadata,
        rag_context_payload=rag_context,
        evidence_sha256=evidence_sha256,
        source_message_ids=source_message_ids,
    )


__all__ = [
    "AssistantOutcome",
    "RagContextPayload",
    "_validated_rag_context_payload",
    "bind_followup_question",
    "fresh_analysis_outcome",
    "map_rag_response",
    "question_outcome",
    "validated_rag_context_payload",
]
