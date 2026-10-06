from test_case_report_presentation import ISSUE, _input
from test_claim_views import ReplayExtractor, output, selected

from app.analysis import views
from app.analysis.pipeline import AnalysisArtifacts, AnalysisInput, bind_to_case, write_analysis
from app.analysis.view_model import CaseViewModel
from app.reports.contracts import CaseReportInput
from app.reports.display import build_case_report_content
from app.reports.render import render_case_report_html
from app.sources.bundle import CaseSourceBundle, CaseSourceItem
from app.sources.evidence import evidence_units
from app.trace.bind import followup_registry_items
from app.trace.claims import CaseFollowupExchange
from app.trace.trace import CaseProviderJudgement, CaseProviderReadingReply


async def test_bound_multiple_documents_and_qa_create_views_without_changing_judgement(monkeypatch):
    texts = [
        "Jane Smith, the complainant, reported losing 25,000 baht on 12 May 2026.",
        "John sent an email.",
        "John is the victim.",
    ]
    sources = CaseSourceBundle(
        5,
        (
            CaseSourceItem("S1", "document", texts[0], "D1", "statement.pdf"),
            CaseSourceItem("S2", "document", texts[1], "D2", "email.pdf"),
        ),
    )
    history = (CaseFollowupExchange("QA-03", "who_affected", "Who was affected?", texts[2]),)
    supplied = (*sources.sources, *followup_registry_items(history))
    reply = CaseProviderReadingReply.model_validate(
        {
            "version": "case_analysis_trace_v1",
            "claims": [
                {
                    "claim_id": f"A-0{index}",
                    "claim_type": "reported",
                    "epistemic_status": "reported",
                    "text": text,
                    "supporting_citations": [
                        {
                            "source_id": source.source_id,
                            "evidence_unit_ids": [evidence_units(source)[0].unit_id],
                        }
                    ],
                }
                for index, (text, source) in enumerate(zip(texts, supplied, strict=True), 1)
            ],
        }
    )
    extractor = ReplayExtractor(
        [
            output(texts[0]),
            {"party": [{"name": selected(texts[1], "John")}], "timeline_event": {}, "impact": {}},
            {
                "party": [
                    {"name": selected(texts[2], "John"), "role": selected(texts[2], "victim")}
                ],
                "timeline_event": {},
                "impact": {},
            },
        ]
    )
    monkeypatch.setattr(views, "load_view_model", lambda: CaseViewModel(extractor))
    requests = []

    async def request_stage(**request):
        requests.append(request)
        if request["stage"] == "case_reading":
            return reply
        reading = request["content"]["reading"]
        assert set(reading) == {"claims"}
        assert "field_spans" not in str(reading)
        assert "view_extraction" not in str(request["content"])
        assert [claim["text"] for claim in reading["claims"]] == texts
        assert all(
            citation["pointer_state"] == "direct"
            for claim in reading["claims"]
            for citation in claim["supporting_citations"]
        )
        return CaseProviderJudgement(version=reply.version, summary="Jane reported a loss [A-01].")

    monkeypatch.setattr("app.analysis.write.request_stage", request_stage)
    data = AnalysisInput(sources=sources, followup_history=history)
    artifacts = await write_analysis(data, AnalysisArtifacts())
    trace = (await bind_to_case(data, artifacts)).trace
    assert [request["stage"] for request in requests] == ["case_reading", "case_judgement"]
    assert [(party.name, party.role) for party in trace.involved_parties] == [
        ("Jane Smith", "complainant"),
        ("John", None),
        ("John", "victim"),
    ]
    assert trace.involved_parties[-1].claim_ids == ["A-03"]
    assert trace.claims[-1].supporting_source_ids == ["QA-03"]
    assert trace.view_extraction.input_claim_ids == ["A-01", "A-02", "A-03"]
    assert trace.timeline[0].event == trace.impacts[0].description == texts[0]
    assert trace.grounding.evidence_ids_resolved == 3
    assert extractor.received[0][0] == texts


def test_report_preserves_claim_context_and_absent_roles_for_extracted_views():
    from test_claim_views import claim

    from app.analysis.views import (
        DerivedCaseViews,
        SelectedViews,
        derive_claim_views,
        materialize_views,
    )

    item = claim("John sent an email.")
    parties, timeline, impacts = materialize_views(
        item,
        SelectedViews.model_validate(
            {"party": [{"name": selected(item.text, "John")}], "timeline_event": {}, "impact": {}}
        ),
    )
    derived = DerivedCaseViews(parties, timeline, impacts, derive_claim_views([]).extraction)
    original = _input()
    trace = original.analysis_trace.model_copy(
        update={
            "claims": [item],
            "involved_parties": derived.parties,
            "timeline": [],
            "impacts": [],
            "view_extraction": derived.extraction,
        }
    )
    report_input: CaseReportInput = original.model_copy(
        update={
            "analysis_trace": trace,
            "source_bundle": CaseSourceBundle(1, (CaseSourceItem("S1", "narrative", item.text),)),
        }
    )
    content = build_case_report_content(report_input)
    assert content.views_derived_from_claims is True
    assert content.parties[0].role is None
    assert content.parties[0].claim_context == [item.text]
    html = render_case_report_html(content, ISSUE)
    assert "John sent an email." in html
    assert "ไม่ได้สกัดบทบาท" in html
    assert "จัดรูปแบบจากข้อความข้อค้นพบ" in html
