from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SEED, RESAMPLES = 2026, 2000
DIGITS = re.compile(r"\d+(?:[.,:]\d+)*")
THAI_DIGITS = str.maketrans("๐๑๒๓๔๕๖๗๘๙", "0123456789")
NLI = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"
GRID = [round(t / 100, 2) for t in range(1, 100)]
SHOWN = (0.1, 0.3, 0.5, 0.7, 0.9)
THOUSANDS = re.compile(r"(?<=\d),(?=\d{3}(?!\d))")


def groups(text: str) -> list[str]:
    return DIGITS.findall(text.translate(THAI_DIGITS))


def present(group: str, text: str) -> bool:
    text = text.translate(THAI_DIGITS)
    if group in text:
        return True
    return bool(re.fullmatch(r"25\d\d", group)) and bool(re.search(rf"(?<!\d){group[2:]}(?!\d)", text))


def present_folded(group: str, text: str) -> bool:
    text = THOUSANDS.sub("", text.translate(THAI_DIGITS))
    group = THOUSANDS.sub("", group)
    if present(group, text):
        return True
    time = re.fullmatch(r"(\d{1,2})[:.](\d{2})", group)
    if time:
        return bool(re.search(rf"(?<!\d)0?{int(time.group(1))}[:.]{time.group(2)}(?!\d)", text))
    return False


def classify(claim_text, quote, text, sentences, found):
    missing = [g for g in groups(claim_text) if not found(g, quote)]
    if not missing:
        return "V0", None
    if any(not found(g, text) for g in missing):
        return "V3", None
    holders = [s for s in sentences if all(found(g, s) for g in missing) and s not in quote]
    if len(holders) == 1:
        return "V1", holders[0]
    return "V2", None


def edited(claim_text: str) -> tuple[str, str]:
    original = claim_text.translate(THAI_DIGITS)
    last = list(DIGITS.finditer(original))[-1]
    at = [i for i in range(last.start(), last.end()) if original[i].isdigit()][-1]
    changed = original[:at] + str((int(original[at]) + 1) % 10) + original[at + 1:]
    return changed, DIGITS.findall(changed[last.start():last.end() + 1])[0]


def bootstrap_rate(rows, key):
    by_case: dict[str, list[int]] = {}
    for r in rows:
        by_case.setdefault(r["case"], [0, 0])
        by_case[r["case"]][0] += int(bool(r[key]))
        by_case[r["case"]][1] += 1
    counts = np.array(list(by_case.values()), dtype=float)
    picks = np.random.default_rng(SEED).integers(0, len(counts), size=(RESAMPLES, len(counts)))
    sums = counts[picks].sum(axis=1)
    rates = sums[:, 0] / np.maximum(sums[:, 1], 1)
    return [round(float(counts[:, 0].sum() / counts[:, 1].sum()), 4), round(float(np.percentile(rates, 2.5)), 4),
            round(float(np.percentile(rates, 97.5)), 4), int(counts[:, 0].sum()), int(counts[:, 1].sum())]


def paired_difference(rows, left, right):
    by_case: dict[str, list[int]] = {}
    for r in rows:
        by_case.setdefault(r["case"], [0, 0, 0])
        by_case[r["case"]][0] += int(bool(r[left]))
        by_case[r["case"]][1] += int(bool(r[right]))
        by_case[r["case"]][2] += 1
    counts = np.array(list(by_case.values()), dtype=float)
    picks = np.random.default_rng(SEED).integers(0, len(counts), size=(RESAMPLES, len(counts)))
    sums = counts[picks].sum(axis=1)
    diffs = (sums[:, 0] - sums[:, 1]) / np.maximum(sums[:, 2], 1)
    point = (counts[:, 0].sum() - counts[:, 1].sum()) / counts[:, 2].sum()
    return [round(float(point), 4), round(float(np.percentile(diffs, 2.5)), 4),
            round(float(np.percentile(diffs, 97.5)), 4)]


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
    from app.trace.sentences import sentence_spans
    from summary_encoder_nli import items
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    torch.set_num_threads(8)
    tokenizer = AutoTokenizer.from_pretrained(NLI)
    model = AutoModelForSequenceClassification.from_pretrained(NLI).eval()
    order = [model.config.id2label[i].lower() for i in range(len(model.config.id2label))]

    units = []
    for name, data in items().items():
        for item in data:
            text = item["text"]
            sentences = [text[a:b] for a, b in sentence_spans(text)]
            for claim in item["claims"]:
                quotes = [c["exact_quote"] for c in claim.get("supporting_citations", []) if c.get("exact_quote")]
                located = [" ".join(p) for p in (bind.located_quote(text, q) for q in quotes) if p]
                claim_text = claim.get("text", "")
                if not located or not groups(claim_text):
                    continue
                quote = " ".join(located)
                unit = {"set": name, "case": item["key"], "claim": claim_text, "quote": quote}
                for rule_name, found in (("rule", present), ("rule_f", present_folded)):
                    unit[rule_name], unit[rule_name + "_attached"] = classify(claim_text, quote, text, sentences, found)
                if unit["rule"] == "V0":
                    changed, new_group = edited(claim_text)
                    unit["edit"] = {"claim": changed,
                                    "elsewhere": present(new_group, text) and not present(new_group, quote)}
                    for rule_name, found in (("rule", present), ("rule_f", present_folded)):
                        unit["edit"][rule_name], unit["edit"][rule_name + "_attached"] = classify(
                            changed, quote, text, sentences, found)
                units.append(unit)

    pairs: dict[tuple[str, str], dict | None] = {}
    for u in units:
        targets = [(u, u["claim"])] + ([(u["edit"], u["edit"]["claim"])] if "edit" in u else [])
        for holder, hypothesis in targets:
            pairs[(u["quote"], hypothesis)] = None
            for rule_name in ("rule", "rule_f"):
                if holder[rule_name + "_attached"]:
                    pairs[(u["quote"] + " " + holder[rule_name + "_attached"], hypothesis)] = None
    keys = list(pairs)
    print(f"units {len(units)}, NLI pairs {len(keys)}", flush=True)
    for start in range(0, len(keys), 16):
        chunk = keys[start:start + 16]
        batch = tokenizer([p for p, _ in chunk], [h for _, h in chunk], truncation="only_first", max_length=512,
                          padding=True, return_tensors="pt")
        with torch.no_grad():
            probs = torch.softmax(model(**batch).logits, dim=-1).tolist()
        for key, p in zip(chunk, probs):
            pairs[key] = dict(zip(order, (round(x, 5) for x in p)))
        if start % 800 == 0:
            print(f"{start}/{len(keys)}", flush=True)

    def pe(quote, hypothesis, attached=None):
        premise = quote + " " + attached if attached else quote
        return pairs[(premise, hypothesis)]["entailment"]

    def argmax_entails(quote, hypothesis, attached=None):
        premise = quote + " " + attached if attached else quote
        scores = pairs[(premise, hypothesis)]
        return max(scores, key=scores.get) == "entailment"

    def flags(holder, hypothesis, quote, t, rule_name="rule"):
        rule, attached = holder[rule_name], holder[rule_name + "_attached"]
        p2 = (not argmax_entails(quote, hypothesis)) if t is None else pe(quote, hypothesis) < t
        if rule == "V0":
            p3 = False
        elif t is None:
            p3 = not argmax_entails(quote, hypothesis, attached)
        else:
            p3 = pe(quote, hypothesis, attached) < t
        return p2, p3

    sets = sorted({u["set"] for u in units})

    def table(t, rule_name="rule"):
        out = {}
        for s in sets:
            real, synth = [], []
            for u in (x for x in units if x["set"] == s):
                p2, p3 = flags(u, u["claim"], u["quote"], t, rule_name)
                real.append({"case": u["case"], "P2": p2, "P3": p3})
                if "edit" in u:
                    q2, q3 = flags(u["edit"], u["edit"]["claim"], u["quote"], t, rule_name)
                    synth.append({"case": u["case"], "P2": q2, "P3": q3, "elsewhere": u["edit"]["elsewhere"]})
            out[s] = (real, synth)
        return out

    def rate(rows, key):
        return sum(bool(r[key]) for r in rows) / max(1, len(rows))

    argmax = table(None)
    curves = {s: [] for s in sets}
    tables_by_t = {t: table(t) for t in GRID}
    for t in GRID:
        for s in sets:
            real, synth = tables_by_t[t][s]
            fooled = [r for r in synth if r["elsewhere"]]
            curves[s].append({"t": t, "P2 flag": round(rate(real, "P2"), 4), "P3 flag": round(rate(real, "P3"), 4),
                              "P2 detect": round(rate(synth, "P2"), 4), "P3 detect": round(rate(synth, "P3"), 4),
                              "P2 detect elsewhere": round(rate(fooled, "P2"), 4),
                              "P3 detect elsewhere": round(rate(fooled, "P3"), 4)})

    def matched_t(s):
        target = rate(argmax[s][0], "P3")
        fitting = [c["t"] for c in curves[s] if c["P2 flag"] <= target]
        return max(fitting) if fitting else None

    def compare(s, t):
        real_a, synth_a = argmax[s]
        real_t, synth_t = tables_by_t[t][s]
        merged = [{"case": a["case"], "P2": b["P2"], "P3": a["P3"], "elsewhere": a["elsewhere"]}
                  for a, b in zip(synth_a, synth_t)]
        fooled = [r for r in merged if r["elsewhere"]]
        return {"t": t, "P2(t) flag": bootstrap_rate([{"case": r["case"], "f": r["P2"]} for r in real_t], "f"),
                "P3 argmax flag": bootstrap_rate([{"case": r["case"], "f": r["P3"]} for r in real_a], "f"),
                "P2(t) detect": bootstrap_rate(merged, "P2"), "P3 argmax detect": bootstrap_rate(merged, "P3"),
                "P3 - P2(t) detect": paired_difference(merged, "P3", "P2"),
                "P2(t) detect elsewhere": bootstrap_rate(fooled, "P2"),
                "P3 argmax detect elsewhere": bootstrap_rate(fooled, "P3"),
                "P3 - P2(t) detect elsewhere": paired_difference(fooled, "P3", "P2")}

    dev = "English development"
    t_dev = matched_t(dev)
    report = {"t chosen on English development": t_dev, "primary": {}, "in-sample": {}, "curves": curves, "P3f": {}}
    for s in sets:
        if t_dev is not None:
            report["primary"][s] = compare(s, t_dev)
        t_own = matched_t(s)
        report["in-sample"][s] = compare(s, t_own) if t_own is not None else None
    folded = table(None, "rule_f")
    for s in sets:
        real, synth = folded[s]
        counts = {c: sum(1 for u in units if u["set"] == s and u["rule_f"] == c) for c in ("V0", "V1", "V2", "V3")}
        report["P3f"][s] = {"classes": counts, "P3f flag": bootstrap_rate(real, "P3"),
                            "P3f detect": bootstrap_rate(synth, "P3"),
                            "P3f detect elsewhere": bootstrap_rate([r for r in synth if r["elsewhere"]], "P3")}

    def cell(v):
        return f"{v[0]:.3f} [{v[1]:.3f}, {v[2]:.3f}]" + (f" ({v[3]}/{v[4]})" if len(v) == 5 else "")

    md = ["# NLI threshold curve: P2(t) against P3", "",
          f"Script sha256 `{hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}`. Backend `{args.backend}`. "
          f"NLI `{NLI}`, softmax entailment. Case bootstrap {RESAMPLES}, seed {SEED}.", "",
          f"## Primary: t chosen on English development = {t_dev}", "",
          "| Set | P2(t) flag | P3 flag | P2(t) detect | P3 detect | P3 − P2(t) | P2(t) elsewhere | P3 elsewhere | P3 − P2(t) elsewhere |",
          "|---|---|---|---|---|---|---|---|---|"]
    for s, r in report["primary"].items():
        md.append(f"| {s} | {cell(r['P2(t) flag'])} | {cell(r['P3 argmax flag'])} | {cell(r['P2(t) detect'])} | "
                  f"{cell(r['P3 argmax detect'])} | {cell(r['P3 - P2(t) detect'])} | {cell(r['P2(t) detect elsewhere'])} | "
                  f"{cell(r['P3 argmax detect elsewhere'])} | {cell(r['P3 - P2(t) detect elsewhere'])} |")
    md += ["", "## In-sample matched threshold (favours P2)", "",
           "| Set | t | P2(t) flag | P3 flag | P2(t) detect | P3 detect | P3 − P2(t) | P3 − P2(t) elsewhere |",
           "|---|---|---|---|---|---|---|---|"]
    for s, r in report["in-sample"].items():
        if r:
            md.append(f"| {s} | {r['t']} | {cell(r['P2(t) flag'])} | {cell(r['P3 argmax flag'])} | {cell(r['P2(t) detect'])} | "
                      f"{cell(r['P3 argmax detect'])} | {cell(r['P3 - P2(t) detect'])} | {cell(r['P3 - P2(t) detect elsewhere'])} |")
    md += ["", "## Curves", ""]
    for s in sets:
        md += [f"### {s}", "", "| t | P2 flag | P3 flag | P2 detect | P3 detect | P2 elsewhere | P3 elsewhere |",
               "|---|---|---|---|---|---|---|"]
        for c in curves[s]:
            if c["t"] in SHOWN:
                md.append(f"| {c['t']} | {c['P2 flag']:.3f} | {c['P3 flag']:.3f} | {c['P2 detect']:.3f} | "
                          f"{c['P3 detect']:.3f} | {c['P2 detect elsewhere']:.3f} | {c['P3 detect elsewhere']:.3f} |")
        md.append("")
    md += ["## P3f, post hoc: separators, Thai digits and times folded", "",
           "| Set | V0 / V1 / V2 / V3 | P3f flag | P3f detect | P3f elsewhere |", "|---|---|---|---|---|"]
    for s, r in report["P3f"].items():
        c = r["classes"]
        md.append(f"| {s} | {c['V0']} / {c['V1']} / {c['V2']} / {c['V3']} | {cell(r['P3f flag'])} | "
                  f"{cell(r['P3f detect'])} | {cell(r['P3f detect elsewhere'])} |")
    (HERE / "results" / "value_binding_nli_curve.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (HERE / "results" / "value_binding_nli_curve.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    rows = [{**u, "nli": {"quote": pairs[(u["quote"], u["claim"])]}} for u in units]
    (HERE / "results" / "value_binding_nli_rows.json").write_text(
        json.dumps({"pairs": [{"premise": p, "hypothesis": h, **v} for (p, h), v in pairs.items()], "units": rows},
                   ensure_ascii=False), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
