from __future__ import annotations

import pytest

from app.sources.bundle import CaseSourceItem
from app.sources.evidence import EvidenceIndex, evidence_units
from app.trace.quotes import MAX_QUOTE_CHARS


@pytest.mark.parametrize(
    "text",
    [
        "John reported that the finance server was encrypted. Jane received the report.",
        "ผู้เสียหายแจ้งว่ามีการโอนเงินออกจากบัญชี ธนาคารกำลังตรวจสอบรายการดังกล่าว",
        "  ผู้เสียหายแจ้งเหตุ\r\n\r\n• โอนเงิน 50,000 บาท\n<table><tr><td>บัญชี</td><td>123</td></tr></table>\n",
        "2026-10-06T13:00Z ERROR service unavailable\n13:01Z resumed\n",
        "\n\n  John sent an email.\n\nJane received it.  \n",
        "",
        " \r\n\t\n",
        ".",
        "???\n…\n",
        "😀 ผู้เสียหาย\nAn account was frozen.",
        "x" * (2 * MAX_QUOTE_CHARS + 17),
    ],
)
def test_units_partition_original_text_without_normalizing_any_character(text):
    source = CaseSourceItem("S1", "narrative", text)
    units = evidence_units(source)
    assert units == evidence_units(source)
    assert "".join(unit.text for unit in units) == text
    cursor = 0
    for unit in units:
        assert unit.source_id == source.source_id
        assert unit.start == cursor
        assert unit.text == text[unit.start : unit.end]
        assert 0 < unit.end - unit.start <= MAX_QUOTE_CHARS
        cursor = unit.end
    assert cursor == len(text)


def test_identical_source_text_and_identity_produce_stable_ids():
    first = CaseSourceItem("S1", "document", "A bank account was frozen.\nFunds were recovered.")
    copied = CaseSourceItem("S1", "document", first.text, filename="renamed.pdf")
    assert [u.unit_id for u in evidence_units(first)] == [u.unit_id for u in evidence_units(copied)]


def test_same_local_unit_number_in_two_sources_never_collides():
    first = CaseSourceItem("S1", "document", "John sent an email.")
    second = CaseSourceItem("S2", "document", first.text)
    first_unit, second_unit = evidence_units(first)[0], evidence_units(second)[0]
    assert ":U001-" in first_unit.unit_id and ":U001-" in second_unit.unit_id
    assert first_unit.unit_id != second_unit.unit_id
    index = EvidenceIndex((first, second))
    assert index.resolve("S1", first_unit.unit_id) == (first_unit, None)
    assert index.resolve("S2", second_unit.unit_id) == (second_unit, None)


def test_a_text_change_invalidates_ids_even_when_the_ordinal_stays_the_same():
    old = CaseSourceItem("S1", "narrative", "John sent an email.")
    new = CaseSourceItem("S1", "narrative", "John did not send an email.")
    assert EvidenceIndex((new,)).resolve("S1", evidence_units(old)[0].unit_id) == (None, "stale_id")


def test_an_empty_fragment_is_addressable_but_cannot_supply_support():
    source = CaseSourceItem("S1", "narrative", "\n \t")
    [unit] = evidence_units(source)
    assert EvidenceIndex((source,)).resolve("S1", unit.unit_id) == (None, "empty_unit")


def test_ambiguous_source_identities_are_refused():
    with pytest.raises(ValueError, match="identities must be unique"):
        EvidenceIndex(
            (CaseSourceItem("S1", "narrative", "One."), CaseSourceItem("S1", "narrative", "Two."))
        )
