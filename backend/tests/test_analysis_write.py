from __future__ import annotations

import asyncio
from unittest.mock import patch
from uuid import uuid4

from case_mitre_test_support import _fixtures

from app.analysis.write import joined_trace, reading_payload, write_trace
from app.llm.settings import AnalysisPipelineConfig
from app.sources.bundle import CaseSourceBundle, CaseSourceItem
from app.trace.bind import resolve_case_trace
from app.trace.claims import CaseAnalysisClaim, CaseAnalysisGap, CaseSourceCitation
from app.trace.trace import CaseMitreAssociation, CaseProviderJudgement, CaseProviderReading

SOURCE_TEXT = "The finance share was encrypted overnight."


def case_with_one_narrative() -> CaseSourceBundle:
    return CaseSourceBundle(
        revision=3,
        sources=(
            CaseSourceItem(source_id=str(uuid4()), source_kind="narrative", text=SOURCE_TEXT),
        ),
    )


def reading_of(bundle: CaseSourceBundle) -> CaseProviderReading:
    source_id = bundle.sources[0].source_id
    return CaseProviderReading(
        version="case_analysis_trace_v1",
        claims=[
            CaseAnalysisClaim(
                claim_id="A-01",
                claim_type="reported",
                text="The finance share was encrypted.",
                epistemic_status="reported",
                supporting_source_ids=[source_id],
                supporting_citations=[
                    CaseSourceCitation(source_id=source_id, exact_quote=SOURCE_TEXT)
                ],
            )
        ],
        involved_parties=[],
        timeline=[],
        impacts=[],
    )


def judgement(**overrides) -> CaseProviderJudgement:
    return CaseProviderJudgement(
        version="case_analysis_trace_v1",
        summary=overrides.pop("summary", "A file share was encrypted overnight."),
        gaps=overrides.pop("gaps", []),
        mitre_associations=overrides.pop("mitre_associations", []),
    )


def written(bundle: CaseSourceBundle, reading: CaseProviderReading, **options):
    seen: list[dict] = []

    async def request_stage(**kwargs):
        seen.append(kwargs)
        return reading if kwargs["stage"] == "case_reading" else judgement()

    with patch("app.analysis.write.request_stage", new=request_stage):
        trace = asyncio.run(
            write_trace(
                sources=bundle,
                language=options.pop("language", "english"),
                config=AnalysisPipelineConfig(),
                **options,
            )
        )
    return trace, seen


def test_the_analysis_is_a_reading_then_a_judgement():
    bundle = case_with_one_narrative()
    trace, seen = written(bundle, reading_of(bundle))

    assert [call["stage"] for call in seen] == ["case_reading", "case_judgement"]
    assert [call["schema"] for call in seen] == [CaseProviderReading, CaseProviderJudgement]
    assert [claim.claim_id for claim in trace.claims] == ["A-01"]
    assert trace.summary == "A file share was encrypted overnight."


def test_the_reading_call_is_never_shown_the_technical_context():
    _, _, bundle, _, context = _fixtures()
    trace, (reading_call, judgement_call) = written(
        bundle, reading_of(bundle), language="thai", technical_context=context
    )

    assert "technical_context" not in reading_call["content"]
    assert judgement_call["content"]["technical_context"] == {
        "context": context.context,
        "mitre_table": list(context.mitre_table),
    }
    assert judgement_call["content"]["response_language"] == "thai"
    assert trace.retrieval_context_id == context.retrieval_context_id


def test_the_judgement_call_receives_the_claims_the_reading_wrote():
    bundle = case_with_one_narrative()
    reading = reading_of(bundle)
    _, (_, judgement_call) = written(bundle, reading)

    assert judgement_call["content"]["reading"] == reading_payload(reading)
    assert judgement_call["content"]["reading"]["claims"][0]["claim_id"] == "A-01"


def test_each_call_is_given_the_case_sources_as_one_structured_collection():
    source = CaseSourceItem(
        source_id="s1",
        source_kind="document",
        text="The report was submitted.",
        document_id="d1",
        filename="report.pdf",
        provenance={"verification_status": "machine_read"},
    )
    reading = CaseProviderReading(
        version="case_analysis_trace_v1", claims=[], involved_parties=[], timeline=[], impacts=[]
    )
    _, (reading_call, judgement_call) = written(
        CaseSourceBundle(revision=1, sources=(source,)), reading
    )
    case_sources = [
        {
            "source_id": "s1",
            "source_kind": "document",
            "text": "The report was submitted.",
            "document": {
                "document_id": "d1",
                "filename": "report.pdf",
                "verification_status": "machine_read",
            },
        }
    ]

    assert reading_call["content"] == {
        "response_language": "english",
        "case_sources": case_sources,
        "followup_history": [],
    }
    assert judgement_call["content"] == {
        "response_language": "english",
        "case_sources": case_sources,
        "followup_history": [],
        "technical_context": None,
        "reading": reading_payload(reading),
    }


def test_the_trace_takes_its_claims_from_the_reading_and_its_summary_from_the_judgement():
    bundle = case_with_one_narrative()
    reading = reading_of(bundle)
    trace = joined_trace(reading, judgement(summary="Overnight encryption of a file share."))

    assert [claim.claim_id for claim in trace.claims] == ["A-01"]
    assert trace.summary == "Overnight encryption of a file share."
    assert trace.involved_parties == reading.involved_parties
    assert trace.grounding is None


def test_a_joined_trace_is_bound_to_the_case_like_any_other():
    bundle = case_with_one_narrative()
    trace = joined_trace(
        reading_of(bundle),
        judgement(
            gaps=[
                CaseAnalysisGap(
                    gap_id="G-01",
                    gap_key="who_paid",
                    topic="Payment",
                    status="NOT_PROVIDED",
                    description="No payment record was supplied.",
                    affected_claim_ids=["A-01", "A-77"],
                    reason="The loss cannot be sized without it.",
                    priority="high",
                    askable=True,
                    clarification_question="Was any ransom paid?",
                )
            ],
            mitre_associations=[
                CaseMitreAssociation(
                    association_id="MA-01",
                    technique_id="T1486",
                    claim_ids=["A-01"],
                    reason="The share was encrypted.",
                    status="candidate_only",
                    support_role="external_technical_context",
                )
            ],
        ),
    )

    bound = resolve_case_trace(trace, bundle, mitre_table=[{"technique_id": "T1486"}])

    assert bound.gaps[0].affected_claim_ids == ["A-01"]
    assert bound.mitre_associations == []
    assert bound.grounding.associations_outside_context == 1
    assert bound.grounding.citations_verified == 1


def test_the_judgement_is_shown_which_sentence_carries_each_claim():
    bundle = case_with_one_narrative()
    payload = reading_payload(reading_of(bundle))

    assert set(payload) == {"claims", "involved_parties", "timeline", "impacts"}
    assert payload["claims"][0]["supporting_citations"][0]["exact_quote"] == SOURCE_TEXT
