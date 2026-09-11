import hashlib
from collections.abc import Mapping
from copy import deepcopy

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


def bind_exact_page_spans(
    provenance: Mapping[str, object],
    exact_text: str,
) -> dict[str, object]:
    output = deepcopy(dict(provenance))
    raw_pages = output.get("pages")
    if not isinstance(raw_pages, list):
        return output
    locations: list[tuple[int, dict[str, object], int, int]] = []
    cursor = 0
    for page_index, raw_page in enumerate(raw_pages):
        if not isinstance(raw_page, Mapping):
            break
        page_number = raw_page.get("page_number")
        page_text = raw_page.get("merged_text")
        if type(page_number) is not int or page_number < 1 or not isinstance(page_text, str):
            break
        if not page_text:
            continue
        start = exact_text.find(page_text, cursor)
        if start < 0:
            break
        end = start + len(page_text)
        locations.append((page_index, dict(raw_page), start, end))
        cursor = end
    if not locations:
        return output
    bound_pages: dict[int, dict[str, object]] = {}
    for index, (page_index, page, start, page_end) in enumerate(locations):
        end = locations[index + 1][2] if index + 1 < len(locations) else page_end
        if end <= start:
            break
        page["start_offset"] = start
        page["end_offset"] = end
        page["text_sha256"] = hashlib.sha256(exact_text[start:end].encode("utf-8")).hexdigest()
        bound_pages[page_index] = page
    if bound_pages:
        output["pages"] = [
            bound_pages.get(page_index, deepcopy(raw_page))
            for page_index, raw_page in enumerate(raw_pages)
        ]
    return output


def order_regions(regions: list[object]) -> list[object]:
    return sorted(
        regions,
        key=lambda region: (
            getattr(region, "bbox", None).y0 if getattr(region, "bbox", None) else float("inf"),
            getattr(region, "bbox", None).x0 if getattr(region, "bbox", None) else float("inf"),
            getattr(region, "region_id", ""),
        ),
    )


def merge_region_text(regions: list[object]) -> str:
    return "\n".join(region.text for region in order_regions(regions) if getattr(region, "text", None))


__all__ = [
    "bind_exact_page_spans",
    "build_block_id",
    "build_region_id",
    "merge_region_text",
    "order_regions",
]
