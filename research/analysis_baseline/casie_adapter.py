from __future__ import annotations

import json
import random
import re
from pathlib import Path

import numpy as np

from scores_analysis import arm, normalize_answer, pointed_at, states
from scores_common import lead, positions, share

ADAPTER = "casie-adapter-v2"
RUN, ARM = "main_20261001_021428", "cybercase_nogrammar"
SEED = 2026
RESAMPLES = 2000
HERE = Path(__file__).resolve().parent
OUT = HERE / "results"
NUMBER = re.compile(r"[0-9]{1,3}(?:[ ,.][0-9]{3})+|[0-9]+")


def whole_words(gold: str, text: str) -> bool:
    return re.search(r"(?<![a-z0-9])" + re.escape(gold) + r"(?![a-z0-9])", text) is not None


def number_values(text: str) -> set[str]:
    return {re.sub(r"[^0-9]", "", found) for found in NUMBER.findall(text)}


def precise(fact: dict, text: str) -> bool:
    gold = normalize_answer(fact["text"])
    if gold and whole_words(gold, normalize_answer(text)):
        return True
    digits = re.sub(r"[^0-9]", "", fact["text"])
    return bool(digits) and digits in number_values(text)


def cited(claim: dict) -> list[dict]:
    return claim["supporting_citations"] + claim["contradicting_citations"]


def citation_spans(text: str, citations: list[dict]) -> tuple[list[tuple[int, int]], dict]:
    spans: list[tuple[int, int]] = []
    path = {"offset": 0, "quote": 0, "unresolved": 0}
    for citation in citations:
        start, end = citation.get("start"), citation.get("end")
        if start is not None and end is not None:
            spans.append((start, end))
            path["offset"] += 1
        elif citation.get("exact_quote"):
            found = positions(text, citation["exact_quote"])
            spans.extend(found)
            path["quote"] += 1
            path["unresolved"] += int(not found)
        else:
            path["unresolved"] += 1
    return spans, path


def analyse(case: dict, trace: dict) -> dict:
    claims = trace["claims"]
    texts = {claim["claim_id"]: claim["text"] for claim in claims}
    spans_by: dict[str, list[tuple[int, int]]] = {}
    paths = {"offset": 0, "quote": 0, "unresolved": 0}
    for claim in claims:
        spans, path = citation_spans(case["text"], cited(claim))
        spans_by[claim["claim_id"]] = spans
        for key, count in path.items():
            paths[key] += count
    return {"texts": texts, "spans": spans_by, "paths": paths}


def pointing(case: dict, state: dict, fact: dict) -> list[str]:
    return [cid for cid, spans in state["spans"].items() if pointed_at(fact, spans)]


def stating(case: dict, state: dict, fact: dict) -> list[str]:
    return [cid for cid in pointing(case, state, fact) if states(state["texts"][cid], case, fact)]


def precising(case: dict, state: dict, fact: dict) -> list[str]:
    return [cid for cid in pointing(case, state, fact) if precise(fact, state["texts"][cid])]


def case_scores(case: dict, trace: dict) -> dict:
    claims = trace["claims"]
    state = analyse(case, trace)
    main = lead(case)
    stated_by: dict[str, set[int]] = {}
    precise_by: dict[str, set[int]] = {}
    pointed_by: dict[str, set[int]] = {}
    for index, fact in enumerate(case["gold"]):
        for claim_id in stating(case, state, fact):
            stated_by.setdefault(claim_id, set()).add(index)
        for claim_id in precising(case, state, fact):
            precise_by.setdefault(claim_id, set()).add(index)
        for claim_id in pointing(case, state, fact):
            pointed_by.setdefault(claim_id, set()).add(index)
    roles: dict[str, list[int]] = {}
    for fact in main:
        counts = roles.setdefault(fact["role"], [0, 0])
        counts[0] += int(bool(precising(case, state, fact)))
        counts[1] += 1
    return {
        "recall_pointed": share(bool(pointing(case, state, fact)) for fact in main),
        "recall_stated": share(bool(stating(case, state, fact)) for fact in main),
        "recall_precise": share(bool(precising(case, state, fact)) for fact in main),
        "precision_stated": len(stated_by) / len(claims) if claims else 0.0,
        "precision_precise": len(precise_by) / len(claims) if claims else 0.0,
        "precision_pointed": len(pointed_by) / len(claims) if claims else 0.0,
        "claims": len(claims),
        "attested_claims": len(stated_by),
        "attested_precise": len(precise_by),
        "gold_args_per_attested_claim": float(np.mean([len(s) for s in precise_by.values()])) if precise_by else 0.0,
        "lead_facts": len(main),
        "roles": roles,
        "paths": state["paths"],
    }


def mean_ci(values: list[float], rng: np.random.RandomState) -> dict:
    array = np.asarray(values, dtype=float)
    draws = rng.randint(0, len(array), size=(RESAMPLES, len(array)))
    means = array[draws].mean(axis=1)
    return {"mean": float(array.mean()), "low": float(np.percentile(means, 2.5)), "high": float(np.percentile(means, 97.5))}


def harmonic(p: float, r: float) -> float:
    return 2 * p * r / (p + r) if p + r else 0.0


def audit_sheet(views: dict[str, dict], rng: random.Random) -> list[dict]:
    stated_rows, near_rows = [], []
    for case_id, view in views.items():
        case, trace = view["case"], view["trace"]
        state = analyse(case, trace)
        for fact in lead(case):
            ids_stated = set(stating(case, state, fact))
            ids_pointed = set(pointing(case, state, fact))
            for claim_id in sorted(ids_stated):
                stated_rows.append({"case": case_id, "fact": fact["text"], "role": fact["role"], "claim_id": claim_id, "claim": state["texts"][claim_id], "match": "stated"})
            for claim_id in sorted(ids_pointed - ids_stated):
                near_rows.append({"case": case_id, "fact": fact["text"], "role": fact["role"], "claim_id": claim_id, "claim": state["texts"][claim_id], "match": "pointed_not_stated"})
    rng.shuffle(stated_rows)
    rng.shuffle(near_rows)
    return stated_rows[:30] + near_rows[:30]


FAILED = {"recall_pointed": 0.0, "recall_stated": 0.0, "recall_precise": 0.0, "precision_stated": 0.0, "precision_precise": 0.0, "precision_pointed": 0.0, "claims": 0, "attested_claims": 0, "attested_precise": 0, "gold_args_per_attested_claim": 0.0, "lead_facts": 0, "roles": {}, "paths": {"offset": 0, "quote": 0, "unresolved": 0}}


def summarise(views: dict[str, dict]) -> dict:
    per_case = {case_id: case_scores(view["case"], view["trace"]) if view["done"] else dict(FAILED) for case_id, view in views.items()}
    values = list(per_case.values())
    rng = np.random.RandomState(SEED)
    summary = {
        "adapter": ADAPTER,
        "run": RUN,
        "arm": ARM,
        "cases": len(values),
        "failed": sum(not view["done"] for view in views.values()),
        "recall_pointed": mean_ci([v["recall_pointed"] for v in values], rng),
        "recall_stated": mean_ci([v["recall_stated"] for v in values], rng),
        "recall_precise": mean_ci([v["recall_precise"] for v in values], rng),
        "precision_stated_lower": mean_ci([v["precision_stated"] for v in values], rng),
        "precision_precise_lower": mean_ci([v["precision_precise"] for v in values], rng),
        "precision_pointed": mean_ci([v["precision_pointed"] for v in values], rng),
        "claims_per_case": float(np.mean([v["claims"] for v in values])),
        "attested_claims_per_case": float(np.mean([v["attested_claims"] for v in values])),
        "attested_precise_per_case": float(np.mean([v["attested_precise"] for v in values])),
        "gold_args_per_attested_claim": float(np.mean([v["gold_args_per_attested_claim"] for v in values])),
        "lead_facts_per_case": float(np.mean([v["lead_facts"] for v in values])),
        "citation_paths": {key: sum(v["paths"][key] for v in values) for key in ("offset", "quote", "unresolved")},
    }
    summary["f1_stated_lower"] = harmonic(summary["precision_stated_lower"]["mean"], summary["recall_stated"]["mean"])
    summary["f1_precise_lower"] = harmonic(summary["precision_precise_lower"]["mean"], summary["recall_precise"]["mean"])
    role_totals: dict[str, list[int]] = {}
    for v in values:
        for role, (hit, total) in v["roles"].items():
            counts = role_totals.setdefault(role, [0, 0])
            counts[0] += hit
            counts[1] += total
    summary["recall_precise_by_role"] = {role: {"hit": hit, "total": total, "share": hit / total} for role, (hit, total) in sorted(role_totals.items(), key=lambda item: -item[1][1])}
    return {"summary": summary, "per_case": per_case}


def main() -> None:
    views = arm(RUN, ARM)
    result = summarise(views)
    OUT.mkdir(exist_ok=True)
    (OUT / "casie_adapter_v2.json").write_text(json.dumps(result["summary"], indent=2, ensure_ascii=False), encoding="utf-8")
    sheet = audit_sheet({case_id: view for case_id, view in views.items() if view["done"]}, random.Random(SEED))
    (OUT / "casie_adapter_v2_audit.json").write_text(json.dumps(sheet, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result["summary"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
