from __future__ import annotations

import argparse
import os
from pathlib import Path

from research.sevenllm_preflight.run_openrouter_b0 import DEFAULT_BASE_URL

from .constants import DEFAULT_B0_CACHE, DEFAULT_GLINER_MODEL, DEFAULT_OUTPUT_DIR, DEFAULT_SBERT_MODEL, SEED
from .dataset import DEFAULT_BENCHMARK, DEFAULT_SELECTION
from .runner import run_experiment


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the frozen SEvenLLM B0/B1/B2 representation comparison")
    parser.add_argument("--benchmark", type=Path, default=DEFAULT_BENCHMARK)
    parser.add_argument("--selection", type=Path, default=DEFAULT_SELECTION)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--b0-cache", type=Path, default=DEFAULT_B0_CACHE)
    parser.add_argument("--gliner-model", default=DEFAULT_GLINER_MODEL)
    parser.add_argument("--gliner-device", choices=("cpu", "cuda"), default="cpu")
    parser.add_argument("--gliner-threshold", type=float, default=0.5)
    parser.add_argument("--sbert-model", default=DEFAULT_SBERT_MODEL)
    parser.add_argument("--sbert-device", choices=("cpu", "cuda"), default="cpu")
    parser.add_argument("--api-key-env", default="OPENROUTER_API_KEY")
    parser.add_argument("--base-url", default=os.getenv("OPENROUTER_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--max-attempts", type=int, default=5)
    parser.add_argument("--backoff-base", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=SEED)
    return parser


def main(argv: list[str] | None = None) -> None:
    run_experiment(build_parser().parse_args(argv))
