from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import locator_baselines as lb  # noqa: E402
import locator_synthetic as ls  # noqa: E402

TIERS = lb.TIER_NAMES
TIER_LABELS = {"find_folded_quote": "NFKC fold", "unique_ellipsis_pieces": "ellipsis pieces",
               "find_relaxed_quote": "markup and whitespace", "find_format_only_quote": "format"}

PAIRS = [
    ("The account showed a balance of -5,000 baht after the transfer.",
     "The account showed a balance of 5,000 baht after the transfer.", "changed", "minus sign dropped"),
    ("The suspect agreed to re-sign the contract on Monday.",
     "The suspect agreed to resign the contract on Monday.", "changed", "hyphen inside a word"),
    ("A licensed therapist examined the victim at the clinic.",
     "A licensed the rapist examined the victim at the clinic.", "changed", "space inserted inside a word"),
    ("Staff at Apple reported the phishing e-mail to the police.",
     "Staff at apple reported the phishing e-mail to the police.", "changed", "case of a proper name"),
    ("The victim said it's the second time the account was hacked.",
     "The victim said its the second time the account was hacked.", "kept", "apostrophe dropped"),
    ("The interest rate rose from 1.5 percent to 2 percent.",
     "The interest rate rose from 15 percent to 2 percent.", "changed", "decimal point between digits"),
    ("Investigators froze 1,500,000 baht in the mule account.",
     "Investigators froze 1500000 baht in the mule account.", "kept", "thousands separator between digits"),
    ("The call was recorded at 10:30 on the morning of the attack.",
     "The call was recorded at 1030 on the morning of the attack.", "kept", "colon between digits"),
    ("The attackers exploited CVE-2017-0144 on the hospital server.",
     "The attackers exploited CVE2017-0144 on the hospital server.", "kept", "hyphen after letters"),
    ("The ransom demand was $5,000 in bitcoin, according to police.",
     "The ransom demand was 5,000 in bitcoin, according to police.", "changed", "currency sign dropped"),
    ("The scammer called from +66 81 234 5678 on two occasions.",
     "The scammer called from 66 81 234 5678 on two occasions.", "kept", "plus sign dropped"),
    ("Police seized the laptop at 9 a.m. on Tuesday morning.",
     "Police seized the laptop at 9 am on Tuesday morning.", "kept", "dots in an abbreviation"),
    ("เหตุเกิดเมื่อวันที่ 13 ก.พ. ที่ผ่านมา ตามที่ผู้เสียหายแจ้ง",
     "เหตุเกิดเมื่อวันที่ 13 กพ ที่ผ่านมา ตามที่ผู้เสียหายแจ้ง", "kept", "Thai month abbreviation without dots"),
    ("ผู้เสียหายโอนเงินจำนวน ๑๒,๐๐๐ บาท ให้แก่คนร้าย",
     "ผู้เสียหายโอนเงินจำนวน 12,000 บาท ให้แก่คนร้าย", "kept", "Thai digits as Arabic digits"),
    ("คนร้ายมีตากลมโต และสวมเสื้อสีดำ",
     "คนร้ายมีตา กลมโต และสวมเสื้อสีดำ", "kept", "space inserted in Thai"),
    ("ผู้ต้องหาให้การปฏิเสธ ตลอดข้อกล่าวหา",
     "ผู้ต้องหาให้การ ปฏิเสธตลอดข้อกล่าวหา", "kept", "Thai space moved"),
]


def accepted_by(text: str, quote: str) -> str:
    import app.trace.quotes as quotes
    from app.trace.bind import located_quote

    if located_quote(text, quote) is None:
        return "rejected"
    kept = {name: getattr(quotes, name) for name in TIERS}
    try:
        for level in range(len(TIERS) + 1):
            for at, name in enumerate(TIERS):
                setattr(quotes, name, kept[name] if at < level else (lambda *args: None))
            if located_quote(text, quote) is not None:
                return "exact" if level == 0 else TIER_LABELS[TIERS[level - 1]]
    finally:
        for name, function in kept.items():
            setattr(quotes, name, function)
    return "?"


def without(name: str, text: str, quote: str) -> bool:
    import app.trace.quotes as quotes
    from app.trace.bind import located_quote

    kept = getattr(quotes, name)
    setattr(quotes, name, lambda *args: None)
    try:
        return located_quote(text, quote) is not None
    finally:
        setattr(quotes, name, kept)


def leave_one_out(backend: str) -> dict:
    from app.trace.bind import located_quote

    import subprocess

    exported = HERE / "results" / "boundaries_export.json"
    subprocess.run([sys.executable, str(HERE / "locator_tiers.py"), "--backend", backend, "--export-only",
                    str(exported)], check=True, cwd=HERE, capture_output=True)
    english = json.loads(exported.read_text(encoding="utf-8"))
    exported.unlink()
    thai_texts, thai = lb.lt.thai_items()
    out = {}
    for language, texts, items in (("English", english["texts"], english["items"]), ("Thai", thai_texts, thai)):
        for split in ("development", "confirmation"):
            chosen = [i for i in items if i["split"] == split]
            row = {"written": len(chosen),
                   "production": sum(located_quote(texts[i["case"]], i["quote"]) is not None for i in chosen)}
            for name in TIERS:
                row[f"without {TIER_LABELS[name]}"] = sum(without(name, texts[i["case"]], i["quote"]) for i in chosen)
            out[f"{language} {split}"] = row
    edits = HERE / "results" / "locator_synthetic_confirmation_edits.jsonl"
    rows = [json.loads(line) for line in edits.read_text(encoding="utf-8").splitlines()]
    by_article: dict[str, list[tuple[str, str]]] = {}
    for r in rows:
        group = "format" if r["kind"] in ls.FORMAT_EDITS else (
            "content" if r["kind"] in ls.CONTENT_EDITS and not r.get("unchanged") else None)
        if group:
            by_article.setdefault(r["article"], []).append((group, r["quote"]))
    from concurrent.futures import ProcessPoolExecutor

    with ProcessPoolExecutor(7, initializer=ls.backend, initargs=(backend,)) as pool:
        parts = list(pool.map(casie_article, sorted(by_article.items()), chunksize=8))
    for group in ("format", "content"):
        row: dict = {"samples": 0}
        for part in parts:
            for key, value in part.get(group, {}).items():
                row[key] = row.get(key, 0) + value
        out[f"CASIE {group} edits (confirmation)"] = row
    return out


def casie_article(job: tuple[str, list[tuple[str, str]]]) -> dict:
    from app.trace.bind import located_quote

    stem, items = job
    text = json.loads((ls.CASIE / f"{stem}.json").read_text(encoding="utf-8"))["content"]
    out: dict[str, dict[str, int]] = {}
    for group, quote in items:
        row = out.setdefault(group, {"samples": 0})
        row["samples"] += 1
        row["production"] = row.get("production", 0) + (located_quote(text, quote) is not None)
        for name in TIERS:
            key = f"without {TIER_LABELS[name]}"
            row[key] = row.get(key, 0) + without(name, text, quote)
    return out


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", required=True)
    args = parser.parse_args()
    ls.backend(args.backend)
    import app.trace.bind as bind

    if not Path(bind.__file__).resolve().is_relative_to(Path(args.backend).resolve()):
        raise SystemExit(f"wrong binder: {bind.__file__}")
    from rapidfuzz import fuzz

    pairs = [{"source": s, "quote": q, "meaning": m, "difference": d, "production": accepted_by(s, q),
              "partial_ratio": round(fuzz.partial_ratio(q, s) / 100, 3)} for s, q, m, d in PAIRS]
    loo = leave_one_out(args.backend)
    md = ["# Leave-one-tier-out and format-tier boundary cases", "",
          f"Script sha256 `{hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}`. Backend `{args.backend}`. "
          "No model call.", "", "## Leave-one-tier-out", ""]
    columns = ["production", *[f"without {TIER_LABELS[n]}" for n in TIERS]]
    md += ["| Data | Total | " + " | ".join(columns) + " |", "|---|---|" + "---|" * len(columns)]
    for name, row in loo.items():
        total = row.get("written", row.get("samples"))
        md.append(f"| {name} | {total} | " + " | ".join(str(row[c]) for c in columns) + " |")
    md += ["", "## Boundary cases (illustrations, not a sample)", "",
           "| Difference | Author's mark | Production | partial_ratio |", "|---|---|---|---|"]
    md += [f"| {p['difference']} | {p['meaning']} | {p['production']} | {p['partial_ratio']} |" for p in pairs]
    (HERE / "results" / "locator_boundaries.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (HERE / "results" / "locator_boundaries.json").write_text(
        json.dumps({"leave_one_out": loo, "pairs": pairs}, indent=1, ensure_ascii=False), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
