from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NLI = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"
TOP = 3


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
    from app.trace.quotes import nearest_passage
    from app.trace.sentences import sentence_spans
    from pythainlp.tokenize import word_tokenize
    from summary_encoder_nli import items
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    torch.set_num_threads(4)
    tokenizer = AutoTokenizer.from_pretrained(NLI)
    model = AutoModelForSequenceClassification.from_pretrained(NLI).eval()
    order = [model.config.id2label[i].lower() for i in range(len(model.config.id2label))]

    def words(text: str, thai: bool) -> set[str]:
        if thai:
            return {w for w in word_tokenize(text, engine="newmm") if w.strip()}
        return set(re.findall(r"\w+", text.lower()))

    def judge(premise: str, hypothesis: str) -> dict:
        batch = tokenizer(premise, hypothesis, truncation="longest_first", max_length=512, return_tensors="pt")
        with torch.no_grad():
            probs = torch.softmax(model(**batch).logits, dim=-1)[0].tolist()
        return dict(zip(order, probs))

    report, md_rows = {}, []
    for name, cases in items().items():
        thai = name.startswith("Thai")
        counts = {"unlocated": 0, "string pointer": 0, "refused": 0, "points": 0, "conflict": 0, "none": 0}
        for item in cases:
            text = item["text"]
            sentences = [text[a:b].strip() for a, b in sentence_spans(text) if text[a:b].strip()]
            for claim in item["claims"]:
                claim_text = claim.get("text", "")
                for citation in claim.get("supporting_citations", []):
                    quote = citation.get("exact_quote", "")
                    if not quote or bind.located_quote(text, quote):
                        continue
                    counts["unlocated"] += 1
                    if nearest_passage(text, quote) is not None:
                        counts["string pointer"] += 1
                        continue
                    counts["refused"] += 1
                    wanted = words(claim_text, thai)
                    ranked = sorted(sentences, key=lambda s: -len(wanted & words(s, thai)))[:TOP]
                    scored = [(s, judge(s, claim_text)) for s in ranked]
                    entailed = [(s, p) for s, p in scored if max(p, key=p.get) == "entailment"]
                    conflicts = [(s, p) for s, p in scored if max(p, key=p.get) == "contradiction"]
                    if entailed:
                        outcome, (sentence, probs) = "points", max(entailed, key=lambda x: x[1]["entailment"])
                    elif conflicts:
                        outcome, (sentence, probs) = "conflict", max(conflicts, key=lambda x: x[1]["contradiction"])
                    else:
                        outcome, sentence, probs = "none", "", {}
                    counts[outcome] += 1
                    clean = lambda s: (s or "").replace("|", "/").replace("\n", " ")[:260]
                    md_rows.append(f"| {name} | {item['key']} | {claim.get('claim_id', '')} | {outcome} | "
                                   f"{clean(claim_text)} | {clean(quote)} | {clean(sentence)} |")
        report[name] = counts
    md = ["# NLI fallback pointer: unlocated quotes the string pointer refused", "",
          f"Script sha256 `{hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}`. Backend `{args.backend}`. "
          f"NLI `{NLI}` argmax; top {TOP} sentences by word overlap with the claim.", "",
          "| Set | Unlocated quotes | String pointer pointed | Refused | NLI points | NLI conflict | None |",
          "|---|---|---|---|---|---|---|"]
    for name, c in report.items():
        md.append(f"| {name} | {c['unlocated']} | {c['string pointer']} | {c['refused']} | {c['points']} | "
                  f"{c['conflict']} | {c['none']} |")
    md += ["", "## Every refused case (read by eye; no gold)", "",
           "| Set | Case | Claim | Outcome | Claim text | Written quote | Sentence chosen |", "|---|---|---|---|---|---|---|"]
    md += md_rows
    (HERE / "results" / "nli_fallback_pointer.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (HERE / "results" / "nli_fallback_pointer.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    print("\n".join(md[:12]))


if __name__ == "__main__":
    main()
