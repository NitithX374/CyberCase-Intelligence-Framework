import argparse
import json
from pathlib import Path
from typing import Any

from app.services.document_ingestion.evaluation import (
    character_error_rate,
    evaluate,
    word_error_rate,
)

__all__ = ["character_error_rate", "evaluate", "word_error_rate"]


def _load_samples(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".jsonl":
        payload = [json.loads(line) for line in text.splitlines() if line.strip()]
    else:
        payload = json.loads(text)
        if isinstance(payload, dict):
            payload = [payload]
    if not isinstance(payload, list):
        raise ValueError(
            "Evaluation input must be a JSON object, JSON array, or JSONL."
        )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    arguments = parser.parse_args()
    print(
        json.dumps(
            evaluate(_load_samples(arguments.input)), ensure_ascii=False, indent=2
        )
    )


if __name__ == "__main__":
    main()
