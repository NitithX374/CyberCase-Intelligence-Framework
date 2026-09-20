"""How much of an analysis is actually bound to a source, counted.

A quotation the model invented is dropped during validation rather than
rejected — losing a whole analysis over one bad citation would be worse. But
dropped silently, a fabricated quote and a correct one leave the same trace,
and a claim can reach the reader with nothing behind it. These counts are what
makes that visible, and measurable.
"""

from __future__ import annotations

from uuid import uuid4

from app.services.analysis.contracts import (
    CaseAnalysisClaim,
    CaseAnalysisTrace,
    CaseSourceCitation,
)
from app.services.analysis.steps.bind import resolve_case_trace
from app.services.sources import CaseSourceBundle, CaseSourceItem

TEXT = "Filenames had been changed and a text file demanded contact by email."


def bundle_and_id() -> tuple[CaseSourceBundle, str]:
    source_id = str(uuid4())
    return (
        CaseSourceBundle(
            revision=1,
            sources=(CaseSourceItem(source_id=source_id, source_kind="narrative", text=TEXT),),
        ),
        source_id,
    )


def claim(source_id: str, claim_id: str, quote: str) -> CaseAnalysisClaim:
    return CaseAnalysisClaim(
        claim_id=claim_id,
        claim_type="reported",
        text="Files on the share were altered.",
        epistemic_status="reported",
        supporting_source_ids=[source_id],
        supporting_citations=[CaseSourceCitation(source_id=source_id, exact_quote=quote)],
    )


def trace_of(*claims: CaseAnalysisClaim) -> CaseAnalysisTrace:
    return CaseAnalysisTrace(
        analysis_mode="case_overview", summary="Files were altered.", claims=list(claims)
    )


def test_a_quote_that_is_in_the_source_counts_as_verified():
    bundle, source_id = bundle_and_id()
    trace = resolve_case_trace(trace_of(claim(source_id, "A-01", TEXT)), bundle)

    assert trace.grounding.claims == 1
    assert trace.grounding.citations_claimed == 1
    assert trace.grounding.citations_verified == 1
    assert trace.grounding.claims_without_citation == 0


def test_an_invented_quote_is_dropped_and_counted():
    """The claim survives, as it always did. Now the loss is on the record."""

    bundle, source_id = bundle_and_id()
    trace = resolve_case_trace(
        trace_of(claim(source_id, "A-01", "There were no issues with the finance drive.")),
        bundle,
    )

    assert trace.claims[0].supporting_citations == []
    assert trace.grounding.citations_claimed == 1
    assert trace.grounding.citations_verified == 0
    assert trace.grounding.citations_unfound == 1
    assert trace.grounding.citations_paraphrased == 0
    assert trace.grounding.claims_without_citation == 1


def test_a_loose_quotation_of_a_real_sentence_is_counted_apart():
    """Quoting badly and inventing evidence are not the same failure."""

    bundle, source_id = bundle_and_id()
    trace = resolve_case_trace(
        trace_of(
            claim(source_id, "A-01", "Filenames were changed and a text file demanded contact")
        ),
        bundle,
    )

    assert trace.grounding.citations_verified == 0
    assert trace.grounding.citations_paraphrased == 1
    assert trace.grounding.citations_unfound == 0


def test_a_thai_quote_written_with_the_decomposed_vowel_still_matches():
    """SARA AM has two forms that look identical and compare unequal."""

    thai = "พนักงานสอบสวนรวบรวมสำนวนคดีไว้แล้ว"
    source_id = str(uuid4())
    bundle = CaseSourceBundle(
        revision=1,
        sources=(CaseSourceItem(source_id=source_id, source_kind="narrative", text=thai),),
    )
    decomposed = "สำนวนคดี".replace("ำ", "ํา")
    assert decomposed != "สำนวนคดี"

    trace = resolve_case_trace(trace_of(claim(source_id, "A-01", decomposed)), bundle)
    assert trace.grounding.citations_verified == 1
    assert trace.claims[0].supporting_citations[0].exact_quote == "สำนวนคดี"


def test_the_counts_separate_the_grounded_from_the_rest():
    bundle, source_id = bundle_and_id()
    trace = resolve_case_trace(
        trace_of(
            claim(source_id, "A-01", TEXT),
            claim(source_id, "A-02", "A quotation from nowhere."),
            claim(source_id, "A-03", "Another one."),
        ),
        bundle,
    )

    assert trace.grounding.claims == 3
    assert trace.grounding.citations_claimed == 3
    assert trace.grounding.citations_verified == 1
    assert trace.grounding.claims_without_citation == 2


def test_the_counts_always_add_up_to_what_was_claimed():
    """A citation is verified, or clumsy, or invented — never two of those.

    A quote the resolver had to repair is kept under the source's spelling
    rather than the model's, which once made it count as verified and as
    missing at the same time.
    """

    thai = "พนักงานสอบสวนรวบรวมสำนวนคดีไว้แล้ว"
    source_id = str(uuid4())
    bundle = CaseSourceBundle(
        revision=1,
        sources=(CaseSourceItem(source_id=source_id, source_kind="narrative", text=thai),),
    )
    trace = resolve_case_trace(
        trace_of(claim(source_id, "A-01", "สำนวนคดี".replace("ำ", "ํา"))), bundle
    )

    grounding = trace.grounding
    assert grounding.citations_verified == 1
    assert (
        grounding.citations_verified + grounding.citations_paraphrased + grounding.citations_unfound
        == grounding.citations_claimed
    )
