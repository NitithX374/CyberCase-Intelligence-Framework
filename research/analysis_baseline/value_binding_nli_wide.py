from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NLI = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"
GRID = [round(t / 100, 2) for t in range(1, 100)]
ARMS = ("P2", "P2w", "P2all", "P2top3", "P3")
TOP = 3


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", required=True)
    parser.add_argument("--arms", default="P2w,P2all,P2top3")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--interim", action="store_true")
    args = parser.parse_args()
    arms = [a for a in args.arms.split(",") if a]
    suffix = "" if set(arms) == {"P2w", "P2all", "P2top3"} else "_" + "_".join(arms)
    sys.path.insert(0, args.backend)
    sys.path.insert(0, str(HERE))
    import app.trace.bind as bind

    if not Path(bind.__file__).resolve().is_relative_to(Path(args.backend).resolve()):
        raise SystemExit(f"wrong binder: {bind.__file__}")
    import torch
    from app.trace.sentences import sentence_spans
    from summary_encoder_nli import items
    from pythainlp.tokenize import word_tokenize
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    from value_binding_nli_curve import bootstrap_rate as _rate, paired_difference as _diff

    def bootstrap_rate(rows, key):
        return _rate(rows, key) if rows else None

    def paired_difference(rows, left, right):
        return _diff(rows, left, right) if rows else None

    torch.set_num_threads(8)
    tokenizer = AutoTokenizer.from_pretrained(NLI)
    model = AutoModelForSequenceClassification.from_pretrained(NLI).eval()
    order = [model.config.id2label[i].lower() for i in range(len(model.config.id2label))]

    stored = json.loads((HERE / "results" / "value_binding_nli_rows.json").read_text(encoding="utf-8"))
    labels3 = ("entailment", "neutral", "contradiction")
    known = {(p["premise"], p["hypothesis"]): {k: p[k] for k in labels3} for p in stored["pairs"]}
    cache = HERE / "results" / "value_binding_nli_wide_cache.jsonl"
    if cache.exists():
        for line in cache.read_text(encoding="utf-8").split("\n"):
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            known[(rec["premise"], rec["hypothesis"])] = {k: rec[k] for k in labels3}
    units = stored["units"]
    if args.limit:
        units = [u for s in sorted({u["set"] for u in units}) for u in [x for x in units if x["set"] == s][:args.limit]]
        suffix += "_smoke"
    texts = {(name, item["key"]): item for name, data in items().items() for item in data}

    def located(text: str, claim: dict) -> list:
        quotes = [c["exact_quote"] for c in claim.get("supporting_citations", []) if c.get("exact_quote")]
        return [p for p in (bind.located_quote(text, q) for q in quotes) if p]

    def window(item: dict, claim_text: str, claim_quote: str) -> str:
        text = item["text"]
        spans = list(sentence_spans(text))
        claim = next(c for c in item["claims"] if c.get("text", "") == claim_text
                     and " ".join(" ".join(p) for p in located(text, c)) == claim_quote)
        hit = set()
        for pieces in located(text, claim):
            for piece in pieces:
                at = text.find(piece)
                if at < 0:
                    continue
                for i, (a, b) in enumerate(spans):
                    if a < at + len(piece) and b > at:
                        hit.add(i)
        if not hit:
            return claim_quote
        low, high = max(0, min(hit) - 1), min(len(spans) - 1, max(hit) + 1)
        return text[spans[low][0]:spans[high][1]]

    def words(text: str, thai: bool) -> set[str]:
        if thai:
            return {w for w in word_tokenize(text, engine="newmm") if w.strip()}
        return set(re.findall(r"\w+", text.lower()))

    def top_sentences(item: dict, hypothesis: str, thai: bool) -> list[str]:
        text = item["text"]
        wanted = words(hypothesis, thai)
        sentences = [text[a:b] for a, b in sentence_spans(text) if text[a:b].strip()]
        ranked = sorted(sentences, key=lambda s: -len(wanted & words(s, thai)))
        return ranked[:TOP]

    needed: dict[tuple[str, str], dict | None] = {}
    truncated = {}
    for u in units:
        item = texts[(u["set"], u["case"])]
        u["premise_w"] = window(item, u["claim"], u["quote"])
        u["premise_all"] = item["text"]
        thai = u["set"].startswith("Thai")
        u["top"] = {}
        u["_keys"] = []
        for hypothesis in [u["claim"]] + ([u["edit"]["claim"]] if "edit" in u else []):
            u["top"][hypothesis] = top_sentences(item, hypothesis, thai)
            wanted = {"P2w": [u["premise_w"]], "P2all": [u["premise_all"]], "P2top3": u["top"][hypothesis]}
            for premise in [x for arm in arms for x in wanted[arm]]:
                u["_keys"].append((premise, hypothesis))
                if (premise, hypothesis) not in known:
                    needed[(premise, hypothesis)] = None
        length = len(tokenizer(item["text"], u["claim"])["input_ids"])
        truncated.setdefault(u["set"], [0, 0])
        truncated[u["set"]][0] += int(length > 512)
        truncated[u["set"]][1] += 1
    keys = list(needed)
    if args.interim:
        units = [u for u in units if all(k in known for k in u["_keys"])]
        keys = []
        suffix += "_interim"
    print(f"units {len(units)}, new NLI pairs {len(keys)}", flush=True)
    for start in range(0, len(keys), 8):
        chunk = keys[start:start + 8]
        batch = tokenizer([p for p, _ in chunk], [h for _, h in chunk], truncation="only_first", max_length=512,
                          padding=True, return_tensors="pt")
        with torch.no_grad():
            probs = torch.softmax(model(**batch).logits, dim=-1).tolist()
        with cache.open("a", encoding="utf-8") as handle:
            for key, p in zip(chunk, probs):
                known[key] = dict(zip(order, (round(x, 5) for x in p)))
                handle.write(json.dumps({"premise": key[0], "hypothesis": key[1], **known[key]}, ensure_ascii=False) + chr(10))
        if start % 400 == 0:
            print(f"{start}/{len(keys)}", flush=True)

    def scores(premise, hypothesis):
        return known[(premise, hypothesis)]

    def flag(arm, holder, hypothesis, u, t):
        if arm == "P2top3":
            found = [scores(s, hypothesis) for s in u["top"][hypothesis]]
            if t is None:
                return not any(max(s, key=s.get) == "entailment" for s in found)
            return max(s["entailment"] for s in found) < t
        if arm == "P3":
            rule, attached = holder["rule"], holder["rule_attached"]
            if rule == "V0":
                return False
            premise = u["quote"] + " " + attached if attached else u["quote"]
        else:
            premise = {"P2": u["quote"], "P2w": u["premise_w"], "P2all": u["premise_all"]}[arm]
        s = scores(premise, hypothesis)
        return (max(s, key=s.get) != "entailment") if t is None or arm == "P3" else s["entailment"] < t

    sets = sorted({u["set"] for u in units})

    def rows_at(arm, t, s):
        real, synth = [], []
        for u in (x for x in units if x["set"] == s):
            real.append({"case": u["case"], "f": flag(arm, u, u["claim"], u, t)})
            if "edit" in u:
                synth.append({"case": u["case"], "f": flag(arm, u["edit"], u["edit"]["claim"], u, t),
                              "elsewhere": u["edit"]["elsewhere"]})
        return real, synth

    def rate(rows):
        return sum(r["f"] for r in rows) / max(1, len(rows))

    p3 = {s: rows_at("P3", None, s) for s in sets}

    def matched(arm, s):
        target = rate(p3[s][0])
        fitting = [t for t in GRID if rate(rows_at(arm, t, s)[0]) <= target]
        return max(fitting) if fitting else None

    report = {"truncated at 512 (whole source + claim)": truncated, "argmax": {}, "matched on English development": {},
              "matched in-sample": {}}
    dev = "English development"
    for arm in ("P2", *arms):
        t_dev = matched(arm, dev)
        for s in sets:
            for label, t in (("argmax", None), ("matched on English development", t_dev),
                             ("matched in-sample", matched(arm, s))):
                if label != "argmax" and t is None:
                    report[label].setdefault(s, {})[arm] = None
                    continue
                real, synth = rows_at(arm, t, s)
                merged = [{"case": a["case"], "arm": a["f"], "P3": b["f"], "elsewhere": a["elsewhere"]}
                          for a, b in zip(synth, p3[s][1])]
                fooled = [r for r in merged if r["elsewhere"]]
                report[label].setdefault(s, {})[arm] = {
                    "t": t, "flag": bootstrap_rate(real, "f"), "detect": bootstrap_rate(merged, "arm"),
                    "detect elsewhere": bootstrap_rate(fooled, "arm"),
                    "P3 - arm detect": paired_difference(merged, "P3", "arm"),
                    "P3 - arm detect elsewhere": paired_difference(fooled, "P3", "arm")}
    for s in sets:
        real, synth = p3[s]
        report["argmax"][s]["P3"] = {"flag": bootstrap_rate(real, "f"), "detect": bootstrap_rate(synth, "f"),
                                     "detect elsewhere": bootstrap_rate([r for r in synth if r["elsewhere"]], "f")}

    def cell(v):
        return "–" if v is None else f"{v[0]:.3f} [{v[1]:.3f}, {v[2]:.3f}]"

    md = ["# Wider NLI premises: P2 (quotes), P2w (±1 sentence), P2all (whole source), P2top3 (SummaC/SeNtLI-style) against P3", "",
          f"Script sha256 `{hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}`. Backend `{args.backend}`. "
          f"Truncated at 512 tokens (whole source + claim): {truncated}.", ""]
    for label in ("argmax", "matched on English development", "matched in-sample"):
        md += [f"## {label}", "", "| Set | Arm | t | Flag | Detect | Detect elsewhere | P3 − arm | P3 − arm elsewhere |",
               "|---|---|---|---|---|---|---|---|"]
        for s in sets:
            for arm, r in report[label][s].items():
                if r is None:
                    md.append(f"| {s} | {arm} | none reaches P3's flag rate | | | | | |")
                    continue
                md.append(f"| {s} | {arm} | {r.get('t', 'argmax')} | {cell(r['flag'])} | {cell(r['detect'])} | "
                          f"{cell(r['detect elsewhere'])} | {cell(r.get('P3 - arm detect'))} | "
                          f"{cell(r.get('P3 - arm detect elsewhere'))} |")
        md.append("")
    (HERE / "results" / f"value_binding_nli_wide{suffix}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (HERE / "results" / f"value_binding_nli_wide{suffix}.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
