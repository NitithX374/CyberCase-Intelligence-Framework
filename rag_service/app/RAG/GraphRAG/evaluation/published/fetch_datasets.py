"""
Fetch the TechniqueRAG benchmark splits
=========================================
Downloads the three zero-shot test splits published with TechniqueRAG from
HuggingFace. Fetched rather than vendored - see NOTICE.md for why, and for the
licence position.

Only the `*_zeroshot_test.json` files are pulled. The few-shot / reflections
variants pre-bake retrieved context into the prompt, which is exactly the part
this project supplies itself, and the train splits are unused because every arm
here is zero-shot.

Usage:
    cd rag_service/app
    python -m RAG.GraphRAG.evaluation.published.fetch_datasets
    python -m RAG.GraphRAG.evaluation.published.fetch_datasets --force
"""

from __future__ import annotations

import argparse
import io
import json
import sys
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

DATA_DIR = Path(__file__).resolve().parent / "data"
REPO = "QCRI/TechniqueRAG-Datasets"
BASE_URL = "https://huggingface.co/datasets/" + REPO + "/resolve/main/test/"

SPLITS = ("tram_zeroshot_test", "expert_zeroshot_test", "procedures_zeroshot_test")


def fetch(force: bool = False) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for split in SPLITS:
        dest = DATA_DIR / (split + ".json")
        if dest.exists() and not force:
            rows = json.loads(dest.read_text(encoding="utf-8"))
            print("[FETCH] " + split.ljust(28) + "present (" + str(len(rows)) + " rows)")
            continue
        url = BASE_URL + split + ".json"
        print("[FETCH] " + split.ljust(28) + "downloading...")
        with urllib.request.urlopen(url) as response:  # noqa: S310 - fixed https host
            payload = response.read()
        dest.write_bytes(payload)
        rows = json.loads(dest.read_text(encoding="utf-8"))
        print("        -> " + str(dest) + " (" + str(len(rows)) + " rows, " + str(len(payload) // 1024) + " KB)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch TechniqueRAG benchmark splits")
    parser.add_argument("--force", action="store_true", help="re-download even if present")
    args = parser.parse_args()
    fetch(force=args.force)


if __name__ == "__main__":
    main()
