from __future__ import annotations

import argparse
import json
from pathlib import Path

from .b2_config import (
    B2_GRADIENT_ACCUMULATION_STEPS,
    B2_SAVE_STEPS,
    B2_TRAIN_BATCH_SIZE,
)
from .b2_training import run_training


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train SEvenLLM B2 on a passing local preflight")
    parser.add_argument("--preflight-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--cache-dir", type=Path)
    parser.add_argument("--resume-from-checkpoint", type=Path)
    parser.add_argument("--resume-latest", action="store_true")
    parser.add_argument("--per-device-train-batch-size", type=int, default=B2_TRAIN_BATCH_SIZE)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=B2_GRADIENT_ACCUMULATION_STEPS)
    parser.add_argument("--save-steps", type=int, default=B2_SAVE_STEPS)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.per_device_train_batch_size < 1 or args.gradient_accumulation_steps < 1 or args.save_steps < 1:
        raise ValueError("batch size, gradient accumulation, and save steps must be positive")
    result = run_training(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
