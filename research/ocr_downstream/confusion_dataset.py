from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator

import pyarrow.parquet as parquet


ROOT = Path(__file__).resolve().parent
THAI_OCR_BENCH = ROOT / "ThaiOCRBench" / "data"
THAI_OCR_EVALUATION = ROOT / "thai-ocr-evaluation" / "test"


@dataclass(frozen=True)
class Sample:
    dataset: str
    sample_id: str
    category: str
    source_label: str
    reference_text: str
    image_path: Path | None
    image_bytes: bytes | None
    image_suffix: str


def iter_thaiocrbench(task_name: str) -> Iterator[Sample]:
    for parquet_path in sorted(THAI_OCR_BENCH.glob("*.parquet")):
        parquet_file = parquet.ParquetFile(parquet_path)
        columns = ["Id", "Task", "category", "answer", "image"]
        for batch in parquet_file.iter_batches(columns=columns, batch_size=64):
            for row in batch.to_pylist():
                if row.get("Task") != task_name:
                    continue
                image = row.get("image") or {}
                image_bytes = image.get("bytes")
                if image_bytes is None:
                    continue
                image_path = str(image.get("path") or "sample.jpeg")
                category = str(row.get("category") or "").strip()
                yield Sample(
                    dataset="ThaiOCRBench",
                    sample_id=str(row["Id"]),
                    category=category,
                    source_label=f"Task={task_name};category={category}",
                    reference_text=str(row.get("answer") or ""),
                    image_path=None,
                    image_bytes=bytes(image_bytes),
                    image_suffix=Path(image_path).suffix or ".jpeg",
                )


def iter_thai_ocr_evaluation() -> Iterator[Sample]:
    metadata_path = THAI_OCR_EVALUATION / "metadata.csv"
    if not metadata_path.exists():
        raise FileNotFoundError(f"Missing thai-ocr-evaluation metadata at {metadata_path}")
    with metadata_path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            file_name = (row.get("file_name") or "").strip()
            if not file_name:
                continue
            relative_path = Path(file_name)
            image_path = THAI_OCR_EVALUATION / relative_path
            if not image_path.exists():
                continue
            category = (row.get("category") or "").strip()
            yield Sample(
                dataset="thai-ocr-evaluation",
                sample_id=relative_path.stem,
                category=category,
                source_label=f"category={category};file={relative_path.as_posix()}",
                reference_text=row.get("text") or "",
                image_path=image_path,
                image_bytes=None,
                image_suffix=relative_path.suffix or ".png",
            )


def count_samples_by_category(samples: list[Sample]) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for sample in samples:
        dataset_counts = summary.setdefault(sample.dataset, {})
        dataset_counts[sample.category] = dataset_counts.get(sample.category, 0) + 1
    return summary


def collect_samples(
    dataset_names: list[str] | None = None,
    limit: int | None = None,
    thaiocrbench_task: str = "Full-page OCR",
) -> list[Sample]:
    if dataset_names is None:
        dataset_names = ["thai-ocr-evaluation"]
    iterators: dict[str, Iterable[Sample]] = {
        "ThaiOCRBench": iter_thaiocrbench(thaiocrbench_task),
        "thai-ocr-evaluation": iter_thai_ocr_evaluation(),
    }
    samples: list[Sample] = []
    for dataset_name in dataset_names:
        if dataset_name not in iterators:
            raise ValueError(f"Unknown dataset name: {dataset_name}. Expected one of {list(iterators.keys())}")
        dataset_samples = list(iterators[dataset_name])
        if limit is not None:
            dataset_samples = dataset_samples[:limit]
        samples.extend(dataset_samples)
    return samples

