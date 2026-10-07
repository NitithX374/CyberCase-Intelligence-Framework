from __future__ import annotations

import json
from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.analysis.schemas import CaseAnalysisResultRead
from app.analysis.write import reading_payload
from app.chat.compose import analysis_payload
from app.llm.schema import structured_output_schema
from app.sources.bundle import CaseSourceBundle, CaseSourceItem
from app.trace.bind import resolve_case_trace
from app.trace.claims import (
    CaseAnalysisClaim,
    CaseReviewFlag,
    CaseSourceCitation,
    normalized_citation,
    stored_review_flags,
)
from app.trace.quote_binding import QuoteSearch, added_citations
from app.trace.quotes import (
    MEANING_MARKS,
    IndexedText,
    edge_marks,
    ignored_marks,
    meaning_marks,
)
from app.trace.trace import (
    CaseAnalysisTrace,
    CaseProviderAnalysis,
    CaseProviderReading,
    CaseProviderReadingReply,
)


def bound(source: str, *quotes: str) -> CaseAnalysisTrace:
    source_id = str(uuid4())
    bundle = CaseSourceBundle(
        revision=1,
        sources=(CaseSourceItem(source_id=source_id, source_kind="narrative", text=source),),
    )
    trace = CaseAnalysisTrace(
        analysis_mode="case_overview",
        summary="The money was sent.",
        claims=[
            CaseAnalysisClaim(
                claim_id="A-01",
                claim_type="reported",
                text="The money was sent.",
                epistemic_status="reported",
                supporting_source_ids=[source_id],
                supporting_citations=[
                    CaseSourceCitation(source_id=source_id, exact_quote=quote) for quote in quotes
                ],
            )
        ],
    )
    return resolve_case_trace(trace, bundle)


def flags(source: str, quote: str) -> list[str]:
    citations = bound(source, quote).claims[0].supporting_citations
    assert len(citations) == 1, citations
    for flag in citations[0].review_flags:
        assert (flag.kind, flag.verdict) == ("meaning_mark", "rule_warning")
    return [flag.detail for flag in citations[0].review_flags]


def test_a_mark_the_format_tier_ignored_in_the_source_is_flagged():
    source = "The money was transferred? Yes it was sent on Monday."

    assert flags(source, "The money was transferred Yes it was sent") == ["? ignored"]


def test_a_mark_the_format_tier_ignored_in_the_quote_is_flagged():
    source = "The money was transferred Yes it was sent on Monday."

    assert flags(source, "The money was transferred? Yes it was sent") == ["? ignored"]


def test_a_tilde_the_markup_tier_ignored_is_flagged():
    source = "Paid about ~5,000 baht to the vendor on Monday."

    assert flags(source, "Paid about 5,000 baht to the vendor on Monday") == ["~ ignored"]


@pytest.mark.parametrize(
    ("written", "located", "ignored"),
    [
        ("%", "", ["%"]),
        ("", "%", ["%"]),
        ("50%", "50", ["%"]),
        ("a ~ b", "a b", ["~"]),
        ("x ? y", "x y", ["?"]),
        ("≈5", "5", ["≈"]),
        ("±5", "5", ["±"]),
        ("5 < 6", "5 6", ["<"]),
        ("5 > 6", "5 6", [">"]),
        ("?%", "", ["?", "%"]),
        ("50%", "50?", ["%", "?"]),
    ],
)
def test_a_mark_on_one_side_of_a_difference_and_not_the_other_is_ignored(written, located, ignored):
    assert ignored_marks([(written, located)]) == ignored


@pytest.mark.parametrize(
    ("written", "located"),
    [
        ("50%", "50%"),
        ("50%", "50 %"),
        ("said?", "asked?"),
        ("apple", "Apple"),
        ("resign", "re-sign"),
        ("1,500,000", "1500000"),
        ("５０％", "50%"),
        ("<page_number>3</page_number>", ""),
        ("", "</page_number>"),
    ],
)
def test_a_mark_both_sides_share_or_that_is_not_one_is_not_ignored(written, located):
    assert ignored_marks([(written, located)]) == []


def test_every_mark_is_a_meaning_mark():
    assert frozenset("?~≈±%<>") == MEANING_MARKS
    assert "-" not in MEANING_MARKS
    assert meaning_marks("a? b~ c≈ d± e% f< g>") == list("?~≈±%<>")


@pytest.mark.parametrize("mark", sorted(MEANING_MARKS))
def test_a_mark_right_after_an_exact_quote_is_flagged(mark):
    source = f"The count was 50{mark} in total over the whole year."

    assert flags(source, "The count was 50") == [f"{mark} edge"]


@pytest.mark.parametrize("mark", sorted(MEANING_MARKS))
def test_a_mark_right_before_an_exact_quote_is_flagged(mark):
    source = f"Reported {mark}50 incidents in total over the whole year."

    assert flags(source, "50 incidents in total over the whole year") == [f"{mark} edge"]


@pytest.mark.parametrize(
    "source",
    [
        "The money was sent ? he said so on Monday.",
        f"The money was sent{chr(0xA0)}? he said so on Monday.",
        f"The money was sent{chr(9)}? he said so on Monday.",
    ],
)
def test_a_mark_up_to_two_characters_away_across_spaces_is_flagged(source):
    assert flags(source, "The money was sent") == ["? edge"]


def test_a_tilde_up_to_two_characters_before_the_quote_is_flagged():
    source = "The accountant said ~ 5,000 baht were sent."

    assert flags(source, "5,000 baht were sent") == ["~ edge"]


@pytest.mark.parametrize(
    "source",
    [
        "The money was sent  ? he said so on Monday.",
        "The money was sent   ? he said so on Monday.",
        "The money was sent\n? he said so on Monday.",
        "The money was sent\r\n? he said so on Monday.",
        "The money was sent.? he said so on Monday.",
        "The money was sent. He said so on Monday.",
    ],
)
def test_a_mark_beyond_two_characters_on_the_next_line_or_behind_another_character_is_not(
    source,
):
    assert flags(source, "The money was sent") == []


def test_a_mark_on_the_line_before_the_quote_is_not_flagged():
    source = "Was it so?\nThe money was sent to the vendor on Monday."

    assert flags(source, "The money was sent to the vendor on Monday") == []


def test_a_mark_inside_the_quote_is_not_flagged():
    source = "The rate was 50% in total over the whole year."

    assert flags(source, "The rate was 50% in total over the whole year") == []


def test_a_mark_in_both_the_quote_and_the_source_of_a_tolerated_difference_is_not_flagged():
    source = "The rate was 50% in total, over the whole year."

    assert flags(source, "The rate was 50% in total over the whole year") == []


def test_curly_against_straight_quote_marks_is_not_flagged():
    source = "He said “yes” and left the room quickly today."

    assert flags(source, 'He said "yes" and left the room quickly today') == []


def test_a_minus_sign_is_not_a_meaning_mark():
    source = "The accountant paid -5,000 baht to the vendor on Monday."

    assert flags(source, "5,000 baht to the vendor on Monday") == []
    assert flags(source, "The accountant paid -5,000 baht to the vendor") == []


def test_a_fullwidth_mark_counts_as_the_plain_mark():
    assert flags("Was it sent？ He said so on Monday.", "Was it sent") == ["? edge"]
    assert flags("The rate was 50％ in total.", "The rate was 50") == ["% edge"]
    assert flags("The rate was 50％ in total.", "The rate was 50% in total") == []


def test_the_brackets_of_an_ocr_tag_are_not_marks():
    source = "Page text ends here<page_number>3</page_number> and goes on."

    assert flags(source, "Page text ends here") == []
    assert (
        flags("Text before</page_number> the next page starts here.", "the next page starts here")
        == []
    )


def test_a_thai_quote_followed_by_a_mark_is_flagged():
    assert flags("โอนเงินแล้ว? ตามที่ผู้เสียหายแจ้ง", "โอนเงินแล้ว") == ["? edge"]


def test_a_quote_flagged_for_both_reasons_carries_both_flags():
    source = "Paid about ~5,000 baht to the vendor? Monday it was."

    assert flags(source, "Paid about 5,000 baht to the vendor") == ["~ ignored", "? edge"]


def test_edge_marks_look_at_the_given_span_of_the_source():
    source = IndexedText("a ? b ~ c")

    assert edge_marks(source, 0, 1) == ["?"]
    assert edge_marks(source, 4, 5) == ["?", "~"]
    assert edge_marks(source, 8, 9) == ["~"]


def test_a_flag_changes_no_status_support_or_count():
    marked = bound("The money was sent? He said so on Monday.", "The money was sent")
    plain = bound("The money was sent. He said so on Monday.", "The money was sent")

    for trace in (marked, plain):
        [claim] = trace.claims
        assert claim.epistemic_status == "reported"
        assert [c.exact_quote for c in claim.supporting_citations] == ["The money was sent"]
        assert claim.unverified_citations == []
        assert trace.grounding.citations_verified == 1
        assert trace.grounding.citations_unfound == 0
    assert marked.grounding.citations_marked == 1
    assert plain.grounding.citations_marked == 0


def test_the_report_counts_the_citations_that_carry_a_flag():
    source = "The money was sent? Okay. He said so. Then it was sent to the vendor ~5,000 baht."

    trace = bound(source, "The money was sent", "He said so", "Then it was sent to the vendor")

    assert trace.grounding.citations_claimed == 3
    assert trace.grounding.citations_marked == 2


def test_binding_a_bound_trace_again_gives_the_same_flags():
    source_id = str(uuid4())
    source = "The money was sent? He said so on Monday."
    bundle = CaseSourceBundle(
        revision=1,
        sources=(CaseSourceItem(source_id=source_id, source_kind="narrative", text=source),),
    )
    first = bound(source, "The money was sent")
    first = first.model_copy(
        update={
            "claims": [
                claim.model_copy(
                    update={
                        "supporting_source_ids": [source_id],
                        "supporting_citations": [
                            c.model_copy(update={"source_id": source_id})
                            for c in claim.supporting_citations
                        ],
                    }
                )
                for claim in first.claims
            ]
        }
    )

    again = resolve_case_trace(first, bundle)

    [citation] = again.claims[0].supporting_citations
    assert [flag.detail for flag in citation.review_flags] == ["? edge"]


def test_a_flag_a_stored_citation_carries_is_recomputed_not_trusted():
    source_id = str(uuid4())
    source = "The money was sent. He said so on Monday."
    bundle = CaseSourceBundle(
        revision=1,
        sources=(CaseSourceItem(source_id=source_id, source_kind="narrative", text=source),),
    )
    stale = CaseSourceCitation(
        source_id=source_id,
        exact_quote="The money was sent",
        review_flags=[CaseReviewFlag(kind="meaning_mark", verdict="rule_warning", detail="? edge")],
    )
    trace = CaseAnalysisTrace(
        analysis_mode="case_overview",
        summary="The money was sent.",
        claims=[
            CaseAnalysisClaim(
                claim_id="A-01",
                claim_type="reported",
                text="The money was sent.",
                epistemic_status="reported",
                supporting_source_ids=[source_id],
                supporting_citations=[stale],
            )
        ],
    )

    [citation] = resolve_case_trace(trace, bundle).claims[0].supporting_citations

    assert citation.review_flags == []


def test_a_chat_citation_is_found_as_before_and_carries_no_flag():
    source_id = "S1"
    registry = {
        source_id: CaseSourceItem(source_id, "narrative", "The money was sent? He said so.")
    }
    offered = [CaseSourceCitation(source_id=source_id, exact_quote="The money was sent")]

    [[found]] = added_citations(offered, registry, QuoteSearch(registry))

    assert found.exact_quote == "The money was sent"
    assert found.review_flags == []


def test_two_written_quotes_for_one_passage_carry_its_flag_once():
    source = "The money was sent? He said so on Monday."

    trace = bound(source, "The money was sent", "The money was sent")

    [citation] = trace.claims[0].supporting_citations
    assert [flag.detail for flag in citation.review_flags] == ["? edge"]


def reading_of(trace: CaseAnalysisTrace) -> CaseProviderReading:
    return CaseProviderReading(
        version="case_analysis_trace_v1",
        claims=trace.claims,
    )


def test_neither_model_is_shown_the_flags():
    trace = bound("The money was sent? He said so on Monday.", "The money was sent")
    assert trace.claims[0].supporting_citations[0].review_flags

    for payload in (reading_payload(reading_of(trace)), analysis_payload(trace, None)):
        assert payload["claims"][0]["supporting_citations"]
        assert "review_flags" not in json.dumps(payload)


def test_the_flags_are_in_no_schema_the_model_fills():
    for schema in (
        CaseProviderReadingReply.model_json_schema(),
        structured_output_schema(CaseProviderAnalysis),
    ):
        assert "review_flags" not in json.dumps(schema)


def test_a_flag_a_reader_writes_into_a_citation_is_rejected():
    with pytest.raises(ValueError, match="review_flags"):
        CaseProviderReadingReply.model_validate(
            {
                "version": "case_analysis_trace_v1",
                "claims": [
                    {
                        "claim_id": "A-01",
                        "claim_type": "reported",
                        "text": "The money was sent.",
                        "epistemic_status": "reported",
                        "supporting_citations": [
                            {
                                "source_id": "S1",
                                "evidence_unit_ids": ["S1:U001-0000000000000000"],
                                "review_flags": [
                                    {
                                        "kind": "meaning_mark",
                                        "verdict": "rule_warning",
                                        "detail": "? edge",
                                    }
                                ],
                            }
                        ],
                    }
                ],
            }
        )


def stored() -> tuple[CaseAnalysisTrace, dict]:
    trace = bound("The money was sent? He said so on Monday.", "The money was sent")
    return trace, json.loads(trace.model_dump_json())


def test_a_citation_stored_before_the_flags_existed_still_validates():
    _, written = stored()
    for claim_json in written["claims"]:
        for citation in claim_json["supporting_citations"]:
            del citation["review_flags"]
    del written["grounding"]["citations_marked"]

    reloaded = CaseAnalysisTrace.model_validate(written)

    assert reloaded.claims[0].supporting_citations[0].review_flags == []
    assert reloaded.grounding.citations_marked == 0
    assert CaseSourceCitation.model_validate({"source_id": "S1"}).review_flags == []


def test_the_flags_survive_the_stored_trace_being_read_back():
    trace, written = stored()

    reloaded = CaseAnalysisTrace.model_validate(written)

    assert reloaded == trace
    assert [f.detail for f in reloaded.claims[0].supporting_citations[0].review_flags] == ["? edge"]
    assert reloaded.grounding.citations_marked == 1


def test_the_api_read_model_keeps_the_flags():
    trace, written = stored()

    read = CaseAnalysisResultRead.model_validate(
        {
            "id": uuid4(),
            "case_id": uuid4(),
            "source_revision": 1,
            "status": "validated",
            "summary": "The money was sent.",
            "trace_json": written,
            "pipeline_config": {},
            "created_at": datetime(2026, 10, 4, tzinfo=UTC),
        }
    )

    [citation] = read.trace_json.claims[0].supporting_citations
    assert [f.detail for f in citation.review_flags] == ["? edge"]
    assert read.trace_json.grounding.citations_marked == 1


def test_a_stored_list_with_junk_in_it_keeps_only_the_valid_flags():
    valid = {"kind": "meaning_mark", "verdict": "rule_warning", "detail": "? edge"}

    assert [f.detail for f in stored_review_flags(["junk", valid, 3, {"kind": "other"}])] == [
        "? edge"
    ]
    assert stored_review_flags("oops") == []
    assert (
        normalized_citation({"source_id": "S1", "exact_quote": "q", "review_flags": "oops"})[
            "review_flags"
        ]
        == []
    )
