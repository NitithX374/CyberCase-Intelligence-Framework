"""Text tidying shared by both report renderers.

The analysis writes prose with light markdown and trailing citations. The PDF and
the HTML both have to strip the same things, so they strip them the same way.
"""

from __future__ import annotations

import re

REFERENCE_SUFFIXES = (
    re.compile(r"\s*[·•]\s*อ้างอิง\s*:\s*.*$"),
    re.compile(r"\s*\(อ้างอิง\s*:\s*.*\)$"),
    re.compile(r"\s*\[อ้างอิง\s*:\s*.*\]$"),
)
HEADING_MARKER = re.compile(r"^#{1,6}\s*", flags=re.MULTILINE)
DASHES = str.maketrans(
    {"\u2010": "-", "\u2011": "-", "\u2012": "-", "\u2013": "-", "\u2014": "-", "\u2212": "-"}
)


def clean_report_text(value: object) -> str:
    """Drop markdown decoration that neither renderer displays."""

    text = HEADING_MARKER.sub("", str(value))
    return text.replace("**", "").replace("`", "")


def strip_reference_text(value: object) -> str:
    """Remove a trailing "อ้างอิง: …" that the renderer shows separately."""

    text = clean_report_text(value)
    for pattern in REFERENCE_SUFFIXES:
        text = pattern.sub("", text)
    return text.strip()


def plain_text(value: object) -> str:
    """Normalise the dashes the PDF font does not carry."""

    return str(value).translate(DASHES)


__all__ = ["clean_report_text", "plain_text", "strip_reference_text"]
