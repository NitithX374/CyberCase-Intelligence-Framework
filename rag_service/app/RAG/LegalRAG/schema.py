"""
LegalRAG API types
==================
What crosses the service boundary. Kept apart from `models.py` so that
`schemas/rag.py` can import these without pulling in the parser, and apart from
`generation.py` so importing them costs no LLM client.

Every guardrail the module enforces internally is represented here as a field,
because the boundary is where they stop being the module's business and start
being the caller's. A suggestion that arrives without `verified_by_human` looks
exactly like a verified one.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class LegalSectionRef(BaseModel):
    """One statute section, quoted verbatim, with what qualifies it."""

    model_config = ConfigDict(extra="forbid")

    citation: str
    act_label: str
    section_number: str
    # Verbatim text as parsed. Never model-generated, never paraphrased.
    text: str
    hierarchy: list[str] = Field(default_factory=list)

    # ── qualifiers that must travel with the text ─────────────────────────
    # False until a named person has checked this wording against Krisdika.
    verified_by_human: bool = False
    verification: str = "current_unverified"
    # False where the penalty wording of this edition is superseded. The
    # penalties are already removed from `text`; this says why it reads oddly.
    penalties_quotable: bool = True
    effective_from: str | None = None
    effective_note: str = ""
    # Set when the incident predates the section, or postdates a version that
    # was later replaced.
    date_warning: str = ""
    source_url: str = ""


class LegalSuggestion(BaseModel):
    """A section an incident may fall under — a suggestion, never a finding."""

    model_config = ConfigDict(extra="forbid")

    # Written by the system, not the model, so the hedge cannot be dropped:
    # "อาจเข้าข่าย …". A prosecutor decides whether an offence was committed.
    headline: str
    section: LegalSectionRef
    # Why it may apply. Model-generated prose about the *facts*, never a
    # restatement of the law.
    reasoning: str = ""
    # ATT&CK techniques that led here, when the MITRE table was supplied.
    from_techniques: list[str] = Field(default_factory=list)
    # Sections this one names, fetched alongside it. PDPA ม.๘๓ is unreadable
    # without ม.๓๗.
    related: list[LegalSectionRef] = Field(default_factory=list)


class LegalResult(BaseModel):
    """The third output of /query, beside `context` and `mitre_table`.

    Absent suggestions are not an error. A statute suggestion is an enhancement;
    losing it must not lose the MITRE mapping, so every failure path returns
    this object with `suggestions` empty and `degraded` explaining why.
    """

    model_config = ConfigDict(extra="forbid")

    suggestions: list[LegalSuggestion] = Field(default_factory=list)
    # Non-empty when something went wrong or was skipped. Human-readable Thai.
    degraded: str = ""
    # True while any section in the answer is unverified — which is all of them
    # until someone checks them against Krisdika.
    contains_unverified: bool = True
    disclaimer: str = (
        "ข้อเสนอแนะเบื้องต้นสำหรับพนักงานสอบสวน/อัยการเท่านั้น "
        "ไม่ใช่การวินิจฉัยว่ามีความผิด และตัวบทยังไม่ได้ตรวจสอบกับสำนักงานคณะกรรมการกฤษฎีกา"
    )
