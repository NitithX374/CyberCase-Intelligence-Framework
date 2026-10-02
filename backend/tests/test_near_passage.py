from __future__ import annotations

from uuid import uuid4

import pytest

from app.analysis.write import reading_payload
from app.chat.compose import analysis_payload
from app.sources.bundle import CaseSourceBundle, CaseSourceItem
from app.trace.bind import resolve_case_trace
from app.trace.claims import CaseAnalysisClaim, CaseSourceCitation
from app.trace.quotes import nearest_passage
from app.trace.trace import CaseAnalysisTrace, CaseProviderReading, CaseProviderReadingReply

THAI_NAME = "ผู้เสียหายชื่อนายสมพงศ์ ใจดี เข้าแจ้งความที่สถานีตำรวจในวันจันทร์"


@pytest.mark.parametrize(
    ("source", "quote", "passage", "places"),
    [
        (
            "The victim called the bank. The transfer happened on 17 March 2026 at noon. "
            "Police were told later.",
            "The transfer happened on 11 March 2026 at noon",
            "The transfer happened on 17 March 2026 at noon",
            (("11", "17"),),
        ),
        (
            "Two people were arrested at the house on Monday and released later.",
            "Two people were arrested at the house on Monday and quickly released later",
            "Two people were arrested at the house on Monday and released later",
            (("quickly", ""),),
        ),
        (
            "Investigators said the attackers encrypted the shared drive on Monday night.",
            "Investigators said the attackers encrypted the drive on Monday night",
            "Investigators said the attackers encrypted the shared drive on Monday night",
            (("", "shared"),),
        ),
        (
            THAI_NAME,
            "ผู้เสียหายชื่อนายสมพงค์ ใจดี เข้าแจ้งความที่สถานีตำรวจ",
            "ผู้เสียหายชื่อนายสมพงศ์ ใจดี เข้าแจ้งความที่สถานีตำรวจ",
            (("สมพงค์", "สมพงศ์"),),
        ),
        (
            "ผู้ต้องหาโอนเงินจากบัญชีของผู้เสียหายไปยังบัญชีม้าในวันศุกร์",
            "ผู้ต้องหาโอนเงินจากบัญชีผู้เสียหายไปยังบัญชีม้าในวันศุกร์",
            "ผู้ต้องหาโอนเงินจากบัญชีของผู้เสียหายไปยังบัญชีม้าในวันศุกร์",
            (("", "ของ"),),
        ),
        (
            "The suspect withdrew the money from an ATM in Philadelphia on Friday evening.",
            "The suspect withdrew the money from an ATM on Friday evening",
            "The suspect withdrew the money from an ATM in Philadelphia on Friday evening",
            (("", "in Philadelphia"),),
        ),
        (
            "The attackers sent a fake invoice to the finance team on Monday morning.",
            "The attackers sent a invoice to the finance team on Monday morning",
            "The attackers sent a fake invoice to the finance team on Monday morning",
            (("", "fake"),),
        ),
        (
            "Filenames had been changed and a text file demanded contact by email.",
            "Filenames were changed and a text file demanded contact",
            "Filenames had been changed and a text file demanded contact",
            (("were", "had been"),),
        ),
        (
            "Police said attackers used a stolen password to log in on Monday.",
            "Hackers used a stolen password to log in on Monday",
            "attackers used a stolen password to log in on Monday",
            (("Hackers", "attackers"),),
        ),
    ],
    ids=[
        "changed-digit",
        "added-word",
        "dropped-word",
        "thai-name",
        "thai-dropped-word",
        "dropped-words-near-the-end",
        "dropped-word-beside-a-short-word",
        "one-word-for-two",
        "edge-words-are-context",
    ],
)
def test_a_near_quote_points_at_its_passage_and_names_each_place(source, quote, passage, places):
    near = nearest_passage(source, quote)

    assert near is not None
    assert near.source_text == passage
    assert near.differences == places


@pytest.mark.parametrize(
    ("source", "quote"),
    [
        (
            "The money was sent to account A on Monday. The money was sent to account B on Friday.",
            "The money was sent to account C on",
        ),
        (
            "The money was sent to account A on Monday and nothing else happened.",
            "The money was sent ... on Tuesday",
        ),
        (
            "The attackers copied the payroll files to a server in Ohio on Monday and deleted the "
            "logs before noon on the same day.",
            "The attackers copied the salary files to a server in Texas on Tuesday and deleted the "
            "logs before midnight on the same day",
        ),
        (
            "The attackers used a stolen password to log in to the payroll system on Monday morning.",
            "Hackers used a borrowed key to enter the salary platform on Friday evening",
        ),
        (
            "The finance share was encrypted overnight and a note demanded contact.",
            "There was no incident.",
        ),
    ],
    ids=[
        "two-passages-as-close",
        "middle-ellipsis",
        "more-than-three-places",
        "more-edits-than-a-third",
        "short-invented-quote",
    ],
)
def test_no_passage_is_pointed_at_when_the_rule_does_not_hold(source, quote):
    assert nearest_passage(source, quote) is None


def bound(*citations: CaseSourceCitation, text: str = THAI_NAME) -> CaseAnalysisTrace:
    source_id = citations[0].source_id
    bundle = CaseSourceBundle(
        revision=1,
        sources=(CaseSourceItem(source_id=source_id, source_kind="narrative", text=text),),
    )
    claim = CaseAnalysisClaim(
        claim_id="A-01",
        claim_type="reported",
        text="ผู้เสียหายแจ้งความ",
        epistemic_status="reported",
        supporting_source_ids=[source_id],
        supporting_citations=list(citations),
    )
    trace = CaseAnalysisTrace(analysis_mode="case_overview", summary="แจ้งความ", claims=[claim])
    return resolve_case_trace(trace, bundle)


def test_the_binder_keeps_an_unverified_quote_with_its_passage_out_of_the_citations():
    source_id = str(uuid4())
    written = "ผู้เสียหายชื่อนายสมพงค์ ใจดี เข้าแจ้งความที่สถานีตำรวจ"

    trace = bound(CaseSourceCitation(source_id=source_id, exact_quote=written))

    [claim] = trace.claims
    [unverified] = claim.unverified_citations
    assert claim.supporting_citations == []
    assert claim.epistemic_status == "not_confirmed"
    assert (unverified.role, unverified.written_quote) == ("supporting", written)
    assert [(d.written, d.source) for d in unverified.near_passage.differences] == [
        ("สมพงค์", "สมพงศ์")
    ]
    assert trace.grounding.citations_pointed == 1
    assert trace.grounding.citations_unfound == 0


def test_a_quote_with_no_near_passage_is_kept_without_one_and_counted_unfound():
    source_id = str(uuid4())

    trace = bound(CaseSourceCitation(source_id=source_id, exact_quote="ข้อความที่ไม่มีอยู่ในต้นฉบับเลย"))

    [unverified] = trace.claims[0].unverified_citations
    assert unverified.near_passage is None
    assert trace.grounding.citations_pointed == 0
    assert trace.grounding.citations_unfound == 1


def test_a_located_quote_is_not_kept_as_unverified():
    source_id = str(uuid4())

    trace = bound(CaseSourceCitation(source_id=source_id, exact_quote="เข้าแจ้งความที่สถานีตำรวจ"))

    assert trace.claims[0].unverified_citations == []
    assert trace.claims[0].epistemic_status == "reported"


def test_binding_a_bound_trace_again_keeps_its_unverified_quotes():
    source_id = str(uuid4())
    written = "ผู้เสียหายชื่อนายสมพงค์ ใจดี เข้าแจ้งความที่สถานีตำรวจ"
    once = bound(CaseSourceCitation(source_id=source_id, exact_quote=written))
    bundle = CaseSourceBundle(
        revision=1,
        sources=(CaseSourceItem(source_id=source_id, source_kind="narrative", text=THAI_NAME),),
    )

    twice = resolve_case_trace(once, bundle)

    assert twice.claims[0].unverified_citations == once.claims[0].unverified_citations


def test_an_analysis_stored_before_the_pointer_still_loads():
    stored = {
        "analysis_mode": "case_overview",
        "summary": "Files were altered.",
        "claims": [
            {
                "claim_id": "A-01",
                "claim_type": "reported",
                "text": "Files were altered.",
                "epistemic_status": "not_confirmed",
                "supporting_citations": [],
            }
        ],
        "grounding": {"claims": 1, "citations_claimed": 1, "citations_paraphrased": 1},
    }

    trace = CaseAnalysisTrace.model_validate(stored)

    assert trace.claims[0].unverified_citations == []
    assert trace.grounding.citations_pointed == 0


def test_neither_model_is_shown_an_unverified_quote():
    source_id = str(uuid4())
    trace = bound(
        CaseSourceCitation(
            source_id=source_id, exact_quote="ผู้เสียหายชื่อนายสมพงค์ ใจดี เข้าแจ้งความที่สถานีตำรวจ"
        )
    )
    reading = CaseProviderReading(
        version="case_analysis_trace_v1",
        claims=trace.claims,
        involved_parties=[],
        timeline=[],
        impacts=[],
    )

    assert trace.claims[0].unverified_citations
    assert all("unverified_citations" not in c for c in reading_payload(reading)["claims"])
    assert all("unverified_citations" not in c for c in analysis_payload(trace, None)["claims"])


def test_the_reply_the_model_fills_has_no_place_for_unverified_quotes():
    assert "unverified_citations" not in str(CaseProviderReadingReply.model_json_schema())
