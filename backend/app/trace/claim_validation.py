from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from time import perf_counter
from typing import Protocol

from app.config import settings
from app.trace import nli_model
from app.trace.claims import CaseAnalysisClaim, CaseClaimGrounding
from app.trace.nli_model import Judgement


class Scorer(Protocol):
    name: str

    def fits(self, premise: str, hypothesis: str) -> bool: ...

    def judge(self, premise: str, hypothesis: str) -> Judgement: ...


def load_scorer() -> Scorer:
    return nli_model.load_nli()


def admitted_claims(claims: Sequence[CaseAnalysisClaim]) -> list[CaseAnalysisClaim]:
    return [
        claim
        for claim in claims
        if claim.semantic_grounding is not None and claim.semantic_grounding.verdict == "supported"
    ]


def source_premise(claim: CaseAnalysisClaim) -> str:
    seen: set[tuple[str, int | None, int | None, str]] = set()
    texts: list[str] = []
    for citation in claim.supporting_citations:
        if citation.pointer_state == "unresolved" or not citation.exact_quote.strip():
            continue
        key = (citation.source_id, citation.start, citation.end, citation.exact_quote)
        if key not in seen:
            seen.add(key)
            texts.append(citation.exact_quote)
    return "\n\n".join(texts)


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
        }


def validate_claims(
    claims: Sequence[CaseAnalysisClaim],
    *,
    provider: Callable[[], Scorer] | None = None,
) -> tuple[list[CaseAnalysisClaim], ClaimValidationStats]:
    started = perf_counter()
    threshold = settings.claim_support_threshold
    scorer: Scorer | None = None
    checked: list[CaseAnalysisClaim] = []
    calls = 0
    for claim in claims:
        claim_started = perf_counter()
        premise = source_premise(claim)
        reason = assessment_blocker(claim, premise)
        verdict = CaseClaimGrounding(
            verdict="unassessed", reason=reason or "input_too_long", threshold=threshold
        )
        if reason is None:
            if scorer is None:
                scorer = (provider or load_scorer)()
            verdict.model = scorer.name
            if scorer.fits(premise, claim.text):
                result = scorer.judge(premise, claim.text)
                calls += 1
                supported = result.label == "entailment" and result.entailment >= threshold
                verdict = CaseClaimGrounding(
                    verdict="supported" if supported else "not_supported",
                    reason=(
                        "entailed"
                        if supported
                        else "low_entailment"
                        if result.label == "entailment"
                        else result.label
                    ),
                    model=scorer.name,
                    label=result.label,
                    entailment=result.entailment,
                    threshold=threshold,
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
    )
