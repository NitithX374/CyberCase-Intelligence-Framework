import sys
from pathlib import Path
HERE = Path("F:/Cybercase Framework/research/analysis_baseline")
BACKEND = "F:/cc-worktrees/measure-e35e558/backend"
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, BACKEND)
sys.path.insert(0, str(HERE))
import app.trace.bind as bind
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from summary_encoder_nli import items
from value_binding_nli import groups, present, NLI

tok = AutoTokenizer.from_pretrained(NLI)
model = AutoModelForSequenceClassification.from_pretrained(NLI).eval()
labels = {k: v.lower() for k, v in model.config.id2label.items()}
def nli(p, h):
    b = tok(p, h, truncation="only_first", max_length=512, return_tensors="pt")
    with torch.no_grad():
        return labels[int(model(**b).logits[0].argmax())]

out = ["# V3 claims: a claim number found nowhere in the source", "",
       "| # | Data | Case | NLI | Missing | Claim | Quotes | Same number written another way in source? |", "|---|---|---|---|---|---|---|---|"]
n = 0
for name, data in items().items():
    for item in data:
        text = item["text"]
        for claim in item["claims"]:
            quotes = [c["exact_quote"] for c in claim.get("supporting_citations", []) if c.get("exact_quote")]
            located = [" ".join(p) for p in (bind.located_quote(text, q) for q in quotes) if p]
            ct = claim.get("text", "")
            if not located or not groups(ct):
                continue
            quote = " ".join(located)
            missing = [g for g in groups(ct) if not present(g, quote)]
            absent = [g for g in missing if not present(g, text)]
            if not absent:
                continue
            n += 1
            c = lambda s: s.replace("|", "/").replace("\n", " ")[:300]
            out.append(f"| {n} | {name} | {item['key']} | {nli(quote, ct)} | {', '.join(absent)} | {c(ct)} | {c(quote)} |  |")
(HERE / "results" / "value_binding_v3_sheet.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(out))
