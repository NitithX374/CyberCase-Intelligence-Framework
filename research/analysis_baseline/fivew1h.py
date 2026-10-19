from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SEED, RESAMPLES, TAU = 2026, 2000, 0.85
RUN, ARM = "main_20261001_021428", "cybercase_nogrammar"
SLOT = {"Victim": "who_affected", "Attacker": "who_responsible", "Compromised-Data": "what", "Time": "when",
        "Place": "where", "Tool": "how", "Payment-Method": "how", "Trusted-Entity": "how", "Price": "how_much",
        "Damage-Amount": "how_much", "Number-of-Victim": "how_much", "Number-of-Data": "how_much"}
SLOTS = ("who_affected", "who_responsible", "what", "when", "where", "how", "how_much")


def share(pairs: dict[str, list[int]]) -> list:
    counts = np.array([v for v in pairs.values() if v[1]], dtype=float)
    if not len(counts):
        return [0, 0, None, None, None]
    picks = np.random.default_rng(SEED).integers(0, len(counts), size=(RESAMPLES, len(counts)))
    sums = counts[picks].sum(axis=1)
    rates = sums[:, 0] / np.maximum(sums[:, 1], 1)
    hits, total = int(counts[:, 0].sum()), int(counts[:, 1].sum())
    return [hits, total, round(hits / total, 4), round(float(np.percentile(rates, 2.5)), 4),
            round(float(np.percentile(rates, 97.5)), 4)]


def shown(cell: list) -> str:
    return "–" if cell[2] is None else f"{cell[2]:.3f} [{cell[3]:.3f}, {cell[4]:.3f}] ({cell[0]}/{cell[1]})"


def similarity(job: tuple[str, list[str]]) -> list[tuple[float, float]]:
    from rapidfuzz import fuzz

    text, quotes = job
    folded = re.sub(r"\s+", " ", text.casefold()).strip()
    return [(fuzz.partial_ratio(q, text) / 100, fuzz.partial_ratio(re.sub(r"\s+", " ", q.casefold()).strip(), folded)
             / 100) for q in quotes]


def keyed_edits() -> dict:
    import locator_synthetic as ls

    rows = [json.loads(line) for line in
            (HERE / "results" / "locator_synthetic_confirmation_edits.jsonl").read_text(encoding="utf-8").splitlines()]
    rows = [r for r in rows if r["kind"] in ls.CONTENT_EDITS and not r.get("unchanged") and r.get("role") in SLOT]
    by_article = defaultdict(list)
    for r in rows:
        by_article[r["article"]].append(r)
    jobs = [(json.loads((ls.CASIE / f"{a}.json").read_text(encoding="utf-8"))["content"], [r["quote"] for r in rs])
            for a, rs in by_article.items()]
    with ProcessPoolExecutor() as pool:
        for rs, scores in zip(by_article.values(), pool.map(similarity, jobs, chunksize=8)):
            for r, (raw, folded) in zip(rs, scores):
                r["raw"], r["folded"] = raw, folded
    out = {}
    for slot in SLOTS:
        for label, keep in (("all content edits", lambda r: True), ("digit edits", lambda r: r["kind"] == "digit")):
            chosen = [r for r in rows if SLOT[r["role"]] == slot and keep(r)]
            if not chosen:
                continue
            cell = {}
            for name, hit, base in (
                    ("production accepts", lambda r: bool(r["verified_by"]), lambda r: True),
                    ("partial_ratio >= 0.85 accepts", lambda r: r["raw"] >= TAU, lambda r: True),
                    ("case-folded >= 0.85 accepts", lambda r: r["folded"] >= TAU, lambda r: True),
                    ("pointer right place", lambda r: bool(r.get("right_place")), lambda r: not r["verified_by"]),
                    ("pointer right difference", lambda r: bool(r.get("right_difference")),
                     lambda r: not r["verified_by"])):
                pairs = defaultdict(lambda: [0, 0])
                for r in chosen:
                    if base(r):
                        pairs[r["article"]][1] += 1
                        pairs[r["article"]][0] += int(hit(r))
                cell[name] = share(pairs)
            out[f"{slot} / {label}"] = cell
    return out


def summaries(backend: str) -> dict:
    sys.path.insert(0, backend)
    import app.trace.bind as bind

    if not Path(bind.__file__).resolve().is_relative_to(Path(backend).resolve()):
        raise SystemExit(f"wrong binder: {bind.__file__}")
    from scores_common import v0_words
    from summary_measures import matcher

    mentioned = matcher(v0_words, stemmed=True)
    cases = {json.loads(line)["id"]: json.loads(line)
             for line in (HERE / "data" / "cases.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()}
    counts = {slot: {k: defaultdict(lambda: [0, 0]) for k in ("ceiling", "coverage", "traceable")} for slot in SLOTS}
    for path in sorted((HERE / "results" / f"raw_{RUN}").glob(f"*_{ARM}_1.json")):
        written = json.loads(path.read_text(encoding="utf-8")).get("written")
        if not written:
            continue
        key = path.name.split("_")[0]
        text = cases[key]["text"]
        checked = []
        for claim in written["claims"]:
            quotes = [c["exact_quote"] for c in claim.get("supporting_citations", []) if c.get("exact_quote")]
            found = [q for q in quotes if bind.located_quote(text, q) is not None]
            if found:
                checked.append(" ".join([claim.get("text", ""), *found]))
        for fact in cases[key]["gold"]:
            slot = SLOT.get(fact["role"])
            if slot is None:
                continue
            in_checked = any(mentioned(t, fact) for t in checked)
            in_summary = mentioned(written["summary"], fact)
            for name, hit, base in (("ceiling", in_checked, True), ("coverage", in_summary, True),
                                    ("traceable", in_checked, in_summary)):
                if base:
                    counts[slot][name][key][1] += 1
                    counts[slot][name][key][0] += int(hit)
    return {slot: {name: share(pairs) for name, pairs in kinds.items()} for slot, kinds in counts.items()}


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(HERE))
    edits = keyed_edits()
    stored = summaries(args.backend)
    md = ["# 5W1H breakdown of the CASIE measures (confirmation)", "",
          f"Script sha256 `{hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}`. Keyed edits from the frozen "
          f"`c883e26` edit log; stored summaries `{RUN}` re-bound at `{args.backend}`. No model call.", "",
          "## 1. Keyed content edits", "",
          "| Slot / edits | production accepts | partial_ratio ≥ 0.85 accepts | case-folded ≥ 0.85 accepts | "
          "pointer right place | pointer right difference |", "|---|---|---|---|---|---|"]
    for name, cell in edits.items():
        md.append(f"| {name} | " + " | ".join(shown(c) for c in cell.values()) + " |")
    md += ["", "## 2. Stored summaries (100 cases, all events' gold facts, stemmed matcher)", "",
           "| Slot | in checked claims (ceiling) | in summary (coverage) | summary facts in checked claims |",
           "|---|---|---|---|"]
    for slot, cell in stored.items():
        md.append(f"| {slot} | {shown(cell['ceiling'])} | {shown(cell['coverage'])} | {shown(cell['traceable'])} |")
    (HERE / "results" / "fivew1h.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (HERE / "results" / "fivew1h.json").write_text(json.dumps({"edits": edits, "stored": stored}, indent=1),
                                                    encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
