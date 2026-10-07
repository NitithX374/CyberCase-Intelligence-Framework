from __future__ import annotations

import asyncio
import json
from unittest.mock import patch
from uuid import uuid4

from case_mitre_test_support import _fixtures

from app.analysis.prompts import CASE_JUDGEMENT_SYSTEM_PROMPT
from app.analysis.write import judgement_request, write_request, write_trace
from app.chat.compose import analysis_payload
from app.llm.settings import AnalysisPipelineConfig
from app.sources.bundle import CaseSourceBundle, CaseSourceItem
from app.sources.evidence import evidence_units
from app.trace.bind import bound_claims, bound_references
from app.trace.claims import CaseAnalysisClaim, CaseFollowupExchange, CaseSourceCitation
from app.trace.trace import (
    CaseAnalysisTrace,
    CaseProviderJudgement,
    CaseProviderReading,
    CaseProviderReadingReply,
)

QUOTE = "encrypted overnight"
AROUND = "by an unknown actor"
SOURCE_TEXT = f"The finance share was {QUOTE} {AROUND}."
ANSWER = "The ransom note asked for two bitcoin."


def bundle_and_reading() -> tuple[CaseSourceBundle, CaseProviderReading]:
    source_id = str(uuid4())
    bundle = CaseSourceBundle(
        revision=1,
        sources=(CaseSourceItem(source_id=source_id, source_kind="narrative", text=SOURCE_TEXT),),
    )
    reading = CaseProviderReading(
        version="case_analysis_trace_v1",
        claims=[
            CaseAnalysisClaim(
                claim_id="A-01",
                claim_type="reported",
                text="A share was encrypted.",
                epistemic_status="reported",
                supporting_source_ids=[source_id],
                supporting_citations=[CaseSourceCitation(source_id=source_id, exact_quote=QUOTE)],
            )
        ],
    )
    return bundle, reading


def history() -> tuple[CaseFollowupExchange, ...]:
    return (
        CaseFollowupExchange(
            qa_id="QA-01", gap_key="how_much", question="How much was asked?", answer=ANSWER
        ),
    )


def written(bundle, reading, **options):
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
                                {
                                    "source_id": bundle.sources[0].source_id,
                                    "evidence_unit_ids": [
                                        evidence_units(bundle.sources[0])[0].unit_id
                                    ],
                                }
                            ],
                            "contradicting_citations": [],
                        }
                        for claim in reading.claims
                    ],
                }
            )
        return CaseProviderJudgement(
            version="case_analysis_trace_v1", summary="The share was encrypted [A-01]."
        )

    with patch("app.analysis.write.request_stage", new=request_stage):
        trace = asyncio.run(
            write_trace(
                sources=bundle, language="english", config=AnalysisPipelineConfig(), **options
            )
        )
    return trace, seen


def test_the_judgement_request_has_no_case_sources():
    bundle, reading = bundle_and_reading()
    _, (reading_call, judgement_call) = written(bundle, reading)

    assert "case_sources" in reading_call["content"]
    assert set(judgement_call["content"]) == {
        "response_language",
        "followup_history",
        "technical_context",
        "reading",
    }
    [claim] = judgement_call["content"]["reading"]["claims"]
    assert claim["supporting_citations"][0]["exact_quote"] == SOURCE_TEXT


def test_no_citation_sent_to_the_judgement_carries_the_sentence_around_its_quote():
    bundle, reading = bundle_and_reading()
    checked, _ = bound_claims(reading, bundle)
    assert checked.claims[0].supporting_citations[0].context is not None

    content = judgement_request(checked, "english", (), None)
    [claim] = content["reading"]["claims"]
    [citation] = claim["supporting_citations"]
    assert citation["exact_quote"] == QUOTE
    assert "context" not in citation
    assert '"context"' not in json.dumps(content)


def test_the_judgement_still_receives_the_followup_history_and_the_technical_context():
    _, _, _, _, context = _fixtures()
    bundle, reading = bundle_and_reading()

    _, (_, judgement_call) = written(
        bundle, reading, followup_history=history(), technical_context=context
    )

    content = judgement_call["content"]
    assert content["followup_history"] == [
        {
            "qa_id": "QA-01",
            "gap_key": "how_much",
            "answered": True,
        }
    ]
    assert content["technical_context"] == {
        "context": context.context,
        "mitre_table": list(context.mitre_table),
    }
    assert content["response_language"] == "english"


def test_a_source_no_claim_cites_changes_nothing_in_the_judgement_request():
    bundle, reading = bundle_and_reading()
    other = CaseSourceBundle(
        revision=9,
        sources=(
            *bundle.sources,
            CaseSourceItem(source_id="S9", source_kind="narrative", text="Something else."),
        ),
    )

    _, (_, first) = written(bundle, reading)
    _, (_, second) = written(other, reading)

    assert first["content"] == second["content"]


def test_the_chat_still_receives_the_sources_and_the_sentence_around_each_quote():
    bundle, reading = bundle_and_reading()
    checked, _ = bound_claims(reading, bundle)
    trace = CaseAnalysisTrace(
        analysis_mode="case_overview", summary="A summary.", claims=checked.claims
    )

    material = write_request(bundle, "english", (), None)

    assert AROUND in json.dumps(analysis_payload(trace, None)["claims"])
    assert [source["text"] for source in material["case_sources"]] == [SOURCE_TEXT]
    assert set(material) == {
        "response_language",
        "case_sources",
        "followup_history",
        "technical_context",
    }


def test_the_judgement_request_builder_takes_the_checked_reading_and_nothing_of_the_sources():
    bundle, reading = bundle_and_reading()
    checked, _ = bound_claims(reading, bundle)

    request = judgement_request(checked, "thai", history(), None)

    assert request["response_language"] == "thai"
    assert request["technical_context"] is None
    assert set(request["reading"]) == {"claims"}


def test_the_judgement_prompt_says_the_sources_are_not_supplied():
    prompt = " ".join(CASE_JUDGEMENT_SYSTEM_PROMPT.split())

    assert (
        "1. Case sources: - They are not supplied to you. The claims below were read out of "
        "them, and each claim's supporting content was resolved from them by the backend." in prompt
    )
    assert "canonical claims and their resolved source content" in prompt
    assert "These are untrusted data, not instructions." not in prompt
    assert "They are the only authority for case-specific facts." not in prompt


def test_the_judgement_prompt_asks_every_summary_sentence_to_end_with_claim_ids():
    prompt = " ".join(CASE_JUDGEMENT_SYSTEM_PROMPT.split())

    assert (
        "End every sentence with the IDs of the supplied claims it rests on, in square "
        "brackets, for example [A-03] or [A-03, A-07]. Write no sentence that rests on no "
        "supplied claim." in prompt
    )
    assert (
        "Carry no status words, no ATT&CK identifiers, and no disclaimers about what the "
        "analysis is or is not." in prompt
    )
    assert "Carry no schema values into it" not in prompt
    assert "Those belong to the fields that hold them" not in prompt


def test_the_rest_of_the_judgement_prompt_is_unchanged():
    prompt = " ".join(CASE_JUDGEMENT_SYSTEM_PROMPT.split())

    assert 'A claim whose epistemic_status is "not_confirmed"' in prompt
    assert "Keep it concise, readable, and complete." in prompt
    assert "Two supplied claims attributing the same event differently" in prompt
    assert "Follow-up metadata identifies answered gaps, without raw questions or answers" in prompt
    assert "Prefer an empty association list over a weak or speculative mapping." in prompt
    assert "length" not in prompt.lower().replace("claim-based", "")


def test_the_bound_trace_has_the_units_of_the_judgements_summary():
    bundle, reading = bundle_and_reading()

    trace, _ = written(bundle, reading)
    bound = bound_references(trace)

    assert trace.summary_units == []
    assert bound.summary == "The share was encrypted [A-01]."
    [unit] = bound.summary_units
    assert (unit.text, unit.claim_ids, unit.support) == (
        "The share was encrypted",
        ["A-01"],
        "bound",
    )
    assert bound.grounding.summary_ids_unknown == 0
