from __future__ import annotations

import re
from collections.abc import Mapping, Sequence

from app.services.analysis.contracts import (
    CaseAnalysisClaim,
    CaseAnalysisTrace,
    CaseFollowupExchange,
    CaseGroundingReport,
    CaseMitreAssociation,
    CaseSourceCitation,
)
from app.services.analysis.steps.quotes import (
    find_aligned_quote,
    looks_like_a_paraphrase,
    quote_occurrences,
    resolve_document_locator,
)
from app.services.sources.case_source_bundle import (
    CaseSourceBundle,
    CaseSourceItem,
    build_document_source_context,
)

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
    registry = {source.source_id: source for source in source_bundle.sources}
    registry.update({item.source_id: item for item in followup_registry_items(followup_history)})
    document_context = build_document_source_context(source_bundle)

    claims = deduplicated_claims(trace.claims)
    known_claim_ids = {claim.claim_id for claim in claims}
    resolved_claims = [resolve_claim(claim, registry, document_context) for claim in claims]

    associations, outside_context, without_claim = kept_associations(
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
                associations_outside_context=outside_context,
                associations_without_claim=without_claim,
                claims_dropped=len(trace.claims) - len(claims),
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
    associations_outside_context: int = 0,
    associations_without_claim: int = 0,
    claims_dropped: int = 0,
) -> CaseGroundingReport:
    def all_citations(claims: list[CaseAnalysisClaim]) -> list[CaseSourceCitation]:
        return [
            c
            for claim in claims
            for c in claim.supporting_citations + claim.contradicting_citations
        ]

    claimed = all_citations(written)
    verified = len(all_citations(kept))
    located = 0
    paraphrased = 0
    unfound = 0
    for citation in claimed:
        source = registry.get(citation.source_id)
        if source is None:
            unfound += 1
        elif located_quote(source.text, citation.exact_quote) is not None:
            located += 1
        elif looks_like_a_paraphrase(source.text, citation.exact_quote):
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
) -> CaseAnalysisClaim:
    supporting = resolved_citations(claim.supporting_citations, registry, document_context)
    contradicting = resolved_citations(claim.contradicting_citations, registry, document_context)
    return claim.model_copy(
        update={
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


def role_source_ids(
    source_ids: list[str],
    citations: list[CaseSourceCitation],
    registry: dict[str, CaseSourceItem],
) -> list[str]:
    named = {*source_ids, *(citation.source_id for citation in citations)}
    return sorted(source_id for source_id in named if source_id in registry)


def located_quote(content: str, quote: str) -> str | None:
    if quote_occurrences(content, quote):
        return quote
    return find_aligned_quote(content, quote)


def resolved_citations(
    citations: list[CaseSourceCitation],
    registry: dict[str, CaseSourceItem],
    document_context: object,
) -> list[CaseSourceCitation]:
    resolved: list[CaseSourceCitation] = []
    seen: set[tuple[str, str]] = set()
    for citation in citations:
        source = registry.get(citation.source_id)
        if source is None:
            continue
        exact_quote = located_quote(source.text, citation.exact_quote)
        if exact_quote is None:
            continue
        canonical = CaseSourceCitation(
            source_id=source.source_id,
            exact_quote=exact_quote,
            **resolve_document_locator(
                source.source_id, exact_quote, source.text, document_context
            ),
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
