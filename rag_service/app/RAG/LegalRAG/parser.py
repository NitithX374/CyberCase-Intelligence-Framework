"""
Thai statute parser
===================
Turns the plain text under data/raw into `LegalSection` records.

Splitting a Thai act on "มาตรา" looks trivial and is not. Four things in the
downloaded text break the obvious approach, and all four are present in the six
acts fetched so far:

1. Section numbers are Thai numerals. `มาตรา\\s*(\\d+)` matches nothing at all.
   The Wikisource licence footer, by contrast, cites "มาตรา 7" of the Copyright
   Act in Arabic numerals — so the Thai-numeral rule also happens to exclude the
   page furniture for free.

2. Most `มาตรา N` occurrences are citations, not headings. The 2566 decree
   opens by citing มาตรา ๒๖, ๓๒, ๓๖, ๓๗, ๔๐ and ๑๗๒ of the Constitution. Across
   the six acts there are 672 citations against 576 headings — a splitter that
   trusts every match invents more sections than it finds. Headings sit at the
   start of a line; citations sit inside a sentence.

3. Position alone is not enough for amending acts. An amending act quotes the
   replacement text it enacts, and the quoted `มาตรา N` also begins a line. In
   the 2560 amendment the quoted CCA-2550 s.4 sits immediately before the
   amendment's own s.4, so "next number in sequence" cannot separate them
   either. What does separate them is that the replacement text is inside
   quotation marks. Quote depth is tracked across the document and a heading
   inside quotes is attributed to the act being amended, not the act being read.
   Those quoted blocks are not noise: they are the current wording of the parent
   act, which is the only consolidated text available here.

4. The transcription is not perfectly regular. Criminal Code มาตรา ๒๒๔ was
   typed onto the end of ม.๒๒๓ with no line break, so the position rule loses
   it. Nothing in the text signals this; it is only visible as a hole in the
   numbering. Every act is therefore audited against a contiguous 1..N sequence
   after classification, and a missing number is looked for mid-line and
   recovered explicitly rather than silently dropped.

Rules 2 and 3 decide, rule 4 checks. Anything the audit cannot explain is
reported rather than parsed over.

Usage:
    cd rag_service/app
    python -m RAG.LegalRAG.parser                 # summary table
    python -m RAG.LegalRAG.parser --show 10       # ten parsed sections in full
    python -m RAG.LegalRAG.parser --act cca_2550 --show 5
"""

from __future__ import annotations

import argparse
import io
import re
import sys
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

from .acts import ACT_UNITS, MISSING_ACTS, SOURCE_FILES, SOURCE_URLS, role_for
from .models import ActReport, LegalSection

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
else:  # pragma: no cover - Windows console fallback
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

RAW_DIR = Path(__file__).resolve().parent / "data" / "raw"

THAI_DIGITS = "๐๑๒๓๔๕๖๗๘๙"
_TO_ARABIC = str.maketrans(THAI_DIGITS, "0123456789")

# `มาตรา ๑๖/๒` — the slash form is an inserted section, added by a later
# amendment between two existing numbers.
SECTION_RE = re.compile(r"มาตรา\s*([๐-๙]+(?:/[๐-๙]+)?)")

# ภาค > ลักษณะ > หมวด > ส่วนที่. `ส่วนที่` is matched with its `ที่` because
# PDPA contains ordinary sentences beginning "ส่วนบุคคล…" that a bare `ส่วน`
# would swallow.
HIERARCHY_RE = re.compile(r"^(ภาค|ลักษณะ|หมวด)\s+([๐-๙]+(?:\s*ทวิ)?)\b|^(ส่วนที่)\s+([๐-๙]+)")
_LEVELS = {"ภาค": 0, "ลักษณะ": 1, "หมวด": 2, "ส่วนที่": 3}

# Where an act's operative text stops. Without these the last section of the
# Criminal Code's enacting act swallows the Code's 700-line table of contents.
END_MARKERS = (
    "ผู้รับสนองพระบรมราชโองการ",
    "หมายเหตุ :-",
    "หมายเหตุ:-",
    "งานนี้ ไม่มีลิขสิทธิ์",
    "สารบาญ",
    "อัตราค่าธรรมเนียม",
)

# Sentences carrying a penalty. Used to redact penalties out of sections whose
# act is flagged `penalties_reliable=False`, so that superseded amounts cannot
# be emitted at all rather than being emitted with a caveat attached.
PENALTY_SENTENCE_MARKERS = ("ต้องระวางโทษ", "ระวางโทษ", "มีความผิดต้องระวางโทษ")

# Appended to sections of a superseded edition that are kept whole because they
# describe penalties rather than impose them.
STALE_EDITION_NOTE = "[ฉบับ 2499 — อัตราโทษที่อ้างถึงถูกแก้ไขแล้ว ต้องตรวจสอบกับ Krisdika]"

_THAI_NUM_WORDS = {
    "ศูนย์": 0, "หนึ่ง": 1, "เอ็ด": 1, "สอง": 2, "ยี่": 2, "สาม": 3, "สี่": 4,
    "ห้า": 5, "หก": 6, "เจ็ด": 7, "แปด": 8, "เก้า": 9,
}
_THAI_NUM_SCALES = {"สิบ": 10, "ร้อย": 100, "พัน": 1000}
_THAI_NUM_TOKEN = re.compile(
    "|".join(sorted((*_THAI_NUM_WORDS, *_THAI_NUM_SCALES), key=len, reverse=True))
)
_THAI_MONTHS = {
    "มกราคม": 1, "กุมภาพันธ์": 2, "มีนาคม": 3, "เมษายน": 4, "พฤษภาคม": 5,
    "มิถุนายน": 6, "กรกฎาคม": 7, "สิงหาคม": 8, "กันยายน": 9, "ตุลาคม": 10,
    "พฤศจิกายน": 11, "ธันวาคม": 12,
}
GAZETTE_RE = re.compile(
    r"([๐-๙]{1,2})\s*(" + "|".join(_THAI_MONTHS) + r")\s*([๐-๙]{4})"
)
COMMENCEMENT_RE = re.compile(r"มาตรา\s*๒\s+(พระราช[^\n]{0,300})")


def thai_to_arabic(s: str) -> str:
    return s.translate(_TO_ARABIC)


def thai_words_to_int(text: str) -> int | None:
    """'สามสิบ' -> 30, 'หนึ่งร้อยยี่สิบ' -> 120."""
    total = current = 0
    seen = False
    for token in _THAI_NUM_TOKEN.findall(text):
        seen = True
        if token in _THAI_NUM_WORDS:
            current = _THAI_NUM_WORDS[token]
        else:
            total += (current or 1) * _THAI_NUM_SCALES[token]
            current = 0
    return (total + current) if seen else None


# ──────────────────────────────────────────────────────────────────────────
# Candidate classification
# ──────────────────────────────────────────────────────────────────────────


@dataclass
class _Candidate:
    number_thai: str
    number: str
    base: int
    start: int
    at_line_start: bool
    in_quote: bool
    # The words immediately after the number. A heading is followed by the
    # operative text; a citation is followed by a conjunction, another citation
    # or a วรรค reference. Used only when recovering a merged heading.
    tail: str = ""

    @property
    def kind(self) -> str:
        if not self.at_line_start:
            return "citation"
        return "quoted" if self.in_quote else "heading"


def quote_depths(text: str) -> list[int]:
    """Quotation nesting depth at each character.

    The downloads are inconsistent about quote characters — the 2560 amendment
    uses straight quotes throughout, the 2568 amendment uses typographic ones —
    so both are handled, straight quotes as a toggle. Every file balances to
    zero, which is what makes this usable as a classifier.
    """
    depth = 0
    out: list[int] = []
    for ch in text:
        if ch == "“":
            depth += 1
        elif ch == "”":
            depth = max(0, depth - 1)
        elif ch == '"':
            depth = 1 if depth == 0 else 0
        out.append(depth)
    return out


def find_candidates(text: str) -> list[_Candidate]:
    depths = quote_depths(text)
    found: list[_Candidate] = []
    for m in SECTION_RE.finditer(text):
        line_start = text.rfind("\n", 0, m.start()) + 1
        # A heading may be preceded by the opening quote of a replacement block:
        # `“ มาตรา ๑๑/๑ …`. Stripping quotes here is what lets the quote-depth
        # test below see it as quoted rather than missing it entirely.
        prefix = text[line_start : m.start()].strip("  \t\"“”")
        number = thai_to_arabic(m.group(1))
        found.append(
            _Candidate(
                number_thai=m.group(1),
                number=number,
                base=int(number.split("/")[0]),
                start=m.start(),
                at_line_start=prefix == "",
                in_quote=depths[m.start()] > 0,
                tail=text[m.end() : m.end() + 40],
            )
        )
    return found


def split_units(headings: list[_Candidate], expected_units: int) -> list[list[_Candidate]]:
    """Cut the heading list where numbering restarts at 1.

    Only used by the Criminal Code file, which holds the enacting act followed
    by the Code. A restart is unambiguous: an act's own numbering never returns
    to 1.
    """
    if expected_units <= 1 or not headings:
        return [headings]
    units: list[list[_Candidate]] = [[]]
    for cand in headings:
        if cand.base == 1 and cand.number == "1" and units[-1] and units[-1][-1].base > 1:
            units.append([])
        units[-1].append(cand)
    return units


# ──────────────────────────────────────────────────────────────────────────
# Effective dates
# ──────────────────────────────────────────────────────────────────────────


def derive_effective_from(text: str) -> tuple[date | None, str]:
    """Gazette date plus the commencement rule in section 2.

    Only the two unconditional patterns are derived. A commencement carrying
    `เว้นแต่` means different parts of the act started on different days, and
    those days are not in this text — that returns None so the caller has to go
    and find them rather than inheriting a date that is wrong for half the act.
    """
    gz = GAZETTE_RE.search(text[:4000])
    if not gz:
        return None, "หาวันประกาศราชกิจจานุเบกษาไม่พบ"
    day, month, year_be = int(thai_to_arabic(gz.group(1))), _THAI_MONTHS[gz.group(2)], int(thai_to_arabic(gz.group(3)))
    try:
        gazette = date(year_be - 543, month, day)
    except ValueError:
        return None, "วันประกาศในราชกิจจานุเบกษาไม่ถูกต้อง"

    m = COMMENCEMENT_RE.search(text)
    if not m:
        return None, f"ประกาศ {gazette.isoformat()} — ไม่พบมาตรา ๒ (วันบังคับใช้)"
    clause = m.group(1)
    if "เว้นแต่" in clause:
        return None, f"ประกาศ {gazette.isoformat()} — บังคับใช้ต่างวันกันรายหมวด"
    if "วันถัดจากวันประกาศ" in clause:
        return gazette + timedelta(days=1), f"ประกาศ {gazette.isoformat()}, บังคับใช้วันถัดไป"
    if "พ้นกำหนด" in clause:
        window = clause.split("พ้นกำหนด", 1)[1].split("วัน", 1)[0]
        days = thai_words_to_int(window)
        if days:
            return gazette + timedelta(days=days), f"ประกาศ {gazette.isoformat()}, พ้นกำหนด {days} วัน"
    return None, f"ประกาศ {gazette.isoformat()} — ตีความวันบังคับใช้อัตโนมัติไม่ได้"


# ──────────────────────────────────────────────────────────────────────────
# Parsing
# ──────────────────────────────────────────────────────────────────────────


def _clean(raw: str) -> str:
    """Collapse the whitespace the HTML strip left behind, keeping line breaks.

    Words are never altered — only spacing. Line breaks carry the วรรค
    (paragraph) structure and the heading positions the classifier depends on.
    """
    lines = [ln.strip("  \t") for ln in raw.split("\n")]
    return "\n".join(lines)


def _trim_at_end_marker(body: str) -> str:
    cut = len(body)
    for marker in END_MARKERS:
        idx = body.find("\n" + marker)
        if idx != -1:
            cut = min(cut, idx)
    return body[:cut].rstrip()


def redact_penalties(text: str) -> str:
    """Remove penalty sentences from text whose penalties are known superseded.

    Applied to the 1956 Criminal Code, whose fine amounts were raised across the
    board in 2560. The conduct description is what makes the section findable
    and is kept; the amounts are cut here rather than downstream, so no caller
    can quote a figure that has not been true for years.
    """
    out: list[str] = []
    for para in text.split("\n"):
        kept: list[str] = []
        for sentence in re.split(r"(?<=\S)\s{2,}|(?<=บาท)\s+(?=มาตรา)", para):
            if any(marker in sentence for marker in PENALTY_SENTENCE_MARKERS):
                head = sentence
                for marker in PENALTY_SENTENCE_MARKERS:
                    if marker in head:
                        head = head.split(marker, 1)[0]
                kept.append((head.rstrip() + " [อัตราโทษถูกตัดออก: ฉบับ 2499 ล้าสมัย ต้องตรวจสอบกับ Krisdika]").strip())
            else:
                kept.append(sentence)
        out.append(" ".join(s for s in kept if s))
    return "\n".join(out).strip()


def parse_source(source_slug: str) -> tuple[list[LegalSection], list[ActReport]]:
    """Parse one file in data/raw into sections, with a report per act."""
    path = RAW_DIR / f"{source_slug}.txt"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found — run `python -m RAG.LegalRAG.fetch_wikisource` first"
        )
    text = _clean(path.read_text(encoding="utf-8"))

    candidates = find_candidates(text)
    headings = [c for c in candidates if c.kind == "heading"]
    quoted = [c for c in candidates if c.kind == "quoted"]
    citations = [c for c in candidates if c.kind == "citation"]

    act_slugs = SOURCE_FILES[source_slug]
    units = split_units(headings, len(act_slugs))
    derived_date, derived_note = derive_effective_from(text)

    hierarchy_at = _hierarchy_index(text)
    sections: list[LegalSection] = []
    reports: list[ActReport] = []

    for idx, act_slug in enumerate(act_slugs):
        act = ACT_UNITS[act_slug]
        unit = units[idx] if idx < len(units) else []
        report = ActReport(act=act, citations=len(citations) if idx == 0 else 0)

        if not unit:
            report.warnings.append("ไม่พบมาตราใด ๆ")
            reports.append(report)
            continue

        # The act's own section 2, unless the registry states the date itself or
        # blocks derivation because no single date is true for the whole act.
        effective = act.effective_from or (None if act.suppress_derived_date else derived_date)
        note = act.effective_note or derived_note
        source_url = act.source_url or SOURCE_URLS.get(source_slug, "")

        recovered = _recover_missing(unit, candidates, report)
        unit = sorted(unit + recovered, key=lambda c: c.start)

        unit_end = units[idx + 1][0].start if idx + 1 < len(units) else len(text)
        for i, cand in enumerate(unit):
            stop = unit[i + 1].start if i + 1 < len(unit) else unit_end
            body = _trim_at_end_marker(text[cand.start : stop])
            role = role_for(act.slug, cand.number)
            # Only an offence provision *imposes* a penalty. ม.๙๕ (อายุความ) and
            # ม.๑๐๒ (นิยามลหุโทษ) merely refer to classes of penalty to define
            # something else, and cutting at "ต้องระวางโทษ" there deleted the
            # limitation table and the definition of a petty offence outright.
            # Those keep their words and carry the warning at the end instead.
            if not act.penalties_reliable:
                body = (
                    redact_penalties(body) if role == "offence"
                    else body.rstrip() + "\n" + STALE_EDITION_NOTE
                )
            sections.append(
                LegalSection(
                    act_slug=act.slug,
                    act_label=act.label,
                    number=cand.number,
                    number_thai=cand.number_thai,
                    # No special case for the Criminal Code's enacting act: its
                    # sections precede every ภาค/ลักษณะ in the file, so the
                    # lookup returns empty for them on its own.
                    hierarchy=hierarchy_at(cand.start),
                    text=body,
                    origin="recovered_midline" if cand in recovered else "own",
                    char_start=cand.start,
                    char_end=cand.start + len(body),
                    effective_from=effective,
                    effective_note=note,
                    penalties_reliable=act.penalties_reliable,
                    source_url=source_url,
                    role=role,
                    # An amending section's body contains the replacement text
                    # it enacts, whose internal references belong to the act
                    # being amended. Those links are carried by the separately
                    # emitted replacement sections instead.
                    cites=[] if role == "amending" else extract_cites(body),
                )
            )
        report.sections = len(unit)
        _audit(unit, act, report)
        reports.append(report)

    # Replacement text quoted inside an amending act belongs to the act being
    # amended. Emitted separately so a later consolidation step can overlay it
    # onto the base act; not merged here, because which wording is current on a
    # given date is a question this parser has no business answering.
    if quoted and (parent := ACT_UNITS[act_slugs[0]].amends):
        parent_act = ACT_UNITS[parent]
        for i, cand in enumerate(quoted):
            stop = quoted[i + 1].start if i + 1 < len(quoted) else len(text)
            stop = min(stop, _quote_close(text, cand.start))
            sections.append(
                LegalSection(
                    act_slug=parent_act.slug,
                    act_label=parent_act.label,
                    number=cand.number,
                    number_thai=cand.number_thai,
                    text=_trim_at_end_marker(text[cand.start : stop]),
                    origin="amendment_replacement",
                    char_start=cand.start,
                    char_end=stop,
                    effective_from=derived_date,
                    effective_note=f"ข้อความที่แก้ไขโดย {ACT_UNITS[act_slugs[0]].label} — {derived_note}",
                    penalties_reliable=parent_act.penalties_reliable,
                    source_url=SOURCE_URLS.get(source_slug, ""),
                    # Role comes from the act being amended, not the amending
                    # act: the replacement text for พ.ร.บ.คอม ม.12 is an offence
                    # provision even though the act carrying it is not.
                    role=role_for(parent_act.slug, cand.number),
                    cites=extract_cites(text[cand.start : stop]),
                    amends_act=parent_act.slug,
                    amends_section=cand.number,
                )
            )
        reports[0].quoted = len(quoted)

    return sections, reports


# A citation naming a different statute: "…มาตรา ๖ แห่งพระราชกำหนด…",
# "…มาตรา ๒๖ ของรัฐธรรมนูญ…". Such a reference is not a link within this act.
_EXTERNAL_REF = re.compile(r"แห่งพระราช|ของรัฐธรรมนูญ|ตามกฎหมายว่าด้วย|แห่งประมวลกฎหมาย")


def extract_cites(text: str) -> list[str]:
    """Sections of the same act named inside this section's text.

    The section's own heading is skipped, and a run of numbers closed by
    "แห่ง<another act>" is dropped, so that ม.๘ of the 2566 decree ("การแจ้ง
    ข้อมูล…ตามมาตรา ๖ และมาตรา ๗") links to its own act while an amending act's
    references to the act it edits do not.
    """
    found: list[str] = []
    matches = list(SECTION_RE.finditer(text))
    for i, m in enumerate(matches[1:], start=1):
        following = text[m.end() : matches[i + 1].start() if i + 1 < len(matches) else m.end() + 80]
        if _EXTERNAL_REF.search(following):
            continue
        number = thai_to_arabic(m.group(1))
        if number not in found:
            found.append(number)
    return found


def _quote_close(text: str, start: int) -> int:
    depths = quote_depths(text)
    for i in range(start, len(text)):
        if depths[i] == 0:
            return i
    return len(text)


def _hierarchy_index(text: str):
    """Return a lookup from character offset to the ภาค/ลักษณะ/หมวด in force.

    The Criminal Code repeats its whole structure in a table of contents before
    the body. That is harmless here: the body re-declares every level
    immediately before its first section, so the most recent heading at any
    section's offset is always the body's.
    """
    marks: list[tuple[int, int, str]] = []
    offset = 0
    for line in text.split("\n"):
        m = HIERARCHY_RE.match(line)
        if m:
            kind = m.group(1) or m.group(3)
            marks.append((offset, _LEVELS[kind], line.strip()))
        offset += len(line) + 1

    def at(pos: int) -> list[str]:
        state: dict[int, str] = {}
        for mark_pos, level, label in marks:
            if mark_pos > pos:
                break
            state[level] = label
            for deeper in [k for k in state if k > level]:
                del state[deeper]
        return [state[k] for k in sorted(state)]

    return at


def _recover_missing(unit: list[_Candidate], all_candidates: list[_Candidate], report: ActReport) -> list[_Candidate]:
    """Look for a heading the transcription merged into the previous line.

    Only a number that is missing from an otherwise contiguous run is looked
    for, and only between the sections that bracket it, so a citation elsewhere
    in the act cannot be mistaken for the lost heading.
    """
    present = {c.base for c in unit}
    if not present:
        return []
    holes = [n for n in range(1, max(present) + 1) if n not in present]
    if not holes:
        return []

    by_base = {c.base: c for c in unit}
    recovered: list[_Candidate] = []
    for hole in holes:
        before = by_base.get(hole - 1)
        after = by_base.get(hole + 1)
        if not before or not after:
            continue
        for cand in all_candidates:
            if (
                cand.base == hole
                and cand.kind == "citation"
                and before.start < cand.start < after.start
                # A heading opens a sentence: the section number is followed by
                # the operative text, not by a conjunction or another citation.
                and not re.match(r"\s*(และ|หรือ|ถึง|วรรค|\()", cand.tail)
            ):
                recovered.append(cand)
                report.recovered.append(f"ม.{cand.number} (ขาดการขึ้นบรรทัดใหม่)")
                break
    return recovered


def _audit(unit: list[_Candidate], act, report: ActReport) -> None:
    bases = [c.base for c in unit]
    seen: set[int] = set()
    for b in bases:
        if b in seen:
            report.duplicates.append(str(b))
        seen.add(b)
    expected = act.expected_sections
    if expected:
        report.missing = [f"ม.{n}" for n in range(1, expected + 1) if n not in seen]
        if len(unit) != expected:
            report.warnings.append(f"พบ {len(unit)} มาตรา แต่คาดว่ามี {expected}")
    if bases != sorted(bases):
        report.warnings.append("ลำดับมาตราไม่เรียง")


def parse_all() -> tuple[list[LegalSection], list[ActReport]]:
    sections: list[LegalSection] = []
    reports: list[ActReport] = []
    for source_slug in SOURCE_FILES:
        s, r = parse_source(source_slug)
        sections.extend(s)
        reports.extend(r)
    # Stamped here rather than by the caller, so there is no path that yields a
    # section without a verification status on it.
    from .verification import apply_to

    apply_to(sections)
    return sections, reports


# ──────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────


def main() -> None:
    ap = argparse.ArgumentParser(description="Parse Thai statutes into sections")
    ap.add_argument("--act", default="", help="Only this act slug")
    ap.add_argument("--show", type=int, default=0, help="Print N parsed sections in full")
    ap.add_argument("--origin", default="", help="Filter --show by origin")
    args = ap.parse_args()

    sections, reports = parse_all()

    print("=" * 78)
    print(f"{'ACT':<40}{'SECTIONS':>9}{'QUOTED':>8}{'CITES':>7}{'STATUS':>12}")
    print("=" * 78)
    for r in reports:
        status = "ok" if r.ok else "CHECK"
        print(f"{r.act.label[:39]:<40}{r.sections:>9}{r.quoted:>8}{r.citations:>7}{status:>12}")
        for w in r.warnings:
            print(f"    ! {w}")
        if r.recovered:
            print(f"    + กู้คืน: {', '.join(r.recovered)}")
        if r.missing:
            print(f"    - ขาด: {', '.join(r.missing[:12])}")
        if r.duplicates:
            print(f"    - ซ้ำ: {', '.join(r.duplicates[:12])}")
    print("=" * 78)

    own = [s for s in sections if s.origin != "amendment_replacement"]
    repl = [s for s in sections if s.origin == "amendment_replacement"]
    print(f"รวม {len(sections)} มาตรา — ของตัวบทเอง {len(own)}, ข้อความแก้ไขที่ยกมา {len(repl)}")
    print(f"ยังไม่ได้ตรวจสอบโดยมนุษย์: {sum(1 for s in sections if not s.verified_by_human)}/{len(sections)}")
    print(f"ห้ามอ้างอัตราโทษ: {sum(1 for s in sections if not s.penalties_reliable)} มาตรา")
    for label, why in MISSING_ACTS.items():
        print(f"  ยังขาด: {label} — {why}")

    if args.show:
        pool = [s for s in sections if not args.act or s.act_slug == args.act]
        if args.origin:
            pool = [s for s in pool if s.origin == args.origin]
        print("\n" + "=" * 78)
        print(f"ตัวอย่าง {min(args.show, len(pool))} มาตรา")
        print("=" * 78)
        for s in pool[: args.show]:
            head = f"[{s.origin}] {s.citation}"
            if s.hierarchy:
                head += "  ⟨" + " › ".join(s.hierarchy) + "⟩"
            print("\n" + head)
            print(f"  บังคับใช้: {s.effective_from or '—'} ({s.effective_note})")
            print(f"  ตรวจสอบแล้ว: {s.verified_by_human} | อ้างโทษได้: {s.penalties_reliable}")
            for para in s.paragraphs:
                print(f"    {para}")


if __name__ == "__main__":
    main()
