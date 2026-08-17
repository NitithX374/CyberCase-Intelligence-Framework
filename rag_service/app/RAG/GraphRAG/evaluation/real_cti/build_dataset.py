"""
Select the real-CTI chain set
==============================
Merges the CTID and CISA chain pools into one balanced selection of N chains
— the input to Thai case-file drafting, not yet an eval dataset.

Selection, and why it is not just "take the first N":

  - the two sources are drawn in equal share by default. CTID chains carry a
    genuine per-step order from an emulation plan; CISA chains are excerpts
    of real incidents. Loading up on either would let one property of the
    source stand in for the property being measured.
  - chains are taken round-robin across adversaries/advisories, so a plan
    with 19 chains (APT29) cannot crowd out one with 3 (FIN7).
  - selection is seeded, so the published sample is reproducible.

Usage:
    cd rag_service/app
    python -m RAG.GraphRAG.evaluation.real_cti.build_dataset --num 100
"""

from __future__ import annotations

import argparse
import io
import json
import random
import sys
from collections import Counter, defaultdict
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

DATA_DIR = Path(__file__).resolve().parent / "data"
CTID_PATH = DATA_DIR / "ctid_chains.json"
CISA_PATH = DATA_DIR / "cisa_chains.json"
OUT_PATH = DATA_DIR / "real_cti_selection.json"


def _load(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"{path} missing — run its loader first")
    return json.loads(path.read_text(encoding="utf-8"))["chains"]


def _bucket_key(chain: dict) -> str:
    """The document a chain came from — the unit diversity is spread over."""
    return chain.get("adversary") or chain.get("advisory_id", "?")


def round_robin(chains: list[dict], want: int, rng: random.Random) -> list[dict]:
    """Take up to `want` chains, cycling over source documents."""
    buckets: dict[str, list[dict]] = defaultdict(list)
    for chain in chains:
        buckets[_bucket_key(chain)].append(chain)
    for items in buckets.values():
        rng.shuffle(items)

    order = sorted(buckets)
    rng.shuffle(order)
    picked: list[dict] = []
    while len(picked) < want:
        drained = True
        for key in order:
            if not buckets[key]:
                continue
            drained = False
            picked.append(buckets[key].pop())
            if len(picked) >= want:
                break
        if drained:
            break  # pool exhausted; caller reports the shortfall
    return picked


def select(num: int, seed: int, ctid_share: float) -> tuple[list[dict], dict]:
    rng = random.Random(seed)
    ctid_pool, cisa_pool = _load(CTID_PATH), _load(CISA_PATH)

    want_ctid = min(round(num * ctid_share), len(ctid_pool))
    want_cisa = min(num - want_ctid, len(cisa_pool))
    # if one pool is short, let the other cover the gap rather than
    # silently returning fewer than asked for
    want_ctid = min(num - want_cisa, len(ctid_pool))

    picked = (round_robin(ctid_pool, want_ctid, rng)
              + round_robin(cisa_pool, want_cisa, rng))
    rng.shuffle(picked)

    report = {
        "requested": num,
        "selected": len(picked),
        "seed": seed,
        "pool_sizes": {"ctid": len(ctid_pool), "cisa": len(cisa_pool)},
        "by_source": dict(Counter(c["source"] for c in picked)),
        "by_document": dict(Counter(_bucket_key(c) for c in picked)),
        "total_steps": sum(len(c["steps"]) for c in picked),
    }
    return picked, report


def main() -> None:
    parser = argparse.ArgumentParser(description="Select real-CTI chains")
    parser.add_argument("--num", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--ctid-share", type=float, default=0.5,
                        help="Fraction of the selection taken from CTID")
    parser.add_argument("--out", type=str, default=str(OUT_PATH))
    args = parser.parse_args()

    picked, report = select(args.num, args.seed, args.ctid_share)

    print(f"selected {report['selected']}/{report['requested']} chains "
          f"({report['total_steps']} steps)")
    print(f"pools: ctid={report['pool_sizes']['ctid']} "
          f"cisa={report['pool_sizes']['cisa']}")
    for src, n in report["by_source"].items():
        print(f"  {src:38} {n}")
    if report["selected"] < report["requested"]:
        print(f"[WARN] pools hold only {sum(report['pool_sizes'].values())} "
              f"chains in total")
    docs = sorted(report["by_document"].items(), key=lambda kv: -kv[1])
    print("per document: " + ", ".join(f"{k}={v}" for k, v in docs))

    out = Path(args.out)
    with open(out, "w", encoding="utf-8") as f:
        json.dump({**report, "chains": picked}, f, indent=2, ensure_ascii=False)
    print(f"\n[OUT] {out}")


if __name__ == "__main__":
    main()
