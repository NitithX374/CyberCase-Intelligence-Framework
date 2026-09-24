from __future__ import annotations

from app.services.analysis.mitre_gate.sentences import split_sources, split_text
from app.services.sources.case_source_bundle import CaseSourceItem

THAI_REPORT = """เมื่อวันที่ 4 พฤศจิกายน 2563 ผู้เสียหายเข้าแจ้งความ
ตรวจพบ PowerShell.exe เชื่อมต่อออกไปยังไอพี 198.51.100.23 เมื่อเวลา 03.00 น.
พนักงานสอบสวนได้ยึดโทรศัพท์มือถือของผู้ต้องหาไว้เป็นของกลาง"""


def test_every_sentence_is_an_exact_piece_of_its_source():
    for sentence in split_text(THAI_REPORT):
        assert sentence in THAI_REPORT


def test_lines_are_separated_before_the_thai_splitter_sees_them():
    assert len(split_text(THAI_REPORT)) >= 3


def test_a_short_fragment_joins_the_sentence_it_belongs_to():
    trigger = "ตรวจพบ PowerShell.exe เชื่อมต่อออกไปยังไอพี 198.51.100.23 เมื่อเวลา 03.00 น."
    assert any("PowerShell.exe เชื่อมต่อ" in sentence for sentence in split_text(trigger))


def test_a_trailing_scrap_joins_the_sentence_before_it():
    line = "เว็บเซิร์ฟเวอร์ถูกโจมตีด้วย SQL injection และมีการวาง web shell ไว้ที่โฟลเดอร์ upload"
    sentences = split_text(line)

    assert sentences == [line]
    assert "upload" not in sentences


def test_english_is_split_too():
    english = "The server was compromised. A web shell was planted in the upload folder."
    assert len(split_text(english)) == 2


def test_blank_material_yields_nothing():
    assert split_text("") == []
    assert split_text("   \n\n  ") == []


def test_each_sentence_carries_the_source_it_came_from():
    sources = (
        CaseSourceItem(source_id="S1", source_kind="narrative", text=THAI_REPORT),
        CaseSourceItem(source_id="S2", source_kind="followup_answer", text="เครื่องถูกเข้ารหัสทั้งหมด"),
    )
    sentences = split_sources(sources)

    assert {item.source_id for item in sentences} == {"S1", "S2"}
    by_id = {source.source_id: source.text for source in sources}
    for sentence in sentences:
        assert sentence.text in by_id[sentence.source_id]
