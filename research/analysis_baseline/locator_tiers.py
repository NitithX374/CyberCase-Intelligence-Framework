from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
THAI = ROOT / "evaluation" / "ocr_downstream" / "thaisum_ocr"
THAI_RUN = "run_20261001_223057"
ENGLISH = {
    "development": ("main_20260930_193646", "cybercase_nogrammar"),
    "confirmation": ("main_20261001_021428", "cybercase_nogrammar"),
}
THAI_ARMS = {"development": ("clean",), "confirmation": ("targeted", "realistic")}
TIERS = ("existing tiers", "format tier", "unverified")


def export(out: Path) -> None:
    sys.path.insert(0, str(HERE))
    import book_scores as bs

    texts, items = {}, []
    for split, (run, arm) in ENGLISH.items():
        bs.ARMS = {**bs.ARMS, split: (run, arm)}
        for case_id, view in bs.arm(split).items():
            if not view["done"]:
                continue
            text = view["case"]["text"]
            texts[f"{split}:{case_id}"] = text
            for claim in view["written"]["claims"]:
                for quote in bs.quotes_of(claim):
                    items.append({"split": split, "case": f"{split}:{case_id}", "quote": quote,
                                  "pinned": bs.dropped_because(text, quote)})
    out.write_text(json.dumps({"texts": texts, "items": items}, ensure_ascii=False), encoding="utf-8")


def thai_items() -> tuple[dict[str, str], list[dict]]:
    articles = {}
    for line in (THAI / "data" / "articles.jsonl").read_text(encoding="utf-8").split("\n"):
        if not line.strip():
            continue
        record = json.loads(line)
        articles[record["id"]] = record
    texts, items = {}, []
    for split, arms in THAI_ARMS.items():
        for arm in arms:
            for path in sorted((THAI / "results" / f"raw_{THAI_RUN[4:]}").glob(f"*_{arm}.json")):
                article = path.name.split("_")[0]
                key = f"{arm}:{article}"
                texts[key] = articles[article][arm]
                saved = json.loads(path.read_text(encoding="utf-8"))
                for claim in (saved["reading"] or {}).get("claims", []):
                    for citation in claim["supporting_citations"] + claim["contradicting_citations"]:
                        items.append({"split": split, "arm": arm, "case": key, "quote": citation["exact_quote"]})
    return texts, items


def differences(quote: str, stored: str) -> list[list[str]]:
    ops = difflib.SequenceMatcher(None, quote, stored, autojunk=False).get_opcodes()
    return [[quote[i1:i2], stored[j1:j2]] for tag, i1, i2, j1, j2 in ops if tag != "equal"]


def measure(backend: Path, exported: Path) -> dict:
    sys.path.insert(0, str(backend))
    import app.trace.quotes as quotes
    from app.trace.bind import located_quote

    format_tier = quotes.find_format_only_quote

    def tier(text: str, quote: str) -> tuple[str, tuple[str, ...] | None]:
        quotes.find_format_only_quote = lambda source, quote: None
        try:
            before = located_quote(text, quote)
        finally:
            quotes.find_format_only_quote = format_tier
        if before is not None:
            return "existing tiers", before
        after = located_quote(text, quote)
        return ("format tier", after) if after is not None else ("unverified", None)

    english = json.loads(exported.read_text(encoding="utf-8"))
    thai_texts, thai = thai_items()
    report: dict = {"backend": str(backend), "datasets": {}, "safety": {}, "accepted": {}}
    for language, texts, items in (("English", english["texts"], english["items"]), ("Thai", thai_texts, thai)):
        for split in ("development", "confirmation"):
            chosen = [item for item in items if item["split"] == split]
            counts, cases_before, cases_after = Counter(), set(), set()
            accepted = []
            for item in chosen:
                name, stored = tier(texts[item["case"]], item["quote"])
                counts[name] += 1
                if name != "existing tiers":
                    cases_before.add(item["case"])
                if name == "unverified":
                    cases_after.add(item["case"])
                if name == "format tier":
                    accepted.append({"case": item["case"], "pinned": item.get("pinned"),
                                     "differences": differences(item["quote"], stored[0] if len(stored) == 1
                                                                else " ".join(stored))})
                if language == "English":
                    key = f"{split}|{item['pinned']}|{name}"
                    report["safety"][key] = report["safety"].get(key, 0) + 1
            report["datasets"][f"{language} {split}"] = {
                "written": len(chosen), **{t: counts[t] for t in TIERS},
                "cases": len({item["case"] for item in chosen}),
                "cases with an unverified quote, existing tiers only": len(cases_before),
                "cases with an unverified quote, with the format tier": len(cases_after),
            }
            report["accepted"][f"{language} {split}"] = accepted
    return report


def write(report: dict, script_hash: str) -> None:
    md = ["# Locator tiers, part 1: the format tier (fixed measurement, README section of 2026-10-02)", "",
          f"Script sha256 `{script_hash}`. Backend `{report['backend']}`. No model call.", "",
          "| Data | Written | Existing tiers | Format tier | Unverified | Cases | Cases with an unverified quote, "
          "before | after |", "|---|---|---|---|---|---|---|---|"]
    for name, row in report["datasets"].items():
        md.append(f"| {name} | {row['written']} | {row['existing tiers']} | {row['format tier']} | {row['unverified']} | "
                  f"{row['cases']} | {row['cases with an unverified quote, existing tiers only']} | "
                  f"{row['cases with an unverified quote, with the format tier']} |")
    md += ["", "## Safety check (English): quotes by the pinned binder's pile and the new tier", "",
           "| Split | Pinned pile | New tier | Quotes |", "|---|---|---|---|"]
    for key, value in sorted(report["safety"].items(), key=lambda kv: kv[0]):
        split, pinned, tier = key.split("|")
        md.append(f"| {split} | {pinned} | {tier} | {value} |")
    md += ["", "## English quotes accepted by the format tier, with what differs (quote -> stored source text)", ""]
    for name in ("English development", "English confirmation"):
        md.append(f"### {name}")
        md += [f"- {row['case']} ({row['pinned']}): {row['differences']}" for row in report["accepted"][name]]
        md.append("")
    (HERE / "results" / "locator_tiers_part1.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    english_only = {**report, "accepted": {k: v for k, v in report["accepted"].items() if k.startswith("English")}}
    (HERE / "results" / "locator_tiers_part1.json").write_text(json.dumps(english_only, indent=1, ensure_ascii=False),
                                                               encoding="utf-8")
    thai = ["# Thai quotes accepted by the format tier (ThaiSum text stays in this ignored folder)", ""]
    for name in ("Thai development", "Thai confirmation"):
        thai.append(f"## {name}")
        thai += [f"- {row['case']}: {row['differences']}" for row in report["accepted"][name]]
        thai.append("")
    (THAI / "results" / "locator_tiers_part1_thai.md").write_text("\n".join(thai) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", required=True)
    parser.add_argument("--export-only", default="")
    args = parser.parse_args()
    if args.export_only:
        export(Path(args.export_only))
        return
    exported = HERE / "results" / "locator_tiers_export.json"
    subprocess.run([sys.executable, __file__, "--backend", args.backend, "--export-only", str(exported)],
                   check=True, cwd=HERE)
    report = measure(Path(args.backend), exported)
    exported.unlink()
    write(report, hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    print(json.dumps(report["datasets"], indent=1, ensure_ascii=False))
    print(json.dumps(report["safety"], indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
