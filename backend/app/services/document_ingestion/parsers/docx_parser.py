from io import BytesIO

from docx import Document
from docx.document import Document as DocumentObject
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table
from docx.text.paragraph import Paragraph

from app.services.document_ingestion.contracts import DocumentPage
from app.services.document_ingestion.errors import InvalidDocumentError


def iter_document_blocks(document: DocumentObject):
    for child in document.element.body.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, document)
        elif isinstance(child, CT_Tbl):
            yield Table(child, document)


def table_text(table: Table) -> str:
    rows = []
    for row in table.rows:
        cells = [" ".join(cell.text.split()) for cell in row.cells]
        if any(cells):
            rows.append(" | ".join(cells))
    return "\n".join(rows)


def parse_docx(content: bytes, document_id: str) -> tuple[list[DocumentPage], list[str]]:
    try:
        document = Document(BytesIO(content))
    except Exception as error:
        raise InvalidDocumentError("The DOCX file could not be parsed.") from error

    texts = []
    for item in iter_document_blocks(document):
        text = item.text if isinstance(item, Paragraph) else table_text(item)
        normalized = text.strip()
        if normalized:
            texts.append(normalized)

    full_text = "\n\n".join(texts)
    warnings = [
        "DOCX does not expose stable rendered page boundaries; page 1 is a logical document page."
    ]
    return [
        DocumentPage(
            page_number=1,
            text=full_text,
            text_method="native",
            verification_status="native",
        )
    ], warnings
