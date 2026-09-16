import re
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class RenderedPage:
    document_id: str
    page_number: int
    image_bytes: bytes
    media_type: str = "image/png"


@dataclass(frozen=True)
class RecognizedPage:
    text: str
    recognizer: str = "unknown"


_FIGURE_PATTERN = re.compile(
    r"<figure\b[^>]*>(.*?)</figure>", re.DOTALL | re.IGNORECASE
)


def separate_generated_visual_descriptions(text: str) -> tuple[str, list[str]]:
    descriptions = [
        " ".join(match.split())
        for match in _FIGURE_PATTERN.findall(text)
        if match.strip()
    ]
    transcription = _FIGURE_PATTERN.sub("", text)
    transcription = re.sub(r"\n{3,}", "\n\n", transcription).strip()
    return transcription, descriptions


class DocumentRecognizer(Protocol):
    async def recognize_page(self, page: RenderedPage) -> RecognizedPage: ...


__all__ = [
    "DocumentRecognizer",
    "RecognizedPage",
    "RenderedPage",
    "separate_generated_visual_descriptions",
]
