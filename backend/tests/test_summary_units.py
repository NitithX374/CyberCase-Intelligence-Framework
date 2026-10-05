from __future__ import annotations

import json
from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.analysis.schemas import CaseAnalysisResultRead
from app.sources.bundle import CaseSourceBundle, CaseSourceItem
from app.trace.bind import resolve_case_trace
from app.trace.claims import CaseAnalysisClaim, CaseSourceCitation
from app.trace.summary import summary_closings, summary_pieces
from app.trace.trace import CaseAnalysisTrace, CaseSummaryUnit

SOURCE_TEXT = "The finance share was encrypted overnight. The attacker demanded two bitcoin."


@pytest.mark.parametrize(
    ("summary", "pieces"),
    [
        ("A share was encrypted [A-01].", [("A share was encrypted", ["A-01"])]),
        ("Two hosts were hit [A-03, A-07].", [("Two hosts were hit", ["A-03", "A-07"])]),
        ("Two hosts were hit [ A-03 ,A-07 ]", [("Two hosts were hit", ["A-03", "A-07"])]),
        (
            "First came the alarm [A-01]. Then the logs were wiped [A-02].",
            [("First came the alarm", ["A-01"]), ("Then the logs were wiped", ["A-02"])],
        ),
        (
            "First came the alarm. [A-01] Then the logs were wiped. [A-02]",
            [("First came the alarm.", ["A-01"]), ("Then the logs were wiped.", ["A-02"])],
        ),
        (
            "The firm [A-01] lost its data [A-02].",
            [("The firm", ["A-01"]), ("lost its data", ["A-02"])],
        ),
        (
            "A share was encrypted [A-01]. It then spread to the backups.",
            [("A share was encrypted", ["A-01"]), ("It then spread to the backups.", [])],
        ),
        (
            "ไฟล์ถูกเข้ารหัสในช่วงกลางคืน [A-01] ทีมพบกุญแจ [A-02, A-03]",
            [("ไฟล์ถูกเข้ารหัสในช่วงกลางคืน", ["A-01"]), ("ทีมพบกุญแจ", ["A-02", "A-03"])],
        ),
        (
            "ไฟล์ถูกเข้ารหัส [A-01]。ทีมพบกุญแจ [A-02]",
            [("ไฟล์ถูกเข้ารหัส", ["A-01"]), ("ทีมพบกุญแจ", ["A-02"])],
        ),
        ("One [A-01]\n\nTwo [A-02]", [("One", ["A-01"]), ("Two", ["A-02"])]),
        ("A share was encrypted.", [("A share was encrypted.", [])]),
        ("A share was encrypted [A-003].", [("A share was encrypted", ["A-03"])]),
        ("A share was encrypted [A-01, A-01].", [("A share was encrypted", ["A-01"])]),
        ("[A-01] A share was encrypted [A-02].", [("A share was encrypted", ["A-02"])]),
        ("A share was encrypted [A-01] [A-02].", [("A share was encrypted", ["A-01", "A-02"])]),
        ("A share was encrypted [A-01].\n", [("A share was encrypted", ["A-01"])]),
    ],
)
def test_a_summary_is_cut_into_the_units_that_end_at_a_bracket(summary, pieces):
    assert summary_pieces(summary) == pieces


@pytest.mark.parametrize(
    "summary",
    [
        "A share was encrypted [A-1].",
        "A share was encrypted [A-01.",
        "A share was encrypted A-01].",
        "A share was encrypted [a-01].",
        "A share was encrypted [B-01].",
        "A share was encrypted [A-01;A-02].",
        "A share was encrypted [A-01, ].",
        "A share was encrypted [A-01 A-02].",
        "A share was encrypted [claim A-01].",
        "A share was encrypted (A-01).",
    ],
)
def test_a_bracket_that_is_not_well_formed_stays_in_the_text(summary):
    assert summary_pieces(summary) == [(summary, [])]


def test_a_summary_with_no_text_is_no_unit():
    assert summary_pieces("") == []
    assert summary_pieces("  \n ") == []
    assert summary_pieces("[A-01].") == []


def claim(claim_id: str, source_id: str, quote: str) -> CaseAnalysisClaim:
    return CaseAnalysisClaim(
        claim_id=claim_id,
        claim_type="reported",
        text=f"Claim {claim_id}.",
        epistemic_status="reported",
        supporting_source_ids=[source_id],
        supporting_citations=[CaseSourceCitation(source_id=source_id, exact_quote=quote)],
    )


def bound_trace(summary: str) -> CaseAnalysisTrace:
    source_id = str(uuid4())
    bundle = CaseSourceBundle(
        revision=1,
        sources=(CaseSourceItem(source_id=source_id, source_kind="narrative", text=SOURCE_TEXT),),
    )
    trace = CaseAnalysisTrace(
        analysis_mode="case_overview",
        summary=summary,
        claims=[
            claim("A-01", source_id, "The finance share was encrypted overnight."),
            claim("A-02", source_id, "The attacker demanded two bitcoin."),
            claim("A-03", source_id, "The attacker demanded ten bitcoin."),
            claim("A-04", source_id, "The backups were wiped."),
        ],
    )
    return resolve_case_trace(trace, bundle)


SUMMARY = (
    "A share was encrypted [A-01]. "
    "Two bitcoin were demanded [A-01, A-02]. "
    "Ten bitcoin were demanded [A-03]. "
    "Some of it was wiped [A-03, A-04]. "
    "Someone is to blame [A-77]. "
    "Nothing else is known."
)


def test_each_unit_is_supported_by_the_claims_it_cites():
    bound = bound_trace(SUMMARY)

    assert [claim_item.epistemic_status for claim_item in bound.claims] == [
        "reported",
        "reported",
        "not_confirmed",
        "not_confirmed",
    ]
    assert [(unit.text, unit.claim_ids, unit.support) for unit in bound.summary_units] == [
        ("A share was encrypted", ["A-01"], "bound"),
        ("Two bitcoin were demanded", ["A-01", "A-02"], "bound"),
        ("Ten bitcoin were demanded", ["A-03"], "unbound"),
        ("Some of it was wiped", ["A-03", "A-04"], "unbound"),
        ("Someone is to blame", [], "no_claim"),
        ("Nothing else is known.", [], "no_claim"),
    ]


def test_a_unit_resting_on_some_checked_claims_and_some_not_is_mixed():
    bound = bound_trace("Both demands [A-02, A-03].")

    [unit] = bound.summary_units
    assert (unit.claim_ids, unit.support) == (["A-02", "A-03"], "mixed")


def test_an_id_that_names_no_claim_is_removed_from_its_unit_and_counted():
    bound = bound_trace(SUMMARY)

    assert bound.summary_units[4].claim_ids == []
    assert bound.grounding.summary_ids_unknown == 1
    assert bound_trace("One [A-01, A-77, A-78]. Two [A-99].").grounding.summary_ids_unknown == 3


def test_the_analysis_does_not_fail_when_every_id_is_unknown():
    bound = bound_trace("Everything is invented [A-77, A-78].")

    [unit] = bound.summary_units
    assert (unit.claim_ids, unit.support) == ([], "no_claim")
    assert bound.grounding.summary_ids_unknown == 2


def test_the_stored_summary_keeps_its_brackets_exactly_as_written():
    bound = bound_trace(SUMMARY)

    assert bound.summary == SUMMARY


def test_a_summary_without_ids_is_one_unit_that_rests_on_no_claim():
    bound = bound_trace("A share was encrypted and a ransom was asked.")

    [unit] = bound.summary_units
    assert unit.text == "A share was encrypted and a ransom was asked."
    assert (unit.claim_ids, unit.support) == ([], "no_claim")
    assert bound.grounding.summary_ids_unknown == 0


def test_binding_a_bound_trace_again_gives_the_same_units_and_count():
    source_id = str(uuid4())
    bundle = CaseSourceBundle(
        revision=1,
        sources=(CaseSourceItem(source_id=source_id, source_kind="narrative", text=SOURCE_TEXT),),
    )
    first = bound_trace(SUMMARY)

    again = resolve_case_trace(first, bundle)

    assert again.summary_units != []
    assert again.grounding.summary_ids_unknown == 1


def test_a_trace_stored_before_the_units_existed_validates_with_none():
    stored = json.loads(bound_trace(SUMMARY).model_dump_json())
    del stored["summary_units"]
    del stored["grounding"]["summary_ids_unknown"]

    reloaded = CaseAnalysisTrace.model_validate(stored)

    assert reloaded.summary_units == []
    assert reloaded.grounding.summary_ids_unknown == 0
    assert reloaded.summary == SUMMARY


def test_the_units_survive_the_stored_trace_being_read_back():
    bound = bound_trace(SUMMARY)

    reloaded = CaseAnalysisTrace.model_validate(json.loads(bound.model_dump_json()))

    assert reloaded == bound
    assert [unit.support for unit in reloaded.summary_units] == [
        "bound",
        "bound",
        "unbound",
        "unbound",
        "no_claim",
        "no_claim",
    ]


def test_the_api_read_model_carries_the_units():
    bound = bound_trace(SUMMARY)

    read = CaseAnalysisResultRead.model_validate(
        {
            "id": uuid4(),
            "case_id": uuid4(),
            "source_revision": 1,
            "status": "validated",
            "summary": SUMMARY,
            "trace_json": json.loads(bound.model_dump_json()),
            "pipeline_config": {},
            "created_at": datetime(2026, 10, 4, tzinfo=UTC),
        }
    )

    assert read.trace_json.summary_units == bound.summary_units
    assert read.trace_json.grounding.summary_ids_unknown == 1


def test_a_unit_is_never_written_by_a_model():
    from app.llm.schema import structured_output_schema
    from app.trace.trace import CaseProviderAnalysis, CaseProviderJudgement

    for schema in (
        CaseProviderJudgement.model_json_schema(),
        structured_output_schema(CaseProviderAnalysis),
    ):
        assert "summary_units" not in json.dumps(schema)
        assert "summary_ids_unknown" not in json.dumps(schema)
    assert CaseSummaryUnit.model_fields.keys() == {"text", "claim_ids", "support"}


CLOSINGS = [
    ("A share was encrypted [A-01].", ["."]),
    ("First [A-01]. Second [A-02].", [".", "."]),
    ("It was found on October 1 [A-03], but the time is unknown [A-04].", [",", "."]),
    ("ไฟล์ถูกเข้ารหัส [A-01] ทีมพบกุญแจ [A-02]", ["", ""]),
    ("A [A-01] [A-02].", ["."]),
    ("A [A-01]. It then spread.", [".", ""]),
    ("No brackets at all.", [""]),
    ("One [A-01]。Two [A-02]", ["。", ""]),
    ("One [A-01]; two [A-02]!", [";", "!"]),
    ("One [A-01] ... two [A-02]", ["...", ""]),
    ("[A-01] Text [A-02].", ["."]),
    ("One [A-01]\n\nTwo [A-02]", ["", ""]),
    ("One [A-01] , two [A-02] .", [",", "."]),
]


@pytest.mark.parametrize(("summary", "closings"), CLOSINGS)
def test_the_punctuation_after_a_bracket_is_the_closing_of_its_unit(summary, closings):
    assert summary_closings(summary) == closings


@pytest.mark.parametrize("summary", [summary for summary, _ in CLOSINGS])
def test_there_is_one_closing_for_each_unit(summary):
    assert len(summary_closings(summary)) == len(summary_pieces(summary))
