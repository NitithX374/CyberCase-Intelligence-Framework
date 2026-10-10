from __future__ import annotations

import pytest

from app.sources.bundle import CaseSourceItem
from app.trace import sentences
from app.trace.sentences import get_sat_segmenter, split_sources, split_text, tokenize_sentences

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


LONG_THAI_PARAGRAPH = (
    "ผู้เสียหายเล่าว่าเมื่อวันที่ 27 ธันวาคม 2560 ได้โอนเงินจำนวน 25,000 บาท ให้ผู้ต้องหาที่ห้องพักแห่งหนึ่งในกรุงเทพมหานคร "
    "ต่อมาผู้ต้องหาไม่สามารถติดต่อได้ ผู้เสียหายจึงไปแจ้งความร้องทุกข์ต่อพนักงานสอบสวนเมื่อวันที่ 29 มกราคม 2561 "
    "เจ้าหน้าที่ตรวจสอบแล้วพบว่าพื้นที่ที่ผู้ต้องหาอ้างถึงไม่มีการเปิดให้เช่า และผู้ต้องหาอาจใช้ชื่ออื่นในการติดต่อ แต่ไม่มีเอกสารยืนยัน"
)


def test_the_thai_segmenter_is_asked_for_a_threshold_below_its_default(monkeypatch):
    asked = []

    class Segmenter:
        def split(self, text, **options):
            asked.append(options)
            return [text]

    monkeypatch.setattr(sentences, "get_sat_segmenter", lambda: Segmenter())

    assert tokenize_sentences("ผู้เสียหายโอนเงิน") == ["ผู้เสียหายโอนเงิน"]
    assert asked == [{"threshold": 0.025}]


def test_a_long_thai_paragraph_is_cut_into_sentences_rather_than_kept_whole():
    if get_sat_segmenter() is None:
        pytest.skip("the SaT segmenter is not available")
    pieces = split_text(LONG_THAI_PARAGRAPH)

    assert len(pieces) >= 3
    assert "".join(pieces).replace(" ", "") == LONG_THAI_PARAGRAPH.replace(" ", "")
