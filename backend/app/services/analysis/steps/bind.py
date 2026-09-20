"""Binding an analysis to the case it was written from.

Nothing here rejects an analysis. Everything the model wrote either resolves
against a source, is trimmed so it stops pointing at something that is not
there, or is counted as lost — and the counts are what a reader, and an
experiment, are given instead of a failure.

That was not always true. Nine rules used to raise, so one invented technique
id or one claim citing a source outside the bundle cost the whole analysis,
while an invented quotation on the next line was quietly dropped. Two policies
for the same kind of mistake. This file now has one.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from app.services.analysis.contracts import (
    CaseAnalysisClaim,
    CaseAnalysisTrace,
    CaseFollowupExchange,
    CaseGroundingReport,
    CaseSourceCitation,
)
from app.services.analysis.steps.quotes import (
    find_aligned_quote,
    looks_like_a_paraphrase,
    quote_occurrences,
    resolve_document_locator,
)
from app.services.sources import CaseSourceBundle, CaseSourceItem, build_document_source_context


def followup_registry_items(
    history: Sequence[CaseFollowupExchange],
) -> tuple[CaseSourceItem, ...]:
    """Answered exchanges, shaped so the citation machinery can read them.

    Quote alignment, paraphrase detection and deduplication all want something
    with a ``source_id`` and a ``text``. A reply has both, so it is handed over
    as one rather than teaching every one of those functions about a second
    kind of thing. Nothing is written to the database by doing this.
    """

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
    """Bind the analysis to what the case actually holds.

    ``sources_total`` counts the follow-up answers too. They are things the
    case knows and the analysis was allowed to draw on, so leaving them out
    would flatter the coverage of an analysis that ignored them.
    """

    registry = {source.source_id: source for source in source_bundle.sources}
    registry.update({item.source_id: item for item in followup_registry_items(followup_history)})
    document_context = build_document_source_context(source_bundle)

    claims = deduplicated_claims(trace.claims)
    known_claim_ids = {claim.claim_id for claim in claims}
    resolved_claims = [resolve_claim(claim, registry, document_context) for claim in claims]

    associations, dropped_associations = kept_associations(
        trace.mitre_associations,
        known_claim_ids,
        context_technique_ids(mitre_table),
        has_retrieval=trace.retrieval_context_id is not None,
    )

    return trace.model_copy(
        update={
            "claims": resolved_claims,
            "involved_parties": [
                bound_to_claims(party, known_claim_ids) for party in trace.involved_parties
            ],
            "timeline": [bound_to_claims(item, known_claim_ids) for item in trace.timeline],
            "impacts": [bound_to_claims(impact, known_claim_ids) for impact in trace.impacts],
            "gaps": [answerable_gap(gap, known_claim_ids) for gap in trace.gaps],
            "mitre_associations": associations,
            "grounding": grounding_report(
                claims,
                resolved_claims,
                registry,
                associations_dropped=dropped_associations,
                claims_dropped=len(trace.claims) - len(claims),
            ),
        }
    )


def deduplicated_claims(claims: list[CaseAnalysisClaim]) -> list[CaseAnalysisClaim]:
    """The first claim under each id. Everything keys on it, including the UI."""

    seen: set[str] = set()
    kept: list[CaseAnalysisClaim] = []
    for claim in claims:
        if claim.claim_id in seen:
            continue
        seen.add(claim.claim_id)
        kept.append(claim)
    return kept


def bound_to_claims(item, known_claim_ids: set[str]):
    """A party, a moment or an impact, pointing only at claims that exist."""

    return item.model_copy(
        update={"claim_ids": [cid for cid in item.claim_ids if cid in known_claim_ids]}
    )


def answerable_gap(gap, known_claim_ids: set[str]):
    """A gap the sources say is unknowable is not worth asking the reader about."""

    return gap.model_copy(
        update={
            "affected_claim_ids": [cid for cid in gap.affected_claim_ids if cid in known_claim_ids],
            "askable": gap.askable and gap.status != "EXPLICITLY_UNKNOWN",
        }
    )


def kept_associations(associations, known_claim_ids, context_techniques, *, has_retrieval):
    """ATT&CK associations that point at something real.

    An association naming a technique that was not in the retrieved context is
    the MITRE version of a quotation that is in no source: the model produced
    it rather than read it. It is dropped, and counted, for the same reason.
    """

    kept = []
    for association in associations:
        if not has_retrieval:
            continue
        if association.technique_id not in context_techniques:
            continue
        kept.append(
            association.model_copy(
                update={
                    "claim_ids": [cid for cid in association.claim_ids if cid in known_claim_ids]
                }
            )
        )
    return kept, len(associations) - len(kept)


def grounding_report(
    written: list[CaseAnalysisClaim],
    kept: list[CaseAnalysisClaim],
    registry: dict[str, CaseSourceItem],
    *,
    associations_dropped: int = 0,
    claims_dropped: int = 0,
) -> CaseGroundingReport:
    """What survived the binding, and what quietly did not.

    A dropped citation is counted twice over: once as dropped, and once as
    either a loose quotation of wording that is in the source, or wording that
    is in no source at all. Reporting them together would put a model that
    quotes sloppily and a model that invents a quotation at the same number.
    """

    def all_citations(claims: list[CaseAnalysisClaim]) -> list[CaseSourceCitation]:
        return [
            c
            for claim in claims
            for c in claim.supporting_citations + claim.contradicting_citations
        ]

    claimed = all_citations(written)
    survived = {(c.source_id, c.exact_quote) for c in all_citations(kept)}
    paraphrased = 0
    unfound = 0
    for citation in claimed:
        if (citation.source_id, citation.exact_quote) in survived:
            continue
        source = registry.get(citation.source_id)
        if source is None:
            unfound += 1
            continue
        # A quote that had to be repaired to be found is kept under the
        # source's spelling, not the model's, so it is missing from the set
        # above while already counted in citations_verified.
        if find_aligned_quote(source.text, citation.exact_quote) is not None:
            continue
        if looks_like_a_paraphrase(source.text, citation.exact_quote):
            paraphrased += 1
        else:
            unfound += 1

    return CaseGroundingReport(
        claims=len(kept),
        citations_claimed=len(claimed),
        citations_verified=len(all_citations(kept)),
        citations_paraphrased=paraphrased,
        citations_unfound=unfound,
        claims_without_citation=sum(1 for c in kept if not c.supporting_citations),
        claims_duplicated=claims_dropped,
        associations_outside_context=associations_dropped,
        sources_cited=len({c.source_id for c in all_citations(kept)}),
        sources_total=len(registry),
    )


def resolve_claim(
    claim: CaseAnalysisClaim,
    registry: dict[str, CaseSourceItem],
    document_context: object,
) -> CaseAnalysisClaim:
    """One claim, pointing only at sources the case actually has.

    A source id the bundle does not contain is removed rather than refused. The
    claim survives without it, and if that leaves it resting on nothing, the
    grounding report is where that shows.
    """

    supporting = {sid for sid in claim.supporting_source_ids if sid in registry}
    contradicting = {sid for sid in claim.contradicting_source_ids if sid in registry}
    return claim.model_copy(
        update={
            "supporting_source_ids": sorted(supporting),
            "contradicting_source_ids": sorted(contradicting),
            "supporting_citations": resolved_citations(
                claim.supporting_citations, supporting, registry, document_context
            ),
            "contradicting_citations": resolved_citations(
                claim.contradicting_citations, contradicting, registry, document_context
            ),
        }
    )


def resolved_citations(
    citations: list[CaseSourceCitation],
    allowed_ids: set[str],
    registry: dict[str, CaseSourceItem],
    document_context: object,
) -> list[CaseSourceCitation]:
    """Each citation whose quotation can be found in the source it names.

    Finding it is also what produces the page numbers, which the model never
    writes and the reader clicks through on.
    """

    resolved: list[CaseSourceCitation] = []
    seen: set[tuple[str, str]] = set()
    for citation in citations:
        if citation.source_id not in allowed_ids:
            continue
        source = registry.get(citation.source_id)
        if source is None:
            continue
        exact_quote = citation.exact_quote
        positions = quote_occurrences(source.text, exact_quote)
        if len(positions) == 0:
            aligned = find_aligned_quote(source.text, exact_quote)
            if aligned is not None:
                exact_quote = aligned
                positions = quote_occurrences(source.text, exact_quote)
        if len(positions) == 0:
            continue
        locator = resolve_document_locator(
            source.source_id,
            exact_quote,
            source.text,
            document_context,
        )
        has_documents = any(
            isinstance(entry, Mapping)
            and entry.get("source_id") == source.source_id
            and entry.get("documents")
            for entry in (document_context if isinstance(document_context, list) else [])
        )
        if len(positions) > 1 and has_documents and not locator.get("page_numbers"):
            locator["page_numbers"] = []
        canonical = CaseSourceCitation(
            source_id=source.source_id,
            exact_quote=exact_quote,
            **locator,
        )
        key = (canonical.source_id, canonical.exact_quote)
        if key not in seen:
            resolved.append(canonical)
            seen.add(key)
    return resolved


def context_technique_ids(value: object) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {
        str(row.get("technique_id")).strip()
        for row in value
        if isinstance(row, Mapping) and row.get("technique_id")
    }


__all__ = [
    "context_technique_ids",
    "followup_registry_items",
    "grounding_report",
    "resolve_case_trace",
    "resolve_claim",
]
