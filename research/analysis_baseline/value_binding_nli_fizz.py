from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LABELS = ("entailment", "neutral", "contradiction")


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
    from app.trace.sentences import sentence_spans
    from summary_encoder_nli import items
    from value_binding_nli_curve import bootstrap_rate, paired_difference

    stored = json.loads((HERE / "results" / "value_binding_nli_rows.json").read_text(encoding="utf-8"))
    known = {(p["premise"], p["hypothesis"]): {k: p[k] for k in LABELS} for p in stored["pairs"]}
    for line in (HERE / "results" / "value_binding_nli_wide_cache.jsonl").read_text(encoding="utf-8").split("\n"):
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        known[(rec["premise"], rec["hypothesis"])] = {k: rec[k] for k in LABELS}
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

    rows = {}
    for u in stored["units"]:
        item = texts[(u["set"], u["case"])]
        w = window(item, u["claim"], u["quote"])
        targets = [("real", u, u["claim"])] + ([("edit", u["edit"], u["edit"]["claim"])] if "edit" in u else [])
        decided = []
        for kind, holder, hypothesis in targets:
            first, second = label(u["quote"], hypothesis), label(w, hypothesis)
            attached = holder["rule_attached"]
            p3_label = label(u["quote"] + " " + attached if attached else u["quote"], hypothesis)
            if None in (first, second) or (holder["rule"] != "V0" and p3_label is None):
                break
            fizz = first != "entailment" and second != "entailment"
            fizz_c = first != "entailment" and second == "contradiction"
            p3 = False if holder["rule"] == "V0" else p3_label != "entailment"
            decided.append({"kind": kind, "case": u["case"], "fizz": fizz, "fizz_c": fizz_c, "p3": p3,
                            "elsewhere": kind == "edit" and u["edit"]["elsewhere"]})
        else:
            rows.setdefault(u["set"], []).extend(decided)

    md = ["# FIZZ-style conditional widening against the number rule (P3)", "",
          f"Script sha256 `{hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}`. Units with every needed pair "
          f"computed are included; a partial cache gives an interim reading.", "",
          "| Set | Real claims | Alert P3 | Alert P2fizz | Alert P2fizz (contra) | Edits | Detect P3 | Detect P2fizz | P3 − fizz | Elsewhere: P3 / P2fizz | P3 − fizz elsewhere |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    report = {}
    cell = lambda v: "–" if v is None else f"{v[0]:.3f} [{v[1]:.3f}, {v[2]:.3f}]"
    for s in sorted(rows):
        real = [r for r in rows[s] if r["kind"] == "real"]
        edits = [r for r in rows[s] if r["kind"] == "edit"]
        fooled = [r for r in edits if r["elsewhere"]]
        entry = {"real": len(real), "edits": len(edits),
                 "alert p3": bootstrap_rate(real, "p3"), "alert fizz": bootstrap_rate(real, "fizz"),
                 "alert fizz contra": bootstrap_rate(real, "fizz_c"),
                 "detect p3": bootstrap_rate(edits, "p3"), "detect fizz": bootstrap_rate(edits, "fizz"),
                 "p3 - fizz detect": paired_difference(edits, "p3", "fizz"),
                 "elsewhere p3": bootstrap_rate(fooled, "p3") if fooled else None,
                 "elsewhere fizz": bootstrap_rate(fooled, "fizz") if fooled else None,
                 "p3 - fizz elsewhere": paired_difference(fooled, "p3", "fizz") if fooled else None}
        report[s] = entry
        md.append(f"| {s} | {len(real)} | {cell(entry['alert p3'])} | {cell(entry['alert fizz'])} | "
                  f"{cell(entry['alert fizz contra'])} | {len(edits)} | {cell(entry['detect p3'])} | "
                  f"{cell(entry['detect fizz'])} | {cell(entry['p3 - fizz detect'])} | "
                  f"{cell(entry['elsewhere p3'])} / {cell(entry['elsewhere fizz'])} | {cell(entry['p3 - fizz elsewhere'])} |")
    (HERE / "results" / "value_binding_nli_fizz.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (HERE / "results" / "value_binding_nli_fizz.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
