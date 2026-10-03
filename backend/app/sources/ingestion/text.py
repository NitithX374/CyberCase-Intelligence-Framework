import re

UNSTORABLE_CHARACTERS = re.compile(r"[\x00\ud800-\udfff]")


def strip_unstorable(text: str) -> str:
    return UNSTORABLE_CHARACTERS.sub("", text)
