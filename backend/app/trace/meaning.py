from __future__ import annotations

import logging
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Protocol

from pythainlp.tokenize import word_tokenize

from app.config import settings
from app.sources.bundle import CaseSourceItem
from app.trace import nli_model
from app.trace.claims import (
    CaseAnalysisClaim,
    CaseMeaningPassage,
    CaseUnverifiedCitation,
)
from app.trace.nli_model import Judgement, NliUnavailable
from app.trace.sentences import sentence_spans

logger = logging.getLogger(__name__)

TOP_CANDIDATES = 3
MAX_CITATIONS = 30
MIN_ENTAILMENT = 0.5
MAX_PASSAGE_CHARS = 4_000
THAI = re.compile(r"[฀-๿]")
WORDS = re.compile(r"\w+")


class Scorer(Protocol):
    name: str

    def fits(self, premise: str, hypothesis: str) -> bool: ...

    def judge(self, premise: str, hypothesis: str) -> Judgement: ...


@dataclass
class MeaningStats:
    eligible: int = 0
    attempted: int = 0
    produced: int = 0
    unavailable: int = 0
    skipped: int = 0
    reason: str | None = None

    def grounding(self) -> dict[str, object]:
        return {
            "citations_meaning_pointed": self.produced,
            "meaning_pointer_eligible": self.eligible,
            "meaning_pointer_attempted": self.attempted,
            "meaning_pointer_unavailable": self.unavailable,
            "meaning_pointer_unavailable_reason": self.reason,
            "meaning_pointer_skipped": self.skipped,
        }


def words_of(text: str, thai: bool) -> set[str]:
    if thai:
        return {word for word in word_tokenize(text, engine="newmm") if word.strip()}
    return set(WORDS.findall(text.lower()))


class Sentences:
    def __init__(self, text: str) -> None:
        self.text = text
        self.spans = [
            (start, end)
            for start, end in sentence_spans(text)
            if text[start:end].strip() and end - start <= MAX_PASSAGE_CHARS
        ]
        self.tokens: dict[bool, list[set[str]]] = {}

    def words(self, thai: bool) -> list[set[str]]:
        if thai not in self.tokens:
            self.tokens[thai] = [words_of(self.text[a:b], thai) for a, b in self.spans]
        return self.tokens[thai]

    def top(self, claim_text: str, count: int) -> list[tuple[int, int]]:
        thai = THAI.search(claim_text) is not None
        wanted = words_of(claim_text, thai)
        ranked = sorted(
            range(len(self.spans)), key=lambda index: -len(wanted & self.words(thai)[index])
        )
        return [self.spans[index] for index in ranked[:count]]


def eligible_citations(
    claims: list[CaseAnalysisClaim], registry: Mapping[str, CaseSourceItem]
) -> list[tuple[int, int]]:
    return [
        (claim_at, citation_at)
        for claim_at, claim in enumerate(claims)
        if claim.epistemic_status == "not_confirmed"
        for citation_at, citation in enumerate(claim.unverified_citations)
        if citation.role == "supporting"
        and citation.near_passage is None
        and citation.source_id in registry
    ]


def passage_for(
    claim_text: str, source: CaseSourceItem, sentences: Sentences, scorer: Scorer
) -> tuple[CaseMeaningPassage | None, bool]:
    judged: list[tuple[int, int, Judgement]] = []
    for start, end in sentences.top(claim_text, TOP_CANDIDATES):
        premise = source.text[start:end]
        if scorer.fits(premise, claim_text):
            judged.append((start, end, scorer.judge(premise, claim_text)))
    entailed = [
        item
        for item in judged
        if item[2].label == "entailment" and item[2].entailment >= MIN_ENTAILMENT
    ]
    if not entailed:
        return None, bool(judged)
    start, end, judgement = min(entailed, key=lambda item: (-item[2].entailment, item[0]))
    return (
        CaseMeaningPassage(
            source_text=source.text[start:end],
            start=start,
            end=end,
            entailment=judgement.entailment,
            model=scorer.name,
        ),
        True,
    )


def meaning_pointed(
    claims: list[CaseAnalysisClaim],
    registry: Mapping[str, CaseSourceItem],
    provider: Callable[[], Scorer] | None = None,
) -> tuple[list[CaseAnalysisClaim], MeaningStats]:
    stats = MeaningStats()
    if settings.quote_meaning_pointer != "on":
        return claims, stats
    eligible = eligible_citations(claims, registry)
    stats.eligible = len(eligible)
    if not eligible:
        return claims, stats
    try:
        scorer = (provider or nli_model.load_nli)()
    except NliUnavailable as error:
        stats.unavailable, stats.reason = len(eligible), error.reason
        return claims, stats
    try:
        found = point_citations(claims, registry, eligible, scorer, stats)
    except Exception as error:
        logger.warning("Meaning pointer failed: %s", type(error).__name__)
        failed = MeaningStats(eligible=stats.eligible)
        failed.unavailable, failed.reason = stats.eligible, f"failed:{type(error).__name__}"
        return claims, failed
    return with_passages(claims, found), stats


def point_citations(
    claims: list[CaseAnalysisClaim],
    registry: Mapping[str, CaseSourceItem],
    eligible: list[tuple[int, int]],
    scorer: Scorer,
    stats: MeaningStats,
) -> dict[tuple[int, int], CaseMeaningPassage]:
    found: dict[tuple[int, int], CaseMeaningPassage] = {}
    sentences: dict[str, Sentences] = {}
    for claim_at, citation_at in eligible:
        if stats.attempted >= MAX_CITATIONS:
            stats.skipped += 1
            continue
        claim = claims[claim_at]
        source = registry[claim.unverified_citations[citation_at].source_id]
        if source.source_id not in sentences:
            sentences[source.source_id] = Sentences(source.text)
        passage, judged = passage_for(claim.text, source, sentences[source.source_id], scorer)
        if not judged:
            stats.skipped += 1
            continue
        stats.attempted += 1
        if passage is not None:
            found[(claim_at, citation_at)] = passage
            stats.produced += 1
    return found


def with_passages(
    claims: list[CaseAnalysisClaim], found: dict[tuple[int, int], CaseMeaningPassage]
) -> list[CaseAnalysisClaim]:
    pointed: list[CaseAnalysisClaim] = []
    for claim_at, claim in enumerate(claims):
        items: list[CaseUnverifiedCitation] = [
            item.model_copy(update={"meaning_passage": found.get((claim_at, citation_at))})
            for citation_at, item in enumerate(claim.unverified_citations)
        ]
        pointed.append(claim.model_copy(update={"unverified_citations": items}))
    return pointed


__all__ = [
    "MAX_CITATIONS",
    "MIN_ENTAILMENT",
    "MeaningStats",
    "TOP_CANDIDATES",
    "meaning_pointed",
]
