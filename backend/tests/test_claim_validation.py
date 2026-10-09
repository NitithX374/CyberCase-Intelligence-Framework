from __future__ import annotations

import pytest
from fake_nli import FakeNli

from app.trace.b1_verifier import THRESHOLD
from app.trace.claim_validation import (
    source_premise,
    unverified_claims,
    usable_claims,
    validate_claims,
)
from app.trace.claims import CaseAnalysisClaim, CaseInvalidEvidence, CaseSourceCitation
from app.trace.nli_model import Judgement, NliUnavailable


def claim(text="John sent an email.", citations=None, **changes):
    return CaseAnalysisClaim(
        claim_id="A-01",
        claim_type="reported",
        text=text,
        epistemic_status=changes.pop("epistemic_status", "reported"),
        supporting_citations=(
            citations
            if citations is not None
            else [
                CaseSourceCitation(
                    source_id="S1",
                    exact_quote="John sent an email.",
                    pointer_state="direct",
                    start=0,
                    end=19,
                    evidence_unit_ids=["S1:U001-fixture"],
                )
            ]
        ),
        **changes,
    )


@pytest.mark.parametrize(
    ("text", "label", "score", "expected"),
    [
        ("John sent an email.", "entailment", 0.99, "supported"),
        ("John is the attacker.", "neutral", 0.1, "not_supported"),
        ("John did not send an email.", "contradiction", 0.01, "not_supported"),
        ("John sent an email.", "entailment", 0.4, "not_supported"),
        ("John sent an email.", "entailment", 0.5, "supported"),
    ],
)
def test_complete_claim_support_uses_frozen_lr_decision(text, label, score, expected):
    original = claim(text)
    scorer = FakeNli(judge=lambda premise, hypothesis: Judgement(label, score))
    checked, stats = validate_claims([original], provider=lambda: scorer)

    assert scorer.judged == [("John sent an email.", text)]
    assert checked[0].semantic_grounding.verdict == expected
    assert checked[0].semantic_grounding.entailment == score
    assert checked[0].semantic_grounding.threshold == THRESHOLD
    assert checked[0].semantic_grounding.method == "b1-lr-wice-train-v1"
    assert usable_claims(checked) == checked
    assert stats.calls == 1
    assert stats.supported + stats.not_supported + stats.unassessed == 1
    assert original.semantic_grounding is None


@pytest.mark.parametrize(
    ("source_text", "hypothesis"),
    [
        ("John sent an email.", "John is the attacker."),
        ("The transfer took place at 13:00.", "The server was encrypted at 13:00."),
        ("Jane lost 25,000 baht.", "Jane lost 250,000 baht."),
        ("The laptop was encrypted.", "The database was encrypted."),
        ("Jane reported the loss.", "Jane committed fraud."),
    ],
)
def test_bound_citations_do_not_bypass_a_negative_semantic_verdict_which_only_labels(
    source_text, hypothesis
):
    original = claim(
        hypothesis,
        [
            CaseSourceCitation(
                source_id="S1",
                exact_quote=source_text,
                pointer_state="direct",
                start=0,
                end=len(source_text),
                evidence_unit_ids=["S1:U001-fixture"],
            )
        ],
    )
    scorer = FakeNli()
    checked, stats = validate_claims([original], provider=lambda: scorer)

    assert scorer.judged == [(source_text, hypothesis)]
    assert checked[0].semantic_grounding.verdict == "not_supported"
    assert usable_claims(checked) == checked
    assert stats.grounding()["claims_admitted_to_judgement"] == 1
    assert stats.grounding()["claims_withheld_from_judgement"] == 0


def test_multiple_units_and_documents_form_one_complete_premise_without_duplicate_spans():
    first = CaseSourceCitation(source_id="S1", exact_quote="Jane made a transfer.", start=0, end=21)
    second = CaseSourceCitation(source_id="S2", exact_quote="The transfer was 25,000 baht.")
    original = claim("Jane transferred 25,000 baht.", [first, first, second])
    scorer = FakeNli(judge=lambda premise, hypothesis: Judgement("entailment", 0.99))

    checked, stats = validate_claims([original], provider=lambda: scorer)

    assert scorer.judged == [
        ("Jane made a transfer.\nThe transfer was 25,000 baht.", original.text)
    ]
    assert stats.calls == 1
    assert checked[0].semantic_grounding.verdict == "supported"
    assert checked[0].supporting_citations == original.supporting_citations


def test_same_text_under_different_sources_remains_distinct_in_the_premise():
    citations = [
        CaseSourceCitation(source_id=name, exact_quote="John sent an email.")
        for name in ("S1", "S2")
    ]
    assert source_premise(claim(citations=citations)) == "John sent an email.\nJohn sent an email."


def test_long_input_follows_research_truncation_policy_and_records_it():
    original = claim("John sent an email and encrypted the server.")
    scorer = FakeNli(fits=lambda premise, hypothesis: False)

    checked, stats = validate_claims([original], provider=lambda: scorer)

    assert checked[0].text == original.text
    assert checked[0].semantic_grounding.reason == "lr_not_supported"
    assert checked[0].semantic_grounding.verdict == "not_supported"
    assert checked[0].semantic_grounding.truncated is True
    assert len(scorer.judged) == 1
    assert stats.calls == stats.truncated == 1
    assert usable_claims(checked) == checked


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"citations": []}, "no_resolved_source"),
        ({"epistemic_status": "suspected"}, "claim_uncertain"),
        ({"epistemic_status": "contradicted"}, "claim_uncertain"),
        ({"epistemic_status": "not_established"}, "claim_uncertain"),
        ({"epistemic_status": "not_confirmed"}, "claim_uncertain"),
        (
            {
                "contradicting_citations": [
                    CaseSourceCitation(source_id="S2", exact_quote="John denied sending it.")
                ]
            },
            "conflicting_source",
        ),
        ({"contradicting_source_ids": ["S2"]}, "conflicting_source"),
        (
            {
                "invalid_evidence": [
                    CaseInvalidEvidence(
                        source_id="S2",
                        evidence_unit_id="unknown-unit",
                        role="contradicting",
                        reason="unknown_unit",
                    )
                ]
            },
            "conflicting_source",
        ),
    ],
)
def test_unassessed_or_conflicting_claims_stay_withheld(changes, reason):
    scorer = FakeNli(judge=lambda premise, hypothesis: Judgement("entailment", 0.99))
    checked, stats = validate_claims([claim(**changes)], provider=lambda: scorer)

    assert checked[0].semantic_grounding.reason == reason
    assert stats.unassessed == 1
    assert stats.calls == 0
    assert usable_claims(checked) == []
    assert stats.grounding()["claims_withheld_from_judgement"] == 1


@pytest.mark.parametrize("reason", ["stale_id", "unknown_unit", "duplicate_id"])
def test_invalid_support_is_withheld_but_duplicate_diagnostics_do_not_change_meaning(reason):
    invalid = CaseInvalidEvidence(
        source_id="S1",
        evidence_unit_id="old-unit",
        role="supporting",
        pointer_state="unresolved",
        reason=reason,
    )
    scorer = FakeNli(judge=lambda premise, hypothesis: Judgement("entailment", 0.99))
    checked, _ = validate_claims([claim(invalid_evidence=[invalid])], provider=lambda: scorer)

    assert bool(usable_claims(checked)) == (reason == "duplicate_id")
    if reason != "duplicate_id":
        assert checked[0].semantic_grounding.reason == "unresolved_source_reference"


def test_the_validator_reports_an_unavailable_verifier_to_its_caller():
    def unavailable():
        raise NliUnavailable("weights_missing")

    with pytest.raises(NliUnavailable, match="weights_missing"):
        validate_claims([claim()], provider=unavailable)


def test_claims_stay_unassessed_and_usable_when_the_verifier_is_unavailable():
    eligible = claim()
    blocked = claim(citations=[])

    checked, stats = unverified_claims([eligible, blocked])

    assert [item.semantic_grounding.verdict for item in checked] == [
        "unassessed",
        "unassessed",
    ]
    assert [item.semantic_grounding.reason for item in checked] == [
        "verifier_unavailable",
        "no_resolved_source",
    ]
    assert stats.calls == 0
    assert stats.grounding()["claims_admitted_to_judgement"] == 1
    assert stats.grounding()["claims_withheld_from_judgement"] == 1
    assert usable_claims(checked) == [checked[0]]
    assert eligible.semantic_grounding is None


def test_frozen_lr_threshold_is_recorded_and_entailment_is_not_the_admission_score():
    scorer = FakeNli(judge=lambda premise, hypothesis: Judgement("entailment", 0.9))
    checked, stats = validate_claims([claim()], provider=lambda: scorer)
    assert checked[0].semantic_grounding.reason == "lr_supported"
    assert stats.threshold == checked[0].semantic_grounding.threshold == 0.5
    assert checked[0].semantic_grounding.p_supported != 0.9


def test_saved_legacy_claims_have_no_invented_verdict():
    original = claim()
    assert original.semantic_grounding is None


def test_selection_diagnostics_address_original_citation_indices_after_source_ordering():
    from types import SimpleNamespace

    from app.trace.b1_verifier import ClaimVerification
    from app.trace.nli_model import NliProbabilities

    citations = [
        CaseSourceCitation(
            source_id="S1", exact_quote="Second.", start=8, end=15, evidence_unit_ids=["second"]
        ),
        CaseSourceCitation(
            source_id="S2", exact_quote="Other.", start=0, end=6, evidence_unit_ids=["other"]
        ),
        CaseSourceCitation(
            source_id="S1", exact_quote="First. ", start=0, end=7, evidence_unit_ids=["first"]
        ),
    ]
    seen = []

    def verify(text, units):
        seen.append(units)
        return ClaimVerification(
            NliProbabilities(0.9, 0.08, 0.02, 25, False), 0.8, (0, 2), (0.8, 0.1, 0.6), 1.0
        )

    checked, _ = validate_claims(
        [claim(citations=citations)], provider=lambda: SimpleNamespace(name="test", verify=verify)
    )
    assert seen == [["First. ", "Second.", "Other."]]
    grounding = checked[0].semantic_grounding
    assert grounding.considered_citation_indices == [2, 0, 1]
    assert grounding.selected_citation_indices == [2, 1]
    assert grounding.selected_evidence_unit_ids == ["first", "other"]
    assert grounding.source_similarities == [0.8, 0.1, 0.6]
