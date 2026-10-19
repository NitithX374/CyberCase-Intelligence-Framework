import io, json, sys
from collections import Counter
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, r"F:/cc-worktrees/measure-c883e26/backend")
from app.trace.bind import located_quote
from app.trace.quotes import nearest_passage
from pythainlp.corpus import thai_words
from pythainlp.tokenize import word_tokenize

WORDS = set(thai_words())
THAI = Path(r"F:\Cybercase Framework\evaluation\ocr_downstream\thaisum_ocr")
articles = {}
for line in (THAI / "data" / "articles.jsonl").read_text(encoding="utf-8").split("\n"):
    if line.strip():
        r = json.loads(line); articles[r["id"]] = r


def unknown(text):
    return [w for w in word_tokenize(text, engine="newmm", keep_whitespace=False)
            if w.strip() and any("\u0e00" <= c <= "\u0e7f" for c in w) and w not in WORDS]


tally = Counter()
for split, arms in (("development", ("clean",)), ("confirmation", ("targeted", "realistic"))):
    for arm in arms:
        for path in sorted((THAI / "results" / "raw_20261001_223057").glob(f"*_{arm}.json")):
            art = articles[path.name.split("_")[0]]
            source = art[arm]
            saved = json.loads(path.read_text(encoding="utf-8"))
            for claim in (saved["reading"] or {}).get("claims", []):
                for c in claim["supporting_citations"] + claim["contradicting_citations"]:
                    quote = c["exact_quote"]
                    if located_quote(source, quote) is not None:
                        continue
                    passage = nearest_passage(source, quote)
                    if passage is None:
                        continue
                    tally[f"{split} pointers"] += 1
                    fixed = any(unknown(s) and not unknown(w) and w.strip() for w, s in passage.differences)
                    in_clean = arm != "clean" and located_quote(art["clean"], quote) is not None
                    if in_clean:
                        tally[f"{split}: model restored an injected OCR error"] += 1
                    elif fixed:
                        tally[f"{split}: source word not in the dictionary, model's word is (likely a source typo the model fixed)"] += 1
                    else:
                        tally[f"{split}: other (the model's own change, or names)"] += 1
print(json.dumps(tally, ensure_ascii=False, indent=1))
