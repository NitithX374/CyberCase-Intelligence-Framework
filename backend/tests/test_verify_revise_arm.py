from __future__ import annotations

import asyncio
from uuid import uuid4

from app.services.analysis.contracts import (
    CaseAnalysisClaim,
    CaseAnalysisOutput,
    CaseAnalysisTrace,
    CaseSourceCitation,
)
from app.services.analysis.pipeline import (
    AnalysisArtifacts,
    AnalysisInput,
    write_analysis,
)
from app.services.sources.case_source_bundle import CaseSourceBundle, CaseSourceItem
from experiments.analysis_arms import revise

TEXT = "The finance share was encrypted overnight and a note demanded contact."
SOURCE_ID = str(uuid4())
BUNDLE = CaseSourceBundle(
    revision=1,
    sources=(CaseSourceItem(source_id=SOURCE_ID, source_kind="narrative", text=TEXT),),
)


def claim(claim_id: str, quote: str) -> CaseAnalysisClaim:
    return CaseAnalysisClaim(
        claim_id=claim_id,
        claim_type="reported",
        text="The share was encrypted.",
        epistemic_status="reported",
        supporting_source_ids=[SOURCE_ID],
        supporting_citations=[CaseSourceCitation(source_id=SOURCE_ID, exact_quote=quote)],
    )


def trace_of(*claims: CaseAnalysisClaim) -> CaseAnalysisTrace:
    return CaseAnalysisTrace(
        analysis_mode="case_overview", summary="The share was encrypted.", claims=list(claims)
    )


def analysis_returning(*traces: CaseAnalysisTrace):
    seen: list[str | None] = []

    async def request(**kwargs):
        seen.append(kwargs.get("revision"))
        trace = traces[min(len(seen) - 1, len(traces) - 1)]
        return CaseAnalysisOutput(answer=trace.summary, trace=trace, execution_receipt={})

    return request, seen


def test_arm_a_leaves_an_invented_quotation_in_place():
    request, seen = analysis_returning(trace_of(claim("A-01", "There was no incident.")))
    artifacts = asyncio.run(
        write_analysis(AnalysisInput(sources=BUNDLE), AnalysisArtifacts(), request=request)
    )

    assert seen == [None]
    assert artifacts.trace.claims[0].supporting_citations[0].exact_quote == "There was no incident."
    assert artifacts.trace.grounding is None


def test_arm_b_verifies_without_revising_when_nothing_missed():
    request, seen = analysis_returning(trace_of(claim("A-01", TEXT)))
    artifacts = asyncio.run(revise(AnalysisInput(sources=BUNDLE), max_revisions=1, request=request))

    assert seen == [None], "a sound analysis costs no second call"
    assert artifacts.trace.grounding.citations_verified == 1
    assert artifacts.receipt["verification"]["rounds"] == [
        {
            "attempt": 0,
            "claims": 1,
            "citations_verified": 1,
            "citations_unfound": 0,
            "sources_cited": 1,
        }
    ]


def test_arm_b_hands_back_the_quotations_that_missed():
    invented = trace_of(claim("A-01", "There was no incident."))
    corrected = trace_of(claim("A-01", TEXT))
    request, seen = analysis_returning(invented, corrected)

    artifacts = asyncio.run(revise(AnalysisInput(sources=BUNDLE), max_revisions=1, request=request))

    assert len(seen) == 2, "the second call is the revision"
    assert "A-01" in seen[1] and "There was no incident." in seen[1]
    assert artifacts.trace.grounding.citations_verified == 1
    assert artifacts.trace.grounding.citations_unfound == 0


def test_the_receipt_shows_whether_revising_fixed_or_deleted():
    invented = trace_of(claim("A-01", TEXT), claim("A-02", "Nothing of the sort happened."))
    gutted = trace_of(claim("A-01", TEXT))
    request, _ = analysis_returning(invented, gutted)

    artifacts = asyncio.run(revise(AnalysisInput(sources=BUNDLE), max_revisions=1, request=request))

    rounds = artifacts.receipt["verification"]["rounds"]
    assert [r["citations_unfound"] for r in rounds] == [1, 0], "grounding looks perfect after"
    assert [r["claims"] for r in rounds] == [2, 1], "and it got there by dropping one"


def test_a_model_that_keeps_missing_stops_at_the_bound():
    invented = trace_of(claim("A-01", "There was no incident."))
    request, seen = analysis_returning(invented)

    artifacts = asyncio.run(revise(AnalysisInput(sources=BUNDLE), max_revisions=2, request=request))

    assert len(seen) == 3, "one analysis and two revisions, then it stops"
    assert artifacts.trace.grounding.citations_unfound == 1
    assert len(artifacts.receipt["verification"]["rounds"]) == 3
