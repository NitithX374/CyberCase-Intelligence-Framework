from __future__ import annotations

import argparse
import os
from pathlib import Path

from research.sevenllm_preflight.run_openrouter_b0 import DEFAULT_BASE_URL

from .compressor import DEFAULT_COMPRESSOR_MODEL, DEFAULT_COMPRESSION_RATE
from .dataset import DEFAULT_BENCHMARK, DEFAULT_SELECTION, PROJECT_ROOT
from .runner import report_existing, run_experiment


def _common_data_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--benchmark", type=Path, default=DEFAULT_BENCHMARK)
    parser.add_argument("--selection", type=Path, default=DEFAULT_SELECTION)
    parser.add_argument("--output-dir", type=Path, default=PROJECT_ROOT / "tmp" / "context_refinement")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the isolated SEvenLLM context-refinement ablation")
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run", help="run raw, refined, or paired conditions")
    _common_data_arguments(run)
    run.add_argument("--condition", choices=("raw", "refined", "both"), default="both")
    run.add_argument("--compressor-model", default=DEFAULT_COMPRESSOR_MODEL)
    run.add_argument("--compression-rate", type=float, default=DEFAULT_COMPRESSION_RATE)
    run.add_argument("--compressor-device", choices=("cpu", "cuda"))
    run.add_argument("--sbert-model")
    run.add_argument("--sbert-device", choices=("cpu", "cuda"), default="cpu")
    run.add_argument("--api-key-env", default="OPENROUTER_API_KEY")
    run.add_argument("--base-url", default=os.getenv("OPENROUTER_BASE_URL", DEFAULT_BASE_URL))
    run.add_argument("--timeout", type=float, default=120.0)
    run.add_argument("--max-attempts", type=int, default=5)
    run.add_argument("--backoff-base", type=float, default=1.0)
    run.add_argument("--seed", type=int, default=42)
    report = commands.add_parser("report", help="rebuild paired artifacts from completed predictions")
    _common_data_arguments(report)
    report.add_argument("--sbert-model", required=True)
    report.add_argument("--sbert-device", choices=("cpu", "cuda"), default="cpu")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    if args.command == "run":
        run_experiment(args)
    else:
        report_existing(args)
