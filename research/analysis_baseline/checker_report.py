from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARMS = (("P3", None), ("P2", None), ("P2fizz", None), ("E-quote", "P2"), ("E-window", "P2fizz"),
        ("L-quote", "P2"), ("L-window", "P2fizz"))
NAMES = {"P3": "number rule, then NLI (argmax)", "P2": "NLI on the quote (argmax)",
         "P2fizz": "NLI, quote then ±1 sentence (argmax)", "E-quote": "bge-m3 cosine, quote",
         "E-window": "bge-m3 cosine, ±1 sentence", "L-quote": "Gemini 2.5 Flash-Lite, quote",
         "L-window": "Gemini 2.5 Flash-Lite, ±1 sentence"}


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(HERE))
    from checker_llm import MODEL, cache_key, cached
    from checker_units import checks as load_checks
    from value_binding_nli_curve import bootstrap_rate, paired_difference

    checks = load_checks(args.backend)
    embedding = json.loads((HERE / "results" / "checker_embedding_scores.json").read_text(encoding="utf-8"))
    scores = {r["id"]: r for r in embedding["rows"]}
    cut = {kind: embedding["thresholds"][kind]["t"] for kind in ("quote", "window")}
    store = cached()
    rows = []
    for c in checks:
        row = {k: c[k] for k in ("id", "set", "case", "kind", "elsewhere", "P3", "P2", "P2fizz")}
        for kind in ("quote", "window"):
            row[f"E-{kind}"] = scores[c["id"]][kind] < cut[kind]
            rec = store.get(cache_key(c[kind], c["claim"]))
            row[f"L-{kind} status"] = "missing" if rec is None else rec["status"]
            row[f"L-{kind} label"] = rec.get("label") if rec else None
            row[f"L-{kind} usd"] = rec.get("usd") or 0.0 if rec else 0.0
            row[f"L-{kind} ms"] = rec.get("ms") if rec else None
            row[f"L-{kind}"] = row[f"L-{kind} label"] != "SUPPORTED"
        rows.append(row)
    if any(r[a] is None for r in rows for a in ("P3", "P2", "P2fizz")):
        raise SystemExit("an NLI flag is missing")

    def cell(v):
        if v is None:
            return "–"
        text = f"{v[0]:.3f} [{v[1]:.3f}, {v[2]:.3f}]"
        return text + (f" ({v[3]}/{v[4]})" if len(v) > 3 else "")

    def table(subset, title, arms, note):
        md = [f"## {title}", "", note, "",
              "| Set | Arm | Real alert | Edit-alert | Edit-alert, number elsewhere | Edit-alert: arm − matching NLI "
              "| Real alert: arm − matching NLI | Edit-alert: arm − P3 | Real alert: arm − P3 |",
              "|---|---|---|---|---|---|---|---|---|"]
        out = {}
        for name in sorted({r["set"] for r in rows}):
            for arm, ref in arms:
                picked = [r for r in rows if r["set"] == name and subset(r, arm)]
                real = [r for r in picked if r["kind"] == "real"]
                edits = [r for r in picked if r["kind"] == "edit"]
                fooled = [r for r in edits if r["elsewhere"]]
                entry = {"real alert": bootstrap_rate(real, arm), "edit alert": bootstrap_rate(edits, arm),
                         "edit alert elsewhere": bootstrap_rate(fooled, arm) if fooled else None,
                         "edit: arm - ref": paired_difference(edits, arm, ref) if ref else None,
                         "real: arm - ref": paired_difference(real, arm, ref) if ref else None,
                         "edit: arm - P3": paired_difference(edits, arm, "P3") if arm != "P3" else None,
                         "real: arm - P3": paired_difference(real, arm, "P3") if arm != "P3" else None}
                out[f"{name}|{arm}"] = entry
                md.append(f"| {name} | {arm}: {NAMES[arm]} | {cell(entry['real alert'])} | {cell(entry['edit alert'])} | "
                          f"{cell(entry['edit alert elsewhere'])} | {cell(entry['edit: arm - ref'])} | "
                          f"{cell(entry['real: arm - ref'])} | {cell(entry['edit: arm - P3'])} | "
                          f"{cell(entry['real: arm - P3'])} |")
        return md + [""], out

    main_md, main_out = table(lambda r, arm: True, "All checks; for L, an invalid or failed answer counts as a warning",
                              ARMS, "Matching NLI arm: P2 for the quote arms, P2fizz for the window arms.")
    valid_md, valid_out = table(
        lambda r, arm: not arm.startswith("L-") or r[f"{arm} status"] == "valid",
        "L with invalid and failed answers excluded",
        [a for a in ARMS if a[0].startswith("L-")],
        "Only checks with a valid L answer; the NLI and P3 differences use the same checks.")

    labels_md = ["## L answers by set, premise and claim kind", "",
                 "| Set | Premise | Claims | SUPPORTED | NOT_SUPPORTED | CONTRADICTED | Invalid | Failed | Missing |",
                 "|---|---|---|---|---|---|---|---|---|"]
    for name in sorted({r["set"] for r in rows}):
        for kind in ("quote", "window"):
            for which in ("real", "edit"):
                picked = [r for r in rows if r["set"] == name and r["kind"] == which]
                n = Counter(r[f"L-{kind} label"] if r[f"L-{kind} status"] == "valid" else r[f"L-{kind} status"]
                            for r in picked)
                labels_md.append(f"| {name} | {kind} | {which} ({len(picked)}) | {n['SUPPORTED']} | "
                                 f"{n['NOT_SUPPORTED']} | {n['CONTRADICTED']} | {n['invalid']} | {n['failed']} | "
                                 f"{n['missing']} |")
    calls = [r for r in rows for kind in ("quote", "window") if r[f"L-{kind} ms"] is not None]
    usd = sum(r[f"L-{kind} usd"] for r in rows for kind in ("quote", "window"))
    ms = [r[f"L-{kind} ms"] for r in rows for kind in ("quote", "window") if r[f"L-{kind} ms"] is not None]
    ms.sort()
    cost_md = ["## Cost and time", "",
               f"- **L** ({MODEL}): {len(calls)} answered checks, USD {usd:.4f} in all, USD {usd / max(1, len(calls)):.6f} "
               f"per check; latency median {ms[len(ms) // 2] if ms else 0} ms, 90th percentile "
               f"{ms[int(len(ms) * 0.9)] if ms else 0} ms (8 concurrent requests). Source text leaves the machine.",
               f"- **E** (bge-m3, local): {embedding['seconds'] / embedding['texts'] * 1000:.0f} ms per text embedded on "
               f"{embedding['threads']} CPU threads shared with the NLI chain; a check needs the claim and its premise.",
               "- **NLI** (mDeBERTa, local): not timed in this study.", ""]
    thresholds_md = ["## E thresholds (chosen on English development real claims)", "",
                     f"Target: P3's real alert rate there, {embedding['target']:.4f}.", ""] + [
        f"- {kind}: t = {embedding['thresholds'][kind]['t']:.6f}, alert there "
        f"{embedding['thresholds'][kind]['dev real alert']:.4f}, reached {embedding['thresholds'][kind]['reached']}"
        for kind in ("quote", "window")] + [""]
    md = ["# Checkers for the claim–quote support check: rules, NLI, embedding similarity, LLM verifier", "",
          f"Script sha256 `{hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}`. Case bootstrap 2000, seed 2026 "
          f"(`value_binding_nli_curve`). Real alert: warnings on the real numeric claims. Edit-alert: warnings on the "
          f"one-digit edits of their V0 claims.", ""] + thresholds_md + main_md + valid_md + labels_md + cost_md
    (HERE / "results" / "checker_report.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (HERE / "results" / "checker_report.json").write_text(json.dumps({"main": main_out, "valid only": valid_out},
                                                                     indent=1), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
