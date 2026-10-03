from __future__ import annotations

from uuid import uuid4

from app.sources.bundle import CaseSourceBundle, CaseSourceItem
from app.trace import quotes
from app.trace.bind import resolve_case_trace
from app.trace.claims import CaseAnalysisClaim, CaseSourceCitation
from app.trace.trace import CaseAnalysisTrace

TEXT = "Filenames had been changed and a text file demanded contact by email."


def bundle_and_id(text: str = TEXT) -> tuple[CaseSourceBundle, str]:
    source_id = str(uuid4())
    return (
        CaseSourceBundle(
            revision=1,
            sources=(CaseSourceItem(source_id=source_id, source_kind="narrative", text=text),),
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


def test_a_reported_claim_without_a_verified_quote_is_not_confirmed():
    bundle, source_id = bundle_and_id()
    invented = claim(source_id, "A-01", "There were no issues with the finance drive.")
    suspected = claim(source_id, "A-02", "Nothing else was touched.").model_copy(
        update={"text": "Other shares may be affected.", "epistemic_status": "suspected"}
    )
    trace = resolve_case_trace(
        trace_of(invented, suspected, claim(source_id, "A-03", TEXT)), bundle
    )

    assert [c.epistemic_status for c in trace.claims] == ["not_confirmed", "suspected", "reported"]


def test_a_quote_cut_with_an_ellipsis_at_either_end_is_found():
    bundle, source_id = bundle_and_id()
    trace = resolve_case_trace(
        trace_of(
            claim(source_id, "A-01", "...had been changed and a text file..."),
            claim(source_id, "A-02", "… demanded contact by email."),
            claim(source_id, "A-03", "[...] a text file demanded"),
        ),
        bundle,
    )

    assert [c.supporting_citations[0].exact_quote for c in trace.claims] == [
        "had been changed and a text file",
        "demanded contact by email.",
        "a text file demanded",
    ]
    assert [c.epistemic_status for c in trace.claims] == ["reported", "reported", "reported"]
    assert trace.grounding.citations_verified == 3
    assert trace.grounding.citations_pointed == 0


GAPPED = "Filenames had been changed ... demanded contact by email."


def test_a_quote_with_a_gap_is_stored_as_one_citation_per_piece():
    bundle, source_id = bundle_and_id()
    trace = resolve_case_trace(trace_of(claim(source_id, "A-01", GAPPED)), bundle)

    assert [c.exact_quote for c in trace.claims[0].supporting_citations] == [
        "Filenames had been changed",
        "demanded contact by email.",
    ]


def test_a_quote_split_into_pieces_is_counted_once_and_keeps_its_claim_reported():
    bundle, source_id = bundle_and_id()
    trace = resolve_case_trace(trace_of(claim(source_id, "A-01", GAPPED)), bundle)

    assert len(trace.claims[0].supporting_citations) == 2
    assert trace.claims[0].epistemic_status == "reported"
    assert trace.grounding.citations_claimed == 1
    assert trace.grounding.citations_verified == 1
    assert trace.grounding.citations_duplicated == 0
    assert_counts_add_up(trace)


def test_a_gapped_quote_whose_later_piece_appears_twice_after_the_first_is_dropped():
    text = "The share was encrypted. Then a note was left. Later a note was left again."
    bundle, source_id = bundle_and_id(text)
    trace = resolve_case_trace(
        trace_of(claim(source_id, "A-01", "The share was encrypted ... a note was left")), bundle
    )

    assert trace.claims[0].supporting_citations == []
    assert trace.claims[0].epistemic_status == "not_confirmed"
    assert trace.grounding.citations_verified == 0
    assert_counts_add_up(trace)


def test_a_gapped_quote_with_a_piece_found_twice_is_stored_as_one_merged_span():
    text = "Payroll was moved. The attacker logged in at night. Payroll was moved."
    bundle, source_id = bundle_and_id(text)
    trace = resolve_case_trace(
        trace_of(claim(source_id, "A-01", "The attacker logged in ... Payroll was moved.")), bundle
    )

    assert [c.exact_quote for c in trace.claims[0].supporting_citations] == [
        "The attacker logged in at night. Payroll was moved."
    ]
    assert trace.claims[0].epistemic_status == "reported"
    assert trace.grounding.citations_verified == 1
    assert_counts_add_up(trace)


def test_ellipses_at_the_ends_are_trimmed_before_a_gapped_quote_is_split():
    bundle, source_id = bundle_and_id()
    trace = resolve_case_trace(
        trace_of(
            claim(source_id, "A-01", "...had been changed and a text file..."),
            claim(source_id, "A-02", "… Filenames had been changed … demanded contact …"),
        ),
        bundle,
    )

    assert [[c.exact_quote for c in item.supporting_citations] for item in trace.claims] == [
        ["had been changed and a text file"],
        ["Filenames had been changed", "demanded contact"],
    ]


def test_a_piece_also_cited_on_its_own_is_kept_once():
    bundle, source_id = bundle_and_id()
    written = claim(source_id, "A-01", GAPPED).model_copy(
        update={
            "supporting_citations": [
                CaseSourceCitation(source_id=source_id, exact_quote=GAPPED),
                CaseSourceCitation(source_id=source_id, exact_quote="Filenames had been changed"),
            ]
        }
    )

    trace = resolve_case_trace(trace_of(written), bundle)

    assert [c.exact_quote for c in trace.claims[0].supporting_citations] == [
        "Filenames had been changed",
        "demanded contact by email.",
    ]
    assert trace.grounding.citations_claimed == 2
    assert trace.grounding.citations_verified == 1
    assert trace.grounding.citations_duplicated == 1
    assert_counts_add_up(trace)


def test_a_gapped_quote_after_one_of_its_pieces_counts_for_the_piece_it_adds():
    bundle, source_id = bundle_and_id()
    written = claim(source_id, "A-01", GAPPED).model_copy(
        update={
            "supporting_citations": [
                CaseSourceCitation(source_id=source_id, exact_quote="Filenames had been changed"),
                CaseSourceCitation(source_id=source_id, exact_quote=GAPPED),
            ]
        }
    )

    trace = resolve_case_trace(trace_of(written), bundle)

    assert [c.exact_quote for c in trace.claims[0].supporting_citations] == [
        "Filenames had been changed",
        "demanded contact by email.",
    ]
    assert trace.grounding.citations_verified == 2
    assert trace.grounding.citations_duplicated == 0
    assert_counts_add_up(trace)


OCR_TABLE = (
    "Transfer record\n"
    "<table>\n"
    "<tr><th>Date</th><th>Amount</th><th>To account</th></tr>\n"
    "<tr><td>3 March 2026</td><td>50,000 baht</td><td>123-4-56789</td></tr>\n"
    "<tr><td>5 March 2026</td><td>20,000 baht</td><td>987-6-54321</td></tr>\n"
    "</table>\n"
    "<page_number>2</page_number>"
)


def test_a_quote_inside_one_table_cell_is_found():
    bundle, source_id = bundle_and_id(OCR_TABLE)
    trace = resolve_case_trace(trace_of(claim(source_id, "A-01", "50,000 baht")), bundle)

    assert [c.exact_quote for c in trace.claims[0].supporting_citations] == ["50,000 baht"]


def test_a_quote_across_the_cells_of_a_table_row_is_found_with_the_tags_between():
    bundle, source_id = bundle_and_id(OCR_TABLE)
    trace = resolve_case_trace(
        trace_of(claim(source_id, "A-01", "3 March 2026 50,000 baht")), bundle
    )

    assert [c.exact_quote for c in trace.claims[0].supporting_citations] == [
        "3 March 2026</td><td>50,000 baht"
    ]
    assert trace.claims[0].epistemic_status == "reported"
    assert trace.grounding.citations_verified == 1
    assert_counts_add_up(trace)


def test_a_thai_quote_across_two_cells_or_a_page_number_is_found():
    text = (
        "<table><tr><td>โอนเงิน</td><td>50,000 บาท</td></tr></table>\n"
        "ผู้เสียหายโอนเงิน\n<page_number>3</page_number>\nให้ผู้ต้องหา"
    )
    bundle, source_id = bundle_and_id(text)
    trace = resolve_case_trace(
        trace_of(
            claim(source_id, "A-01", "โอนเงิน 50,000 บาท"),
            claim(source_id, "A-02", "ผู้เสียหายโอนเงินให้ผู้ต้องหา"),
        ),
        bundle,
    )

    assert [c.supporting_citations[0].exact_quote for c in trace.claims] == [
        "โอนเงิน</td><td>50,000 บาท",
        "ผู้เสียหายโอนเงิน\n<page_number>3</page_number>\nให้ผู้ต้องหา",
    ]


def test_cells_from_different_rows_still_do_not_make_a_quote():
    bundle, source_id = bundle_and_id(OCR_TABLE)
    trace = resolve_case_trace(
        trace_of(claim(source_id, "A-01", "3 March 2026 20,000 baht")), bundle
    )

    assert trace.claims[0].supporting_citations == []
    assert trace.claims[0].epistemic_status == "not_confirmed"
    assert_counts_add_up(trace)


def test_a_quote_across_cells_that_matches_twice_is_refused():
    row = "<tr><td>1 April 2026</td><td>10,000 baht</td></tr>\n"
    bundle, source_id = bundle_and_id(f"<table>\n{row}{row}</table>")
    trace = resolve_case_trace(
        trace_of(claim(source_id, "A-01", "1 April 2026 10,000 baht")), bundle
    )

    assert trace.claims[0].supporting_citations == []
    assert trace.claims[0].epistemic_status == "not_confirmed"


def test_a_quote_with_other_quotation_marks_than_the_source_is_found():
    text = 'Abta said the "vast majority" of the 43,000 people affected had registered.'
    bundle, source_id = bundle_and_id(text)
    trace = resolve_case_trace(
        trace_of(
            claim(source_id, "A-01", "the 'vast majority' of the 43,000 people affected"),
            claim(source_id, "A-02", "the “vast majority” of the 43,000"),
        ),
        bundle,
    )

    assert [c.supporting_citations[0].exact_quote for c in trace.claims] == [
        'the "vast majority" of the 43,000 people affected',
        'the "vast majority" of the 43,000',
    ]
    assert [c.epistemic_status for c in trace.claims] == ["reported", "reported"]


def test_an_invented_quote_is_dropped_and_counted():
    bundle, source_id = bundle_and_id()
    trace = resolve_case_trace(
        trace_of(claim(source_id, "A-01", "There were no issues with the finance drive.")),
        bundle,
    )

    assert trace.claims[0].supporting_citations == []
    assert trace.grounding.citations_claimed == 1
    assert trace.grounding.citations_verified == 0
    assert trace.grounding.citations_unfound == 1
    assert trace.grounding.citations_pointed == 0
    assert trace.grounding.claims_without_citation == 1


def test_a_near_quotation_of_a_real_sentence_is_kept_with_a_pointer():
    bundle, source_id = bundle_and_id()
    trace = resolve_case_trace(
        trace_of(
            claim(source_id, "A-01", "Filenames were changed and a text file demanded contact")
        ),
        bundle,
    )

    [unverified] = trace.claims[0].unverified_citations
    assert trace.claims[0].supporting_citations == []
    assert trace.claims[0].epistemic_status == "not_confirmed"
    assert unverified.role == "supporting"
    assert unverified.written_quote == "Filenames were changed and a text file demanded contact"
    assert unverified.near_passage.source_text == (
        "Filenames had been changed and a text file demanded contact"
    )
    assert trace.grounding.citations_verified == 0
    assert trace.grounding.citations_pointed == 1
    assert trace.grounding.citations_unfound == 0


def test_a_thai_quote_written_with_the_decomposed_vowel_still_matches():
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
    thai = "พนักงานสอบสวนรวบรวมสำนวนคดีไว้แล้ว"
    source_id = str(uuid4())
    bundle = CaseSourceBundle(
        revision=1,
        sources=(CaseSourceItem(source_id=source_id, source_kind="narrative", text=thai),),
    )
    trace = resolve_case_trace(
        trace_of(claim(source_id, "A-01", "สำนวนคดี".replace("ำ", "ํา"))), bundle
    )

    assert trace.grounding.citations_verified == 1
    assert_counts_add_up(trace)


def assert_counts_add_up(trace: CaseAnalysisTrace) -> None:
    grounding = trace.grounding
    assert (
        grounding.citations_verified
        + grounding.citations_duplicated
        + grounding.citations_pointed
        + grounding.citations_unfound
        == grounding.citations_claimed
    )


def test_a_quote_is_kept_when_its_source_is_left_out_of_the_role():
    bundle, source_id = bundle_and_id()
    written = claim(source_id, "A-01", TEXT).model_copy(update={"supporting_source_ids": []})

    trace = resolve_case_trace(trace_of(written), bundle)

    assert trace.claims[0].supporting_source_ids == [source_id]
    assert [c.exact_quote for c in trace.claims[0].supporting_citations] == [TEXT]
    assert trace.grounding.citations_verified == 1
    assert_counts_add_up(trace)


def test_an_invented_quote_does_not_add_its_source_to_the_role():
    bundle, source_id = bundle_and_id()
    other_id = str(uuid4())
    bundle = CaseSourceBundle(
        revision=1,
        sources=(
            *bundle.sources,
            CaseSourceItem(
                source_id=other_id, source_kind="narrative", text="The backup ran overnight."
            ),
        ),
    )
    written = claim(source_id, "A-01", TEXT).model_copy(
        update={
            "supporting_citations": [
                CaseSourceCitation(source_id=source_id, exact_quote=TEXT),
                CaseSourceCitation(
                    source_id=other_id, exact_quote="Payroll was wired to an unknown account."
                ),
            ]
        }
    )

    trace = resolve_case_trace(trace_of(written), bundle)

    assert trace.claims[0].supporting_source_ids == [source_id]
    assert [c.source_id for c in trace.claims[0].supporting_citations] == [source_id]
    assert trace.grounding.citations_unfound == 1
    assert_counts_add_up(trace)


def test_a_repeated_quote_is_kept_once_and_counted_as_a_duplicate():
    bundle, source_id = bundle_and_id()
    citation = CaseSourceCitation(source_id=source_id, exact_quote=TEXT)
    written = claim(source_id, "A-01", TEXT).model_copy(
        update={"supporting_citations": [citation, citation]}
    )

    trace = resolve_case_trace(trace_of(written), bundle)

    assert len(trace.claims[0].supporting_citations) == 1
    assert trace.grounding.citations_claimed == 2
    assert trace.grounding.citations_verified == 1
    assert trace.grounding.citations_duplicated == 1
    assert_counts_add_up(trace)


def test_an_elided_quote_that_widens_past_a_citation_is_dropped_and_counted():
    head = "The attacker logged in to the VPN gateway."
    tail = "The attacker exfiltrated the payroll archive."
    filler = " ".join(f"Routine log line {n} recorded nothing unusual." for n in range(80))
    bundle, source_id = bundle_and_id(f"{head} {filler} {tail}")

    trace = resolve_case_trace(
        trace_of(
            claim(source_id, "A-01", f"{head} ... {tail}"),
            claim(source_id, "A-02", head),
        ),
        bundle,
    )

    assert trace.claims[0].supporting_citations == []
    assert [c.exact_quote for c in trace.claims[1].supporting_citations] == [head]
    assert trace.grounding.citations_verified == 1
    assert trace.grounding.citations_duplicated == 0
    assert_counts_add_up(trace)


def test_a_quote_the_markdown_match_widens_past_a_citation_is_dropped_and_counted():
    words = [f"tok{n:03d}" for n in range(250)]
    bundle, source_id = bundle_and_id("\n\n".join(f"**{word}**" for word in words))

    trace = resolve_case_trace(trace_of(claim(source_id, "A-01", " ".join(words))), bundle)

    assert trace.claims[0].supporting_citations == []
    assert trace.grounding.citations_verified == 0
    assert trace.grounding.citations_duplicated == 0
    assert_counts_add_up(trace)


def test_a_source_is_folded_and_formed_once_however_many_quotes_are_sought_in_it(monkeypatch):
    folded: list[str] = []
    split: list[str] = []
    fold, form = quotes.folded, quotes.format_form
    monkeypatch.setattr(quotes, "folded", lambda text: folded.append(text) or fold(text))
    monkeypatch.setattr(quotes, "format_form", lambda text: split.append(text) or form(text))
    bundle, source_id = bundle_and_id()
    loose = [
        "Filenames were changed and a text file demanded contact",
        "Filenames were altered and a text file demanded contact",
        "Filenames had changed and the text file demanded contact",
    ]

    trace = resolve_case_trace(
        trace_of(*(claim(source_id, f"A-0{n}", quote) for n, quote in enumerate(loose, 1))),
        bundle,
    )

    assert trace.grounding.citations_pointed == 3
    assert folded.count(TEXT) == 1
    assert split.count(TEXT) == 1
