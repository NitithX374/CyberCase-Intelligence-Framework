from __future__ import annotations

from uuid import uuid4

import pytest

from app.sources.bundle import CaseSourceBundle, CaseSourceItem
from app.trace.bind import resolve_case_trace
from app.trace.claims import CaseAnalysisClaim, CaseSourceCitation
from app.trace.quotes import find_aligned_quote, find_format_only_quote
from app.trace.trace import CaseAnalysisTrace


def located(source: str, quote: str) -> list[str] | None:
    spans = find_aligned_quote(source, quote)
    return None if spans is None else [source[start:end] for start, end in spans]


@pytest.mark.parametrize(
    ("source", "quote", "stored"),
    [
        (
            "The attackers sent a phishing email to staff on Monday.",
            '"The attackers sent a phishing email"',
            "The attackers sent a phishing email",
        ),
        (
            "Police said the server was encrypted on Monday and the backups were gone.",
            "the server was encrypted on Monday.",
            "the server was encrypted on Monday",
        ),
        (
            "Investigators found the backups were gone, and the logs had been wiped.",
            "the backups were gone and the logs had been wiped,",
            "the backups were gone, and the logs had been wiped",
        ),
        (
            "The report says the files were renamed with a new suffix.",
            "The files were renamed with a new suffix",
            "the files were renamed with a new suffix",
        ),
        (
            "The intrusion lasted from 10−15 March according to the logs.",
            "lasted from 10—15 March",
            "lasted from 10−15 March",
        ),
        (
            "ผู้เสียหายโอนเงินไปยังบัญชีของคนร้าย, จากนั้นติดต่อไม่ได้อีก",
            "ผู้เสียหายโอนเงินไปยังบัญชีของคนร้าย จากนั้นติดต่อไม่ได้อีก",
            "ผู้เสียหายโอนเงินไปยังบัญชีของคนร้าย, จากนั้นติดต่อไม่ได้อีก",
        ),
    ],
    ids=["quote-marks", "trailing-period", "comma-moved", "capital", "dash-style", "thai-comma"],
)
def test_a_quote_that_differs_only_in_format_is_stored_as_source_text(source, quote, stored):
    assert located(source, quote) == [stored]


@pytest.mark.parametrize(
    ("source", "quote"),
    [
        (
            "The transfer happened on 17 March 2026 at noon.",
            "The transfer happened on 11 March 2026",
        ),
        ("A ransom of 15 million baht was demanded.", "A ransom of 1.5 million baht was demanded"),
        ("เขาบอกว่าไม้หายไปจากบ้านตั้งแต่เช้า", "เขาบอกว่าไม่หายไปจากบ้านตั้งแต่เช้า"),
        ("The attackers used a stolen password to log in.", "The attackers used a stolen passward"),
        ("Then the money was sent. Later the money was sent!", '"the money was sent."'),
        ("The money was sent to an account abroad.", '"was sent"'),
    ],
    ids=["digit", "decimal-point", "thai-tone-mark", "one-letter", "form-twice", "too-short"],
)
def test_a_quote_that_changes_text_is_not_located(source, quote):
    assert located(source, quote) is None
    assert find_format_only_quote(source, quote) is None


def test_the_earlier_tiers_still_decide_first():
    source = "Files on the **shared** drive were reported encrypted."

    assert located(source, "Files on the shared drive") == ["Files on the **shared** drive"]


def test_the_binder_counts_a_format_only_quote_as_verified():
    source_id = str(uuid4())
    source = "Police said the server was encrypted on Monday and the backups were gone."
    bundle = CaseSourceBundle(
        revision=1,
        sources=(CaseSourceItem(source_id=source_id, source_kind="narrative", text=source),),
    )
    trace = CaseAnalysisTrace(
        analysis_mode="case_overview",
        summary="The server was encrypted.",
        claims=[
            CaseAnalysisClaim(
                claim_id="A-01",
                claim_type="reported",
                text="The server was encrypted on Monday.",
                epistemic_status="reported",
                supporting_source_ids=[source_id],
                supporting_citations=[
                    CaseSourceCitation(
                        source_id=source_id, exact_quote='"The server was encrypted on Monday."'
                    )
                ],
            )
        ],
    )

    resolved = resolve_case_trace(trace, bundle)

    [claim] = resolved.claims
    assert claim.epistemic_status == "reported"
    assert [c.exact_quote for c in claim.supporting_citations] == [
        "the server was encrypted on Monday"
    ]
    assert resolved.grounding.citations_verified == 1
    assert resolved.grounding.citations_unfound == 0
