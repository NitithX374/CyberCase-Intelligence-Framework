import asyncio

import pytest
from case_view_test_support import reply
from test_case_report_presentation import ISSUE, _input

from app.analysis import views, write
from app.analysis.pipeline import AnalysisArtifacts, AnalysisInput, bind_to_case, write_analysis
from app.errors import CaseAnalysisFailure
from app.llm.settings import AnalysisPipelineConfig
from app.reports.display import build_case_report_content
from app.reports.render import render_case_report_html
from app.sources.bundle import CaseSourceBundle, CaseSourceItem
from app.trace.claims import CaseFollowupExchange
from app.trace.trace import CaseAnalysisTrace, CaseProviderJudgement, CaseProviderReadingReply


def reading_fixture():
    texts = [
        "Jane Smith, the complainant, reported losing 25,000 baht on 12 May 2026.",
        "John sent an email.",
        "John is the victim.",
        "The server was unavailable.",
    ]
    bundle = CaseSourceBundle(
        5,
        (
            CaseSourceItem("S1", "document", texts[0], "D1", "statement.pdf"),
            CaseSourceItem("S2", "document", texts[1], "D2", "email.pdf"),
        ),
    )
    history = (CaseFollowupExchange("QA-03", "who_affected", "Who was affected?", texts[2]),)
    output = CaseProviderReadingReply.model_validate(
        {
            "version": "case_analysis_trace_v1",
            "claims": [
                {
                    "claim_id": f"A-0{index}",
                    "claim_type": "reported",
                    "text": text,
                    "epistemic_status": "reported",
                    "supporting_citations": [
                        {"source_id": source or "missing", "evidence_unit_ids": ["U001"]}
                    ],
                }
                for index, (text, source) in enumerate(
                    zip(texts, ["S1", "S2", "QA-03", None], strict=True), 1
                )
            ],
        }
    )
    return bundle, history, output


@pytest.mark.parametrize("extraction_fails", [False, True])
async def test_bound_whole_case_same_claim_set_concurrent_views_and_judgement(
    monkeypatch, extraction_fails
):
    bundle, history, reading = reading_fixture()
    views_started, judge_started = asyncio.Event(), asyncio.Event()
    requests = []
    extraction_input, judgement_input = [], []

    async def view_stage(**kwargs):
        extraction_input.extend(kwargs["content"]["claims"])
        views_started.set()
        await judge_started.wait()
        if extraction_fails:
            raise CaseAnalysisFailure("case_views_invalid", "Provider schema failed")
        return reply(
            parties=[{"name": "Jane Smith", "role": "complainant", "claim_ids": ["A-01"]}],
            timeline=[{"time": None, "event": "John sent an email.", "claim_ids": ["A-02"]}],
            impacts=[{"description": "Jane reported losing 25,000 baht.", "claim_ids": ["A-01"]}],
        )

    async def judgement_stage(**kwargs):
        requests.append(kwargs["stage"])
        if kwargs["stage"] == "case_reading":
            return reading
        assert kwargs["stage"] == "case_judgement"
        judge_started.set()
        await views_started.wait()
        assert set(kwargs["content"]["reading"]) == {"claims"}
        assert not {"parties", "timeline", "impacts", "view_extraction"} & kwargs["content"].keys()
        claims = kwargs["content"]["reading"]["claims"]
        judgement_input.extend(
            {"claim_id": item["claim_id"], "text": item["text"]} for item in claims
        )
        assert all(
            c["pointer_state"] == "direct" for item in claims for c in item["supporting_citations"]
        )
        return CaseProviderJudgement(
            version=reading.version, summary="Jane reported a loss [A-01]."
        )

    monkeypatch.setattr(views, "request_stage", view_stage)
    monkeypatch.setattr(write, "request_stage", judgement_stage)
    data = AnalysisInput(sources=bundle, followup_history=history)
    artifacts = await asyncio.wait_for(write_analysis(data, AnalysisArtifacts()), timeout=5)
    trace = (await bind_to_case(data, artifacts)).trace
    assert requests == ["case_reading", "case_judgement"]
    assert extraction_input == judgement_input
    assert len(extraction_input) == 3
    assert trace.claims[2].supporting_source_ids == ["QA-03"]
    assert trace.claims[3].epistemic_status == "not_confirmed"
    assert trace.claims[3].semantic_grounding.verdict == "unassessed"
    assert trace.grounding.claims_withheld_from_judgement == 1
    assert trace.grounding.evidence_ids_resolved == 3
    assert trace.summary_units[0].support == "bound"
    assert trace.view_extraction.excluded_claim_ids == ["A-04"]
    assert CaseAnalysisTrace.model_validate_json(trace.model_dump_json()) == trace
    if extraction_fails:
        assert trace.involved_parties == trace.timeline == trace.impacts == []
        assert trace.view_extraction.status == "failed"
        assert trace.view_extraction.warning == "case_views_invalid"
    else:
        assert trace.involved_parties[0].claim_ids == ["A-01"]
        assert trace.timeline[0].time is None
        assert trace.view_extraction.status == "completed"


async def test_judgement_failure_cancels_outstanding_extraction_without_orphan_tasks(monkeypatch):
    bundle, history, reading = reading_fixture()
    started, cancelled = asyncio.Event(), asyncio.Event()

    async def view_stage(**kwargs):
        started.set()
        try:
            await asyncio.Event().wait()
        finally:
            cancelled.set()

    async def judgement_stage(**kwargs):
        if kwargs["stage"] == "case_reading":
            return reading
        await started.wait()
        raise CaseAnalysisFailure("case_judgement_invalid", "Judgement failed")

    monkeypatch.setattr(views, "request_stage", view_stage)
    monkeypatch.setattr(write, "request_stage", judgement_stage)
    with pytest.raises(CaseAnalysisFailure) as failure:
        await write.write_trace(
            sources=bundle,
            language="english",
            followup_history=history,
            config=AnalysisPipelineConfig(),
        )
    assert failure.value.code == "case_judgement_invalid"
    assert cancelled.is_set()


def test_report_links_derived_views_to_claims_and_renders_null_times():
    from case_view_test_support import claim

    from app.trace.trace import CaseViewExtraction

    item = claim("John sent an email.")
    parties, timeline, impacts, _ = views.materialize_views(
        reply(
            parties=[{"name": "John", "role": None, "claim_ids": ["A-01"]}],
            timeline=[{"time": None, "event": item.text, "claim_ids": ["A-01"]}],
        ),
        [item],
    )
    original = _input()
    trace = original.analysis_trace.model_copy(
        update={
            "claims": [item],
            "involved_parties": parties,
            "timeline": timeline,
            "impacts": impacts,
            "view_extraction": CaseViewExtraction(
                method="llm",
                model="test/model",
                input_claim_ids=["A-01"],
                excluded_claim_ids=[],
                duration_ms=0,
            ),
        }
    )
    report_input = original.model_copy(
        update={
            "analysis_trace": trace,
            "source_bundle": CaseSourceBundle(1, (CaseSourceItem("S1", "narrative", item.text),)),
        }
    )
    content = build_case_report_content(report_input)
    assert content.views_derived_from_claims is True
    assert content.parties[0].claim_context == [item.text]
    assert content.parties[0].references
    assert content.timeline[0].time is None
    html = render_case_report_html(content, ISSUE)
    assert "John sent an email." in html
    assert "ไม่ได้สกัดบทบาท" in html
    assert "ไม่ได้สกัดวันหรือเวลา" in html
    assert "จัดรูปแบบจากข้อความข้อค้นพบ" in html
