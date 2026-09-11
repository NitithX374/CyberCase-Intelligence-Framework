from __future__ import annotations

import json
from collections import defaultdict, deque
from collections.abc import Callable, Mapping
from dataclasses import dataclass

from app.services.case_analysis.contracts import (
    CaseAdmittedSource,
    CaseAnalysisClaim,
    CaseAnalysisFailure,
    CaseEvidenceCitation,
    CaseExtractedClaims,
)
from app.services.case_analysis.evidenceQuoteResolver import (
    find_aligned_quote,
    quote_occurrences,
    resolve_document_locator,
)


@dataclass(frozen=True)
class CaseBoundSpan:
    citation: CaseEvidenceCitation
    source_text_sha256: str
    start_offset: int
    end_offset: int
    role: str


@dataclass(frozen=True)
class CaseBoundClaim:
    candidate_id: str
    claim: CaseAnalysisClaim
    spans: tuple[CaseBoundSpan, ...]


@dataclass(frozen=True)
class CaseSelection:
    claims: tuple[CaseBoundClaim, ...]
    omissions: tuple[dict[str, str], ...]


def bind_case_claims(
    extracted: CaseExtractedClaims,
    sources: tuple[CaseAdmittedSource, ...],
    document_context: object,
) -> tuple[CaseBoundClaim, ...]:
    registry = {source.source_id: source for source in sources}
    bound: list[CaseBoundClaim] = []
    for index, candidate in enumerate(extracted.claims, 1):
        spans: list[CaseBoundSpan] = []
        for evidence in candidate.evidence:
            source = registry.get(evidence.source_id)
            if source is None or source.revision != evidence.source_revision:
                raise CaseAnalysisFailure(
                    "case_source_unknown",
                    "Case analysis cites an unadmitted source revision",
                )
            exact_quote = evidence.exact_quote
            positions = quote_occurrences(source.content, exact_quote)
            if not positions:
                aligned = find_aligned_quote(source.content, exact_quote)
                if aligned is not None:
                    exact_quote = aligned
                    positions = quote_occurrences(source.content, exact_quote)
            if not positions:
                raise CaseAnalysisFailure(
                    "case_quote_absent",
                    "Case analysis quotation is absent from the source revision",
                )
            locator = resolve_document_locator(
                source.source_id,
                exact_quote,
                source.content,
                document_context,
                require_complete_coverage=True,
            )
            has_documents = any(
                isinstance(e, Mapping) and e.get("source_id") == source.source_id and e.get("documents")
                for e in (document_context if isinstance(document_context, list) else [])
            )
            if len(positions) != 1:
                if has_documents and not locator.get("page_numbers"):
                    raise CaseAnalysisFailure(
                        "case_quote_ambiguous",
                        "Case analysis quotation occurs more than once in the source revision",
                    )
            citation = CaseEvidenceCitation(
                source_id=source.source_id,
                source_revision=source.revision,
                exact_quote=exact_quote,
                **locator,
            )
            spans.append(
                CaseBoundSpan(
                    citation=citation,
                    source_text_sha256=source.content_sha256,
                    start_offset=positions[0],
                    end_offset=positions[0] + len(exact_quote),
                    role=evidence.role,
                )
            )
        supporting = [span.citation for span in spans if span.role == "supporting"]
        contradicting = [span.citation for span in spans if span.role == "contradicting"]
        supporting_ids = list(dict.fromkeys(item.source_id for item in supporting))
        contradicting_ids = list(dict.fromkeys(item.source_id for item in contradicting))
        if set(supporting_ids) & set(contradicting_ids):
            raise CaseAnalysisFailure(
                "case_source_roles_overlap",
                "Opposing statements from one source need separate claims",
            )
        if candidate.claim_type in {"reported", "analytical_inference"} and not supporting:
            raise CaseAnalysisFailure(
                "case_claim_unbound",
                "Reported and inferred claims need supporting case evidence",
            )
        bound.append(
            CaseBoundClaim(
                candidate_id=f"C-{index:03d}",
                claim=CaseAnalysisClaim(
                    claim_id=f"A-{index:02d}",
                    text=candidate.text,
                    claim_type=candidate.claim_type,
                    epistemic_status=candidate.epistemic_status,
                    supporting_source_ids=supporting_ids,
                    contradicting_source_ids=contradicting_ids,
                    supporting_citations=supporting,
                    contradicting_citations=contradicting,
                    reasoning_summary=candidate.reasoning_summary,
                ),
                spans=tuple(spans),
            )
        )
    return tuple(bound)


def assign_case_ids(
    claims: tuple[CaseBoundClaim, ...],
) -> tuple[CaseBoundClaim, ...]:
    return tuple(
        CaseBoundClaim(
            candidate_id=bound.candidate_id,
            claim=bound.claim.model_copy(update={"claim_id": f"A-{index:02d}"}),
            spans=bound.spans,
        )
        for index, bound in enumerate(claims, 1)
    )


def select_case_claims(
    claims: tuple[CaseBoundClaim, ...],
    *,
    source_ids: tuple[str, ...],
    max_claims: int,
    fits: Callable[[tuple[CaseBoundClaim, ...]], bool],
) -> CaseSelection:
    unique: list[CaseBoundClaim] = []
    seen: set[str] = set()
    omissions: list[dict[str, str]] = []
    source_rank = {value: index for index, value in enumerate(source_ids)}
    for bound in claims:
        signature = json.dumps(
            {"claim": bound.claim.model_dump(exclude={"claim_id"}), "spans": [span.__dict__ for span in bound.spans]},
            sort_keys=True,
            ensure_ascii=False,
            default=lambda value: value.model_dump() if hasattr(value, "model_dump") else value,
        )
        if signature in seen:
            omissions.append({"candidate_id": bound.candidate_id, "reason": "exact_duplicate"})
        else:
            seen.add(signature)
            unique.append(bound)
    unique.sort(
        key=lambda bound: min(
            (source_rank[span.citation.source_id], span.start_offset)
            for span in bound.spans
        )
    )
    numbered = assign_case_ids(tuple(unique))
    if len(numbered) <= max_claims and fits(numbered):
        return CaseSelection(numbered, tuple(omissions))
    required = [
        bound
        for bound in unique
        if bound.claim.claim_type == "unknown"
        or bound.claim.epistemic_status != "reported"
        or bound.claim.contradicting_citations
    ]
    required_numbered = assign_case_ids(tuple(required))
    if len(required) > max_claims or not fits(required_numbered):
        raise CaseAnalysisFailure(
            "case_claim_required_budget_exceeded",
            "Uncertainty claims cannot fit the configured analysis budget",
        )
    selected = list(required)
    groups: dict[str, deque[CaseBoundClaim]] = defaultdict(deque)
    required_ids = {bound.candidate_id for bound in required}
    for bound in unique:
        if bound.candidate_id not in required_ids:
            source_id = min(
                (span.citation.source_id for span in bound.spans),
                key=source_rank.get,
            )
            groups[source_id].append(bound)
    while any(groups.values()):
        for source_id in source_ids:
            if not groups[source_id]:
                continue
            bound = groups[source_id].popleft()
            candidate = assign_case_ids(tuple([*selected, bound]))
            if len(candidate) <= max_claims and fits(candidate):
                selected.append(bound)
            else:
                omissions.append({"candidate_id": bound.candidate_id, "reason": "selection_budget"})
    numbered_selected = assign_case_ids(tuple(selected))
    if not numbered_selected:
        raise CaseAnalysisFailure(
            "case_selection_empty",
            "No admitted Case claim fits the configured analysis budget",
        )
    return CaseSelection(numbered_selected, tuple(omissions))


# Backward-compatibility aliases
NativeBoundSpan = CaseBoundSpan
NativeBoundClaim = CaseBoundClaim
NativeSelection = CaseSelection
bind_native_claims = bind_case_claims
select_native_claims = select_case_claims
assign_native_ids = assign_case_ids

__all__ = [
    "CaseBoundClaim",
    "CaseBoundSpan",
    "CaseSelection",
    "NativeBoundClaim",
    "NativeBoundSpan",
    "NativeSelection",
    "assign_case_ids",
    "assign_native_ids",
    "bind_case_claims",
    "bind_native_claims",
    "select_case_claims",
    "select_native_claims",
]
