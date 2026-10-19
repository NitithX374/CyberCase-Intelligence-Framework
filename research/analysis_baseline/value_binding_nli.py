from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SEED, RESAMPLES = 2026, 2000
DIGITS = re.compile(r"\d+(?:[.,:]\d+)*")
THAI_DIGITS = str.maketrans("๐๑๒๓๔๕๖๗๘๙", "0123456789")
NLI = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"
POLICIES = ("P1", "P2", "P3")


def groups(text: str) -> list[str]:
    return DIGITS.findall(text.translate(THAI_DIGITS))


def present(group: str, text: str) -> bool:
    text = text.translate(THAI_DIGITS)
    if group in text:
        return True
    return bool(re.fullmatch(r"25\d\d", group)) and bool(re.search(rf"(?<!\d){group[2:]}(?!\d)", text))


def share(rows: list[dict], key: str) -> list:
    by_case: dict[str, list[int]] = {}
    for r in rows:
        by_case.setdefault(r["case"], [0, 0])
        by_case[r["case"]][0] += int(bool(r[key]))
        by_case[r["case"]][1] += 1
    counts = np.array(list(by_case.values()), dtype=float)
    if not len(counts):
        return [0, 0, None, None, None]
    picks = np.random.default_rng(SEED).integers(0, len(counts), size=(RESAMPLES, len(counts)))
    sums = counts[picks].sum(axis=1)
    rates = sums[:, 0] / np.maximum(sums[:, 1], 1)
    hits, total = int(counts[:, 0].sum()), int(counts[:, 1].sum())
    return [hits, total, round(hits / total, 4), round(float(np.percentile(rates, 2.5)), 4),
            round(float(np.percentile(rates, 97.5)), 4)]


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

    tokenizer = AutoTokenizer.from_pretrained(NLI)
    model = AutoModelForSequenceClassification.from_pretrained(NLI).eval()
    labels = {k: v.lower() for k, v in model.config.id2label.items()}

    def nli(premise: str, hypothesis: str) -> str:
        batch = tokenizer(premise, hypothesis, truncation="only_first", max_length=512, return_tensors="pt")
        with torch.no_grad():
            return labels[int(model(**batch).logits[0].argmax())]

    def classify(claim_text: str, quote: str, text: str, sentences: list[str]) -> tuple[str, str | None]:
        missing = [g for g in groups(claim_text) if not present(g, quote)]
        if not missing:
            return "V0", None
        if any(not present(g, text) for g in missing):
            return "V3", None
        holders = [s for s in sentences if all(present(g, s) for g in missing) and s not in quote]
        if len(holders) == 1:
            return "V1", holders[0]
        return "V2", None

    def decide(rule: str, nli_quote: str, nli_attached: str | None) -> dict:
        return {"P1": rule in ("V2", "V3"), "P2": nli_quote != "entailment",
                "P3": False if rule == "V0" else ((nli_attached or nli_quote) != "entailment")}

    report: dict = {}
    md = ["# Value binding with an NLI tie-break", "",
          f"Script sha256 `{hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}`. Backend `{args.backend}`. "
          f"NLI `{NLI}` argmax. Case bootstrap {RESAMPLES}, seed {SEED}.", ""]
    sheet = ["# Value binding check sheet: is the flag right? (mark yes/no)", "",
             "| # | Data | Case | Class | NLI | Flag P3 | Claim | Quotes | Attached sentence | Problem? |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for name, data in items().items():
        rows, synthetic = [], []
        bound_total = 0
        for item in data:
            text = item["text"]
            sentences = [text[a:b] for a, b in sentence_spans(text)]
            for claim in item["claims"]:
                quotes = [c["exact_quote"] for c in claim.get("supporting_citations", []) if c.get("exact_quote")]
                located = [" ".join(p) for p in (bind.located_quote(text, q) for q in quotes) if p]
                if not located:
                    continue
                bound_total += 1
                claim_text = claim.get("text", "")
                if not groups(claim_text):
                    continue
                quote = " ".join(located)
                rule, attached = classify(claim_text, quote, text, sentences)
                nli_quote = nli(quote, claim_text)
                nli_attached = nli(quote + " " + attached, claim_text) if attached else None
                row = {"case": item["key"], "claim": claim_text, "quote": quote, "rule": rule, "attached": attached,
                       "nli_quote": nli_quote, "nli_attached": nli_attached, **decide(rule, nli_quote, nli_attached)}
                rows.append(row)
                if rule == "V0":
                    found = list(DIGITS.finditer(claim_text.translate(THAI_DIGITS)))
                    last = found[-1]
                    digits = [i for i in range(last.start(), last.end()) if claim_text.translate(THAI_DIGITS)[i].isdigit()]
                    at = digits[-1]
                    original = claim_text.translate(THAI_DIGITS)
                    edited = original[:at] + str((int(original[at]) + 1) % 10) + original[at + 1:]
                    new_group = DIGITS.findall(edited[last.start():last.end() + 1])[0]
                    e_rule, e_attached = classify(edited, quote, text, sentences)
                    e_nli_quote = nli(quote, edited)
                    e_nli_attached = nli(quote + " " + e_attached, edited) if e_attached else None
                    synthetic.append({"case": item["key"], "rule": e_rule,
                                      "elsewhere": present(new_group, text) and not present(new_group, quote),
                                      **decide(e_rule, e_nli_quote, e_nli_attached)})
        cell: dict = {"bound claims": bound_total, "numeric bound claims": len(rows)}
        for cls in ("V0", "V1", "V2", "V3"):
            subset = [r for r in rows if r["rule"] == cls]
            for r in rows:
                r["is_" + cls] = r["rule"] == cls
            cell[cls] = share(rows, "is_" + cls)
            cell[cls + " NLI labels (quotes)"] = {lab: sum(r["nli_quote"] == lab for r in subset)
                                                  for lab in ("entailment", "neutral", "contradiction")}
            if cls == "V1":
                cell["V1 NLI labels (quotes + sentence)"] = {lab: sum(r["nli_attached"] == lab for r in subset)
                                                             for lab in ("entailment", "neutral", "contradiction")}
        for policy in POLICIES:
            cell[f"flag {policy}"] = share(rows, policy)
            cell[f"flag {policy} over all bound"] = round(sum(r[policy] for r in rows) / bound_total, 4)
        for r in synthetic:
            r["elsewhere_flag"] = r["elsewhere"]
        cell["synthetic edits"] = len(synthetic)
        cell["synthetic new number elsewhere in source"] = share(synthetic, "elsewhere_flag")
        for policy in POLICIES:
            cell[f"synthetic detected {policy}"] = share(synthetic, policy)
            fooled = [r for r in synthetic if r["elsewhere"]]
            cell[f"synthetic detected {policy}, new number elsewhere"] = share(fooled, policy) if fooled else None
        report[name] = cell
        md += [f"## {name}", "", f"Bound claims {bound_total}; with digits {len(rows)}; synthetic edits {len(synthetic)}.", "",
               "| Measure | Value |", "|---|---|"]
        for key, value in cell.items():
            if key in ("bound claims", "numeric bound claims", "synthetic edits"):
                continue
            shown = f"{value[2]:.3f} [{value[3]:.3f}, {value[4]:.3f}] ({value[0]}/{value[1]})" if isinstance(value, list) and value[2] is not None else value
            md.append(f"| {key} | {shown} |")
        md.append("")
        flagged = [r for r in rows if r["P3"]]
        unflagged = [r for r in rows if not r["P3"]]
        rng = random.Random(f"{SEED}:{name}")
        picked = rng.sample(flagged, min(20, len(flagged))) + rng.sample(unflagged, min(20, len(unflagged)))
        rng.shuffle(picked)
        for n, r in enumerate(picked, 1):
            clean = lambda s: (s or "").replace("|", "/").replace("\n", " ")[:300]
            sheet.append(f"| {n} | {name} | {r['case']} | {r['rule']} | {r['nli_attached'] or r['nli_quote']} | {r['P3']} | "
                         f"{clean(r['claim'])} | {clean(r['quote'])} | {clean(r['attached'])} |  |")
    (HERE / "results" / "value_binding_nli.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (HERE / "results" / "value_binding_nli.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    (HERE / "results" / "value_binding_check_sheet.md").write_text("\n".join(sheet) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
