"""What each case source looks like by the time the model sees it.

A follow-up answer is the one source that cannot be read on its own. "No
information" settles exactly one of the case's open questions, and which one it
settles is not in the reply.
"""

from __future__ import annotations

from uuid import uuid4

from app.services.case_analysis.analysis import provider_source_payload
from app.services.sources import CaseSourceItem


def test_a_follow_up_answer_carries_the_question_it_answers():
    source = CaseSourceItem(
        source_id=str(uuid4()),
        source_kind="followup_answer",
        text="No information",
        provenance={
            "origin": "case_followup",
            "gap_key": "topic:eyewitness",
            "question": "Who is the reported direct eyewitness?",
        },
    )
    payload = provider_source_payload(source)
    assert payload["answers_question"] == "Who is the reported direct eyewitness?"
    assert payload["text"] == "No information"


def test_a_narrative_carries_no_question():
    source = CaseSourceItem(
        source_id=str(uuid4()),
        source_kind="narrative",
        text="The finance share was encrypted overnight.",
    )
    assert "answers_question" not in provider_source_payload(source)


def test_a_document_still_carries_its_extraction_quality():
    source = CaseSourceItem(
        source_id=str(uuid4()),
        source_kind="document",
        text="Received statement",
        document_id=str(uuid4()),
        filename="statement.pdf",
        provenance={"extraction_method": "native", "warnings": []},
    )
    payload = provider_source_payload(source)
    assert payload["document"]["filename"] == "statement.pdf"
    assert payload["document"]["extraction_method"] == "native"
    assert "answers_question" not in payload


def test_an_answer_with_no_recorded_question_is_sent_as_it_is():
    """Sources written before the question was kept still have to go through."""

    source = CaseSourceItem(
        source_id=str(uuid4()),
        source_kind="followup_answer",
        text="Around two in the morning.",
        provenance={"origin": "case_followup"},
    )
    assert "answers_question" not in provider_source_payload(source)
