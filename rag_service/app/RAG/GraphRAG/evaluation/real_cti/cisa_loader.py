"""
CISA advisories -> attack chains
=================================
Turns the CISA TTP Articles Data Set (see fetch_cisa.py) into chains with the
same shape ctid_loader.py produces.

Why the narrative and not the table: CISA's TECHNICAL DETAILS section tags
behaviours inline, in the order they happened —

    "the actors use open source brute force tools to gain access [T1110]"

so each tagged sentence yields a step whose *order* comes from the incident
itself and whose *cue* is CISA's own prose describing what was observed. The
ATT&CK table at the foot of an advisory is unordered and lists techniques the
narrative never mentions, so it is not used as gold here.

Filtering applied, and why each matters for a case-file eval:
  - reconnaissance / resource-development steps are dropped: they happen
    outside the victim's visibility and cannot appear as evidence (same rule
    as make_incident_dataset.KILL_CHAIN_ORDER)
  - sentences carrying more than MAX_TAGS_PER_CUE tags are dropped as
    listings rather than narration
  - sub-technique IDs are rolled up to their parent, because the graph holds
    no sub-techniques (see ctid_loader)

Usage:
    cd rag_service/app
    python -m RAG.GraphRAG.evaluation.real_cti.cisa_loader
    python -m RAG.GraphRAG.evaluation.real_cti.cisa_loader --no-neo4j --stats
"""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
from pathlib import Path

# Fix relative imports when run directly
if __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    __package__ = "GraphRAG.evaluation.real_cti"

# UTF-8 fix for Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from .ctid_loader import MAX_TECHNIQUES, MIN_TECHNIQUES, resolve_stix_ids
from .fetch_cisa import DEST as CISA_JSONL, ZENODO_DOI

DATA_DIR = Path(__file__).resolve().parent / "data"
LOOKUP_PATH = Path(__file__).resolve().parents[1] / "data" / "attack_lookup.json"
OUT_PATH = DATA_DIR / "cisa_chains.json"

# Tactics whose activity a victim organisation cannot observe, so a case file
# could never carry evidence of them.
UNOBSERVABLE_TACTICS = {"reconnaissance", "resource-development"}

MIN_CUE_WORDS = 8       # shorter than this is a table cell, not narration
MAX_TAGS_PER_CUE = 3    # more than this is an enumeration, not a step
# One advisory can tag 80+ behaviours. Taking every window from it would fill
# the set with near-neighbours from a single document instead of covering
# many incidents, so cap the yield per source.
MAX_CHAINS_PER_ADVISORY = 5
# A chain that meets MIN_TECHNIQUES out of a single sentence is not a
# chronology — a case file needs several observations in sequence.
MIN_STEPS = 3

TAG_RE = re.compile(r"\[(T\d{4}(?:\.\d{3})?)\]")
CITATION_RE = re.compile(r"\[\d+\]")
SECTION_START_RE = re.compile(r"TECHNICAL DETAILS", re.I)
SECTION_END_RE = re.compile(
    r"(MITRE ATT&CK TACTICS AND TECHNIQUES|MITIGATIONS|"
    r"INDICATORS OF COMPROMISE|DETECTION METHODS)",
    re.I,
)
# CISA runs headings and sentences together across newlines; split on both.
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+|\n+")


# ══════════════════════════════════════════════════════════════════════════════
# 1. LOOKUPS
# ══════════════════════════════════════════════════════════════════════════════


def load_lookups() -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """Return (attack_id -> tactics, attack_id -> known names/aliases)."""
    data = json.loads(LOOKUP_PATH.read_text(encoding="utf-8"))
    names: dict[str, list[str]] = {}
    for name, aid in data["alias_map"].items():
        names.setdefault(aid, []).append(name)
    return data["technique_to_tactics"], names


def is_observable(attack_id: str, raw_id: str, tactics: dict[str, list[str]]) -> bool:
    """False when every tactic the technique belongs to is unobservable."""
    t = tactics.get(raw_id) or tactics.get(attack_id)
    if not t:
        return True  # unknown tactic: keep, the reviewer decides
    return bool(set(t) - UNOBSERVABLE_TACTICS)


# ══════════════════════════════════════════════════════════════════════════════
# 2. PARSE ONE ADVISORY
# ══════════════════════════════════════════════════════════════════════════════


def extract_technical_details(raw_text: str) -> str:
    m = SECTION_START_RE.search(raw_text)
    if not m:
        return ""
    rest = raw_text[m.end():]
    end = SECTION_END_RE.search(rest)
    return rest[:end.start()] if end else rest


def clean_cue(sentence: str) -> str:
    """Strip ATT&CK tags and CISA's numeric citations from a cue.

    Removing the tags is what makes the cue usable as a query: the sentence
    keeps the observed behaviour and loses the answer.
    """
    text = TAG_RE.sub("", sentence)
    text = CITATION_RE.sub("", text)
    return re.sub(r"\s+", " ", text).strip(" .,;:").strip()


def parse_advisory(
    record: dict,
    tactics: dict[str, list[str]],
) -> tuple[str, list[dict]]:
    """Return (advisory_id, ordered steps) for one advisory record."""
    advisory_id = record["URL"].rstrip("/").rsplit("/", 1)[-1].lower()
    section = extract_technical_details(record.get("RawText", ""))
    if not section:
        return advisory_id, []

    steps: list[dict] = []
    for sentence in SENTENCE_RE.split(section):
        raw_ids = list(dict.fromkeys(TAG_RE.findall(sentence)))
        if not raw_ids or len(raw_ids) > MAX_TAGS_PER_CUE:
            continue
        cue = clean_cue(sentence)
        if len(cue.split()) < MIN_CUE_WORDS:
            continue
        # One sentence is one step even when it carries several tags: CISA
        # often names two techniques in a single observation ("abuse of valid
        # accounts and exploitation of public-facing applications"). Splitting
        # that into two steps would invent an order the source never states
        # and give both steps the same cue.
        kept = [r for r in raw_ids if is_observable(r.split(".")[0], r, tactics)]
        if not kept:
            continue
        parents = list(dict.fromkeys(r.split(".")[0] for r in kept))
        first = kept[0]
        steps.append({
            "attack_ids": parents,
            "attack_ids_raw": kept,
            "tactic": (tactics.get(first) or tactics.get(parents[0]) or [""])[0],
            "cue_en": cue,
            "cti_source": [record["URL"]],
        })
    return advisory_id, steps


# ══════════════════════════════════════════════════════════════════════════════
# 3. CHUNK
# ══════════════════════════════════════════════════════════════════════════════


def merge_repeat_steps(steps: list[dict]) -> list[dict]:
    """Drop a step whose technique set repeats the step just before it.

    CISA restates the same finding across a paragraph break often enough that
    without this the same gold set gets scored twice in a row.
    """
    merged: list[dict] = []
    for step in steps:
        if merged and merged[-1]["attack_ids"] == step["attack_ids"]:
            prev = merged[-1]
            if step["cue_en"] not in prev["cue_en"]:
                prev["cue_en"] = f'{prev["cue_en"]} {step["cue_en"]}'
            prev["attack_ids_raw"] = list(dict.fromkeys(
                prev["attack_ids_raw"] + step["attack_ids_raw"]
            ))
            continue
        merged.append(dict(step))
    for i, step in enumerate(merged, start=1):
        step["order"] = i
    return merged


def chunk_narrative(steps: list[dict]) -> list[list[dict]]:
    """Cut an advisory's ordered steps into MIN..MAX-technique chains.

    Unlike the CTID plans there is no procedure_group to cut on, so a window
    closes once it holds MIN distinct techniques, and never grows past MAX.
    A trailing window too small to stand alone is folded into the previous
    chain unless that would push it over MAX.
    """
    def uniq(ss: list[dict]) -> set[str]:
        return {a for s in ss for a in s["attack_ids"]}

    chains: list[list[dict]] = []
    cur: list[dict] = []
    for step in steps:
        if cur and len(uniq(cur + [step])) > MAX_TECHNIQUES:
            chains.append(cur)
            cur = []
        cur.append(step)
        if len(uniq(cur)) >= MIN_TECHNIQUES and len(cur) >= MIN_STEPS:
            chains.append(cur)
            cur = []
    if cur and chains and len(uniq(chains[-1] + cur)) <= MAX_TECHNIQUES:
        chains[-1] += cur
    elif cur and len(uniq(cur)) >= MIN_TECHNIQUES and len(cur) >= MIN_STEPS:
        chains.append(cur)
    return chains


def _tokens(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z]+", text.lower()) if len(w) >= 4}


def classify_cue_type(step: dict, names: dict[str, list[str]]) -> str:
    """named when the cue spells the technique out, described otherwise.

    Same distinction the existing incident dataset draws, but read off CISA's
    wording instead of requested from an LLM. Matching is on token overlap,
    not substring: advisories inflect the official name ("Exploit
    Public-Facing Application" is written "exploitation of public-facing
    applications"), and a substring test scores those as described, which
    would overstate how much behaviour-only text the set contains.
    """
    cue_tokens = _tokens(step["cue_en"])
    for aid in {*step["attack_ids"], *step["attack_ids_raw"]}:
        for name in names.get(aid, []):
            for part in re.split(r":\s*", name):
                want = _tokens(part)
                if not want:
                    continue
                # count a token as present if the cue has it or an inflection
                hit = sum(
                    1 for w in want
                    if any(c.startswith(w[:max(4, len(w) - 2)]) for c in cue_tokens)
                )
                if hit == len(want):
                    return "named"
    return "described"


# ══════════════════════════════════════════════════════════════════════════════
# 4. BUILD
# ══════════════════════════════════════════════════════════════════════════════


REVISION_SUFFIX_RE = re.compile(r"-\d+$")


def dedupe_revisions(records: list[dict]) -> tuple[list[dict], list[str]]:
    """Keep one record per advisory, dropping CISA's revision duplicates.

    CISA republishes a revised advisory at a new URL ending `-0`, `-1`, ...
    (aa22-249a and aa22-249a-0 differ by 17 characters). Both crawls sit in
    the dataset, and both would yield near-identical chains — samples that
    look independent but are not. The longest text wins as the fullest
    revision.
    """
    by_base: dict[str, dict] = {}
    dropped: list[str] = []
    for record in records:
        slug = record["URL"].rstrip("/").rsplit("/", 1)[-1].lower()
        base = REVISION_SUFFIX_RE.sub("", slug)
        keep = by_base.get(base)
        if keep is None:
            by_base[base] = record
            continue
        loser, winner = sorted(
            (keep, record), key=lambda r: len(r.get("RawText", ""))
        )
        by_base[base] = winner
        dropped.append(loser["URL"].rstrip("/").rsplit("/", 1)[-1].lower())
    return list(by_base.values()), sorted(dropped)


def build_chains(use_neo4j: bool = True) -> tuple[list[dict], dict]:
    if not CISA_JSONL.exists():
        raise SystemExit(
            f"{CISA_JSONL} missing — run:\n"
            f"  python -m RAG.GraphRAG.evaluation.real_cti.fetch_cisa"
        )
    records = [
        json.loads(line)
        for line in CISA_JSONL.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    records, revisions = dedupe_revisions(records)
    tactics, names = load_lookups()

    chains: list[dict] = []
    skipped: list[str] = []
    for record in records:
        advisory_id, steps = parse_advisory(record, tactics)
        if not steps:
            skipped.append(advisory_id)
            continue
        steps = merge_repeat_steps(steps)
        made = 0
        for chunk in chunk_narrative(steps):
            if made >= MAX_CHAINS_PER_ADVISORY:
                break
            for i, step in enumerate(chunk, start=1):
                step["cue_type"] = classify_cue_type(step, names)
                step["order"] = i
            made += 1
            chains.append({
                "chain_id": f"cisa_{advisory_id}_{made:03d}",
                "source": "CISA cybersecurity advisory",
                "source_prov": f"CISA {advisory_id.upper()} (Zenodo {ZENODO_DOI})",
                "advisory_id": advisory_id.upper(),
                "cti_sources": [record["URL"]],
                "steps": chunk,
            })
        if not made:
            skipped.append(advisory_id)

    all_raw = {r for c in chains for s in c["steps"] for r in s["attack_ids_raw"]}
    report = {
        "source_doi": ZENODO_DOI,
        "advisories_total": len(records),
        "advisories_dropped_as_revisions": revisions,
        "advisories_used": len({c["advisory_id"] for c in chains}),
        "advisories_skipped_no_inline_tags": sorted(set(skipped)),
        "rolled_up_subtechniques": sorted(r for r in all_raw if "." in r),
        "unresolved_attack_ids": [],
    }

    if use_neo4j:
        all_ids = {a for c in chains for s in c["steps"] for a in s["attack_ids"]}
        stix = resolve_stix_ids(all_ids)
        report["unresolved_attack_ids"] = sorted(all_ids - set(stix))
        for chain in chains:
            for step in chain["steps"]:
                step["stix_ids"] = [
                    stix[a] for a in step["attack_ids"] if a in stix
                ]
    return chains, report


def print_stats(chains: list[dict], report: dict) -> None:
    per_adv: dict[str, int] = {}
    for c in chains:
        per_adv[c["advisory_id"]] = per_adv.get(c["advisory_id"], 0) + 1
    steps = [s for c in chains for s in c["steps"]]
    named = sum(1 for s in steps if s["cue_type"] == "named")

    print(f"advisories in dataset : {report['advisories_total']}")
    print(f"advisories usable     : {report['advisories_used']} "
          f"(rest have no inline [T####] tags in TECHNICAL DETAILS)")
    print(f"chains                : {len(chains)}")
    print(f"steps                 : {len(steps)}  "
          f"(named {named} / described {len(steps) - named})")
    print(f"sub-techniques rolled up: {len(report['rolled_up_subtechniques'])}")
    top = sorted(per_adv.items(), key=lambda kv: -kv[1])[:8]
    print("top advisories        : " + ", ".join(f"{k}={v}" for k, v in top))
    if report["unresolved_attack_ids"]:
        print(f"\n[WARN] {len(report['unresolved_attack_ids'])} parent IDs not in "
              f"Neo4j: {', '.join(report['unresolved_attack_ids'])}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build CISA advisory chains")
    parser.add_argument("--no-neo4j", action="store_true",
                        help="Skip stix_id resolution (offline structure check)")
    parser.add_argument("--stats", action="store_true", help="Print stats only")
    parser.add_argument("--out", type=str, default=str(OUT_PATH))
    args = parser.parse_args()

    chains, report = build_chains(use_neo4j=not args.no_neo4j)
    print_stats(chains, report)

    if args.stats:
        return
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump({**report, "chains": chains}, f, indent=2, ensure_ascii=False)
    print(f"\n[OUT] {out}")


if __name__ == "__main__":
    main()
