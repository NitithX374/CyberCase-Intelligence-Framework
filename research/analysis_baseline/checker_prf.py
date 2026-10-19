from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SETS = ("English confirmation", "English development", "Thai clean")
ARMS = (("P2", "NLI"), ("P3", "Rule, then NLI"), ("P2fizz", "NLI, widened ±1 sentence"),
        ("E-quote", "Embedding, quote"), ("E-window", "Embedding, ±1 sentence"),
        ("L-quote", "LLM verifier, quote"), ("L-window", "LLM verifier, ±1 sentence"))
PREVALENCE = 0.05


def scores(fp: int, n_real: int, tp: int, n_edit: int) -> dict:
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / n_edit
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    false_alarm = fp / n_real
    at_prevalence = PREVALENCE * recall / (PREVALENCE * recall + (1 - PREVALENCE) * false_alarm) \
        if recall or false_alarm else 0.0
    return {"flagged real": fp, "real": n_real, "flagged edits": tp, "edits": n_edit, "precision": precision,
            "recall": recall, "f1": f1, "edits accepted": 1 - recall, "false alarm": false_alarm,
            "accuracy": (tp + n_real - fp) / (n_real + n_edit), "balanced accuracy": (recall + 1 - false_alarm) / 2,
            f"precision at {PREVALENCE:.0%} unsupported": at_prevalence}


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    rule = json.loads((HERE / "results" / "value_binding_nli.json").read_text(encoding="utf-8"))
    report = json.loads((HERE / "results" / "checker_report.json").read_text(encoding="utf-8"))["main"]
    out = {}
    for name in SETS:
        flag, detected = rule[name]["flag P1"], rule[name]["synthetic detected P1"]
        out[f"{name}|Rule"] = scores(flag[0], flag[1], detected[0], detected[1])
        for arm, _ in ARMS:
            real, edit = report[f"{name}|{arm}"]["real alert"], report[f"{name}|{arm}"]["edit alert"]
            out[f"{name}|{arm}"] = scores(real[3], real[4], edit[3], edit[4])
    labels = {"Rule": "Rule", **dict(ARMS)}
    md = ["# Checkers as a supported / not-supported classifier (re-expression of stored counts)", "",
          f"Script sha256 `{hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}`. Counts: Rule from "
          f"`value_binding_nli.json` (flag P1, synthetic detected P1); every other row from `checker_report.json` "
          f"(main table). No model is run.", "",
          "Positive class: not supported. A one-digit edit of a V0 claim is taken as not supported, and every real "
          "numeric claim is taken as supported. The second assumption is not verified, so a correct flag on a real "
          "claim counts here as a false positive.", "",
          f"Precision depends on the mix: about one edit per real claim here. The last column shows what the same "
          f"recall and false-alarm rate would give if {PREVALENCE:.0%} of claims were not supported. It is arithmetic, "
          f"not a measurement. Balanced accuracy, the mean of recall and the real-claim pass rate, does not depend on the "
          f"mix; it inherits the unverified assumption about real claims, which can only lower it.", ""]
    for name in SETS:
        md += [f"## {name}", "",
               "| Checker | Flagged real | Flagged edits | Balanced accuracy | Accuracy | Precision | Recall | F1 | "
               f"Edits accepted | Precision at {PREVALENCE:.0%} unsupported |", "|---|---|---|---|---|---|---|---|---|---|"]
        for key in ["Rule"] + [a for a, _ in ARMS]:
            r = out[f"{name}|{key}"]
            md.append(f"| {labels[key]} | {r['flagged real']}/{r['real']} | {r['flagged edits']}/{r['edits']} | "
                      f"{r['balanced accuracy']:.3f} | {r['accuracy']:.3f} | "
                      f"{r['precision']:.3f} | {r['recall']:.3f} | {r['f1']:.3f} | {r['edits accepted']:.3f} | "
                      f"{r[f'precision at {PREVALENCE:.0%} unsupported']:.3f} |")
        md.append("")
    (HERE / "results" / "checker_prf.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (HERE / "results" / "checker_prf.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
