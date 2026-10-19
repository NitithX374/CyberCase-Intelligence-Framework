from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
CLAIMS_ONLY = HERE / "results" / "raw_judgement_claims_only_main_20261004_013832"
ATTRFIRST = HERE / "results" / "raw_attrfirst_cot_main_20261004_041927"
DIRECT = HERE / "results" / "raw_direct_summary_20261004_053633"
SEED, RESAMPLES = 2026, 2000
SYSTEMS = ("D", "A", "C", "AF")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.path.insert(0, str(HERE))
    from fivew1h import SLOT, SLOTS
    from judgement_claims_only_score import stripped
    from scores_common import v0_words
    from summary_measures import matcher

    mentioned = matcher(v0_words, stemmed=True)
    cases = {json.loads(line)["id"]: json.loads(line)
             for line in (HERE / "data" / "cases.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()}
    texts: dict[str, dict[str, str]] = {}
    for path in CLAIMS_ONLY.glob("*_?.json"):
        saved = json.loads(path.read_text(encoding="utf-8"))
        if saved["language"] == "english" and saved["arm"] in ("A", "C") and "judgement" in saved:
            texts.setdefault(saved["key"], {})[saved["arm"]] = stripped(saved["judgement"]["summary"])
    for folder, system in ((ATTRFIRST, "AF"), (DIRECT, "D")):
        for path in folder.glob("*.json"):
            saved = json.loads(path.read_text(encoding="utf-8")) if path.name != "run.json" else {}
            if saved.get("language") == "english" and saved.get("summary"):
                texts.setdefault(saved["key"], {})[system] = saved["summary"]

    rows: dict[str, dict[str, dict]] = {"full": {}, "at A length": {}}
    for key, systems in texts.items():
        n = len(systems["A"].split())
        facts = cases[key]["gold"]
        for version in rows:
            for system, text in systems.items():
                candidate = text if version == "full" else " ".join(text.split()[:n])
                hits = [mentioned(candidate, f) for f in facts]
                rows[version].setdefault(key, {})[system] = {
                    slot: (sum(h for f, h in zip(facts, hits) if SLOT.get(f["role"]) == slot),
                           sum(1 for f in facts if SLOT.get(f["role"]) == slot)) for slot in SLOTS}

    def pooled(rows_now, keys, system, slot, picks=None):
        values = np.array([rows_now[k][system][slot] for k in keys], dtype=float)
        if picks is None:
            return values[:, 0].sum() / max(values[:, 1].sum(), 1e-12)
        sums = values[picks].sum(axis=1)
        return sums[:, 0] / np.maximum(sums[:, 1], 1e-12)

    md = ["# 5W1H key-fact coverage: D, A, C, AF (English CASIE, 50 cases)", "",
          f"Script sha256 `{hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}`. Stemmed matcher, all events' "
          f"facts; pooled; case bootstrap {RESAMPLES}, seed {SEED}. Decided after the pipeline result was seen.", ""]
    report: dict = {}
    for version, rows_now in rows.items():
        md += [f"## {version}", "", "| Slot (facts) | D | A | C | AF | C − D | AF − D |", "|---|---|---|---|---|---|---|"]
        report[version] = {}
        for slot in SLOTS:
            keys_all = [k for k, v in rows_now.items() if v["A"][slot][1] > 0]
            total = sum(rows_now[k]["A"][slot][1] for k in keys_all)
            cells, entry = [], {}
            for system in SYSTEMS:
                keys = [k for k in keys_all if system in rows_now[k]]
                point = pooled(rows_now, keys, system, slot)
                entry[system] = round(float(point), 4)
                cells.append(f"{point:.3f}")
            for left in ("C", "AF"):
                keys = [k for k in keys_all if left in rows_now[k] and "D" in rows_now[k]]
                picks = np.random.default_rng(SEED).integers(0, len(keys), size=(RESAMPLES, len(keys)))
                point = pooled(rows_now, keys, left, slot) - pooled(rows_now, keys, "D", slot)
                lo, hi = np.percentile(pooled(rows_now, keys, left, slot, picks) - pooled(rows_now, keys, "D", slot, picks),
                                       [2.5, 97.5])
                entry[f"{left}-D"] = [round(float(point), 4), round(float(lo), 4), round(float(hi), 4)]
                cells.append(f"{point:+.3f} [{lo:+.3f}, {hi:+.3f}]")
            report[version][slot] = entry
            md.append(f"| {slot} ({total}) | " + " | ".join(cells) + " |")
        md.append("")
    (HERE / "results" / "fivew1h_pipeline.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (HERE / "results" / "fivew1h_pipeline.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
