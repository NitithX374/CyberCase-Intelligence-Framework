"""
Act registry
============
Static facts about each act that the text itself does not reliably state, and
the mapping from downloaded file to act.

The mapping is not one-to-one. `criminal_code_1956_original.txt` is the 1956 act
that *enacted* the Criminal Code, and it carries both that act (8 sections) and
the Code it enacted (398 sections). Both restart numbering at 1, so reading the
file as a single act produces two sections numbered 1, two numbered 2, and so on
up to 8.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from .models import ActUnit

WIKISOURCE = "https://th.wikisource.org/wiki/"

# Keyed by the act slug. `source_slug` is the stem of the file in data/raw.
ACT_UNITS: dict[str, ActUnit] = {
    "cca_2550": ActUnit(
        slug="cca_2550",
        label="พ.ร.บ.คอมพิวเตอร์ 2550",
        title="พระราชบัญญัติว่าด้วยการกระทำความผิดเกี่ยวกับคอมพิวเตอร์ พ.ศ. 2550",
        source_slug="cca_2550",
        expected_sections=30,
    ),
    "cca_2560_amend": ActUnit(
        slug="cca_2560_amend",
        label="พ.ร.บ.คอมพิวเตอร์ ฉบับที่ 2 (2560)",
        title="พระราชบัญญัติว่าด้วยการกระทำความผิดเกี่ยวกับคอมพิวเตอร์ (ฉบับที่ 2) พ.ศ. 2560",
        source_slug="cca_2560_amend",
        expected_sections=21,
        amends="cca_2550",
    ),
    "tech_crime_decree_2566": ActUnit(
        slug="tech_crime_decree_2566",
        label="พ.ร.ก.อาชญากรรมทางเทคโนโลยี 2566",
        title="พระราชกำหนดมาตรการป้องกันและปราบปรามอาชญากรรมทางเทคโนโลยี พ.ศ. 2566",
        source_slug="tech_crime_decree_2566",
        expected_sections=14,
    ),
    "tech_crime_decree_2568_amend": ActUnit(
        slug="tech_crime_decree_2568_amend",
        label="พ.ร.ก.อาชญากรรมทางเทคโนโลยี ฉบับที่ 2 (2568)",
        title="พระราชกำหนดมาตรการป้องกันและปราบปรามอาชญากรรมทางเทคโนโลยี (ฉบับที่ 2) พ.ศ. 2568",
        source_slug="tech_crime_decree_2568_amend",
        expected_sections=10,
        amends="tech_crime_decree_2566",
    ),
    "pdpa_2562": ActUnit(
        slug="pdpa_2562",
        label="พ.ร.บ.คุ้มครองข้อมูลส่วนบุคคล 2562",
        title="พระราชบัญญัติคุ้มครองข้อมูลส่วนบุคคล พ.ศ. 2562",
        source_slug="pdpa_2562",
        expected_sections=96,
        # PDPA section 2 carries a split commencement: most of the act took
        # effect the day after publication, but หมวด ๒, ๓, ๕, ๖, ๗ and มาตรา ๙๕
        # were deferred, and that deferral was then postponed twice by royal
        # decree. No single date is correct for the act, and the per-chapter
        # dates are not in this text. Derivation is suppressed deliberately.
        effective_note=(
            "บังคับใช้ต่างวันกันรายหมวด (มาตรา ๒ มีข้อยกเว้น) — "
            "ต้องยืนยันรายหมวดกับ Krisdika ก่อนใช้อ้างอิง"
        ),
        suppress_derived_date=True,
    ),
    "criminal_code_enacting_2499": ActUnit(
        slug="criminal_code_enacting_2499",
        label="พ.ร.บ.ให้ใช้ประมวลกฎหมายอาญา 2499",
        title="พระราชบัญญัติให้ใช้ประมวลกฎหมายอาญา พ.ศ. 2499",
        source_slug="criminal_code_1956_original",
        ordinal=0,
        expected_sections=8,
    ),
    "criminal_code_2499_original": ActUnit(
        slug="criminal_code_2499_original",
        label="ประมวลกฎหมายอาญา (ฉบับดั้งเดิม 2499)",
        title="ประมวลกฎหมายอาญา",
        source_slug="criminal_code_1956_original",
        ordinal=1,
        expected_sections=398,
        # The Code has been amended continuously since 1956. The 2560 amendment
        # raised fine amounts across the whole Code, so essentially every
        # penalty sentence in this text is superseded. Conduct descriptions are
        # still usable to locate a section; the penalties are not quotable.
        penalties_reliable=False,
        # The Code did not commence with the act that carried it. Section 3 of
        # the enacting act puts it in force on 1 January 2500 (1957), six weeks
        # after the gazette date that section 2 would otherwise imply.
        effective_from=date(1957, 1, 1),
        effective_note=(
            "ใช้บังคับ 1 ม.ค. 2500 ตามมาตรา ๓ แห่ง พ.ร.บ.ให้ใช้ฯ — "
            "ฉบับดั้งเดิม โทษถูกแก้ไขแล้ว ห้ามอ้างอัตราโทษจากฉบับนี้"
        ),
        suppress_derived_date=True,
    ),
}


# Which sections of each act do what, as (first, last, role) over the section
# number's integer part. Written out rather than inferred from หมวด headings:
# the two decrees carry no internal division at all, and this table is something
# a lawyer can check line by line, which an inference rule is not.
#
# Ranges verified against the acts' own structure:
#   พ.ร.บ.คอม  หมวด ๑ ความผิดเกี่ยวกับคอมพิวเตอร์ = ม.5-17
#              หมวด ๒ พนักงานเจ้าหน้าที่          = ม.18-30
#   PDPA       หมวด ๗ บทกำหนดโทษ                = ม.79-96
#   ป.อาญา     ภาค ๑ = ม.1-106 (ซอยตามหมวด ๑-๙), ภาค ๒ ความผิด = ม.107-366,
#              ภาค ๓ ลหุโทษ = ม.367-398
ROLE_RANGES: dict[str, list[tuple[int, int, str]]] = {
    # หมวด ๒ is titled "พนักงานเจ้าหน้าที่" but is not uniformly procedural: it
    # carries five offence provisions among the powers. ม.๒๖ (ผู้ให้บริการ must
    # keep traffic data 90 days) in particular is charged in real cases, and a
    # flat "ม.18-30 = procedural" would have hidden it.
    "cca_2550": [
        (1, 4, "definition"),
        (5, 17, "offence"),      # หมวด ๑ ความผิดเกี่ยวกับคอมพิวเตอร์
        (18, 21, "procedural"),  # อำนาจสืบสวน ยึด/อายัด ปิดกั้น
        (22, 24, "offence"),     # เปิดเผยข้อมูลโดยมิชอบ / ประมาท / ล่วงรู้แล้วเปิดเผย
        (25, 25, "procedural"),  # การรับฟังพยานหลักฐาน
        (26, 27, "offence"),     # ผู้ให้บริการไม่เก็บ log / ไม่ปฏิบัติตามคำสั่ง
        (28, 30, "procedural"),
    ],
    # PDPA หมวด ๗ บทกำหนดโทษ mixes three kinds of liability. Only ม.๗๙-๘๑ are
    # criminal. ม.๘๒-๘๙ read identically ("ต้องระวางโทษปรับทางปกครอง") but are
    # imposed by คณะกรรมการผู้เชี่ยวชาญ, not prosecuted.
    "pdpa_2562": [
        (1, 7, "definition"),
        (8, 76, "procedural"),
        (77, 78, "civil"),           # หมวด ๖ ความรับผิดทางแพ่ง
        (79, 81, "offence"),         # โทษอาญา — จำคุก/ปรับ
        (82, 89, "administrative"),  # โทษปรับทางปกครอง
        (90, 90, "procedural"),      # อำนาจสั่งปรับทางปกครอง
        (91, 96, "transitional"),    # บทเฉพาะกาล
    ],
    "tech_crime_decree_2566": [
        (1, 3, "definition"),
        (4, 8, "procedural"),   # การระงับ/อายัดบัญชี การแลกเปลี่ยนข้อมูล
        (9, 11, "offence"),     # บัญชีม้า ซื้อขายบัญชี ซิมม้า
        (12, 12, "procedural"),   # การเปิดเผย/แลกเปลี่ยนข้อมูลส่วนบุคคล
        (13, 13, "transitional"), # "ในวาระเริ่มแรก ให้นายกรัฐมนตรีแต่งตั้งคณะกรรมการ"
        (14, 14, "definition"),   # รัฐมนตรีรักษาการ
    ],
    # ภาค ๑ is not one thing. Split along its own หมวด, because the three kinds
    # of provision in it are asked about differently: whether someone is liable,
    # what may be done to them, and whether it is too late to prosecute.
    "criminal_code_2499_original": [
        (1, 1, "definition"),           # หมวด ๑ บทนิยาม
        (2, 17, "general_principle"),   # หมวด ๒ การใช้กฎหมายอาญา
        (18, 58, "sentencing"),         # หมวด ๓ โทษฯ — ม.๓๓ ริบทรัพย์ ใช้บ่อยในคดีไซเบอร์
        (59, 89, "general_principle"),  # หมวด ๔-๖ ความรับผิด, พยายาม, ตัวการ/ผู้สนับสนุน
        (90, 94, "sentencing"),         # หมวด ๗-๘ หลายบท/หลายกระทง, กระทำผิดอีก
        (95, 101, "limitation"),        # หมวด ๙ อายุความ
        (102, 106, "general_principle"),# ลักษณะ ๒ ความผิดลหุโทษ
        (107, 366, "offence"),          # ภาค ๒ ความผิด
        (367, 398, "offence"),          # ภาค ๓ ลหุโทษ
    ],
    # Every own section of an amending act is an instruction to edit another
    # act. None of them is chargeable.
    "cca_2560_amend": [(1, 999, "amending")],
    "tech_crime_decree_2568_amend": [(1, 999, "amending")],
    "criminal_code_enacting_2499": [(1, 999, "amending")],
}


# Inserted sections (มาตรา ๘/๑๑) take their number from the section they follow
# but not necessarily its character. The 2568 amendment appended a penalties
# block at ม.๘/๑๑ and ม.๘/๑๒, inside a stretch of the decree that is otherwise
# procedural, so the range table cannot see them. Listed individually.
ROLE_OVERRIDES: dict[tuple[str, str], str] = {
    ("tech_crime_decree_2566", "8/11"): "offence",   # สถาบันการเงินไม่ปฏิบัติตาม ม.๔/๒
    ("tech_crime_decree_2566", "8/12"): "offence",   # ไม่ปฏิบัติตามคำสั่งพนักงานเจ้าหน้าที่ ม.๗/๑
}


def role_for(act_slug: str, number: str) -> str:
    """Role of one section. Defaults to procedural — the safe direction, since
    an unclassified section is then never offered as a charge."""
    if (override := ROLE_OVERRIDES.get((act_slug, number))) is not None:
        return override
    try:
        base = int(number.split("/")[0])
    except ValueError:
        return "procedural"
    for first, last, role in ROLE_RANGES.get(act_slug, []):
        if first <= base <= last:
            return role
    return "procedural"


def _source_urls() -> dict[str, str]:
    """Provenance from the fetch manifest, keyed by source file slug.

    Read rather than duplicated so the URL in an API response is the URL the
    text was actually downloaded from.
    """
    manifest = Path(__file__).resolve().parent / "data" / "manifest.json"
    if not manifest.exists():
        return {}
    entries = json.loads(manifest.read_text(encoding="utf-8"))
    return {e["slug"]: e.get("source_url", "") for e in entries if e.get("slug")}


SOURCE_URLS: dict[str, str] = _source_urls()

# Files in data/raw and the acts each is expected to yield, in document order.
SOURCE_FILES: dict[str, list[str]] = {
    "cca_2550": ["cca_2550"],
    "cca_2560_amend": ["cca_2560_amend"],
    "tech_crime_decree_2566": ["tech_crime_decree_2566"],
    "tech_crime_decree_2568_amend": ["tech_crime_decree_2568_amend"],
    "pdpa_2562": ["pdpa_2562"],
    "criminal_code_1956_original": [
        "criminal_code_enacting_2499",
        "criminal_code_2499_original",
    ],
}

# Acts wanted for cybercrime work that no source has yet supplied. Carried in
# code so the gap is visible to callers rather than living only in a manifest.
MISSING_ACTS: dict[str, str] = {
    "พ.ร.บ.การรักษาความมั่นคงปลอดภัยไซเบอร์ พ.ศ. 2562": (
        "ไม่มีบน Wikisource — ต้องดึงจาก Krisdika (โครงสร้างพื้นฐานสำคัญทางสารสนเทศถูกโจมตี)"
    ),
    "ประมวลกฎหมายอาญา ฉบับรวมแก้ไขปัจจุบัน": (
        "ไม่มีบน Wikisource — ฉบับ 2499 ที่มีอยู่ใช้อ้างอัตราโทษไม่ได้"
    ),
}
