import warnings
from io import BytesIO

import pypdfium2 as pdfium
from PIL import Image

from app.services.document_ingestion.contracts import BoundingBox
from app.services.document_ingestion.errors import InvalidDocumentError


def _encode_png(image: Image.Image) -> bytes:
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
        return _encode_png(image)
    except Exception as error:
        raise InvalidDocumentError(
            f"PDF page {page_number} could not be rendered."
        ) from error
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
        return _encode_png(image)
    except InvalidDocumentError:
        raise
    except Exception as error:
        raise InvalidDocumentError("The image file could not be decoded.") from error


def image_dimensions(content: bytes) -> tuple[int, int]:
    try:
        with Image.open(BytesIO(content)) as image:
            return image.width, image.height
    except Exception as error:
        raise InvalidDocumentError("The rendered page could not be decoded.") from error


def crop_image_region(content: bytes, bbox: BoundingBox) -> bytes:
    try:
        with Image.open(BytesIO(content)) as image:
            left = max(0, min(image.width - 1, int(bbox.x0)))
            top = max(0, min(image.height - 1, int(bbox.y0)))
            right = max(left + 1, min(image.width, int(bbox.x1 + 0.999)))
            bottom = max(top + 1, min(image.height, int(bbox.y1 + 0.999)))
            return _encode_png(image.crop((left, top, right, bottom)))
    except Exception as error:
        raise InvalidDocumentError("A document region could not be cropped.") from error
