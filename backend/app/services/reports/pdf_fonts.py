from __future__ import annotations

import os
from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def register_report_fonts() -> tuple[str, str]:
    regular_path = find_report_font(
        "CYBERCASE_PDF_FONT",
        (
            "/usr/share/fonts/truetype/tlwg/Garuda.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "C:/Windows/Fonts/tahoma.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ),
    )
    bold_path = find_report_font(
        "CYBERCASE_PDF_BOLD_FONT",
        (
            "/usr/share/fonts/truetype/tlwg/Garuda-Bold.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansThai-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "C:/Windows/Fonts/tahomabd.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
        ),
    )
    if regular_path is None or bold_path is None:
        return "Helvetica", "Helvetica-Bold"

    try:
        pdfmetrics.registerFont(TTFont("CyberCaseSans", regular_path))
        pdfmetrics.registerFont(TTFont("CyberCaseSansBold", bold_path))
        return "CyberCaseSans", "CyberCaseSansBold"
    except Exception:
        return "Helvetica", "Helvetica-Bold"


def find_report_font(
    environment_name: str,
    candidates: tuple[str, ...],
) -> str | None:
    configured = Path(os.environ.get(environment_name, ""))
    if configured.is_file():
        return str(configured)
    for candidate in candidates:
        path = Path(candidate)
        if path.is_file():
            return str(path)
    return None
