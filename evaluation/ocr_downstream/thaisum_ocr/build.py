"""Sample, key-fact targets, corrupted bodies and the edit log (README.md protocol). No model call.

  python build.py

Writes data/sample.json, data/articles.jsonl, data/edits.jsonl and data/build_summary.json. articles.jsonl holds
article text: it stays in this gitignored folder.
"""
from __future__ import annotations

import json
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import pythainlp

from facts import ZERO_WIDTH, candidates, category

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
BANK = HERE.parent / "fullpage_bank" / "verified_bank.json"
SEED = 2026
SAMPLE_SIZE = 100
BACKGROUND_RATE = 3259 / 285660
CATEGORIES = ("number", "place", "other")


def clean_text(text: str) -> str:
    return ZERO_WIDTH.sub("", unicodedata.normalize("NFC", text))


def char_class(character: str) -> str | None:
    if character in "0123456789":
        return "arabic_digit"
    if "\u0e50" <= character <= "\u0e59":
        return "thai_digit"
    if "\u0e00" <= character <= "\u0e7f":
        return "thai"
    if character.isascii() and character.isalpha():
        return "latin"
    return None


def bank_pairs() -> tuple[dict[str, list[tuple[str, int]]], dict]:
    typhoon = json.loads(BANK.read_text(encoding="utf-8"))["typhoon"]
    pairs: dict[str, list[tuple[str, int]]] = defaultdict(list)
    kept = Counter()
    for pair in typhoon["substitution_pairs"]:
        source, target, count = pair["reference"], pair["predicted"], pair["count"]
        if len(source) == 1 and len(target) == 1 and char_class(source) and char_class(source) == char_class(target):
            pairs[source].append((target, count))
            kept[char_class(source)] += count
    profile = {"substitutions": typhoon["substitutions"], "reference_characters": typhoon["reference_characters"],
               "class_preserving_kept": dict(kept), "source_characters_with_pairs": len(pairs)}
    return dict(pairs), profile


def eligible_rows() -> pd.DataFrame:
    df = pd.read_csv("F:/ThaiSum/thaisum.csv", encoding="utf-8")
    crime = df["type"].fillna("").str.contains("อาชญากรรม") | df["tags"].fillna("").str.contains("อาชญากรรม")
    summary = df["summary"].fillna("").str.strip() != ""
    length = df["body"].fillna("").str.len()
    rows = df[crime & summary & (length >= 1500) & (length <= 5000)]
    rows = rows.drop_duplicates("url").sort_values("url")
    return rows.reset_index().rename(columns={"index": "row"})


def occurrences(text: str, needle: str) -> list[int]:
    found, start = [], text.find(needle)
    while start >= 0:
        found.append(start)
        start = text.find(needle, start + len(needle))
    return found


def conflicts(surface: str, chosen: list[str], body: str) -> bool:
    spans = [(s, s + len(surface)) for s in occurrences(body, surface)]
    for other in chosen:
        if surface in other or other in surface:
            return True
        for start in occurrences(body, other):
            if any(a < start + len(other) and start < b for a, b in spans):
                return True
    return False


def substitution_options(fact: str, kind: str, pairs: dict) -> list[tuple[str, str, int]]:
    wanted = {"arabic_digit", "thai_digit"} if kind == "number" else {"thai", "latin"}
    sources = {c for c in fact if char_class(c) in wanted and c in pairs}
    return [(source, target, count) for source in sorted(sources) for target, count in pairs[source]]


def substituted(fact: str, options: list, rng: np.random.Generator) -> tuple[str, int, str, str]:
    weights = np.array([count for _, _, count in options], dtype=float)
    source, target, _ = options[rng.choice(len(options), p=weights / weights.sum())]
    positions = [i for i, c in enumerate(fact) if c == source]
    position = positions[rng.integers(len(positions))]
    return fact[:position] + target + fact[position + 1:], position, source, target


def edited(body: str, replacements: list[tuple[int, int, str]]) -> str:
    out, cursor = [], 0
    for start, end, new in sorted(replacements):
        out.append(body[cursor:start])
        out.append(new)
        cursor = end
    out.append(body[cursor:])
    return "".join(out)


def main() -> None:
    DATA.mkdir(exist_ok=True)
    pairs, profile = bank_pairs()
    rows = eligible_rows()
    rng = np.random.default_rng(SEED)
    picked = sorted(rng.choice(len(rows), SAMPLE_SIZE, replace=False))
    articles = []
    for i in picked:
        row = rows.iloc[i]
        articles.append({"id": f"r{int(row['row'])}", "row": int(row["row"]), "url": row["url"],
                         "clean": clean_text(row["body"]), "summary": clean_text(row["summary"])})

    for article in articles:
        found = candidates(article["clean"], article["summary"])
        by_category = {name: [c for c in found if category(c) == name] for name in CATEGORIES}
        article["candidates"] = {name: len(items) for name, items in by_category.items()}
        chosen: list[str] = []
        article["targets"] = []
        for name in CATEGORIES:
            for index in rng.permutation(len(by_category[name])):
                surface = by_category[name][index]
                if not conflicts(surface, chosen, article["clean"]):
                    chosen.append(surface)
                    article["targets"].append({"surface": surface, "category": name})
                    break

    types = Counter()
    for name in CATEGORIES:
        targets = [t for a in articles for t in a["targets"] if t["category"] == name]
        able = [k for k, t in enumerate(targets) if substitution_options(t["surface"], name, pairs)]
        wanted = min(len(targets) // 2, len(able))
        subs = set(rng.choice(able, wanted, replace=False).tolist()) if wanted else set()
        for k, target in enumerate(targets):
            target["type"] = "substitution" if k in subs else "deletion"
            types[(name, target["type"])] += 1
        types[(name, "could_substitute")] = len(able)

    edits, dropped, corrupted_in_clean = [], [], 0
    for article in articles:
        body, replacements, masked = article["clean"], [], []
        for target in article["targets"]:
            fact = target["surface"]
            if target["type"] == "substitution":
                new, position, source, replacement = substituted(
                    fact, substitution_options(fact, target["category"], pairs), rng)
                target.update(corrupted=new, position=position, source=source, replacement=replacement)
                corrupted_in_clean += new in body
            else:
                new = ""
                target["corrupted"] = ""
            starts = occurrences(body, fact)
            target["occurrences"] = len(starts)
            for start in starts:
                replacements.append((start, start + len(fact), new))
                masked.append((start, start + len(fact)))
                edits.append({"article": article["id"], "arm": "targeted", "offset": start, "original": fact,
                              "corrupted": new, "type": target["type"], "category": target["category"]})
        article["targeted"] = edited(body, replacements)
        for target in article["targets"]:
            target["original_survives"] = target["surface"] in article["targeted"]
            if target["original_survives"]:
                dropped.append({"article": article["id"], "category": target["category"], "type": target["type"]})

        background = []
        inside = np.zeros(len(body), dtype=bool)
        for start, end in masked:
            inside[start:end] = True
        for position, character in enumerate(body):
            if inside[position] or character not in pairs:
                continue
            if rng.random() < BACKGROUND_RATE:
                options = pairs[character]
                weights = np.array([count for _, count in options], dtype=float)
                target_character = options[rng.choice(len(options), p=weights / weights.sum())][0]
                background.append((position, position + 1, target_character))
                edits.append({"article": article["id"], "arm": "realistic", "offset": position,
                              "original": character, "corrupted": target_character, "type": "background_substitution",
                              "category": None})
        article["realistic"] = edited(body, replacements + background)
        article["background_substitutions"] = len(background)

    sample = [{"id": a["id"], "row": a["row"], "url": a["url"], "body_chars": len(a["clean"]),
               "summary_chars": len(a["summary"]), "targets": len(a["targets"])} for a in articles]
    (DATA / "sample.json").write_text(json.dumps(sample, ensure_ascii=False, indent=1), encoding="utf-8")
    with (DATA / "articles.jsonl").open("w", encoding="utf-8") as handle:
        for article in articles:
            handle.write(json.dumps(article, ensure_ascii=False) + "\n")
    with (DATA / "edits.jsonl").open("w", encoding="utf-8") as handle:
        for edit in edits:
            handle.write(json.dumps(edit, ensure_ascii=False) + "\n")

    body_chars = sum(len(a["clean"]) for a in articles)
    background_total = sum(a["background_substitutions"] for a in articles)
    summary = {
        "pythainlp": pythainlp.__version__, "eligible_rows": len(rows), "articles": len(articles),
        "bank": profile,
        "articles_with_candidates": {name: sum(a["candidates"][name] > 0 for a in articles) for name in CATEGORIES},
        "targets": {name: sum(t["category"] == name for a in articles for t in a["targets"]) for name in CATEGORIES},
        "types": {f"{k[0]}|{k[1]}": v for k, v in sorted(types.items())},
        "target_occurrences": sum(t["occurrences"] for a in articles for t in a["targets"]),
        "original_survives_after_edit": dropped,
        "substituted_form_already_in_clean_body": corrupted_in_clean,
        "background_substitutions": background_total,
        "background_rate_realised": round(background_total / body_chars, 5),
        "body_chars": body_chars,
    }
    (DATA / "build_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
