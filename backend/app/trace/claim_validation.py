from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from threading import Event
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


class VerificationStopped(Exception):
    pass


class Scorer(Protocol):
    name: str

    def verify(self, claim: str, units: Sequence[str]) -> ClaimVerification: ...


def load_scorer() -> Scorer:
    return load_verifier()


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


def claim_blocker(claim: CaseAnalysisClaim) -> str | None:
    return assessment_blocker(claim, source_premise(claim))


def usable_claims(claims: Sequence[CaseAnalysisClaim]) -> list[CaseAnalysisClaim]:
    return [claim for claim in claims if claim_blocker(claim) is None]


@dataclass(frozen=True)
class ClaimValidationStats:
    supported: int
    not_supported: int
    unassessed: int
    calls: int
    duration_ms: float


def validation_stats(
    checked: Sequence[CaseAnalysisClaim], calls: int, started: float
) -> ClaimValidationStats:
    verdicts = [claim.semantic_grounding.verdict for claim in checked]
    return ClaimValidationStats(
        supported=verdicts.count("supported"),
        not_supported=verdicts.count("not_supported"),
        unassessed=verdicts.count("unassessed"),
        calls=calls,
        duration_ms=(perf_counter() - started) * 1_000,
    )


def validate_claims(
    claims: Sequence[CaseAnalysisClaim],
    *,
    provider: Callable[[], Scorer] | None = None,
    stop: Event | None = None,
) -> tuple[list[CaseAnalysisClaim], ClaimValidationStats]:
    started = perf_counter()
    scorer: Scorer | None = None
    checked: list[CaseAnalysisClaim] = []
    calls = 0
    for claim in claims:
        if stop is not None and stop.is_set():
            raise VerificationStopped
        reason = claim_blocker(claim)
        verdict = CaseClaimGrounding(
            verdict="unassessed",
            reason=reason or "no_resolved_source",
            method=METHOD,
            artifact_sha256=ARTIFACT_SHA256,
        )
        if reason is None:
            if scorer is None:
                scorer = (provider or load_scorer)()
            units = [citation.exact_quote for _, citation in resolved_support(claim)]
            result = scorer.verify(claim.text, units)
            calls += 1
            supported = result.p_supported >= THRESHOLD
            verdict = CaseClaimGrounding(
                verdict="supported" if supported else "not_supported",
                reason="lr_supported" if supported else "lr_not_supported",
                method=METHOD,
                artifact_sha256=ARTIFACT_SHA256,
            )
        checked.append(claim.model_copy(update={"semantic_grounding": verdict}))
    return checked, validation_stats(checked, calls, started)


def unverified_claims(
    claims: Sequence[CaseAnalysisClaim],
) -> tuple[list[CaseAnalysisClaim], ClaimValidationStats]:
    started = perf_counter()
    checked = [
        claim.model_copy(
            update={
                "semantic_grounding": CaseClaimGrounding(
                    verdict="unassessed",
                    reason=claim_blocker(claim) or "verifier_unavailable",
                    method=METHOD,
                    artifact_sha256=ARTIFACT_SHA256,
                )
            }
        )
        for claim in claims
    ]
    return checked, validation_stats(checked, 0, started)
