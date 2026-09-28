from __future__ import annotations

import logging
from collections.abc import Iterable, Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
from typing import Literal

from fastapi import status
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from app.analysis.language import ResponseLanguage
from app.analysis.technical_context.contracts import CaseRagContextPayload
from app.analysis.write import write_request
from app.chat.contracts import CaseAnalysisOutput
from app.chat.prompts import CHAT_PROMPT
from app.errors import CaseAnalysisFailure
from app.llm.request import request_stage
from app.llm.settings import configured_pipeline
from app.models.analysis_result import CaseAnalysisResult
from app.models.chat_message import ChatMessage
from app.sources.bundle import CaseSourceBundle, CaseSourceItem, build_document_source_context
from app.trace.bind import (
    QuoteSearch,
    followup_registry_items,
    resolve_case_trace,
    resolved_citations,
)
from app.trace.claims import (
    CaseAnalysisClaim,
    CaseFollowupExchange,
    CaseSourceCitation,
    normalize_identifier,
)
from app.trace.messages import ChatAnswerUnit
from app.trace.trace import MAX_SUMMARY_CHARS, CaseAnalysisTrace

logger = logging.getLogger(__name__)

AnalysisStatus = Literal["none", "current", "stale"]
BASES = ("case_fact", "interpretation", "technical", "general")
CHAT_OUTPUT_TOKENS = 4_096
SUGGESTIONS = ("none", "add_source", "run_analysis")


UNANSWERED = {
    "thai": "ยังตอบคำถามนี้จากข้อมูลของคดีไม่ได้ ลองถามใหม่อีกครั้ง หรือเพิ่มข้อมูลที่หน้า Sources",
    "english": (
        "This question could not be answered from the case material. "
        "Ask again, or add material on the Sources page."
    ),
}


class ChatReplyQuote(BaseModel):
    model_config = ConfigDict(extra="ignore")

    source_id: str = ""
    exact_quote: str = ""


class ChatReplyUnit(BaseModel):
    model_config = ConfigDict(extra="ignore")

    text: str = ""
    basis: Literal["case_fact", "interpretation", "technical", "general"] = "case_fact"
    claim_ids: list[str] = Field(default_factory=list)
    quotes: list[ChatReplyQuote] = Field(default_factory=list)

    @field_validator("text", mode="before")
    @classmethod
    def text_or_nothing(cls, value: object) -> object:
        return value if isinstance(value, str) else ""

    @field_validator("basis", mode="before")
    @classmethod
    def known_basis(cls, value: object) -> str:
        basis = str(value or "").strip().lower()
        return basis if basis in BASES else "case_fact"

    @field_validator("claim_ids", mode="before")
    @classmethod
    def claim_id_strings(cls, value: object) -> list[str]:
        if isinstance(value, str):
            value = [value]
        if not isinstance(value, (list, tuple)):
            return []
        return [item for item in value if isinstance(item, str) and item.strip()]

    @field_validator("quotes", mode="before")
    @classmethod
    def quote_records(cls, value: object) -> list[object]:
        if not isinstance(value, (list, tuple)):
            return []
        return [item for item in value if isinstance(item, Mapping)]


class ChatReply(BaseModel):
    model_config = ConfigDict(extra="ignore")

    units: list[ChatReplyUnit] = Field(default_factory=list)
    suggestion: Literal["none", "add_source", "run_analysis"] = "none"

    @field_validator("units", mode="before")
    @classmethod
    def unit_records(cls, value: object) -> list[object]:
        if not isinstance(value, (list, tuple)):
            return []
        return [item for item in value if isinstance(item, Mapping)]

    @field_validator("suggestion", mode="before")
    @classmethod
    def known_suggestion(cls, value: object) -> str:
        suggestion = str(value or "").strip().lower()
        return suggestion if suggestion in SUGGESTIONS else "none"


@dataclass(frozen=True)
class DraftUnit:
    text: str
    basis: str
    claim_ids: tuple[str, ...]
    quotes: tuple[CaseSourceCitation, ...]
    offered_quotes: int


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
    material = write_request(sources, language, followups, technical_context)
    return {
        "response_language": material["response_language"],
        "question": question,
        "analysis_status": analysis_status,
        "analysis": analysis_payload(trace, summary) if trace is not None else None,
        "followup_history": material["followup_history"],
        "technical_context": material["technical_context"],
        "case_sources": material["case_sources"],
        "conversation_history": [
            {"id": str(message.id), "role": message.role, "content": message.content}
            for message in history
            if message.content.strip()
        ],
    }


def analysis_payload(trace: CaseAnalysisTrace, summary: str | None) -> dict[str, object]:
    return {
        "summary": summary or trace.summary,
        "claims": [claim.model_dump(mode="json") for claim in trace.claims],
        "involved_parties": [party.model_dump(mode="json") for party in trace.involved_parties],
        "timeline": [item.model_dump(mode="json") for item in trace.timeline],
        "impacts": [impact.model_dump(mode="json") for impact in trace.impacts],
        "mitre_associations": [
            association.model_dump(mode="json") for association in trace.mitre_associations
        ],
        "gaps": [
            {"topic": gap.topic, "status": gap.status, "description": gap.description}
            for gap in trace.gaps
        ],
    }


def answer_from(
    reply: ChatReply,
    trace: CaseAnalysisTrace | None,
    sources: CaseSourceBundle,
    followups: Sequence[CaseFollowupExchange],
    language: ResponseLanguage,
) -> CaseAnalysisOutput:
    claims = {claim.claim_id: claim for claim in trace.claims} if trace is not None else {}
    registry: dict[str, CaseSourceItem] = {source.source_id: source for source in sources.sources}
    registry.update({item.source_id: item for item in followup_registry_items(followups)})
    document_context = build_document_source_context(sources)
    search = QuoteSearch(registry)
    drafts = [
        draft
        for draft in (
            drafted_unit(item, claims, registry, document_context, search) for item in reply.units
        )
        if draft is not None
    ]
    answer = "\n\n".join(draft.text for draft in drafts) or UNANSWERED[language]
    if len(answer) > MAX_SUMMARY_CHARS:
        raise CaseAnalysisFailure(
            "chat_answer_invalid",
            "The chat answer is longer than one message can hold",
            status.HTTP_502_BAD_GATEWAY,
        )
    selected = list(dict.fromkeys(claim_id for draft in drafts for claim_id in draft.claim_ids))
    answer_trace = (
        resolve_case_trace(
            CaseAnalysisTrace(
                analysis_mode="question_answer",
                summary=answer,
                claims=[deepcopy(claims[claim_id]) for claim_id in selected],
            ),
            sources,
            followup_history=followups,
        )
        if selected
        else None
    )
    bound = {claim.claim_id: claim for claim in answer_trace.claims} if answer_trace else {}
    units = tuple(finished_unit(draft, bound) for draft in drafts)
    log_grounding(drafts, units)
    return CaseAnalysisOutput(
        answer=answer, trace=answer_trace, units=units, suggestion=reply.suggestion
    )


def drafted_unit(
    item: ChatReplyUnit,
    claims: Mapping[str, CaseAnalysisClaim],
    registry: dict[str, CaseSourceItem],
    document_context: object,
    search: QuoteSearch,
) -> DraftUnit | None:
    text = item.text.strip()
    if not text:
        return None
    claim_ids = tuple(
        dict.fromkeys(
            claim_id
            for claim_id in (
                normalize_identifier(value, "A", "A|claim|c") for value in item.claim_ids
            )
            if claim_id in claims
        )
    )
    offered: list[CaseSourceCitation] = []
    for quote in item.quotes:
        try:
            offered.append(
                CaseSourceCitation(source_id=quote.source_id, exact_quote=quote.exact_quote)
            )
        except ValidationError:
            continue
    quotes = tuple(resolved_citations(offered, registry, document_context, search))
    return DraftUnit(text, item.basis, claim_ids, quotes, len(item.quotes))


def finished_unit(draft: DraftUnit, bound: Mapping[str, CaseAnalysisClaim]) -> ChatAnswerUnit:
    cited = [bound[claim_id] for claim_id in draft.claim_ids if claim_id in bound]
    supporting = unique_citations(
        [*draft.quotes, *(citation for claim in cited for citation in claim.supporting_citations)]
    )
    contradicting = unique_citations(
        [citation for claim in cited for citation in claim.contradicting_citations]
    )
    return ChatAnswerUnit(
        text=draft.text,
        basis=draft.basis,
        claim_ids=[claim.claim_id for claim in cited],
        supporting_source_ids=unique(
            [
                *(citation.source_id for citation in supporting),
                *(source_id for claim in cited for source_id in claim.supporting_source_ids),
            ]
        ),
        supporting_citations=supporting,
        contradicting_source_ids=unique(
            [
                *(citation.source_id for citation in contradicting),
                *(source_id for claim in cited for source_id in claim.contradicting_source_ids),
            ]
        ),
        contradicting_citations=contradicting,
    )


def unique(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(values))


def unique_citations(citations: Iterable[CaseSourceCitation]) -> list[CaseSourceCitation]:
    kept: dict[tuple[str, str], CaseSourceCitation] = {}
    for citation in citations:
        kept.setdefault((citation.source_id, citation.exact_quote), citation)
    return list(kept.values())


def log_grounding(drafts: Sequence[DraftUnit], units: Sequence[ChatAnswerUnit]) -> None:
    facts = [unit for unit in units if unit.basis == "case_fact"]
    cited = [unit for unit in facts if unit.claim_ids or unit.cited]
    logger.info(
        "Chat answer grounding: %d units, %d case facts (%d cited, %d uncited), "
        "%d interpretation, %d technical, %d general, quotes %d offered %d verified",
        len(units),
        len(facts),
        len(cited),
        len(facts) - len(cited),
        sum(unit.basis == "interpretation" for unit in units),
        sum(unit.basis == "technical" for unit in units),
        sum(unit.basis == "general" for unit in units),
        sum(draft.offered_quotes for draft in drafts),
        sum(len(draft.quotes) for draft in drafts),
    )


__all__ = [
    "CHAT_OUTPUT_TOKENS",
    "ChatReply",
    "generate_case_answer",
]
