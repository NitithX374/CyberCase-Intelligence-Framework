from dataclasses import dataclass
from enum import StrEnum
from io import BytesIO
from zipfile import BadZipFile, ZipFile

from app.services.document_ingestion.errors import UnsupportedDocumentError


class DocumentKind(StrEnum):
    PDF = "pdf"
    DOCX = "docx"
    PNG = "png"
    JPEG = "jpeg"


@dataclass(frozen=True)
class DetectedDocument:
    kind: DocumentKind
    media_type: str


def _is_docx(content: bytes) -> bool:
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
    if content.startswith(b"PK") and _is_docx(content):
        return DetectedDocument(
            DocumentKind.DOCX,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    raise UnsupportedDocumentError("Only PDF, DOCX, PNG, and JPEG files are supported.")
