import importlib.metadata
import json
import os
import platform
import statistics
import sys
import time
from pathlib import Path

NL = chr(10)
MIN_SENTENCE_CHARS = 25
WARMUP_DOCS = 2
WARMUP_CHARS = 500

tokenize_sentences = None


def line_spans(text: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    start = 0
    for line in text.splitlines(keepends=True):
        content = line.splitlines()[0] if line.splitlines() else ""
        if content.strip():
            spans.append((start, start + len(content)))
        start += len(line)
    return spans


def line_sentences(text: str, start: int, end: int) -> list[tuple[int, int]]:
    segment_text = text[start:end]
    pieces = tokenize_sentences(segment_text)
    if "".join(pieces) != segment_text:
        return [stripped(text, start, end)]
    spans: list[tuple[int, int]] = []
    held_start, at = start, start
    for piece in pieces:
        at += len(piece)
        if len(text[held_start:at].strip()) >= MIN_SENTENCE_CHARS:
            spans.append((held_start, at))
            held_start = at
    if text[held_start:at].strip():
        if spans:
            spans[-1] = (spans[-1][0], at)
        else:
            spans.append((held_start, at))
    return [stripped(text, span_start, span_end) for span_start, span_end in spans]


def stripped(text: str, start: int, end: int) -> tuple[int, int]:
    piece = text[start:end]
    return start + len(piece) - len(piece.lstrip()), end - len(piece) + len(piece.rstrip())


def versions() -> dict[str, str]:
    found = {}
    for package in ["wtpsplit", "pythainlp", "python-crfsuite", "torch", "transformers", "numpy", "huggingface-hub"]:
        try:
            found[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            found[package] = "missing"
    return found


def cpu_model() -> str:
    try:
        for row in Path("/proc/cpuinfo").read_text().split(NL):
            if row.startswith("model name"):
                return row.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor()


def skip_space(text: str, position: int) -> int:
    while position < len(text) and text[position].isspace():
        position += 1
    return position


def raw_boundaries(text: str, start: int, pieces: list[str]) -> list[int]:
    found = []
    at = start
    for piece in pieces[:-1]:
        at += len(piece)
        found.append(skip_space(text, at))
    return found


def agreement(first: set[int], second: set[int]) -> dict[str, float | int]:
    shared = len(first & second)
    total = len(first) + len(second)
    return {
        "sat_boundaries": len(first),
        "crfcut_boundaries": len(second),
        "shared": shared,
        "agreement_f1": round(2 * shared / total, 4) if total else 1.0,
    }


def read_inputs(path: str) -> list[dict]:
    text = Path(path).read_text(encoding="utf-8")
    return [json.loads(row) for row in text.split(NL) if row.strip()]


def main(input_path: str, out_dir: str) -> None:
    global tokenize_sentences
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    import torch
    from pythainlp.tokenize import sent_tokenize

    loaded_at = time.perf_counter()
    from wtpsplit import SaT

    sat = SaT("sat-3l-sm")
    sat_load_seconds = time.perf_counter() - loaded_at

    engines = {
        "sat": lambda line: sat.split(line),
        "crfcut": lambda line: sent_tokenize(line, engine="crfcut"),
    }

    docs = read_inputs(input_path)
    languages = sorted({doc["lang"] for doc in docs})
    warmup = [doc["text"][:WARMUP_CHARS] for lang in languages for doc in [d for d in docs if d["lang"] == lang][:WARMUP_DOCS]]
    for engine in engines.values():
        for text in warmup:
            engine(text)

    per_doc = []
    began_run = time.perf_counter()
    for index, doc in enumerate(docs, 1):
        text = doc["text"]
        spans = line_spans(text)
        record = {"id": doc["id"], "lang": doc["lang"], "chars": len(text), "lines": len(spans)}
        for name, engine in engines.items():
            cached: dict[str, list[str]] = {}
            boundaries: list[int] = []
            pieces_total = 0
            rejoin_failures = 0
            seconds = 0.0
            for start, end in spans:
                began = time.perf_counter()
                pieces = engine(text[start:end])
                seconds += time.perf_counter() - began
                cached[text[start:end]] = pieces
                pieces_total += len(pieces)
                if "".join(pieces) != text[start:end]:
                    rejoin_failures += 1
                    continue
                boundaries.extend(raw_boundaries(text, start, pieces))
            tokenize_sentences = cached.__getitem__
            units = [span for start, end in spans for span in line_sentences(text, start, end)]
            record[name] = {
                "seconds": round(seconds, 4),
                "pieces": pieces_total,
                "rejoin_failed_lines": rejoin_failures,
                "boundaries": boundaries,
                "unit_starts": [start for start, _ in units],
                "unit_lengths": [end - start for start, end in units],
            }
        per_doc.append(record)
        if index % 10 == 0:
            print(f"{index}/{len(docs)} docs, {time.perf_counter() - began_run:.0f} s", file=sys.stderr, flush=True)

    summary = {}
    for lang in languages:
        group = [record for record in per_doc if record["lang"] == lang]
        chars = sum(record["chars"] for record in group)
        entry = {"docs": len(group), "chars": chars, "lines": sum(record["lines"] for record in group)}
        for name in engines:
            lengths = [length for record in group for length in record[name]["unit_lengths"]]
            seconds = sum(record[name]["seconds"] for record in group)
            entry[name] = {
                "raw_pieces_per_1000_chars": round(sum(r[name]["pieces"] for r in group) / chars * 1000, 2),
                "rejoin_failed_lines": sum(r[name]["rejoin_failed_lines"] for r in group),
                "units_per_1000_chars": round(len(lengths) / chars * 1000, 2),
                "median_unit_chars": statistics.median(lengths),
                "mean_unit_chars": round(statistics.fmean(lengths), 1),
                "total_seconds": round(seconds, 2),
                "ms_per_1000_chars": round(seconds / chars * 1000 * 1000, 1),
                "median_doc_ms_per_1000_chars": round(
                    statistics.median(r[name]["seconds"] / r["chars"] * 1000 * 1000 for r in group), 1
                ),
            }
        entry["raw_boundary_agreement"] = agreement(
            {(r["id"], b) for r in group for b in r["sat"]["boundaries"]},
            {(r["id"], b) for r in group for b in r["crfcut"]["boundaries"]},
        )
        entry["unit_start_agreement"] = agreement(
            {(r["id"], b) for r in group for b in r["sat"]["unit_starts"][1:]},
            {(r["id"], b) for r in group for b in r["crfcut"]["unit_starts"][1:]},
        )
        summary[lang] = entry

    environment = {
        "python": sys.version,
        "platform": platform.platform(),
        "cpu": cpu_model(),
        "cpu_count": os.cpu_count(),
        "torch_threads": torch.get_num_threads(),
        "packages": versions(),
        "sat_model": "sat-3l-sm",
        "sat_threshold_argument": None,
        "crfcut_call": "pythainlp.tokenize.sent_tokenize(line, engine='crfcut')",
        "sat_load_seconds": round(sat_load_seconds, 2),
        "hf_hub_offline": os.environ.get("HF_HUB_OFFLINE"),
        "hf_home": os.environ.get("HF_HOME"),
        "min_sentence_chars": MIN_SENTENCE_CHARS,
        "warmup": f"{WARMUP_DOCS} docs per language, first {WARMUP_CHARS} characters, untimed",
        "timing": "one timed call per line per engine; the same call's pieces feed the unit and boundary counts",
        "input": input_path,
    }
    (out / "summary.json").write_text(
        json.dumps({"environment": environment, "summary": summary}, indent=2), encoding="utf-8"
    )
    (out / "per_doc.jsonl").write_text(
        NL.join(json.dumps(record, ensure_ascii=True) for record in per_doc) + NL, encoding="utf-8"
    )
    print(json.dumps({"environment": environment, "summary": summary}, indent=2))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
