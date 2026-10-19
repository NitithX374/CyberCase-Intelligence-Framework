from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import locator_synthetic as ls  # noqa: E402

SPLIT_AT = 64


def rapidfuzz_window(content: str, quote: str):
    import app.trace.quotes as quotes
    from rapidfuzz import fuzz
    from rapidfuzz.distance import Levenshtein

    window = fuzz.partial_ratio_alignment(quote, content)
    if window is None or window.dest_start >= window.dest_end:
        return None
    text = content[window.dest_start:window.dest_end]
    return quotes.Alignment(start=window.dest_start, end=window.dest_end,
                            edits=Levenshtein.distance(quote, text))


def occurrences(content: str, passage: str | None) -> list[int]:
    import app.trace.quotes as quotes

    return quotes.quote_occurrences(content, passage) if passage else []


def p1(content: str, quote: str) -> dict:
    import app.trace.quotes as quotes

    production = quotes.aligned_candidate
    quotes.aligned_candidate = rapidfuzz_window
    try:
        return ls.pointed(content, quote)
    finally:
        quotes.aligned_candidate = production


def judged(row: dict, outcome: dict, content: str) -> dict:
    if not outcome.get("pointer"):
        return {"pointer": False, "reason": outcome.get("reason")}
    length = len(outcome["passage"])
    at = outcome["at"]
    places = outcome["places"]
    result = {"pointer": True, "passage": outcome["passage"], "places": places}
    if "edits" in row:
        result["right_place"] = any(a < row["e"] and a + length > row["s"] for a in at)
        result["covers"] = all(any(a <= x["a"] and a + length >= x["b"] for a in at) for x in row["edits"])
        result["named"] = all(any(x["new"] in ls.words(w) and x["old"] in ls.words(s) for w, s in places)
                              for x in row["edits"])
    else:
        result["right_place"] = any(a < row["b"] and a + length > row["a"] for a in at)
        result["covers"] = any(a <= row["a"] and a + length >= row["b"] for a in at)
        result["named"] = ls.right_difference(row["kind"], {**row, "original": row["original"]}, places)
    return result


def run_article(job: tuple[str, list[dict]]) -> list[dict]:
    stem, rows = job
    content = json.loads((ls.CASIE / f"{stem}.json").read_text(encoding="utf-8"))["content"]
    out = []
    for row in rows:
        production = {"pointer": row.get("pointer"), "reason": row.get("reason"), "passage": row.get("passage"),
                      "places": row.get("places"), "at": occurrences(content, row.get("passage"))}
        out.append({"article": stem, "group": row["group"], "length": len(row["quote"]), "quote": row["quote"],
                    "P0": judged(row, production, content), "P1": judged(row, p1(content, row["quote"]), content)})
    return out


def load(split: str) -> dict[str, list[dict]]:
    jobs: dict[str, list[dict]] = defaultdict(list)
    for line in (HERE / "results" / f"locator_synthetic_{split}_edits.jsonl").read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row["kind"] in ls.CONTENT_EDITS and not row.get("unchanged") and not row["verified_by"]:
            jobs[row["article"]].append({**row, "group": row["kind"]})
    for line in (HERE / "results" / f"locator_sweep_{split}_edits.jsonl").read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if "skipped" not in row and not row["verified_by"]:
            jobs[row["article"]].append({**row, "group": f"sweep {row['level']}%"})
    return jobs


def cells(rows: list[dict], arm: str) -> dict:
    return {
        "pointer": ls.interval(rows, lambda r: r[arm]["pointer"], lambda r: True),
        "right place": ls.interval(rows, lambda r: r[arm].get("right_place"), lambda r: r[arm]["pointer"]),
        "difference named": ls.interval(rows, lambda r: r[arm].get("named"), lambda r: r[arm]["pointer"]),
        "covers": ls.interval(rows, lambda r: r[arm].get("covers"), lambda r: r[arm]["pointer"]),
    }


def shown(cell: list) -> str:
    hits, total, value, low, high = cell
    return "–" if value is None else f"{value:.3f} [{low:.3f}, {high:.3f}] ({hits}/{total})"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", required=True)
    parser.add_argument("--split", choices=("development", "confirmation"), required=True)
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()
    jobs = load(args.split)
    with ProcessPoolExecutor(args.workers, initializer=ls.backend, initargs=(args.backend,)) as pool:
        rows = [r for part in pool.map(run_article, sorted(jobs.items()), chunksize=4) for r in part]
    groups = [*ls.CONTENT_EDITS, *[f"sweep {p}%" for p in (5, 10, 15, 20, 25)]]
    report: dict = {}
    md = [f"# Pointer ablation: infix alignment (P0, production) vs RapidFuzz window only (P1), {args.split}", "",
          f"Script sha256 `{hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}`. Backend `{args.backend}`. "
          "No model call.", "",
          "| Group | Length | Arm | Pointer | Right place | Difference named | Covers argument / every edit |",
          "|---|---|---|---|---|---|---|"]
    for group in groups:
        for bucket, chosen in (("all", lambda r: True), (f"≤{SPLIT_AT}", lambda r: r["length"] <= SPLIT_AT),
                               (f">{SPLIT_AT}", lambda r: r["length"] > SPLIT_AT)):
            mine = [r for r in rows if r["group"] == group and chosen(r)]
            if not mine:
                continue
            for arm in ("P0", "P1"):
                c = cells(mine, arm)
                report[f"{group} | {bucket} | {arm}"] = c
                md.append(f"| {group} | {bucket} (n={len(mine)}) | {arm} | {shown(c['pointer'])} | "
                          f"{shown(c['right place'])} | {shown(c['difference named'])} | {shown(c['covers'])} |")
    disagree = [r for r in rows if r["P0"]["pointer"] and r["P1"]["pointer"]
                and (r["P0"]["right_place"] != r["P1"]["right_place"] or r["P0"]["named"] != r["P1"]["named"])]
    md += ["", f"## Both point, but disagree on place or difference ({len(disagree)})", ""]
    for r in disagree[:40]:
        md.append(f"- `{r['article']}` {r['group']}: «{r['quote'][:160]}»")
        for arm in ("P0", "P1"):
            md.append(f"  - {arm}: place {r[arm]['right_place']}, named {r[arm]['named']}; "
                      + "; ".join(f"«{w}» → «{s}»" for w, s in r[arm]["places"]))
    (HERE / "results" / f"locator_pointer_ablation_{args.split}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (HERE / "results" / f"locator_pointer_ablation_{args.split}.json").write_text(
        json.dumps({"disagreements": len(disagree), **report}, indent=1, ensure_ascii=False), encoding="utf-8")
    print("\n".join(md[:7 + len(report)]))


if __name__ == "__main__":
    main()
