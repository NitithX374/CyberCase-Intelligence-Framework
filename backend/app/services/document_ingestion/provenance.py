import hashlib
from collections.abc import Mapping
from copy import deepcopy


def build_document_id(content: bytes) -> str:
    digest = hashlib.sha256(content).hexdigest()[:12].upper()
    return f"DOC-{digest}"


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
        page_text = raw_page.get("text") if "text" in raw_page else raw_page.get("merged_text")
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
        bound_pages[page_index] = page
    if bound_pages:
        output["pages"] = [
            bound_pages.get(page_index, deepcopy(raw_page))
            for page_index, raw_page in enumerate(raw_pages)
        ]
    return output


__all__ = [
    "bind_exact_page_spans",
    "build_document_id",
]
