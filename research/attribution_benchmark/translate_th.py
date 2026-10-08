from __future__ import annotations

import argparse
import html
import json
from datetime import UTC, datetime
from pathlib import Path
from time import monotonic, sleep

import httpx
from dotenv import dotenv_values

from research.attribution_benchmark.champion import row_units
from research.attribution_benchmark.data import read_split, verify_manifest
from research.attribution_benchmark.receipts import digest, save

ENDPOINT = "https://translation.googleapis.com/language/translate/v2"
ROOT = Path(__file__).resolve().parents[2]


class TranslationUnavailable(RuntimeError):
    def __init__(self, message: str, *, http_status: int | None = None):
        super().__init__(message)
        self.http_status = http_status


def plan() -> tuple[list[dict], dict[str, str]]:
    verify_manifest()
    examples, texts = [], {}
    for split in ("test", "test_ood"):
        for row in read_split(split):
            claim = row["claim"].strip()
            units = row_units(row)
            for text in (claim, *units):
                texts[digest(text)] = text
            examples.append(
                {
                    "split": split,
                    "id": row["id"],
                    "gold": row["attribution_label"],
                    "original_row_sha256": digest(row),
                    "claim_key": digest(claim),
                    "unit_keys": [digest(unit) for unit in units],
                    "reference_unit_counts": [
                        len(row_units({"references": [ref]}))
                        for ref in row["references"]
                    ],
                }
            )
    return examples, texts


def read_cache(path: Path) -> dict:
    if not path.exists():
        return {}
    entries = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if (
            row["key"] != digest(row["source"])
            or row["endpoint"] != ENDPOINT
            or row["model"] != "nmt"
            or row["source_language"] != "en"
            or row["target_language"] != "th"
        ):
            raise ValueError("Translation cache identity mismatch")
        if row["key"] in entries:
            raise ValueError("Duplicate cached translation")
        if not row["translation"].strip():
            raise ValueError("Blank translation")
        entries[row["key"]] = row
    return entries


def batches(texts: dict[str, str]):
    batch, size = [], 0
    for key, text in texts.items():
        if len(text.encode("utf-8")) > 90_000:
            raise ValueError(
                "An original unit exceeds the Translation Basic request limit"
            )
        if batch and (len(batch) >= 128 or size + len(text) > 5_000):
            yield batch
            batch, size = [], 0
        batch.append((key, text))
        size += len(text)
    if batch:
        yield batch


def translate(
    client: httpx.Client, key: str, batch: list[tuple[str, str]]
) -> list[str]:
    try:
        response = client.post(
            ENDPOINT,
            headers={"X-goog-api-key": key},
            json={
                "q": [text for _, text in batch],
                "source": "en",
                "target": "th",
                "format": "text",
                "model": "nmt",
            },
        )
    except httpx.HTTPError as error:
        raise TranslationUnavailable(
            f"Translation transport failed: {type(error).__name__}"
        ) from None
    try:
        data = response.json()
    except ValueError:
        raise TranslationUnavailable(
            f"Google Translation HTTP {response.status_code}: non-JSON response ({response.headers.get('content-type', 'unknown')})",
            http_status=response.status_code,
        ) from None
    if response.status_code != 200:
        reasons = [
            item.get("reason", "unknown")
            for item in data.get("error", {}).get("errors", [])
        ]
        raise TranslationUnavailable(
            f"Google Translation HTTP {response.status_code}: {reasons}",
            http_status=response.status_code,
        )
    translations = [
        html.unescape(item["translatedText"]) for item in data["data"]["translations"]
    ]
    if len(translations) != len(batch) or any(
        not text.strip() for text in translations
    ):
        raise TranslationUnavailable("Incomplete Google translation batch")
    return translations


def translate_with_attempts(client, key, batch, attempts, record):
    if not 1 <= attempts <= 3:
        raise ValueError("Explicit transient attempts must be 1..3")
    for attempt in range(1, attempts + 1):
        try:
            return translate(client, key, batch)
        except TranslationUnavailable as error:
            record(
                {
                    "attempt": attempt,
                    "batch_keys": [key for key, _ in batch],
                    "error": str(error),
                    "at": datetime.now(UTC).isoformat(),
                }
            )
            if error.http_status not in (502, 503, 504) or attempt == attempts:
                raise
            sleep(max(2**attempt, sum(len(text) for _, text in batch) / 5_000))
    raise RuntimeError("Translation attempt loop did not return")


def run(output: Path, *, execute: bool, transient_attempts=1):
    output.mkdir(parents=True, exist_ok=True)
    examples, texts = plan()
    cache_path = output / "translations.jsonl"
    cached = read_cache(cache_path)
    missing = {key: text for key, text in texts.items() if key not in cached}
    manifest = {
        "dataset": verify_manifest(),
        "rows": len(examples),
        "unique_texts": len(texts),
        "total_characters": sum(len(text) for text in texts.values()),
        "pending_characters": sum(len(text) for text in missing.values()),
        "cached_texts": len(cached),
        "endpoint": ENDPOINT,
        "model": "nmt",
        "source_language": "en",
        "target_language": "th",
        "characters_per_minute_limit": 300_000,
        "transient_attempts": transient_attempts,
        "selection": "All original ID/OOD rows; no gold selection or Thai tuning",
        "unit_mapping": "Translate each original English unit once; preserve reference/unit ordering and gold",
        "status": "prepared",
        "at": datetime.now(UTC).isoformat(),
    }
    save(output / "plan.json", examples)
    save(output / "manifest.json", manifest)
    if execute:
        key = dotenv_values(ROOT / ".env").get(
            "GOOGLE_TRANSLATE_API_KEY"
        ) or dotenv_values(ROOT / ".env").get("GOOGLE_API_KEY")
        if not key:
            raise TranslationUnavailable(
                "Google Translation key missing from project .env"
            )
        try:
            with (
                httpx.Client(timeout=60) as client,
                cache_path.open("a", encoding="utf-8") as file,
            ):
                next_call_at = monotonic()
                for batch in batches(missing):
                    sleep(max(0, next_call_at - monotonic()))
                    next_call_at = (
                        monotonic() + sum(len(text) for _, text in batch) / 5_000
                    )

                    def record_error(event):
                        with (output / "transient_errors.jsonl").open(
                            "a", encoding="utf-8"
                        ) as errors:
                            errors.write(json.dumps(event) + "\n")

                    translated = translate_with_attempts(
                        client, key, batch, transient_attempts, record_error
                    )
                    for (item_key, source), target in zip(
                        batch, translated, strict=True
                    ):
                        record = {
                            "key": item_key,
                            "source": source,
                            "translation": target,
                            "endpoint": ENDPOINT,
                            "model": "nmt",
                            "source_language": "en",
                            "target_language": "th",
                            "at": datetime.now(UTC).isoformat(),
                        }
                        file.write(json.dumps(record, ensure_ascii=False) + "\n")
                        cached[item_key] = record
                    file.flush()
                    manifest["pending_characters"] -= sum(
                        len(text) for _, text in batch
                    )
                    manifest.update(status="translating", cached_texts=len(cached))
                    save(output / "manifest.json", manifest)
        except TranslationUnavailable as error:
            manifest.update(status="blocked", error=str(error))
            save(output / "manifest.json", manifest)
            raise
        manifest.update(
            status="complete",
            cached_texts=len(cached),
            finished_at=datetime.now(UTC).isoformat(),
        )
        save(output / "manifest.json", manifest)
    return manifest


def main():
    parser = argparse.ArgumentParser(
        description="Resumable official Google MT-TH; prepare without API calls by default"
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--transient-attempts", type=int, choices=(1, 2, 3), default=1)
    args = parser.parse_args()
    print(
        json.dumps(
            run(
                args.output,
                execute=args.execute,
                transient_attempts=args.transient_attempts,
            ),
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
