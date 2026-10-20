"""Builds the Observed OCR Error Catalogue from paired GT and Typhoon OCR predictions.

Pipeline:
  Paired GT + Typhoon OCR
      ↓
  Levenshtein character-level alignment
      ↓
  Observed OCR Error Catalogue (observed_ocr_error_catalogue.json)
      ↓
  Recognition-error filtering & rejection logging
      ↓
  Filtered Catalogue (observed_ocr_error_catalogue_filtered.json)
  Rejections Log (observed_ocr_error_rejections.json)
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import Levenshtein

ROOT = Path(__file__).resolve().parent

HTML_TAG_OR_ENTITY_RE = re.compile(r"(&[a-zA-Z]+;|&#\d+;|</?[a-zA-Z0-9_-]+>)")
MARKDOWN_CHARS = set("#*_~`|>")
QUOTE_PAIRS = {
    ("\u201c", '"'),
    ('"', "\u201d"),
    ("\u2018", "'"),
    ("'", "\u2019"),
    ("\u201c", "\u201d"),
    ("\u2018", "\u2019"),
    ('"', "\u201c"),
    ('"', "\u201d"),
}
DASH_PAIRS = {
    ("-", "\u2013"),
    ("-", "\u2014"),
    ("\u2013", "-"),
    ("\u2014", "-"),
    ("\u2013", "\u2014"),
}


def is_thai(c: str) -> bool:
    """Checks if a character is within Thai Unicode block (U+0E00 to U+0E7F)."""
    return len(c) == 1 and "\u0e00" <= c <= "\u0e7f"


def is_arabic_digit(c: str) -> bool:
    """Checks if a character is an ASCII Arabic digit (0-9)."""
    return len(c) == 1 and "0" <= c <= "9"


def is_thai_digit(c: str) -> bool:
    """Checks if a character is a Thai digit (U+0E50 to U+0E59)."""
    return len(c) == 1 and "\u0e50" <= c <= "\u0e59"


def classify_error(
    operation: str,
    source: str,
    target: str,
    reference_context: str,
    prediction_context: str,
) -> tuple[bool, str]:
    """Classifies an edit operation as a valid recognition error or a rejected artifact.

    Returns:
      (is_valid: bool, reason_or_category: str)
      If is_valid is False, reason is one of:
        - 'non_atomic'
        - 'whitespace_only'
        - 'html_artifact'
        - 'markdown_artifact'
        - 'formatting_convention'
        - 'invalid_alignment'
        - 'ambiguous'
    """
    if len(source) > 1 or len(target) > 1:
        return False, "non_atomic"

    # Whitespace only differences
    if (source and source.isspace()) or (target and target.isspace()):
        return False, "whitespace_only"

    # HTML entity or tag artifacts
    if (source in "<>&;/=" or target in "<>&;/=") and (
        HTML_TAG_OR_ENTITY_RE.search(reference_context)
        or HTML_TAG_OR_ENTITY_RE.search(prediction_context)
        or "&gt;" in prediction_context
        or "&lt;" in prediction_context
        or "&amp;" in prediction_context
        or "<table>" in prediction_context
        or "<figure>" in prediction_context
    ):
        return False, "html_artifact"

    # Markdown artifacts
    if operation == "substitution":
        if source in MARKDOWN_CHARS or target in MARKDOWN_CHARS:
            return False, "markdown_artifact"
    elif operation == "insertion" and target in MARKDOWN_CHARS:
        return False, "markdown_artifact"
    elif operation == "deletion" and source in MARKDOWN_CHARS:
        return False, "markdown_artifact"

    # Formatting conventions (quote glyphs, dashes, bullets)
    if operation == "substitution":
        if (source, target) in QUOTE_PAIRS or (target, source) in QUOTE_PAIRS:
            return False, "formatting_convention"
        if (source, target) in DASH_PAIRS or (target, source) in DASH_PAIRS:
            return False, "formatting_convention"
        if source in "•·" or target in "•·":
            return False, "formatting_convention"

    # Evaluate substitutions
    if operation == "substitution":
        # Thai consonant / vowel / tone substitutions
        if is_thai(source) and is_thai(target):
            return True, "valid_recognition"
        # Arabic digit substitutions
        if is_arabic_digit(source) and is_arabic_digit(target):
            return True, "valid_recognition"
        # Thai digit substitutions
        if is_thai_digit(source) and is_thai_digit(target):
            return True, "valid_recognition"
        # Arabic digit <-> Thai digit substitutions
        if (is_arabic_digit(source) and is_thai_digit(target)) or (
            is_thai_digit(source) and is_arabic_digit(target)
        ):
            return True, "valid_recognition"
        # Confusable digit/letter pairs (e.g. 0 <-> O, 1 <-> l, 5 <-> S, 0 <-> o)
        if (source in "0Ol" and target in "0Ol") or (source in "5S" and target in "5S"):
            return True, "valid_recognition"
        # Cross-script Thai <-> Latin misalignment
        if (is_thai(source) and not is_thai(target)) or (not is_thai(source) and is_thai(target)):
            return False, "invalid_alignment"
        # Standard punctuation substitutions
        if not source.isalnum() and not target.isalnum():
            punct = set(".,:;!?()-[]/\"'")
            if source in punct and target in punct:
                return True, "valid_recognition"
            return False, "formatting_convention"
        return False, "ambiguous"

    # Evaluate deletions
    if operation == "deletion":
        if is_thai(source) or is_arabic_digit(source) or is_thai_digit(source):
            return True, "valid_recognition"
        return False, "invalid_alignment"

    # Evaluate insertions
    if operation == "insertion":
        if is_thai(target) or is_arabic_digit(target) or is_thai_digit(target):
            return True, "valid_recognition"
        return False, "invalid_alignment"

    return False, "ambiguous"


def extract_atomic_operations(
    reference: str,
    prediction: str,
    sample_meta: dict[str, Any],
    context_window: int = 15,
) -> list[dict[str, Any]]:
    """Extracts atomic edit operations with local context and sample provenance."""
    ops = Levenshtein.editops(reference, prediction)
    results = []

    for op_type, r_i, p_i in ops:
        if op_type == "replace":
            operation = "substitution"
            source = reference[r_i]
            target = prediction[p_i]
            r_ctx = reference[max(0, r_i - context_window) : min(len(reference), r_i + context_window + 1)]
            p_ctx = prediction[max(0, p_i - context_window) : min(len(prediction), p_i + context_window + 1)]
        elif op_type == "delete":
            operation = "deletion"
            source = reference[r_i]
            target = ""
            r_ctx = reference[max(0, r_i - context_window) : min(len(reference), r_i + context_window + 1)]
            p_ctx = prediction[max(0, p_i - context_window) : min(len(prediction), p_i + context_window)]
        elif op_type == "insert":
            operation = "insertion"
            source = ""
            target = prediction[p_i]
            r_ctx = reference[max(0, r_i - context_window) : min(len(reference), r_i + context_window)]
            p_ctx = prediction[max(0, p_i - context_window) : min(len(prediction), p_i + context_window + 1)]
        else:
            continue

        results.append(
            {
                "operation": operation,
                "source": source,
                "target": target,
                "dataset": sample_meta.get("dataset", "unknown"),
                "sample_id": sample_meta.get("sample_id", "unknown"),
                "category": sample_meta.get("category") or "unknown",
                "reference_context": r_ctx,
                "prediction_context": p_ctx,
            }
        )

    return results


def build_catalogues(
    prediction_paths: list[Path],
    output_dir: Path,
    max_provenance_examples: int = 10,
) -> tuple[Path, Path, Path]:
    """Processes prediction files to build observed catalogue, filtered catalogue, and rejections log."""
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_edits: list[dict[str, Any]] = []

    for path in prediction_paths:
        if not path.exists():
            continue
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                ref = rec.get("reference_normalized", "")
                pred = rec.get("prediction_normalized", "")
                sample_meta = {
                    "dataset": rec.get("dataset", "unknown"),
                    "sample_id": rec.get("sample_id", "unknown"),
                    "category": rec.get("category") or "unknown",
                }
                edits = extract_atomic_operations(ref, pred, sample_meta)
                raw_edits.extend(edits)

    # Aggregate complete observed catalogue
    grouped_observed: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for edit in raw_edits:
        key = (edit["operation"], edit["source"], edit["target"])
        grouped_observed[key].append(edit)

    catalogue_entries = []
    for (op, src, tgt), instances in grouped_observed.items():
        prov_list = []
        seen_samples = set()
        for inst in instances:
            s_id = inst["sample_id"]
            if s_id not in seen_samples:
                seen_samples.add(s_id)
                prov_list.append(
                    {
                        "dataset": inst["dataset"],
                        "sample_id": inst["sample_id"],
                        "category": inst["category"],
                        "reference_context": inst["reference_context"],
                        "prediction_context": inst["prediction_context"],
                    }
                )
                if len(prov_list) >= max_provenance_examples:
                    break

        catalogue_entries.append(
            {
                "operation": op,
                "source": src,
                "target": tgt,
                "observed_count": len(instances),
                "provenance": prov_list,
            }
        )

    # Sort catalogue by observed_count descending
    catalogue_entries.sort(key=lambda x: -x["observed_count"])
    catalogue_path = output_dir / "observed_ocr_error_catalogue.json"
    with open(catalogue_path, "w", encoding="utf-8") as f:
        json.dump(catalogue_entries, f, ensure_ascii=False, indent=2)

    # Filter into filtered catalogue and rejections
    filtered_entries = []
    rejected_entries = []

    for entry in catalogue_entries:
        op = entry["operation"]
        src = entry["source"]
        tgt = entry["target"]
        count = entry["observed_count"]
        prov = entry["provenance"]

        ref_ctx = prov[0]["reference_context"] if prov else ""
        pred_ctx = prov[0]["prediction_context"] if prov else ""

        is_valid, reason = classify_error(op, src, tgt, ref_ctx, pred_ctx)
        if is_valid:
            filtered_entries.append(
                {
                    "operation": op,
                    "source": src,
                    "target": tgt,
                    "observed_count": count,
                    "provenance": prov,
                }
            )
        else:
            rejected_entries.append(
                {
                    "operation": op,
                    "source": src,
                    "target": tgt,
                    "rejection_reason": reason,
                    "observed_count": count,
                    "provenance": prov,
                }
            )

    filtered_entries.sort(key=lambda x: -x["observed_count"])
    rejected_entries.sort(key=lambda x: -x["observed_count"])

    filtered_path = output_dir / "observed_ocr_error_catalogue_filtered.json"
    with open(filtered_path, "w", encoding="utf-8") as f:
        json.dump(filtered_entries, f, ensure_ascii=False, indent=2)

    rejections_path = output_dir / "observed_ocr_error_rejections.json"
    with open(rejections_path, "w", encoding="utf-8") as f:
        json.dump(rejected_entries, f, ensure_ascii=False, indent=2)

    return catalogue_path, filtered_path, rejections_path


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Build Observed OCR Error Catalogue")
    parser.add_argument(
        "--dataset",
        choices=["thai-ocr-evaluation", "all", "ThaiOCRBench"],
        default="thai-ocr-evaluation",
        help="Main dataset to build catalogue from (default: thai-ocr-evaluation)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT,
        help="Output directory for generated catalogues (default: evaluation/ocr_downstream)",
    )
    args = parser.parse_args()

    if args.dataset == "thai-ocr-evaluation":
        pred_files = [
            ROOT / "results" / "character_confusion_thai_ocr_evaluation_all" / "predictions.jsonl",
        ]
    elif args.dataset == "ThaiOCRBench":
        pred_files = [
            ROOT / "results" / "character_confusion_document_plaintext" / "predictions.jsonl",
        ]
    else:
        pred_files = [
            ROOT / "results" / "character_confusion_thai_ocr_evaluation_all" / "predictions.jsonl",
            ROOT / "results" / "character_confusion_document_plaintext" / "predictions.jsonl",
        ]

    print(f"Building Observed OCR Error Catalogue using main dataset: {args.dataset}")
    for p in pred_files:
        print(f"  Source predictions: {p}")

    cat_path, filt_path, rej_path = build_catalogues(pred_files, args.output_dir)
    print(f"\nCompleted catalogue generation:")
    print(f"  Master Catalogue:   {cat_path}")
    print(f"  Filtered Catalogue: {filt_path}")
    print(f"  Rejections Log:     {rej_path}")
