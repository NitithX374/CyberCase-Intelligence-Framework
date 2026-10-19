from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NLI = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"
SEED, SIZE = 2026, 30
MID_ELLIPSIS = re.compile(r"\S\s*(?:\.{3,}|…+)\s*\S")
EN_NEGATION = {"not", "never", "no", "without"}
EN_FILLERS = {"also", "then", "however", "recently", "the"}
TH_FILLERS = {"ดังกล่าว", "ทั้งนี้", "นั้น", "ก็"}


def negation(token: str, thai: bool) -> bool:
    token = token.strip()
    if thai:
        return token.startswith("ไม่") or token == "มิได้"
    word = token.lower().strip(".,;:!?\"'()")
    return word in EN_NEGATION or word.endswith("n't")


def filler(token: str, thai: bool) -> bool:
    token = token.strip()
    return token in TH_FILLERS if thai else token.lower().strip(".,;:!?\"'()") in EN_FILLERS


def wilson(hits: int, n: int) -> list:
    if not n:
        return [None, None, None, hits, n]
    p, z = hits / n, 1.96
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return [round(p, 4), round(max(0, centre - half), 4), round(min(1, centre + half), 4), hits, n]


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", required=True)
    args = parser.parse_args()
    sys.path.insert(0, args.backend)
    sys.path.insert(0, str(HERE))
    import app.trace.bind as bind

    if not Path(bind.__file__).resolve().is_relative_to(Path(args.backend).resolve()):
        raise SystemExit(f"wrong binder: {bind.__file__}")
    import torch
    from app.trace.quotes import locate_quote
    from app.trace.sentences import sentence_spans
    from pythainlp.tokenize import word_tokenize
    from summary_encoder_nli import items
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    data = items()
    real: dict[str, dict] = {}
    for name, cases in data.items():
        thai = name.startswith("Thai")
        counts = {"ellipsis quotes located": 0, "with negation skipped": 0, "examples": []}
        for item in cases:
            text = item["text"]
            for claim in item["claims"]:
                for citation in claim.get("supporting_citations", []):
                    quote = citation.get("exact_quote", "")
                    if not quote or not MID_ELLIPSIS.search(quote):
                        continue
                    located = locate_quote(text, quote)
                    if located is None or located.tier != "ellipsis":
                        continue
                    counts["ellipsis quotes located"] += 1
                    gaps = [text[a[1]:b[0]] for a, b in zip(located.spans, located.spans[1:])]
                    tokens = [t for g in gaps for t in (word_tokenize(g, engine="newmm") if thai else g.split())]
                    if any(negation(t, thai) for t in tokens):
                        counts["with negation skipped"] += 1
                        counts["examples"].append({"case": item["key"], "claim": claim.get("claim_id"),
                                                   "gap": " | ".join(g.strip()[:80] for g in gaps)})
        real[name] = counts

    def split_of(name: str, key: str) -> str:
        if name == "English development":
            return "pilot"
        if name == "English confirmation":
            return "evaluation"
        return "pilot" if int(hashlib.sha256(key.encode()).hexdigest(), 16) % 2 == 0 else "evaluation"

    pools: dict[tuple[str, str, str], list] = {}
    for name, cases in data.items():
        thai = name.startswith("Thai")
        language = "thai" if thai else "english"
        joiner = "" if thai else " "
        for item in cases:
            text = item["text"]
            split = split_of(name, item["key"])
            for a, b in sentence_spans(text):
                sentence = text[a:b].strip()
                tokens = [t for t in (word_tokenize(sentence, engine="newmm") if thai else sentence.split())]
                if thai:
                    tokens = [t for t in tokens if t.strip()]
                if len(tokens) < 8 or len(tokens) > 80:
                    continue
                negs = [i for i, t in enumerate(tokens) if negation(t, thai) and 0 < i < len(tokens) - 1]
                if not negs:
                    continue
                i = negs[0]
                left, right = joiner.join(tokens[:i]), joiner.join(tokens[i + 1:])
                pools.setdefault((language, split, "planted"), []).append(
                    {"case": item["key"], "sentence": sentence, "pieces": left + " " + right,
                     "claim": left + joiner + right})
                fills = [j for j, t in enumerate(tokens) if filler(t, thai) and 0 < j < len(tokens) - 1]
                if fills:
                    j = fills[0]
                    left, right = joiner.join(tokens[:j]), joiner.join(tokens[j + 1:])
                    pools.setdefault((language, split, "control"), []).append(
                        {"case": item["key"], "sentence": sentence, "pieces": left + " " + right,
                         "claim": left + joiner + right})
    chosen = {k: random.Random(f"{SEED}:{k}").sample(v, min(SIZE, len(v))) for k, v in pools.items()}

    torch.set_num_threads(8)
    tokenizer = AutoTokenizer.from_pretrained(NLI)
    model = AutoModelForSequenceClassification.from_pretrained(NLI).eval()
    order = [model.config.id2label[i].lower() for i in range(len(model.config.id2label))]

    def judge(premise: str, hypothesis: str) -> str:
        batch = tokenizer(premise, hypothesis, truncation="longest_first", max_length=512, return_tensors="pt")
        with torch.no_grad():
            return order[int(model(**batch).logits[0].argmax())]

    report = {"real": real, "pairs": {}}
    md = ["# Ellipsis gaps: pieces-only against full-span premises", "",
          f"Script sha256 `{hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}`. Backend `{args.backend}`. "
          f"NLI `{NLI}` argmax; warning = not entailment. Wilson 95% intervals.", "",
          "## Real ellipsis quotes (stored readings)", "", "| Set | Ellipsis quotes located | Negation in the skipped text |",
          "|---|---|---|"]
    for name, c in real.items():
        md.append(f"| {name} | {c['ellipsis quotes located']} | {c['with negation skipped']} |")
    md += ["", "## Constructed pairs", "",
           "| Language | Split | Kind | Pairs | Warning, pieces premise | Warning, full-span premise | Labels pieces | Labels full |",
           "|---|---|---|---|---|---|---|---|"]
    for key in sorted(chosen):
        rows = chosen[key]
        for r in rows:
            r["label_pieces"] = judge(r["pieces"], r["claim"])
            r["label_full"] = judge(r["sentence"], r["claim"])
        wp = wilson(sum(r["label_pieces"] != "entailment" for r in rows), len(rows))
        wf = wilson(sum(r["label_full"] != "entailment" for r in rows), len(rows))
        lp = {lab: sum(r["label_pieces"] == lab for r in rows) for lab in order}
        lf = {lab: sum(r["label_full"] == lab for r in rows) for lab in order}
        report["pairs"]["/".join(key)] = {"warning pieces": wp, "warning full": wf, "labels pieces": lp,
                                          "labels full": lf, "rows": rows}
        cell = lambda w: "–" if w[0] is None else f"{w[0]:.3f} [{w[1]:.3f}, {w[2]:.3f}] ({w[3]}/{w[4]})"
        md.append(f"| {key[0]} | {key[1]} | {key[2]} | {len(rows)} | {cell(wp)} | {cell(wf)} | {lp} | {lf} |")
    (HERE / "results" / "nli_ellipsis_gap.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (HERE / "results" / "nli_ellipsis_gap.json").write_text(json.dumps(report, ensure_ascii=False, indent=1),
                                                            encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
