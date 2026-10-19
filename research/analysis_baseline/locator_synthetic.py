from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import sys
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
CASIE = Path("F:/CASIE/data/annotation")
SEED = 2026
DEVELOPMENT = 300
SHORTEST, LONGEST = 40, 300
RESAMPLES = 2000
WORDS = re.compile(r"\w+")
CONTENT_EDITS = ("digit", "letter", "drop", "add", "swap")
FORMAT_EDITS = ("quotes", "case")
EDITS = CONTENT_EDITS + FORMAT_EDITS
BACKEND: Path | None = None
DONORS: dict[str, list[tuple[str, str]]] = {}
SENTENCES: list[tuple[str, str]] = []


def normalise(text: str) -> str:
    import unicodedata

    return " ".join(re.findall(r"[a-z0-9]+", unicodedata.normalize("NFKC", text).lower()))


def words(text: str) -> list[str]:
    return WORDS.findall(text)


def splits() -> dict[str, str]:
    stems = sorted(path.stem for path in CASIE.glob("*.json"))
    random.Random(SEED).shuffle(stems)
    return {stem: "development" if at < DEVELOPMENT else "confirmation" for at, stem in enumerate(stems)}


def shared(path: str, donors: dict, sentences: list) -> None:
    global DONORS, SENTENCES
    backend(path)
    DONORS, SENTENCES = donors, sentences


def backend(path: str) -> None:
    global BACKEND
    BACKEND = Path(path)
    if str(BACKEND) not in sys.path:
        sys.path.insert(0, str(BACKEND))


def aligned_arguments(content: str, doc: dict) -> tuple[list[dict], int]:
    found: dict[tuple[int, int], dict] = {}
    unmatched = 0
    for hopper in doc.get("cyberevent", {}).get("hopper", []):
        for event in hopper.get("events", []):
            for argument in event.get("argument", []):
                text = argument.get("text", "")
                start, end = argument["startOffset"], argument["endOffset"]
                for shift in (0, -1, 1, -2, 2):
                    if start + shift >= 0 and normalise(content[start + shift:end + shift]) == normalise(text) \
                            and normalise(text):
                        span = (start + shift, end + shift)
                        piece = content[span[0]:span[1]]
                        span = (span[0] + len(piece) - len(piece.lstrip()), span[1] - len(piece) + len(piece.rstrip()))
                        found.setdefault(span, {"a": span[0], "b": span[1],
                                                "role": argument.get("role", {}).get("type", "")})
                        break
                else:
                    unmatched += 1
    return sorted(found.values(), key=lambda item: (item["a"], item["b"])), unmatched


def letters_and_digits(text: str) -> str:
    import unicodedata

    return "".join(character.casefold() for character in unicodedata.normalize("NFKC", text) if character.isalnum())


def cuts_a_word(content: str, a: int, b: int) -> bool:
    starts_inside = 0 < a < len(content) and content[a - 1].isalnum() and content[a].isalnum()
    ends_inside = 0 < b < len(content) and content[b - 1].isalnum() and content[b].isalnum()
    return starts_inside or ends_inside


def middle_ellipsis(quote: str) -> bool:
    return any(mark in quote.strip(" .…")[1:-1] for mark in ("...", "…"))


def prepare(stem: str) -> dict:
    from app.trace.bind import located_quote
    from app.trace.sentences import sentence_spans

    doc = json.loads((CASIE / f"{stem}.json").read_text(encoding="utf-8"))
    content = doc.get("content", "")
    arguments, unmatched = aligned_arguments(content, doc)
    spans = sentence_spans(content)
    excluded = Counter({"argument span does not match its text": unmatched})
    kept, sentences = [], {}
    for argument in arguments:
        a, b = argument["a"], argument["b"]
        if cuts_a_word(content, a, b):
            excluded["argument span cuts a word"] += 1
            continue
        covering = [(s, e) for s, e in spans if s < b and e > a]
        if len(covering) != 1 or not (covering[0][0] <= a and b <= covering[0][1]):
            excluded["not inside exactly one sentence"] += 1
            continue
        s, e = covering[0]
        if (s, e) not in sentences:
            sentence = content[s:e]
            if not SHORTEST <= len(sentence) <= LONGEST:
                sentences[(s, e)] = "sentence shorter than 40 or longer than 300 characters"
            elif middle_ellipsis(sentence):
                sentences[(s, e)] = "sentence has ... in its middle"
            elif located_quote(content, sentence) is None:
                sentences[(s, e)] = "unedited sentence not located"
            else:
                sentences[(s, e)] = ""
        if sentences[(s, e)]:
            excluded[sentences[(s, e)]] += 1
            continue
        kept.append({**argument, "s": s, "e": e, "text": content[a:b]})
    return {"stem": stem, "content": content, "arguments": kept, "excluded": dict(excluded),
            "sentences": sorted(span for span, why in sentences.items() if not why)}


def edited(kind: str, argument: dict, sentence: str, rng: random.Random, donors: list[tuple[str, str]],
           stem: str) -> dict | None:
    text = argument["text"]
    a, b = argument["a"] - argument["s"], argument["b"] - argument["s"]
    new, original_word, injected_word = None, "", ""
    if kind == "digit":
        digits = [at for at, character in enumerate(text) if character in "0123456789"]
        if not digits:
            return None
        at = digits[-1]
        new = text[:at] + str((int(text[at]) + 1) % 10) + text[at + 1:]
    elif kind == "letter":
        candidates = [m for m in WORDS.finditer(text) if sum(c.isascii() and c.isalpha() for c in m.group()) >= 4]
        if not candidates:
            return None
        word = max(candidates, key=lambda m: (len(m.group()), -m.start()))
        letters = [at for at in range(word.start(), word.end()) if text[at].isascii() and text[at].isalpha()]
        at = letters[len(letters) // 2]
        base = "a" if text[at].islower() else "A"
        new = text[:at] + chr(ord(base) + (ord(text[at]) - ord(base) + 1) % 26) + text[at + 1:]
    elif kind == "drop":
        found = list(WORDS.finditer(text))
        if len(found) < 2:
            return None
        last, first = found[-1], found[0]
        if re.search(r"\w", sentence[b:]):
            new = text[:last.start()].rstrip() + text[last.end():]
            original_word = last.group()
        elif re.search(r"\w", sentence[:a]):
            new = text[:first.start()] + text[first.end():].lstrip()
            original_word = first.group()
        else:
            return None
    elif kind == "add":
        new = "also " + text
        injected_word = "also"
    elif kind == "swap":
        mine = normalise(text)
        pool = [donor for donor_stem, donor in donors if donor_stem != stem and normalise(donor) != mine
                and len(donor) >= 4]
        if not pool:
            return None
        new = rng.choice(pool)
    elif kind == "case":
        if text == text.upper():
            return None
        new = text.upper()
    if kind == "quotes":
        quote = "“" + sentence + "”"
        new = text
    else:
        quote = sentence[:a] + new + sentence[b:]
    if kind in ("digit", "letter"):
        before, after = words(text), words(new)
        changed = [(x, y) for x, y in zip(before, after) if x != y]
        if len(before) != len(after) or len(changed) != 1:
            return None
        original_word, injected_word = changed[0]
    return {"quote": quote, "new": new, "original_word": original_word, "injected_word": injected_word}


def why_not(quotes, text: str, quote: str) -> str:
    quote = quotes.without_edge_ellipses(quote)
    if not quote or middle_ellipsis(quote):
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


def located_by(text: str, quote: str) -> str:
    import app.trace.quotes as quotes
    from app.trace.bind import located_quote

    format_tier = quotes.find_format_only_quote
    quotes.find_format_only_quote = lambda source, quote: None
    try:
        before = located_quote(text, quote)
    finally:
        quotes.find_format_only_quote = format_tier
    if before is not None:
        return "existing tiers"
    return "format tier" if located_quote(text, quote) is not None else ""


def pointed(text: str, quote: str) -> dict:
    import app.trace.quotes as quotes

    passage = quotes.nearest_passage(text, quote)
    if passage is None:
        return {"pointer": False, "reason": why_not(quotes, text, quote)}
    return {"pointer": True, "passage": passage.source_text, "occurrences": passage.occurrences,
            "places": [list(place) for place in passage.differences],
            "at": quotes.quote_occurrences(text, passage.source_text)}


def right_difference(kind: str, sample: dict, places: list[list[str]]) -> bool:
    for written, source in places:
        written_words, source_words = set(words(written)), set(words(source))
        if kind in ("digit", "letter"):
            if sample["injected_word"] in written_words and sample["original_word"] in source_words:
                return True
        elif kind == "drop":
            if sample["original_word"] in source_words:
                return True
        elif kind == "add":
            if "also" in written_words:
                return True
        elif kind == "swap":
            new, old = set(words(sample["new"])), set(words(sample["original"]))
            if (not new - old or written_words & (new - old)) and (not old - new or source_words & (old - new)):
                return True
    return False


def run_article(prepared: dict) -> dict:
    from app.trace.bind import located_quote

    stem, content = prepared["stem"], prepared["content"]
    article_form = letters_and_digits(content)
    rows = []
    for argument in prepared["arguments"]:
        sentence = content[argument["s"]:argument["e"]]
        for kind in EDITS:
            rng = random.Random(f"{stem}:{argument['a']}:{argument['b']}:{kind}")
            sample = edited(kind, argument, sentence, rng, DONORS.get(argument["role"], []), stem)
            if sample is None:
                continue
            row = {"article": stem, "kind": kind, "role": argument["role"], "a": argument["a"], "b": argument["b"],
                   "s": argument["s"], "e": argument["e"], "sentence": sentence, "quote": sample["quote"],
                   "original": argument["text"], "new": sample["new"], "original_word": sample["original_word"],
                   "injected_word": sample["injected_word"]}
            if kind in CONTENT_EDITS and letters_and_digits(sample["quote"]) in article_form:
                row["unchanged"] = True
                rows.append(row)
                continue
            row["verified_by"] = located_by(content, sample["quote"])
            if not row["verified_by"] and kind in CONTENT_EDITS:
                row.update(pointed(content, sample["quote"]))
                if row["pointer"]:
                    row["right_place"] = any(at < argument["b"] and at + len(row["passage"]) > argument["a"]
                                             for at in row["at"])
                    row["covers_argument"] = any(at <= argument["a"] and at + len(row["passage"]) >= argument["b"]
                                                 for at in row["at"])
                    row["right_difference"] = right_difference(kind, {**sample, "original": argument["text"]},
                                                               row["places"])
            rows.append(row)
    facts = defaultdict(list)
    for argument in prepared["arguments"]:
        facts[(argument["s"], argument["e"])].append(argument["text"])
    for s, e in prepared["sentences"]:
        sentence = content[s:e]
        row = {"article": stem, "kind": "N1", "s": s, "e": e, "sentence": sentence, "quote": sentence,
               "facts": facts[(s, e)], "repeated": content.count(sentence) > 1}
        shortened = content[:s] + content[e:]
        row["verified_by"] = located_by(shortened, sentence)
        if not row["verified_by"]:
            row.update(pointed(shortened, sentence))
            if row["pointer"]:
                row["same_facts"] = all(fact in row["passage"] for fact in facts[(s, e)])
        rows.append(row)
    others = [pair for pair in SENTENCES if pair[0] != stem]
    if others:
        rng = random.Random(f"{stem}:N2")
        source_stem, sentence = rng.choice(others)
        row = {"article": stem, "kind": "N2", "from": source_stem, "quote": sentence}
        row["verified_by"] = "skipped: occurs here" if located_quote(content, sentence) is not None else ""
        if not row["verified_by"]:
            row.update(pointed(content, sentence))
        rows.append(row)
    return {"stem": stem, "rows": rows}


def interval(rows: list[dict], numerator, denominator) -> list:
    by_article = defaultdict(lambda: [0, 0])
    for row in rows:
        if denominator(row):
            by_article[row["article"]][1] += 1
            if numerator(row):
                by_article[row["article"]][0] += 1
    if not by_article:
        return [0, 0, None, None, None]
    counts = np.array(list(by_article.values()), dtype=float)
    hits, total = int(counts[:, 0].sum()), int(counts[:, 1].sum())
    rng = np.random.default_rng(SEED)
    picks = rng.integers(0, len(counts), size=(RESAMPLES, len(counts)))
    sums = counts[picks].sum(axis=1)
    rates = sums[:, 0] / np.maximum(sums[:, 1], 1)
    return [hits, total, round(hits / total, 4) if total else None,
            round(float(np.percentile(rates, 2.5)), 4), round(float(np.percentile(rates, 97.5)), 4)]


def summarise(rows: list[dict]) -> dict:
    report: dict = {"edits": {}, "controls": {}}
    for kind in CONTENT_EDITS:
        left = [row for row in rows if row["kind"] == kind]
        mine = [row for row in left if not row.get("unchanged")]
        unverified = [row for row in mine if not row["verified_by"]]
        report["edits"][kind] = {
            "samples": len(mine),
            "excluded, letters and digits still in the article": len(left) - len(mine),
            "false acceptance": interval(mine, lambda r: bool(r["verified_by"]), lambda r: True),
            "false acceptance, by tier": dict(Counter(row["verified_by"] for row in mine if row["verified_by"])),
            "pointer rate": interval(mine, lambda r: r.get("pointer"), lambda r: not r["verified_by"]),
            "right place": interval(mine, lambda r: r.get("right_place"), lambda r: r.get("pointer")),
            "right difference": interval(mine, lambda r: r.get("right_difference"),
                                         lambda r: r.get("right_place")),
            "passage covers the whole argument": interval(mine, lambda r: r.get("covers_argument"),
                                                          lambda r: r.get("right_place")),
            "places": dict(sorted(Counter(len(row["places"]) for row in unverified if row.get("pointer")).items())),
            "pointers with a place other than the edit": sum(
                1 for row in unverified if row.get("pointer") and len(row["places"]) > 1),
            "no pointer, by reason": dict(Counter(row["reason"] for row in unverified if not row.get("pointer"))),
        }
    for kind in FORMAT_EDITS:
        mine = [row for row in rows if row["kind"] == kind]
        report["edits"][kind] = {
            "samples": len(mine),
            "verified": interval(mine, lambda r: bool(r["verified_by"]), lambda r: True),
            "verified, by tier": dict(Counter(row["verified_by"] or "not verified" for row in mine)),
        }
    n1 = [row for row in rows if row["kind"] == "N1"]
    report["controls"]["N1"] = {
        "sentences": len(n1),
        "verified elsewhere, by tier": dict(Counter(row["verified_by"] for row in n1 if row["verified_by"])),
        "pointer, different facts": interval(n1, lambda r: r.get("pointer") and not r.get("same_facts"),
                                             lambda r: not r["verified_by"]),
        "pointer, same facts": interval(n1, lambda r: r.get("pointer") and r.get("same_facts"),
                                        lambda r: not r["verified_by"]),
        "no pointer, by reason": dict(Counter(row["reason"] for row in n1 if "reason" in row)),
    }
    report["controls"]["repeats"] = interval(n1, lambda r: r["repeated"], lambda r: True)
    n2 = [row for row in rows if row["kind"] == "N2"]
    report["controls"]["N2"] = {
        "samples": len(n2),
        "skipped, occurs here": sum(1 for row in n2 if row["verified_by"]),
        "pointer": interval(n2, lambda r: r.get("pointer"), lambda r: not r["verified_by"]),
    }
    return report


def table(name: str, cell: list) -> str:
    hits, total, rate, low, high = cell
    shown = "–" if rate is None else f"{rate:.3f} [{low:.3f}, {high:.3f}]"
    return f"| {name} | {hits} / {total} | {shown} |"


def write(split: str, report: dict, excluded: Counter, script_hash: str, log_hash: str, path: str) -> None:
    md = [f"# Locator, synthetic edits on CASIE: {split}", "",
          f"Script sha256 `{script_hash}`. Backend `{path}`. Edit log sha256 `{log_hash}`. No model call.", "",
          f"Exclusions (arguments): {dict(excluded)}", "", "| Measure | Count | Rate [95% CI, article bootstrap] |",
          "|---|---|---|"]
    for kind in CONTENT_EDITS:
        row = report["edits"][kind]
        md += [table(f"{kind}: false acceptance", row["false acceptance"]),
               table(f"{kind}: pointer rate", row["pointer rate"]),
               table(f"{kind}: right place", row["right place"]),
               table(f"{kind}: right difference", row["right difference"]),
               table(f"{kind}: passage covers the whole argument", row["passage covers the whole argument"])]
    for kind in FORMAT_EDITS:
        md.append(table(f"{kind}: verified", report["edits"][kind]["verified"]))
    controls = report["controls"]
    md += [table("N1: pointer, different facts", controls["N1"]["pointer, different facts"]),
           table("N1: pointer, same facts", controls["N1"]["pointer, same facts"]),
           table("N2: pointer", controls["N2"]["pointer"]),
           table("sentences found more than once in their article", controls["repeats"]), "", "## Details", "",
           "```json", json.dumps(report, indent=1, ensure_ascii=False), "```", ""]
    (HERE / "results" / f"locator_synthetic_{split}.md").write_text("\n".join(md), encoding="utf-8")
    (HERE / "results" / f"locator_synthetic_{split}.json").write_text(
        json.dumps({"script": script_hash, "edit_log": log_hash, "excluded": dict(excluded), **report}, indent=1,
                   ensure_ascii=False), encoding="utf-8")


def examples(split: str, rows: list[dict]) -> None:
    md = [f"# Locator, synthetic edits on CASIE: rows to read ({split}; CASIE text, ignored folder)", ""]
    groups = [
        ("False acceptance", lambda r: r["kind"] in CONTENT_EDITS and r["verified_by"]),
        ("Pointer at the wrong place", lambda r: r.get("pointer") and r.get("right_place") is False),
        ("Pointer at the right place, wrong difference",
         lambda r: r.get("right_place") and r.get("right_difference") is False),
        ("Format edit not verified", lambda r: r["kind"] in FORMAT_EDITS and not r["verified_by"]),
        ("N1 pointer, different facts", lambda r: r["kind"] == "N1" and r.get("pointer") and not r.get("same_facts")),
        ("N1 pointer, same facts", lambda r: r["kind"] == "N1" and r.get("pointer") and r.get("same_facts")),
        ("N2 pointer", lambda r: r["kind"] == "N2" and r.get("pointer")),
    ]
    for title, chosen in groups:
        picked = [row for row in rows if chosen(row)]
        md += [f"## {title} ({len(picked)})", ""]
        for row in picked:
            md.append(f"- `{row['article']}` {row['kind']} {row.get('role', '')}: quote «{row['quote']}»")
            if row.get("pointer"):
                places = "; ".join(f"«{w}» → «{s}»" for w, s in row["places"])
                md.append(f"  - passage «{row['passage']}»; places {places}")
            elif row["verified_by"]:
                md.append(f"  - verified by {row['verified_by']}")
        md.append("")
    (HERE / "results" / f"locator_synthetic_{split}_examples.md").write_text("\n".join(md), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", required=True)
    parser.add_argument("--split", choices=("development", "confirmation"), required=True)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()
    backend(args.backend)
    chosen = sorted(stem for stem, split in splits().items() if split == args.split)
    if args.limit:
        chosen = chosen[:args.limit]
    with ProcessPoolExecutor(args.workers, initializer=backend, initargs=(args.backend,)) as pool:
        prepared = list(pool.map(prepare, chosen, chunksize=8))
    excluded: Counter = Counter()
    donors: dict[str, list[tuple[str, str]]] = defaultdict(list)
    sentences: list[tuple[str, str]] = []
    for item in prepared:
        excluded.update(item["excluded"])
        for argument in item["arguments"]:
            donors[argument["role"]].append((item["stem"], argument["text"]))
        sentences += [(item["stem"], item["content"][s:e]) for s, e in item["sentences"]]
    for role in donors:
        donors[role] = sorted(set(donors[role]))
    with ProcessPoolExecutor(args.workers, initializer=shared,
                             initargs=(args.backend, dict(donors), sentences)) as pool:
        results = list(pool.map(run_article, prepared, chunksize=4))
    rows = [row for result in sorted(results, key=lambda r: r["stem"]) for row in result["rows"]]
    for row in rows:
        row["split"] = args.split
        row.setdefault("verified_by", "")
        row.pop("at", None)
    log = HERE / "results" / f"locator_synthetic_{args.split}_edits.jsonl"
    log.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    log_hash = hashlib.sha256(log.read_bytes()).hexdigest()
    report = summarise(rows)
    write(args.split, report, excluded, hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), log_hash,
          args.backend)
    examples(args.split, rows)
    print((HERE / "results" / f"locator_synthetic_{args.split}.md").read_text(encoding="utf-8").split("## Details")[0])


if __name__ == "__main__":
    main()
