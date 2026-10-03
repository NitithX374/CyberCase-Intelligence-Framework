"""
Ingest check
============
A read-only snapshot of the live ATT&CK stores, taken before and after a
re-ingest to show that it changed what it should and nothing else.

What a re-ingest of the current parser should change: the 45 entities that
sit in both the Enterprise and the Mobile bundle (APT28, APT41, Sandworm Team,
...) move from domain "mobile" to "enterprise" (stix_parser._DOMAIN_PRIORITY).
What it should not change: node, edge and point counts, the label split and
the relationship types.

Nothing is written to Neo4j or Qdrant.

Usage (from rag_service/app; PYTHONUTF8=1 on Windows):
    python -m RAG.GraphRAG.ingestion.verify_ingest --save before.json
    # ... re-ingest ...
    python -m RAG.GraphRAG.ingestion.verify_ingest --save after.json --compare before.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .. import config
from .stix_parser import StixParser


def shared_entities() -> dict[str, dict[str, Any]]:
    """Entities that more than one configured ATT&CK bundle lists, by stix_id."""
    seen: dict[str, dict[str, Any]] = {}
    for domain, folder in config.ATTACK_DOMAINS.items():
        parser = StixParser()
        parser.parse_folder(folder, domain=domain)
        for entity in parser.entities:
            row = seen.setdefault(
                entity.stix_id,
                {"name": entity.name, "label": entity.node_label, "domains": []},
            )
            row["domains"].append(domain)
    return {sid: row for sid, row in seen.items() if len(row["domains"]) > 1}


def neo4j_snapshot(stix_ids: list[str]) -> dict[str, Any]:
    from neo4j import GraphDatabase

    driver = GraphDatabase.driver(
        config.NEO4J_URI, auth=(config.NEO4J_USER, config.NEO4J_PASSWORD)
    )
    try:
        with driver.session() as session:
            def rows(query: str, **params: Any) -> list[Any]:
                return list(session.run(query, **params))

            return {
                "nodes": rows("MATCH (n) RETURN count(n) AS c")[0]["c"],
                "edges": rows("MATCH ()-[r]->() RETURN count(r) AS c")[0]["c"],
                "labels": {
                    r["label"]: r["c"]
                    for r in rows(
                        "MATCH (n:Entity) UNWIND [l IN labels(n) WHERE l <> 'Entity'] AS label "
                        "RETURN label, count(*) AS c"
                    )
                },
                "edge_types": {
                    r["t"]: r["c"]
                    for r in rows("MATCH ()-[r]->() RETURN type(r) AS t, count(*) AS c")
                },
                "domains": {
                    str(r["d"]): r["c"]
                    for r in rows("MATCH (n:Entity) RETURN n.domain AS d, count(*) AS c")
                },
                "shared_domain": {
                    r["sid"]: r["d"]
                    for r in rows(
                        "MATCH (n:Entity) WHERE n.stix_id IN $sids "
                        "RETURN n.stix_id AS sid, n.domain AS d",
                        sids=stix_ids,
                    )
                },
            }
    finally:
        driver.close()


def qdrant_snapshot(stix_ids: list[str]) -> dict[str, Any]:
    from qdrant_client import QdrantClient

    from .vector_loader import uuid_from_stix_id

    if config.QDRANT_URL:
        client = QdrantClient(url=config.QDRANT_URL, api_key=config.QDRANT_API_KEY)
    elif config.QDRANT_HOST:
        client = QdrantClient(
            host=config.QDRANT_HOST, port=config.QDRANT_PORT, api_key=config.QDRANT_API_KEY
        )
    else:
        # An in-memory client would report an empty store as the result.
        raise SystemExit("Neither QDRANT_URL nor QDRANT_HOST is set")

    entities = config.QDRANT_COLLECTION_ENTITIES
    relationships = config.QDRANT_COLLECTION_RELATIONSHIPS

    domains: dict[str, int] = {}
    offset = None
    while True:
        points, offset = client.scroll(
            collection_name=entities,
            limit=1000,
            offset=offset,
            with_payload=["domain"],
            with_vectors=False,
        )
        for point in points:
            domain = str((point.payload or {}).get("domain"))
            domains[domain] = domains.get(domain, 0) + 1
        if offset is None:
            break

    shared = client.retrieve(
        collection_name=entities,
        ids=[uuid_from_stix_id(sid) for sid in stix_ids],
        with_payload=["stix_id", "domain"],
        with_vectors=False,
    )
    return {
        "entity_points": client.count(collection_name=entities, exact=True).count,
        "relationship_points": client.count(collection_name=relationships, exact=True).count,
        "domains": domains,
        "shared_domain": {
            (p.payload or {}).get("stix_id"): (p.payload or {}).get("domain") for p in shared
        },
    }


def check_shared(snapshot: dict[str, Any], shared: dict[str, dict[str, Any]]) -> list[str]:
    """Problems with where the shared entities are filed (empty list = all enterprise)."""
    problems = []
    for store in ("neo4j", "qdrant"):
        filed = snapshot[store]["shared_domain"]
        wrong = sorted(
            shared[sid]["name"] for sid, domain in filed.items() if sid in shared and domain != "enterprise"
        )
        if wrong:
            problems.append(f"{store}: {len(wrong)} of {len(filed)} not enterprise: {', '.join(wrong)}")
    return problems


def compare(before: dict[str, Any], after: dict[str, Any]) -> list[str]:
    """What changed that a re-ingest of the same ATT&CK release should not change."""
    problems = []
    for store, keys in (
        ("neo4j", ("nodes", "edges", "labels", "edge_types")),
        ("qdrant", ("entity_points", "relationship_points")),
    ):
        for key in keys:
            if before[store][key] != after[store][key]:
                problems.append(f"{store}.{key}: {before[store][key]} -> {after[store][key]}")
    for store in ("neo4j", "qdrant"):
        if sum(before[store]["domains"].values()) != sum(after[store]["domains"].values()):
            problems.append(f"{store}.domains total changed: {before[store]['domains']} -> {after[store]['domains']}")
    return problems


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--save", type=Path, help="write the snapshot to this JSON file")
    ap.add_argument("--compare", type=Path, help="an earlier snapshot to compare against")
    args = ap.parse_args()

    shared = shared_entities()
    sids = sorted(shared)
    snapshot = {
        "shared_entities": shared,
        "neo4j": neo4j_snapshot(sids),
        "qdrant": qdrant_snapshot(sids),
    }

    print(f"\nEntities in more than one bundle: {len(shared)}")
    for store in ("neo4j", "qdrant"):
        s = snapshot[store]
        counts = (
            f"{s['nodes']} nodes, {s['edges']} edges"
            if store == "neo4j"
            else f"{s['entity_points']} entity points, {s['relationship_points']} relationship points"
        )
        print(f"{store}: {counts}; domains {s['domains']}")
        filed: dict[str, int] = {}
        for domain in s["shared_domain"].values():
            filed[str(domain)] = filed.get(str(domain), 0) + 1
        print(f"  shared entities filed as {filed} ({len(s['shared_domain'])} found)")

    problems = check_shared(snapshot, shared)
    if args.compare:
        problems += compare(json.loads(args.compare.read_text(encoding="utf-8")), snapshot)
    print("\n" + ("\n".join(f"PROBLEM {p}" for p in problems) if problems else "OK"))

    if args.save:
        args.save.write_text(json.dumps(snapshot, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"Saved {args.save}")


if __name__ == "__main__":
    main()
