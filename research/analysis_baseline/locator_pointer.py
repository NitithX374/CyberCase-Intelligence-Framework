from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import locator_tiers as lt  # noqa: E402

SPLITS = ("development", "confirmation")


def measure(backend: Path, exported: Path) -> dict:
    sys.path.insert(0, str(backend))
    import app.trace.quotes as quotes
    from app.trace.bind import located_quote

    format_tier = quotes.find_format_only_quote

    def tier(text: str, quote: str) -> str:
        quotes.find_format_only_quote = lambda source, quote: None
        try:
            before = located_quote(text, quote)
        finally:
            quotes.find_format_only_quote = format_tier
        if before is not None:
            return "existing tiers"
        return "format tier" if located_quote(text, quote) is not None else "unverified"

    def why_not(text: str, quote: str) -> str:
        quote = quotes.without_edge_ellipses(quote)
        if not quote or any(mark in quote.strip(" .…")[1:-1] for mark in ("...", "…")):
            return "joined with ... in the middle"
        best = quotes.aligned_candidate(text, quote)
        if best is None:
            return "no candidate passage"
        second = quotes.aligned_candidate(quotes.masked_everywhere(text, text[best.start:best.end]), quote)
        second_edits = second.edits if second is not None else len(quote)
        too_many = best.edits > len(quote) / 3
        too_close = second_edits < best.edits + max(3, len(quote) // 10)
        if too_many and too_close:
            return "more than a third edited, and another passage as close"
        if too_many:
            return "more than a third edited"
        if too_close:
            return "another passage as close"
        worded = quotes.word_places(quote, text, best.start, best.end)
        if worded is None:
            return "no word-level alignment"
        return f"{len(worded[1])} places, more than {quotes.MAX_POINTER_PLACES}"

    english = json.loads(exported.read_text(encoding="utf-8"))
    thai_texts, thai = lt.thai_items()
    report: dict = {"backend": str(backend), "datasets": {}, "pointers": {}, "agreement_failures": 0}
    for language, texts, items in (("English", english["texts"], english["items"]), ("Thai", thai_texts, thai)):
        for split in SPLITS:
            chosen = [item for item in items if item["split"] == split]
            counts, reasons, seconds = Counter(), Counter(), []
            unverified_cases, unpointed_cases = set(), set()
            pointers = []
            for item in chosen:
                text, quote = texts[item["case"]], item["quote"]
                name = tier(text, quote)
                counts[name] += 1
                if name != "unverified":
                    continue
                unverified_cases.add(item["case"])
                began = time.perf_counter()
                passage = quotes.nearest_passage(text, quote)
                seconds.append(time.perf_counter() - began)
                reason = why_not(text, quote)
                if passage is not None:
                    counts["pointer"] += 1
                    if not reason[0].isdigit() or int(reason.split()[0]) > quotes.MAX_POINTER_PLACES:
                        report["agreement_failures"] += 1
                    pointers.append({"case": item["case"], "pinned": item.get("pinned"), "quote": quote,
                                     "passage": passage.source_text, "occurrences": passage.occurrences,
                                     "places": [list(place) for place in passage.differences]})
                else:
                    counts["no pointer"] += 1
                    unpointed_cases.add(item["case"])
                    reasons[reason] += 1
                    if reason[0].isdigit() and int(reason.split()[0]) <= quotes.MAX_POINTER_PLACES:
                        report["agreement_failures"] += 1
            seconds.sort()
            report["datasets"][f"{language} {split}"] = {
                "written": len(chosen),
                "existing tiers": counts["existing tiers"],
                "format tier": counts["format tier"],
                "unverified": counts["unverified"],
                "pointer": counts["pointer"],
                "no pointer": counts["no pointer"],
                "no pointer, by reason": dict(reasons),
                "cases": len({item["case"] for item in chosen}),
                "cases with an unverified quote": len(unverified_cases),
                "cases with an unverified quote and no pointer": len(unpointed_cases),
                "pointer seconds, median and max": [round(seconds[len(seconds) // 2], 3) if seconds else None,
                                                    round(seconds[-1], 3) if seconds else None],
            }
            report["pointers"][f"{language} {split}"] = pointers
    return report


def hand_check(rows: list[dict], title: str) -> list[str]:
    md = [f"## {title}", "", "| # | Case | Quote (model) | Passage (source) | Places (written → source) | Occurrences | "
          "Right place? | Right differences? |", "|---|---|---|---|---|---|---|---|"]
    for number, row in enumerate(rows, 1):
        places = "; ".join(f"«{w}» → «{s}»" for w, s in row["places"])
        quote = row["quote"].replace("|", "/").replace("\n", " ")
        passage = row["passage"].replace("|", "/").replace("\n", " ")
        md.append(f"| {number} | {row['case']} | {quote} | {passage} | {places} | {row['occurrences']} |  |  |")
    return md + [""]


def write(report: dict, script_hash: str) -> None:
    md = ["# Locator, part 2: the near-match pointer (fixed measurement; README sections of 2026-10-02 and 2026-10-03)",
          "", f"Script sha256 `{script_hash}`. Backend `{report['backend']}`. No model call.",
          f"Agreement between the production pointer and this script's reasons: {report['agreement_failures']} "
          "disagreements.", "",
          "| Data | Written | Existing tiers | Format tier | Unverified | Pointer | No pointer | Cases with an unverified "
          "quote | of them with a quote left unpointed |", "|---|---|---|---|---|---|---|---|---|"]
    for name, row in report["datasets"].items():
        md.append(f"| {name} | {row['written']} | {row['existing tiers']} | {row['format tier']} | {row['unverified']} | "
                  f"{row['pointer']} | {row['no pointer']} | {row['cases with an unverified quote']} | "
                  f"{row['cases with an unverified quote and no pointer']} |")
    md += ["", "## No pointer, by reason", ""]
    for name, row in report["datasets"].items():
        md.append(f"- {name}: {row['no pointer, by reason']}; pointer seconds (median, max) "
                  f"{row['pointer seconds, median and max']}")
    md.append("")
    (HERE / "results" / "locator_pointer_part2.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    counts_only = {key: value for key, value in report.items() if key != "pointers"}
    (HERE / "results" / "locator_pointer_part2.json").write_text(json.dumps(counts_only, indent=1, ensure_ascii=False),
                                                                 encoding="utf-8")
    english = ["# Hand check, English pointers: for each row, is the passage the right place, and are the places "
               "right? Fill the last two columns with yes or no.", ""]
    for split in SPLITS:
        english += hand_check(report["pointers"][f"English {split}"], f"English {split}")
    (HERE / "results" / "locator_pointer_handcheck_english.md").write_text("\n".join(english), encoding="utf-8")
    thai = ["# Hand check, Thai pointers (ThaiSum text stays in this ignored folder): for each row, is the passage the "
            "right place, and are the places right? Fill the last two columns with yes or no.", ""]
    for split in SPLITS:
        thai += hand_check(report["pointers"][f"Thai {split}"], f"Thai {split}")
    (lt.THAI / "results" / "locator_pointer_handcheck_thai.md").write_text("\n".join(thai), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", required=True)
    args = parser.parse_args()
    exported = HERE / "results" / "locator_pointer_export.json"
    subprocess.run([sys.executable, str(HERE / "locator_tiers.py"), "--backend", args.backend, "--export-only",
                    str(exported)], check=True, cwd=HERE)
    report = measure(Path(args.backend), exported)
    exported.unlink()
    write(report, hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    print(json.dumps(report["datasets"], indent=1, ensure_ascii=False))
    print("agreement failures:", report["agreement_failures"])


if __name__ == "__main__":
    main()
