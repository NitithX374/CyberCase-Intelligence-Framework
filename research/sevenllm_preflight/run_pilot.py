from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from .protocol import SELECTED_CATEGORIES, build_mt5_input, language_for, metadata_for


DATASET_COMMIT = "a84b86aabf2b5be35a2cbbac546511883cc5ff85"
B1_NAME = "google/mt5-base"
B1_REVISION = "2eb15465c5dd7f72a8f7984306ad05ebc3dd1e1f"
MAX_NEW_TOKENS = 512


def load_rows(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def english_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected = [row for row in rows if row.get("category") in SELECTED_CATEGORIES and language_for(row) == "en"]
    if len(selected) != 300:
        raise ValueError(f"Pilot-1 requires exactly 300 English rows, found {len(selected)}")
    if any(language_for(row) != "en" for row in selected):
        raise ValueError("Pilot-1 contains a non-English row")
    return sorted(selected, key=lambda row: int(row["id"]))


def tokenized_input(tokenizer: Any, prompt: str) -> dict[str, torch.Tensor]:
    return tokenizer(
        prompt,
        return_tensors="pt",
        truncation=False,
        add_special_tokens=True,
    )


def load_model(model_dir: Path, device: torch.device) -> tuple[Any, Any]:
    tokenizer = AutoTokenizer.from_pretrained(model_dir, use_fast=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_dir, dtype=torch.float32, low_cpu_mem_usage=True)
    model.to(device)
    model.eval()
    return tokenizer, model


def generate_prediction(tokenizer: Any, model: Any, row: dict[str, Any], device: torch.device) -> tuple[str, str, int]:
    semantic = build_mt5_input(row)
    encoded = tokenized_input(tokenizer, semantic)
    input_length = int(encoded["input_ids"].shape[-1])
    encoded = {key: value.to(device) for key, value in encoded.items()}
    with torch.inference_mode():
        generated = model.generate(
            **encoded,
            do_sample=False,
            num_beams=1,
            max_new_tokens=MAX_NEW_TOKENS,
        )
    generated = generated[0]
    return semantic, tokenizer.decode(generated, skip_special_tokens=True).strip(), input_length


def write_predictions(rows: list[dict[str, Any]], model_dir: Path, output_path: Path, device: torch.device) -> None:
    tokenizer, model = load_model(model_dir, device)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for index, row in enumerate(rows, start=1):
            semantic, prediction, input_tokens = generate_prediction(tokenizer, model, row, device)
            record = {
                **metadata_for(row),
                "model_key": "B1",
                "model": B1_NAME,
                "model_revision": B1_REVISION,
                "tokenizer_revision": B1_REVISION,
                "precision": "float32",
                "device": str(device),
                "generation": {"do_sample": False, "num_beams": 1, "max_new_tokens": MAX_NEW_TOKENS},
                "semantic_prompt": semantic,
                "rendered_prompt": semantic,
                "input_tokens": input_tokens,
                "raw_prediction": prediction,
            }
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            handle.flush()
            if index == 1 or index % 10 == 0 or index == len(rows):
                print(f"B1: {index}/{len(rows)} id={row['id']}", flush=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", choices=("cpu", "cuda"), required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA was requested but is not available")
    rows = english_rows(load_rows(args.dataset))
    write_predictions(rows, args.model_dir, args.output, torch.device(args.device))


if __name__ == "__main__":
    main()
