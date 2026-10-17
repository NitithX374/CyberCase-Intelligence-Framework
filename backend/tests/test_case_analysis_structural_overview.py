import pytest

from app.trace.bind import bound_references
from app.trace.claims import CaseAnalysisClaim
from app.trace.trace import (
    CaseAnalysisTrace,
    CaseImpactItem,
    CaseInvolvedParty,
    CaseTimelineItem,
)


def test_case_overview_models_construct_and_normalize_claim_ids() -> None:
    party = CaseInvolvedParty(
        name="Alice Corp",
        role="Victim Organization",
        claim_ids=["claim-1", "A-02"],
    )
    assert party.name == "Alice Corp"
    assert party.role == "Victim Organization"
    assert party.claim_ids == ["A-01", "A-02"]

    timeline_item = CaseTimelineItem(
        time="2026-03-01 10:00:00 UTC",
        event="Unauthorized access detected",
        claim_ids=["c-2"],
    )
    assert timeline_item.time == "2026-03-01 10:00:00 UTC"
    assert timeline_item.event == "Unauthorized access detected"
    assert timeline_item.claim_ids == ["A-02"]

    impact = CaseImpactItem(
        description="Customer database exfiltrated",
        claim_ids=["A-03"],
    )
    assert impact.description == "Customer database exfiltrated"
    assert impact.claim_ids == ["A-03"]


def server_claim() -> CaseAnalysisClaim:
    return CaseAnalysisClaim(
        claim_id="A-01",
        claim_type="reported",
        text="Server breached on Monday.",
        epistemic_status="reported",
        supporting_source_ids=["s1"],
    )


def test_binding_keeps_parties_timeline_and_impacts_that_name_a_claim() -> None:
    trace = CaseAnalysisTrace(
        analysis_mode="case_overview",
        summary="Breach occurred.",
        involved_parties=[CaseInvolvedParty(name="Victim Org", role="Target", claim_ids=["A-01"])],
        timeline=[CaseTimelineItem(time="Monday", event="Breach", claim_ids=["A-01"])],
        claims=[server_claim()],
        impacts=[CaseImpactItem(description="Server compromise", claim_ids=["A-01"])],
    )
    validated = bound_references(trace, [])
    assert len(validated.involved_parties) == 1
    assert len(validated.timeline) == 1
    assert len(validated.impacts) == 1


@pytest.mark.parametrize(
    ("section", "item"),
    [
        (
            "involved_parties",
            CaseInvolvedParty(name="Unknown Actor", role="Attacker", claim_ids=["A-99"]),
        ),
        (
            "timeline",
            CaseTimelineItem(time="Tuesday", event="Lateral movement", claim_ids=["A-05"]),
        ),
        ("impacts", CaseImpactItem(description="Financial loss", claim_ids=["A-99"])),
    ],
)
def test_binding_drops_an_unknown_claim_id(section, item) -> None:
    trace = CaseAnalysisTrace(
        analysis_mode="case_overview",
        summary="Breach occurred.",
        claims=[server_claim()],
        **{section: [item]},
    )
    validated = bound_references(trace, [])
    assert getattr(validated, section)[0].claim_ids == []


def test_case_overview_models_allow_empty_claim_ids() -> None:
    party = CaseInvolvedParty(name="Alice Corp", role="Victim", claim_ids=[])
    assert party.claim_ids == []
    item = CaseTimelineItem(time="Monday", event="Breach", claim_ids=[])
    assert item.claim_ids == []
    impact = CaseImpactItem(description="Data leak", claim_ids=[])
    assert impact.claim_ids == []


def test_persisted_case_analysis_trace_defaults_structural_keys_when_omitted() -> None:
    trace = CaseAnalysisTrace.model_validate(
        {
            "analysis_mode": "case_overview",
            "summary": "Summary",
            "claims": [],
        }
    )
    assert trace.involved_parties == []
    assert trace.timeline == []
    assert trace.impacts == []
