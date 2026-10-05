from __future__ import annotations

import json
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from fake_nli import NEUTRAL, FakeNli, entailing

from app.analysis.schemas import CaseAnalysisResultRead
from app.analysis.write import reading_payload
from app.chat.compose import analysis_payload
from app.config import settings
from app.sources.bundle import CaseSourceBundle, CaseSourceItem
from app.trace import nli_model
from app.trace.bind import bound_claims, bound_references, resolve_case_trace
from app.trace.claims import CaseAnalysisClaim, CaseSourceCitation, CaseUnverifiedCitation
from app.trace.meaning import MAX_CITATIONS, MIN_ENTAILMENT
from app.trace.nli_model import Judgement, NliUnavailable
from app.trace.trace import (
    CaseAnalysisTrace,
    CaseInvolvedParty,
    CaseProviderReading,
)

SOURCE = (
    "The outage began on Monday. "
    "The attackers encrypted the file server on Monday night. "
    "Staff were sent home early. "
    "A ransom note appeared on every desktop."
)
CLAIM = "The file server was encrypted on Monday night."
ENCRYPTED = "The attackers encrypted the file server on Monday night."
UNRELATED = "Quantum widgets shimmer under violet moonlight beyond the horizon."


def bundle_of(*texts: str) -> CaseSourceBundle:
    return CaseSourceBundle(
        revision=1,
        sources=tuple(
            CaseSourceItem(source_id=f"S{number}", source_kind="narrative", text=text)
            for number, text in enumerate(texts, 1)
        ),
    )


def claim_of(
    quote: str,
    *,
    claim_id: str = "A-01",
    text: str = CLAIM,
    source_id: str = "S1",
    status: str = "reported",
    role: str = "supporting",
) -> CaseAnalysisClaim:
    citation = CaseSourceCitation(source_id=source_id, exact_quote=quote)
    return CaseAnalysisClaim(
        claim_id=claim_id,
        claim_type="reported",
        text=text,
        epistemic_status=status,
        supporting_source_ids=[source_id],
        supporting_citations=[citation] if role == "supporting" else [],
        contradicting_source_ids=[source_id] if role == "contradicting" else [],
        contradicting_citations=[citation] if role == "contradicting" else [],
    )


def reading_of(*claims: CaseAnalysisClaim) -> CaseProviderReading:
    return CaseProviderReading(
        version="case_analysis_trace_v1",
        claims=list(claims),
        involved_parties=[],
        timeline=[],
        impacts=[],
    )


@pytest.fixture
def model(monkeypatch):
    def install(fake: FakeNli) -> FakeNli:
        monkeypatch.setattr(nli_model, "load_nli", lambda: fake)
        return fake

    return install


def pointed(model, fake, *claims, bundle=None):
    model(fake)
    return bound_claims(reading_of(*claims), bundle or bundle_of(SOURCE))


def only_unverified(bound) -> CaseUnverifiedCitation:
    [claim] = bound.claims
    [item] = claim.unverified_citations
    return item


def test_a_quote_the_string_pointer_found_is_not_given_a_meaning_passage(model):
    fake = entailing("encrypted")
    near = "The attackers encrypted the file servers on Monday night"

    bound, grounding = pointed(model, fake, claim_of(near))

    item = only_unverified(bound)
    assert item.near_passage is not None
    assert item.meaning_passage is None
    assert fake.judged == []
    assert grounding.meaning_pointer_eligible == 0
    assert grounding.citations_meaning_pointed == 0


def test_when_the_string_pointer_refuses_the_sentence_that_is_entailed_is_pointed_at(model):
    fake = entailing("encrypted the file server")

    bound, grounding = pointed(model, fake, claim_of(UNRELATED))

    item = only_unverified(bound)
    assert item.near_passage is None
    passage = item.meaning_passage
    assert passage is not None
    assert passage.source_text == ENCRYPTED
    assert SOURCE[passage.start : passage.end] == ENCRYPTED
    assert passage.entailment == pytest.approx(0.9)
    assert passage.model == "fake-nli"
    assert grounding.meaning_pointer_eligible == 1
    assert grounding.meaning_pointer_attempted == 1
    assert grounding.citations_meaning_pointed == 1
    assert (grounding.meaning_pointer_unavailable, grounding.meaning_pointer_skipped) == (0, 0)
    assert grounding.meaning_pointer_unavailable_reason is None


def test_the_candidates_are_the_three_sentences_that_share_most_words_with_the_claim(model):
    fake = FakeNli()

    pointed(model, fake, claim_of(UNRELATED))

    assert [premise for premise, _ in fake.judged] == [
        ENCRYPTED,
        "The outage began on Monday.",
        "A ransom note appeared on every desktop.",
    ]
    assert {hypothesis for _, hypothesis in fake.judged} == {CLAIM}


def test_a_thai_claim_ranks_the_sentences_by_thai_words(model):
    source = "\n".join(
        [
            "ตำรวจตั้งด่านตรวจรถยนต์บริเวณทางแยกในช่วงเช้า",
            "ผู้เสียหายโอนเงินจำนวนแปดหมื่นห้าพันบาทไปยังบัญชีของคนร้าย",
            "ผู้ว่าราชการจังหวัดเปิดงานกีฬาประจำปี",
            "ธนาคารปลายทางอายัดบัญชีทันทีที่ได้รับแจ้ง",
        ]
    )
    fake = FakeNli()

    pointed(
        model,
        fake,
        claim_of(UNRELATED, text="ผู้เสียหายโอนเงินไปยังบัญชีของคนร้าย"),
        bundle=bundle_of(source),
    )

    assert fake.judged[0][0] == "ผู้เสียหายโอนเงินจำนวนแปดหมื่นห้าพันบาทไปยังบัญชีของคนร้าย"
    assert len(fake.judged) == 3


def test_the_claim_stays_not_confirmed_and_the_passage_is_never_a_located_quote(model):
    bound, grounding = pointed(model, entailing("encrypted"), claim_of(UNRELATED))

    [claim] = bound.claims
    assert claim.epistemic_status == "not_confirmed"
    assert claim.supporting_citations == []
    assert claim.supporting_source_ids == ["S1"]
    assert claim.contradicting_citations == []
    assert (grounding.citations_verified, grounding.citations_unfound) == (0, 1)
    assert grounding.claims_without_citation == 1
    assert grounding.sources_cited == 0


def test_only_contradiction_or_neutral_gives_no_meaning_passage(model):
    contradicting = FakeNli(judge=lambda premise, hypothesis: Judgement("contradiction", 0.01))

    bound, grounding = pointed(model, contradicting, claim_of(UNRELATED))

    assert only_unverified(bound).meaning_passage is None
    assert (grounding.meaning_pointer_attempted, grounding.citations_meaning_pointed) == (1, 0)
    assert len(contradicting.judged) == 3


def test_an_entailment_below_one_half_is_not_a_passage(model):
    low = FakeNli(judge=lambda premise, hypothesis: Judgement("entailment", 0.49))
    edge = FakeNli(judge=lambda premise, hypothesis: Judgement("entailment", 0.5))

    bound_low, _ = pointed(model, low, claim_of(UNRELATED))
    bound_edge, _ = pointed(model, edge, claim_of(UNRELATED))

    assert MIN_ENTAILMENT == 0.5
    assert only_unverified(bound_low).meaning_passage is None
    assert only_unverified(bound_edge).meaning_passage is not None


def test_the_label_decides_not_the_score_alone(model):
    odd = FakeNli(judge=lambda premise, hypothesis: Judgement("neutral", 0.9))

    bound, grounding = pointed(model, odd, claim_of(UNRELATED))

    assert only_unverified(bound).meaning_passage is None
    assert grounding.citations_meaning_pointed == 0


def test_the_highest_entailment_wins_and_a_tie_goes_to_the_earlier_sentence(model):
    by_sentence = {
        "The outage began on Monday.": 0.8,
        ENCRYPTED: 0.8,
        "A ransom note appeared on every desktop.": 0.6,
    }
    tied = FakeNli(judge=lambda premise, hypothesis: Judgement("entailment", by_sentence[premise]))

    bound, _ = pointed(model, tied, claim_of(UNRELATED))

    assert only_unverified(bound).meaning_passage.source_text == "The outage began on Monday."

    by_sentence[ENCRYPTED] = 0.95
    higher, _ = pointed(model, tied, claim_of(UNRELATED))

    assert only_unverified(higher).meaning_passage.source_text == ENCRYPTED


def test_a_pair_that_does_not_fit_the_model_is_skipped_never_cut(model):
    fake = FakeNli(
        judge=lambda premise, hypothesis: Judgement("entailment", 0.9),
        fits=lambda premise, hypothesis: "encrypted" not in premise,
    )

    bound, grounding = pointed(model, fake, claim_of(UNRELATED))

    assert all("encrypted" not in premise for premise, _ in fake.judged)
    assert only_unverified(bound).meaning_passage.source_text != ENCRYPTED
    assert grounding.meaning_pointer_attempted == 1

    nothing = FakeNli(fits=lambda premise, hypothesis: False)
    bound, grounding = pointed(model, nothing, claim_of(UNRELATED))

    assert nothing.judged == []
    assert only_unverified(bound).meaning_passage is None
    assert (grounding.meaning_pointer_eligible, grounding.meaning_pointer_attempted) == (1, 0)
    assert grounding.meaning_pointer_skipped == 1


def test_a_missing_model_does_not_stop_the_analysis_and_is_recorded_with_its_reason(
    model, monkeypatch, caplog
):
    def missing():
        raise NliUnavailable("weights_missing")

    monkeypatch.setattr(nli_model, "load_nli", missing)

    bound, grounding = bound_claims(reading_of(claim_of(UNRELATED)), bundle_of(SOURCE))

    [claim] = bound.claims
    assert claim.epistemic_status == "not_confirmed"
    assert only_unverified(bound).meaning_passage is None
    assert grounding.meaning_pointer_eligible == 1
    assert grounding.meaning_pointer_unavailable == 1
    assert grounding.meaning_pointer_unavailable_reason == "weights_missing"
    assert (grounding.meaning_pointer_attempted, grounding.citations_meaning_pointed) == (0, 0)
    assert grounding.citations_unfound == 1


def test_a_model_that_fails_while_judging_is_unavailable_too(model):
    def broken(premise: str, hypothesis: str) -> Judgement:
        raise RuntimeError("out of memory")

    bound, grounding = pointed(model, FakeNli(judge=broken), claim_of(UNRELATED))

    assert only_unverified(bound).meaning_passage is None
    assert grounding.meaning_pointer_unavailable == 1
    assert grounding.meaning_pointer_unavailable_reason == "failed:RuntimeError"
    assert (grounding.meaning_pointer_attempted, grounding.citations_meaning_pointed) == (0, 0)


def test_the_model_is_not_loaded_when_no_citation_needs_it(monkeypatch):
    def forbidden():
        raise AssertionError("the model was loaded")

    monkeypatch.setattr(nli_model, "load_nli", forbidden)

    _, grounding = bound_claims(
        reading_of(claim_of("The attackers encrypted the file server on Monday night.")),
        bundle_of(SOURCE),
    )

    assert grounding.meaning_pointer_eligible == 0
    assert grounding.meaning_pointer_unavailable == 0


def test_the_budget_is_thirty_citations_and_the_rest_are_counted_as_skipped(model):
    fake = entailing("encrypted")
    claims = [claim_of(UNRELATED, claim_id=f"A-{number:02d}") for number in range(1, 34)]

    bound, grounding = pointed(model, fake, *claims)

    assert MAX_CITATIONS == 30
    assert grounding.meaning_pointer_eligible == 33
    assert grounding.meaning_pointer_attempted == 30
    assert grounding.meaning_pointer_skipped == 3
    assert grounding.citations_meaning_pointed == 30
    assert len(fake.judged) == 90
    pointed_claims = [c for c in bound.claims if c.unverified_citations[0].meaning_passage]
    assert [c.claim_id for c in pointed_claims] == [f"A-{number:02d}" for number in range(1, 31)]


def test_the_setting_off_computes_nothing(model, monkeypatch):
    fake = entailing("encrypted")
    model(fake)
    monkeypatch.setattr(settings, "quote_meaning_pointer", "off")

    bound, grounding = bound_claims(reading_of(claim_of(UNRELATED)), bundle_of(SOURCE))

    assert only_unverified(bound).meaning_passage is None
    assert fake.judged == []
    assert grounding.meaning_pointer_eligible == 0


@pytest.mark.parametrize(
    "case",
    [
        pytest.param({"role": "contradicting"}, id="a contradicting quote"),
        pytest.param({"status": "contradicted"}, id="a claim that is not a reported fact"),
        pytest.param({"source_id": "S9"}, id="a source that is not in the case"),
    ],
)
def test_only_an_unlocated_supporting_quote_of_a_not_confirmed_claim_is_eligible(model, case):
    fake = entailing("encrypted")

    bound, grounding = pointed(model, fake, claim_of(UNRELATED, **case))

    assert fake.judged == []
    assert grounding.meaning_pointer_eligible == 0
    assert all(
        item.meaning_passage is None for c in bound.claims for item in c.unverified_citations
    )


def test_a_claim_that_kept_one_verified_quote_is_not_pointed_for_its_other_quote(model):
    fake = entailing("encrypted")
    claim = claim_of(UNRELATED).model_copy(
        update={
            "supporting_citations": [
                CaseSourceCitation(source_id="S1", exact_quote="The outage began on Monday."),
                CaseSourceCitation(source_id="S1", exact_quote=UNRELATED),
            ]
        }
    )

    bound, grounding = pointed(model, fake, claim)

    [kept] = bound.claims
    assert kept.epistemic_status == "reported"
    assert grounding.meaning_pointer_eligible == 0
    assert fake.judged == []


def test_each_source_is_read_for_its_own_claim(model):
    other = (
        "The weather over the harbour stayed dry all week. "
        "The backup tape was copied to a safe in the vault. "
        "Lunch for the whole staff was served late."
    )
    fake = entailing("backup tape")

    bound, grounding = pointed(
        model,
        fake,
        claim_of(UNRELATED, claim_id="A-01", source_id="S2", text="The backup tape was copied."),
        bundle=bundle_of(SOURCE, other),
    )

    passage = only_unverified(bound).meaning_passage
    assert passage.source_text == "The backup tape was copied to a safe in the vault."
    assert other[passage.start : passage.end] == passage.source_text
    assert grounding.citations_meaning_pointed == 1


def test_a_passage_a_stored_claim_carries_is_not_trusted_on_a_second_binding(model):
    model(FakeNli())
    first, _ = bound_claims(reading_of(claim_of(UNRELATED)), bundle_of(SOURCE))
    stale = entailing("encrypted")
    model(stale)
    [claim] = first.claims
    [item] = claim.unverified_citations
    again, grounding = bound_claims(reading_of(claim), bundle_of(SOURCE))

    assert only_unverified(again).meaning_passage is not None
    assert grounding.citations_meaning_pointed == 1
    model(FakeNli())
    cleared, grounding = bound_claims(reading_of(only_unverified_claim(again)), bundle_of(SOURCE))

    assert only_unverified(cleared).meaning_passage is None
    assert grounding.citations_meaning_pointed == 0
    assert item.meaning_passage is None


@pytest.mark.parametrize("why", ["setting_off", "model_unavailable"])
def test_a_stored_passage_is_dropped_when_the_pointer_does_not_run(model, monkeypatch, why):
    model(entailing("encrypted"))
    first, _ = bound_claims(reading_of(claim_of(UNRELATED)), bundle_of(SOURCE))
    stored = only_unverified_claim(first)

    assert stored.unverified_citations[0].meaning_passage is not None
    if why == "setting_off":
        monkeypatch.setattr(settings, "quote_meaning_pointer", "off")
    else:

        def unavailable():
            raise NliUnavailable("weights_missing")

        monkeypatch.setattr(nli_model, "load_nli", unavailable)

    again, _ = bound_claims(reading_of(stored), bundle_of(SOURCE))

    assert only_unverified(again).meaning_passage is None


def only_unverified_claim(bound) -> CaseAnalysisClaim:
    [claim] = bound.claims
    return claim


def trace_with_passage(model) -> tuple[CaseAnalysisTrace, CaseSourceBundle]:
    model(entailing("encrypted the file server"))
    bundle = bundle_of(SOURCE)
    trace = CaseAnalysisTrace(
        analysis_mode="case_overview",
        summary="The file server was encrypted [A-01].",
        involved_parties=[CaseInvolvedParty(name="Staff", role="Affected", claim_ids=["A-01"])],
        claims=[claim_of(UNRELATED)],
    )
    return resolve_case_trace(trace, bundle), bundle


def test_the_passage_counts_for_nothing_in_support_summary_or_counts(model):
    pointed_trace, _ = trace_with_passage(model)
    model(FakeNli())
    plain_trace, _ = trace_with_passage(model)
    model(FakeNli())
    plain_trace = resolve_case_trace(
        CaseAnalysisTrace(
            analysis_mode="case_overview",
            summary="The file server was encrypted [A-01].",
            involved_parties=[CaseInvolvedParty(name="Staff", role="Affected", claim_ids=["A-01"])],
            claims=[claim_of(UNRELATED)],
        ),
        bundle_of(SOURCE),
    )

    assert only_unverified_claim(pointed_trace).unverified_citations[0].meaning_passage
    assert only_unverified_claim(plain_trace).unverified_citations[0].meaning_passage is None
    assert [p.support for p in pointed_trace.involved_parties] == ["unbound"]
    assert [p.support for p in pointed_trace.involved_parties] == [
        p.support for p in plain_trace.involved_parties
    ]
    assert [(u.claim_ids, u.support) for u in pointed_trace.summary_units] == [
        (["A-01"], "unbound")
    ]
    ours, theirs = pointed_trace.grounding, plain_trace.grounding
    for name in (
        "claims",
        "citations_claimed",
        "citations_verified",
        "citations_pointed",
        "citations_unfound",
        "claims_without_citation",
        "citations_duplicated",
        "citations_marked",
        "sources_cited",
    ):
        assert getattr(ours, name) == getattr(theirs, name), name
    assert (ours.citations_meaning_pointed, theirs.citations_meaning_pointed) == (1, 0)


def test_neither_model_is_shown_the_passage(model):
    trace, _ = trace_with_passage(model)
    assert only_unverified_claim(trace).unverified_citations[0].meaning_passage
    reading = reading_of(*trace.claims)

    for payload in (reading_payload(reading), analysis_payload(trace, None)):
        assert "meaning_passage" not in json.dumps(payload)
        assert ENCRYPTED not in json.dumps(payload)


def test_a_citation_stored_before_the_passage_existed_still_validates():
    old = {
        "source_id": "S1",
        "role": "supporting",
        "written_quote": UNRELATED,
        "near_passage": None,
    }

    item = CaseUnverifiedCitation.model_validate(old)

    assert item.meaning_passage is None


def test_the_passage_survives_the_stored_trace_and_the_api_read_model(model):
    trace, _ = trace_with_passage(model)
    stored = json.loads(trace.model_dump_json())

    reloaded = CaseAnalysisTrace.model_validate(stored)
    read = CaseAnalysisResultRead.model_validate(
        {
            "id": uuid4(),
            "case_id": uuid4(),
            "source_revision": 1,
            "status": "validated",
            "summary": trace.summary,
            "trace_json": stored,
            "pipeline_config": {},
            "created_at": datetime(2026, 10, 5, tzinfo=UTC),
        }
    )

    assert reloaded == trace
    [item] = read.trace_json.claims[0].unverified_citations
    assert item.meaning_passage.source_text == ENCRYPTED
    assert read.trace_json.grounding.citations_meaning_pointed == 1


def test_an_analysis_stored_before_the_counts_existed_validates_with_none(model):
    trace, _ = trace_with_passage(model)
    stored = json.loads(trace.model_dump_json())
    for name in (
        "citations_meaning_pointed",
        "meaning_pointer_eligible",
        "meaning_pointer_attempted",
        "meaning_pointer_unavailable",
        "meaning_pointer_unavailable_reason",
        "meaning_pointer_skipped",
    ):
        del stored["grounding"][name]

    reloaded = CaseAnalysisTrace.model_validate(stored)

    assert reloaded.grounding.citations_meaning_pointed == 0
    assert reloaded.grounding.meaning_pointer_unavailable_reason is None


def test_binding_the_references_keeps_the_passage_and_the_counts(model):
    trace, _ = trace_with_passage(model)

    again = bound_references(trace)

    assert only_unverified_claim(again).unverified_citations[0].meaning_passage is not None
    assert again.grounding.citations_meaning_pointed == 1
    assert again.claims[0].epistemic_status == "not_confirmed"


def test_the_default_model_is_the_real_loader_when_nothing_is_injected(monkeypatch):
    monkeypatch.undo()
    monkeypatch.setattr(settings, "quote_meaning_pointer_path", "no/such/folder")
    nli_model.forget()

    _, grounding = bound_claims(reading_of(claim_of(UNRELATED)), bundle_of(SOURCE))

    assert grounding.meaning_pointer_unavailable == 1
    assert grounding.meaning_pointer_unavailable_reason == "weights_missing"
    nli_model.forget()


def test_a_neutral_default_changes_nothing_for_an_unrelated_claim(model):
    bound, grounding = pointed(model, FakeNli(judge=lambda p, h: NEUTRAL), claim_of(UNRELATED))

    assert only_unverified(bound).meaning_passage is None
    assert grounding.meaning_pointer_attempted == 1
