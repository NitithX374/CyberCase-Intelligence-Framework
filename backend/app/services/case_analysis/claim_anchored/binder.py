from app.services.case_analysis.claim_anchored.contracts import (
    BoundClaim,
    BoundSpan,
    ExtractedClaims,
)
from app.services.case_analysis.claim_anchored.failure import ClaimAnchoredFailure
from app.services.case_analysis.claim_anchored.source_registry import AdmittedSource
from app.services.case_analysis.contracts import (
    AnalysisClaimV3,
    AnalysisEvidenceCitation,
)
from app.services.case_analysis.evidence_quote_resolver import (
    quote_occurrences,
    resolve_document_locator,
)


def bind_claims(
    extracted: ExtractedClaims,
    sources: tuple[AdmittedSource, ...],
    document_context: object,
) -> tuple[BoundClaim, ...]:
    registry = {source.source_message_id: source for source in sources}
    bound = []
    for index, candidate in enumerate(extracted.claims, 1):
        spans = []
        for evidence in candidate.evidence:
            source = registry.get(evidence.source_message_id)
            if source is None:
                raise ClaimAnchoredFailure(
                    "claim_source_unknown", "Claim cites an unadmitted source"
                )
            positions = quote_occurrences(source.content, evidence.exact_quote)
            if not positions:
                raise ClaimAnchoredFailure(
                    "claim_quote_absent", "Claim quotation is absent from source"
                )
            if len(positions) != 1:
                raise ClaimAnchoredFailure(
                    "claim_quote_ambiguous", "Claim quotation occurs more than once"
                )
            locator = resolve_document_locator(
                source.source_message_id,
                evidence.exact_quote,
                source.content,
                document_context,
                require_complete_coverage=True,
            )
            citation = AnalysisEvidenceCitation(
                source_message_id=source.source_message_id,
                exact_quote=evidence.exact_quote,
                **locator,
            )
            spans.append(
                BoundSpan(
                    citation=citation,
                    source_text_sha256=source.content_sha256,
                    start_offset=positions[0],
                    end_offset=positions[0] + len(evidence.exact_quote),
                    role=evidence.role,
                    locator_status="document_page"
                    if citation.page_numbers
                    else "narrative_only",
                )
            )
        supporting = [span.citation for span in spans if span.role == "supporting"]
        contradicting = [
            span.citation for span in spans if span.role == "contradicting"
        ]
        support_ids = list(dict.fromkeys(item.source_message_id for item in supporting))
        contradict_ids = list(
            dict.fromkeys(item.source_message_id for item in contradicting)
        )
        if set(support_ids) & set(contradict_ids):
            raise ClaimAnchoredFailure(
                "claim_source_roles_overlap",
                "Opposing statements from one source need separate claims",
            )
        if candidate.claim_type == "reported" and not supporting:
            raise ClaimAnchoredFailure(
                "claim_reported_unbound", "Reported claim needs supporting evidence"
            )
        bound.append(
            BoundClaim(
                candidate_id=f"C-{index:03d}",
                claim=AnalysisClaimV3(
                    claim_id=f"A-{index:02d}",
                    text=candidate.text,
                    claim_type=candidate.claim_type,
                    epistemic_status=candidate.epistemic_status,
                    reasoning_summary=candidate.reasoning_summary,
                    supporting_source_message_ids=support_ids,
                    contradicting_source_message_ids=contradict_ids,
                    supporting_citations=supporting,
                    contradicting_citations=contradicting,
                ),
                spans=tuple(spans),
            )
        )
    return tuple(bound)
