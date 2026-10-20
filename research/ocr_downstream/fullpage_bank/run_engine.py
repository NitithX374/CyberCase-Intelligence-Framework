"""Run one OCR engine over every ThaiOCRBench Full-page OCR sample.

Three engines, one record shape, so the bank is built from comparable rows:

  typhoon    the VLM the product uses; predictions are read from the cached
             run rather than re-billed
  paddle     PaddleOCR's full pipeline - PP-DocLayoutV3 layout and reading
             order, then PP-OCRv5 detection, then Thai recognition
  tesseract  the classical LSTM baseline, tha+eng

Writes predictions/<engine>.jsonl. Reruns skip samples already written, so a
long CPU run can be interrupted.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
OCR_ROOT = HERE.parent
sys.path.insert(0, str(OCR_ROOT))

from confusion_dataset import iter_thaiocrbench  # noqa: E402
from confusion_text import normalize_for_alignment  # noqa: E402

TASK = "Full-page OCR"
PREDICTIONS = HERE / "predictions"
TYPHOON_CACHE = OCR_ROOT / "results" / "character_confusion_document_plaintext" / "predictions.jsonl"


def record(sample, prediction_text: str, elapsed: float, engine: str) -> dict:
    reference_normalized = normalize_for_alignment(sample.reference_text)
    prediction_normalized = normalize_for_alignment(prediction_text)
    return {
        "status": "ok" if prediction_normalized else "empty",
        "engine": engine,
        "dataset": "ThaiOCRBench",
        "task": TASK,
        "sample_id": sample.sample_id,
        "category": sample.category or "unknown",
        "source_label": sample.source_label,
        "reference_text": sample.reference_text,
        "prediction_text": prediction_text,
        "reference_normalized": reference_normalized,
        "prediction_normalized": prediction_normalized,
        "elapsed_seconds": round(elapsed, 3),
    }


def already_written(path: Path) -> set[str]:
    if not path.exists():
        return set()
    with path.open(encoding="utf-8") as handle:
        return {json.loads(line)["sample_id"] for line in handle if line.strip()}


def typhoon_predictions() -> dict[str, str]:
    """The cached run. Re-billing 197 pages to reproduce it buys nothing."""

    cached: dict[str, str] = {}
    with TYPHOON_CACHE.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            text = row.get("prediction_text") or ""
            if text.strip():
                cached[row["sample_id"]] = text
    return cached


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", required=True, choices=("typhoon", "paddle", "tesseract"))
    parser.add_argument("--limit", type=int, default=None, help="stop after N new samples")
    parser.add_argument(
        "--mark-crashed",
        action="store_true",
        help="record the sample named in the sentinel as crashed, so a rerun moves past it",
    )
    arguments = parser.parse_args()

    PREDICTIONS.mkdir(parents=True, exist_ok=True)
    output = PREDICTIONS / f"{arguments.engine}.jsonl"
    sentinel = PREDICTIONS / f".{arguments.engine}.attempting"

    if arguments.mark_crashed:
        return mark_crashed(sentinel, output, arguments.engine)

    done = already_written(output)

    samples = [s for s in iter_thaiocrbench(TASK)]
    pending = [s for s in samples if s.sample_id not in done]
    if arguments.limit is not None:
        pending = pending[: arguments.limit]
    print(f"{arguments.engine}: {len(samples)} samples, {len(done)} done, {len(pending)} to run", flush=True)

    predict = build_engine(arguments.engine)

    with output.open("a", encoding="utf-8") as handle:
        for index, sample in enumerate(pending, 1):
            # PaddleOCR segfaults on some pages, which no except clause can
            # catch. Name the page first so a supervisor knows what died.
            sentinel.write_text(sample.sample_id, encoding="utf-8")
            started = time.time()
            try:
                text = predict(sample)
            except Exception as error:  # a page that fails is a row, not a crash
                text = ""
                print(f"  [{index}/{len(pending)}] {sample.sample_id} FAILED {error}", flush=True)
            row = record(sample, text, time.time() - started, arguments.engine)
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            handle.flush()
            sentinel.unlink(missing_ok=True)
            print(
                f"  [{index}/{len(pending)}] {sample.sample_id} {sample.category} "
                f"ref={len(row['reference_normalized'])} pred={len(row['prediction_normalized'])} "
                f"{row['elapsed_seconds']}s",
                flush=True,
            )
    return 0


def mark_crashed(sentinel: Path, output: Path, engine: str) -> int:
    """Write the page that killed the process as an empty row.

    Without this a rerun attempts the same page, dies the same way, and the
    loop never advances. A page the engine cannot read is a result.
    """

    if not sentinel.exists():
        print("no sentinel: nothing crashed")
        return 0
    sample_id = sentinel.read_text(encoding="utf-8").strip()
    for sample in iter_thaiocrbench(TASK):
        if sample.sample_id != sample_id:
            continue
        row = record(sample, "", 0.0, engine)
        row["status"] = "crashed"
        with output.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        sentinel.unlink(missing_ok=True)
        print(f"recorded {sample_id} as crashed")
        return 0
    print(f"sentinel names an unknown sample: {sample_id}")
    return 1


def build_engine(name: str):
    if name == "typhoon":
        cached = typhoon_predictions()
        return lambda sample: cached.get(sample.sample_id, "")

    if name == "tesseract":
        from tesseract_adapter import TesseractThaiAdapter

        adapter = TesseractThaiAdapter(lang="tha+eng")

        def tesseract(sample):
            with tempfile.NamedTemporaryFile(suffix=sample.image_suffix, delete=False) as handle:
                handle.write(sample.image_bytes)
                path = handle.name
            try:
                return adapter.predict_image(path, sample_id=sample.sample_id)["plain_text"]
            finally:
                Path(path).unlink(missing_ok=True)

        return tesseract

    from modular_layout_ocr import ModularLayoutThaiOCR

    engine = ModularLayoutThaiOCR(device="cpu")
    return lambda sample: engine.predict(sample.image_bytes, sample_id=sample.sample_id)["plain_text"]


if __name__ == "__main__":
    raise SystemExit(main())
