"""Scores, analysis part: the metrics M1-M5, M4b, V0, V3 and M7, then every analysis arm scored case by case.
"""
from __future__ import annotations

import json
import re
import string
from collections import Counter

import numpy as np

from scores_binder import stitched
from scores_common import CASES, HERE, jsonl, lead, positions, quotes_of, share, v0_words

# ================================================================================================= RULES

TOKEN_CAP = 40_800
HARMLESS = {"the", "a", "an", "of", "and", "s"}


def m1(trace: dict) -> tuple[int, int]:
    """M1 for one case: claims still reported after binding, over those plus the claims the binder demoted."""
    statuses = Counter(claim["epistemic_status"] for claim in trace["claims"])
    return statuses["reported"], statuses["reported"] + statuses["not_confirmed"]


def m2(record: dict) -> tuple[int, int]:
    """M2 for one case: quotes the binder verified, over the quotes the model wrote."""
    return record["grounding"]["citations_verified"], record["grounding"]["citations_claimed"]


def m3(trace: dict) -> bool:
    """M3 for one case: no claim was demoted to not_confirmed."""
    return all(claim["epistemic_status"] != "not_confirmed" for claim in trace["claims"])


def pointed_at(fact: dict, spans: list[tuple[int, int]]) -> bool:
    """A fact is pointed at when a quote position overlaps one of its annotated character spans."""
    return any(a < end and b > start for start, end in fact["spans"] for a, b in spans)


def citing(case: dict, claims: list[dict], fact: dict, keep=lambda quote: True) -> list[str]:
    """The claims whose verified quotes point at the fact."""
    return [c["claim_id"] for c in claims
            if pointed_at(fact, [p for q in quotes_of(c) if keep(q) for p in positions(case["text"], q)])]


def m4(case: dict, trace: dict, keep=lambda quote: True) -> float:
    """M4 for one case: main-event facts that a verified quote points at, over the main-event facts."""
    return share(bool(citing(case, trace["claims"], fact, keep)) for fact in lead(case))


def normalize_answer(s):
    """Lower text and remove punctuation, articles and extra whitespace."""
    def remove_articles(text):
        return re.sub(r'\b(a|an|the)\b', ' ', text)

    def white_space_fix(text):
        return ' '.join(text.split())

    def remove_punc(text):
        exclude = set(string.punctuation)
        return ''.join(ch for ch in text if ch not in exclude)

    def lower(text):
        return text.lower()

    return white_space_fix(remove_articles(remove_punc(lower(s))))


def states(text: str, case: dict, fact: dict) -> bool:
    """SQuAD subspan rule: the normalised article text at one of the fact's spans is in the normalised text."""
    written = normalize_answer(text)
    return any(form and form in written for form in (normalize_answer(case["text"][s:e]) for s, e in fact["spans"]))


def m5_std(text: str, gold: dict) -> float:
    """M5-std for one case: main-event facts of `gold` that the text states; the chance floor passes the next case."""
    return share(states(text, gold, fact) for fact in lead(gold))


def stating(case: dict, claims: list[dict], fact: dict) -> list[str]:
    """The claims that point at the fact with a verified quote and state it in their own text."""
    return [cid for cid in citing(case, claims, fact)
            if states(next(c["text"] for c in claims if c["claim_id"] == cid), case, fact)]


def m4b(case: dict, trace: dict) -> float:
    """M4b for one case: main-event facts that one claim both points at and states, over the main-event facts."""
    return share(bool(stating(case, trace["claims"], fact)) for fact in lead(case))


def mentions(text: str, fact: dict) -> bool:
    """V0: the fact's normalised words appear as a contiguous run of whole words in the text."""
    return f" {fact['text']} " in f" {v0_words(text)} "


def m5_v0(text: str, case: dict) -> float:
    """M5 for one case: main-event facts the text mentions by V0, over the main-event facts."""
    return share(mentions(text, fact) for fact in lead(case))


def v3_words(text: str) -> list[str]:
    """V0 words without a few function words, with digit groups such as "43 000" joined into "43000"."""
    words, out, i = [w for w in v0_words(text).split() if w not in HARMLESS], [], 0
    while i < len(words):
        word, j = words[i], i + 1
        if word.isdigit() and len(word) <= 3:
            while j < len(words) and words[j].isdigit() and len(words[j]) == 3:
                word, j = word + words[j], j + 1
        out.append(word)
        i = j
    return out


def v3(text: str, case: dict) -> float:
    """V3 for one case: every word of a main-event fact appears within one sentence of the text, in any order."""
    sentences = [set(v3_words(s)) for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]
    return share(bool(words := set(v3_words(fact["text"]))) and any(words <= s for s in sentences)
                 for fact in lead(case))


def own_text(trace: dict) -> str:
    """The text an arm wrote itself: summary, parties, timeline, claims with reasoning, impacts, gaps; no quotes."""
    parts = [trace["summary"]]
    parts += [f"{p['name']} {p['role']}" for p in trace["involved_parties"]]
    parts += [f"{t['time']} {t['event']}" for t in trace["timeline"]]
    parts += [f"{c['text']} {c['reasoning_summary'] or ''}" for c in trace["claims"]]
    parts += [i["description"] for i in trace["impacts"]]
    parts += [f"{g['topic']} {g['description']}" for g in trace["gaps"]]
    return "\n".join(parts)


def capped(call: dict) -> bool:
    """A model call stopped at its output limit: the provider said so, or it used the whole token budget."""
    return call.get("stop_reason") in ("max_tokens", "length") or (call.get("output_tokens") or 0) >= TOKEN_CAP


def model_seconds(record: dict) -> float:
    """A case's model seconds: the sum of its call durations."""
    return sum(call.get("ms") or 0 for call in record.get("calls", [])) / 1000


# ================================================================================================= DATA

DESIGN, SHIPPED, FINAL = "main_20260930_020141", "main_20260930_062138", "main_20260930_193646"
ARMS = {"prose": (DESIGN, "prose"), "one call": (DESIGN, "single"), "two calls": (DESIGN, "cybercase"),
        "shipped": (SHIPPED, "cybercase"), "final": (FINAL, "cybercase_nogrammar")}
TRACED = ("one call", "two calls", "shipped", "final")


def arm(run: str, name: str) -> dict[str, dict]:
    """The scored records of one arm, by case id; a completed case carries its bound trace and own text."""
    views = {}
    for record in jsonl(HERE / "results" / f"{run}.jsonl"):
        if record["arm"] != name or record.get("run", 1) != 1 or record.get("error_kind") in ("budget", "harness"):
            continue
        view = {"record": record, "case": CASES[record["case"]], "done": "error" not in record}
        if view["done"]:
            stem = HERE / "results" / f"raw_{run}" / f"{record['case']}_{name}_1"
            if name == "prose":
                view["text"] = stem.with_suffix(".txt").read_text(encoding="utf-8")
            else:
                saved = json.loads(stem.with_suffix(".json").read_text(encoding="utf-8"))
                view.update(trace=saved["bound"], written=saved.get("written"), text=own_text(saved["bound"]))
        views[record["case"]] = view
    return dict(sorted(views.items()))


def per_case(views: dict[str, dict], metric) -> dict[str, float]:
    """A metric for every case of an arm; a failed case scores 0."""
    return {c: metric(v) if v["done"] else 0.0 for c, v in views.items()}


def unstitched(view: dict) -> float:
    """M4 for one case without the spans the binder kept only by stitching (the binder sensitivity)."""
    leaky = stitched(view["case"]["text"], view["written"])
    return m4(view["case"], view["trace"], keep=lambda quote: quote not in leaky)


def analysis(arms: dict[str, tuple[str, str]] = ARMS, traced: tuple[str, ...] = TRACED) -> tuple[dict, dict]:
    """Every analysis arm's records, and its scores: per-case values with failures scored 0, and per-case counts."""
    views = {label: arm(*arms[label]) for label in arms}
    for label, vs in views.items():
        for c, v in vs.items():
            if v["done"] and sorted(f"{f['role']}|{f['text']}" for f in lead(v["case"]) if mentions(v["text"], f)) \
                    != sorted(v["record"]["stated_lead"]):
                raise SystemExit(f"V0 does not reproduce the stored mentions of {label}, case {c}")
    scores = {}
    for label, vs in views.items():
        ids, done = list(vs), [c for c, v in vs.items() if v["done"]]
        x = {"cases": len(vs), "done": done,
             "m5": per_case(vs, lambda v: m5_v0(v["text"], v["case"])),
             "m5std": per_case(vs, lambda v: m5_std(v["text"], v["case"])),
             "v3": per_case(vs, lambda v: v3(v["text"], v["case"])),
             "floor": [m5_std(vs[c]["text"], CASES[ids[(i + 1) % len(ids)]])
                       for i, c in enumerate(ids) if vs[c]["done"]]}
        if label in traced:
            calls = [call for v in vs.values() for call in v["record"].get("calls", [])]
            x.update(m1={c: m1(vs[c]["trace"]) for c in done}, m2={c: m2(vs[c]["record"]) for c in done},
                     m3=sum(m3(vs[c]["trace"]) for c in done),
                     m4=per_case(vs, lambda v: m4(v["case"], v["trace"])),
                     m4b=per_case(vs, lambda v: m4b(v["case"], v["trace"])),
                     failed=len(vs) - len(done), capped=sum(map(capped, calls)),
                     seconds=float(np.median([model_seconds(v["record"]) for v in vs.values()])),
                     usd=sum(call["usd"] for call in calls) / len(vs))
        if label in ("two calls", "shipped", "final"):
            x["m4_unstitched"] = per_case(vs, unstitched)
        scores[label] = x
    return views, scores
