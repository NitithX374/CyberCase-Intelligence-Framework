import warnings
from dataclasses import dataclass
from enum import StrEnum
from io import BytesIO
from zipfile import BadZipFile, ZipFile

import pypdfium2 as pdfium
from PIL import Image

from app.services.document_ingestion.contracts import InvalidDocumentError, UnsupportedDocumentError


class DocumentKind(StrEnum):
    PDF = "pdf"
    DOCX = "docx"
    PNG = "png"
    JPEG = "jpeg"


@dataclass(frozen=True)
class DetectedDocument:
    kind: DocumentKind
    media_type: str


def is_docx(content: bytes) -> bool:
    try:
        with ZipFile(BytesIO(content)) as archive:
            return "word/document.xml" in archive.namelist()
    except BadZipFile:
        return False


def detect_document(content: bytes) -> DetectedDocument:
    if content.startswith(b"%PDF-"):
        return DetectedDocument(DocumentKind.PDF, "application/pdf")
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return DetectedDocument(DocumentKind.PNG, "image/png")
    if content.startswith(b"\xff\xd8\xff"):
        return DetectedDocument(DocumentKind.JPEG, "image/jpeg")
    if content.startswith(b"PK") and is_docx(content):
        return DetectedDocument(
            DocumentKind.DOCX,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    raise UnsupportedDocumentError("Only PDF, DOCX, PNG, and JPEG files are supported.")


def encode_png(image: Image.Image) -> bytes:
    output = BytesIO()
    image.convert("RGB").save(output, format="PNG")
    return output.getvalue()


def render_pdf_page(content: bytes, page_number: int, longest_edge: int) -> bytes:
    document = None
    page = None
    try:
        document = pdfium.PdfDocument(content)
        page = document[page_number - 1]
        width, height = page.get_size()
        scale = longest_edge / max(width, height)
        image = page.render(scale=scale).to_pil()
        return encode_png(image)
    except Exception as error:
        raise InvalidDocumentError(f"PDF page {page_number} could not be rendered.") from error
    finally:
        if page is not None:
            page.close()
        if document is not None:
            document.close()


def normalize_image(content: bytes, longest_edge: int, max_pixels: int) -> bytes:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            image = Image.open(BytesIO(content))
            if image.width * image.height > max_pixels:
                raise InvalidDocumentError(
                    f"The image exceeds the {max_pixels:,}-pixel ingestion limit."
                )
            image.load()
        image.thumbnail((longest_edge, longest_edge), Image.Resampling.LANCZOS)
        return encode_png(image)
    except InvalidDocumentError:
        raise
    except Exception as error:
        raise InvalidDocumentError("The image file could not be decoded.") from error
