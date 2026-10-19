from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import locator_synthetic as ls  # noqa: E402

LEVELS = (5, 10, 15, 20, 25)


def candidates(sentence: str) -> list[tuple[int, int]]:
    return [m.span() for m in ls.WORDS.finditer(sentence) if any(c.isascii() and c.isalpha() for c in m.group())]


def next_letter(word: str) -> str:
    letters = [at for at, c in enumerate(word) if c.isascii() and c.isalpha()]
    at = letters[len(letters) // 2]
    base = "a" if word[at].islower() else "A"
    return word[:at] + chr(ord(base) + (ord(word[at]) - ord(base) + 1) % 26) + word[at + 1:]


def run_article(job: tuple[str, list[tuple[int, int]]]) -> list[dict]:
    stem, spans = job
    content = json.loads((ls.CASIE / f"{stem}.json").read_text(encoding="utf-8"))["content"]
    article_form = ls.letters_and_digits(content)
    rows = []
    for s, e in spans:
        sentence = content[s:e]
        words = len(ls.WORDS.findall(sentence))
        order = candidates(sentence)
        random.Random(f"{stem}:{s}").shuffle(order)
        for level in LEVELS:
            k = max(1, math.ceil(level * words / 100))
            row = {"article": stem, "s": s, "e": e, "level": level, "k": k, "words": words}
            if len(order) < k:
                rows.append({**row, "skipped": "fewer candidates than k"})
                continue
            chosen = sorted(order[:k])
            quote, shift, edits = sentence, 0, []
            for a, b in chosen:
                old = sentence[a:b]
                new = next_letter(old)
                quote = quote[:a + shift] + new + quote[b + shift:]
                shift += len(new) - len(old)
                edits.append({"a": s + a, "b": s + b, "old": old, "new": new})
            row.update({"quote": quote, "edits": edits,
                        "edited_share": round(sum(x["b"] - x["a"] for x in edits) / len(sentence), 4)})
            if ls.letters_and_digits(quote) in article_form:
                rows.append({**row, "skipped": "letters and digits still in the article"})
                continue
            row["verified_by"] = ls.located_by(content, quote)
            if not row["verified_by"]:
                row.update(ls.pointed(content, quote))
                if row["pointer"]:
                    length = len(row["passage"])
                    row["right_place"] = any(at < e and at + length > s for at in row["at"])
                    row["covers_every_edit"] = all(
                        any(at <= x["a"] and at + length >= x["b"] for at in row["at"]) for x in edits)
                    named = [any(x["new"] in ls.words(w) and x["old"] in ls.words(src) for w, src in row["places"])
                             for x in edits]
                    row["every_edit_named"], row["some_edit_named"] = all(named), any(named)
            row.pop("at", None)
            rows.append(row)
    return rows


def summarise(rows: list[dict]) -> dict:
    report = {}
    for level in LEVELS:
        mine = [r for r in rows if r["level"] == level]
        used = [r for r in mine if "skipped" not in r]
        report[f"{level}%"] = {
            "samples": len(used),
            "skipped": dict(Counter(r["skipped"] for r in mine if "skipped" in r)),
            "mean k": round(sum(r["k"] for r in used) / len(used), 2) if used else None,
            "mean edited share of characters": round(sum(r["edited_share"] for r in used) / len(used), 4)
            if used else None,
            "verified (must be 0)": ls.interval(used, lambda r: bool(r["verified_by"]), lambda r: True),
            "pointer": ls.interval(used, lambda r: r.get("pointer"), lambda r: not r["verified_by"]),
            "right place": ls.interval(used, lambda r: r.get("right_place"), lambda r: r.get("pointer")),
            "covers every edit": ls.interval(used, lambda r: r.get("covers_every_edit"), lambda r: r.get("pointer")),
            "every edit named": ls.interval(used, lambda r: r.get("every_edit_named"), lambda r: r.get("pointer")),
            "some edit named": ls.interval(used, lambda r: r.get("some_edit_named"), lambda r: r.get("pointer")),
            "places": dict(sorted(Counter(len(r["places"]) for r in used if r.get("pointer")).items())),
            "no pointer, by reason": dict(Counter(r["reason"] for r in used if "reason" in r)),
        }
    return report


def shown(cell: list) -> str:
    hits, total, value, low, high = cell
    return "–" if value is None else f"{value:.3f} [{low:.3f}, {high:.3f}] ({hits}/{total})"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", required=True)
    parser.add_argument("--split", choices=("development", "confirmation"), required=True)
    parser.add_argument("--workers", type=int, default=7)
    args = parser.parse_args()
    spans: dict[str, list[tuple[int, int]]] = defaultdict(list)
    log = HERE / "results" / f"locator_synthetic_{args.split}_edits.jsonl"
    for line in log.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row["kind"] == "N1":
            spans[row["article"]].append((row["s"], row["e"]))
    with ProcessPoolExecutor(args.workers, initializer=ls.backend, initargs=(args.backend,)) as pool:
        rows = [row for part in pool.map(run_article, sorted(spans.items()), chunksize=4) for row in part]
    out = HERE / "results" / f"locator_sweep_{args.split}_edits.jsonl"
    out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    report = summarise(rows)
    script = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    log_hash = hashlib.sha256(out.read_bytes()).hexdigest()
    md = [f"# Near-match pointer: scattered word edits by share ({args.split})", "",
          f"Script sha256 `{script}`. Edit log sha256 `{log_hash}`. Backend `{args.backend}`. No model call.", "",
          "| Level | Samples | Mean words edited | Verified (must be 0) | Pointer | Right place | Covers every edit | "
          "Every edit named | Some edit named |", "|---|---|---|---|---|---|---|---|---|"]
    for level, r in report.items():
        md.append(f"| {level} | {r['samples']} | {r['mean k']} | {shown(r['verified (must be 0)'])} | "
                  f"{shown(r['pointer'])} | {shown(r['right place'])} | {shown(r['covers every edit'])} | "
                  f"{shown(r['every edit named'])} | {shown(r['some edit named'])} |")
    md += ["", "## No pointer, by reason, and places", ""]
    md += [f"- {level}: {r['no pointer, by reason']}; places {r['places']}; skipped {r['skipped']}"
           for level, r in report.items()]
    (HERE / "results" / f"locator_sweep_{args.split}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (HERE / "results" / f"locator_sweep_{args.split}.json").write_text(
        json.dumps({"script": script, "edit_log": log_hash, **report}, indent=1, ensure_ascii=False), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
