from __future__ import annotations

import argparse
import json
import os
import re
import sys
import warnings
from dataclasses import asdict
from pathlib import Path
from time import perf_counter

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

warnings.filterwarnings("ignore")

import logging
import transformers
transformers.logging.set_verbosity_error()
logging.getLogger("transformers").setLevel(logging.ERROR)

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))

import unicodedata
from app.sources.bundle import CaseSourceItem
from app.sources.evidence import evidence_units
from app.trace.b1_verifier import (
    ARTIFACT,
    ARTIFACT_SHA256,
    ClaimVerification,
    selected_indices,
    supported_probability,
)
from app.trace.sentences import segmenter_identity

from research.attribution_benchmark.data import read_split
from research.attribution_benchmark.receipts import digest, save
from research.attribution_benchmark.translate_th import plan, read_cache
from research.attribution_benchmark.verifier_runtime import load_runtime

BENCH = HERE.parent
NEWLINE = chr(10)



def paragraph_units(reference: str) -> list[list[str]]:
    if not reference.strip():
        return []
    paragraphs = [
        [
            sentence.strip()
            for sentence in re.split(r"(?<=[.!?])\s+", paragraph.strip())
            if len(sentence.strip()) > 3
        ]
        for paragraph in reference.split("\n")
        if paragraph.strip()
    ]
    paragraphs = [units for units in paragraphs if units]
    return paragraphs or [[reference.strip()]]


def sat_units(references: list[str]) -> list[str]:
    units = []
    for index, reference in enumerate(references, 1):
        source = CaseSourceItem(source_id=f"ref{index:02d}", source_kind="narrative", text=reference)
        units.extend(unit.text for unit in evidence_units(source) if unit.text.strip())
    return units


def score_pair(verifier, claim: str, units: list[str], *, with_nfkc: bool = False) -> tuple[dict, dict | None]:
    started = perf_counter()
    if units:
        similarities = tuple(verifier.selector.similarities(claim, units))
        indices = selected_indices(similarities)
        selection_ms = (perf_counter() - started) * 1000
        premise = ARTIFACT["premise_separator"].join(units[index] for index in indices)

        # 1. Base NLI (without NFKC)
        nli_base = verifier.nli.predict(premise, claim)
        p_base = supported_probability(nli_base.vector)
        res_base = {
            "p_supported": p_base,
            "supported": p_base >= 0.5,
            "nli": asdict(nli_base),
            "units": len(units),
            "selected": len(indices),
            "indices": list(indices),
            "duration_ms": (perf_counter() - started) * 1000,
        }

        # 2. NFKC NLI (with NFKC)
        if with_nfkc:
            nli_prem = unicodedata.normalize("NFKC", premise)
            nli_hyp = unicodedata.normalize("NFKC", claim)
            t_nfkc = perf_counter()
            nli_nfkc = verifier.nli.predict(nli_prem, nli_hyp)
            p_nfkc = supported_probability(nli_nfkc.vector)
            res_nfkc = {
                "p_supported": p_nfkc,
                "supported": p_nfkc >= 0.5,
                "nli": asdict(nli_nfkc),
                "units": len(units),
                "selected": len(indices),
                "indices": list(indices),
                "duration_ms": (perf_counter() - t_nfkc + selection_ms),
            }
        else:
            res_nfkc = None
    else:
        # Empty units
        nli_base = verifier.nli.predict("", claim)
        p_base = supported_probability(nli_base.vector)
        res_base = {
            "p_supported": p_base,
            "supported": p_base >= 0.5,
            "nli": asdict(nli_base),
            "units": 0,
            "selected": 0,
            "indices": [],
            "duration_ms": (perf_counter() - started) * 1000,
        }
        if with_nfkc:
            nli_hyp = unicodedata.normalize("NFKC", claim)
            nli_nfkc = verifier.nli.predict("", nli_hyp)
            p_nfkc = supported_probability(nli_nfkc.vector)
            res_nfkc = {
                "p_supported": p_nfkc,
                "supported": p_nfkc >= 0.5,
                "nli": asdict(nli_nfkc),
                "units": 0,
                "selected": 0,
                "indices": [],
                "duration_ms": (perf_counter() - started) * 1000,
            }
        else:
            res_nfkc = None

    return res_base, res_nfkc


def score(verifier, claim: str, units: list[str]) -> dict:
    base, _ = score_pair(verifier, claim, units, with_nfkc=False)
    return base



def thai_rebuild(row, translated) -> list[str]:
    return [
        NEWLINE.join(" ".join(translated[digest(unit)] for unit in para) for para in reference)
        for reference in (paragraph_units(reference) for reference in row["references"])
    ]


def cut(output: Path):
    output.mkdir(parents=True, exist_ok=True)
    examples, _ = plan()
    cached = read_cache(BENCH / "raw/attribution-mt-th/translations.jsonl")
    translated = {key: entry["translation"] for key, entry in cached.items()}
    rows = {row["id"]: row for split in ("test", "test_ood") for row in read_split(split)}
    started = perf_counter()
    with (output / "units.jsonl").open("w", encoding="utf-8") as file:
        for count, example in enumerate(examples):
            row = rows[example["id"]]
            thai_references = thai_rebuild(row, translated)
            file.write(json.dumps({
                "id": example["id"],
                "segmenter": segmenter_identity(),
                "sat_en_units": sat_units(row["references"]),
                "sat_th_units": sat_units(thai_references),
                "thai_references": thai_references,
            }, ensure_ascii=False) + NEWLINE)
            if count % 200 == 0:
                print(f"cut {count} rows, {perf_counter() - started:.0f} s", flush=True)
    print(f"cut done in {perf_counter() - started:.0f} s", flush=True)


def run(output: Path, limit: int | None, device: str, units_path: Path | None):
    output.mkdir(parents=True, exist_ok=True)
    examples, texts = plan()
    cached = read_cache(BENCH / "raw/attribution-mt-th/translations.jsonl")
    published = {
        json.loads(line)["id"]: json.loads(line)
        for line in (BENCH / "raw/b1-mt-th/scores.jsonl").read_text(encoding="utf-8").split(NEWLINE) if line
    }
    published_norm_path = BENCH / "raw/b1-mt-th-normalized/scores.jsonl"
    published_norm = {}
    if published_norm_path.exists():
        published_norm = {
            json.loads(line)["id"]: json.loads(line)
            for line in published_norm_path.read_text(encoding="utf-8").split(NEWLINE) if line
        }
    rows = {row["id"]: row for split in ("test", "test_ood") for row in read_split(split)}
    translated = {key: entry["translation"] for key, entry in cached.items()}
    precut = {}
    if units_path:
        for line in units_path.read_text(encoding="utf-8").split(NEWLINE):
            if not line:
                continue
            entry = json.loads(line)
            precut[entry["id"]] = entry
    verifier, runtime = load_runtime(device)
    runtime["segmenter"] = segmenter_identity()
    save(output / "runtime.json", runtime)
    score_path = output / "scores.jsonl"
    done = set()
    if score_path.exists():
        done = {json.loads(line)["id"] for line in score_path.read_text(encoding="utf-8").split(NEWLINE) if line}
    started = perf_counter()
    with score_path.open("a", encoding="utf-8") as file:
        for count, example in enumerate(examples[:limit] if limit else examples):
            if example["id"] in done:
                continue
            row = rows[example["id"]]
            original = published[example["id"]]
            en_claim = texts[example["claim_key"]]
            th_claim = translated[example["claim_key"]]
            regex_en = [texts[key] for key in example["unit_keys"]]
            regex_th = [translated[key] for key in example["unit_keys"]]
            if original["input_sha256"] != digest([th_claim, regex_th, example]):
                raise ValueError("Regex input differs from the published row")
            grouped = [paragraph_units(reference) for reference in row["references"]]
            if [unit for reference in grouped for para in reference for unit in para] != regex_en:
                raise ValueError(f"Paragraph regrouping differs from plan units: {example['id']}")
            thai_references = thai_rebuild(row, translated)
            if precut:
                entry = precut[example["id"]]
                if entry["thai_references"] != thai_references:
                    raise ValueError("Pre-cut Thai text differs")
                sat_en_units, sat_th_units = entry["sat_en_units"], entry["sat_th_units"]
            else:
                sat_en_units = sat_units(row["references"])
                sat_th_units = sat_units(thai_references)

            rloc_en, rloc_en_nfkc = score_pair(verifier, en_claim, regex_en, with_nfkc=True)
            rloc_th, rloc_th_nfkc = score_pair(verifier, th_claim, regex_th, with_nfkc=True)
            sat_en, sat_en_nfkc = score_pair(verifier, en_claim, sat_en_units, with_nfkc=True)
            sat_th, sat_th_nfkc = score_pair(verifier, th_claim, sat_th_units, with_nfkc=True)

            norm_orig = published_norm.get(example["id"])
            record = {
                "split": example["split"],
                "id": example["id"],
                "gold": example["gold"],
                "artifact_sha256": ARTIFACT_SHA256,
                "published_en_supported": original["en_supported"],
                "published_th_supported": original["th_supported"],
                "published_th_normalized_supported": norm_orig["th_supported"] if norm_orig else None,
                "published_en_nli": original["en"]["nli"],
                "published_th_nli": original["th"]["nli"],
                "rloc_en": rloc_en,
                "rloc_th": rloc_th,
                "rloc_th_nfkc": rloc_th_nfkc,
                "rloc_en_nfkc": rloc_en_nfkc,
                "sat_en": sat_en,
                "sat_th": sat_th,
                "sat_en_nfkc": sat_en_nfkc,
                "sat_th_nfkc": sat_th_nfkc,
                "sat_en_units": sat_en_units,
                "sat_th_units": sat_th_units,
                "thai_references": thai_references,
                "empty_references": not row["references"],
            }
            file.write(json.dumps(record, ensure_ascii=False) + "\n")
            file.flush()
            if count % 50 == 0:
                print(f"{count} rows, {perf_counter() - started:.0f} s", flush=True)
    print(f"done in {perf_counter() - started:.0f} s", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    parser.add_argument("--units", type=Path)
    parser.add_argument("--cut-only", action="store_true")
    args = parser.parse_args()
    if args.cut_only:
        cut(args.output)
    else:
        run(args.output, args.limit, args.device, args.units)


if __name__ == "__main__":
    main()
