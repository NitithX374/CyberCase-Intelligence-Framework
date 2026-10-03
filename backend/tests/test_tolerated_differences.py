from __future__ import annotations

import json
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.analysis.schemas import CaseAnalysisResultRead
from app.analysis.write import reading_from, reading_payload
from app.chat.compose import analysis_payload
from app.llm.schema import structured_output_schema
from app.reports.display import report_findings
from app.reports.generate import validated_trace
from app.sources.bundle import CaseSourceBundle, CaseSourceItem
from app.trace.bind import QuoteSearch, added_citations, resolve_case_trace, tolerated_in
from app.trace.claims import CaseAnalysisClaim, CaseSourceCitation
from app.trace.quotes import MAX_TOLERATED_DIFFERENCES, locate_quote, tolerated_differences
from app.trace.trace import (
    CaseAnalysisTrace,
    CaseProviderAnalysis,
    CaseProviderReading,
    CaseProviderReadingReply,
)

SOURCE = "The accountant paid -5,000 baht to the vendor on Monday."


@pytest.mark.parametrize(
    ("source", "quote", "tier"),
    [
        ("The attacker logged in at noon.", "The attacker logged in", "exact"),
        (
            "The ﬁnal report was signed on Monday.",
            "The final report was signed on Monday",
            "folded",
        ),
        (
            "First came the alarm. Then the logs were wiped. Last the backups failed.",
            "First came the alarm ... Last the backups failed",
            "ellipsis",
        ),
        ("The **attacker** logged in on Monday.", "The attacker logged in on Monday", "relaxed"),
        (
            "Mr. Smith, the accountant, paid 5,000 baht.",
            "Mr Smith the accountant paid 5,000 baht",
            "format",
        ),
    ],
)
def test_the_locator_says_which_tier_accepted_a_quote(source, quote, tier):
    located = locate_quote(source, quote)

    assert located is not None
    assert located.tier == tier


def test_a_quote_nothing_locates_has_no_tier():
    assert locate_quote(SOURCE, "The accountant stole two million baht") is None


@pytest.mark.parametrize(
    ("source", "quote", "differences"),
    [
        (SOURCE, "paid 5,000 baht", [("", "-")]),
        ("We must re-sign the lease today.", "must resign the lease", [("resign", "re-sign")]),
        (
            "Our therapist said so after the meeting.",
            "Our the rapist said so after the meeting",
            [("the rapist", "therapist")],
        ),
        (
            "Apple pays 5,000 baht each month.",
            "apple pays 5,000 baht each month",
            [("apple", "Apple")],
        ),
    ],
)
def test_a_tolerated_quote_shows_what_the_locator_ignored(source, quote, differences):
    assert QuoteSearch({"S": CaseSourceItem("S", "narrative", source)}).located("S", quote)

    shown = tolerated_in(source, quote)

    assert [(item.written, item.source) for item in shown] == differences


@pytest.mark.parametrize(
    ("source", "quote", "tier"),
    [
        ("The attacker logged in at noon.", "The attacker logged in", "exact"),
        (
            "First came the alarm. Then the logs were wiped. Last the backups failed.",
            "First came the alarm ... Last the backups failed",
            "ellipsis",
        ),
    ],
)
def test_an_exact_quote_and_ellipsis_pieces_have_nothing_to_show(source, quote, tier):
    assert locate_quote(source, quote).tier == tier
    assert tolerated_in(source, quote) == []


@pytest.mark.parametrize(
    ("written", "located"),
    [
        ("“Hello” world", "Hello world"),
        ('say "yes" now', "say yes now"),
        ("«bonjour» tout le monde", "bonjour tout le monde"),
        ("it’s done", "it's done"),
        ("two  spaces here", "two spaces here"),
    ],
)
def test_a_difference_in_quote_marks_or_spacing_between_words_is_not_shown(written, located):
    assert tolerated_differences(written, located) == ()


@pytest.mark.parametrize(
    ("written", "located", "shown"),
    [
        ("paid 5,000", "paid -5,000", (("", "-"),)),
        ("Apple", "apple", (("Apple", "apple"),)),
        ("resign", "re-sign", (("resign", "re-sign"),)),
        ("the rapist", "therapist", (("the rapist", "therapist"),)),
        ("sent 100 now", "sent +100 now", (("", "+"),)),
        ("e.mail it", "email it", (("e.mail", "email"),)),
        ("ﬁle it", "file it", (("ﬁle", "file"),)),
    ],
)
def test_a_dash_sign_case_punctuation_or_spacing_inside_a_word_is_shown(written, located, shown):
    assert tolerated_differences(written, located) == shown


def test_at_most_a_fixed_number_of_differences_are_kept():
    written = " ".join(f"alpha{n}" for n in range(MAX_TOLERATED_DIFFERENCES + 4))
    located = " ".join(f"omega{n}" for n in range(MAX_TOLERATED_DIFFERENCES + 4))

    shown = tolerated_differences(written, located)

    assert len(shown) == MAX_TOLERATED_DIFFERENCES
    assert shown[0] == ("alpha0", "omega0")


def claim(*quotes: str, source_id: str) -> CaseAnalysisClaim:
    return CaseAnalysisClaim(
        claim_id="A-01",
        claim_type="reported",
        text="The accountant paid the vendor.",
        epistemic_status="reported",
        supporting_source_ids=[source_id],
        supporting_citations=[
            CaseSourceCitation(source_id=source_id, exact_quote=quote) for quote in quotes
        ],
    )


def bundle_and_trace(*quotes: str) -> tuple[CaseSourceBundle, CaseAnalysisTrace]:
    source_id = str(uuid4())
    bundle = CaseSourceBundle(
        revision=1,
        sources=(CaseSourceItem(source_id=source_id, source_kind="narrative", text=SOURCE),),
    )
    trace = CaseAnalysisTrace(
        analysis_mode="case_overview",
        summary="The accountant paid the vendor.",
        claims=[claim(*quotes, source_id=source_id)],
    )
    return bundle, trace


QUOTES = ("paid 5,000 baht", "on Monday", "The accountant ... to the vendor")


def test_binding_records_the_differences_on_a_tolerated_citation_and_only_there():
    bundle, trace = bundle_and_trace(*QUOTES)

    bound = resolve_case_trace(trace, bundle)

    [reported] = bound.claims
    assert reported.epistemic_status == "reported"
    shown = {
        citation.exact_quote: [
            (item.written, item.source) for item in citation.tolerated_differences
        ]
        for citation in reported.supporting_citations
    }
    assert shown == {
        "paid -5,000 baht": [("", "-")],
        "on Monday": [],
        "The accountant": [],
        "to the vendor": [],
    }
    assert bound.grounding.citations_verified == 3


def test_binding_a_bound_trace_again_keeps_the_differences():
    bundle, trace = bundle_and_trace(*QUOTES)

    again = resolve_case_trace(resolve_case_trace(trace, bundle), bundle)

    [reported] = again.claims
    [tolerated] = [c for c in reported.supporting_citations if c.tolerated_differences]
    assert tolerated.exact_quote == "paid -5,000 baht"


def test_a_citation_stored_before_the_differences_existed_still_validates():
    bundle, trace = bundle_and_trace(*QUOTES)
    stored = json.loads(resolve_case_trace(trace, bundle).model_dump_json())
    for claim_json in stored["claims"]:
        for citation in claim_json["supporting_citations"]:
            del citation["tolerated_differences"]

    reloaded = CaseAnalysisTrace.model_validate(stored)

    assert [c.tolerated_differences for c in reloaded.claims[0].supporting_citations] == [[]] * 4
    assert CaseSourceCitation.model_validate({"source_id": "S1"}).tolerated_differences == []


def test_a_chat_citation_is_found_as_before_and_carries_no_differences():
    source_id = "S1"
    registry = {source_id: CaseSourceItem(source_id, "narrative", SOURCE)}
    offered = [CaseSourceCitation(source_id=source_id, exact_quote="paid 5,000 baht")]

    [[found]] = added_citations(offered, registry, QuoteSearch(registry))

    assert found.exact_quote == "paid -5,000 baht"
    assert found.tolerated_differences == []


def test_neither_model_is_shown_the_differences():
    bundle, trace = bundle_and_trace(*QUOTES)
    bound = resolve_case_trace(trace, bundle)
    reading = CaseProviderReading(
        version="case_analysis_trace_v1",
        claims=bound.claims,
        involved_parties=[],
        timeline=[],
        impacts=[],
    )
    assert any(c.tolerated_differences for c in bound.claims[0].supporting_citations)

    for payload in (reading_payload(reading), analysis_payload(bound, None)):
        assert payload["claims"][0]["supporting_citations"]
        assert "tolerated_differences" not in json.dumps(payload)


def test_the_differences_are_in_no_schema_the_model_fills():
    for schema in (
        CaseProviderReadingReply.model_json_schema(),
        structured_output_schema(CaseProviderAnalysis),
    ):
        assert '"tolerated_differences"' not in json.dumps(schema)


def test_a_difference_a_model_writes_into_a_citation_is_dropped():
    reply = CaseProviderReadingReply.model_validate(
        {
            "version": "case_analysis_trace_v1",
            "claims": [
                {
                    "claim_id": "A-01",
                    "claim_type": "reported",
                    "text": "The accountant paid the vendor.",
                    "epistemic_status": "reported",
                    "supporting_source_ids": ["S1"],
                    "supporting_citations": [
                        {
                            "source_id": "S1",
                            "exact_quote": "paid 5,000 baht",
                            "tolerated_differences": [{"written": "a", "source": "b"}],
                        }
                    ],
                }
            ],
            "involved_parties": [],
            "timeline": [],
            "impacts": [],
        }
    )

    [citation] = reading_from(reply).claims[0].supporting_citations

    assert citation.tolerated_differences == []


def shown(trace: CaseAnalysisTrace) -> dict[str, list[tuple[str, str]]]:
    return {
        citation.exact_quote: [
            (item.written, item.source) for item in citation.tolerated_differences
        ]
        for claim_item in trace.claims
        for citation in claim_item.supporting_citations
    }


def stored_trace() -> tuple[CaseAnalysisTrace, dict]:
    bundle, trace = bundle_and_trace(*QUOTES)
    bound = resolve_case_trace(trace, bundle)
    return bound, json.loads(bound.model_dump_json())


def test_the_differences_survive_the_stored_trace_being_read_back():
    bound, stored = stored_trace()

    reloaded = CaseAnalysisTrace.model_validate(stored)

    assert shown(reloaded) == shown(bound)
    assert shown(reloaded)["paid -5,000 baht"] == [("", "-")]


def test_the_api_read_model_keeps_the_differences():
    bound, stored = stored_trace()

    read = CaseAnalysisResultRead.model_validate(
        {
            "id": uuid4(),
            "case_id": uuid4(),
            "source_revision": 1,
            "status": "validated",
            "summary": "The accountant paid the vendor.",
            "trace_json": stored,
            "pipeline_config": {},
            "created_at": datetime(2026, 10, 3, tzinfo=UTC),
        }
    )

    assert shown(read.trace_json) == shown(bound)
    assert shown(read.trace_json)["paid -5,000 baht"] == [("", "-")]


def test_a_report_built_from_the_stored_analysis_has_the_differences():
    bound, stored = stored_trace()

    trace = validated_trace(SimpleNamespace(trace_json=stored))
    [finding], _ = report_findings(trace.claims, {})

    places = [[(p.written, p.source) for p in group] for group in finding.supporting_tolerated]
    assert [("", "-")] in places


def test_a_stored_list_with_junk_in_it_keeps_only_the_valid_differences():
    claim_json = {
        "claim_id": "A-01",
        "claim_type": "reported",
        "text": "The accountant paid the vendor.",
        "epistemic_status": "reported",
        "supporting_source_ids": ["S1"],
        "supporting_citations": [
            {
                "source_id": "S1",
                "exact_quote": "paid -5,000 baht",
                "tolerated_differences": ["junk", {"written": "", "source": "-"}, 3],
            },
            {"source_id": "S1", "exact_quote": "on Monday", "tolerated_differences": "oops"},
        ],
    }

    [first, second] = CaseAnalysisClaim.model_validate(claim_json).supporting_citations

    assert [(d.written, d.source) for d in first.tolerated_differences] == [("", "-")]
    assert second.tolerated_differences == []


@pytest.mark.parametrize(
    "order",
    [("paid -5,000 baht", "paid 5,000 baht"), ("paid 5,000 baht", "paid -5,000 baht")],
)
def test_the_differences_do_not_depend_on_which_written_quote_came_first(order):
    bundle, trace = bundle_and_trace(*order)

    bound = resolve_case_trace(trace, bundle)

    assert shown(bound) == {"paid -5,000 baht": [("", "-")]}


@pytest.mark.parametrize(
    "order",
    [
        ("apple pays 5,000 baht", "APPLE pays 5,000 baht"),
        ("APPLE pays 5,000 baht", "apple pays 5,000 baht"),
    ],
)
def test_two_tolerated_variants_of_one_passage_keep_every_difference(order):
    source_id = str(uuid4())
    text = "Apple pays 5,000 baht each month."
    bundle = CaseSourceBundle(
        revision=1,
        sources=(CaseSourceItem(source_id=source_id, source_kind="narrative", text=text),),
    )
    trace = CaseAnalysisTrace(
        analysis_mode="case_overview",
        summary="Apple pays.",
        claims=[claim(*order, source_id=source_id)],
    )

    bound = resolve_case_trace(trace, bundle)

    [(quote, found)] = shown(bound).items()
    assert quote == "Apple pays 5,000 baht"
    assert sorted(found) == [("APPLE", "Apple"), ("apple", "Apple")]
