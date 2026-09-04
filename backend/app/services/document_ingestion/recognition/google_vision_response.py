from pydantic import BaseModel, Field, ValidationError

from app.services.document_ingestion.contracts import BoundingBox, OCRWord
from app.services.document_ingestion.errors import (
    RecognitionProviderError,
    RecognitionResponseError,
)


class _Vertex(BaseModel):
    x: float | None = Field(default=None, strict=True, allow_inf_nan=False)
    y: float | None = Field(default=None, strict=True, allow_inf_nan=False)


class _Polygon(BaseModel):
    vertices: list[_Vertex] = Field(default_factory=list)


class _Symbol(BaseModel):
    text: str = Field(min_length=1)


class _Word(BaseModel):
    symbols: list[_Symbol] = Field(min_length=1)
    confidence: float | None = Field(default=None, ge=0, le=1, strict=True)
    boundingBox: _Polygon | None = None


class _Paragraph(BaseModel):
    words: list[_Word] = Field(default_factory=list)


class _Block(BaseModel):
    paragraphs: list[_Paragraph] = Field(default_factory=list)


class _Page(BaseModel):
    blocks: list[_Block] = Field(default_factory=list)


class _Annotation(BaseModel):
    text: str
    pages: list[_Page] = Field(default_factory=list)


class _ProviderError(BaseModel):
    code: int = 0
    message: str = ""


class _ImageResponse(BaseModel):
    fullTextAnnotation: _Annotation | None = None
    error: _ProviderError | None = None


class _BatchResponse(BaseModel):
    responses: list[_ImageResponse] = Field(min_length=1, max_length=1)


def _bounding_box(polygon: _Polygon | None) -> BoundingBox | None:
    if polygon is None or len(polygon.vertices) != 4:
        return None
    if any(vertex.x is None or vertex.y is None for vertex in polygon.vertices):
        return None
    xs = [vertex.x for vertex in polygon.vertices]
    ys = [vertex.y for vertex in polygon.vertices]
    return BoundingBox(x0=min(xs), y0=min(ys), x1=max(xs), y1=max(ys))


def normalize_response(payload: object) -> tuple[str, list[OCRWord]]:
    try:
        response = _BatchResponse.model_validate(payload).responses[0]
    except ValidationError as error:
        raise RecognitionResponseError(
            "Google Vision returned an invalid recognition response."
        ) from error
    if response.error and (response.error.code or response.error.message):
        raise RecognitionProviderError("Google Vision could not recognize the image.")
    annotation = response.fullTextAnnotation
    if annotation is None or not annotation.text.strip():
        raise RecognitionResponseError("Google Vision returned no document text.")
    words = [
        OCRWord(
            text="".join(symbol.text for symbol in word.symbols),
            confidence=word.confidence,
            bbox=_bounding_box(word.boundingBox),
        )
        for page in annotation.pages
        for block in page.blocks
        for paragraph in block.paragraphs
        for word in paragraph.words
    ]
    return annotation.text, words


def minimum_word_confidence(words: list[OCRWord]) -> float | None:
    return min(
        (word.confidence for word in words if word.confidence is not None),
        default=None,
    )
