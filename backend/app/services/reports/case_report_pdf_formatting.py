from __future__ import annotations

import re
from html import escape


def formatted_text(value: object) -> str:
    raw = plain_text(value)
    raw = re.sub(r"^#{1,6}\s*", "", raw, flags=re.MULTILINE)
    escaped = escape(raw)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escaped)
    escaped = re.sub(r"\*([^\*]+?)\*", r"<i>\1</i>", escaped)
    escaped = re.sub(r"`([^`]+?)`", r'<font name="Courier" size="7.5">\1</font>', escaped)
    return escaped.replace("\n", "<br/>")


def paragraph_text(value: object) -> str:
    return formatted_text(value)


def plain_text(value: object) -> str:
    return (
        str(value)
        .replace("\u2010", "-")
        .replace("\u2011", "-")
        .replace("\u2012", "-")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u2212", "-")
    )


__all__ = ["formatted_text", "paragraph_text", "plain_text"]
