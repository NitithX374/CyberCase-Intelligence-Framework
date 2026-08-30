"""
Legal reference API types
=========================
The third output of /query, beside the retrieval context and the MITRE mapping.

These are **references, not recommendations**. The field names, the disclaimer
and the absence of any "reasoning" or "confidence" field are all deliberate: the
service returns provisions that may bear on the incident, and deciding whether
one applies is the prosecutor's job, not this system's. Nothing here should read
as a charge being proposed.

Kept apart from the client so that `schemas/rag.py` can import these without
pulling in an HTTP client.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class LegalProvision(BaseModel):
    """One statutory provision the external service returned."""

    model_config = ConfigDict(extra="forbid")

    # As the provider labels it, e.g. "พ.ร.บ.คอมพิวเตอร์ฯ 2550 มาตรา 9".
    citation: str = ""
    title: str = ""
    # The provision's text as the provider supplied it. Never rewritten here.
    text: str = ""
    url: str = ""
    # Provider's own relevance figure, on the provider's own scale. Carried
    # through rather than normalised, because a number rescaled by us would
    # look like our judgement of relevance instead of theirs.
    score: float | None = None


class LegalReferenceResult(BaseModel):
    """Provisions that may be relevant — an aid to looking things up.

    An empty list is a normal outcome, not an error. The provisions are an
    enhancement to the response; losing them must never cost the caller its
    MITRE mapping, so every failure path returns this object with `provisions`
    empty and `degraded` saying what happened.
    """

    model_config = ConfigDict(extra="forbid")

    provisions: list[LegalProvision] = Field(default_factory=list)
    # Which service answered, and what was asked. Both travel with the result
    # so a reader can tell where a provision came from and go check it.
    provider: str = ""
    query_sent: str = ""
    # Human-readable Thai. Empty when the lookup succeeded.
    degraded: str = ""
    disclaimer: str = (
        "รายการอ้างอิงตัวบทที่อาจเกี่ยวข้อง จากบริการภายนอก "
        "ไม่ใช่การเสนอข้อหาหรือความเห็นทางกฎหมาย "
        "ผู้ใช้ต้องตรวจสอบตัวบทและความเกี่ยวข้องเองก่อนนำไปใช้"
    )
