import json
import statistics
import sys
import time
from pathlib import Path

NL = chr(10)
PER_LANGUAGE = 20
REPEATS = 3


def read_inputs(path: str) -> list[dict]:
    text = Path(path).read_text(encoding="utf-8")
    return [json.loads(row) for row in text.split(NL) if row.strip()]


def main(input_path: str, out_path: str) -> None:
    from pythainlp.tokenize import sent_tokenize
    from wtpsplit import SaT

    sat = SaT("sat-3l-sm")
    engines = {
        "sat": lambda line: sat.split(line),
        "crfcut": lambda line: sent_tokenize(line, engine="crfcut"),
    }
    docs = read_inputs(input_path)
    for engine in engines.values():
        engine(docs[0]["text"][:500])
    rows = []
    summary = {}
    for lang in ["th", "en"]:
        chosen = [doc for doc in docs if doc["lang"] == lang][:PER_LANGUAGE]
        totals = {}
        for name, engine in engines.items():
            best_total = 0.0
            median_total = 0.0
            for doc in chosen:
                runs = []
                for _ in range(REPEATS):
                    began = time.perf_counter()
                    engine(doc["text"])
                    runs.append(time.perf_counter() - began)
                rows.append({"id": doc["id"], "lang": lang, "engine": name, "chars": len(doc["text"]), "seconds": [round(v, 4) for v in runs]})
                best_total += min(runs)
                median_total += statistics.median(runs)
                print(f"{lang} {name} {doc['id']} {len(doc['text'])} {min(runs):.3f}", file=sys.stderr, flush=True)
            chars = sum(len(doc["text"]) for doc in chosen)
            totals[name] = {
                "docs": len(chosen),
                "chars": chars,
                "ms_per_1000_chars_min_of_repeats": round(best_total / chars * 1e6, 1),
                "ms_per_1000_chars_median_of_repeats": round(median_total / chars * 1e6, 1),
            }
        totals["sat_over_crfcut_min"] = round(
            totals["sat"]["ms_per_1000_chars_min_of_repeats"] / totals["crfcut"]["ms_per_1000_chars_min_of_repeats"], 1
        )
        summary[lang] = totals
    payload = {"repeats": REPEATS, "per_language": PER_LANGUAGE, "summary": summary, "rows": rows}
    Path(out_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
