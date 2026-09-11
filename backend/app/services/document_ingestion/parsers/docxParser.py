from io import BytesIO

from docx import Document
from docx.document import Document as DocumentObject
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P

from app.services.document_ingestion.contracts import (
    DocumentPage,
    RoutingSummary,
    SourceType,
)
from app.services.document_ingestion.errors import InvalidDocumentError
from app.services.document_ingestion.provenance import (
    build_blocks,
    build_native_regions,
)


def _iter_document_blocks(document: DocumentObject):
    for child in document.element.body.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, document)
        elif isinstance(child, CT_Tbl):
            yield Table(child, document)


def _table_text(table: Table) -> str:
    rows = []
    for row in table.rows:
        cells = [" ".join(cell.text.split()) for cell in row.cells]
        if any(cells):
            rows.append(" | ".join(cells))
    return "\n".join(rows)


def parse_docx(
    content: bytes, document_id: str
) -> tuple[list[DocumentPage], list[str]]:
    try:
        document = Document(BytesIO(content))
    except Exception as error:
        raise InvalidDocumentError("The DOCX file could not be parsed.") from error

    texts = []
    for item in _iter_document_blocks(document):
        text = item.text if isinstance(item, Paragraph) else _table_text(item)
        normalized = text.strip()
        if normalized:
            texts.append(normalized)

    blocks = build_blocks(document_id, 1, texts, SourceType.NATIVE)
    regions = build_native_regions(document_id, 1, texts)
    full_text = "\n\n".join(block.text for block in blocks)
    warnings = [
        "DOCX does not expose stable rendered page boundaries; page 1 is a logical document page."
    ]
    return [
        DocumentPage(
            page_number=1,
            regions=regions,
            merged_text=full_text,
            routing_summary=RoutingSummary(native=len(regions)),
            blocks=blocks,
            full_text=full_text,
        )
    ], warnings
