"""
Verification store
==================
Records that a named person compared a section against Krisdika and found it
right, in a file that survives re-parsing and is committed to the repository.

The design turns on one property: **a verification is bound to the exact words
it vouched for.** Each record stores the digest of the section text as it stood
when it was checked. If the source is re-fetched and a single character differs,
the record no longer matches and the section drops back to unverified with a
`verification_stale` marker rather than carrying a human's name on text nobody
read. Wikisource is an open wiki; without this, one edit silently converts a
real check into a false assurance.

Nothing here decides whether a section is right. It records who says so, when,
and against what — so that the claim can be withdrawn or re-examined later.

Usage:
    cd rag_service/app
    python -m RAG.LegalRAG.verification --status
    python -m RAG.LegalRAG.verification --pending --role offence
    python -m RAG.LegalRAG.verification --show cca_2550 9
    python -m RAG.LegalRAG.verification --mark cca_2550 9 \
        --by "ชื่อผู้ตรวจ" --source "https://krisdika.go.th/..." --note "ตรงกัน"
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
else:  # pragma: no cover - Windows console fallback
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

STORE_PATH = Path(__file__).resolve().parent / "data" / "verified.json"


def text_digest(text: str) -> str:
    """Digest of a section's text. Whitespace is normalised first so that a
    re-render with different line wrapping does not read as a changed law."""
    return hashlib.sha256(" ".join(text.split()).encode("utf-8")).hexdigest()[:16]


@dataclass
class VerificationRecord:
    act_slug: str
    number: str
    # The text this check applies to. A mismatch invalidates the record.
    text_sha256: str
    checked_on: str
    checked_by: str
    source_url: str = ""
    note: str = ""

    @property
    def key(self) -> tuple[str, str]:
        return (self.act_slug, self.number)


def load() -> dict[tuple[str, str], VerificationRecord]:
    if not STORE_PATH.exists():
        return {}
    raw = json.loads(STORE_PATH.read_text(encoding="utf-8"))
    records = [VerificationRecord(**entry) for entry in raw]
    return {r.key: r for r in records}


def save(records: dict[tuple[str, str], VerificationRecord]) -> None:
    ordered = sorted(records.values(), key=lambda r: (r.act_slug, _sort_key(r.number)))
    STORE_PATH.write_text(
        json.dumps([asdict(r) for r in ordered], indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _sort_key(number: str) -> tuple[int, int]:
    head, _, tail = number.partition("/")
    return (int(head) if head.isdigit() else 0, int(tail) if tail.isdigit() else 0)


def apply_to(sections) -> dict[str, int]:
    """Stamp verification status onto parsed sections. Returns a tally.

    Called by the parser, so that nothing downstream can obtain a section
    without its status already attached.
    """
    records = load()
    tally = {"verified": 0, "current_unverified": 0, "conduct_only": 0, "verification_stale": 0}
    for section in sections:
        section.text_sha256 = text_digest(section.text)
        record = records.get((section.act_slug, section.number))

        if record and record.text_sha256 == section.text_sha256:
            section.verification = "verified"
            section.verified_on = _parse_date(record.checked_on)
            section.verified_by = record.checked_by
            section.verified_source = record.source_url
        elif record:
            # Checked once, but not against these words.
            section.verification = "verification_stale"
            section.verified_by = record.checked_by
            section.verified_source = record.source_url
        elif not section.penalties_reliable:
            section.verification = "conduct_only"
        else:
            section.verification = "current_unverified"
        tally[section.verification] += 1
    return tally


def _parse_date(value: str) -> date | None:
    try:
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        return None


def audit_roles(sections) -> list:
    """Sections that prescribe a penalty but are not classified as an offence.

    A provision saying `ต้องระวางโทษ` is normally a ฐานความผิด, so a mismatch
    means the role table has fallen behind the text — which is exactly what
    happened when the 2568 amendment inserted a penalties block at ม.๘/๑๑ into
    an otherwise procedural stretch of the decree.

    Only the roles that should carry no penalty language at all are examined.
    Several others mention penalties perfectly properly: `general_principle`
    (ป.อาญา ม.๘๓ borrows the penalty of the offence it attaches to),
    `limitation` (ม.๙๕ keys each period to a class of penalty), `sentencing`,
    `administrative` (ปรับทางปกครอง is a penalty, just not a prosecutable one),
    and `amending` (which quotes replacement text wholesale).

    Sections whose penalties were redacted no longer contain the word, so the
    redaction marker counts as evidence of one too — otherwise the audit would
    be blind to exactly the sections it cannot read.
    """
    checked = ("procedural", "definition", "transitional", "civil")
    return [
        s for s in sections
        if s.role in checked
        and ("ระวางโทษ" in s.text or "[อัตราโทษถูกตัดออก" in s.text)
    ]


def mark(act_slug: str, number: str, digest: str, by: str, source: str, note: str) -> VerificationRecord:
    records = load()
    record = VerificationRecord(
        act_slug=act_slug,
        number=number,
        text_sha256=digest,
        checked_on=date.today().isoformat(),
        checked_by=by,
        source_url=source,
        note=note,
    )
    records[record.key] = record
    save(records)
    return record


# ──────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────


def main() -> None:
    ap = argparse.ArgumentParser(description="Record and inspect section verifications")
    ap.add_argument("--status", action="store_true", help="Summary by act")
    ap.add_argument("--pending", action="store_true", help="List sections awaiting a check")
    ap.add_argument("--role", default="offence", help="Filter --pending by role")
    ap.add_argument("--limit", type=int, default=30)
    ap.add_argument("--audit", action="store_true", help="Find penalty provisions not marked as offences")
    ap.add_argument("--show", nargs=2, metavar=("ACT", "SECTION"), help="Print a section to compare")
    ap.add_argument("--mark", nargs=2, metavar=("ACT", "SECTION"), help="Record a check")
    ap.add_argument("--by", default="", help="Who checked it")
    ap.add_argument("--source", default="", help="URL of the authoritative text used")
    ap.add_argument("--note", default="", help="What was found")
    args = ap.parse_args()

    from .parser import parse_all  # deferred: importing the parser is not free

    sections, _ = parse_all()
    index = {(s.act_slug, s.number): s for s in sections}

    if args.show:
        section = index.get((args.show[0], args.show[1]))
        if not section:
            print(f"ไม่พบ {args.show[0]} ม.{args.show[1]}")
            return
        print(f"{section.citation}   [{section.role} / {section.verification}]")
        print(f"digest: {section.text_sha256}")
        print(f"ที่มา  : {section.source_url}")
        print(f"บังคับใช้: {section.effective_from or '—'} ({section.effective_note})")
        print("-" * 70)
        for para in section.paragraphs:
            print(para)
        print("-" * 70)
        print("ตรวจแล้วบันทึกด้วย:")
        print(f'  python -m RAG.LegalRAG.verification --mark {section.act_slug} {section.number} \\')
        print('      --by "ชื่อ" --source "URL กฤษฎีกา" --note "ตรงกัน"')
        return

    if args.mark:
        act_slug, number = args.mark
        section = index.get((act_slug, number))
        if not section:
            print(f"ไม่พบ {act_slug} ม.{number}")
            return
        if not args.by:
            print("ต้องระบุ --by (ใครเป็นคนตรวจ) — บันทึกที่ไม่มีชื่อผู้ตรวจไม่มีความหมาย")
            return
        if not args.source:
            print("ต้องระบุ --source (URL ตัวบทที่ใช้เทียบ)")
            return
        record = mark(act_slug, number, section.text_sha256, args.by, args.source, args.note)
        print(f"บันทึกแล้ว: {section.citation} โดย {record.checked_by} เมื่อ {record.checked_on}")
        print(f"  ผูกกับข้อความ digest {record.text_sha256} — ถ้าตัวบทเปลี่ยน การตรวจนี้จะเป็นโมฆะอัตโนมัติ")
        return

    tally = apply_to(sections)

    if args.audit:
        suspects = audit_roles(sections)
        if not suspects:
            print("ไม่พบมาตราที่มีบทกำหนดโทษแต่ไม่ได้จัดเป็นฐานความผิด")
            return
        print(f"⚠ {len(suspects)} มาตรามีข้อความ 'ระวางโทษ' แต่ role ไม่ใช่ offence — ตรวจ ROLE_RANGES/ROLE_OVERRIDES")
        print("-" * 78)
        for s in suspects:
            print(f"  {s.citation:<46} role={s.role}")
            print(f"      {' '.join(s.text.split())[:110]}")
        return

    if args.pending:
        pending = [
            s for s in sections
            if s.verification != "verified" and (args.role == "all" or s.role == args.role)
        ]
        print(f"รอตรวจ {len(pending)} มาตรา (role={args.role})")
        print("-" * 78)
        for s in pending[: args.limit]:
            print(f"  {s.citation:<48} [{s.verification}]")
        if len(pending) > args.limit:
            print(f"  … อีก {len(pending) - args.limit} มาตรา")
        return

    # Default: --status
    print("=" * 78)
    print(f"{'ACT':<38}{'offence':>8}{'verified':>10}{'unver':>8}{'conduct':>9}")
    print("=" * 78)
    for slug in dict.fromkeys(s.act_slug for s in sections):
        group = [s for s in sections if s.act_slug == slug]
        label = next(s.act_label for s in group)
        print(
            f"{label[:37]:<38}"
            f"{sum(1 for s in group if s.chargeable):>8}"
            f"{sum(1 for s in group if s.verification == 'verified'):>10}"
            f"{sum(1 for s in group if s.verification == 'current_unverified'):>8}"
            f"{sum(1 for s in group if s.verification == 'conduct_only'):>9}"
        )
    print("=" * 78)
    for status, count in tally.items():
        print(f"  {status:<22}{count:>5}")
    if tally["verification_stale"]:
        print(f"\n  ⚠ {tally['verification_stale']} มาตราเคยตรวจแล้วแต่ตัวบทเปลี่ยนไป — ต้องตรวจซ้ำ")
    roles = {}
    for s in sections:
        roles[s.role] = roles.get(s.role, 0) + 1
    print("\n  บทบาท:")
    for role, count in sorted(roles.items(), key=lambda kv: -kv[1]):
        note = " (เสนอเป็นข้อหาได้)" if role == "offence" else ""
        print(f"    {role:<20}{count:>5}{note}")


if __name__ == "__main__":
    main()
