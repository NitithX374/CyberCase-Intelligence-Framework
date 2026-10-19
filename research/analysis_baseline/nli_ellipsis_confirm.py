from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NLI = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"
SEED, SIZE = 2027, 60


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", required=True)
    args = parser.parse_args()
    sys.path.insert(0, args.backend)
    sys.path.insert(0, str(HERE))
    import torch
    from app.trace.sentences import sentence_spans
    from nli_ellipsis_gap import filler, negation, wilson
    from pythainlp.tokenize import word_tokenize
    from summary_encoder_nli import items
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    used = json.loads((HERE / "results" / "nli_ellipsis_gap.json").read_text(encoding="utf-8"))["pairs"]
    seen = {(r["case"], r["sentence"], key.split("/")[2]) for key, cell in used.items() for r in cell["rows"]}
    pools: dict[tuple[str, str], list] = {}
    for name, cases in items().items():
        thai = name.startswith("Thai")
        language = "thai" if thai else "english"
        joiner = "" if thai else " "
        for item in cases:
            text = item["text"]
            for a, b in sentence_spans(text):
                sentence = text[a:b].strip()
                tokens = word_tokenize(sentence, engine="newmm") if thai else sentence.split()
                tokens = [t for t in tokens if t.strip()] if thai else tokens
                if len(tokens) < 8 or len(tokens) > 80:
                    continue
                for kind, test in (("planted", negation), ("control", filler)):
                    hits = [i for i, t in enumerate(tokens) if test(t, thai) and 0 < i < len(tokens) - 1]
                    if not hits or (item["key"], sentence, kind) in seen:
                        continue
                    i = hits[0]
                    pools.setdefault((language, kind), []).append(
                        {"case": item["key"], "sentence": sentence,
                         "claim": joiner.join(tokens[:i]) + joiner + joiner.join(tokens[i + 1:])})
    chosen = {k: random.Random(f"{SEED}:{k}").sample(v, min(SIZE, len(v))) for k, v in pools.items()}

    torch.set_num_threads(4)
    tokenizer = AutoTokenizer.from_pretrained(NLI)
    model = AutoModelForSequenceClassification.from_pretrained(NLI).eval()
    order = [model.config.id2label[i].lower() for i in range(len(model.config.id2label))]
    md = ["# Ellipsis gaps: confirmation of the contradiction-only rule", "",
          f"Script sha256 `{hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}`. Fresh pairs, full-span premise, seed {SEED}.", "",
          "| Language | Kind | Pairs | Warn, contradiction only | Warn, not entailment | Labels |", "|---|---|---|---|---|---|"]
    report = {}
    for key in sorted(chosen):
        rows = chosen[key]
        for r in rows:
            batch = tokenizer(r["sentence"], r["claim"], truncation="longest_first", max_length=512, return_tensors="pt")
            with torch.no_grad():
                r["label"] = order[int(model(**batch).logits[0].argmax())]
        c = wilson(sum(r["label"] == "contradiction" for r in rows), len(rows))
        n = wilson(sum(r["label"] != "entailment" for r in rows), len(rows))
        labels = {lab: sum(r["label"] == lab for r in rows) for lab in order}
        report["/".join(key)] = {"contradiction only": c, "not entailment": n, "labels": labels, "rows": rows}
        cell = lambda w: f"{w[0]:.3f} [{w[1]:.3f}, {w[2]:.3f}] ({w[3]}/{w[4]})"
        md.append(f"| {key[0]} | {key[1]} | {len(rows)} | {cell(c)} | {cell(n)} | {labels} |")
    (HERE / "results" / "nli_ellipsis_confirm.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (HERE / "results" / "nli_ellipsis_confirm.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
