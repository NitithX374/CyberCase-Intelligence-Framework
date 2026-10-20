"""Recompute every reported number without the inherited modules.

The bank was first produced through confusion_alignment.py and
build_error_catalogue.py, which are not code we vouch for. Nothing here
imports from the parent directory: normalisation, alignment and counting are
all written out, so the numbers either reproduce or the difference is real and
the inherited version is what has to be explained.

Reads predictions/*.jsonl and writes verified_bank.json.
"""

from __future__ import annotations

import html
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

import Levenshtein

HERE = Path(__file__).resolve().parent
PREDICTIONS = HERE / "predictions"
ENGINES = ("typhoon", "paddle", "tesseract")

FIGURE = re.compile(r"<figure\b[^>]*>.*?</figure\s*>", re.IGNORECASE | re.DOTALL)
TAG = re.compile(r"<[^>]+>")
HEADING = re.compile(r"(?m)^\s{0,3}#{1,6}\s*")
BULLET = re.compile(r"(?m)^\s*[-*+]\s+")


def normalize(value: str) -> str:
    """Markup out, NFC, one space between words.

    OCR output is markdown-ish and the reference is not, so comparing them raw
    counts formatting as recognition error. NFC matters more in Thai than in
    most scripts: the same syllable can arrive pre-composed or as a base plus
    combining marks, and those must not read as substitutions.
    """

    text = value.replace("\r\n", "\n").replace("\r", "\n")
    text = FIGURE.sub(" ", text)
    text = TAG.sub(" ", text)
    text = html.unescape(text)
    text = HEADING.sub("", text)
    text = BULLET.sub("", text)
    text = text.replace("```", "").replace("`", "").replace("**", "").replace("__", "")
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", text)).strip()


def align(reference: str, prediction: str) -> dict:
    """Character edits, counted by kind, straight off Levenshtein.editops."""

    substitutions: Counter[tuple[str, str]] = Counter()
    deletions: Counter[str] = Counter()
    insertions: Counter[str] = Counter()
    for operation, source_index, target_index in Levenshtein.editops(reference, prediction):
        if operation == "replace":
            substitutions[(reference[source_index], prediction[target_index])] += 1
        elif operation == "delete":
            deletions[reference[source_index]] += 1
        else:
            insertions[prediction[target_index]] += 1
    return {"substitutions": substitutions, "deletions": deletions, "insertions": insertions}


def spans(text: str, minimum: int = 40) -> list[str]:
    """Clause-sized pieces of the reference, split on the space Thai uses."""

    found: list[str] = []
    current: list[str] = []
    for word in text.split(" "):
        current.append(word)
        if sum(len(item) for item in current) >= minimum:
            found.append(" ".join(current))
            current = []
    if current:
        found.append(" ".join(current))
    return [span for span in found if len(span) >= minimum]


def verify(engine: str) -> dict | None:
    path = PREDICTIONS / f"{engine}.jsonl"
    if not path.exists():
        return None
    rows = [json.loads(line) for line in path.open(encoding="utf-8") if line.strip()]

    substitutions: Counter[tuple[str, str]] = Counter()
    deletions: Counter[str] = Counter()
    insertions: Counter[str] = Counter()
    reference_characters = 0
    edits = 0
    quotable = 0
    total_spans = 0
    renormalised = 0

    for row in rows:
        reference = normalize(row["reference_text"])
        prediction = normalize(row["prediction_text"])
        if reference != row["reference_normalized"] or prediction != row["prediction_normalized"]:
            renormalised += 1
        counts = align(reference, prediction)
        substitutions.update(counts["substitutions"])
        deletions.update(counts["deletions"])
        insertions.update(counts["insertions"])
        reference_characters += len(reference)
        edits += Levenshtein.distance(reference, prediction)
        for span in spans(reference):
            total_spans += 1
            if span in prediction:
                quotable += 1

    substitutions_per_source: Counter[str] = Counter()
    for (source, _), count in substitutions.items():
        substitutions_per_source[source] += count

    top = [
        {
            "reference": source,
            "predicted": target,
            "count": count,
            "probability_given_misread": round(count / substitutions_per_source[source], 3),
        }
        for (source, target), count in substitutions.most_common(20)
    ]

    total_edits = sum(substitutions.values()) + sum(deletions.values()) + sum(insertions.values())
    return {
        "samples": len(rows),
        "reference_characters": reference_characters,
        "cer": round(edits / reference_characters, 4) if reference_characters else None,
        "substitutions": sum(substitutions.values()),
        "deletions": sum(deletions.values()),
        "insertions": sum(insertions.values()),
        "edits_total": total_edits,
        "substitution_rate": round(sum(substitutions.values()) / reference_characters, 5)
        if reference_characters
        else None,
        "deletion_rate": round(sum(deletions.values()) / reference_characters, 5)
        if reference_characters
        else None,
        "insertion_rate": round(sum(insertions.values()) / reference_characters, 5)
        if reference_characters
        else None,
        "distinct_substitution_pairs": len(substitutions),
        "top_substitutions": top,
        # The full list, not just the head: anything sampling from this bank
        # needs every character the engine was seen to confuse, or it falls
        # back to deleting and the injected mix stops matching the measured one.
        "substitution_pairs": [
            {"reference": source, "predicted": target, "count": count}
            for (source, target), count in substitutions.most_common()
        ],
        "top_deletions": [
            {"character": character, "count": count} for character, count in deletions.most_common(15)
        ],
        "top_insertions": [
            {"character": character, "count": count}
            for character, count in insertions.most_common(15)
        ],
        "quotable_spans": {
            "reference_spans": total_spans,
            "recoverable_verbatim": quotable,
            "rate": round(quotable / total_spans, 4) if total_spans else None,
        },
        "rows_where_stored_normalisation_differed": renormalised,
    }


def main() -> int:
    verified = {}
    for engine in ENGINES:
        result = verify(engine)
        if result is None:
            continue
        verified[engine] = result
        print(
            f"{engine}: n={result['samples']} CER={result['cer']} "
            f"sub={result['substitutions']} del={result['deletions']} ins={result['insertions']} "
            f"quotable={result['quotable_spans']['rate']} "
            f"renormalised_rows={result['rows_where_stored_normalisation_differed']}"
        )
    (HERE / "verified_bank.json").write_text(
        json.dumps(verified, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
