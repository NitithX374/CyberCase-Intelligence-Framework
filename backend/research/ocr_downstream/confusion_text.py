import html
import re
import unicodedata
from typing import Any


FIGURE_BLOCK = re.compile(r"<figure\b[^>]*>.*?</figure\s*>", re.IGNORECASE | re.DOTALL)
HTML_TAG = re.compile(r"<[^>]+>")
HEADING_MARKER = re.compile(r"(?m)^\s{0,3}#{1,6}\s*")
BULLET_MARKER = re.compile(r"(?m)^\s*[-*+]\s+")


def get_normalization_metadata() -> dict[str, Any]:
    return {
        "unicode": "NFC",
        "line_endings": "LF",
        "figure_blocks": "remove_<figure>_blocks",
        "html_tags": "remove_html_tags",
        "html_entities": "html.unescape_decoded",
        "markdown": "remove_heading_bullet_code_and_emphasis_markers",
        "whitespace": "collapse_runs_to_single_space_and_strip",
        "unit": "Unicode_code_point",
        "thai_spelling_policy": "preserve_raw_thai_no_silent_correction",
    }


def normalize_for_alignment(value: str) -> str:
    text = value.replace("\r\n", "\n").replace("\r", "\n")
    text = FIGURE_BLOCK.sub(" ", text)
    text = HTML_TAG.sub(" ", text)
    text = html.unescape(text)
    text = HEADING_MARKER.sub("", text)
    text = BULLET_MARKER.sub("", text)
    text = text.replace("```", "").replace("`", "")
    text = text.replace("**", "").replace("__", "")
    text = unicodedata.normalize("NFC", text)
    return re.sub(r"\s+", " ", text).strip()

