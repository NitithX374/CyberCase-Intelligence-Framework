"""
CTID Adversary Emulation Library -> attack chains
==================================================
Reads the vendored emulation-plan YAMLs (see NOTICE.md) and cuts each plan
into chains of consecutive steps suitable for one case-file sample.

Why this source: every step already carries an ATT&CK technique ID assigned
by MITRE Engenuity analysts *and* an explicit position in the intrusion, so
the gold labels are external to this project's graph and already ordered —
which is exactly the shape `attack_steps` needs (order + gold_attack_ids).
Contrast with the existing incident samples, where the chain is sampled from
the same Neo4j the retriever searches.

Chunking: plan files list steps in execution order and tag them with a
`procedure_group`. Consecutive groups are merged until the window holds
MIN_TECHNIQUES distinct techniques; oversized groups are split at step
boundaries. Chains never straddle two plans, and cuts never fall inside a
procedure_group unless that group alone exceeds MAX_TECHNIQUES.

Usage:
    cd rag_service/app
    python -m RAG.GraphRAG.evaluation.real_cti.ctid_loader
    python -m RAG.GraphRAG.evaluation.real_cti.ctid_loader --no-neo4j --stats
"""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
from pathlib import Path

import yaml

# Fix relative imports when run directly
if __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    __package__ = "GraphRAG.evaluation.real_cti"

# UTF-8 fix for Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PLAN_DIR = Path(__file__).resolve().parent / "data" / "ctid_plans"
OUT_DIR = Path(__file__).resolve().parent / "data"
OUT_PATH = OUT_DIR / "ctid_chains.json"

MIN_TECHNIQUES = 3   # below this a narrative is too thin to read as a case
MAX_TECHNIQUES = 6   # above this the Thai narrative gets unnaturally long

# A handful of plan steps carry a procedure step number ("7.A.5") or a
# placeholder ("x") where the ATT&CK ID belongs. Those steps are dropped.
ATTACK_ID_RE = re.compile(r"^T\d{4}(\.\d{3})?$")

STIX_CYPHER = """
MATCH (t:Technique)
WHERE t.attack_id IN $ids
RETURN t.attack_id AS attack_id, t.stix_id AS stix_id, t.name AS name
"""


# ══════════════════════════════════════════════════════════════════════════════
# 1. PARSE
# ══════════════════════════════════════════════════════════════════════════════


def _as_list(value) -> list[str]:
    if not value:
        return []
    if isinstance(value, str):
        return [value]
    return [str(v) for v in value if v]


def parse_plan(path: Path) -> tuple[dict, list[dict], list[str]]:
    """Return (plan_details, ordered steps, dropped raw ids) for one plan."""
    docs = yaml.safe_load(path.read_text(encoding="utf-8"))
    details: dict = {}
    steps: list[dict] = []
    dropped: list[str] = []
    for entry in docs:
        if not isinstance(entry, dict):
            continue
        if "emulation_plan_details" in entry:
            details = entry["emulation_plan_details"]
            continue
        tech = entry.get("technique")
        if not isinstance(tech, dict) or not tech.get("attack_id"):
            continue
        raw_id = str(tech["attack_id"]).strip()
        if not ATTACK_ID_RE.match(raw_id):
            dropped.append(raw_id)
            continue
        steps.append({
            # attack_id is the graph-scoreable ID (parent), attack_id_raw
            # keeps CTID's original label so nothing published is lost and
            # sub-technique scoring becomes possible if the graph gains them
            "attack_id": raw_id.split(".")[0],
            "attack_ids_raw": [raw_id],
            "technique_name": tech.get("name", ""),
            "tactic": entry.get("tactic", ""),
            "red_team_name": entry.get("name", ""),
            # description doubles as the behavioural source text the Thai
            # narrative is rewritten from, so keep it whole
            "red_team_description": (entry.get("description") or "").strip(),
            "procedure_group": str(entry.get("procedure_group", "")),
            "procedure_step": str(entry.get("procedure_step", "")),
            # some plans give one URL, others a list — normalise to a list
            "cti_source": _as_list(entry.get("cti_source")),
        })
    return details, steps, dropped


# ══════════════════════════════════════════════════════════════════════════════
# 2. CHUNK INTO CHAINS
# ══════════════════════════════════════════════════════════════════════════════


def _uniq_ids(steps: list[dict]) -> list[str]:
    return list(dict.fromkeys(s["attack_id"] for s in steps))


def _split_oversized(group: list[dict]) -> list[list[dict]]:
    """Cut a single procedure_group that alone exceeds MAX_TECHNIQUES."""
    out: list[list[dict]] = []
    cur: list[dict] = []
    for step in group:
        cur.append(step)
        if len(_uniq_ids(cur)) >= MAX_TECHNIQUES:
            out.append(cur)
            cur = []
    if cur:
        if out and len(_uniq_ids(cur)) < MIN_TECHNIQUES:
            out[-1] += cur
        else:
            out.append(cur)
    return out


def chunk_steps(steps: list[dict]) -> list[list[dict]]:
    """Group consecutive steps into chains of MIN..MAX distinct techniques."""
    groups: list[list[dict]] = []
    for step in steps:
        if groups and groups[-1][0]["procedure_group"] == step["procedure_group"]:
            groups[-1].append(step)
        else:
            groups.append([step])

    chains: list[list[dict]] = []
    cur: list[dict] = []
    for group in groups:
        if len(_uniq_ids(group)) > MAX_TECHNIQUES:
            # Split the fat group on its own. A pending window that is still
            # under MIN rides along into the split rather than being flushed
            # as an undersized chain of its own.
            if cur and len(_uniq_ids(cur)) >= MIN_TECHNIQUES:
                chains.append(cur)
                cur = []
            chains.extend(_split_oversized(cur + group))
            cur = []
            continue
        cur += group
        if len(_uniq_ids(cur)) >= MIN_TECHNIQUES:
            chains.append(cur)
            cur = []
    if cur:
        if chains and len(_uniq_ids(cur)) < MIN_TECHNIQUES:
            chains[-1] += cur
        else:
            chains.append(cur)
    return chains


def collapse_repeats(steps: list[dict]) -> list[dict]:
    """Merge consecutive steps sharing one technique into a single step.

    Emulation plans often split one technique across several red-team
    commands (transfer webshell / deploy webshell). A case file would narrate
    that as one action, and scoring the same gold ID twice in a row would
    double-count it.

    After the sub-technique roll-up this also merges neighbours that differ
    only below the parent (T1003.001 then T1003.002): the graph holds no
    sub-techniques, so the retriever cannot tell those apart and two
    separately-scored steps would just be the same question asked twice.
    """
    # Shared with cisa_loader, whose steps carry a different field set, so
    # merge by field kind rather than by a fixed list of names.
    joined_text = ("red_team_description", "cue_en")
    joined_ids = ("procedure_step",)
    unioned = ("cti_source", "attack_ids_raw")

    merged: list[dict] = []
    for step in steps:
        if merged and merged[-1]["attack_id"] == step["attack_id"]:
            prev = merged[-1]
            for key in joined_text:
                if key in prev and prev[key] != step.get(key):
                    prev[key] = f"{prev[key]}\n{step.get(key, '')}".strip()
            for key in joined_ids:
                if key in prev:
                    prev[key] = f"{prev[key]}, {step.get(key, '')}"
            for key in unioned:
                if key in prev:
                    prev[key] = list(dict.fromkeys(prev[key] + step.get(key, [])))
            continue
        merged.append(dict(step))
    for i, step in enumerate(merged, start=1):
        step["order"] = i
    return merged


# ══════════════════════════════════════════════════════════════════════════════
# 3. STIX RESOLUTION
# ══════════════════════════════════════════════════════════════════════════════


def resolve_stix_ids(attack_ids: set[str]) -> dict[str, str]:
    """attack_id -> stix_id from Neo4j.

    The gold labels stay the CTID ones; this only attaches the graph's own
    identifier so retrieval metrics (which match on stix_id) can score them.
    An unresolved ID means the technique is missing from the graph — that is
    a real coverage gap and is reported rather than silently dropped.
    """
    # Imported lazily: it pulls in config.py and the model stack, which
    # --no-neo4j runs (structure checks) have no reason to wait for.
    from ..generate_eval_dataset import Neo4jGroundTruthBuilder

    neo4j = Neo4jGroundTruthBuilder()
    try:
        rows = neo4j.run_query(STIX_CYPHER, {"ids": sorted(attack_ids)})
    finally:
        neo4j.close()
    return {r["attack_id"]: r["stix_id"] for r in rows if r.get("stix_id")}


# ══════════════════════════════════════════════════════════════════════════════
# 4. BUILD
# ══════════════════════════════════════════════════════════════════════════════


def build_chains(use_neo4j: bool = True) -> tuple[list[dict], dict]:
    plan_paths = sorted(PLAN_DIR.glob("*.yaml"))
    if not plan_paths:
        raise SystemExit(f"No plan YAMLs under {PLAN_DIR} — see NOTICE.md")

    raw: list[dict] = []
    dropped_ids: list[str] = []
    for path in plan_paths:
        details, steps, dropped = parse_plan(path)
        dropped_ids += dropped
        adversary = details.get("adversary_name", path.stem)
        for i, chain_steps in enumerate(chunk_steps(steps), start=1):
            chain_steps = collapse_repeats(chain_steps)
            sources = list(dict.fromkeys(
                url for s in chain_steps for url in s["cti_source"]
            ))
            raw.append({
                "chain_id": f"ctid_{path.stem.lower()}_{i:03d}",
                "source": "CTID Adversary Emulation Library",
                "source_prov": f"{adversary} (CTID emulation plan {path.name})",
                "adversary": adversary,
                "plan_file": path.name,
                "attack_version": str(details.get("attack_version", "")),
                "cti_sources": sources,
                "steps": chain_steps,
            })

    all_raw = {r for c in raw for s in c["steps"] for r in s["attack_ids_raw"]}
    report = {
        "dropped_malformed_ids": sorted(set(dropped_ids)),
        "rolled_up_subtechniques": sorted(r for r in all_raw if "." in r),
        "unresolved_attack_ids": [],
    }

    if use_neo4j:
        all_ids = {s["attack_id"] for c in raw for s in c["steps"]}
        stix = resolve_stix_ids(all_ids)
        report["unresolved_attack_ids"] = sorted(all_ids - set(stix))
        for chain in raw:
            for step in chain["steps"]:
                step["stix_id"] = stix.get(step["attack_id"], "")
    return raw, report


def print_stats(chains: list[dict], report: dict) -> None:
    by_plan: dict[str, list[dict]] = {}
    for c in chains:
        by_plan.setdefault(c["adversary"], []).append(c)
    print(f"{'adversary':30} chains  steps/chain")
    for adv, cs in by_plan.items():
        sizes = [len(c["steps"]) for c in cs]
        print(f"{adv:30} {len(cs):5}   {sizes}")
    total_steps = sum(len(c["steps"]) for c in chains)
    print(f"\nTOTAL {len(chains)} chains / {total_steps} steps")

    dropped = report["dropped_malformed_ids"]
    if dropped:
        print(f"[INFO] dropped {len(dropped)} steps with a malformed "
              f"attack_id: {', '.join(dropped)}")
    rolled = report["rolled_up_subtechniques"]
    if rolled:
        print(f"[INFO] {len(rolled)} distinct sub-technique labels rolled up "
              f"to their parent (graph holds no sub-techniques); originals "
              f"kept in attack_ids_raw")
    unresolved = report["unresolved_attack_ids"]
    if unresolved:
        print(f"\n[WARN] {len(unresolved)} parent ATT&CK IDs still not found "
              f"in Neo4j (no stix_id, retrieval cannot score them):")
        print("       " + ", ".join(unresolved))


def main() -> None:
    parser = argparse.ArgumentParser(description="Build CTID attack chains")
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
