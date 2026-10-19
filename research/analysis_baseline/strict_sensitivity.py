"""Strict recall sensitivity (README, 2026-10-02): M4b with a token-overlap statement rule beside M4 and M4b. No model call."""
from __future__ import annotations

import statistics
import sys

from scores_analysis import ARMS, HARMLESS, TRACED, arm, citing, lead, m4, m4b, normalize_answer, per_case, states
from scores_common import share


def counted(text: str) -> list[str]:
    return [t for t in normalize_answer(text).split() if t not in HARMLESS]


def states_tok(text: str, case: dict, fact: dict, share_needed: float = 0.5) -> bool:
    written = set(counted(text))
    for s, e in fact["spans"]:
        tokens = counted(case["text"][s:e])
        if len(tokens) <= 1:
            if states(text, case, fact):
                return True
            continue
        if sum(t in written for t in tokens) / len(tokens) >= share_needed:
            return True
    return False


def claim_text(claims: list[dict], cid: str) -> str:
    return next(c["text"] for c in claims if c["claim_id"] == cid)


def m4b_tok(case: dict, trace: dict) -> float:
    claims = trace["claims"]
    return share(any(states_tok(claim_text(claims, cid), case, fact) for cid in citing(case, claims, fact))
                 for fact in lead(case))


def mean(values: dict[str, float]) -> float:
    return sum(values.values()) / len(values)


def main() -> None:
    arms = {label: ARMS[label] for label in TRACED}
    arms["current 51-150"] = ("main_20261001_021428", "cybercase_nogrammar")
    print("| Arm | Cases | M4 | M4b | M4b-tok50 | M4 − M4b | M4 − M4b-tok50 | ratio |")
    print("|---|---|---|---|---|---|---|---|")
    for label, (run, name) in arms.items():
        vs = arm(run, name)
        a = mean(per_case(vs, lambda v: m4(v["case"], v["trace"])))
        b = mean(per_case(vs, lambda v: m4b(v["case"], v["trace"])))
        t = mean(per_case(vs, lambda v: m4b_tok(v["case"], v["trace"])))
        print(f"| {label} | {len(vs)} | {a:.3f} | {b:.3f} | {t:.3f} | {a - b:.3f} | {a - t:.3f} | {(a - t) / (a - b):.2f} |")
    vs = arm(*ARMS["final"])
    moved = strict_not = 0
    stated_len, not_len = [], []
    for v in vs.values():
        if not v["done"]:
            continue
        case, claims = v["case"], v["trace"]["claims"]
        for fact in lead(case):
            cids = citing(case, claims, fact)
            if not cids:
                continue
            length = max(len(counted(case["text"][s:e])) for s, e in fact["spans"])
            if any(states(claim_text(claims, c), case, fact) for c in cids):
                stated_len.append(length)
                continue
            strict_not += 1
            not_len.append(length)
            moved += any(states_tok(claim_text(claims, c), case, fact) for c in cids)
    print()
    print(f"final arm: cited facts not stated by a citing claim (M4b rule) {strict_not}; stated under tok50 {moved}")
    print(f"span tokens, cited and stated: median {statistics.median(stated_len)} (n {len(stated_len)}); "
          f"cited, not stated: median {statistics.median(not_len)} (n {len(not_len)})")
    print(f"share of spans with 4+ tokens: stated {sum(x >= 4 for x in stated_len) / len(stated_len):.2f}, "
          f"not stated {sum(x >= 4 for x in not_len) / len(not_len):.2f}")


if __name__ == "__main__":
    sys.exit(main())
