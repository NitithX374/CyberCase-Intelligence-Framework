from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

from .protocol import (
    build_b0_prompt,
    format_for,
    instruction_text,
    language_for,
    normalize_choice_output,
)
from .selection import load_jsonl, parse_category_counts, selected_english, selection_manifest


DATASET_COMMIT = "a84b86aabf2b5be35a2cbbac546511883cc5ff85"
MODEL = "meta-llama/llama-3.1-8b-instruct"
DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
GENERATION_CONFIG = {"temperature": 0, "top_p": 1, "max_tokens": 512}
TRANSIENT_STATUS_CODES = {408, 429, 500, 502, 503, 504}


class RequestFailure(RuntimeError):
    def __init__(self, message: str, metadata: dict[str, Any]) -> None:
        super().__init__(message)
        self.metadata = metadata


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def completed_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    records = load_jsonl(path)
    ids: set[str] = set()
    for record in records:
        sample_id = str(record.get("sample_id", ""))
        if not sample_id or sample_id in ids:
            raise ValueError(f"Duplicate or missing sample_id in {path}: {sample_id}")
        if record.get("condition") != "B0" or record.get("provider") != "openrouter":
            raise ValueError(f"Output is not an OpenRouter B0 file: {path}")
        if record.get("requested_model") != MODEL or record.get("language") != "EN":
            raise ValueError(f"Output contract mismatch for sample {sample_id}: {path}")
        ids.add(sample_id)
    return ids


def retry_delay(response: httpx.Response | None, attempt: int, base: float) -> float:
    if response is not None:
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                return min(60.0, max(0.0, float(retry_after)))
            except ValueError:
                pass
    return min(30.0, base * (2 ** (attempt - 1)))


def response_error(response: httpx.Response) -> str:
    try:
        payload = response.json()
        error = payload.get("error", payload) if isinstance(payload, dict) else payload
        return json.dumps(error, ensure_ascii=False)[:1000]
    except (json.JSONDecodeError, ValueError):
        return response.text[:1000]


def request_prediction(
    client: httpx.Client,
    prompt: str,
    sample_id: str,
    max_attempts: int,
    backoff_base: float,
) -> tuple[str, str, str, dict[str, Any]]:
    attempts: list[dict[str, Any]] = []
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        **GENERATION_CONFIG,
    }
    for attempt in range(1, max_attempts + 1):
        requested_at = utc_now()
        started = time.perf_counter()
        response: httpx.Response | None = None
        try:
            response = client.post("/chat/completions", json=payload)
            latency_ms = round((time.perf_counter() - started) * 1000, 3)
            attempt_record = {"attempt": attempt, "timestamp": requested_at, "status_code": response.status_code, "latency_ms": latency_ms}
            attempts.append(attempt_record)
            if response.status_code in TRANSIENT_STATUS_CODES:
                attempt_record["error"] = response_error(response)
                if attempt < max_attempts:
                    time.sleep(retry_delay(response, attempt, backoff_base))
                    continue
                raise RequestFailure("transient OpenRouter error exhausted retry budget", {"attempts": attempts})
            if not 200 <= response.status_code < 300:
                attempt_record["error"] = response_error(response)
                raise RequestFailure(f"permanent OpenRouter HTTP {response.status_code}", {"attempts": attempts})
            data = response.json()
            choices = data.get("choices") if isinstance(data, dict) else None
            content = choices[0].get("message", {}).get("content") if choices else None
            if not isinstance(content, str):
                attempt_record["error"] = "missing textual completion"
                if attempt < max_attempts:
                    time.sleep(retry_delay(response, attempt, backoff_base))
                    continue
                raise RequestFailure("OpenRouter returned no textual completion", {"attempts": attempts})
            metadata = {
                "sample_idempotency_key": sample_id,
                "response_id": data.get("id"),
                "created": data.get("created"),
                "finish_reason": choices[0].get("finish_reason"),
                "usage": data.get("usage", {}),
                "openrouter_metadata": data.get("openrouter_metadata", {}),
                "system_fingerprint": data.get("system_fingerprint"),
                "service_tier": data.get("service_tier"),
                "attempts": attempts,
            }
            return content, str(data.get("model", "")), requested_at, metadata
        except (httpx.TimeoutException, httpx.RequestError) as exc:
            attempts.append({"attempt": attempt, "timestamp": requested_at, "error": f"{type(exc).__name__}: {exc}"})
            if attempt < max_attempts:
                time.sleep(retry_delay(response, attempt, backoff_base))
                continue
            raise RequestFailure("OpenRouter network error exhausted retry budget", {"attempts": attempts}) from exc
        except json.JSONDecodeError as exc:
            attempts[-1]["error"] = f"JSONDecodeError: {exc}"
            if attempt < max_attempts:
                time.sleep(retry_delay(response, attempt, backoff_base))
                continue
            raise RequestFailure("OpenRouter returned invalid JSON", {"attempts": attempts}) from exc
    raise RequestFailure("OpenRouter retry loop ended unexpectedly", {"attempts": attempts})


def normalized_prediction(row: dict[str, Any], raw: str) -> str | None:
    if format_for(row) == "choice":
        return normalize_choice_output(raw)
    return raw.strip()


def base_record(row: dict[str, Any], base_url: str, key_env: str) -> dict[str, Any]:
    return {
        "sample_id": str(row["id"]),
        "category": row["category"],
        "language": "EN",
        "format": format_for(row),
        "task": row["task"],
        "condition": "B0",
        "provider": "openrouter",
        "requested_model": MODEL,
        "dataset_commit": DATASET_COMMIT,
        "instruction": instruction_text(row),
        "input": row["input"],
        "prompt": build_b0_prompt(row),
        "generation_config": GENERATION_CONFIG,
        "api_config": {"base_url": base_url, "api_key_env": key_env},
    }


def write_record(handle: Any, record: dict[str, Any]) -> None:
    handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    handle.flush()
    os.fsync(handle.fileno())


def seed_records(path: Path | None, selected_ids: set[str]) -> dict[str, dict[str, Any]]:
    if path is None:
        return {}
    completed_ids(path)
    records = {str(record["sample_id"]): record for record in load_jsonl(path)}
    return {sample_id: record for sample_id, record in records.items() if sample_id in selected_ids}


def run(args: argparse.Namespace) -> None:
    api_key = os.getenv(args.api_key_env, "").strip()
    if not api_key:
        raise RuntimeError(f"Missing OpenRouter key in {args.api_key_env}")
    category_counts = parse_category_counts(args.category_count)
    rows = selected_english(load_jsonl(args.dataset), args.limit, category_counts)
    if args.selection_output:
        args.selection_output.parent.mkdir(parents=True, exist_ok=True)
        args.selection_output.write_text(json.dumps(selection_manifest(rows, category_counts), ensure_ascii=False, indent=2), encoding="utf-8")
    target = args.output.with_suffix(args.output.suffix + ".force.tmp") if args.force else args.output
    existing = set() if args.force else completed_ids(target)
    seeds = seed_records(args.seed_predictions, {str(row["id"]) for row in rows})
    target.parent.mkdir(parents=True, exist_ok=True)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-OpenRouter-Metadata": "enabled",
        "HTTP-Referer": "https://github.com/CyberCase-Intelligence-Framework",
        "X-Title": "CyberCase SEvenLLM Pilot-1",
    }
    mode = "w" if args.force else "a"
    with httpx.Client(base_url=args.base_url.rstrip("/"), headers=headers, timeout=args.timeout) as client, target.open(mode, encoding="utf-8") as handle:
        for index, row in enumerate(rows, start=1):
            sample_id = str(row["id"])
            if sample_id in existing:
                continue
            if sample_id in seeds:
                write_record(handle, seeds[sample_id])
                existing.add(sample_id)
                print(f"B0 OpenRouter: reused id={sample_id}", flush=True)
                continue
            record = base_record(row, args.base_url.rstrip("/"), args.api_key_env)
            try:
                raw, returned_model, requested_at, metadata = request_prediction(client, record["prompt"], sample_id, args.max_attempts, args.backoff_base)
                record.update({"returned_model": returned_model, "request_timestamp": requested_at, "prediction_raw": raw, "prediction_normalized": normalized_prediction(row, raw), "request_metadata": metadata, "error": None})
            except RequestFailure as exc:
                record.update({"returned_model": "", "request_timestamp": utc_now(), "prediction_raw": "", "prediction_normalized": None, "request_metadata": exc.metadata, "error": {"type": type(exc).__name__, "message": str(exc)}})
            write_record(handle, record)
            print(f"B0 OpenRouter: {index}/{len(rows)} id={sample_id} error={record['error'] is not None}", flush=True)
    if args.force:
        target.replace(args.output)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--api-key-env", default="OPENROUTER_API_KEY")
    parser.add_argument("--base-url", default=os.getenv("OPENROUTER_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--max-attempts", type=int, default=5)
    parser.add_argument("--backoff-base", type=float, default=1.0)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--category-count", action="append", default=[])
    parser.add_argument("--selection-output", type=Path)
    parser.add_argument("--seed-predictions", type=Path)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.max_attempts < 1 or args.backoff_base < 0:
        raise ValueError("Retry configuration is invalid")
    run(args)


if __name__ == "__main__":
    main()
