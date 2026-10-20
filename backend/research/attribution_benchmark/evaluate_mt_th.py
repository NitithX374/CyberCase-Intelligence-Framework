from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from time import perf_counter

from app.trace.b1_verifier import (
    ARTIFACT_SHA256,
    ClaimVerification,
    supported_probability,
)

from research.attribution_benchmark.champion import load_champion
from research.attribution_benchmark.data import read_split
from research.attribution_benchmark.paired_statistics import confusion, mcnemar
from research.attribution_benchmark.receipts import digest, save
from research.attribution_benchmark.translate_th import plan, read_cache
from research.attribution_benchmark.verifier_runtime import (
    load_runtime,
    peak_vram_bytes,
)


def run(translations: Path, output: Path, *, device="cpu"):
    examples, texts = plan()
    cached = read_cache(translations / "translations.jsonl")
    if not set(texts) <= cached.keys():
        raise ValueError(
            "Complete official MT cache required; no partial transfer result"
        )
    output.mkdir(parents=True, exist_ok=True)
    verifier, runtime = load_runtime(device)
    runtime_path = output / "runtime.json"
    if (
        runtime_path.exists()
        and json.loads(runtime_path.read_text(encoding="utf-8")) != runtime
    ):
        raise ValueError("Research execution runtime changed during paired evaluation")
    save(runtime_path, runtime)
    score_path = output / "scores.jsonl"
    scores = {}
    if score_path.exists():
        for line in score_path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            if row["artifact_sha256"] != ARTIFACT_SHA256:
                raise ValueError("Frozen verifier changed during resumable evaluation")
            if row["id"] in scores:
                raise ValueError("Duplicate saved score")
            scores[row["id"]] = row
    english = {
        split: load_champion(split, read_split(split)) for split in ("test", "test_ood")
    }
    with score_path.open("a", encoding="utf-8") as file:
        for example in examples:
            claim = cached[example["claim_key"]]["translation"]
            units = [cached[key]["translation"] for key in example["unit_keys"]]
            input_hash = digest([claim, units, example])
            if example["id"] in scores:
                if scores[example["id"]]["input_sha256"] != input_hash:
                    raise ValueError(
                        "Saved Thai input differs from paired original row"
                    )
                continue
            en_claim = texts[example["claim_key"]]
            en_units = [texts[key] for key in example["unit_keys"]]
            results = {}
            for language, hypothesis, source in (
                ("en", en_claim, en_units),
                ("th", claim, units),
            ):
                started = perf_counter()
                if source:
                    result = verifier.verify(hypothesis, source)
                else:
                    nli = verifier.nli.predict("", hypothesis)
                    result = ClaimVerification(
                        nli, supported_probability(nli.vector), (), (), 0
                    )
                results[language] = {
                    **asdict(result),
                    "duration_ms": (perf_counter() - started) * 1000,
                }
            record = {
                **example,
                "input_sha256": input_hash,
                "artifact_sha256": ARTIFACT_SHA256,
                **results,
                "archived_en_p_supported": english[example["split"]].scores[
                    example["id"]
                ]["p_supported"],
                "en_supported": results["en"]["p_supported"] >= 0.5,
                "th_supported": results["th"]["p_supported"] >= 0.5,
                "empty_source": not units,
                "empty_source_policy": "Research scores the empty premise identically to EN; production withholds structurally"
                if not units
                else None,
            }
            file.write(json.dumps(record, ensure_ascii=False) + "\n")
            file.flush()
            scores[example["id"]] = record
    summary = {
        "artifact_sha256": ARTIFACT_SHA256,
        "rows": len(scores),
        "scope": "Paired machine-translated transfer; label invariance assumed, no human Thai gold or tuning",
        "runtime": runtime,
        "peak_vram_bytes": peak_vram_bytes(device),
    }
    for split in ("test", "test_ood"):
        rows = [
            scores[example["id"]] for example in examples if example["split"] == split
        ]
        gold = [int(row["gold"] == "attributable") for row in rows]
        en = [row["en_supported"] for row in rows]
        th = [row["th_supported"] for row in rows]
        archived = [row["archived_en_p_supported"] >= 0.5 for row in rows]
        summary[split] = {
            "en": confusion(gold, en),
            "th": confusion(gold, th),
            "archived_en": confusion(gold, archived),
            "archived_en_decision_differences": sum(
                a != b for a, b in zip(en, archived, strict=True)
            ),
            "paired_correctness": mcnemar(
                [p == y for p, y in zip(en, gold, strict=True)],
                [p == y for p, y in zip(th, gold, strict=True)],
            ),
            "empty_source_rows": sum(row["empty_source"] for row in rows),
        }
    save(output / "summary.json", summary)
    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Frozen B1-LR paired EN/MT-TH; no training or tuning"
    )
    parser.add_argument("--translations", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    args = parser.parse_args()
    print(json.dumps(run(args.translations, args.output, device=args.device)))


if __name__ == "__main__":
    main()
