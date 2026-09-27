import pytest

from app.analysis.language import case_language, question_language
from app.sources.bundle import CaseSourceBundle, CaseSourceItem


def bundle_of(*texts: str) -> CaseSourceBundle:
    return CaseSourceBundle(
        revision=1,
        sources=tuple(
            CaseSourceItem(source_id=f"s{index}", source_kind="narrative", text=text)
            for index, text in enumerate(texts)
        ),
    )


def test_a_case_is_thai_when_any_source_is():
    assert case_language(bundle_of("Firewall log 10.0.0.5")) == "english"
    assert case_language(bundle_of("Firewall log 10.0.0.5", "ผู้เสียหายแจ้งความ")) == "thai"
    assert case_language(bundle_of()) == "english"


@pytest.mark.parametrize("reply", ["02:00", "192.168.1.10", "1+1", "?", "   "])
def test_a_question_with_no_letters_keeps_the_case_language(reply):
    assert question_language(reply, "thai") == "thai"
    assert question_language(reply, "english") == "english"


def test_a_question_with_letters_is_answered_in_its_own_language():
    assert question_language("What happened at 02:00?", "thai") == "english"
    assert question_language("เกิดอะไรขึ้นตอน 02:00", "english") == "thai"
    assert question_language("T1059 คืออะไร", "english") == "thai"
