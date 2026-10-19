"""Deterministic measurements of the Source-unit construction (no model calls, no labels).

Runs the production segmentation and identifiers (backend/app/sources/evidence.py) over public
corpora and records:

  1. losslessness: every unit equals S[start:end], units are contiguous and their concatenation is S;
  2. determinism: a second run gives identical units and identifiers (and a digest of all units is
     stored, so separate runs can be compared);
  3. revision safety: after one random single-character insertion, every old identifier resolves to
     stale_id, compared with what raw offsets and position-only identifiers would silently return;
  4. boundary integrity: the share of cut points that fall inside a word, for unit boundaries and for
     fixed-size character chunks of the same mean length (PyThaiNLP newmm words for Thai, \\w+ runs
     for English);
  5. unit lengths and segmentation time.

Corpora (pinned revisions):
  ThaiSum test articles (pythainlp/thaisum, MIT), deterministic sample of N by SHA-256 of the text;
  AttributionBench test + test_ood references (osunlp/AttributionBench), all unique non-empty texts.

Run from the repository root with the backend requirements installed:
  python research/traceability_properties/run.py [--thai-n 1000] [--en-n 0]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import random
import re
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "backend"))

from app.sources.bundle import CaseSourceItem  # noqa: E402
from app.sources.evidence import (  # noqa: E402
    EVIDENCE_VERSION,
    EvidenceIndex,
    evidence_units,
)
from app.trace import sentences  # noqa: E402
from app.trace.quotes import MAX_QUOTE_CHARS  # noqa: E402

THAISUM = ("pythainlp/thaisum", "6c2928cb64cd0d8ec0f3790ce848048fde1911dd",
           "data/test-00000-of-00001-f0463a2623057daa.parquet")
ATTRBENCH = ("osunlp/AttributionBench", "62569e644f4186606f54f742178a4517431b42e1",
             ("test_all_subset_balanced.jsonl", "test_ood_all_subset_balanced.jsonl"))
THAI_CHAR = re.compile(r"[฀-๿]")
WORD = re.compile(r"\w+")


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def download(repo: str, revision: str, filename: str) -> Path:
    from huggingface_hub import hf_hub_download

    return Path(hf_hub_download(repo, filename, repo_type="dataset", revision=revision))


def thai_corpus(n: int) -> tuple[list[str], dict]:
    import pyarrow.parquet as pq

    path = download(*THAISUM)
    bodies = [b for b in pq.read_table(path, columns=["body"]).column("body").to_pylist() if b and b.strip()]
    unique = sorted(set(bodies), key=sha)
    texts = unique[:n] if n else unique
    return texts, {"dataset": THAISUM[0], "revision": THAISUM[1], "file": THAISUM[2],
                   "file_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                   "available": len(unique), "used": len(texts), "sample": "first N by SHA-256 of text"}


def english_corpus(n: int) -> tuple[list[str], dict]:
    refs, hashes = set(), {}
    for filename in ATTRBENCH[2]:
        path = download(ATTRBENCH[0], ATTRBENCH[1], filename)
        hashes[filename] = hashlib.sha256(path.read_bytes()).hexdigest()
        for line in path.read_text().splitlines():
            for ref in json.loads(line)["references"]:
                if ref.strip():
                    refs.add(ref)
    unique = sorted(refs, key=sha)
    texts = unique[:n] if n else unique
    return texts, {"dataset": ATTRBENCH[0], "revision": ATTRBENCH[1], "files": hashes,
                   "available": len(unique), "used": len(texts), "sample": "all unique non-empty references"
                   if not n else "first N by SHA-256 of text"}


def source(text: str, sid: str = "S1") -> CaseSourceItem:
    return CaseSourceItem(source_id=sid, source_kind="narrative", text=text)


def lossless(text: str, units) -> bool:
    if not units:
        return text == ""
    ok = units[0].start == 0 and units[-1].end == len(text)
    ok &= all(u.text == text[u.start:u.end] for u in units)
    ok &= all(a.end == b.start for a, b in zip(units, units[1:]))
    return ok and "".join(u.text for u in units) == text


def word_boundaries(text: str, thai: bool) -> tuple[set[int], list[tuple[int, int]]]:
    """Positions that are word boundaries, and word spans (for the English check)."""
    if thai:
        from pythainlp.tokenize import word_tokenize

        cuts, at = {0}, 0
        for token in word_tokenize(text, engine="newmm", keep_whitespace=True):
            at += len(token)
            cuts.add(at)
        if at != len(text):  # tokenizer did not reproduce the text; fall back to no-information
            return set(range(len(text) + 1)), []
        return cuts, []
    spans = [(m.start(), m.end()) for m in WORD.finditer(text)]
    return set(), spans


def mid_word(cut: int, text: str, thai: bool, cuts: set[int], spans: list[tuple[int, int]]) -> bool:
    if thai:
        return cut not in cuts
    return any(a < cut < b for a, b in spans)


def splits_number(cut: int, text: str) -> bool:
    return 0 < cut < len(text) and text[cut - 1].isdigit() and text[cut].isdigit()


def edit(text: str, rng: random.Random, thai: bool) -> str:
    position = rng.randrange(len(text) + 1)
    return text[:position] + ("ก" if thai else "x") + text[position:]


def summarise(values: list[float]) -> dict:
    values = sorted(values)
    return {"mean": statistics.fmean(values), "median": statistics.median(values),
            "p95": values[int(0.95 * (len(values) - 1))], "max": values[-1], "min": values[0]}


def measure(name: str, texts: list[str], thai: bool) -> dict:
    t0 = time.perf_counter()
    all_units = [evidence_units(source(text)) for text in texts]
    seconds = time.perf_counter() - t0

    lengths = [u.end - u.start for units in all_units for u in units]
    mean_len = statistics.fmean(lengths)
    chunk = max(1, round(mean_len))

    # 1. losslessness
    lossless_fail = sum(not lossless(text, units) for text, units in zip(texts, all_units))

    # 2. determinism: a second pass in this run, plus a digest for comparing separate runs
    det_fail = sum(evidence_units(source(text)) != units for text, units in zip(texts, all_units))
    digest = hashlib.sha256("\n".join(f"{u.unit_id}\t{u.start}\t{u.end}" for units in all_units
                                       for u in units).encode()).hexdigest()

    # 3. revision safety after one random insertion
    flagged = offsets_silent = positional_silent = positional_error = unchanged_units = total_ids = 0
    sources_offsets_silent = sources_positional_silent = 0
    for text, units in zip(texts, all_units):
        rng = random.Random(sha(text))
        edited = edit(text, rng, thai)
        index = EvidenceIndex([source(edited)])
        new_units = evidence_units(source(edited))
        any_offset, any_positional = False, False
        for k, u in enumerate(units):
            total_ids += 1
            _, reason = index.resolve("S1", u.unit_id)
            flagged += reason == "stale_id"
            if edited[u.start:u.end] != u.text:
                offsets_silent += 1
                any_offset = True
            else:
                unchanged_units += 1
            if k < len(new_units):
                if new_units[k].text != u.text:
                    positional_silent += 1
                    any_positional = True
            else:
                positional_error += 1
        sources_offsets_silent += any_offset
        sources_positional_silent += any_positional

    # 4. boundary integrity
    unit_cuts = unit_mid = unit_num = 0
    fixed_cuts = fixed_mid = fixed_num = 0
    for text, units in zip(texts, all_units):
        cuts, spans = word_boundaries(text, thai)
        for u in units[1:]:
            unit_cuts += 1
            unit_mid += mid_word(u.start, text, thai, cuts, spans)
            unit_num += splits_number(u.start, text)
        for cut in range(chunk, len(text), chunk):
            fixed_cuts += 1
            fixed_mid += mid_word(cut, text, thai, cuts, spans)
            fixed_num += splits_number(cut, text)

    chars = sum(len(t) for t in texts)
    return {
        "corpus": name,
        "sources": len(texts),
        "characters": chars,
        "thai_share_of_sources": sum(bool(THAI_CHAR.search(t)) for t in texts) / len(texts),
        "units": len(lengths),
        "units_per_source": summarise([len(u) for u in all_units]),
        "unit_length_chars": summarise(lengths),
        "units_at_length_cap": sum(n == MAX_QUOTE_CHARS for n in lengths),
        "segmentation_seconds": seconds,
        "ms_per_1000_chars": 1000 * seconds / (chars / 1000),
        "lossless_failures": lossless_fail,
        "determinism_failures": det_fail,
        "units_digest": digest,
        "revision": {
            "edit": "one random single-character insertion per source (seeded by SHA-256 of the text)",
            "old_ids": total_ids,
            "content_addressed_stale_id": flagged,
            "raw_offsets_silently_changed": offsets_silent,
            "raw_offsets_unchanged": unchanged_units,
            "positional_ids_silently_changed": positional_silent,
            "positional_ids_out_of_range": positional_error,
            "sources_with_a_silent_offset_change": sources_offsets_silent,
            "sources_with_a_silent_positional_change": sources_positional_silent,
        },
        "boundaries": {
            "reference_words": "PyThaiNLP newmm" if thai else "regex \\w+ runs",
            "fixed_chunk_chars": chunk,
            "unit_cuts": unit_cuts,
            "unit_cuts_mid_word": unit_mid,
            "unit_cuts_splitting_digits": unit_num,
            "fixed_cuts": fixed_cuts,
            "fixed_cuts_mid_word": fixed_mid,
            "fixed_cuts_splitting_digits": fixed_num,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--thai-n", type=int, default=1000)
    parser.add_argument("--en-n", type=int, default=0)
    parser.add_argument("--out", default=str(HERE / "results" / "properties.json"))
    args = parser.parse_args()

    segmenter = sentences.get_sat_segmenter()
    import pythainlp
    import torch
    import wtpsplit

    th_texts, th_meta = thai_corpus(args.thai_n)
    en_texts, en_meta = english_corpus(args.en_n)
    result = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "evidence_version": EVIDENCE_VERSION,
        "segmenter": "SaT sat-3l-sm (threshold %.3f)" % sentences.SAT_THRESHOLD if segmenter else
                     "PyThaiNLP crfcut fallback (SaT unavailable)",
        "min_sentence_chars": sentences.MIN_SENTENCE_CHARS,
        "max_unit_chars": MAX_QUOTE_CHARS,
        "environment": {"python": platform.python_version(), "platform": platform.platform(),
                        "pythainlp": pythainlp.__version__, "wtpsplit": getattr(wtpsplit, "__version__", "?"),
                        "torch": torch.__version__},
        "inputs": {"thai": th_meta, "english": en_meta},
        "results": [measure("ThaiSum test (Thai news)", th_texts, True),
                    measure("AttributionBench references (English)", en_texts, False)],
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result["results"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
