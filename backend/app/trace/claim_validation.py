from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from time import perf_counter
from typing import Protocol

from app.trace.b1_verifier import (
    ARTIFACT,
    ARTIFACT_SHA256,
    METHOD,
    THRESHOLD,
    ClaimVerification,
    load_verifier,
)
from app.trace.claims import CaseAnalysisClaim, CaseClaimGrounding


class Scorer(Protocol):
    name: str

    def verify(self, claim: str, units: Sequence[str]) -> ClaimVerification: ...


def load_scorer() -> Scorer:
    return load_verifier()


def admitted_claims(claims: Sequence[CaseAnalysisClaim]) -> list[CaseAnalysisClaim]:
    return [
        claim
        for claim in claims
        if claim.semantic_grounding is not None and claim.semantic_grounding.verdict == "supported"
    ]


def resolved_support(claim: CaseAnalysisClaim):
    seen = set()
    sources = {}
    for index, citation in enumerate(claim.supporting_citations):
        key = (citation.source_id, citation.start, citation.end, citation.exact_quote)
        if (
            citation.pointer_state != "unresolved"
            and citation.exact_quote.strip()
            and key not in seen
        ):
            seen.add(key)
            sources.setdefault(citation.source_id, []).append((index, citation))
    resolved = []
    for citations in sources.values():
        if all(citation.start is not None for _, citation in citations):
            citations = sorted(citations, key=lambda item: item[1].start)
        resolved.extend(citations)
    return resolved


def source_premise(claim: CaseAnalysisClaim) -> str:
    return ARTIFACT["premise_separator"].join(
        citation.exact_quote for _, citation in resolved_support(claim)
    )


def assessment_blocker(claim: CaseAnalysisClaim, premise: str) -> str | None:
    if not premise:
        return "no_resolved_source"
    if any(item.role == "supporting" for item in claim.unverified_citations) or any(
        item.role == "supporting" and item.reason != "duplicate_id"
        for item in claim.invalid_evidence
    ):
        return "unresolved_source_reference"
    if (
        claim.contradicting_citations
        or claim.contradicting_source_ids
        or any(
            item.role == "contradicting"
            for item in [*claim.unverified_citations, *claim.invalid_evidence]
        )
    ):
        return "conflicting_source"
    if claim.epistemic_status not in ("reported", "unknown"):
        return "claim_uncertain"
    return None


@dataclass(frozen=True)
class ClaimValidationStats:
    supported: int
    not_supported: int
    unassessed: int
    calls: int
    duration_ms: float
    model: str | None
    threshold: float
    considered: int
    selected: int
    truncated: int

    def grounding(self) -> dict[str, object]:
        return {
            "claims_semantically_supported": self.supported,
            "claims_semantically_not_supported": self.not_supported,
            "claims_semantically_unassessed": self.unassessed,
            "claims_admitted_to_judgement": self.supported,
            "claims_withheld_from_judgement": self.not_supported + self.unassessed,
            "claim_verifier_calls": self.calls,
            "claim_validation_ms": self.duration_ms,
            "claim_verifier_model": self.model,
            "claim_verifier_threshold": self.threshold,
            "claim_verifier_artifact_sha256": ARTIFACT_SHA256,
            "claim_source_units_considered": self.considered,
            "claim_source_units_selected": self.selected,
            "claim_verifier_truncated_pairs": self.truncated,
        }


def validate_claims(
    claims: Sequence[CaseAnalysisClaim],
    *,
    provider: Callable[[], Scorer] | None = None,
) -> tuple[list[CaseAnalysisClaim], ClaimValidationStats]:
    started = perf_counter()
    threshold = THRESHOLD
    scorer: Scorer | None = None
    checked: list[CaseAnalysisClaim] = []
    calls = 0
    considered = selected = truncated = 0
    for claim in claims:
        claim_started = perf_counter()
        premise = source_premise(claim)
        reason = assessment_blocker(claim, premise)
        verdict = CaseClaimGrounding(
            verdict="unassessed",
            reason=reason or "no_resolved_source",
            threshold=threshold,
            method=METHOD,
            artifact_sha256=ARTIFACT_SHA256,
        )
        if reason is None:
            if scorer is None:
                scorer = (provider or load_scorer)()
            citations = resolved_support(claim)
            result = scorer.verify(claim.text, [citation.exact_quote for _, citation in citations])
            calls += 1
            considered += len(citations)
            selected += len(result.indices)
            truncated += int(result.nli.truncated)
            supported = result.p_supported >= threshold
            verdict = CaseClaimGrounding(
                verdict="supported" if supported else "not_supported",
                reason="lr_supported" if supported else "lr_not_supported",
                method=METHOD,
                artifact_sha256=ARTIFACT_SHA256,
                model=scorer.name,
                label=result.nli.label,
                entailment=result.nli.entailment,
                neutral=result.nli.neutral,
                contradiction=result.nli.contradiction,
                p_supported=result.p_supported,
                threshold=threshold,
                selected_citation_indices=[citations[index][0] for index in result.indices],
                considered_citation_indices=[index for index, _ in citations],
                selected_evidence_unit_ids=[
                    unit_id
                    for index in result.indices
                    for unit_id in citations[index][1].evidence_unit_ids
                ],
                source_similarities=list(result.similarities),
                selector_threshold=ARTIFACT["selector_threshold"],
                selection_ms=result.selection_ms,
                raw_tokens=result.nli.raw_tokens,
                truncated=result.nli.truncated,
            )
        verdict.duration_ms = (perf_counter() - claim_started) * 1_000
        checked.append(claim.model_copy(update={"semantic_grounding": verdict}))
    verdicts = [claim.semantic_grounding.verdict for claim in checked]
    return checked, ClaimValidationStats(
        supported=verdicts.count("supported"),
        not_supported=verdicts.count("not_supported"),
        unassessed=verdicts.count("unassessed"),
        calls=calls,
        duration_ms=(perf_counter() - started) * 1_000,
        model=scorer.name if scorer is not None else None,
        threshold=threshold,
        considered=considered,
        selected=selected,
        truncated=truncated,
    )
