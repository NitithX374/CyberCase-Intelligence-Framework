"""The free robustness checks of README.md (A3, A4, A5), read from the saved main run. No model is called.

  python robustness.py
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
RUN = "main_20260928_081639"
RAW = HERE / "results" / f"raw_{RUN}"
ARMS = ("prose", "cybercase", "single")
PAIRS = (("cybercase", "prose"), ("cybercase", "single"), ("single", "prose"))
HARMLESS = {"the", "a", "an", "of", "and", "s"}
SEED = 2026

records = [json.loads(line) for line in (HERE / "results" / f"{RUN}.jsonl").read_text(encoding="utf-8").splitlines()]
by = {(r["case"], r["arm"]): r for r in records if r.get("error_kind") not in ("budget", "harness")}
cases = {c["id"]: c for c in map(json.loads, (HERE / "data" / "cases.jsonl").read_text(encoding="utf-8").splitlines())}
order = [c["id"] for c in map(json.loads, (HERE / "data" / "cases.jsonl").read_text(encoding="utf-8").splitlines())
         if c["sample"] == "main"]
ids = [c for c in order if all((c, arm) in by for arm in ARMS)]
NEXT = {c: ids[(i + 1) % len(ids)] for i, c in enumerate(ids)}


def norm(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", unicodedata.normalize("NFKC", text).lower()))


def contains(haystack: str, needle: str) -> bool:
    return bool(needle) and f" {needle} " in f" {haystack} "


def own_text(trace: dict) -> str:
    parts = [trace["summary"]]
    parts += [f"{p['name']} {p['role']}" for p in trace["involved_parties"]]
    parts += [f"{t['time']} {t['event']}" for t in trace["timeline"]]
    parts += [f"{c['text']} {c.get('reasoning_summary') or ''}" for c in trace["claims"]]
    parts += [i["description"] for i in trace["impacts"]]
    parts += [f"{g['topic']} {g['description']}" for g in trace["gaps"]]
    return "\n".join(parts)


def written_text(case_id: str, arm: str) -> str | None:
    if "error" in by[(case_id, arm)]:
        return None
    if arm == "prose":
        return (RAW / f"{case_id}_prose_1.txt").read_text(encoding="utf-8")
    return own_text(json.loads((RAW / f"{case_id}_{arm}_1.json").read_text(encoding="utf-8"))["bound"])


TEXTS = {(c, arm): written_text(c, arm) for c in ids for arm in ARMS}


def v1_tokens(text: str) -> list[str]:
    tokens = [t for t in norm(text).split() if t not in HARMLESS]
    joined: list[str] = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.isdigit() and len(token) <= 3:
            j = i + 1
            while j < len(tokens) and tokens[j].isdigit() and len(tokens[j]) == 3:
                token += tokens[j]
                j += 1
            joined.append(token)
            i = j
        else:
            joined.append(token)
            i += 1
    return joined


def sentences(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]


def best_long_form(short: str, long: str) -> str | None:
    s_index, l_index = len(short) - 1, len(long) - 1
    while s_index >= 0:
        char = short[s_index].lower()
        if not char.isalnum():
            s_index -= 1
            continue
        while (l_index >= 0 and long[l_index].lower() != char) or (
                s_index == 0 and l_index > 0 and long[l_index - 1].isalnum()):
            l_index -= 1
        if l_index < 0:
            return None
        l_index -= 1
        s_index -= 1
    l_index = long.rfind(" ", 0, l_index + 1) + 1
    return long[l_index:]


def abbreviation_pairs(article: str) -> list[tuple[str, str]]:
    pairs = []
    for match in re.finditer(r"\(([^()]{2,10})\)", article):
        short = match.group(1).strip()
        if not (2 <= len(short) <= 10 and any(ch.isalpha() for ch in short) and short[0].isalnum()
                and len(short.split()) <= 2):
            continue
        words = article[:match.start()].rstrip().split()
        window = min(len(short) + 5, len(short) * 2)
        long = best_long_form(short, " ".join(words[-window:]))
        if long and len(long) > len(short):
            pairs.append((norm(long), norm(short)))
    return pairs


def matched(fact: str, text: str, variant: str, case_id: str) -> bool:
    written = norm(text)
    if variant in ("V0", "V5"):
        return contains(written, fact)
    fact_tokens = v1_tokens(fact)
    if variant == "V1":
        return contains(" ".join(v1_tokens(text)), " ".join(fact_tokens))
    if variant == "V2":
        if contains(written, fact):
            return True
        for long, short in abbreviation_pairs(cases[case_id]["text"]):
            if fact == long and contains(written, short):
                return True
            if fact == short and contains(written, long):
                return True
        return False
    if variant == "V3":
        if not fact_tokens:
            return False
        return any(set(fact_tokens) <= set(v1_tokens(s)) for s in sentences(text))
    if variant == "V4":
        if not fact_tokens:
            return False
        present = set(v1_tokens(text))
        hits = [t for t in fact_tokens if t in present]
        return len(hits) / len(fact_tokens) >= 0.5 and any(len(t) >= 4 for t in hits)
    if variant == "V6":
        return any(matched(fact, text, v, case_id) for v in ("V1", "V2", "V3"))
    raise ValueError(variant)


def strip_quotes(text: str) -> str:
    return re.sub(r"[\"“]([^\"”]*?)[\"”]", lambda m: " " if len(m.group(1).split()) >= 3 else m.group(0), text)


def recall(case_id: str, arm: str, variant: str, lead: bool, gold_case: str | None = None,
           text: str | None = None) -> float:
    text = TEXTS[(case_id, arm)] if text is None else text
    if text is None:
        return 0.0
    if variant in ("V5", "V6") and arm == "prose":
        text = strip_quotes(text)
    gold = [f for f in cases[gold_case or case_id]["gold"] if f["lead"] or not lead]
    return sum(matched(f["text"], text, variant, case_id) for f in gold) / len(gold)


def bootstrap(values: dict[str, float], subset: list[str]) -> tuple[float, float, float]:
    rng = np.random.default_rng(SEED)
    array = np.array([values[c] for c in subset])
    draws = [array[rng.integers(0, len(array), len(array))].mean() for _ in range(2000)]
    return float(array.mean()), float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))


def fmt(point: float, low: float, high: float) -> str:
    return f"{point:+.3f} [{low:+.3f}, {high:+.3f}]"


def fragments(summary: list[str], article: list[str]) -> list[list[str]]:
    found, i = [], 0
    while i < len(summary):
        best: list[str] = []
        j = 0
        while j < len(article):
            if summary[i] == article[j]:
                i2, j2 = i, j
                while i2 < len(summary) and j2 < len(article) and summary[i2] == article[j2]:
                    i2 += 1
                    j2 += 1
                if len(best) < i2 - i:
                    best = summary[i:i2]
                j = j2
            else:
                j += 1
        found.append(best)
        i += max(len(best), 1)
    return found


def extractiveness(text: str, article: str) -> tuple[float, float]:
    s, a = norm(text).split(), norm(article).split()
    parts = fragments(s, a)
    return sum(len(f) for f in parts) / len(s), sum(len(f) ** 2 for f in parts) / len(s)


def main() -> None:
    report: dict = {"cases": len(ids)}
    lines: list[str] = [f"# Robustness checks on {RUN} ({len(ids)} cases, no model call)", ""]

    # V0 reproduction and the A4 specification curve
    lines += ["## A4: scorer specification curve", "",
              "| Variant | Level | prose | cybercase | single | cybercase − prose | cybercase − single | single − prose |",
              "|---|---|---|---|---|---|---|---|"]
    curve = {}
    for variant in ("V0", "V1", "V2", "V3", "V4", "V5", "V6"):
        for lead in (True, False):
            level = "main event" if lead else "all events"
            per = {arm: {c: recall(c, arm, variant, lead) for c in ids} for arm in ARMS}
            means = {arm: float(np.mean(list(per[arm].values()))) for arm in ARMS}
            diffs = {f"{a}-{b}": bootstrap({c: per[a][c] - per[b][c] for c in ids}, ids) for a, b in PAIRS}
            curve[f"{variant}/{level}"] = {"means": means, "diffs": diffs}
            lines.append(f"| {variant} | {level} | {means['prose']:.3f} | {means['cybercase']:.3f} | {means['single']:.3f} | "
                         + " | ".join(fmt(*diffs[f'{a}-{b}']) for a, b in PAIRS) + " |")
    report["specification_curve"] = curve
    v0 = curve["V0/main event"]["means"]
    report["v0_reproduces"] = {arm: round(v0[arm], 2) for arm in ARMS}

    floor = {arm: float(np.mean([recall(c, arm, "V4", True, gold_case=NEXT[c]) for c in ids])) for arm in ARMS}
    corrected = {arm: curve["V4/main event"]["means"][arm] - floor[arm] for arm in ARMS}
    report["v4_floor_main_event"] = {"floor": floor, "floor_corrected": corrected}
    lines += ["", "V4 floor (each text against the next case's main-event gold): "
              + ", ".join(f"{arm} {floor[arm]:.3f}" for arm in ARMS)
              + "; floor-corrected: " + ", ".join(f"{arm} {corrected[arm]:.3f}" for arm in ARMS)]

    extract = {}
    for arm in ARMS:
        pairs = [extractiveness(TEXTS[(c, arm)], cases[c]["text"]) for c in ids if TEXTS[(c, arm)]]
        extract[arm] = {"coverage": float(np.mean([p[0] for p in pairs])), "density": float(np.mean([p[1] for p in pairs]))}
    report["extractiveness"] = extract
    quoted = sum(len(re.findall(r"[\"“]([^\"”]*?)[\"”]", TEXTS[(c, "prose")] or "")) for c in ids)
    lines += ["", "Extractive fragment coverage and density (Grusky et al. 2018), of the scored text: "
              + "; ".join(f"{arm} {extract[arm]['coverage']:.2f} / {extract[arm]['density']:.2f}" for arm in ARMS)
              + f". Quoted passages in the prose outputs: {quoted}."]

    # A3 length control
    lines += ["", "## A3: length control (the longer text truncated to the shorter one's word count)", "",
              "| Pair | Cases | Mean words kept | Difference, full length | Difference, matched length |", "|---|---|---|---|---|"]
    length = {}
    for a, b in PAIRS:
        both = [c for c in ids if TEXTS[(c, a)] and TEXTS[(c, b)]]
        full, cut, kept = {}, {}, []
        for c in both:
            ta, tb = TEXTS[(c, a)], TEXTS[(c, b)]
            n = min(len(ta.split()), len(tb.split()))
            kept.append(n)
            full[c] = recall(c, a, "V0", True) - recall(c, b, "V0", True)
            cut[c] = (recall(c, a, "V0", True, text=" ".join(ta.split()[:n]))
                      - recall(c, b, "V0", True, text=" ".join(tb.split()[:n])))
        length[f"{a}-{b}"] = {"cases": len(both), "mean_words": float(np.mean(kept)),
                              "full": bootstrap(full, both), "matched": bootstrap(cut, both)}
        lines.append(f"| {a} − {b} | {len(both)} | {np.mean(kept):.0f} | {fmt(*bootstrap(full, both))} | "
                     f"{fmt(*bootstrap(cut, both))} |")
    report["length_control"] = length

    described = {}
    for arm in ARMS:
        lead_r, rand_r, saturated = [], [], 0
        for c in ids:
            text = TEXTS[(c, arm)]
            if not text:
                continue
            n, article = len(text.split()), cases[c]["text"]
            saturated += n >= len(article.split())
            lead_r.append(recall(c, arm, "V0", True, text=" ".join(article.split()[:n])))
            sents = sentences(article)
            draws = []
            for seed in range(20):
                shuffled = [sents[i] for i in np.random.default_rng(seed).permutation(len(sents))]
                draws.append(recall(c, arm, "V0", True, text=" ".join(" ".join(shuffled).split()[:n])))
            rand_r.append(float(np.mean(draws)))
        described[arm] = {"lead_extract": float(np.mean(lead_r)), "random_extract": float(np.mean(rand_r)),
                          "texts_as_long_as_article": saturated}
    report["same_length_extracts"] = described
    lines += ["", "Same-length extracts of the article, main-event recall (descriptive; extracts copy the article): "
              + "; ".join(f"{arm}: lead {described[arm]['lead_extract']:.3f}, random {described[arm]['random_extract']:.3f}, "
                          f"{described[arm]['texts_as_long_as_article']} texts at least as long as the article"
                          for arm in ARMS)]

    # A5 estimand reporting
    lines += ["", "## A5: estimands and tests (main-event recall, frozen scorer)", ""]
    completion = {}
    for arm in ARMS:
        done = [c for c in ids if TEXTS[(c, arm)]]
        mean_done = float(np.mean([recall(c, arm, "V0", True) for c in done]))
        completion[arm] = {"completion": len(done) / len(ids), "mean_completed": mean_done,
                           "product": len(done) / len(ids) * mean_done}
    report["completion"] = completion
    lines += ["| Arm | Completion | Mean over completed | Product |", "|---|---|---|---|"]
    lines += [f"| {arm} | {completion[arm]['completion']:.2f} | {completion[arm]['mean_completed']:.3f} | "
              f"{completion[arm]['product']:.3f} |" for arm in ARMS]

    all_done = [c for c in ids if all(TEXTS[(c, arm)] for arm in ARMS)]
    tests, pvalues = {}, []
    rng = np.random.default_rng(SEED)
    for a, b in PAIRS:
        d = np.array([recall(c, a, "V0", True) - recall(c, b, "V0", True) for c in ids])
        flips = rng.choice([-1.0, 1.0], size=(10000, len(d)))
        null = np.abs((flips * d).mean(axis=1))
        p = (1 + int((null >= abs(d.mean())).sum())) / 10001
        bca = stats.bootstrap((d,), np.mean, method="BCa", n_resamples=9999, random_state=np.random.default_rng(SEED))
        percentile = bootstrap(dict(zip(ids, d)), ids)
        se = float(np.std([d[np.random.default_rng(SEED + k).integers(0, len(d), len(d))].mean() for k in range(2000)]))
        paired_done = bootstrap({c: recall(c, a, "V0", True) - recall(c, b, "V0", True) for c in all_done}, all_done)
        tests[f"{a}-{b}"] = {"mean": float(d.mean()), "percentile": percentile[1:], "bca": [
            float(bca.confidence_interval.low), float(bca.confidence_interval.high)], "sign_flip_p": p,
            "mde_80": 2.8 * se, "completed_in_every_arm": {"cases": len(all_done), "diff": paired_done}}
        pvalues.append((f"{a}-{b}", p))
    ordered = sorted(pvalues, key=lambda item: item[1])
    running = 0.0
    for rank, (name, p) in enumerate(ordered):
        running = max(running, min(1.0, p * (len(ordered) - rank)))
        tests[name]["holm_p"] = running
    report["tests"] = tests
    lines += ["", "| Comparison | Difference | Percentile 95% | BCa 95% | Sign-flip p | Holm p | MDE (80%) | "
              "Completed in every arm |", "|---|---|---|---|---|---|---|---|"]
    for a, b in PAIRS:
        t = tests[f"{a}-{b}"]
        lines.append(f"| {a} − {b} | {t['mean']:+.3f} | [{t['percentile'][0]:+.3f}, {t['percentile'][1]:+.3f}] | "
                     f"[{t['bca'][0]:+.3f}, {t['bca'][1]:+.3f}] | {t['sign_flip_p']:.4f} | {t['holm_p']:.4f} | "
                     f"{t['mde_80']:.3f} | {fmt(*t['completed_in_every_arm']['diff'])} (n={len(all_done)}) |")

    (HERE / "results" / f"{RUN}_robustness.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (HERE / "results" / f"{RUN}_robustness.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
