import hashlib

from app.services.document_ingestion.contracts import (
    ContentRole,
    DocumentBlock,
    DocumentRegion,
    RecognitionMethod,
    RegionType,
    SourceType,
    VerificationStatus,
)


def build_document_id(content: bytes) -> str:
    digest = hashlib.sha256(content).hexdigest()[:12].upper()
    return f"DOC-{digest}"


def build_block_id(document_id: str, page_number: int, block_number: int) -> str:
    return f"{document_id}-P{page_number:03d}-B{block_number:03d}"


def build_region_id(document_id: str, page_number: int, region_number: int) -> str:
    return f"{document_id}-P{page_number:03d}-R{region_number:03d}"


def build_blocks(
    document_id: str,
    page_number: int,
    texts: list[str],
    source_type: SourceType,
) -> list[DocumentBlock]:
    normalized_texts = [text.strip() for text in texts if text.strip()]
    return [
        DocumentBlock(
            block_id=build_block_id(document_id, page_number, index),
            text=text,
            source_type=source_type,
        )
        for index, text in enumerate(normalized_texts, start=1)
    ]


def build_native_regions(
    document_id: str,
    page_number: int,
    texts: list[str],
) -> list[DocumentRegion]:
    normalized_texts = [text.strip() for text in texts if text.strip()]
    return [
        DocumentRegion(
            region_id=build_region_id(document_id, page_number, index),
            page_number=page_number,
            region_type=RegionType.PRINTED_TEXT,
            recognition_method=RecognitionMethod.NATIVE,
            recognizer="native",
            text=text,
            verification_status=VerificationStatus.NATIVE,
            content_role=ContentRole.TRANSCRIBED_TEXT,
        )
        for index, text in enumerate(normalized_texts, start=1)
    ]
