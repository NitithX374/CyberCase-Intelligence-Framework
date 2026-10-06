import json
from copy import deepcopy

import pytest

from app.analysis import views
from app.analysis.view_model import (
    VIEW_MODEL_FILES,
    CaseViewModel,
    ClaimWordSplitter,
    load_view_model,
)
from app.analysis.views import SelectedViews, derive_claim_views, materialize_views
from app.analysis.write import joined_trace, reading_payload
from app.config import settings
from app.errors import CaseAnalysisFailure
from app.sources.bundle import CaseSourceBundle, CaseSourceItem
from app.sources.evidence import evidence_units
from app.trace.bind import bound_claims
from app.trace.claims import CaseAnalysisClaim, CaseSourceCitation
from app.trace.trace import CaseProviderJudgement, CaseProviderReading, CaseProviderReadingReply


def claim(
    text="Jane Smith, the complainant, reported losing 25,000 baht on 12 May 2026.",
    claim_id="A-01",
    source="S1",
):
    bundle = CaseSourceBundle(1, (CaseSourceItem(source, "narrative", text),))
    item = CaseAnalysisClaim(
        claim_id=claim_id,
        claim_type="reported",
        text=text,
        epistemic_status="reported",
        supporting_source_ids=[source],
        supporting_citations=[
            CaseSourceCitation(
                source_id=source, evidence_unit_ids=[evidence_units(bundle.sources[0])[0].unit_id]
            )
        ],
    )
    reading, _ = bound_claims(
        CaseProviderReading(version="case_analysis_trace_v1", claims=[item]), bundle
    )
    return reading.claims[0]


def selected(text, value):
    start = text.index(value)
    return {"text": value, "start": start, "end": start + len(value), "confidence": 0.9}


def output(text):
    return {
        "party": [{"name": selected(text, "Jane Smith"), "role": selected(text, "complainant")}],
        "timeline_event": [
            {"time": selected(text, "12 May 2026"), "event": selected(text, "losing 25,000 baht")}
        ],
        "impact": [{"description": selected(text, "losing 25,000 baht")}],
    }


class ReplayExtractor:
    def __init__(self, results):
        self.results = results
        self.received = []

    def batch_extract_json(self, texts, structures, **kwargs):
        self.received.append((texts, structures, kwargs))
        return self.results


def test_three_views_select_exact_claim_spans_and_preserve_full_attributed_context(monkeypatch):
    item = claim()
    extractor = ReplayExtractor([output(item.text)])
    monkeypatch.setattr(views, "load_view_model", lambda: CaseViewModel(extractor))
    result = derive_claim_views([item])
    assert result.parties[0].role == "complainant"
    assert result.timeline[0].event == result.impacts[0].description == item.text
    for row in [*result.parties, *result.timeline, *result.impacts]:
        assert row.claim_ids == [item.claim_id]
        assert row.projection_grounding is None
        for field_name, span in row.field_spans.items():
            assert getattr(row, field_name) == item.text[span.start : span.end]
    assert extractor.received[0][0] == [item.text]
    assert extractor.received[0][2]["include_spans"] is True
    assert extractor.received[0][2]["max_len"] is None


def test_roles_are_optional_and_never_invented_when_a_name_has_no_stated_role():
    item = claim("John sent an email.")
    raw = SelectedViews.model_validate(
        {
            "party": [{"name": selected(item.text, "John"), "role": None}],
            "timeline_event": [],
            "impact": [],
        }
    )
    parties, timeline, impacts = materialize_views(item, raw)
    assert parties[0].name == "John"
    assert parties[0].role is None
    assert set(parties[0].field_spans) == {"name"}
    assert timeline == impacts == []


def test_sdk_empty_structure_sentinel_means_no_extracted_records():
    result = SelectedViews.model_validate({"party": {}, "timeline_event": {}, "impact": {}})
    assert result.party == result.timeline_event == result.impact == []


@pytest.mark.parametrize(
    "section,field,value",
    [
        ("party", "role", "attacker"),
        ("timeline_event", "event", "encrypted the server"),
        ("impact", "description", "lost 50,000 baht"),
    ],
)
def test_invented_role_event_or_impact_fields_fail_instead_of_becoming_views(
    monkeypatch, section, field, value
):
    item = claim()
    raw = output(item.text)
    raw[section][0][field] = {"text": value, "start": 0, "end": len(value), "confidence": 0.9}
    monkeypatch.setattr(views, "load_view_model", lambda: CaseViewModel(ReplayExtractor([raw])))
    with pytest.raises(CaseAnalysisFailure) as caught:
        derive_claim_views([item])
    assert caught.value.code == "case_view_invalid"


def test_missing_event_does_not_turn_an_isolated_time_mention_into_a_timeline_event():
    item = claim()
    raw = output(item.text)
    raw["timeline_event"][0]["event"] = None
    _, timeline, _ = materialize_views(item, SelectedViews.model_validate(raw))
    assert timeline == []


def test_extraction_does_not_claim_semantic_verification_of_name_role_pairing():
    item = claim("John emailed Jane, who was identified as the victim.")
    raw = SelectedViews.model_validate(
        {
            "party": [{"name": selected(item.text, "John"), "role": selected(item.text, "victim")}],
            "timeline_event": [],
            "impact": [],
        }
    )
    parties, _, _ = materialize_views(item, raw)
    assert parties[0].projection_grounding is None
    assert parties[0].support == "bound"
    assert "involved_parties" not in reading_payload(
        CaseProviderReading(version="case_analysis_trace_v1", claims=[item])
    )


def test_unresolved_claims_are_excluded_without_loading_the_extractor(monkeypatch):
    item = claim().model_copy(
        update={"supporting_citations": [], "epistemic_status": "not_confirmed"}
    )

    def forbidden():
        raise AssertionError("Unresolved claims cannot be extraction inputs")

    monkeypatch.setattr(views, "load_view_model", forbidden)
    result = derive_claim_views([item])
    assert result.parties == result.timeline == result.impacts == []
    assert result.extraction.input_claim_ids == []
    assert result.extraction.excluded_claim_ids == [item.claim_id]


def test_same_party_across_claims_and_documents_consolidates_only_exact_name_role_pairs(
    monkeypatch,
):
    first, second = claim(), claim(claim_id="A-02", source="S2")
    extractor = ReplayExtractor([output(first.text), output(second.text)])
    monkeypatch.setattr(views, "load_view_model", lambda: CaseViewModel(extractor))
    result = derive_claim_views([first, second])
    assert len(result.parties) == len(result.timeline) == len(result.impacts) == 1
    assert result.parties[0].claim_ids == ["A-01", "A-02"]
    assert first.supporting_source_ids == ["S1"]
    assert second.supporting_source_ids == ["S2"]


def test_joined_trace_contains_derived_views_but_reader_and_judgement_contract_remain_claims_only():
    from app.chat.compose import analysis_payload

    item = claim()
    parties, timeline, impacts = materialize_views(
        item, SelectedViews.model_validate(output(item.text))
    )
    metadata = derive_claim_views([]).extraction
    derived = views.DerivedCaseViews(parties, timeline, impacts, metadata)
    reading = CaseProviderReading(version="case_analysis_trace_v1", claims=[item])
    trace = joined_trace(
        reading,
        CaseProviderJudgement(version=reading.version, summary="Jane reported a loss [A-01]."),
        views=derived,
    )
    assert trace.involved_parties == parties
    assert trace.view_extraction.method == "gliner2"
    assert set(reading_payload(reading)) == {"claims"}
    assert set(CaseProviderReadingReply.model_fields) == {"version", "claims"}
    assert (
        not {"involved_parties", "timeline", "impacts", "view_extraction"}
        & analysis_payload(trace, trace.summary).keys()
    )


def test_word_splitting_preserves_thai_and_mixed_text_offsets():
    splitter = ClaimWordSplitter(lambda text, lower: [])
    text = "ผู้ร้องเรียน Jane Smith สูญเสียเงิน 25,000 บาท"
    tokens = list(splitter(text, lower=False))
    assert len(tokens) > 5
    assert all(token == text[start:end] for token, start, end in tokens)
    assert any(token == "Jane" for token, _, _ in tokens)


def test_model_unavailable_surfaces_an_explicit_error(monkeypatch, tmp_path):
    load_view_model.cache_clear()
    monkeypatch.setattr(settings, "case_view_model_path", str(tmp_path))
    with pytest.raises(CaseAnalysisFailure) as caught:
        load_view_model()
    assert caught.value.code == "case_view_model_missing"


def test_mismatched_checkpoint_fails_before_loading_any_model(monkeypatch, tmp_path):
    load_view_model.cache_clear()
    for name in VIEW_MODEL_FILES:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"")
    (tmp_path / "cybercase_model.json").write_text(
        json.dumps({"model": "another", "revision": "0" * 40})
    )
    monkeypatch.setattr(settings, "case_view_model_path", str(tmp_path))
    with pytest.raises(CaseAnalysisFailure) as caught:
        load_view_model()
    assert caught.value.code == "case_view_model_invalid"


def test_wrong_result_count_fails_instead_of_silently_losing_claims(monkeypatch):
    monkeypatch.setattr(views, "load_view_model", lambda: CaseViewModel(ReplayExtractor([])))
    with pytest.raises(CaseAnalysisFailure, match="GLiNER2"):
        derive_claim_views([claim()])


def test_backend_trims_only_original_whitespace_and_keeps_exact_final_offsets():
    item = claim(" Jane Smith reported the loss.")
    span = views.SelectedField(text="Jane Smith", start=0, end=11, confidence=0.9)
    text, pointer = span.resolve(item)
    assert text == item.text[pointer.start : pointer.end] == "Jane Smith"


def test_invalid_offsets_and_extra_fields_fail_validation():
    item = claim()
    raw = deepcopy(output(item.text))
    raw["party"][0]["name"]["end"] = len(item.text) + 1
    with pytest.raises(ValueError):
        materialize_views(item, SelectedViews.model_validate(raw))
