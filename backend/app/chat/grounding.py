from __future__ import annotations

import logging
import re
from collections.abc import Iterable, Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass

from fastapi import status

from app.analysis.language import ResponseLanguage
from app.chat.answer_contract import CaseAnalysisOutput, ChatReply, ChatReplyUnit
from app.errors import CaseAnalysisFailure
from app.sources.bundle import CaseSourceBundle, CaseSourceItem
from app.trace.bind import followup_registry_items, resolve_case_trace
from app.trace.claims import (
    CaseAnalysisClaim,
    CaseFollowupExchange,
    CaseSourceCitation,
    normalize_identifier,
)
from app.trace.messages import ChatAnswerUnit
from app.trace.quotes import find_document_locator
from app.trace.trace import MAX_SUMMARY_CHARS, CaseAnalysisTrace

logger = logging.getLogger("app.chat.compose")


UNANSWERED = {
    "thai": "ยังตอบคำถามนี้จากข้อมูลของคดีไม่ได้ ลองถามใหม่อีกครั้ง หรือเพิ่มข้อมูลที่หน้า Sources",
    "english": (
        "This question could not be answered from the case material. "
        "Ask again, or add material on the Sources page."
    ),
}

INLINE_CITATION_PATTERN = re.compile(
    r"\s*\[\s*(?:(?:A|QA|C)-\d+|[A-Z]\d+)(?:\s*[,;]\s*(?:(?:A|QA|C)-\d+|[A-Z]\d+))*\s*\]",
    re.IGNORECASE,
)


def strip_inline_citations(text: str) -> str:
    cleaned = INLINE_CITATION_PATTERN.sub("", text)
    cleaned = re.sub(r" +", " ", cleaned)
    cleaned = re.sub(r" ([.,;:!?])", r"\1", cleaned)
    return cleaned.strip()


@dataclass(frozen=True)
class DraftUnit:
    text: str
    basis: str
    claim_ids: tuple[str, ...]
    quotes: tuple[CaseSourceCitation, ...]
    offered_quotes: int
    verified_quotes: int


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
    drafts = []
    for item in reply.units:
        draft = drafted_unit(item, claims, registry)
        if draft is not None:
            drafts.append(draft)
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
) -> DraftUnit | None:
    text = strip_inline_citations(item.text)
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
    quotes: list[CaseSourceCitation] = []
    verified_count = 0
    for quote in item.quotes:
        source = registry.get(quote.source_id)
        if source is None or not quote.exact_quote.strip():
            continue
        exact = quote.exact_quote.strip()
        pieces = (
            [p.strip() for p in re.split(r"(?:\.{3,}|…+)", exact) if p.strip()]
            if ("..." in exact or "…" in exact)
            else [exact]
        )
        matched = False
        for piece in pieces:
            start = source.text.find(piece)
            if start >= 0:
                matched = True
                locator = find_document_locator(
                    {
                        "document_id": source.document_id,
                        "filename": source.filename,
                        "page_spans": source.provenance.get("pages"),
                    },
                    source.text,
                    [start],
                    len(piece),
                )
                quotes.append(
                    CaseSourceCitation(
                        source_id=source.source_id,
                        exact_quote=piece,
                        start=start,
                        end=start + len(piece),
                        document_id=source.document_id,
                        filename=source.filename,
                        page_numbers=list(locator[2]) if locator else [],
                    )
                )
        if matched:
            verified_count += 1
    return DraftUnit(text, item.basis, claim_ids, tuple(quotes), len(item.quotes), verified_count)


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
        sum(draft.verified_quotes for draft in drafts),
    )
