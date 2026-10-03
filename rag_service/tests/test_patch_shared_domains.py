from RAG.GraphRAG.ingestion.patch_shared_domains import _diff, neo4j_props, qdrant_payload
from RAG.GraphRAG.models import Group


def _apt28(domain: str = "enterprise", description: str = "Russian threat group.") -> Group:
    return Group(
        stix_id="intrusion-set--a", attack_id="G0007", name="APT28",
        description=description, url="https://attack.mitre.org/groups/G0007",
        domain=domain, aliases=["APT28", "Fancy Bear"],
    )


def test_node_properties_are_the_ones_ingestion_writes() -> None:
    props = neo4j_props(_apt28())

    assert props["domain"] == "enterprise"
    assert props["aliases"] == ["APT28", "Fancy Bear"]
    assert props["stix_id"] == "intrusion-set--a"


def test_payload_carries_the_embedded_text_and_skips_entities_without_one() -> None:
    payload = qdrant_payload(_apt28())

    assert payload["document"] == "Group: APT28. Russian threat group."
    assert payload["domain"] == "enterprise"
    assert qdrant_payload(_apt28(description="")) is None


def test_only_the_domain_differs_between_the_live_and_the_patched_payload() -> None:
    live = qdrant_payload(_apt28(domain="mobile"))

    assert _diff(live, qdrant_payload(_apt28())) == {"domain": ("mobile", "enterprise")}
