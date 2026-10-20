"""Tesseract OCR Thai recognition adapter.

Provides a minimal, isolated adapter for running Tesseract OCR with Thai language support,
reconstructing plain recognized text without requiring external python wrapper packages.
"""

from __future__ import annotations

import logging
import subprocess
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_TESSERACT_EXE = Path(r"C:\Program Files\Autopsy-4.22.1\autopsy\Tesseract-OCR\tesseract.exe")
DEFAULT_TESSDATA_DIR = Path(__file__).resolve().parent / "tessdata"


class TesseractThaiAdapter:
    """Adapter for running Tesseract on Thai text images and returning plain text."""

    def __init__(
        self,
        tesseract_cmd: Path | str | None = None,
        tessdata_dir: Path | str | None = None,
        lang: str = "tha+eng",
    ) -> None:
        self.tesseract_cmd = Path(tesseract_cmd or DEFAULT_TESSERACT_EXE)
        self.tessdata_dir = Path(tessdata_dir or DEFAULT_TESSDATA_DIR).resolve()
        self.lang = lang

        if not self.tesseract_cmd.exists():
            raise FileNotFoundError(f"Tesseract executable not found at {self.tesseract_cmd}")
        if not self.tessdata_dir.exists():
            raise FileNotFoundError(f"Tessdata directory not found at {self.tessdata_dir}")

    def predict_image(
        self,
        image_path: Path | str,
        sample_id: str = "",
    ) -> dict[str, Any]:
        """Runs Tesseract on the given image and returns plain recognized text."""
        img_path = Path(image_path).resolve()
        if not img_path.exists():
            raise FileNotFoundError(f"Image not found at {img_path}")

        cmd = [
            str(self.tesseract_cmd),
            str(img_path),
            "stdout",
            "--tessdata-dir",
            str(self.tessdata_dir),
            "-l",
            self.lang,
        ]

        t0 = time.time()
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        elapsed = time.time() - t0

        if res.returncode != 0:
            logger.error("Tesseract error on %s: %s", sample_id, res.stderr)
            raw_text = ""
        else:
            # Strip trailing form-feed \x0c
            raw_text = res.stdout.replace("\x0c", "").strip()

        return {
            "sample_id": sample_id,
            "image_path": str(img_path),
            "plain_text": raw_text,
            "ocr_engine": "tesseract",
            "elapsed_seconds": elapsed,
        }
