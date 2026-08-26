"""
LegalRAG data model
===================
What a parsed Thai statute section carries, and why each field exists.

Most of these fields are here because of a guardrail rather than a feature.
`penalties_reliable`, `effective_from` and `verified_by_human` all exist so that
a downstream caller cannot quietly present unchecked or superseded text as the
law. They are carried on the *section*, not the act, because the API response
hands back sections and anything travelling separately from the text it
qualifies eventually gets separated from it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


# How a `มาตรา N` match in the raw text was classified. Kept on every section so
# the provenance survives into Qdrant and out through the API.
#   own                   — a section heading of the act being read
#   amendment_replacement — text quoted inside an amending act; it is the new
#                           wording of a section of the *parent* act, not a
#                           section of the amending act
#   recovered_midline     — a heading the transcription failed to put on its own
#                           line, recovered by the sequence audit
Origin = str

# What the section *is*, which decides whether it may be suggested as a charge.
# Kept separate from verification status because the two are independent: an
# amending provision does not become chargeable by being verified.
#   offence           — a ฐานความผิด carrying a criminal penalty. The only role
#                       that may be suggested as a charge.
#   general_principle — ตัวการ/ผู้สนับสนุน/พยายาม/เรียงกระทง. Cited *alongside* an
#                       offence, never alone. "ม.83" on its own says nothing.
#   administrative    — โทษปรับทางปกครอง. Carries a penalty, but one imposed by a
#                       committee, not obtained by a prosecutor. PDPA ม.82-89
#                       read like offences and are not; treating them as
#                       chargeable would put an อัยการ in the wrong forum.
#   civil             — ความรับผิดทางแพ่ง (PDPA ม.77-78). Damages, not charges.
#   sentencing        — โทษและวิธีการเพื่อความปลอดภัย. What may be done to a
#                       convicted person: ป.อาญา ม.๓๓ ริบทรัพย์ (forfeiture of
#                       devices) is asked for in cyber cases constantly, and
#                       ม.๙๑ เรียงกระทง decides how counts are punished. Cited in
#                       the prayer for relief, never as the charge.
#   limitation        — อายุความ (ป.อาญา ม.๙๕-๑๐๑). Kept separate because
#                       "is it out of time" is a question a prosecutor must ask
#                       about every charge, independently of what the charge is.
#   procedural        — powers of officers, search, seizure, blocking, evidence.
#   definition        — บทนิยาม and commencement provisions.
#   transitional      — บทเฉพาะกาล. Sets up the machinery of a new act.
#   amending          — "ให้ยกเลิกความในมาตรา ๑๔ และให้ใช้ความต่อไปนี้แทน".
#                       Never a charge; suggesting one means the text was
#                       misread as an offence.
SectionRole = str

# Whether the text can be relied on, on two counts: has a human checked it, and
# do we already know part of it is superseded.
#   verified           — checked against Krisdika by a named person, and the text
#                        has not changed since that check.
#   current_unverified — believed to be the wording in force; nobody has
#                        confirmed it. The default for a fresh download.
#   conduct_only       — known to contain superseded penalties. The conduct
#                        description is usable; the penalty is removed entirely.
#   verification_stale — was verified, but the source text has changed since.
#                        Treated as unverified, and reported loudly, because a
#                        verification vouches for particular words.
VerificationStatus = str


@dataclass(frozen=True)
class ActUnit:
    """One act. Not one file — `criminal_code_1956_original.txt` holds two."""

    slug: str
    label: str
    title: str
    source_slug: str
    # Which act within the source file, in document order. The Criminal Code
    # file opens with the 1956 act that enacted the Code (ss.1-8) and then
    # carries the Code itself (ss.1-398); both restart at 1.
    ordinal: int = 0
    # What the act is expected to contain, from the act's own structure. Used to
    # fail loudly rather than silently ingesting a truncated download.
    expected_sections: int | None = None
    # False where the fetched text is a superseded edition whose penalties have
    # since been amended. Sections carrying False must never have their penalty
    # sentences quoted — see parser.PENALTY_SENTENCE_MARKERS.
    penalties_reliable: bool = True
    # Set only where the date cannot be derived from the act's own section 2 —
    # the Criminal Code's commencement is stated by the act that enacted it, not
    # by the Code.
    effective_from: date | None = None
    effective_note: str = ""
    # Blocks the derived date from being used. For acts whose commencement is
    # genuinely split across chapters, an approximate single date is worse than
    # none, because it reads as authoritative.
    suppress_derived_date: bool = False
    # Slug of the act this one amends, for amending acts.
    amends: str | None = None
    source_url: str = ""


@dataclass
class LegalSection:
    """A single มาตรา, sliced verbatim out of the raw text."""

    act_slug: str
    act_label: str
    # Canonical Arabic form, including inserted-section suffixes: "9", "16/2".
    number: str
    # As printed in the statute: "๙", "๑๖/๒".
    number_thai: str
    # ภาค / ลักษณะ / หมวด / ส่วนที่ in force at this point in the document.
    # Empty for acts that carry no internal division (the two decrees).
    hierarchy: list[str] = field(default_factory=list)
    text: str = ""
    origin: Origin = "own"
    char_start: int = 0
    char_end: int = 0

    # ── Guardrail fields ──────────────────────────────────────────────────
    effective_from: date | None = None
    effective_note: str = ""
    penalties_reliable: bool = True
    source_url: str = ""

    role: SectionRole = "offence"
    verification: VerificationStatus = "current_unverified"
    # Digest of `text` as parsed. A verification is recorded against this value,
    # so re-fetching the source and getting different words invalidates the
    # check instead of silently inheriting it.
    text_sha256: str = ""
    verified_on: date | None = None
    verified_by: str = ""
    verified_source: str = ""

    # Other sections of the same act named in this section's text, in order of
    # appearance. Penalty provisions name the duties they enforce — PDPA ม.๘๓
    # punishes breaches of ม.๒๑, ๒๒, ๒๔ … — and without the link the penalty
    # retrieves on its own and reads as a rule about nothing.
    cites: list[str] = field(default_factory=list)

    # Set on amendment_replacement sections: which act and section this text is
    # the new wording *of*.
    amends_act: str | None = None
    amends_section: str | None = None

    @property
    def verified_by_human(self) -> bool:
        """Required on the API response. Backed by `verification` so that a
        stale check reads as unverified rather than as a human's word."""
        return self.verification == "verified"

    @property
    def chargeable(self) -> bool:
        """Whether this section may be put forward as a charge at all."""
        return self.role == "offence"

    @property
    def citation(self) -> str:
        """How the section should be referred to in output, e.g. 'พ.ร.บ.คอมพิวเตอร์ 2550 มาตรา 9'."""
        return f"{self.act_label} มาตรา {self.number}"

    @property
    def paragraphs(self) -> list[str]:
        """วรรค — the section's paragraphs, in order."""
        return [ln for ln in (p.strip() for p in self.text.split("\n")) if ln]


@dataclass
class ActReport:
    """What the parser found in one act, for eyeballing before ingestion."""

    act: ActUnit
    sections: int = 0
    quoted: int = 0
    citations: int = 0
    recovered: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    duplicates: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.missing and not self.duplicates
