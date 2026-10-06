from __future__ import annotations

import re
from collections.abc import Mapping, Sequence

from app.sources.bundle import CaseSourceBundle, CaseSourceItem, build_document_source_context
from app.sources.evidence import EvidenceIndex
from app.trace.claims import (
    CaseAnalysisClaim,
    CaseEpistemicStatus,
    CaseFollowupExchange,
    CaseSourceCitation,
    CaseUnverifiedCitation,
)
from app.trace.evidence_binding import bind_citations, evidence_counts
from app.trace.grounding import grounding_report as grounding_report
from app.trace.meaning import meaning_pointed
from app.trace.projection import ProjectionValidator
from app.trace.quote_binding import QuoteSearch
from app.trace.summary import summary_pieces
from app.trace.support import item_support as item_support
from app.trace.support import with_support
from app.trace.trace import (
    CaseAnalysisTrace,
    CaseGroundingReport,
    CaseMitreAssociation,
    CaseProviderReading,
    CaseSummaryUnit,
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
    bound, grounding = bound_claims(trace, source_bundle, followup_history)
    return bound_references(bound.model_copy(update={"grounding": grounding}), mitre_table)


def bound_claims(
    written: CaseAnalysisTrace | CaseProviderReading,
    source_bundle: CaseSourceBundle,
    followup_history: Sequence[CaseFollowupExchange] = (),
) -> tuple[CaseAnalysisTrace | CaseProviderReading, CaseGroundingReport]:
    evidence = EvidenceIndex((*source_bundle.sources, *followup_registry_items(followup_history)))
    registry = evidence.sources
    document_context = build_document_source_context(source_bundle)
    search = QuoteSearch(registry)

    claims = deduplicated_claims(written.claims)
    resolved_claims = [
        resolve_claim(claim, registry, document_context, search, evidence) for claim in claims
    ]
    resolved_claims, meaning = meaning_pointed(resolved_claims, registry)

    projection = ProjectionValidator(resolved_claims)
    bound = written.model_copy(
        update={
            "claims": resolved_claims,
            "involved_parties": [projection.check(party) for party in written.involved_parties],
            "timeline": [projection.check(item) for item in written.timeline],
            "impacts": [projection.check(impact) for impact in written.impacts],
        }
    )
    grounding = grounding_report(
        claims,
        resolved_claims,
        registry,
        search=search,
        evidence=evidence,
        claims_dropped=len(written.claims) - len(claims),
    ).model_copy(
        update={**meaning.grounding(), **evidence_counts(written.claims, resolved_claims, evidence)}
    )
    return bound, grounding


def bound_references(trace: CaseAnalysisTrace, mitre_table: object = None) -> CaseAnalysisTrace:
    claims_by_id = {claim.claim_id: claim for claim in trace.claims}
    known_claim_ids = set(claims_by_id)
    associations, outside_context, without_claim = kept_associations(
        trace.mitre_associations,
        known_claim_ids,
        context_technique_ids(mitre_table),
        has_retrieval=trace.retrieval_context_id is not None,
    )
    units, unknown_ids = summary_units(trace.summary, claims_by_id)
    return trace.model_copy(
        update={
            "summary_units": units,
            "involved_parties": [
                with_support(party, claims_by_id) for party in trace.involved_parties
            ],
            "timeline": [with_support(item, claims_by_id) for item in trace.timeline],
            "impacts": [with_support(impact, claims_by_id) for impact in trace.impacts],
            "gaps": [answerable_gap(gap, known_claim_ids) for gap in trace.gaps],
            "mitre_associations": associations,
            "grounding": trace.grounding.model_copy(
                update={
                    "associations_outside_context": outside_context,
                    "associations_without_claim": without_claim,
                    "summary_ids_unknown": unknown_ids,
                }
            ),
        }
    )


def summary_units(
    summary: str, claims_by_id: Mapping[str, CaseAnalysisClaim]
) -> tuple[list[CaseSummaryUnit], int]:
    units: list[CaseSummaryUnit] = []
    unknown_ids = 0
    for text, written in summary_pieces(summary):
        known = [claim_id for claim_id in written if claim_id in claims_by_id]
        unknown_ids += len(written) - len(known)
        units.append(
            CaseSummaryUnit(text=text, claim_ids=known, support=item_support(known, claims_by_id))
        )
    return units, unknown_ids


def deduplicated_claims(claims: list[CaseAnalysisClaim]) -> list[CaseAnalysisClaim]:
    seen: set[str] = set()
    kept: list[CaseAnalysisClaim] = []
    for claim in claims:
        if claim.claim_id in seen:
            continue
        seen.add(claim.claim_id)
        kept.append(claim)
    return kept


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


def resolve_claim(
    claim: CaseAnalysisClaim,
    registry: dict[str, CaseSourceItem],
    document_context: object,
    search: QuoteSearch | None = None,
    evidence: EvidenceIndex | None = None,
) -> CaseAnalysisClaim:
    search = search or QuoteSearch(registry)
    evidence = evidence or EvidenceIndex(tuple(registry.values()))
    seen: set[str] = set()
    supporting, supporting_invalid, supporting_unverified = bind_citations(
        claim.supporting_citations, "supporting", evidence, search, document_context, seen
    )
    contradicting, contradicting_invalid, contradicting_unverified = bind_citations(
        claim.contradicting_citations, "contradicting", evidence, search, document_context, seen
    )
    unverified: list[CaseUnverifiedCitation] = []
    for item in [
        *(item.model_copy(update={"meaning_passage": None}) for item in claim.unverified_citations),
        *supporting_unverified,
        *contradicting_unverified,
    ]:
        if item not in unverified:
            unverified.append(item)
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
            "unverified_citations": unverified,
            "invalid_evidence": [*supporting_invalid, *contradicting_invalid],
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
