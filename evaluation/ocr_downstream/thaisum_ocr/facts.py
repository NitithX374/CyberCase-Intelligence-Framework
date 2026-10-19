"""Key-fact candidates, categories and the text normalisation the outcomes use. No model call."""
from __future__ import annotations

import re
import string
import unicodedata

from pythainlp.corpus import thai_stopwords
from pythainlp.tokenize import word_tokenize

PROVINCE_SOURCE = "F:/ThaiSum/extract_province.py"
PROVINCES = frozenset(re.findall(r'if "([^"]+)" in row\["body"\]',
                                 open(PROVINCE_SOURCE, encoding="utf-8").read()))
PLACE_PREFIXES = ("จังหวัด", "จ. ", "จ.")
STOPWORDS = frozenset(thai_stopwords())
DIGITS = frozenset("0123456789๐๑๒๓๔๕๖๗๘๙")
ZERO_WIDTH = re.compile("[\u200b\u200c\u200d\u2060\ufeff]")
PUNCTUATION = frozenset(string.punctuation) | frozenset("“”‘’…–—«»•·ๆฯ")


def normalized(text: str) -> str:
    return re.sub(r"\s+", " ", ZERO_WIDTH.sub("", unicodedata.normalize("NFC", text))).strip()


def words(text: str) -> list[tuple[str, int, int]]:
    found, position = [], 0
    for token in word_tokenize(text, engine="newmm", keep_whitespace=True):
        start = text.index(token, position)
        position = start + len(token)
        if token.strip():
            found.append((token, start, position))
    return found


def pure_punctuation(token: str) -> bool:
    return all(character in PUNCTUATION or character.isspace() for character in token)


def candidates(body: str, summary: str) -> list[str]:
    tokens = words(body)
    found: dict[str, None] = {}
    for i in range(len(tokens)):
        for n in range(1, 5):
            gram = tokens[i:i + n]
            if len(gram) < n:
                break
            if any(pure_punctuation(token) for token, _, _ in gram):
                break
            if gram[0][0] in STOPWORDS or gram[-1][0] in STOPWORDS:
                continue
            surface = body[gram[0][1]:gram[-1][2]]
            if len(surface) >= 4 and "\n" not in surface and surface in summary:
                found[surface] = None
    return list(found)


def category(surface: str) -> str:
    if any(character in DIGITS for character in surface):
        return "number"
    bare = surface
    for prefix in PLACE_PREFIXES:
        if bare.startswith(prefix):
            bare = bare[len(prefix):]
            break
    return "place" if bare in PROVINCES else "other"
