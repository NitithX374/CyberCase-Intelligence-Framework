import math
import unicodedata
from dataclasses import dataclass
from io import BytesIO

from pypdf import PdfReader

from app.services.document_ingestion.errors import (
    DocumentLimitError,
    InvalidDocumentError,
)


@dataclass(frozen=True)
class NativeTextPolicy:
    minimum_characters: int = 80
    minimum_printable_ratio: float = 0.9
    minimum_meaningful_ratio: float = 0.5
    minimum_characters_per_square_inch: float = 0.5
    minimum_unique_meaningful_characters: int = 8


@dataclass(frozen=True)
class PdfPageInspection:
    page_number: int
    text: str
    usable_native_text: bool
    warning: str | None = None


@dataclass(frozen=True)
class PdfInspection:
    page_count: int
    pages: list[PdfPageInspection]


def _normalize_text(text: str) -> str:
    lines = [" ".join(line.split()) for line in text.replace("\x00", "").splitlines()]
    return "\n".join(line for line in lines if line)


def split_native_blocks(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def _is_printable(character: str) -> bool:
    return character.isspace() or not unicodedata.category(character).startswith("C")


def _is_meaningful(character: str) -> bool:
    category = unicodedata.category(character)
    return character.isalpha() or character.isdigit() or category.startswith("M")


def _has_usable_text(
    text: str, width: float, height: float, policy: NativeTextPolicy
) -> bool:
    compact = [character for character in text if not character.isspace()]
    if not compact:
        return False
    printable_ratio = sum(_is_printable(character) for character in compact) / len(
        compact
    )
    meaningful = [character for character in compact if _is_meaningful(character)]
    meaningful_ratio = len(meaningful) / len(compact)
    square_inches = max((width * height) / math.pow(72, 2), 1)
    density = len(compact) / square_inches
    unique_meaningful = len({character.casefold() for character in meaningful})
    return all(
        (
            len(compact) >= policy.minimum_characters,
            printable_ratio >= policy.minimum_printable_ratio,
            meaningful_ratio >= policy.minimum_meaningful_ratio,
            density >= policy.minimum_characters_per_square_inch,
            unique_meaningful >= policy.minimum_unique_meaningful_characters,
        )
    )


def inspect_pdf(
    content: bytes, policy: NativeTextPolicy, max_pages: int
) -> PdfInspection:
    try:
        reader = PdfReader(BytesIO(content), strict=False)
        page_count = len(reader.pages)
    except Exception as error:
        raise InvalidDocumentError("The PDF file could not be parsed.") from error

    if page_count == 0:
        raise InvalidDocumentError("The PDF file contains no pages.")
    if page_count > max_pages:
        raise DocumentLimitError(
            "document_page_limit_exceeded",
            f"The document exceeds the {max_pages}-page ingestion limit.",
        )

    pages = []
    for page_number, page in enumerate(reader.pages, start=1):
        try:
            text = _normalize_text(page.extract_text() or "")
            width = float(page.mediabox.width)
            height = float(page.mediabox.height)
            usable = _has_usable_text(text, width, height, policy)
            pages.append(PdfPageInspection(page_number, text, usable))
        except Exception:
            pages.append(
                PdfPageInspection(
                    page_number,
                    "",
                    False,
                    f"Page {page_number}: native PDF text extraction failed; recognition was requested.",
                )
            )
    return PdfInspection(page_count=page_count, pages=pages)
