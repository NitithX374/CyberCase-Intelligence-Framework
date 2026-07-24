"""
Verify Eval Dataset Against the Live Index (Neo4j + Qdrant)
============================================================
A sample's gold is only fair if the retrieval stack can actually find it.
Chains sampled from the local STIX bundle may reference entities that were
never ingested (the bundle carries more campaigns/techniques than the graph),
which would make those samples permanently unanswerable and drag eval scores
down for the wrong reason.

This script checks every gold STIX id in a dataset against:
  - Neo4j   : node exists (graph expansion can reach it)
  - Qdrant  : entity is embedded (vector search can surface it)

and writes a filtered dataset containing only fully-verified samples.

Usage:
    cd rag_service/app
    python -m RAG.GraphRAG.evaluation.verify_dataset_against_index \
        --input incident_eval_set.json --out incident_eval_set_verified.json
    # inspect only (no file written):
    python -m RAG.GraphRAG.evaluation.verify_dataset_against_index \
        --input incident_eval_set.json --report-only
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from collections import Counter
from pathlib import Path

if __package__ is None or __package__ == "evaluation":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    __package__ = "GraphRAG.evaluation"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

OUT_DIR = Path(__file__).resolve().parent / "data"


def gold_stix_ids(sample: dict) -> set[str]:
    ids = set(sample.get("relevant_stix_ids") or [])
    for st in sample.get("attack_steps") or []:
        ids.update(st.get("gold_stix_ids") or [])
    return {i for i in ids if i}


def neo4j_present(ids: set[str]) -> set[str]:
    """Subset of ids that exist as nodes in Neo4j."""
    from neo4j import GraphDatabase, Query

    from ..config import NEO4J_PASSWORD, NEO4J_URI, NEO4J_USER

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    try:
        with driver.session() as s:
            rows = s.run(
                Query("""
                UNWIND $ids AS sid
                MATCH (n {stix_id: sid})
                RETURN DISTINCT sid AS sid
                """),
                ids=sorted(ids),
            )
            return {r["sid"] for r in rows}
    finally:
        driver.close()


def qdrant_present(ids: set[str]) -> set[str]:
    """Subset of ids embedded in the Qdrant entity collection."""
    from qdrant_client import QdrantClient

    from ..config import (
        QDRANT_API_KEY, QDRANT_COLLECTION_ENTITIES, QDRANT_URL,
    )

    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    try:
        found: set[str] = set()
        offset = None
        while True:
            points, offset = client.scroll(
                collection_name=QDRANT_COLLECTION_ENTITIES,
                limit=1000, offset=offset,
                with_payload=["stix_id"], with_vectors=False,
            )
            for p in points:
                sid = (p.payload or {}).get("stix_id")
                if sid in ids:
                    found.add(sid)
            if offset is None:
                break
        return found
    finally:
        client.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify dataset against live index")
    parser.add_argument("--input", required=True, help="Dataset filename under data/")
    parser.add_argument("--out", default="", help="Filtered output filename under data/")
    parser.add_argument("--report-only", action="store_true",
                        help="Print the report without writing a filtered file")
    parser.add_argument("--skip-qdrant", action="store_true",
                        help="Check Neo4j only (faster)")
    args = parser.parse_args()

    with open(OUT_DIR / args.input, "r", encoding="utf-8") as f:
        samples = json.load(f)

    all_ids: set[str] = set()
    for s in samples:
        all_ids |= gold_stix_ids(s)
    print(f"[VERIFY] {len(samples)} samples · {len(all_ids)} unique gold STIX ids")

    in_neo = neo4j_present(all_ids)
    print(f"[VERIFY] Neo4j : {len(in_neo)}/{len(all_ids)} present")

    if args.skip_qdrant:
        in_qdrant = all_ids
    else:
        in_qdrant = qdrant_present(all_ids)
        print(f"[VERIFY] Qdrant: {len(in_qdrant)}/{len(all_ids)} present")

    retrievable = in_neo & in_qdrant
    missing = all_ids - retrievable

    kept, dropped = [], []
    for s in samples:
        gold = gold_stix_ids(s)
        bad = gold - retrievable
        (dropped if bad else kept).append((s, bad))

    print(f"\n[VERIFY] usable {len(kept)} · unusable {len(dropped)}")
    if dropped:
        by_source: Counter = Counter()
        for s, bad in dropped:
            by_source[s.get("source_prov", "?")] += 1
            if len(by_source) <= 12:
                print(f"  {s.get('id')}: {len(bad)} gold id(s) not retrievable")
    if missing:
        print(f"\n[VERIFY] {len(missing)} gold ids missing from the index "
              f"(sample: {sorted(missing)[:3]})")

    if not args.report_only:
        out_name = args.out or (Path(args.input).stem + "_verified.json")
        with open(OUT_DIR / out_name, "w", encoding="utf-8") as f:
            json.dump([s for s, _ in kept], f, indent=2, ensure_ascii=False)
        print(f"\n[VERIFY] Saved {len(kept)} verified samples: {OUT_DIR / out_name}")


if __name__ == "__main__":
    main()
