from copy import deepcopy
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.analysis.write import joined_trace, reading_from, reading_payload
from app.llm.schema import structured_output_schema
from app.reports.contracts import CaseReportInput
from app.reports.display import build_case_report_content
from app.reports.render import render_case_report_html
from app.sources.bundle import CaseSourceBundle, CaseSourceItem
from app.sources.evidence import evidence_units
from app.trace.bind import bound_claims, bound_references
from app.trace.trace import CaseProviderJudgement, CaseProviderReadingReply

SOURCE = CaseSourceItem("S1", "document", "Jane reported losing 25,000 baht.", "D1", "report.pdf")
SECOND = CaseSourceItem("S2", "narrative", "The transfer was recorded on 12 May 2026.")
BUNDLE = CaseSourceBundle(3, (SOURCE, SECOND))


def reader_json():
    return {
        "version": "case_analysis_trace_v1",
        "claims": [
            {
                "claim_id": "A-01",
                "claim_type": "reported",
                "text": "Jane reported losing 25,000 baht.",
                "epistemic_status": "reported",
                "supporting_citations": [
                    {"source_id": "S1", "evidence_unit_ids": [evidence_units(SOURCE)[0].unit_id]}
                ],
                "contradicting_citations": [],
            }
        ],
    }


def test_reader_accepts_only_canonical_claims_and_selects_only_unit_references():
    reply = CaseProviderReadingReply.model_validate(reader_json())
    schema = structured_output_schema(CaseProviderReadingReply)
    assert set(schema["properties"]) == {"version", "claims"}
    assert set(schema["$defs"]["CaseReadingClaim"]["properties"]) == {
        "claim_id",
        "claim_type",
        "text",
        "epistemic_status",
        "supporting_citations",
        "contradicting_citations",
    }
    assert set(schema["$defs"]["CaseEvidenceReference"]["properties"]) == {
        "source_id",
        "evidence_unit_ids",
    }
    assert reply.model_dump() == reader_json()
    assert (
        CaseProviderReadingReply.model_validate({"version": reply.version, "claims": []}).claims
        == []
    )


@pytest.mark.parametrize(
    "field", ["involved_parties", "timeline", "impacts", "summary", "gaps", "mitre_associations"]
)
def test_reader_rejects_independently_generated_factual_views(field):
    with pytest.raises(ValidationError, match=field):
        CaseProviderReadingReply.model_validate({**reader_json(), field: []})


@pytest.mark.parametrize(
    "field",
    [
        "supporting_source_ids",
        "contradicting_source_ids",
        "reasoning_summary",
        "confidence",
        "retrieval_context_id",
    ],
)
def test_reader_rejects_duplicated_or_unverifiable_claim_state(field):
    payload = reader_json()
    payload["claims"][0][field] = []
    with pytest.raises(ValidationError, match=field):
        CaseProviderReadingReply.model_validate(payload)


@pytest.mark.parametrize(
    "field",
    [
        "exact_quote",
        "start",
        "end",
        "page_numbers",
        "document_id",
        "filename",
        "hash",
        "pointer_state",
    ],
)
def test_reader_rejects_backend_owned_citation_fields(field):
    payload = reader_json()
    payload["claims"][0]["supporting_citations"][0][field] = "invented"
    with pytest.raises(ValidationError, match=field):
        CaseProviderReadingReply.model_validate(payload)


def test_source_id_lists_are_derived_uniquely_from_selected_citations():
    payload = reader_json()
    citation = payload["claims"][0]["supporting_citations"][0]
    payload["claims"][0]["supporting_citations"].append(deepcopy(citation))
    payload["claims"][0]["contradicting_citations"] = [
        {"source_id": "S2", "evidence_unit_ids": [evidence_units(SECOND)[0].unit_id]}
    ]
    [claim] = reading_from(CaseProviderReadingReply.model_validate(payload)).claims
    assert claim.supporting_source_ids == ["S1"]
    assert claim.contradicting_source_ids == ["S2"]
    assert claim.reasoning_summary is None
    assert claim.supporting_citations[0].exact_quote == ""
    assert claim.supporting_citations[0].start is None


@pytest.mark.parametrize(
    ("source_id", "unit_id", "reason"),
    [
        ("missing", evidence_units(SOURCE)[0].unit_id, "unknown_source"),
        ("S1", "malformed", "malformed_id"),
        ("S1", evidence_units(SECOND)[0].unit_id, "cross_source"),
        ("S1", "S1:U001-0000000000000000", "stale_id"),
    ],
)
def test_invalid_provider_pointers_are_diagnosed_before_judgement(source_id, unit_id, reason):
    payload = reader_json()
    payload["claims"][0]["supporting_citations"] = [
        {"source_id": source_id, "evidence_unit_ids": [unit_id]}
    ]
    reading = reading_from(CaseProviderReadingReply.model_validate(payload))
    checked, metrics = bound_claims(reading, BUNDLE)
    [claim] = checked.claims
    assert claim.supporting_citations == []
    assert claim.invalid_evidence[0].reason == reason
    assert claim.epistemic_status == "not_confirmed"
    assert metrics.evidence_ids_invalid == 1
    assert set(reading_payload(checked)) == {"claims"}


def test_reader_does_not_construct_analytical_inferences_or_backend_confirmation_status():
    for field, value in [
        ("claim_type", "analytical_inference"),
        ("epistemic_status", "not_confirmed"),
    ]:
        payload = reader_json()
        payload["claims"][0][field] = value
        with pytest.raises(ValidationError, match=field):
            CaseProviderReadingReply.model_validate(payload)


def test_claims_only_trace_builds_a_deterministic_report_without_a_provider(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Report construction must not invoke a model")

    monkeypatch.setattr("app.llm.request.request_stage", forbidden)
    monkeypatch.setattr("app.analysis.write.request_stage", forbidden)
    checked, metrics = bound_claims(
        reading_from(CaseProviderReadingReply.model_validate(reader_json())), BUNDLE
    )
    trace = bound_references(
        joined_trace(
            checked,
            CaseProviderJudgement(
                version=checked.version, summary="Jane reported losing 25,000 baht [A-01]."
            ),
            grounding=metrics,
        )
    )
    report = build_case_report_content(
        CaseReportInput(
            case_id=uuid4(),
            case_title="A transfer",
            analysis_result_id=uuid4(),
            source_bundle=BUNDLE,
            analysis_summary=trace.summary,
            analysis_trace=trace,
        )
    )
    assert trace.involved_parties == trace.timeline == trace.impacts == []
    assert report.parties == report.timeline == report.impacts == []
    assert report.findings[0].ordinal == 1
    assert report.findings[0].text == "Jane reported losing 25,000 baht."
    assert report.findings[0].supporting_quotes == [SOURCE.text]
    assert render_case_report_html(report) == render_case_report_html(report)
