from __future__ import annotations

import json
from uuid import uuid4

import pytest

from app.analysis.write import reading_payload
from app.chat.compose import analysis_payload
from app.llm.schema import structured_output_schema
from app.sources.bundle import CaseSourceBundle, CaseSourceItem
from app.trace.bind import item_support, resolve_case_trace
from app.trace.claims import CaseAnalysisClaim, CaseSourceCitation
from app.trace.trace import (
    CaseAnalysisTrace,
    CaseImpactItem,
    CaseInvolvedParty,
    CaseProviderAnalysis,
    CaseProviderJudgement,
    CaseProviderReading,
    CaseProviderReadingReply,
    CaseTimelineItem,
)

SOURCE_TEXT = "The finance share was encrypted overnight."
INVENTED = "The attacker demanded two bitcoin."


def claim(claim_id: str, source_id: str, quote: str) -> CaseAnalysisClaim:
    return CaseAnalysisClaim(
        claim_id=claim_id,
        claim_type="reported",
        text=f"Claim {claim_id}.",
        epistemic_status="reported",
        supporting_source_ids=[source_id],
        supporting_citations=[CaseSourceCitation(source_id=source_id, exact_quote=quote)],
    )


def unbound_claim(claim_id: str, source_id: str) -> CaseAnalysisClaim:
    return CaseAnalysisClaim(
        claim_id=claim_id,
        claim_type="reported",
        text=f"Claim {claim_id}.",
        epistemic_status="not_confirmed",
        supporting_source_ids=[source_id],
    )


CLAIMS = {
    "A-01": claim("A-01", "S1", "quote one"),
    "A-02": claim("A-02", "S1", "quote two"),
    "A-03": unbound_claim("A-03", "S1"),
    "A-04": unbound_claim("A-04", "S1"),
}


@pytest.mark.parametrize(
    ("claim_ids", "expected"),
    [
        (["A-01"], "bound"),
        (["A-01", "A-02"], "bound"),
        (["A-01", "A-03"], "mixed"),
        (["A-03", "A-02", "A-04"], "mixed"),
        (["A-03"], "unbound"),
        (["A-03", "A-04"], "unbound"),
        ([], "no_claim"),
        (["A-77"], "no_claim"),
        (["A-77", "A-78"], "no_claim"),
        (["A-01", "A-77"], "bound"),
        (["A-03", "A-77"], "unbound"),
        (["A-01", "A-03", "A-77"], "mixed"),
        (["A-03", "A-03"], "unbound"),
    ],
)
def test_an_item_is_as_supported_as_the_claims_it_names_that_exist(claim_ids, expected):
    assert item_support(claim_ids, CLAIMS) == expected


def bundle_and_trace() -> tuple[CaseSourceBundle, CaseAnalysisTrace]:
    source_id = str(uuid4())
    bundle = CaseSourceBundle(
        revision=1,
        sources=(CaseSourceItem(source_id=source_id, source_kind="narrative", text=SOURCE_TEXT),),
    )
    trace = CaseAnalysisTrace(
        analysis_mode="case_overview",
        summary="A share was encrypted.",
        involved_parties=[
            CaseInvolvedParty(name="Finance team", role="Victim", claim_ids=["A-01", "A-02"]),
            CaseInvolvedParty(name="Unnamed actor", role="Attacker", claim_ids=[]),
        ],
        timeline=[
            CaseTimelineItem(time="Overnight", event="Files encrypted", claim_ids=["A-01"]),
            CaseTimelineItem(time="Next day", event="A ransom was demanded", claim_ids=["A-02"]),
        ],
        impacts=[CaseImpactItem(description="Payroll was lost", claim_ids=["A-99"])],
        claims=[
            claim("A-01", source_id, SOURCE_TEXT),
            claim("A-02", source_id, INVENTED),
        ],
    )
    return bundle, trace


def test_binding_marks_what_rests_only_on_a_claim_whose_quote_was_not_found():
    bundle, trace = bundle_and_trace()

    bound = resolve_case_trace(trace, bundle)

    assert [claim.epistemic_status for claim in bound.claims] == ["reported", "not_confirmed"]
    assert [party.support for party in bound.involved_parties] == ["mixed", "no_claim"]
    assert [item.support for item in bound.timeline] == ["bound", "unbound"]
    assert [impact.support for impact in bound.impacts] == ["no_claim"]
    assert bound.impacts[0].claim_ids == []


def test_a_trace_stored_before_the_status_existed_still_validates_without_one():
    _, trace = bundle_and_trace()
    stored = json.loads(trace.model_dump_json())
    for key in ("involved_parties", "timeline", "impacts"):
        for item in stored[key]:
            del item["support"]

    reloaded = CaseAnalysisTrace.model_validate(stored)

    assert [party.support for party in reloaded.involved_parties] == [None, None]
    assert [item.support for item in reloaded.timeline] == [None, None]
    assert [impact.support for impact in reloaded.impacts] == [None]


def test_the_status_is_in_no_schema_the_model_fills():
    for schema in (
        CaseProviderReadingReply.model_json_schema(),
        structured_output_schema(CaseProviderAnalysis),
        structured_output_schema(CaseProviderJudgement),
    ):
        assert '"support"' not in json.dumps(schema)


def test_a_reply_that_names_a_status_is_refused():
    reply = {
        "version": "case_analysis_trace_v1",
        "claims": [],
        "involved_parties": [{"name": "A", "role": "B", "claim_ids": [], "support": "bound"}],
        "timeline": [],
        "impacts": [],
    }

    with pytest.raises(ValueError, match="support"):
        CaseProviderAnalysis.model_validate({**reply, "summary": "Legacy summary."})


def test_neither_model_is_shown_the_status():
    bundle, trace = bundle_and_trace()
    bound = resolve_case_trace(trace, bundle)
    reading = CaseProviderReading(
        version="case_analysis_trace_v1",
        claims=bound.claims,
    )

    for payload in (reading_payload(reading), analysis_payload(bound, None)):
        assert not {"involved_parties", "timeline", "impacts"} & payload.keys()
