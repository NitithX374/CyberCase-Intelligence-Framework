from __future__ import annotations

import logging
import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass

from fastapi import status

from app.analysis.language import ResponseLanguage
from app.analysis.reading_sources import ReadingSources
from app.chat.answer_contract import CaseAnalysisOutput, ChatReply, ChatReplyUnit
from app.errors import CaseAnalysisFailure
from app.sources.bundle import CaseSourceItem
from app.trace.citations import CaseInvalidEvidence
from app.trace.claims import CaseAnalysisClaim, CaseSourceCitation, normalize_identifier
from app.trace.evidence_binding import bind_citations
from app.trace.messages import ChatAnswerUnit
from app.trace.trace import MAX_SUMMARY_CHARS, CaseAnalysisTrace

logger = logging.getLogger("app.chat.compose")

CITING_BASES = ("case_fact", "interpretation")


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
    citations: tuple[CaseSourceCitation, ...]
    invalid: tuple[CaseInvalidEvidence, ...]
    offered_units: int


def answer_from(
    reply: ChatReply,
    trace: CaseAnalysisTrace | None,
    reading_sources: ReadingSources,
    language: ResponseLanguage,
) -> CaseAnalysisOutput:
    registry = reading_sources.evidence.sources
    claims = (
        {claim.claim_id: still_held(claim, registry) for claim in trace.claims}
        if trace is not None
        else {}
    )
    drafts = []
    for item in reply.units:
        draft = drafted_unit(item, claims, reading_sources)
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
        CaseAnalysisTrace(
            analysis_mode="question_answer",
            summary=answer,
            claims=[claims[claim_id] for claim_id in selected],
        )
        if selected
        else None
    )
    units = tuple(finished_unit(draft, claims) for draft in drafts)
    log_grounding(drafts, units)
    return CaseAnalysisOutput(
        answer=answer, trace=answer_trace, units=units, suggestion=reply.suggestion
    )


def still_held(
    claim: CaseAnalysisClaim, registry: Mapping[str, CaseSourceItem]
) -> CaseAnalysisClaim:
    return claim.model_copy(
        update={
            "supporting_citations": [
                citation for citation in claim.supporting_citations if holds(citation, registry)
            ],
            "contradicting_citations": [
                citation for citation in claim.contradicting_citations if holds(citation, registry)
            ],
        }
    )


def holds(citation: CaseSourceCitation, registry: Mapping[str, CaseSourceItem]) -> bool:
    source = registry.get(citation.source_id)
    if source is None or not citation.exact_quote or citation.start is None or citation.end is None:
        return False
    return source.text[citation.start : citation.end] == citation.exact_quote


def drafted_unit(
    item: ChatReplyUnit,
    claims: Mapping[str, CaseAnalysisClaim],
    reading_sources: ReadingSources,
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
    cites = item.basis in CITING_BASES
    cited = [citation for citation in item.citations if cites and citation.source_id]
    bound, invalid, _ = bind_citations(
        cited, "supporting", reading_sources.evidence, set(), reading_sources.canonical_id
    )
    return DraftUnit(
        text=text,
        basis=item.basis,
        claim_ids=claim_ids,
        citations=tuple(bound),
        invalid=tuple(entry for entry in invalid if entry.reason != "duplicate_id"),
        offered_units=sum(max(len(citation.evidence_unit_ids), 1) for citation in cited),
    )


def finished_unit(draft: DraftUnit, bound: Mapping[str, CaseAnalysisClaim]) -> ChatAnswerUnit:
    cited = [bound[claim_id] for claim_id in draft.claim_ids if claim_id in bound]
    supporting = unique_citations(
        [
            *draft.citations,
            *(citation for claim in cited for citation in claim.supporting_citations),
        ]
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
        invalid_evidence=list(draft.invalid),
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
        "%d interpretation, %d technical, %d general, units %d offered %d bound",
        len(units),
        len(facts),
        len(cited),
        len(facts) - len(cited),
        sum(unit.basis == "interpretation" for unit in units),
        sum(unit.basis == "technical" for unit in units),
        sum(unit.basis == "general" for unit in units),
        sum(draft.offered_units for draft in drafts),
        sum(len(draft.citations) for draft in drafts),
    )
