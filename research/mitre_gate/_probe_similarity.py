"""Does 'looks like an ATT&CK technique' separate the classes, with no training?

bge-m3 is an XLM-RoBERTa-large encoder, and it is already the retriever's
embedding model. If a sentence is far from every technique in that space, the
retrieval the gate is guarding would return nothing useful anyway.
"""
import glob, json, re, sys
import torch
from transformers import AutoModel, AutoTokenizer

BUNDLE = sorted(glob.glob("../../Mitre_ATT&CK Doc/enterprise-attack/*.json"))[-1]


def techniques():
    objects = json.load(open(BUNDLE, encoding="utf-8"))["objects"]
    out = []
    for o in objects:
        if o.get("type") != "attack-pattern" or o.get("revoked") or o.get("x_mitre_deprecated"):
            continue
        description = re.sub(r"<[^>]+>|\(Citation:[^)]*\)", "", o.get("description", ""))
        first = re.split(r"(?<=[.])\s", description.strip())[0]
        if o.get("name") and first:
            out.append(f"{o['name']}. {first}".strip()[:400])
    return sorted(set(out))


def embed(model, tokenizer, texts, batch=16):
    vectors = []
    for i in range(0, len(texts), batch):
        enc = tokenizer(texts[i:i + batch], padding=True, truncation=True, max_length=192, return_tensors="pt")
        with torch.no_grad():
            hidden = model(**enc).last_hidden_state[:, 0]
        vectors.append(torch.nn.functional.normalize(hidden, dim=-1))
        print(f"\r  {min(i + batch, len(texts))}/{len(texts)}", end="", file=sys.stderr)
    print(file=sys.stderr)
    return torch.cat(vectors)


refs = techniques()
print(f"{BUNDLE.split('/')[-1]}: {len(refs)} techniques")
print("  e.g.", refs[0][:110])

rows = [json.loads(line) for line in open("eval_sentences.jsonl", encoding="utf-8")]
tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-m3")
model = AutoModel.from_pretrained("BAAI/bge-m3").eval()

reference = embed(model, tokenizer, refs)
sentences = embed(model, tokenizer, [r["text"] for r in rows])
best = (sentences @ reference.T).max(dim=1)

for row, score, which in zip(rows, best.values.tolist(), best.indices.tolist()):
    row["score"] = score
    row["nearest"] = refs[which].split(".")[0]

rows.sort(key=lambda r: -r["score"])
for r in rows:
    print(f"  {r['score']:.3f}  y={r['label']}  {r['lang']}  {r['text'][:58]:60}  ~ {r['nearest'][:26]}")

positive = [r["score"] for r in rows if r["label"] == 1]
negative = [r["score"] for r in rows if r["label"] == 0]
print(f"\npositives {min(positive):.3f}..{max(positive):.3f}   negatives {min(negative):.3f}..{max(negative):.3f}")
best_threshold = max(
    ((sum(s >= t for s in positive) + sum(s < t for s in negative)) / len(rows), t)
    for t in [i / 200 for i in range(200)]
)
print(f"best achievable accuracy {best_threshold[0]:.1%} at threshold {best_threshold[1]:.3f}")
json.dump(rows, open("_probe_similarity.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
