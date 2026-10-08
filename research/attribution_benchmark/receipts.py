from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from research.attribution_benchmark.data import sha256

REPOSITORY = Path(__file__).resolve().parents[2]


def now() -> str:
    return datetime.now(UTC).isoformat()


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()


def save(path: Path, value: object) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def git_receipt() -> dict:
    def git(*args):
        return subprocess.check_output(
            ["git", *args], cwd=REPOSITORY, text=True, encoding="utf-8"
        ).strip()

    return {
        "head": git("rev-parse", "HEAD"),
        "branch": git("branch", "--show-current"),
        "status": git("status", "--short"),
    }


def source_receipt() -> dict:
    paths = [
        "research/attribution_benchmark/data.py",
        "research/attribution_benchmark/propagation_data.py",
        "research/attribution_benchmark/propagation_judgement.py",
        "research/attribution_benchmark/propagation_metrics.py",
        "research/attribution_benchmark/run_propagation.py",
        "research/attribution_benchmark/receipts.py",
        "research/attribution_benchmark/propagation_execution.py",
        "research/attribution_benchmark/champion.py",
        "research/attribution_benchmark/b1_cache_manifest.json",
        "backend/app/trace/b1_lr.json",
        "backend/app/analysis/write.py",
        "backend/app/analysis/prompts.py",
        "backend/app/trace/claims.py",
        "backend/app/trace/citations.py",
        "backend/app/trace/evidence_binding.py",
        "backend/app/trace/trace.py",
        "backend/app/trace/summary.py",
        "backend/app/sources/evidence.py",
        "backend/app/llm/request.py",
        "backend/app/llm/settings.py",
    ]
    return {path: sha256(REPOSITORY / path) for path in paths}
