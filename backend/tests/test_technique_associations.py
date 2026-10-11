import pytest
from pydantic import ValidationError

from app.sources.bundle import CaseSourceBundle
from app.trace.associations import mapped_associations
from app.trace.bind import resolve_case_trace
from app.trace.trace import CaseAnalysisTrace, CaseProviderJudgement

FIRST = "The finance share was encrypted overnight."
SECOND = "A ransom note named a wallet address."
DESCRIPTION = (
    "Adversaries may encrypt data on target systems. They do it to interrupt availability."
)


def row(technique_id: str = "T1486", text: str = FIRST, basis: str = "reread", start: int = 0):
    return {
        "technique_id": technique_id,
        "name": "Data Encrypted for Impact",
        "entity_type": "Technique",
        "description": DESCRIPTION,
        "evidence": [{"text": text, "start": start, "end": start + len(text), "basis": basis}],
    }


def test_a_row_the_reread_tied_to_a_sentence_becomes_an_association_showing_that_sentence():
    [association] = mapped_associations([row()])

    assert association.association_id == "MA-01"
    assert association.technique_id == "T1486"
    assert association.claim_ids == []
    assert association.reason == f"“{FIRST}”"
    assert association.plain_meaning == "Adversaries may encrypt data on target systems."
    assert association.status == "candidate_only"
    assert association.support_role == "external_technical_context"


def test_a_row_with_only_retrieval_evidence_or_none_is_not_an_association():
    table = [row(basis="retrieval"), {"technique_id": "T1059", "name": "Command"}]

    assert mapped_associations(table) == []


def test_associations_follow_the_case_file_order_and_are_numbered_from_one():
    table = [row("T1059", SECOND, start=len(FIRST) + 1), row("T1486", FIRST, start=0)]

    assert [(a.association_id, a.technique_id) for a in mapped_associations(table)] == [
        ("MA-01", "T1486"),
        ("MA-02", "T1059"),
    ]


def test_a_row_the_reread_tied_to_two_sentences_quotes_both():
    two = row("T1486", FIRST, start=0)
    two["evidence"].append(
        {
            "text": SECOND,
            "start": len(FIRST) + 1,
            "end": len(FIRST) + 1 + len(SECOND),
            "basis": "reread",
        }
    )

    [association] = mapped_associations([two])

    assert association.reason == f"“{FIRST}” “{SECOND}”"


def test_a_technique_listed_twice_is_one_association():
    assert len(mapped_associations([row(), row()])) == 1


@pytest.mark.parametrize("table", [None, [], (), "rows", {"technique_id": "T1486"}, [None, 3]])
def test_without_rows_there_are_no_associations(table):
    assert mapped_associations(table) == []


def test_the_sentence_is_shown_as_the_service_sent_it_with_nothing_checked_against_the_case():
    trace = CaseAnalysisTrace(analysis_mode="case_overview", summary="No claims.", claims=[])

    bound = resolve_case_trace(
        trace,
        CaseSourceBundle(revision=1, sources=()),
        mitre_table=[row(text="A sentence no source holds.")],
    )

    [association] = bound.mitre_associations
    assert (association.technique_id, association.claim_ids) == ("T1486", [])
    assert association.reason == "“A sentence no source holds.”"
    assert bound.grounding.associations_without_claim == 0
    assert CaseAnalysisTrace.model_validate(bound.model_dump()) == bound


def test_the_judgement_can_no_longer_return_associations():
    base = {"version": "case_analysis_trace_v1", "summary": "A share was encrypted. [A-01]"}

    assert CaseProviderJudgement.model_validate({**base, "gaps": []}).gaps == []
    with pytest.raises(ValidationError):
        CaseProviderJudgement.model_validate({**base, "gaps": [], "mitre_associations": []})
