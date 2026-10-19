from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "results" / "raw_judgement_claims_only_main_20261004_013832"
NLI = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"
DIGITS = re.compile(r"\d+(?:[.,:]\d+)*")
THAI_DIGITS = str.maketrans("๐๑๒๓๔๕๖๗๘๙", "0123456789")
PREFIX = {
    "english": {"reported": "The source reports that", "suspected": "It is suspected that",
                "not_confirmed": "It is not confirmed that", "not_established": "It is not established that",
                "unknown": "It is unknown whether", "contradicted": "The source contradicts that"},
    "thai": {"reported": "ต้นฉบับรายงานว่า", "suspected": "สงสัยว่า", "not_confirmed": "ยังไม่ยืนยันว่า",
             "not_established": "ยังไม่ได้ข้อยุติว่า", "unknown": "ไม่ทราบว่า", "contradicted": "ต้นฉบับขัดแย้งกับว่า"},
}
STRONG = {"english": "It is confirmed that", "thai": "ยืนยันแล้วว่า"}


def edited(text: str) -> str | None:
    text = text.translate(THAI_DIGITS)
    found = list(DIGITS.finditer(text))
    if not found:
        return None
    last = found[-1]
    at = [i for i in range(last.start(), last.end()) if text[i].isdigit()][-1]
    return text[:at] + str((int(text[at]) + 1) % 10) + text[at + 1:]


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.path.insert(0, str(HERE))
    import torch
    from judgement_claims_only_score import units
    from nli_ellipsis_gap import wilson
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    rows = []
    for path in sorted(RAW.glob("*_C.json")):
        saved = json.loads(path.read_text(encoding="utf-8"))
        if "judgement" not in saved:
            continue
        language = saved["language"]
        claims = {c["claim_id"]: c for c in saved["reading"]["claims"]}
        split = "pilot" if int(hashlib.sha256(saved["key"].encode()).hexdigest(), 16) % 2 == 0 else "evaluation"
        for text, ids in units(saved["judgement"]["summary"]):
            cited = [claims[i] for i in ids if i in claims]
            if not text or not cited:
                continue
            statuses = [c.get("epistemic_status") or "reported" for c in cited]
            plain = " ".join(c["text"] for c in cited)
            status = " ".join(f"{PREFIX[language].get(s, PREFIX[language]['reported'])} {c['text']}"
                              for c, s in zip(cited, statuses))
            row = {"case": saved["key"], "language": language, "split": split, "unit": text,
                   "statuses": statuses, "plain": plain, "status": status, "variants": {"original": text}}
            changed = edited(text)
            if changed and changed != text.translate(THAI_DIGITS):
                row["variants"]["digit"] = changed
            if any(s != "reported" for s in statuses):
                row["variants"]["strengthened"] = f"{STRONG[language]} {text}"
            rows.append(row)

    torch.set_num_threads(8)
    tokenizer = AutoTokenizer.from_pretrained(NLI)
    model = AutoModelForSequenceClassification.from_pretrained(NLI).eval()
    order = [model.config.id2label[i].lower() for i in range(len(model.config.id2label))]

    def judge(premise: str, hypothesis: str) -> str:
        batch = tokenizer(premise, hypothesis, truncation="only_first", max_length=512, return_tensors="pt")
        with torch.no_grad():
            return order[int(model(**batch).logits[0].argmax())]

    for r in rows:
        r["labels"] = {f"{v}/{rendering}": judge(r[rendering], h)
                       for v, h in r["variants"].items() for rendering in ("plain", "status")}

    md = ["# Summary units against their cited claims", "",
          f"Script sha256 `{hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}`. Raw `{RAW.name}`. "
          f"NLI `{NLI}` argmax; warning = not entailment. Wilson 95% intervals.", "",
          "| Language | Split | Variant | Units | Warning, plain premise | Warning, status premise |", "|---|---|---|---|---|---|"]
    report = {}
    for language in ("english", "thai"):
        for split in ("pilot", "evaluation"):
            for variant in ("original", "digit", "strengthened"):
                group = [r for r in rows if r["language"] == language and r["split"] == split
                         and variant in r["variants"]]
                cells = {}
                for rendering in ("plain", "status"):
                    cells[rendering] = wilson(sum(r["labels"][f"{variant}/{rendering}"] != "entailment" for r in group),
                                              len(group))
                report[f"{language}/{split}/{variant}"] = cells
                fmt = lambda w: "–" if w[0] is None else f"{w[0]:.3f} [{w[1]:.3f}, {w[2]:.3f}] ({w[3]}/{w[4]})"
                md.append(f"| {language} | {split} | {variant} | {len(group)} | {fmt(cells['plain'])} | "
                          f"{fmt(cells['status'])} |")
    (HERE / "results" / "nli_summary_units.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (HERE / "results" / "nli_summary_units.json").write_text(
        json.dumps({"report": report, "rows": rows}, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
