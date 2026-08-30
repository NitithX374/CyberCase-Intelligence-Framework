from typing import Literal


ResponseLanguage = Literal["thai", "english"]
VALID_RESPONSE_LANGUAGES: frozenset[str] = frozenset({"thai", "english"})


def validate_response_language(value: object) -> ResponseLanguage:
    if value == "thai":
        return "thai"
    if value == "english":
        return "english"
    raise ValueError(f"Unsupported response language: {value!r}")


def resolve_response_language(user_message: object) -> ResponseLanguage:
    if not isinstance(user_message, str) or not user_message.strip():
        raise ValueError("User message must be a non-empty string")

    if any("\u0e00" <= character <= "\u0e7f" for character in user_message):
        return "thai"
    if any(character.isascii() and character.isalpha() for character in user_message):
        return "english"

    raise ValueError("User message language must be Thai or English")


__all__ = [
    "ResponseLanguage",
    "VALID_RESPONSE_LANGUAGES",
    "resolve_response_language",
    "validate_response_language",
]
