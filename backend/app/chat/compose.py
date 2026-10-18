from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

from app.analysis.language import ResponseLanguage
from app.analysis.reading_sources import provider_source_payload
from app.analysis.technical_context.contracts import CaseRagContextPayload
from app.chat.answer_contract import CaseAnalysisOutput, ChatReply
from app.chat.grounding import answer_from
from app.config import settings
from app.llm.prompt_files import prompt_template
from app.llm.request import request_stage
from app.llm.settings import configured_pipeline
from app.models.analysis_result import CaseAnalysisResult
from app.models.chat_message import ChatMessage
from app.sources.bundle import CaseSourceBundle
from app.trace.claims import (
    CLAIM_FIELDS_HIDDEN_FROM_MODELS,
    CaseFollowupExchange,
    followup_payload,
)
from app.trace.trace import CaseAnalysisTrace

AnalysisStatus = Literal["none", "current", "stale"]
CHAT_OUTPUT_TOKENS = 4_096


CHAT_PROMPT = prompt_template(__file__, "answer") + "\n"


async def generate_case_answer(
    *,
    result: CaseAnalysisResult | None,
    question: str,
    history: list[ChatMessage],
    sources: CaseSourceBundle,
    language: ResponseLanguage,
    followups: Sequence[CaseFollowupExchange] = (),
    technical_context: CaseRagContextPayload | None = None,
    analysis_status: AnalysisStatus = "none",
) -> CaseAnalysisOutput:
    trace = CaseAnalysisTrace.model_validate(result.trace_json) if result is not None else None
    reply = await request_stage(
        config=configured_pipeline().model_copy(
            update={"output_tokens": CHAT_OUTPUT_TOKENS, "thinking_tokens": 0}
        ),
        stage="chat_answer",
        system=CHAT_PROMPT,
        content=chat_request(
            question=question,
            history=history,
            sources=sources,
            language=language,
            followups=followups,
            technical_context=technical_context,
            analysis_status=analysis_status,
            trace=trace,
            summary=result.summary if result is not None else None,
        ),
        schema=ChatReply,
        attempts=settings.chat_stage_attempts,
    )
    return answer_from(reply, trace, sources, followups, language)


def chat_request(
    *,
    question: str,
    history: list[ChatMessage],
    sources: CaseSourceBundle,
    language: ResponseLanguage,
    followups: Sequence[CaseFollowupExchange],
    technical_context: CaseRagContextPayload | None,
    analysis_status: AnalysisStatus,
    trace: CaseAnalysisTrace | None,
    summary: str | None,
) -> dict[str, object]:
    return {
        "response_language": language,
        "question": question,
        "analysis_status": analysis_status,
        "analysis": analysis_payload(trace, summary) if trace is not None else None,
        "followup_history": followup_payload(followups),
        "technical_context": technical_context_payload(technical_context),
        "case_sources": [provider_source_payload(source) for source in sources.sources],
        "conversation_history": [
            {"id": str(message.id), "role": message.role, "content": message.content}
            for message in history
            if message.content.strip()
        ],
    }


def technical_context_payload(
    technical_context: CaseRagContextPayload | None,
) -> dict[str, object] | None:
    if technical_context is None:
        return None
    return {
        "context": technical_context.context,
        "mitre_table": list(technical_context.mitre_table),
    }


def analysis_payload(trace: CaseAnalysisTrace, summary: str | None) -> dict[str, object]:
    return {
        "summary": summary or trace.summary,
        "claims": [
            claim.model_dump(mode="json", exclude=CLAIM_FIELDS_HIDDEN_FROM_MODELS)
            for claim in trace.claims
        ],
        "mitre_associations": [
            association.model_dump(mode="json") for association in trace.mitre_associations
        ],
        "gaps": [
            {"topic": gap.topic, "status": gap.status, "description": gap.description}
            for gap in trace.gaps
        ],
    }


__all__ = ["generate_case_answer"]
