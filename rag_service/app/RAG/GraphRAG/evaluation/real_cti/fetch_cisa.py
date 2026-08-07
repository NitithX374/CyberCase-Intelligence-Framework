"""
Fetch the CISA TTP Articles Data Set (Zenodo, DOI 10.5281/zenodo.14659512)
==========================================================================
77 CISA cybersecurity advisories (Jul 2020 - Feb 2024) crawled from
cisa.gov, kept because they carry an explicit MITRE ATT&CK section.
CC-BY-4.0.

The file is fetched rather than vendored: a Zenodo DOI points at an
immutable record, so pinning the DOI already guarantees reproducibility —
unlike the CTID plans, whose upstream branch moves and therefore had to be
copied into the repo.

cisa.gov itself answers 403 to scripted requests; this dataset is also the
citable route for a thesis.

Usage:
    cd rag_service/app
    python -m RAG.GraphRAG.evaluation.real_cti.fetch_cisa
"""

from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

ZENODO_DOI = "10.5281/zenodo.14659512"
ZENODO_URL = (
    "https://zenodo.org/records/14659512/files/"
    "CISA-crawl-rt-ttp-ct.json?download=1"
)
DEST = Path(__file__).resolve().parent / "data" / "cisa_ttp_articles.jsonl"
EXPECTED_RECORDS = 77


def fetch(force: bool = False) -> Path:
    if DEST.exists() and not force:
        print(f"[CISA] Already present: {DEST}")
        return DEST
    DEST.parent.mkdir(parents=True, exist_ok=True)
    print(f"[CISA] Downloading {ZENODO_URL}")
    with urllib.request.urlopen(ZENODO_URL, timeout=180) as resp:
        data = resp.read()
    DEST.write_bytes(data)
    n = sum(1 for line in DEST.read_text(encoding="utf-8").splitlines() if line.strip())
    print(f"[CISA] {len(data):,} bytes, {n} records -> {DEST}")
    if n != EXPECTED_RECORDS:
        print(f"[CISA] WARNING: expected {EXPECTED_RECORDS} records, got {n} — "
              f"the Zenodo record may have been superseded")
    return DEST


if __name__ == "__main__":
    fetch(force="--force" in sys.argv)
