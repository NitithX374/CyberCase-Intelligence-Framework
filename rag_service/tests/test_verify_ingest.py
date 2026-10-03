from RAG.GraphRAG.ingestion.verify_ingest import check_shared, compare


SHARED = {
    "intrusion-set--a": {"name": "APT28", "label": "Group", "domains": ["enterprise", "mobile"]},
    "intrusion-set--b": {"name": "APT41", "label": "Group", "domains": ["enterprise", "mobile"]},
}


def _snapshot(domain_of_shared: str, *, edges: int = 10) -> dict:
    filed = {sid: domain_of_shared for sid in SHARED}
    return {
        "neo4j": {
            "nodes": 5,
            "edges": edges,
            "labels": {"Group": 5},
            "edge_types": {"USES": edges},
            "domains": {"enterprise": 3, "mobile": 2} if domain_of_shared == "mobile" else {"enterprise": 5},
            "shared_domain": filed,
        },
        "qdrant": {
            "entity_points": 5,
            "relationship_points": edges,
            "domains": {"enterprise": 3, "mobile": 2} if domain_of_shared == "mobile" else {"enterprise": 5},
            "shared_domain": filed,
        },
    }


def test_shared_entities_filed_as_mobile_are_reported_in_both_stores() -> None:
    problems = check_shared(_snapshot("mobile"), SHARED)

    assert len(problems) == 2
    assert problems[0].startswith("neo4j: 2 of 2 not enterprise: APT28, APT41")
    assert problems[1].startswith("qdrant:")


def test_a_reingest_that_only_moves_the_shared_entities_passes() -> None:
    before, after = _snapshot("mobile"), _snapshot("enterprise")

    assert check_shared(after, SHARED) == []
    assert compare(before, after) == []


def test_a_reingest_that_loses_edges_is_reported() -> None:
    problems = compare(_snapshot("mobile"), _snapshot("enterprise", edges=9))

    assert "neo4j.edges: 10 -> 9" in problems
    assert "qdrant.relationship_points: 10 -> 9" in problems
