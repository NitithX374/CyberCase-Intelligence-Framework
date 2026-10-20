"""Modular Layout-Aware Thai OCR Engine.

Architecture:
  [1] Document Layout Analysis & Reading Order: PP-DocLayoutV3
  [2] Textual Region Filtering & Reading Order Sorting
  [3] Intra-Region Text-Line Detection: PP-OCRv5_server_det
  [4] Optical Thai Recognition: th_PP-OCRv5_mobile_rec (no orientation flip)
  [5] Deterministic Reconstruction: Line -> Region -> Page plain-text projection
"""

from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import Any

from PIL import Image
import numpy as np

try:
    import torch  # noqa: F401
except ImportError:
    pass

import paddlex
from paddleocr import PaddleOCR

logger = logging.getLogger(__name__)

DEFAULT_TEXTUAL_LABELS = {
    "paragraph_title",
    "text",
    "list",
    "header",
    "footer",
    "caption",
    "reference",
    "title",
}

DEFAULT_NON_TEXTUAL_LABELS = {
    "table",
    "formula",
    "chart",
    "figure",
    "image",
    "stamp",
}


class ModularLayoutThaiOCR:
    """Modular layout-aware OCR engine for Thai documents."""

    def __init__(
        self,
        device: str = "cpu",
        textual_labels: set[str] | None = None,
        non_textual_labels: set[str] | None = None,
    ) -> None:
        self.device = device
        self.textual_labels = set(textual_labels or DEFAULT_TEXTUAL_LABELS)
        self.non_textual_labels = set(non_textual_labels or DEFAULT_NON_TEXTUAL_LABELS)

        logger.info("Loading PP-DocLayoutV3 on device=%s...", device)
        self.layout_model = paddlex.create_model("PP-DocLayoutV3", device=device)

        logger.info("Loading PP-OCRv5_server_det and th_PP-OCRv5_mobile_rec on device=%s...", device)
        self._paddle_ocr = PaddleOCR(
            lang="th",
            device=device,
            enable_mkldnn=False,
            use_doc_unwarping=False,
            use_doc_orientation_classify=False,
            use_textline_orientation=False,
        )
        self.det_model = self._paddle_ocr.paddlex_pipeline._pipeline.text_det_model
        self.rec_model = self._paddle_ocr.paddlex_pipeline._pipeline.text_rec_model

    @staticmethod
    def _prepare_image(image_input: Image.Image | np.ndarray | str | Path | bytes) -> tuple[Image.Image, np.ndarray]:
        if isinstance(image_input, (str, Path)):
            pil_img = Image.open(image_input).convert("RGB")
        elif isinstance(image_input, bytes):
            pil_img = Image.open(io.BytesIO(image_input)).convert("RGB")
        elif isinstance(image_input, Image.Image):
            pil_img = image_input.convert("RGB")
        elif isinstance(image_input, np.ndarray):
            pil_img = Image.fromarray(image_input).convert("RGB")
        else:
            raise TypeError(f"Unsupported image input type: {type(image_input)}")
        return pil_img, np.array(pil_img)

    @staticmethod
    def _region_order_key(box: dict[str, Any]) -> tuple[int, Any, int, int]:
        order_val = box.get("order")
        coord = box.get("coordinate", [0, 0, 0, 0])
        y_top = int(coord[1]) if len(coord) > 1 else 0
        x_left = int(coord[0]) if len(coord) > 0 else 0
        if order_val is not None:
            return (0, order_val, y_top, x_left)
        return (1, 0, y_top, x_left)

    def predict(
        self,
        image_input: Image.Image | np.ndarray | str | Path | bytes,
        sample_id: str = "",
    ) -> dict[str, Any]:
        """Performs layout analysis, line detection, recognition, and hierarchical reconstruction."""
        pil_img, img_np = self._prepare_image(image_input)
        img_h, img_w = img_np.shape[:2]

        # 1. Layout analysis
        layout_res = list(self.layout_model.predict(img_np))[0]
        raw_boxes = layout_res.get("boxes", [])

        # 2. Reading-order determination & region filtering
        sorted_boxes = sorted(raw_boxes, key=self._region_order_key)

        regions_output = []
        text_lines_all = []
        all_rec_scores = []

        for reg_idx, b in enumerate(sorted_boxes, start=1):
            label = str(b.get("label", "text"))
            score = float(b.get("score", 0.0))
            order = b.get("order")
            coord = [int(round(v)) for v in b.get("coordinate", [0, 0, 0, 0])]
            rx1, ry1, rx2, ry2 = coord[0], coord[1], coord[2], coord[3]
            rx1 = max(0, min(rx1, img_w))
            ry1 = max(0, min(ry1, img_h))
            rx2 = max(0, min(rx2, img_w))
            ry2 = max(0, min(ry2, img_h))

            is_textual = label in self.textual_labels

            region_dict: dict[str, Any] = {
                "region_id": reg_idx,
                "layout_type": label,
                "score": score,
                "reading_order": order,
                "bbox": [rx1, ry1, rx2, ry2],
                "is_textual": is_textual,
                "lines": [],
            }

            if not is_textual or rx2 <= rx1 or ry2 <= ry1:
                regions_output.append(region_dict)
                continue

            # Crop region
            reg_crop = img_np[ry1:ry2, rx1:rx2]
            det_res = list(self.det_model.predict(reg_crop))[0]
            dt_polys = det_res.get("dt_polys", [])

            # Line bounding boxes within region
            line_meta = []
            for poly in dt_polys:
                arr = np.array(poly)
                lx1 = int(np.floor(arr[:, 0].min()))
                ly1 = int(np.floor(arr[:, 1].min()))
                lx2 = int(np.ceil(arr[:, 0].max()))
                ly2 = int(np.ceil(arr[:, 1].max()))
                lx1, ly1 = max(0, lx1), max(0, ly1)
                lx2 = min(reg_crop.shape[1], lx2)
                ly2 = min(reg_crop.shape[0], ly2)
                if lx2 > lx1 and ly2 > ly1:
                    line_meta.append({
                        "crop": reg_crop[ly1:ly2, lx1:lx2],
                        "lx1": lx1,
                        "ly1": ly1,
                        "lx2": lx2,
                        "ly2": ly2,
                        "gx1": rx1 + lx1,
                        "gy1": ry1 + ly1,
                        "gx2": rx1 + lx2,
                        "gy2": ry1 + ly2,
                    })

            # Sort lines within region: top-to-bottom, left-to-right
            line_meta.sort(key=lambda x: (x["ly1"], x["lx1"]))

            # Recognize lines
            region_lines = []
            for l_idx, lm in enumerate(line_meta, start=1):
                rec_res = list(self.rec_model.predict(lm["crop"]))[0]
                rec_text = str(rec_res.get("rec_text", "")).strip()
                rec_score = float(rec_res.get("rec_score", 0.0))

                line_info = {
                    "line_id": l_idx,
                    "text": rec_text,
                    "confidence": rec_score,
                    "local_bbox": [lm["lx1"], lm["ly1"], lm["lx2"], lm["ly2"]],
                    "global_bbox": [lm["gx1"], lm["gy1"], lm["gx2"], lm["gy2"]],
                }
                region_dict["lines"].append(line_info)

                if rec_text:
                    region_lines.append(rec_text)
                    text_lines_all.append(line_info)
                    all_rec_scores.append(rec_score)

            if region_lines:
                region_dict["region_text"] = " ".join(region_lines)
            else:
                region_dict["region_text"] = ""

            regions_output.append(region_dict)

        # 5. Deterministic plain-text reconstruction
        plain_paragraphs = []
        for r in regions_output:
            if r.get("is_textual") and r.get("region_text"):
                plain_paragraphs.append(r["region_text"])

        plain_text = "\n".join(plain_paragraphs)
        mean_conf = float(np.mean(all_rec_scores)) if all_rec_scores else 0.0

        return {
            "sample_id": sample_id,
            "regions": regions_output,
            "plain_text": plain_text,
            "metadata": {
                "total_regions": len(regions_output),
                "textual_regions": sum(1 for r in regions_output if r.get("is_textual")),
                "total_lines": len(text_lines_all),
                "mean_recognition_confidence": mean_conf,
                "image_size": [img_w, img_h],
            },
        }
