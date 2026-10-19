"""Turn the three prediction files into one bank and one report.

Per engine this produces the character confusion bank (what turns into what,
how often) and the filtered error catalogue (the same, minus edits that are
formatting rather than recognition). The bank is the point: it is what the
downstream corruption generator should be driven by instead of substitution
rules written by hand.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import Levenshtein

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from build_error_catalogue import build_catalogues  # noqa: E402
from confusion_alignment import build_bank  # noqa: E402
from confusion_text import get_normalization_metadata  # noqa: E402

ENGINES = ("typhoon", "paddle", "tesseract")
PREDICTIONS = HERE / "predictions"
BANK = HERE / "bank"

# What each engine was actually asked to do. The PaddleOCR entry is the one
# that changes how its score should be read: the pipeline classifies layout
# first and keeps only the regions it calls text, so a government form's table
# never reaches recognition. Its CER is therefore the cost of a pipeline that
# drops tables, not a measure of how well it reads Thai characters.
ENGINE_CONFIGURATION = {
    "typhoon": (
        "Typhoon OCR, the vision-language model the product uses. Whole page in, "
        "text out; no layout stage of our own. Predictions are reused from the "
        "earlier cached run rather than re-billed."
    ),
    "paddle": (
        "PaddleOCR full pipeline: PP-DocLayoutV3 for layout and reading order, then "
        "PP-OCRv5_server_det for line detection, then th_PP-OCRv5_mobile_rec. CPU. "
        "Regions labelled table, formula, chart, figure, image or stamp are EXCLUDED "
        "before recognition, so their text is scored as deleted. Some pages kill the "
        "native process outright; those are recorded with status=crashed and an empty "
        "prediction rather than dropped from the denominator."
    ),
    "tesseract": "Tesseract LSTM, lang=tha+eng, official tessdata. Whole page, no layout stage.",
}


def load(engine: str) -> list[dict]:
    path = PREDICTIONS / f"{engine}.jsonl"
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def engine_metrics(records: list[dict]) -> dict:
    """CER over the whole task, and per sample, so one bad page is visible."""

    per_sample = []
    total_edits = 0
    total_reference = 0
    empty = 0
    for row in records:
        reference = row["reference_normalized"]
        prediction = row["prediction_normalized"]
        if not prediction:
            empty += 1
        edits = Levenshtein.distance(reference, prediction)
        total_edits += edits
        total_reference += len(reference)
        per_sample.append(
            {
                "sample_id": row["sample_id"],
                "category": row["category"],
                "reference_characters": len(reference),
                "prediction_characters": len(prediction),
                "edits": edits,
                "cer": round(edits / len(reference), 4) if reference else None,
                "elapsed_seconds": row.get("elapsed_seconds"),
            }
        )

    by_category: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0])
    for sample in per_sample:
        bucket = by_category[sample["category"]]
        bucket[0] += sample["edits"]
        bucket[1] += sample["reference_characters"]
        bucket[2] += 1

    seconds = [s["elapsed_seconds"] for s in per_sample if s["elapsed_seconds"]]
    cers = [s["cer"] for s in per_sample if s["cer"] is not None]
    return {
        "samples": len(records),
        "empty_predictions": empty,
        # A page the engine could not survive still counts against it.
        "crashed_pages": sum(1 for row in records if row.get("status") == "crashed"),
        "reference_characters": total_reference,
        "edits": total_edits,
        # One CER over all characters, so long pages weigh what they cost.
        "cer_micro": round(total_edits / total_reference, 4) if total_reference else None,
        # And one averaging the pages, which a short page can move.
        "cer_macro": round(sum(cers) / len(cers), 4) if cers else None,
        "seconds_per_page_mean": round(sum(seconds) / len(seconds), 2) if seconds else None,
        "by_category": {
            name: {
                "samples": bucket[2],
                "cer": round(bucket[0] / bucket[1], 4) if bucket[1] else None,
            }
            for name, bucket in sorted(by_category.items(), key=lambda item: -item[1][2])
        },
        "per_sample": sorted(per_sample, key=lambda s: -(s["cer"] or 0)),
    }


def quotable_sentences(records: list[dict]) -> dict:
    """How much of the true text survives OCR exactly.

    This is the ceiling on exact-quote grounding: a citation can only ever be
    checked against the OCR text, so a reference span that OCR did not
    reproduce verbatim is a span no claim can correctly quote.
    """

    exact = 0
    total = 0
    for row in records:
        prediction = row["prediction_normalized"]
        for span in split_spans(row["reference_normalized"]):
            total += 1
            if span in prediction:
                exact += 1
    return {
        "reference_spans": total,
        "recoverable_verbatim": exact,
        "rate": round(exact / total, 4) if total else None,
    }


def split_spans(text: str, minimum: int = 40) -> list[str]:
    """Thai writes no sentence-final period, so build spans on the space it uses.

    A span is roughly a clause: long enough that finding it verbatim means
    something, short enough that a claim would plausibly quote it.
    """

    spans: list[str] = []
    current: list[str] = []
    for word in text.split(" "):
        current.append(word)
        if sum(len(item) for item in current) >= minimum:
            spans.append(" ".join(current))
            current = []
    if current:
        spans.append(" ".join(current))
    return [span for span in spans if len(span) >= minimum]


def matched_subset(loaded: dict[str, list[dict]]) -> dict:
    """The same pages for every engine.

    An engine that only got through part of the task cannot be compared to one
    that finished it: whichever pages it happened to reach decide its score,
    and the categories are not evenly hard. This restricts all engines to the
    pages they all have, which is the only head-to-head number here.
    """

    shared = set.intersection(*({row["sample_id"] for row in rows} for rows in loaded.values()))
    result = {"pages": len(shared), "engines": {}}
    for engine, rows in loaded.items():
        edits = 0
        reference_characters = 0
        for row in rows:
            if row["sample_id"] not in shared:
                continue
            reference = row["reference_normalized"]
            edits += Levenshtein.distance(reference, row["prediction_normalized"])
            reference_characters += len(reference)
        result["engines"][engine] = {
            "cer": round(edits / reference_characters, 4) if reference_characters else None,
            "reference_characters": reference_characters,
        }
    return result


def main() -> int:
    BANK.mkdir(parents=True, exist_ok=True)
    settings = {
        "dataset": "ThaiOCRBench",
        "task": "Full-page OCR",
        "normalization": get_normalization_metadata(),
        "engine_configuration": ENGINE_CONFIGURATION,
    }

    report: dict[str, dict] = {}
    loaded: dict[str, list[dict]] = {}
    for engine in ENGINES:
        records = load(engine)
        if not records:
            print(f"{engine}: no predictions yet, skipped")
            continue
        loaded[engine] = records
        metrics = engine_metrics(records)
        bank = build_bank(records, {**settings, "engine": engine})
        (BANK / f"{engine}_confusion_bank.json").write_text(
            json.dumps(bank, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        catalogue, filtered, rejections = build_catalogues(
            [PREDICTIONS / f"{engine}.jsonl"], BANK / engine
        )
        report[engine] = {
            **metrics,
            "quotable": quotable_sentences(records),
            "catalogue": {
                "raw": catalogue.name,
                "filtered": filtered.name,
                "rejections": rejections.name,
            },
        }
        print(
            f"{engine}: n={metrics['samples']} CER={metrics['cer_micro']} "
            f"quotable={report[engine]['quotable']['rate']}"
        )

    matched = matched_subset(loaded) if loaded else {"pages": 0, "engines": {}}
    (HERE / "metrics.json").write_text(
        json.dumps(
            {"settings": settings, "matched_subset": matched, "engines": report},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    write_report(report, matched)
    return 0


def write_report(report: dict[str, dict], matched: dict) -> None:
    lines = [
        "# Full-page OCR: three engines over ThaiOCRBench",
        "",
        "The task is all 197 `Task=Full-page OCR` samples of ThaiOCRBench (IJCNLP-AACL 2025).",
        "The `n` column says how many each engine actually got through: Typhoon has the whole",
        "task, the two CPU engines were stopped short. Use the shared-page table below for any",
        "comparison between engines.",
        "",
        "CER is computed on NFC-normalised text with markup removed; `cer_micro` pools all",
        "characters, `cer_macro` averages the pages.",
        "",
        "| Engine | n | CER micro | CER macro | Empty | Crashed | s/page | Spans quotable verbatim |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for engine, data in report.items():
        quotable = data["quotable"]
        lines.append(
            f"| {engine} | {data['samples']} | {data['cer_micro']} | {data['cer_macro']} | "
            f"{data['empty_predictions']} | {data['crashed_pages']} | "
            f"{data['seconds_per_page_mean']} | "
            f"{quotable['recoverable_verbatim']}/{quotable['reference_spans']} "
            f"({quotable['rate']}) |"
        )

    lines += [
        "",
        f"## Head to head, on the {matched['pages']} pages every engine read",
        "",
        "The table above gives each engine its own page set, and the engines did not all",
        "finish. Categories differ in difficulty, so those columns are not comparable to",
        "each other. These are.",
        "",
        "| Engine | CER on the shared pages |",
        "| --- | ---: |",
    ]
    for engine, data in matched["engines"].items():
        lines.append(f"| {engine} | {data['cer']} |")

    lines += ["", "## What each engine was asked to do", ""]
    for engine in report:
        lines += [f"**{engine}** — {ENGINE_CONFIGURATION[engine]}", ""]
    lines += [
        "The three are not equivalent readers of a page. Typhoon and Tesseract are given",
        "the whole image; PaddleOCR is given only what its layout model calls text. Read",
        "the PaddleOCR column as the pipeline's score, not the recogniser's.",
    ]

    for engine, data in report.items():
        lines += [
            "",
            f"## {engine} by category",
            "",
            "| Category | n | CER |",
            "| --- | ---: | ---: |",
        ]
        for name, bucket in data["by_category"].items():
            lines.append(f"| {name} | {bucket['samples']} | {bucket['cer']} |")

    (HERE / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
