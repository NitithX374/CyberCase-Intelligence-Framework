from __future__ import annotations

import asyncio
from unittest.mock import patch
from uuid import uuid4

from case_mitre_test_support import _fixtures

from app.analysis.prompts import (
    CASE_JUDGEMENT_SYSTEM_PROMPT,
    CASE_READING_JSON_PROMPT,
    CASE_READING_SYSTEM_PROMPT,
    READING_JSON_FORMAT,
)
from app.analysis.reading_sources import ReadingSources
from app.analysis.write import (
    joined_trace,
    reading_payload,
    write_trace,
)
from app.llm.settings import AnalysisPipelineConfig
from app.sources.bundle import CaseSourceBundle, CaseSourceItem
from app.sources.evidence import evidence_units
from app.trace.bind import bound_claims, bound_references, resolve_case_trace
from app.trace.claims import CaseAnalysisClaim, CaseAnalysisGap, CaseSourceCitation
from app.trace.trace import (
    CaseProviderJudgement,
    CaseProviderReading,
    CaseProviderReadingReply,
)

SOURCE_TEXT = "The finance share was encrypted overnight."


def reread_row(technique_id: str, text: str = SOURCE_TEXT) -> dict:
    return {
        "technique_id": technique_id,
        "name": technique_id,
        "description": "Adversaries may encrypt data. They do it to interrupt availability.",
        "evidence": [{"text": text, "start": 0, "end": len(text), "basis": "reread"}],
    }


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
                    CaseSourceCitation(
                        source_id=source_id,
                        evidence_unit_ids=[evidence_units(bundle.sources[0])[0].unit_id],
                    )
                ],
            )
        ],
    )


def judgement(**overrides) -> CaseProviderJudgement:
    return CaseProviderJudgement(
        version="case_analysis_trace_v1",
        summary=overrides.pop("summary", "A file share was encrypted overnight."),
        gaps=overrides.pop("gaps", []),
    )


def written(bundle: CaseSourceBundle, reading: CaseProviderReading, **options):
    seen: list[dict] = []

    async def request_stage(**kwargs):
        seen.append(kwargs)
        if kwargs["stage"] == "case_reading":
            return CaseProviderReadingReply.model_validate(
                {
                    "version": reading.version,
                    "claims": [
                        {
                            **claim.model_dump(
                                include={"claim_id", "claim_type", "text", "epistemic_status"}
                            ),
                            "supporting_citations": [
                                citation.model_dump(include={"source_id", "evidence_unit_ids"})
                                for citation in claim.supporting_citations
                            ],
                            "contradicting_citations": [],
                        }
                        for claim in reading.claims
                    ],
                }
            )
        return judgement()

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
    assert [call["schema"] for call in seen] == [CaseProviderReadingReply, CaseProviderJudgement]
    assert [claim.claim_id for claim in trace.claims] == ["A-01"]
    assert trace.summary == "A file share was encrypted overnight."


def test_reading_and_judgement_use_the_shared_prompt_structured_transport():
    bundle = case_with_one_narrative()
    _, (reading_call, judgement_call) = written(bundle, reading_of(bundle))

    assert "grammar" not in reading_call
    assert reading_call["system"] == CASE_READING_JSON_PROMPT
    assert "grammar" not in judgement_call
    assert judgement_call["system"] == CASE_JUDGEMENT_SYSTEM_PROMPT


def test_the_reading_prompt_selects_units_and_states_the_json():
    assert '"document_id"' not in READING_JSON_FORMAT
    assert '"page_numbers"' not in READING_JSON_FORMAT
    assert CASE_READING_SYSTEM_PROMPT + READING_JSON_FORMAT == CASE_READING_JSON_PROMPT
    assert "evidence_unit_ids" in READING_JSON_FORMAT
    assert "Do not reproduce source text as evidence" in CASE_READING_SYSTEM_PROMPT
    assert '"supporting_source_ids"' not in READING_JSON_FORMAT
    assert '"reasoning_summary"' not in READING_JSON_FORMAT
    assert READING_JSON_FORMAT.endswith(
        'write a double quotation mark as \\" so the JSON stays valid.'
    )


def test_a_stored_legacy_quote_remains_locatable_without_the_new_reader_contract():
    source_id = str(uuid4())
    reading = CaseProviderReading.model_validate(
        {
            "version": "case_analysis_trace_v1",
            "claims": [
                {
                    "claim_id": "A-01",
                    "claim_type": "reported",
                    "text": "The finance share was encrypted.",
                    "epistemic_status": "reported",
                    "supporting_source_ids": [source_id],
                    "contradicting_source_ids": [],
                    "reasoning_summary": None,
                    "supporting_citations": [{"source_id": source_id, "exact_quote": SOURCE_TEXT}],
                    "contradicting_citations": [],
                }
            ],
        }
    )

    bundle = CaseSourceBundle(1, (CaseSourceItem(source_id, "narrative", SOURCE_TEXT),))
    checked, _ = bound_claims(reading, bundle)
    [citation] = checked.claims[0].supporting_citations
    assert citation.exact_quote == SOURCE_TEXT
    assert citation.pointer_state == "recovered"
    assert citation.page_numbers == []


def test_neither_call_is_shown_the_technical_context():
    _, _, bundle, _, context = _fixtures()
    trace, (reading_call, judgement_call) = written(
        bundle, reading_of(bundle), language="thai", technical_context=context
    )

    assert "technical_context" not in reading_call["content"]
    assert "technical_context" not in judgement_call["content"]
    assert judgement_call["content"]["response_language"] == "thai"
    assert trace.retrieval_context_id == context.retrieval_context_id
    assert trace.mitre_associations == []


def test_the_judgement_call_receives_claims_after_their_unit_references_are_checked():
    bundle = case_with_one_narrative()
    reading = reading_of(bundle)
    _, (_, judgement_call) = written(bundle, reading)

    checked, _ = bound_claims(reading, bundle)
    assert judgement_call["content"]["reading"] == reading_payload(checked)
    assert judgement_call["content"]["reading"]["claims"][0]["claim_id"] == "A-01"


def invented_claim(source_id: str) -> CaseAnalysisClaim:
    return CaseAnalysisClaim(
        claim_id="A-02",
        claim_type="reported",
        text="The payroll server was wiped.",
        epistemic_status="reported",
        supporting_source_ids=[source_id],
        supporting_citations=[
            CaseSourceCitation(source_id=source_id, evidence_unit_ids=["invented-unit"])
        ],
    )


def test_the_judgement_excludes_a_claim_whose_unit_was_not_found_but_retains_it_for_review():
    bundle = case_with_one_narrative()
    reading = reading_of(bundle)
    reading = reading.model_copy(
        update={"claims": [*reading.claims, invented_claim(bundle.sources[0].source_id)]}
    )

    trace, (_, judgement_call) = written(bundle, reading)

    [found] = judgement_call["content"]["reading"]["claims"]
    demoted = trace.claims[1].model_dump()
    assert found["epistemic_status"] == "reported"
    assert [c["exact_quote"] for c in found["supporting_citations"]] == [SOURCE_TEXT]
    assert demoted["claim_id"] == "A-02"
    assert demoted["epistemic_status"] == "not_confirmed"
    assert demoted["supporting_citations"] == []
    assert demoted["semantic_grounding"]["verdict"] == "unassessed"
    assert trace.grounding.claims_withheld_from_judgement == 1
    assert trace.grounding.citations_claimed == 2
    assert trace.grounding.citations_verified == 1


def test_the_judgement_is_not_told_the_claims_were_verified():
    bundle = case_with_one_narrative()
    reading = reading_of(bundle)
    reading = reading.model_copy(
        update={"claims": [*reading.claims, invented_claim(bundle.sources[0].source_id)]}
    )

    _, (_, judgement_call) = written(bundle, reading)

    system = " ".join(judgement_call["system"].split())
    assert "semantic support verification" not in system
    assert "admitted" not in system
    assert "Treat these claims as the case-specific factual input for synthesis." in system
    assert "not_confirmed" not in system
    assert [claim["claim_id"] for claim in judgement_call["content"]["reading"]["claims"]] == [
        "A-01"
    ]


def test_checking_the_claims_before_the_judgement_binds_them_as_checking_after_it():
    _, _, _, _, context = _fixtures()
    bundle = case_with_one_narrative()
    source_id = bundle.sources[0].source_id
    reading = reading_of(bundle)
    [first] = reading.claims
    reading = reading.model_copy(
        update={
            "claims": [first, invented_claim(source_id), first],
        }
    )
    verdict = judgement(
        gaps=[
            CaseAnalysisGap(
                gap_id="G-01",
                gap_key="who_paid",
                topic="Payment",
                status="NOT_PROVIDED",
                description="No payment record was supplied.",
                affected_claim_ids=["A-02", "A-77"],
                reason="The loss cannot be sized without it.",
                priority="high",
                askable=True,
                clarification_question="Was any ransom paid?",
            )
        ],
    )
    mitre_table = [reread_row("T1486"), {"technique_id": "T1059.001"}]

    after = resolve_case_trace(
        joined_trace(reading, verdict, context), bundle, mitre_table=mitre_table
    )
    checked, grounding = bound_claims(reading, bundle)
    before = bound_references(joined_trace(checked, verdict, context, grounding), mitre_table)

    assert before == after
    assert [claim.epistemic_status for claim in before.claims] == ["reported", "not_confirmed"]
    assert before.grounding.claims_duplicated == 1
    assert [a.technique_id for a in before.mitre_associations] == ["T1486"]


def test_the_reading_is_given_the_case_sources_and_the_judgement_is_not():
    source = CaseSourceItem(
        source_id="s1",
        source_kind="document",
        text="The report was submitted.",
        document_id="d1",
        filename="report.pdf",
        provenance={"verification_status": "machine_read"},
    )
    reading = CaseProviderReading(
        version="case_analysis_trace_v1",
        claims=[],
    )
    trace, (reading_call,) = written(CaseSourceBundle(revision=1, sources=(source,)), reading)
    assert reading_call["content"] == {
        "response_language": "english",
        "source_revision": 1,
        "case_sources": [ReadingSources.source_payload(source)],
        "followup_history": [],
    }
    assert "text" not in reading_call["content"]["case_sources"][0]

    assert trace.grounding.claims_admitted_to_judgement == 0
    assert "no case summary was generated" in trace.summary


def test_the_trace_takes_its_claims_from_the_reading_and_its_summary_from_the_judgement():
    bundle = case_with_one_narrative()
    reading = reading_of(bundle)
    trace = joined_trace(reading, judgement(summary="Overnight encryption of a file share."))

    assert [claim.claim_id for claim in trace.claims] == ["A-01"]
    assert trace.summary == "Overnight encryption of a file share."
    assert trace.involved_parties == trace.timeline == trace.impacts == []
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
        ),
    )

    bound = resolve_case_trace(trace, bundle, mitre_table=[reread_row("T1486")])

    assert bound.gaps[0].affected_claim_ids == ["A-01"]
    assert [item.technique_id for item in bound.mitre_associations] == ["T1486"]
    assert bound.grounding.associations_outside_context == 0
    assert bound.grounding.citations_verified == 1


def test_the_judgement_is_shown_which_sentence_carries_each_claim():
    bundle = case_with_one_narrative()
    payload = reading_payload(reading_of(bundle))

    assert set(payload) == {"claims"}
    checked, _ = bound_claims(reading_of(bundle), bundle)
    assert (
        reading_payload(checked)["claims"][0]["supporting_citations"][0]["exact_quote"]
        == SOURCE_TEXT
    )
