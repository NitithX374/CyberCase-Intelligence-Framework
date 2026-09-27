from __future__ import annotations

from typing import Literal

from app.sources.bundle import CaseSourceBundle

ResponseLanguage = Literal["thai", "english"]


def has_thai(text: str) -> bool:
    return any("\u0e00" <= character <= "\u0e7f" for character in text)


def case_language(bundle: CaseSourceBundle) -> ResponseLanguage:
    return "thai" if any(has_thai(source.text) for source in bundle.sources) else "english"


def question_language(question: str, case: ResponseLanguage) -> ResponseLanguage:
    if has_thai(question):
        return "thai"
    if any(character.isascii() and character.isalpha() for character in question):
        return "english"
    return case


__all__ = ["ResponseLanguage", "case_language", "has_thai", "question_language"]
