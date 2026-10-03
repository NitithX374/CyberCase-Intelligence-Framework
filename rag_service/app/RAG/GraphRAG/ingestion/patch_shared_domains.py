"""
Patch the shared entities in place
==================================
``stix_parser.finalize_parsing`` now files an entity that both the Enterprise
and the Mobile bundle list under enterprise. The live stores were ingested
before that change and hold all 45 such entities as mobile, which the
Enterprise filter of entity search drops (APT28, APT41, Sandworm Team, ...).

A full re-ingest clears both stores and re-embeds everything: about 4 h on the
development laptop, with the deployed service reading an empty or partial
store meanwhile. For these entities the embedded text is the same in both
bundles, so their vectors would not change; only stored fields would. This
writes, for those entities only, exactly the Neo4j properties and Qdrant
payload a re-ingest would write, and refuses if any embedded text would change
(that needs a re-embedding, i.e. the full re-ingest).

Dry run by default; ``--apply`` writes. Check with verify_ingest around it.

Usage (from rag_service/app; PYTHONUTF8=1 on Windows):
    python -m RAG.GraphRAG.ingestion.verify_ingest --save before.json
    python -m RAG.GraphRAG.ingestion.patch_shared_domains            # dry run
    python -m RAG.GraphRAG.ingestion.patch_shared_domains --apply
    python -m RAG.GraphRAG.ingestion.verify_ingest --save after.json --compare before.json
"""

from __future__ import annotations

import argparse
from collections import Counter
from typing import Any

from .. import config
from ..models import AttackEntity
from .graph_loader import GraphLoader
from .stix_parser import parse_all_domains
from .vector_loader import uuid_from_stix_id
from .verify_ingest import shared_entities


def neo4j_props(entity: AttackEntity) -> dict[str, Any]:
    """The node properties ingestion writes for this entity."""
    return GraphLoader.__new__(GraphLoader)._entity_to_props(entity)


def qdrant_payload(entity: AttackEntity) -> dict[str, Any] | None:
    """The point payload ingestion writes (None: not embedded, no description).

    Mirrors ``VectorLoader.load_entities``; the ``document`` field is the
    embedded text, so a change there means the vector would change too.
    """
    if not entity.description:
        return None
    text = f"{entity.node_label}: {entity.name}. {entity.description}"[:8000]
    return {
        "stix_id": entity.stix_id,
        "attack_id": entity.attack_id,
        "entity_type": "Node",
        "node_label": entity.node_label,
        "name": entity.name,
        "domain": entity.domain,
        "url": entity.url,
        "document": text,
    }


def _diff(old: dict[str, Any], new: dict[str, Any]) -> dict[str, tuple[Any, Any]]:
    return {k: (old.get(k), v) for k, v in new.items() if old.get(k) != v}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="write the changes (default: dry run)")
    args = ap.parse_args()

    shared = shared_entities()
    parsed = {e.stix_id: e for e in parse_all_domains().entities}
    entities = [parsed[sid] for sid in sorted(shared) if sid in parsed]
    print(f"\n{len(shared)} entities in more than one bundle; {len(entities)} after deduplication, "
          f"filed now as {dict(Counter(e.domain for e in entities))}")

    from neo4j import GraphDatabase
    from qdrant_client import QdrantClient

    driver = GraphDatabase.driver(config.NEO4J_URI, auth=(config.NEO4J_USER, config.NEO4J_PASSWORD))
    if not config.QDRANT_URL:
        raise SystemExit("QDRANT_URL is not set")
    client = QdrantClient(url=config.QDRANT_URL, api_key=config.QDRANT_API_KEY)
    collection = config.QDRANT_COLLECTION_ENTITIES

    try:
        with driver.session() as session:
            live_nodes = {
                r["sid"]: dict(r["n"])
                for r in session.run(
                    "MATCH (n:Entity) WHERE n.stix_id IN $sids RETURN n.stix_id AS sid, n AS n",
                    sids=[e.stix_id for e in entities],
                )
            }
        live_points = {
            (p.payload or {}).get("stix_id"): p.payload or {}
            for p in client.retrieve(
                collection_name=collection,
                ids=[uuid_from_stix_id(e.stix_id) for e in entities],
                with_payload=True,
                with_vectors=False,
            )
        }

        node_rows, point_rows = [], []
        node_fields, point_fields = Counter(), Counter()
        missing, text_changed = [], []
        for e in entities:
            if e.stix_id not in live_nodes:
                missing.append(f"neo4j:{e.name}")
            else:
                new = neo4j_props(e)
                diff = _diff(live_nodes[e.stix_id], new)
                if diff:
                    node_rows.append({"sid": e.stix_id, "props": new})
                    node_fields.update(diff.keys())
            payload = qdrant_payload(e)
            if payload is None:
                continue
            if e.stix_id not in live_points:
                missing.append(f"qdrant:{e.name}")
                continue
            diff = _diff(live_points[e.stix_id], payload)
            if "document" in diff:
                text_changed.append(e.name)
            if diff:
                point_rows.append((e.stix_id, payload))
                point_fields.update(diff.keys())

        print(f"neo4j : {len(node_rows)} nodes to update, fields {dict(node_fields)}")
        print(f"qdrant: {len(point_rows)} points to update, fields {dict(point_fields)}")
        if missing:
            print(f"not found in the live stores: {missing}")
        if text_changed:
            raise SystemExit(f"REFUSED: the embedded text would change for {text_changed}; "
                             "that needs new vectors, i.e. the full re-ingest")
        if not args.apply:
            print("\nDry run — nothing written. Re-run with --apply.")
            return

        with driver.session() as session:
            written = session.run(
                "UNWIND $rows AS r MATCH (n:Entity {stix_id: r.sid}) SET n += r.props RETURN count(n) AS c",
                rows=node_rows,
            ).single()["c"]
        for sid, payload in point_rows:
            client.set_payload(collection_name=collection, payload=payload,
                               points=[uuid_from_stix_id(sid)], wait=True)
        print(f"\nWritten: {written} Neo4j nodes, {len(point_rows)} Qdrant points. "
              "Now run verify_ingest --compare.")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
