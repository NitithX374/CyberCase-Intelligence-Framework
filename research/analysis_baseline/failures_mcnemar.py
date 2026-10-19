from __future__ import annotations

import hashlib
import json
import sys
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
R = HERE / "results"
PAIRS = {
    "Gemma 4 26B": (R / "raw_judgement_claims_only_main_20261004_013832", "*_C.json", R / "raw_attrfirst_cot_main_20261004_041927"),
    "Gemini 2.5 Flash-Lite": (R / "raw_c_pipeline_gemini-2.5-flash-lite_main_20261004_061915", "*_C.json",
                              R / "raw_attrfirst_cot_gemini-2.5-flash-lite_main_20261004_060104"),
}


def exact_mcnemar(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    md = ["# Item failures, C against Attribute First, paired (exact McNemar)", "",
          f"Script sha256 `{hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}`. Failure = no summary produced.", "",
          "| Model | Items paired | C fails | AF fails | Both | C only | AF only | Exact McNemar p |", "|---|---|---|---|---|---|---|---|"]
    out = {}
    for model, (c_dir, pattern, af_dir) in PAIRS.items():
        c_fail = {}
        for p in c_dir.glob(pattern):
            d = json.loads(p.read_text(encoding="utf-8"))
            c_fail[d["key"]] = "judgement" not in d
        af_fail = {}
        for p in af_dir.glob("*.json"):
            if p.name == "run.json":
                continue
            d = json.loads(p.read_text(encoding="utf-8"))
            af_fail[d["key"]] = not d.get("summary")
        keys = sorted(set(c_fail) & set(af_fail))
        both = sum(c_fail[k] and af_fail[k] for k in keys)
        c_only = sum(c_fail[k] and not af_fail[k] for k in keys)
        af_only = sum(af_fail[k] and not c_fail[k] for k in keys)
        p = exact_mcnemar(c_only, af_only)
        out[model] = {"paired": len(keys), "c_fail": sum(c_fail[k] for k in keys), "af_fail": sum(af_fail[k] for k in keys),
                      "both": both, "c_only": c_only, "af_only": af_only, "p": round(p, 4)}
        md.append(f"| {model} | {len(keys)} | {out[model]['c_fail']} | {out[model]['af_fail']} | {both} | {c_only} | {af_only} | {p:.4f} |")
    (R / "failures_mcnemar.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (R / "failures_mcnemar.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
