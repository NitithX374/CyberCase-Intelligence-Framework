from __future__ import annotations

from app.analysis.pipeline import AnalysisArtifacts, AnalysisInput, bind_to_case, write_analysis
from app.analysis.reading_sources import ReadingSources
from app.analysis.write import reading_request
from app.sources.bundle import CaseSourceBundle, CaseSourceItem
from app.trace.bind import bound_claims, followup_registry_items
from app.trace.claims import CaseFollowupExchange
from app.trace.trace import CaseAnalysisTrace, CaseProviderJudgement, CaseProviderReadingReply


async def test_whole_case_claims_only_reading_direct_binding_judgement_and_join(monkeypatch):
    first = CaseSourceItem(
        "S1",
        "document",
        "John is the victim.\nAt 13:00, the server was encrypted.",
        "D1",
        "statement.pdf",
    )
    second = CaseSourceItem(
        "S2",
        "document",
        "The server encryption interrupted payroll.\nJohn sent an email.",
        "D2",
        "logs.pdf",
    )
    bundle = CaseSourceBundle(4, (first, second))
    texts = [
        "John is the victim.",
        "At 13:00, the server was encrypted.",
        "Payroll was interrupted.",
        "John sent an email.",
    ]
    citations = [
        [{"source_id": "S1", "evidence_unit_ids": ["U001"]}],
        [
            {"source_id": "S1", "evidence_unit_ids": ["U002"]},
            {"source_id": "S2", "evidence_unit_ids": ["U001"]},
        ],
        [{"source_id": "S2", "evidence_unit_ids": ["U001"]}],
        [{"source_id": "S2", "evidence_unit_ids": ["U002"]}],
    ]
    reply = CaseProviderReadingReply.model_validate(
        {
            "version": "case_analysis_trace_v1",
            "claims": [
                {
                    "claim_id": f"A-0{index}",
                    "claim_type": "reported",
                    "epistemic_status": "reported",
                    "text": text,
                    "supporting_citations": evidence,
                }
                for index, (text, evidence) in enumerate(zip(texts, citations, strict=True), 1)
            ],
        }
    )

    seen = []

    async def request_stage(**kwargs):
        seen.append(kwargs)
        if kwargs["stage"] == "case_reading":
            assert len(kwargs["content"]["case_sources"]) == 2
            assert "technical_context" not in kwargs["content"]
            return reply
        reading = kwargs["content"]["reading"]
        assert "case_sources" not in kwargs["content"]
        assert set(reading) == {"claims"}
        assert all(
            set(c) == {"exact_quote"}
            for claim in reading["claims"]
            for c in claim["supporting_citations"]
        )
        assert [
            [citation["exact_quote"] for citation in claim["supporting_citations"]]
            for claim in reading["claims"]
        ] == [
            [first.text.splitlines(keepends=True)[0]],
            [first.text.splitlines(keepends=True)[1], second.text.splitlines(keepends=True)[0]],
            [second.text.splitlines(keepends=True)[0]],
            [second.text.splitlines(keepends=True)[1]],
        ]
        return CaseProviderJudgement(
            version="case_analysis_trace_v1",
            summary="John is the victim [A-01]. The server was encrypted at 13:00, interrupting payroll [A-02, A-03].",
        )

    monkeypatch.setattr("app.analysis.write.request_stage", request_stage)
    data = AnalysisInput(sources=bundle)
    written = await write_analysis(data, AnalysisArtifacts())
    final = (await bind_to_case(data, written)).trace
    assert [item["stage"] for item in seen] == ["case_reading", "case_judgement"]
    assert final.claims[1].supporting_source_ids == ["S1", "S2"]
    assert all(
        citation.pointer_state == "direct"
        for claim in final.claims
        for citation in claim.supporting_citations
    )
    assert final.involved_parties == final.timeline == final.impacts == []
    assert [unit.support for unit in final.summary_units] == ["bound", "bound"]
    assert final.grounding.evidence_ids_claimed == final.grounding.evidence_ids_resolved == 5
    assert CaseAnalysisTrace.model_validate_json(final.model_dump_json()) == final


def test_answered_followups_use_the_same_unit_contract_and_unanswered_ones_are_absent():
    native = CaseSourceItem("S1", "narrative", "A payment was made.")
    history = (
        CaseFollowupExchange("QA-03", "who_affected", "Who was affected?", "John is the victim."),
        CaseFollowupExchange("QA-04", "when", "When?", None),
    )
    bundle = CaseSourceBundle(7, (native,))
    payload = reading_request(bundle, "english", history)
    assert [source["source_id"] for source in payload["case_sources"]] == ["S1", "QA-03"]
    qa = payload["case_sources"][1]
    [unit] = qa["evidence_units"]
    assert unit["unit_id"] == "U001"
    assert unit["text"] == history[0].answer
    reply = CaseProviderReadingReply.model_validate(
        {
            "version": "case_analysis_trace_v1",
            "claims": [
                {
                    "claim_id": "A-01",
                    "claim_type": "reported",
                    "epistemic_status": "reported",
                    "text": "John is the victim.",
                    "supporting_citations": [
                        {"source_id": "QA-03", "evidence_unit_ids": [unit["unit_id"]]}
                    ],
                }
            ],
        }
    )
    from app.analysis.write import reading_from

    sources = ReadingSources((*bundle.sources, *followup_registry_items(history)))
    reading, grounding = bound_claims(reading_from(reply, reading_sources=sources), bundle, history)
    assert reading.claims[0].supporting_citations[0].source_id == "QA-03"
    assert reading.claims[0].supporting_citations[0].pointer_state == "direct"
    assert grounding.sources_total == 2
    assert bundle.revision == 7
