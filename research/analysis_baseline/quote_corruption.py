"""Quote corruption (README "Quick check: result"): written quotes holding a control character. No model call.

  python quote_corruption.py          (on Windows, set PYTHONIOENCODING=utf-8 first)

A written quote is corrupted when it holds a character in U+0000-U+001F. The quotes are those the model wrote: the
saved readings of the two screens and the written traces of the 100-case no-grammar confirmation. Prints the counts
per arm, as the README's table groups them, and one example from each grammar + template arm (its first corrupted
quote, in case order, whose source text can be found) beside the source characters.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
CASES = {c["id"]: c for c in map(json.loads, (HERE / "data" / "cases.jsonl").read_text(encoding="utf-8").splitlines())}
GROUPS = {
    "grammar + template": [("screen_main_20260930_153526", "template_reorder"),
                           ("screen_main_20260930_205044", "g_template_reorder_noesc"),
                           ("screen_main_20260930_205044", "g_template_shipped_noesc")],
    "no grammar": [("screen_main_20260930_153526", "nogrammar"), ("main_20260930_193646", "cybercase_nogrammar")],
    "grammar without the template": [("screen_main_20260930_153526", "shipped")],
    "gpt-oss-20b": [("screen_main_20260930_153526", "gptoss20b")],
}


def corrupted(quote: str) -> bool:
    """The quote holds a C0 control character, U+0000-U+001F."""
    return any(ord(ch) < 0x20 for ch in quote)


def written_quotes(run: str, arm: str) -> list[tuple[str, str, str]]:
    """(case, claim, quote) for every quote the model wrote in one arm's saved files."""
    out = []
    for path in sorted((RESULTS / f"raw_{run}").glob(f"*_{arm}*.json")):
        case, rest = path.stem.split("_", 1)
        if rest not in (arm, f"{arm}_1"):
            continue
        saved = json.loads(path.read_text(encoding="utf-8"))
        trace = saved.get("reading") or saved.get("written")
        out += [(case, claim["claim_id"], c["exact_quote"]) for claim in trace["claims"]
                for c in claim["supporting_citations"] + claim["contradicting_citations"]]
    return out


def source_for(case: str, quote: str) -> str | None:
    """The source text the quote was copied from, if putting back the lost high byte (0x20 or 0x22) finds it."""
    text = CASES[case]["text"]
    for high in (0x2000, 0x2200):
        repaired = "".join(chr(high + ord(ch)) if ord(ch) < 0x20 else ch for ch in quote)
        if repaired in text:
            return repaired
    return None


def main() -> None:
    examples = []
    print("| Arms | Quotes holding a control character |\n|---|---|")
    for group, arms in GROUPS.items():
        counts = []
        for run, arm in arms:
            quotes = written_quotes(run, arm)
            bad = [q for q in quotes if corrupted(q[2])]
            counts.append((arm, len(bad), len(quotes)))
            if group == "grammar + template":
                examples += [(arm, *q) for q in bad if source_for(q[0], q[2])][:1]
        total = sum(n for _, n, _ in counts), sum(d for _, _, d in counts)
        print(f"| {group}: {', '.join(a for a, _, _ in counts)} | {total[0]:,} of {total[1]:,} "
              f"({', '.join(f'{n}/{d}' for _, n, d in counts)}) |")
    print()
    for arm, case, claim, quote in examples:
        source = source_for(case, quote)
        at = next(i for i, ch in enumerate(quote) if ord(ch) < 0x20)
        window = slice(max(0, at - 25), at + 25)
        print(f"- {arm}, case {case}, claim {claim}: written {quote[window]!r}")
        print(f"  source  {source[window]!r}")
        changed = sorted({(w, s) for w, s in zip(quote, source, strict=True) if w != s})
        print("  characters: " + ", ".join(f"U+{ord(w):04X} for U+{ord(s):04X} {s}" for w, s in changed))


if __name__ == "__main__":
    main()
