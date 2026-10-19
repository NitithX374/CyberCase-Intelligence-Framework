from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

import book_scores as bs

CURRENT = "main_20261001_021428"
CONFIGURED = {"prose": (bs.DESIGN, "prose"), "one call": (bs.DESIGN, "single"),
              "two calls": (bs.DESIGN, "cybercase"), "current": (CURRENT, "cybercase_nogrammar")}
TRACED = ("one call", "two calls", "current")
DRAWS = 200
NL = chr(10)


def cases(views: dict, x: str, y: str, completed: bool = False) -> list[str]:
    ids = sorted(set(views[x]) & set(views[y]))
    return [c for c in ids if views[x][c]["done"] and views[y][c]["done"]] if completed else ids


def shown(result: tuple[float, float, float]) -> str:
    return f"{bs.signed(result[0])} [{bs.signed(result[1])}, {bs.signed(result[2])}]"


def verdict(result: tuple[float, float, float]) -> str:
    return "excludes 0" if result[1] > 0 or result[2] < 0 else "includes 0"


def spans_of(view: dict) -> list[tuple[int, int]]:
    text = view["case"]["text"]
    return [p for claim in view["trace"]["claims"] for q in bs.quotes_of(claim) for p in bs.positions(text, q)]


def m4_from(case: dict, spans: list[tuple[int, int]]) -> float:
    return bs.share(bs.pointed_at(fact, spans) for fact in bs.lead(case))


def quoted_share(view: dict) -> float:
    covered = np.zeros(len(view["case"]["text"]), dtype=bool)
    for a, b in spans_of(view):
        covered[a:b] = True
    return float(covered.mean())


def chance_m4(view: dict) -> float:
    text, spans = view["case"]["text"], spans_of(view)
    rng = np.random.default_rng(2026)
    total = 0.0
    for _ in range(DRAWS):
        moved = []
        for a, b in spans:
            start = int(rng.integers(0, len(text) - (b - a) + 1))
            moved.append((start, start + b - a))
        total += m4_from(view["case"], moved)
    return total / DRAWS


def cut(text: str, n: int) -> str:
    return " ".join(text.split()[:n])


def matched(views: dict, a: str, b: str, metric) -> tuple[list[str], dict, dict, list[int]]:
    both = cases(views, a, b, True)
    da, db, kept = {}, {}, []
    for c in both:
        ta, tb, case = views[a][c]["text"], views[b][c]["text"], views[a][c]["case"]
        n = min(len(ta.split()), len(tb.split()))
        kept.append(n)
        da[c], db[c] = metric(cut(ta, n), case), metric(cut(tb, n), case)
    return both, da, db, kept


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    views, scores = bs.analysis(CONFIGURED, TRACED)

    volume = {}
    for label in TRACED:
        actual, chance, adjusted, share = {}, {}, {}, []
        for c, v in views[label].items():
            if not v["done"]:
                actual[c] = chance[c] = adjusted[c] = 0.0
                continue
            actual[c] = m4_from(v["case"], spans_of(v))
            if abs(actual[c] - scores[label]["m4"][c]) > 1e-12:
                raise SystemExit(f"M4 not reproduced: {label} {c}")
            chance[c] = chance_m4(v)
            adjusted[c] = actual[c] - chance[c]
            share.append(quoted_share(v))
        volume[label] = {"m4": actual, "chance": chance, "adjusted": adjusted, "share": share}

    steps = (("one call", "prose", (("M5 V0", "m5"), ("M5-std", "m5std"))),
             ("two calls", "one call", (("M4", "m4"), ("M4b", "m4b"), ("M5 V0", "m5"), ("M5-std", "m5std"))),
             ("current", "two calls", (("M4", "m4"), ("M4b", "m4b"), ("M5 V0", "m5"), ("M5-std", "m5std"))))
    step_rows = []
    for later, earlier, metrics in steps:
        every, both = cases(views, earlier, later), cases(views, earlier, later, True)
        for name, key in metrics:
            a, b = scores[earlier][key], scores[later][key]
            step_rows.append({"pair": f"{later} − {earlier}", "metric": name, "cases": len(every),
                              "completed_in_both": len(both), "failures_0": list(bs.mean_difference(a, b, every)),
                              "completed": list(bs.mean_difference(a, b, both))})

    words = {label: float(np.mean([len(v["text"].split()) for v in views[label].values() if v["done"]]))
             for label in CONFIGURED}
    length_rows = []
    for later, earlier in (("current", "prose"), ("current", "one call"), ("one call", "prose")):
        for name, metric in (("M5 V0", bs.m5_v0), ("M5-std", bs.m5_std)):
            both, da, db, kept = matched(views, earlier, later, metric)
            full = bs.mean_difference(scores[earlier]["m5" if name == "M5 V0" else "m5std"],
                                      scores[later]["m5" if name == "M5 V0" else "m5std"], both)
            length_rows.append({"pair": f"{later} − {earlier}", "metric": name, "cases": len(both),
                                "mean_words_kept": float(np.mean(kept)), "full": list(full),
                                "matched": list(bs.mean_difference(da, db, both))})

    volume_rows = []
    for later, earlier in (("current", "one call"), ("two calls", "one call"), ("current", "two calls")):
        every, both = cases(views, earlier, later), cases(views, earlier, later, True)
        for name, key in (("M4", "m4"), ("chance M4", "chance"), ("adjusted M4", "adjusted")):
            a, b = volume[earlier][key], volume[later][key]
            volume_rows.append({"pair": f"{later} − {earlier}", "metric": name, "cases": len(every),
                                "completed_in_both": len(both), "failures_0": list(bs.mean_difference(a, b, every)),
                                "completed": list(bs.mean_difference(a, b, both))})

    arms = {label: {"words": words[label]} for label in CONFIGURED}
    for label in TRACED:
        done = [c for c, v in views[label].items() if v["done"]]
        arms[label].update(quoted_share=float(np.mean(volume[label]["share"])),
                           m4_completed=float(np.mean([volume[label]["m4"][c] for c in done])),
                           chance_m4_completed=float(np.mean([volume[label]["chance"][c] for c in done])),
                           adjusted_m4_completed=float(np.mean([volume[label]["adjusted"][c] for c in done])))

    here = Path(__file__).resolve()
    out = {"script_sha256": hashlib.sha256(here.read_bytes()).hexdigest(), "current_run": CURRENT, "draws": DRAWS,
           "arms": arms, "steps": step_rows, "length": length_rows, "volume": volume_rows}
    (bs.HERE / "results" / "heldout_controls.json").write_text(json.dumps(out, indent=1), encoding="utf-8")

    md = ["# Held-out controls: step intervals, length and quoted volume", "",
          f"Script sha256 `{out['script_sha256']}`. Cases 51-150; current = `{CURRENT}`, the other arms "
          f"`{bs.DESIGN}`. Bootstrap as book_scores (2,000 case resamples, seed 2026). No model call.", "",
          "## Arms", "", "| Arm | Mean words (own text) | Quoted share of the article | M4 | Chance M4 | Adjusted M4 |",
          "|---|---|---|---|---|---|"]
    for label, a in arms.items():
        if label in TRACED:
            md.append(f"| {label} | {a['words']:.0f} | {a['quoted_share']:.3f} | {a['m4_completed']:.3f} | "
                      f"{a['chance_m4_completed']:.3f} | {a['adjusted_m4_completed']:.3f} |")
        else:
            md.append(f"| {label} | {a['words']:.0f} | - | - | - | - |")
    md += ["", "M4, chance and adjusted M4 in this table are means over completed cases.", "",
           "## 1. Step intervals", "", "| Pair | Metric | Failures 0 (n) | Completed in both (n) | Interval |",
           "|---|---|---|---|---|"]
    for r in step_rows:
        md.append(f"| {r['pair']} | {r['metric']} | {shown(r['failures_0'])} ({r['cases']}) | "
                  f"{shown(r['completed'])} ({r['completed_in_both']}) | {verdict(r['failures_0'])} |")
    md += ["", "## 2. Length control (completed in both; both texts cut to the shorter one's word count)", "",
           "| Pair | Metric | Cases | Mean words kept | Full length | Matched length | Matched interval |",
           "|---|---|---|---|---|---|---|"]
    for r in length_rows:
        md.append(f"| {r['pair']} | {r['metric']} | {r['cases']} | {r['mean_words_kept']:.0f} | {shown(r['full'])} | "
                  f"{shown(r['matched'])} | {verdict(r['matched'])} |")
    md += ["", f"## 3. Quoted-volume control (chance M4: every quote position moved to a random start, {DRAWS} draws)",
           "", "| Pair | Metric | Failures 0 (n) | Completed in both (n) | Interval |", "|---|---|---|---|---|"]
    for r in volume_rows:
        md.append(f"| {r['pair']} | {r['metric']} | {shown(r['failures_0'])} ({r['cases']}) | "
                  f"{shown(r['completed'])} ({r['completed_in_both']}) | {verdict(r['failures_0'])} |")
    (bs.HERE / "results" / "heldout_controls.md").write_text(NL.join(md) + NL, encoding="utf-8")
    print(NL.join(md))


if __name__ == "__main__":
    main()
