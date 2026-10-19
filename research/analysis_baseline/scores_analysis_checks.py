"""Scores, analysis tables: Tables 5-11, 5-12, 5-13, 5-15 and 5-16 and the comparisons of section 5.4.2, each number
beside the value the book prints.
"""
from __future__ import annotations

from collections import Counter

import numpy as np

from scores_analysis import ARMS, TRACED, citing, mentions, stating
from scores_common import (
    CASES,
    average,
    frac,
    interval_row,
    lead,
    mean_difference,
    pooled,
    pooled_difference,
    quotes_of,
    row,
)

# ================================================================================================= DATA


def traceability_tables(scores: dict) -> None:
    book = {"one call": ("1,340/1,383 = 0.969", "1,399/1,424 = 0.982", "77/100"),
            "two calls": ("1,670/1,693 = 0.986", "1,779/1,803 = 0.987", "86/95"),
            "shipped": ("1,577/1,614 = 0.977", "1,649/1,668 = 0.989", "85/96"),
            "final": ("1,601/1,625 = 0.985", "1,677/1,704 = 0.984", "85/99")}
    for label, (b1, b2, b3) in book.items():
        x = scores[label]
        row("5-11", f"{label}: M1", frac(*pooled(x["m1"])), b1)
        row("5-11", f"{label}: M2", frac(*pooled(x["m2"])), b2)
        row("5-11", f"{label}: M3", frac(x["m3"], len(x["done"]), False), b3)
    m1s = [n / d for n, d in (pooled(scores[label]["m1"]) for label in TRACED)]
    m2s = [n / d for n, d in (pooled(scores[label]["m2"]) for label in TRACED)]
    row("5-11", "M1 range in the text", f"{min(m1s):.0%} to {max(m1s):.0%}", "97% to 99%")
    row("5-11", "M2 range in the text", f"{min(m2s):.1%} and {max(m2s):.1%}", "98.2% and 98.9%")

    book = {"prose": (None, None, "0.699", "0.767", "0.141 (100)"),
            "one call": ("0.805", "0.624", "0.771", "0.808", "0.151 (100)"),
            "two calls": ("0.872", "0.729", "0.793", "0.833", "0.159 (95)"),
            "shipped": ("0.888", "0.743", "0.825", "0.842", "0.111 (96)"),
            "final": ("0.928", "0.775", "0.847", "0.870", "0.102 (99)")}
    for label, (b4, b4b, b5, b5s, bfloor) in book.items():
        x = scores[label]
        if b4:
            row("5-12", f"{label}: M4", f"{average(x['m4']):.3f}", b4)
            row("5-12", f"{label}: M4b", f"{average(x['m4b']):.3f}", b4b)
        row("5-12", f"{label}: M5", f"{average(x['m5']):.3f}", b5)
        row("5-12", f"{label}: M5-std", f"{average(x['m5std']):.3f}", b5s)
        row("5-12", f"{label}: chance floor (cases)", f"{np.mean(x['floor']):.3f} ({len(x['floor'])})", bfloor)
    m4s = {label: average(scores[label]["m4"]) for label in TRACED}
    m4bs = {label: average(scores[label]["m4b"]) for label in TRACED}
    floors = [float(np.mean(scores[label]["floor"])) for label in ARMS]
    for label, b in zip(TRACED, ("0.805", "0.917", "0.925", "0.938"), strict=True):
        done = scores[label]["done"]
        row("5-12", f"{label}: M4 over completed cases", f"{np.mean([scores[label]['m4'][c] for c in done]):.3f}", b)
    row("5-12", "M4 range in the text", f"{min(m4s.values()):.1%} to {max(m4s.values()):.1%}", "80.5% to 92.8%")
    gaps = [m4s[label] - m4bs[label] for label in TRACED]
    row("5-12", "M4 minus M4b in the text", f"{min(gaps):.2f} to {max(gaps):.2f}", "0.14 to 0.18")
    row("5-12", "M4b range in the text", f"{min(m4bs.values()):.3f} to {max(m4bs.values()):.3f}", "0.624 to 0.775")
    row("5-12", "chance floor range in the text", f"{min(floors):.3f} to {max(floors):.3f}", "0.102 to 0.159")
    row("6.1.2", "final M4 and M4b as percentages", f"{m4s['final']:.1%} and {m4bs['final']:.1%}", "92.8% and 77.5%")
    drops = {}
    for label, b in (("two calls", "0.855"), ("shipped", "0.888"), ("final", "0.926")):
        without = average(scores[label]["m4_unstitched"])
        drops[label] = round(m4s[label], 3) - round(without, 3)
        row("5.4.2 binder", f"{label}: M4 without stitched quotes", f"{without:.3f}", b)
    row("5.4.2 binder", "two calls: M4 lowered by removing them", f"{drops['two calls']:.3f}", "0.017")
    row("5.4.2 binder", "shipped and final: M4 lowered by removing them",
        f"{drops['shipped']:.3f} and {drops['final']:.3f}", "0.002 or less",
        agrees=max(drops["shipped"], drops["final"]) <= 0.002 + 1e-9)


def comparisons(views: dict, scores: dict) -> None:
    def cases(x: str, y: str, completed: bool = False) -> list[str]:
        ids = sorted(set(views[x]) & set(views[y]))
        return [c for c in ids if views[x][c]["done"] and views[y][c]["done"]] if completed else ids

    books = {"5.4.2 design": ("one call", "two calls", "+0.019 [−0.012, +0.056]", "+0.005 [−0.015, +0.018]",
                              "+0.066 [−0.009, +0.142]", "+0.120 [+0.059, +0.180]", "+0.105 [+0.035, +0.172]",
                              "+0.151 [+0.090, +0.212]"),
             "5-13 decoding": ("shipped", "final", "+0.008 [−0.013, +0.042]", "−0.004 [−0.015, +0.005]",
                               "+0.041 [−0.010, +0.099]", None, "+0.032 [−0.019, +0.088]", None)}
    for table, (x, y, b1, b2, b4, b4_both, b4b, b4b_both) in books.items():
        a, b, every, both = scores[x], scores[y], cases(x, y), cases(x, y, True)
        interval_row(table, f"M1, {y} − {x}", pooled_difference(a["m1"], b["m1"], both), b1)
        interval_row(table, f"M2, {y} − {x}", pooled_difference(a["m2"], b["m2"], both), b2)
        interval_row(table, f"M4, {y} − {x}, failures 0", mean_difference(a["m4"], b["m4"], every), b4)
        if b4_both:
            interval_row(table, f"M4, {y} − {x}, completed in both", mean_difference(a["m4"], b["m4"], both), b4_both)
        interval_row(table, f"M4b, {y} − {x}, failures 0", mean_difference(a["m4b"], b["m4b"], every), b4b)
        if b4b_both:
            interval_row(table, f"M4b, {y} − {x}, completed in both", mean_difference(a["m4b"], b["m4b"], both),
                         b4b_both)
    interval_row("5-13 decoding", "M5-std, final − shipped",
                 mean_difference(scores["shipped"]["m5std"], scores["final"]["m5std"], cases("shipped", "final")),
                 "+0.028 [−0.012, +0.068]")
    for label, b in (("shipped", "0.977 0.989 0.888 0.743 0.842"), ("final", "0.985 0.984 0.928 0.775 0.870")):
        x = scores[label]
        values = (frac(*pooled(x["m1"])).split()[-1], frac(*pooled(x["m2"])).split()[-1], f"{average(x['m4']):.3f}",
                  f"{average(x['m4b']):.3f}", f"{average(x['m5std']):.3f}")
        row("5-13 decoding", f"{label}: M1, M2, M4, M4b, M5-std", " ".join(values), b)
    for x, y, b_std, b_v3 in (("prose", "two calls", "+0.067 [+0.016, +0.117]", "+0.064 [+0.010, +0.114]"),
                              ("prose", "one call", "+0.041 [−0.004, +0.090]", None),
                              ("one call", "two calls", "+0.025 [−0.037, +0.081]", "+0.016 [−0.044, +0.079]")):
        every = cases(x, y)
        interval_row("5.4.2 prose", f"M5-std, {y} − {x}",
                     mean_difference(scores[x]["m5std"], scores[y]["m5std"], every), b_std)
        if b_v3:
            interval_row("5.4.2 prose", f"V3, {y} − {x}",
                         mean_difference(scores[x]["v3"], scores[y]["v3"], every), b_v3)


def reliability(scores: dict) -> None:
    book = {"one call": "0 / 4 / 92 / 0.0032", "two calls": "5 / 25 / 170 / 0.0074",
            "shipped": "4 / 19 / 253 / 0.0067", "final": "1 / 4 / 136 / 0.0044"}
    for label, b in book.items():
        x = scores[label]
        row("5-15", f"{label}: failed / calls to the cap / median model s / USD per case",
            f"{x['failed']} / {x['capped']} / {x['seconds']:.0f} / {x['usd']:.4f}", b)
    shipped, final = scores["shipped"], scores["final"]
    row("5-13 decoding", "failed cases, shipped and final",
        f"{shipped['failed']}/{shipped['cases']} and {final['failed']}/{final['cases']}", "4/100 and 1/100")
    ratio = final["usd"] / shipped["usd"]
    row("5-15", "final USD over shipped USD", f"{ratio:.2f}", "about two thirds", agrees=abs(ratio - 2 / 3) < 0.05)


def worked_case(views: dict) -> None:
    case = CASES["10049"]
    two = views["two calls"]["10049"]["trace"]
    book = {"the attackers": "Attacker 741-754 yes yes yes A-06", "meta data": "Compromised-Data 786-795 no no no A-07",
            "21 february": "Time 768-779 yes yes yes A-06", "a file server": "Victim 831-844 yes yes yes A-07",
            "athlete tues": "Victim 799-811 no yes yes A-07",
            "athletes therapeutic use exemption tue applications": "Victim 243-297 no yes yes A-02",
            "iaaf servers": "Victim 308-320 no yes yes A-02", "the iaaf network": "Victim 721-737 no yes yes A-06"}
    totals, stated_and_cited = Counter(), 0
    for fact in lead(case):
        said = ["yes" if mentions(views[label]["10049"]["text"], fact) else "no"
                for label in ("prose", "one call", "two calls")]
        cites = citing(case, two["claims"], fact)
        totals.update({label: s == "yes" for label, s in zip(("prose", "one call", "two calls"), said, strict=True)})
        totals["cite"] += bool(cites)
        stated_and_cited += bool(stating(case, two["claims"], fact))
        start, end = fact["spans"][0]
        row("5-16", fact["text"], f"{fact['role']} {start}-{end} {' '.join(said)} {', '.join(cites) or '-'}",
            book[fact["text"]])
    n = len(lead(case))
    row("5-16", "totals: prose, one call, two calls mention; two calls cite",
        f"{totals['prose']}/{n} {totals['one call']}/{n} {totals['two calls']}/{n} {totals['cite']}/{n}",
        "3/8 7/8 7/8 8/8")
    single = views["one call"]["10049"]["trace"]
    row("5-16", "one call: claims, quotes, facts cited",
        f"{len(single['claims'])}, {sum(len(quotes_of(c)) for c in single['claims'])}, "
        f"{sum(bool(citing(case, single['claims'], f)) for f in lead(case))}", "1, 1, 0")
    row("5-16", "two calls: claims that cite, facts cited and stated by one claim (M4b)",
        f"{len({cid for f in lead(case) for cid in citing(case, two['claims'], f)})}, {stated_and_cited}/{n}", "3, 6/8")
