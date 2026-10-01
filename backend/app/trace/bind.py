from __future__ import annotations

import re
from collections.abc import Mapping, Sequence

from app.sources.bundle import CaseSourceBundle, CaseSourceItem, build_document_source_context
from app.trace.claims import (
    CaseAnalysisClaim,
    CaseEpistemicStatus,
    CaseFollowupExchange,
    CaseQuoteContext,
    CaseSourceCitation,
)
from app.trace.quotes import (
    MAX_QUOTE_CHARS,
    IndexedText,
    find_aligned_quote,
    indexed,
    looks_like_a_paraphrase,
    quote_occurrences,
    resolve_document_locator,
    without_edge_ellipses,
)

from app.trace.sentences import SentenceIndex, quote_context
from app.trace.trace import CaseAnalysisTrace, CaseGroundingReport, CaseMitreAssociation

ATTACK_TECHNIQUE_ID = re.compile(r"T\d{4}(?:\.\d{3})?")


def followup_registry_items(
    history: Sequence[CaseFollowupExchange],
) -> tuple[CaseSourceItem, ...]:
    return tuple(
        CaseSourceItem(
            source_id=item.qa_id,
            source_kind="followup_answer",
            text=item.answer or "",
            provenance={"origin": "case_followup", "gap_key": item.gap_key},
        )
        for item in history
        if item.is_answered
    )


def resolve_case_trace(
    trace: CaseAnalysisTrace,
    source_bundle: CaseSourceBundle,
    mitre_table: object = None,
    followup_history: Sequence[CaseFollowupExchange] = (),
) -> CaseAnalysisTrace:
    bound, grounding = bound_claims(trace, source_bundle, followup_history)
    return bound_references(bound.model_copy(update={"grounding": grounding}), mitre_table)


def bound_claims(
    written: CaseAnalysisTrace | CaseProviderReading,
    source_bundle: CaseSourceBundle,
    followup_history: Sequence[CaseFollowupExchange] = (),
) -> tuple[CaseAnalysisTrace | CaseProviderReading, CaseGroundingReport]:
    registry = {source.source_id: source for source in source_bundle.sources}
    registry.update({item.source_id: item for item in followup_registry_items(followup_history)})
    document_context = build_document_source_context(source_bundle)
    search = QuoteSearch(registry)

    claims = deduplicated_claims(written.claims)
    known_claim_ids = {claim.claim_id for claim in claims}
    resolved_claims = [resolve_claim(claim, registry, document_context, search) for claim in claims]

    bound = written.model_copy(
        update={
            "claims": resolved_claims,
            "involved_parties": [
                bound_to_claims(party, known_claim_ids) for party in written.involved_parties
            ],
            "timeline": [bound_to_claims(item, known_claim_ids) for item in written.timeline],
            "impacts": [bound_to_claims(impact, known_claim_ids) for impact in written.impacts],
        }
    )
    grounding = grounding_report(
        claims,
        resolved_claims,
        registry,
        search=search,
        claims_dropped=len(written.claims) - len(claims),
    )
    return bound, grounding


def bound_references(trace: CaseAnalysisTrace, mitre_table: object = None) -> CaseAnalysisTrace:
    known_claim_ids = {claim.claim_id for claim in trace.claims}
    associations, outside_context, without_claim = kept_associations(
        trace.mitre_associations,
        known_claim_ids,
        context_technique_ids(mitre_table),
        has_retrieval=trace.retrieval_context_id is not None,
    )
    return trace.model_copy(
        update={
            "gaps": [answerable_gap(gap, known_claim_ids) for gap in trace.gaps],
            "mitre_associations": associations,
            "grounding": trace.grounding.model_copy(
                update={
                    "associations_outside_context": outside_context,
                    "associations_without_claim": without_claim,
                }
            ),
        }
    )


def deduplicated_claims(claims: list[CaseAnalysisClaim]) -> list[CaseAnalysisClaim]:
    seen: set[str] = set()
    kept: list[CaseAnalysisClaim] = []
    for claim in claims:
        if claim.claim_id in seen:
            continue
        seen.add(claim.claim_id)
        kept.append(claim)
    return kept


def bound_to_claims(item, known_claim_ids: set[str]):
    return item.model_copy(
        update={"claim_ids": [cid for cid in item.claim_ids if cid in known_claim_ids]}
    )


def answerable_gap(gap, known_claim_ids: set[str]):
    return gap.model_copy(
        update={
            "affected_claim_ids": [cid for cid in gap.affected_claim_ids if cid in known_claim_ids],
            "askable": gap.askable and gap.status != "EXPLICITLY_UNKNOWN",
        }
    )


def kept_associations(
    associations: list[CaseMitreAssociation],
    known_claim_ids: set[str],
    context_techniques: set[str],
    *,
    has_retrieval: bool,
) -> tuple[list[CaseMitreAssociation], int, int]:
    kept: list[CaseMitreAssociation] = []
    outside_context = 0
    without_claim = 0
    for association in associations:
        technique_id = association.technique_id
        if (
            not has_retrieval
            or ATTACK_TECHNIQUE_ID.fullmatch(technique_id) is None
            or technique_id not in context_techniques
        ):
            outside_context += 1
            continue
        claim_ids = [cid for cid in association.claim_ids if cid in known_claim_ids]
        if not claim_ids:
            without_claim += 1
            continue
        kept.append(association.model_copy(update={"claim_ids": claim_ids}))
    return kept, outside_context, without_claim


def grounding_report(
    written: list[CaseAnalysisClaim],
    kept: list[CaseAnalysisClaim],
    registry: dict[str, CaseSourceItem],
    *,
    search: QuoteSearch | None = None,
    associations_outside_context: int = 0,
    associations_without_claim: int = 0,
    claims_dropped: int = 0,
) -> CaseGroundingReport:
    search = search or QuoteSearch(registry)

    def all_citations(claims: list[CaseAnalysisClaim]) -> list[CaseSourceCitation]:
        return [
            c
            for claim in claims
            for c in claim.supporting_citations + claim.contradicting_citations
        ]

    claimed = all_citations(written)
    verified = sum(
        bool(fresh)
        for claim in written
        for citations in (claim.supporting_citations, claim.contradicting_citations)
        for fresh in added_citations(citations, registry, search)
    )
    located = 0
    paraphrased = 0
    unfound = 0
    for citation in claimed:
        if citation.source_id not in registry:
            unfound += 1
        elif search.located(citation.source_id, citation.exact_quote) is not None:
            located += 1
        elif search.paraphrased(citation.source_id, citation.exact_quote):
            paraphrased += 1
        else:
            unfound += 1

    return CaseGroundingReport(
        claims=len(kept),
        citations_claimed=len(claimed),
        citations_verified=verified,
        citations_paraphrased=paraphrased,
        citations_unfound=unfound,
        claims_without_citation=sum(1 for c in kept if not c.supporting_citations),
        claims_duplicated=claims_dropped,
        citations_duplicated=located - verified,
        associations_outside_context=associations_outside_context,
        associations_without_claim=associations_without_claim,
        sources_cited=len({c.source_id for c in all_citations(kept)}),
        sources_total=len(registry),
    )


def resolve_claim(
    claim: CaseAnalysisClaim,
    registry: dict[str, CaseSourceItem],
    document_context: object,
    search: QuoteSearch | None = None,
) -> CaseAnalysisClaim:
    search = search or QuoteSearch(registry)
    supporting = resolved_citations(claim.supporting_citations, registry, document_context, search)
    contradicting = resolved_citations(
        claim.contradicting_citations, registry, document_context, search
    )
    return claim.model_copy(
        update={
            "epistemic_status": confirmed_status(claim.epistemic_status, supporting),
            "supporting_source_ids": role_source_ids(
                claim.supporting_source_ids, supporting, registry
            ),
            "contradicting_source_ids": role_source_ids(
                claim.contradicting_source_ids, contradicting, registry
            ),
            "supporting_citations": supporting,
            "contradicting_citations": contradicting,
        }
    )


def confirmed_status(
    status: CaseEpistemicStatus, supporting: list[CaseSourceCitation]
) -> CaseEpistemicStatus:
    return "not_confirmed" if status == "reported" and not supporting else status


def role_source_ids(
    source_ids: list[str],
    citations: list[CaseSourceCitation],
    registry: dict[str, CaseSourceItem],
) -> list[str]:
    named = {*source_ids, *(citation.source_id for citation in citations)}
    return sorted(source_id for source_id in named if source_id in registry)


def located_quote(source: str | IndexedText, quote: str) -> tuple[str, ...] | None:
    source = indexed(source)
    quote = without_edge_ellipses(quote)
    if quote_occurrences(source.text, quote):
        return (quote,) if len(quote) <= MAX_QUOTE_CHARS else None
    spans = find_aligned_quote(source, quote)
    if spans is None or spans[-1][1] - spans[0][0] > MAX_QUOTE_CHARS:
        return None
    pieces = tuple(source.text[start:end] for start, end in spans)
    if any(len(quote_occurrences(source.text, piece)) > 1 for piece in pieces):
        return (source.text[spans[0][0] : spans[-1][1]],)
    return pieces


class QuoteSearch:
    def __init__(self, registry: Mapping[str, CaseSourceItem]) -> None:
        self.texts = {source_id: IndexedText(source.text) for source_id, source in registry.items()}
        self.found: dict[tuple[str, str], tuple[str, ...] | None] = {}
        self.sentences: dict[str, SentenceIndex] = {}
        self.contexts: dict[tuple[str, str], CaseQuoteContext | None] = {}

    def located(self, source_id: str, quote: str) -> tuple[str, ...] | None:
        key = (source_id, quote)
        if key not in self.found:
            self.found[key] = located_quote(self.texts[source_id], quote)
        return self.found[key]

    def context(self, source_id: str, quote: str) -> CaseQuoteContext | None:
        key = (source_id, quote)
        if key not in self.contexts:
            if source_id not in self.sentences:
                self.sentences[source_id] = SentenceIndex(self.texts[source_id].text)
            self.contexts[key] = quote_context(self.sentences[source_id], quote)
        return self.contexts[key]

    def paraphrased(self, source_id: str, quote: str) -> bool:
        return looks_like_a_paraphrase(self.texts[source_id], quote)


def added_citations(
    citations: list[CaseSourceCitation],
    registry: dict[str, CaseSourceItem],
    search: QuoteSearch,
    document_context: object = None,
) -> list[list[CaseSourceCitation]]:
    added: list[list[CaseSourceCitation]] = []
    seen: set[tuple[str, str]] = set()
    for citation in citations:
        fresh: list[CaseSourceCitation] = []
        added.append(fresh)
        source = registry.get(citation.source_id)
        if source is None:
            continue
        for exact_quote in search.located(source.source_id, citation.exact_quote) or ():
            canonical = CaseSourceCitation(
                source_id=source.source_id,
                exact_quote=exact_quote,
                context=search.context(source.source_id, exact_quote),
                **resolve_document_locator(
                    source.source_id, exact_quote, source.text, document_context
                ),
            )
            key = (canonical.source_id, canonical.exact_quote)
            if key not in seen:
                fresh.append(canonical)
                seen.add(key)
    return added


def resolved_citations(
    citations: list[CaseSourceCitation],
    registry: dict[str, CaseSourceItem],
    document_context: object,
    search: QuoteSearch | None = None,
) -> list[CaseSourceCitation]:
    search = search or QuoteSearch(registry)
    return [
        citation
        for fresh in added_citations(citations, registry, search, document_context)
        for citation in fresh
    ]


def context_technique_ids(value: object) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {
        str(row.get("technique_id")).strip()
        for row in value
        if isinstance(row, Mapping) and row.get("technique_id")
    }


__all__ = [
    "bound_claims",
    "bound_references",
    "context_technique_ids",
    "followup_registry_items",
    "grounding_report",
    "resolve_case_trace",
    "resolve_claim",
]
