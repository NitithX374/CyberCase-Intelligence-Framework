import pytest
from app.services.case_analysis.claim_anchored.assembly import assemble_trace
from app.services.case_analysis.claim_anchored.binder import bind_claims
from app.services.case_analysis.claim_anchored.contracts import (
    ExtractedClaims,
    GeneratedSummary,
)
from app.services.case_analysis.claim_anchored.failure import ClaimAnchoredFailure
from app.services.case_analysis.claim_anchored.selector import select_claims
from app.services.case_analysis.claim_anchored.source_registry import (
    build_source_registry,
)
from test_claim_anchored_binding import extraction


def candidates(count=3):
    quotes = [f"fact {index:03d}" for index in range(count)]
    context = {
        "source_message_ids": ["message-1"],
        "_source_text_by_message_id": {"message-1": "; ".join(quotes)},
    }
    extracted = ExtractedClaims(
        claims=tuple(extraction(quote).claims[0] for quote in quotes)
    )
    return bind_claims(extracted, build_source_registry(context), [])


def select(values, max_claims=64, fits=lambda _: True):
    return select_claims(
        values, source_ids=("message-1",), max_claims=max_claims, fits=fits
    )


def test_selector_records_duplicates_and_claim_cap_without_silent_overflow():
    values = candidates(66)
    result = select((*values, values[0]))
    assert len(result.claims) == 64
    assert result.claims[-1].claim.claim_id == "A-64"
    assert len(result.omissions) == 3
    assert {value["reason"] for value in result.omissions} == {
        "exact_duplicate",
        "selection_budget",
    }


def test_uncertainty_is_reserved_and_cannot_be_dropped_to_fit():
    values = candidates()
    uncertain = values[2].model_copy(
        update={
            "claim": values[2].claim.model_copy(update={"epistemic_status": "unknown"})
        }
    )
    result = select((*values[:2], uncertain), max_claims=1)
    assert result.claims[0].candidate_id == uncertain.candidate_id
    assert result.claims[0].claim.claim_id == "A-01"
    with pytest.raises(ClaimAnchoredFailure) as error:
        select((*values[:2], uncertain), fits=lambda _: False)
    assert error.value.code == "claim_required_budget_exceeded"


def test_generation_cannot_lose_selected_claims_or_add_unknown_ids():
    values = select(candidates(2)).claims
    for ids, code in [
        (["A-01"], "claim_generation_mapping_loss"),
        (["A-03"], "claim_generation_unknown_id"),
    ]:
        generated = GeneratedSummary.model_validate(
            {"units": [{"text": "Summary", "claim_ids": ids}]}
        )
        with pytest.raises(ClaimAnchoredFailure) as error:
            assemble_trace(generated, values, "a" * 64, {"message-1"})
        assert error.value.code == code


def test_assembly_copies_citations_status_and_joins_only_valid_units():
    values = select(candidates(2)).claims
    generated = GeneratedSummary.model_validate(
        {
            "units": [
                {"text": "First report", "claim_ids": ["A-01"]},
                {"text": "Second report", "claim_ids": ["A-02"]},
            ]
        }
    )
    trace = assemble_trace(generated, values, "a" * 64, {"message-1"})
    assert trace.summary == "First report\n\nSecond report"
    assert trace.claims == [value.claim for value in values]
    assert trace.retrieval_context_id is None
    assert trace.mitre_associations == []


def test_selection_is_stable_and_uses_actual_fit_function():
    values = candidates(5)

    def budget(selected):
        return len(selected) <= 2

    first = select(values, fits=budget)
    assert first == select(values, fits=budget)
    assert len(first.claims) == 2 and len(first.omissions) == 3
