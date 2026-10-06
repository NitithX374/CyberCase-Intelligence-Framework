from __future__ import annotations

import pytest
from fake_nli import NEUTRAL, FakeNli

from app.analysis.write import reading_payload
from app.sources.bundle import CaseSourceBundle, CaseSourceItem
from app.sources.evidence import evidence_units
from app.trace.bind import bound_claims
from app.trace.claims import CaseAnalysisClaim, CaseSourceCitation
from app.trace.nli_model import Judgement, NliUnavailable
from app.trace.projection import ProjectionValidator, projection_statement
from app.trace.trace import CaseImpactItem, CaseInvolvedParty, CaseProviderReading, CaseTimelineItem


def grounded_claim(text="John sent an email.", claim_id="A-01", **overrides):
    return CaseAnalysisClaim(
        claim_id=claim_id,
        claim_type="reported",
        text=text,
        epistemic_status=overrides.pop("epistemic_status", "reported"),
        supporting_citations=overrides.pop(
            "supporting_citations", [CaseSourceCitation(source_id="S1", exact_quote=text)]
        ),
        **overrides,
    )


@pytest.mark.parametrize(
    "item",
    [
        CaseInvolvedParty(name="John", role="Attacker", claim_ids=["A-01"]),
        CaseTimelineItem(time="13:00", event="The server was encrypted", claim_ids=["A-01"]),
        CaseImpactItem(description="The company lost 50,000 baht", claim_ids=["A-01"]),
    ],
)
def test_resolvable_claim_evidence_does_not_establish_projection_semantics(item):
    source = CaseSourceItem("S1", "narrative", "John sent an email.")
    reading = CaseProviderReading(
        version="case_analysis_trace_v1",
        claims=[
            grounded_claim(
                supporting_citations=[
                    CaseSourceCitation(
                        source_id="S1", evidence_unit_ids=[evidence_units(source)[0].unit_id]
                    )
                ]
            )
        ],
        involved_parties=[item] if isinstance(item, CaseInvolvedParty) else [],
        timeline=[item] if isinstance(item, CaseTimelineItem) else [],
        impacts=[item] if isinstance(item, CaseImpactItem) else [],
    )
    checked, report = bound_claims(reading, CaseSourceBundle(1, (source,)))
    section = (
        "involved_parties"
        if isinstance(item, CaseInvolvedParty)
        else "timeline"
        if isinstance(item, CaseTimelineItem)
        else "impacts"
    )
    [projection] = getattr(checked, section)
    assert projection.support == "bound"
    assert projection.projection_grounding.verdict == "not_supported"
    assert projection.projection_grounding.reason == "neutral"
    assert reading_payload(checked)[section] == []
    assert report.evidence_id_resolution_rate == 1


@pytest.mark.parametrize(
    ("text", "item", "hypothesis"),
    [
        (
            "John is the victim.",
            CaseInvolvedParty(name="John", role="the victim", claim_ids=["A-01"]),
            "John is the victim.",
        ),
        (
            "At 13:00, the server was encrypted.",
            CaseTimelineItem(time="13:00", event="the server was encrypted.", claim_ids=["A-01"]),
            "At 13:00, the server was encrypted.",
        ),
        (
            "Payroll was interrupted for two days.",
            CaseImpactItem(description="Payroll was interrupted for two days.", claim_ids=["A-01"]),
            "Payroll was interrupted for two days.",
        ),
    ],
)
def test_the_complete_projection_is_checked_against_claim_text_not_source_text(
    text, item, hypothesis
):
    scorer = FakeNli(
        judge=lambda premise, conclusion: (
            Judgement("entailment", 0.9) if (premise, conclusion) == (text, hypothesis) else NEUTRAL
        )
    )
    projection = ProjectionValidator([grounded_claim(text)], lambda: scorer).check(item)
    assert scorer.judged == [(text, hypothesis)]
    assert projection.projection_grounding.verdict == "supported"
    assert projection.support == "bound"
    assert projection.projection_grounding.model == scorer.name
    assert projection.projection_grounding.entailment == 0.9


@pytest.mark.parametrize(
    ("text", "item"),
    [
        (
            "The report was received at 13:00.",
            CaseTimelineItem(time="13:00", event="the server was encrypted", claim_ids=["A-01"]),
        ),
        (
            "John sent an email to the company.",
            CaseInvolvedParty(name="John", role="Attacker", claim_ids=["A-01"]),
        ),
        (
            "The server was encrypted.",
            CaseImpactItem(description="All customer records were stolen", claim_ids=["A-01"]),
        ),
        (
            "Jane is the attacker. John sent an email.",
            CaseInvolvedParty(name="John", role="Attacker", claim_ids=["A-01"]),
        ),
    ],
)
def test_partial_or_wrong_subject_support_does_not_bypass_the_joint_hypothesis(text, item):
    scorer = FakeNli()
    projection = ProjectionValidator([grounded_claim(text)], lambda: scorer).check(item)
    assert scorer.judged == [(text, projection_statement(item))]
    assert projection.projection_grounding.verdict == "not_supported"


@pytest.mark.parametrize(
    ("label", "probability", "verdict"),
    [
        ("entailment", 0.9, "supported"),
        ("entailment", 0.49, "not_supported"),
        ("neutral", 0.1, "not_supported"),
        ("contradiction", 0.02, "not_supported"),
    ],
)
def test_the_semantic_verdict_is_separate_from_binding(label, probability, verdict):
    scorer = FakeNli(judge=lambda *args: Judgement(label, probability))
    item = CaseInvolvedParty(name="John", role="Victim", claim_ids=["A-01"])
    projection = ProjectionValidator([grounded_claim()], lambda: scorer).check(item)
    assert projection.support == "bound"
    assert projection.projection_grounding.verdict == verdict


def test_missing_claims_and_unbound_or_qualified_claims_are_explicitly_unassessed():
    claims = [
        grounded_claim(),
        grounded_claim(claim_id="A-02", supporting_citations=[]),
        grounded_claim(claim_id="A-03", epistemic_status="suspected"),
    ]
    scorer = FakeNli(judge=lambda *args: Judgement("entailment", 1.0))
    validator = ProjectionValidator(claims, lambda: scorer)
    for ids, reason in [
        ([], "no_claim"),
        (["A-01", "A-99"], "unknown_claim"),
        (["A-02"], "unbound_claim"),
        (["A-03"], "qualified_claim"),
    ]:
        projection = validator.check(CaseInvolvedParty(name="John", role="Attacker", claim_ids=ids))
        assert projection.projection_grounding.verdict == "unassessed"
        assert projection.projection_grounding.reason == reason
    assert scorer.judged == []


def test_full_context_is_never_silently_truncated():
    scorer = FakeNli(fits=lambda *args: False)
    item = CaseImpactItem(description="A service outage occurred", claim_ids=["A-01"])
    projection = ProjectionValidator([grounded_claim()], lambda: scorer).check(item)
    assert projection.projection_grounding.verdict == "unassessed"
    assert projection.projection_grounding.reason == "context_limit"
    assert scorer.judged == []


def test_missing_model_is_reported_and_never_falls_back_to_bound_as_semantic_support():
    calls = []

    def unavailable():
        calls.append(1)
        raise NliUnavailable("weights_missing")

    validator = ProjectionValidator([grounded_claim()], unavailable)
    for _ in range(2):
        projection = validator.check(
            CaseInvolvedParty(name="John", role="Attacker", claim_ids=["A-01"])
        )
        assert projection.support == "bound"
        assert projection.projection_grounding.verdict == "unassessed"
        assert projection.projection_grounding.reason == "model_unavailable:weights_missing"
    assert calls == [1]


def test_unexpected_verifier_failure_is_not_hidden():
    def broken(*args):
        raise RuntimeError("broken verifier")

    validator = ProjectionValidator([grounded_claim()], lambda: FakeNli(judge=broken))
    with pytest.raises(RuntimeError, match="broken verifier"):
        validator.check(CaseInvolvedParty(name="John", role="Attacker", claim_ids=["A-01"]))


def test_multiple_linked_claims_are_the_only_premise_and_are_checked_together():
    scorer = FakeNli(judge=lambda *args: Judgement("entailment", 0.9))
    claims = [
        grounded_claim("John is the victim."),
        grounded_claim("John works for Acme.", "A-02"),
        grounded_claim("Jane is an attacker.", "A-03"),
    ]
    item = CaseInvolvedParty(
        name="John", role="Victim employed by Acme", claim_ids=["A-01", "A-02"]
    )
    ProjectionValidator(claims, lambda: scorer).check(item)
    assert scorer.judged == [
        ("John is the victim.\nJohn works for Acme.", projection_statement(item))
    ]


def test_thai_projection_keeps_name_and_role_in_the_same_hypothesis():
    item = CaseInvolvedParty(name="สมชาย", role="ผู้เสียหาย", claim_ids=["A-01"])
    assert projection_statement(item) == "สมชาย มีบทบาทเป็นผู้เสียหาย"
