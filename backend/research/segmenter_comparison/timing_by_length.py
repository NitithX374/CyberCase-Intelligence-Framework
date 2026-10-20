import json
import math
import statistics
import sys
import time
from pathlib import Path

NL = chr(10)
LENGTHS = [250, 500, 1000, 2000, 4000]
DOCS_PER_LANGUAGE = 5
REPEATS = 3
BLOCK_SIZE = 512
STRIDE = 64


def read_inputs(path: str) -> list[dict]:
    text = Path(path).read_text(encoding="utf-8")
    return [json.loads(row) for row in text.split(NL) if row.strip()]


def model_chunks(token_count: int) -> tuple[int, int]:
    block = min(BLOCK_SIZE, token_count)
    if block > 510:
        block = 510
    chunks = math.ceil(max(token_count - block, 0) / STRIDE) + 1
    return chunks, chunks * (block + 2)


def main(input_path: str, out_path: str) -> None:
    from pythainlp.tokenize import sent_tokenize
    from wtpsplit import SaT

    sat = SaT("sat-3l-sm")
    tokenizer = sat.tokenizer
    engines = {
        "sat": lambda line: sat.split(line),
        "crfcut": lambda line: sent_tokenize(line, engine="crfcut"),
    }
    docs = read_inputs(input_path)
    for engine in engines.values():
        engine(docs[0]["text"][:500])
    rows = []
    for lang in ["th", "en"]:
        chosen = [doc for doc in docs if doc["lang"] == lang and len(doc["text"]) >= max(LENGTHS)][:DOCS_PER_LANGUAGE]
        for doc in chosen:
            for length in LENGTHS:
                line = doc["text"][:length]
                tokens = len(tokenizer(line, add_special_tokens=False)["input_ids"])
                chunks, positions = model_chunks(tokens)
                row = {"id": doc["id"], "lang": lang, "chars": length, "xlmr_tokens": tokens, "sat_chunks": chunks, "sat_token_positions": positions}
                for name, engine in engines.items():
                    runs = []
                    for _ in range(REPEATS):
                        began = time.perf_counter()
                        engine(line)
                        runs.append(time.perf_counter() - began)
                    row[name + "_seconds"] = [round(v, 4) for v in runs]
                rows.append(row)
                print(lang, doc["id"], length, tokens, chunks, min(row["sat_seconds"]), min(row["crfcut_seconds"]), file=sys.stderr, flush=True)
    summary = {}
    for lang in ["th", "en"]:
        summary[lang] = {}
        for length in LENGTHS:
            group = [row for row in rows if row["lang"] == lang and row["chars"] == length]
            chars = sum(row["chars"] for row in group)
            summary[lang][str(length)] = {
                "docs": len(group),
                "median_xlmr_tokens": statistics.median(row["xlmr_tokens"] for row in group),
                "sat_token_positions_per_1000_chars": round(sum(row["sat_token_positions"] for row in group) / chars * 1000, 1),
                "sat_ms_per_1000_chars_min": round(sum(min(row["sat_seconds"]) for row in group) / chars * 1e6, 1),
                "crfcut_ms_per_1000_chars_min": round(sum(min(row["crfcut_seconds"]) for row in group) / chars * 1e6, 1),
            }
    payload = {"lengths": LENGTHS, "repeats": REPEATS, "block_size": BLOCK_SIZE, "stride": STRIDE, "summary": summary, "rows": rows}
    Path(out_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
