from __future__ import annotations

import argparse
import platform
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

from research.projection_validation.runtime import (
    HERE,
    ROOT,
    file_digest,
    initialize,
    read_json,
    read_rows,
    write_json,
    write_rows,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--nli-path", type=Path, required=True)
    parser.add_argument("--threads", type=int)
    parser.add_argument("--output", type=Path, default=HERE / "results/local")
    args = parser.parse_args()
    args.nli_path = args.nli_path.resolve()
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(output)
    initialize()
    import torch

    from app.config import settings
    from app.trace import nli_model

    from research.projection_validation.evaluation import (
        cost_metrics,
        eligibility_diagnostics,
        evaluate_cases,
    )
    from research.projection_validation.measurement import MeasuredScorer
    from research.projection_validation.metrics import summary_tables
    from research.projection_validation.structural import structural_evaluation

    manifest = read_json(HERE / "data/manifest.json")
    assert file_digest(HERE / "data/benchmark.jsonl") == manifest["benchmark_sha256"]
    cases = read_rows(HERE / "data/benchmark.jsonl")
    write_json(output / "structural.json", structural_evaluation())
    configured_path = settings.quote_meaning_pointer_path
    configured_load = nli_model.load_nli
    nli_model.forget()
    try:
        configured_scorer = MeasuredScorer(nli_model.load_nli())
        configured_status = "available"
    except nli_model.NliUnavailable as error:
        configured_status = error.reason
        configured_scorer = None

    def configured_provider():
        if configured_scorer is not None:
            return configured_scorer
        return configured_load()

    configured_rows, configured_cost, _ = evaluate_cases(
        cases, configured_provider, configured_scorer
    )
    write_rows(output / "configured_predictions.jsonl", configured_rows)
    write_json(
        output / "configured_summary.json",
        {
            "path": configured_path,
            "status": configured_status,
            "metrics": summary_tables(configured_rows),
            "cost": cost_metrics(configured_rows, configured_cost, configured_scorer),
        },
    )
    default_threads = torch.get_num_threads()
    if args.threads is not None:
        torch.set_num_threads(args.threads)
    settings.quote_meaning_pointer_path = str(args.nli_path)
    nli_model.forget()
    started = perf_counter()
    scorer = MeasuredScorer(nli_model.load_nli())
    load_seconds = perf_counter() - started
    parameter = next(scorer.scorer.model.parameters())
    rows, costs, readings = evaluate_cases(cases, lambda: scorer, scorer)
    write_rows(output / "predictions.jsonl", rows)
    write_rows(output / "case_receipts.jsonl", costs)
    write_rows(output / "grounded_readings.jsonl", readings)
    metrics = summary_tables(rows)
    metrics["cost"] = cost_metrics(rows, costs, scorer)
    write_json(output / "metrics.json", metrics)
    write_json(
        output / "eligibility_diagnostics.json",
        eligibility_diagnostics(scorer_claim(readings), scorer),
    )
    write_json(
        output / "run.json",
        {
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "benchmark_sha256": manifest["benchmark_sha256"],
            "production_baseline": read_json(
                ROOT / "tmp/projection-validation/baseline.json"
            )["head"],
            "model": scorer.name,
            "weights_sha256": nli_model.WEIGHTS_SHA256,
            "nli_path": str(args.nli_path),
            "configured_path": configured_path,
            "default_threads": default_threads,
            "measured_threads": torch.get_num_threads(),
            "device": str(parameter.device),
            "dtype": str(parameter.dtype),
            "cuda_available": torch.cuda.is_available(),
            "peak_cuda_vram_bytes": None,
            "model_load_seconds": load_seconds,
            "threshold": 0.5,
            "max_tokens": 512,
            "platform": platform.platform(),
            "torch": torch.__version__,
            "source_code_sha256": {
                path.name: file_digest(path) for path in sorted(HERE.glob("*.py"))
            },
        },
    )
    print(
        "COMPLETED", output, metrics["quality"]["overall"], metrics["cost"], flush=True
    )


def scorer_claim(readings: list[dict]):
    from app.trace.claims import CaseAnalysisClaim

    return CaseAnalysisClaim.model_validate(readings[0]["reading"]["claims"][0])


if __name__ == "__main__":
    main()
