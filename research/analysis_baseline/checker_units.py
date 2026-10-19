from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LABELS = ("entailment", "neutral", "contradiction")


def nli_scores() -> tuple[dict, dict]:
    stored = json.loads((HERE / "results" / "value_binding_nli_rows.json").read_text(encoding="utf-8"))
    known = {(p["premise"], p["hypothesis"]): {k: p[k] for k in LABELS} for p in stored["pairs"]}
    for line in (HERE / "results" / "value_binding_nli_wide_cache.jsonl").read_text(encoding="utf-8").split("\n"):
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        known[(rec["premise"], rec["hypothesis"])] = {k: rec[k] for k in LABELS}
    return stored, known


def checks(backend: str) -> list[dict]:
    sys.path.insert(0, backend)
    sys.path.insert(0, str(HERE))
    import app.trace.bind as bind

    if not Path(bind.__file__).resolve().is_relative_to(Path(backend).resolve()):
        raise SystemExit(f"wrong binder: {bind.__file__}")
    from app.trace.sentences import sentence_spans
    from summary_encoder_nli import items

    stored, known = nli_scores()
    texts = {(name, item["key"]): item for name, data in items().items() for item in data}

    def located(text, claim):
        quotes = [c["exact_quote"] for c in claim.get("supporting_citations", []) if c.get("exact_quote")]
        return [p for p in (bind.located_quote(text, q) for q in quotes) if p]

    def window(item, claim_text, claim_quote):
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

    def label(premise, hypothesis):
        s = known.get((premise, hypothesis))
        return None if s is None else max(s, key=s.get)

    out = []
    for i, u in enumerate(stored["units"]):
        w = window(texts[(u["set"], u["case"])], u["claim"], u["quote"])
        targets = [("real", u, u["claim"])] + ([("edit", u["edit"], u["edit"]["claim"])] if "edit" in u else [])
        for kind, holder, hypothesis in targets:
            first, second = label(u["quote"], hypothesis), label(w, hypothesis)
            attached = holder["rule_attached"]
            p3 = False
            if holder["rule"] != "V0":
                anchored = label(u["quote"] + " " + attached if attached else u["quote"], hypothesis)
                p3 = None if anchored is None else anchored != "entailment"
            out.append({"id": f"{i}:{kind}", "set": u["set"], "case": u["case"], "kind": kind,
                        "elsewhere": kind == "edit" and u["edit"]["elsewhere"], "rule": holder["rule"],
                        "quote": u["quote"], "window": w, "claim": hypothesis,
                        "P2": None if first is None else first != "entailment",
                        "P2fizz": None if None in (first, second) else first != "entailment" and second != "entailment",
                        "P3": p3})
    return out
