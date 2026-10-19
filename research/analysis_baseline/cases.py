"""Builds the analysis-baseline cases from CASIE exactly as README.md fixes them. Writes data/cases.jsonl and
data/manifest.json."""
from __future__ import annotations

import json
import re
import subprocess
import unicodedata
from pathlib import Path

import numpy as np

CASIE = Path("F:/CASIE")
HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
OUT = HERE / "data"
ATTACK = {"Databreach", "Phishing", "Ransom"}
ROLES = {"Victim", "Attacker", "Compromised-Data", "Time", "Tool", "Price", "Payment-Method", "Number-of-Victim",
         "Number-of-Data", "Place", "Damage-Amount", "Trusted-Entity"}
MIN_FACTS = 3
SEED = 2026
PILOT, MAIN = 3, 330
COMMON = {"the", "a", "an", "and", "or", "of", "to", "in", "on", "at", "for", "by", "with", "from", "it", "its", "this",
          "that", "these", "those", "they", "them", "their", "he", "she", "his", "her", "we", "us", "our", "you", "your",
          "may", "march", "will", "can", "said", "also", "some", "all", "one", "who", "which", "what", "when", "where"}


def normalise(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", unicodedata.normalize("NFKC", text).lower()))


def usable(fact: str) -> bool:
    tokens = fact.split()
    return len(fact) >= 4 and not (len(tokens) == 1 and tokens[0] in COMMON)


def used_elsewhere() -> set[str]:
    runs = RESEARCH / "report_fidelity" / "runs"
    used = {path.name for sample in ("main", "dry_run") for path in (runs / sample).iterdir() if path.is_dir()}
    clarification = RESEARCH / "casie_clarification" / "data" / "cases.jsonl"
    used |= {json.loads(line)["id"] for line in clarification.read_text(encoding="utf-8").splitlines() if line.strip()}
    return used


def aligned(content: str, start: int, end: int, fact: str, shifted: list[int]) -> tuple[int, int] | None:
    for shift in (0, -1, 1, -2, 2):
        if start + shift >= 0 and normalise(content[start + shift:end + shift]) == fact:
            if shift:
                shifted.append(shift)
            return start + shift, end + shift
    return None


def actual_attacks(hopper: dict) -> list[dict]:
    return [event for event in hopper.get("events", [])
            if event.get("type") == "Attack" and event.get("subtype") in ATTACK and event.get("realis") == "Actual"]


def build(path: Path, mismatches: list[str], shifted: list[int]) -> dict | None:
    doc = json.loads(path.read_text(encoding="utf-8"))
    content = doc.get("content", "")
    hoppers = [actual_attacks(h) for h in doc.get("cyberevent", {}).get("hopper", [])]
    starts = [min(e["nugget"]["startOffset"] for e in events) for events in hoppers if events]
    if not starts:
        return None
    lead_start = min(starts)
    gold: dict[tuple[str, str], dict] = {}
    for events in hoppers:
        lead = bool(events) and min(e["nugget"]["startOffset"] for e in events) == lead_start
        for event in events:
            for arg in event.get("argument", []):
                role = arg.get("role", {}).get("type")
                fact = normalise(arg.get("text", ""))
                if role not in ROLES or not usable(fact):
                    continue
                span = aligned(content, arg["startOffset"], arg["endOffset"], fact, shifted)
                if span is None:
                    mismatches.append(f"{path.stem}:{arg['startOffset']}")
                    continue
                entry = gold.setdefault((role, fact), {"spans": [], "lead": False})
                entry["spans"].append(list(span))
                entry["lead"] = entry["lead"] or lead
    if len({fact for (_, fact), entry in gold.items() if entry["lead"]}) < MIN_FACTS:
        return None
    return {
        "id": path.stem,
        "text": content,
        "gold": [{"role": role, "text": fact, **entry} for (role, fact), entry in sorted(gold.items())],
    }


def main() -> None:
    files = sorted((CASIE / "data" / "annotation").glob("*.json"))
    used = used_elsewhere()
    mismatches: list[str] = []
    shifted: list[int] = []
    built = {p.stem: case for p in files if p.stem not in used and (case := build(p, mismatches, shifted)) is not None}
    order = [sorted(built)[i] for i in np.random.default_rng(SEED).permutation(len(built))]
    rows = [{**built[k], "sample": "pilot" if n < PILOT else "main"} for n, k in enumerate(order[:PILOT + MAIN])]
    OUT.mkdir(exist_ok=True)
    with (OUT / "cases.jsonl").open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    head = subprocess.run(["git", "-C", str(CASIE), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    main_rows = [r for r in rows if r["sample"] == "main"]
    manifest = {
        "casie_head": head, "articles": len(files), "excluded_as_used": len(used), "eligible": len(built),
        "spans_realigned": len(shifted),
        "span_mismatches": len(mismatches),
        "pilot": [r["id"] for r in rows if r["sample"] == "pilot"],
        "main": len(main_rows),
        "gold_facts_main": sum(len(r["gold"]) for r in main_rows),
        "lead_facts_main": sum(g["lead"] for r in main_rows for g in r["gold"]),
        "gold_facts_by_role_main": {role: sum(g["role"] == role for r in main_rows for g in r["gold"])
                                    for role in sorted(ROLES)},
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
