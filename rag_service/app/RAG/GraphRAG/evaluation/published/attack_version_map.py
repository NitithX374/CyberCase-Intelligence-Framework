"""
ATT&CK Version Reconciliation
===============================
Published TTP-annotation benchmarks (TRAM, Procedures, Expert) were labelled
against an older ATT&CK release than the one this project indexes.

  their labels : ~v14 era (their assets/mitre_kb.json holds 780 technique IDs,
                 including long-revoked ones like T1043 / T1064)
  our index    : v19.0 (821 live technique + sub-technique IDs)

Between those releases MITRE revoked whole families. The ones that actually
show up in the benchmark gold sets:

  T1562.*   Impair Defenses          -> revoked in v19
  T1574.002 DLL Side-Loading         -> merged into T1574.001 "DLL"
  T1070.001 Clear Windows Event Logs -> revoked
  T1043     Commonly Used Port       -> revoked long ago
  T1064     Scripting                -> deprecated long ago

Scoring a v19 retriever against v14 gold without reconciling these puts a hard
ceiling on recall that has nothing to do with retrieval quality. This module
derives the mapping from the STIX bundles already in the repo, so the fix is
reproducible rather than hand-maintained.

Two STIX signals are used:
  - `revoked-by` relationships: old attack-pattern -> its replacement. This is
    the authoritative "renamed / merged into" edge.
  - `x_mitre_deprecated`: retired with no replacement. Nothing to map to, so
    those gold IDs are unscoreable and get reported, not silently dropped.

Usage:
    cd rag_service/app
    python -m RAG.GraphRAG.evaluation.published.attack_version_map
    python -m RAG.GraphRAG.evaluation.published.attack_version_map --stats
"""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

_REPO_ROOT = Path(__file__).resolve().parents[6]
STIX_ROOT = _REPO_ROOT / "Mitre_ATT&CK Doc"
DATA_DIR = Path(__file__).resolve().parent / "data"
OUTPUT_PATH = DATA_DIR / "attack_version_map.json"

_VERSION_RE = re.compile(r"-(\d+)\.(\d+)\.json$")
_DOMAINS = ("enterprise-attack", "ics-attack", "mobile-attack")

BENCHMARKS = ("tram", "expert", "procedures")


def latest_bundle(domain_dir: Path) -> Path | None:
    """Newest versioned bundle in a domain folder (e.g. enterprise-attack-19.0.json)."""
    best: tuple[int, int] | None = None
    best_path: Path | None = None
    for p in domain_dir.glob("*.json"):
        m = _VERSION_RE.search(p.name)
        if not m:
            continue
        version = (int(m.group(1)), int(m.group(2)))
        if best is None or version > best:
            best, best_path = version, p
    return best_path


def _attack_id(obj: dict) -> str | None:
    for ref in obj.get("external_references", []):
        if ref.get("source_name") == "mitre-attack":
            return ref.get("external_id")
    return None


def build_map() -> dict:
    """Derive {old_attack_id: new_attack_id} plus the dead-end list."""
    revoked_to: dict[str, str] = {}
    deprecated: dict[str, str] = {}
    live: set[str] = set()
    bundles: list[str] = []

    for domain in _DOMAINS:
        bundle_path = latest_bundle(STIX_ROOT / domain)
        if bundle_path is None:
            continue
        bundles.append(bundle_path.name)
        objects = json.loads(bundle_path.read_text(encoding="utf-8"))["objects"]

        by_stix = {o["id"]: o for o in objects if o.get("type") == "attack-pattern"}

        for obj in by_stix.values():
            aid = _attack_id(obj)
            if not aid:
                continue
            if obj.get("revoked"):
                continue  # the replacement comes from the relationship pass below
            if obj.get("x_mitre_deprecated"):
                deprecated[aid] = "deprecated"
                continue
            live.add(aid)

        for obj in objects:
            if obj.get("type") != "relationship":
                continue
            if obj.get("relationship_type") != "revoked-by":
                continue
            src = by_stix.get(obj.get("source_ref", ""))
            dst = by_stix.get(obj.get("target_ref", ""))
            if not src or not dst:
                continue
            old_id, new_id = _attack_id(src), _attack_id(dst)
            if old_id and new_id and old_id != new_id:
                revoked_to[old_id] = new_id

    # Follow chains (A revoked-by B, B revoked-by C) to the final landing spot.
    resolved: dict[str, str] = {}
    for old_id in revoked_to:
        seen = {old_id}
        cur = revoked_to[old_id]
        while cur in revoked_to and cur not in seen:
            seen.add(cur)
            cur = revoked_to[cur]
        resolved[old_id] = cur

    # A revoked ID whose replacement is itself dead is a dead end, not a mapping.
    dead_chain = {k: v for k, v in resolved.items() if v not in live}
    resolved = {k: v for k, v in resolved.items() if v in live}

    dead_ends = dict(deprecated)
    dead_ends.update({k: "revoked->" + v + " (also dead)" for k, v in dead_chain.items()})

    return {
        "source_bundles": bundles,
        "live_ids": sorted(live),
        "revoked_to": dict(sorted(resolved.items())),
        "dead_ends": dict(sorted(dead_ends.items())),
    }


class VersionMap:
    """Applies the derived mapping to benchmark gold labels."""

    def __init__(self, payload: dict):
        self.revoked_to: dict[str, str] = payload["revoked_to"]
        self.live: set[str] = set(payload["live_ids"])
        self.dead_ends: dict[str, str] = payload["dead_ends"]

    @classmethod
    def load(cls, path: Path = OUTPUT_PATH) -> "VersionMap":
        if not path.exists():
            raise FileNotFoundError(
                str(path) + " missing - run:\n"
                "  python -m RAG.GraphRAG.evaluation.published.attack_version_map"
            )
        return cls(json.loads(path.read_text(encoding="utf-8")))

    def map_id(self, attack_id: str) -> str | None:
        """Current-release ID for one label, or None when it has no live successor.

        A sub-technique whose own number was retired but whose parent survived
        falls back to the parent - that is the least-lossy reading of the old
        label, and it is exactly what MITRE did when it merged sub-techniques.
        """
        if attack_id in self.live:
            return attack_id
        if attack_id in self.revoked_to:
            return self.revoked_to[attack_id]
        if "." in attack_id:
            parent = attack_id.split(".")[0]
            if parent in self.live:
                return parent
            if parent in self.revoked_to:
                return self.revoked_to[parent]
        return None

    def map_gold(self, gold: list[str]) -> tuple[list[str], list[str]]:
        """Map a gold list. Returns (mapped_ids, dropped_ids)."""
        mapped: list[str] = []
        dropped: list[str] = []
        for gid in gold:
            new = self.map_id(gid)
            if new is None:
                dropped.append(gid)
            elif new not in mapped:
                mapped.append(new)
        return mapped, dropped


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the ATT&CK version reconciliation map")
    parser.add_argument("--stats", action="store_true", help="report gold reachability per benchmark")
    args = parser.parse_args()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    payload = build_map()
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print("[MAP] bundles     : " + ", ".join(payload["source_bundles"]))
    print("[MAP] live ids    : " + str(len(payload["live_ids"])))
    print("[MAP] revoked->new: " + str(len(payload["revoked_to"])))
    print("[MAP] dead ends   : " + str(len(payload["dead_ends"])))
    print("[MAP] written to  : " + str(OUTPUT_PATH))

    if not args.stats:
        return

    vmap = VersionMap(payload)
    print("\n[STATS] gold-label reachability per benchmark")
    for name in BENCHMARKS:
        path = DATA_DIR / (name + "_zeroshot_test.json")
        if not path.exists():
            print("  " + name.ljust(12) + "(not fetched)")
            continue
        rows = json.loads(path.read_text(encoding="utf-8"))
        all_gold = {g for r in rows for g in r["gold"]}
        remapped = {g for g in all_gold if vmap.map_id(g) not in (None, g)}
        dropped = {g for g in all_gold if vmap.map_id(g) is None}
        print(
            "  " + name.ljust(12)
            + str(len(rows)).rjust(5) + " samples | "
            + str(len(all_gold)).rjust(3) + " unique gold | "
            + "remapped " + str(len(remapped)).rjust(2) + " | "
            + "unscoreable " + str(len(dropped)).rjust(2) + " "
            + (str(sorted(dropped)) if dropped else "")
        )
        for g in sorted(remapped):
            print("      " + g.ljust(12) + " -> " + str(vmap.map_id(g)))


if __name__ == "__main__":
    main()
