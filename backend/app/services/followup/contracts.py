"""Contracts and utilities for Case follow-up evaluation."""

from __future__ import annotations

import re
import unicodedata

_UNAVAILABLE_ANSWER_PHRASES = (
    "unknown",
    "unavailable",
    "not available",
    "not provided",
    "not known",
    "no information",
    "cannot be obtained",
    "can't be obtained",
    "could not be obtained",
    "couldn't be obtained",
    "cannot be determined",
    "can't be determined",
    "could not be determined",
    "couldn't be determined",
    "don't know",
    "dont know",
    "do not know",
    "i don't know",
    "i do not know",
    "we don't know",
    "we do not know",
    "not sure",
    "unsure",
    "no idea",
    "idk",
    "absent",
    "missing",
    "n/a",
    "ไม่ทราบ",
    "ยังไม่ทราบ",
    "ไม่รู้",
    "ยังไม่รู้",
    "ไม่มีข้อมูล",
    "ไม่มีรายละเอียด",
    "ไม่แน่ใจ",
    "จำไม่ได้",
    "ไม่สามารถระบุได้",
    "ไม่สามารถยืนยันได้",
    "หาไม่ได้",
    "หาไม่เจอ",
    "ไม่พบข้อมูล",
    "ไม่พร้อมใช้งาน",
    "ไม่ระบุ",
    "ไม่ชัดเจน",
)


def answer_indicates_unavailable(answer: str) -> bool:
    normalized = unicodedata.normalize("NFKC", answer)
    normalized = " ".join(normalized.split()).casefold()
    if not normalized:
        return False
    normalized = normalized.strip(" .,!?:;()[]{}")
    if normalized in {
        "none",
        "not known",
        "not available",
        "unavailable",
        "ไม่มี",
        "ไม่มีครับ",
        "ไม่มีค่ะ",
        "ไม่มีเลย",
    }:
        return True
    if re.search(r"\bnot\s+unavailable\b", normalized):
        return False
    for phrase in _UNAVAILABLE_ANSWER_PHRASES:
        if any(ord(character) > 127 for character in phrase):
            if phrase in normalized:
                return True
        elif re.search(rf"(?<!\w){re.escape(phrase)}(?!\w)", normalized):
            return True
    return False


__all__ = [
    "answer_indicates_unavailable",
]
