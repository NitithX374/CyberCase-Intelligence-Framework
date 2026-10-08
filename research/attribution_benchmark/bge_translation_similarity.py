from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from time import perf_counter

from research.attribution_benchmark.bge_similarity_report import write_results
from research.attribution_benchmark.bge_similarity_runtime import (
    MAX_LENGTH,
    cosine_pairs,
    file_hash,
    load_model,
    pair_batches,
    token_lengths,
)
from research.attribution_benchmark.receipts import digest, now, save
from research.attribution_benchmark.translate_th import plan, read_cache


def paired_inputs(translations: Path):
    examples, texts = plan()
    cached = read_cache(translations / "translations.jsonl")
    if not set(texts) <= cached.keys():
        raise ValueError("Complete matched original/translated cache required")
    roles = defaultdict(set)
    for example in examples:
        roles[example["claim_key"]].add("claim")
        for key in example["unit_keys"]:
            roles[key].add("source_unit")
    pairs = {}
    for key, original in texts.items():
        if cached[key]["source"] != original:
            raise ValueError("Original translation pair changed")
        pairs[key] = {
            "key": key,
            "source": original,
            "translation": cached[key]["translation"],
            "roles": sorted(roles[key]),
        }
    return examples, pairs


def read_scores(path: Path, pairs: dict, manifest_hash: str) -> dict:
    scores = {}
    if not path.exists():
        return scores
    for line in path.read_text(encoding="utf-8").splitlines():
        score = json.loads(line)
        key = score["key"]
        if key not in pairs or key in scores:
            raise ValueError("Unknown or duplicate scored pair")
        if score["contract_sha256"] != manifest_hash or score["pair_sha256"] != digest(
            pairs[key]
        ):
            raise ValueError("Scored pair input/runtime identity changed")
        if not -1 <= score["cosine"] <= 1:
            raise ValueError("Invalid saved cosine")
        scores[key] = score
    return scores


def run(args):
    import torch

    examples, pairs = paired_inputs(args.translations)
    args.output.mkdir(parents=True, exist_ok=True)
    score_path = args.output / "scores.jsonl"
    manifest_path = args.output / "manifest.json"
    if manifest_path.exists() and not args.resume:
        raise ValueError("Existing run requires explicit --resume")
    print(json.dumps({"phase": "load_pinned_model", "pairs": len(pairs)}), flush=True)
    model, runtime = load_model(args.model_path, args.device, args.precision)
    root = Path(__file__).resolve().parents[2]
    contract = {
        "runtime": runtime,
        "input": {
            "rows": len(examples),
            "unique_text_pairs": len(pairs),
            "dataset_manifest_sha256": file_hash(
                root / "research/attribution_benchmark/data/manifest.json"
            ),
            "translations_sha256": file_hash(args.translations / "translations.jsonl"),
            "paired_inputs_sha256": digest(pairs),
            "mapping": "Original English segmentation; same cached Thai Claim and Source units in original order",
        },
        "pairs_per_batch": args.pairs_per_batch,
        "padded_token_budget": args.token_budget,
        "code_sha256": {
            name: file_hash(Path(__file__).with_name(name))
            for name in (
                "bge_translation_similarity.py",
                "bge_similarity_runtime.py",
                "bge_similarity_report.py",
            )
        },
    }
    contract_hash = digest(contract)
    if manifest_path.exists():
        previous = json.loads(manifest_path.read_text(encoding="utf-8"))
        if previous["contract_sha256"] != contract_hash:
            raise ValueError(
                "Input/model/runtime/method changed; cannot resume this run"
            )
    scores = read_scores(score_path, pairs, contract_hash)
    manifest = {
        **contract,
        "contract_sha256": contract_hash,
        "status": "running",
        "started_at": now(),
    }
    save(manifest_path, manifest)
    started = perf_counter()
    try:
        lengths = token_lengths(model.tokenizer, pairs)
        print(
            json.dumps(
                {
                    "phase": "encode",
                    "pending": len(pairs) - len(scores),
                    "max_tokens": max(max(value) for value in lengths.values()),
                }
            ),
            flush=True,
        )
        pending = [key for key in pairs if key not in scores]
        with score_path.open("a", encoding="utf-8") as file:
            for batch in pair_batches(
                pending, lengths, args.pairs_per_batch, args.token_budget
            ):
                texts = [
                    pairs[key][language]
                    for key in batch
                    for language in ("source", "translation")
                ]
                batch_started = perf_counter()
                vectors = model.encode(
                    texts,
                    batch_size=len(texts),
                    normalize_embeddings=True,
                    convert_to_numpy=True,
                    show_progress_bar=False,
                )
                similarities = cosine_pairs(vectors)
                elapsed = (perf_counter() - batch_started) * 1_000
                for key, score in zip(batch, similarities, strict=True):
                    en_length, th_length = lengths[key]
                    record = {
                        "key": key,
                        "pair_sha256": digest(pairs[key]),
                        "contract_sha256": contract_hash,
                        "cosine": float(score),
                        "en_tokens": en_length,
                        "th_tokens": th_length,
                        "en_truncated": en_length > MAX_LENGTH,
                        "th_truncated": th_length > MAX_LENGTH,
                        "batch_pairs": len(batch),
                        "batch_elapsed_ms": elapsed,
                    }
                    file.write(json.dumps(record, ensure_ascii=False) + "\n")
                    scores[key] = record
                file.flush()
                if len(scores) % 1024 < len(batch) or len(scores) == len(pairs):
                    print(
                        json.dumps(
                            {
                                "completed": len(scores),
                                "total": len(pairs),
                                "elapsed_seconds": round(perf_counter() - started, 2),
                            }
                        ),
                        flush=True,
                    )
        if (
            file_hash(args.translations / "translations.jsonl")
            != contract["input"]["translations_sha256"]
        ):
            raise ValueError("Translation cache changed during scoring")
        manifest.update(
            {
                "status": "complete",
                "finished_at": now(),
                "elapsed_seconds_this_attempt": perf_counter() - started,
                "completed_pairs": len(scores),
                "peak_allocated_vram_bytes": torch.cuda.max_memory_allocated()
                if args.device == "cuda"
                else None,
            }
        )
        summary = write_results(args.output, examples, pairs, scores, manifest)
        save(manifest_path, manifest)
        print(
            json.dumps(
                {
                    "status": "complete",
                    "output": str(args.output),
                    "unique_text_pairs": summary["unique_text_pairs"],
                }
            ),
            flush=True,
        )
        return summary
    except BaseException as error:
        manifest.update(
            {
                "status": "failed",
                "finished_at": now(),
                "completed_pairs": len(scores),
                "error_type": type(error).__name__,
                "error": str(error),
            }
        )
        save(manifest_path, manifest)
        raise


def main():
    parser = argparse.ArgumentParser(
        description="Pinned local BGE-M3 paired original EN / cached MT-TH cosine similarity"
    )
    parser.add_argument("--translations", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--device", choices=("cpu", "cuda"), required=True)
    parser.add_argument("--precision", choices=("float16", "float32"), required=True)
    parser.add_argument("--pairs-per-batch", type=int, default=32)
    parser.add_argument("--token-budget", type=int, default=8192)
    parser.add_argument("--resume", action="store_true")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
