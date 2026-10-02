"""
Unit Tests for GraphRetriever.expand_batch
==========================================
The three batched lookups go through the indexed ``:Entity`` label, do not
fetch edge descriptions nobody renders, and name a node by its ATT&CK label
whatever order Neo4j returns its labels in.
"""

import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent.parent / "app"
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

from RAG.GraphRAG.retrieval.graph_retriever import GraphRetriever, _own_label

TECH = "attack-pattern--1"


class _Session:
    def __init__(self, log):
        self.log = log

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def run(self, query, **params):
        text = getattr(query, "text", str(query))
        self.log.append(text)
        if "RETURN sid AS sid, n AS n" in text:
            return [{"sid": TECH, "labels": ["Entity", "Technique"],
                     "n": {"stix_id": TECH, "name": "Phishing", "attack_id": "T1566",
                           "description": "d" * 400}}]
        if "-[r]->(m)" in text:  # outgoing
            return [{"sid": TECH, "rel_type": "IN_TACTIC", "target_id": "x-mitre-tactic--1",
                     "target_name": "Initial Access", "target_attack_id": "TA0001",
                     "target_labels": ["Entity", "Tactic"]}]
        return [{"sid": TECH, "rel_type": "USES", "source_id": "intrusion-set--1",
                 "source_name": "APT28", "source_attack_id": "G0007",
                 "source_labels": ["Group", "Entity"]}]


class _Driver:
    def __init__(self):
        self.log = []

    def session(self):
        return _Session(self.log)


def _retriever():
    g = GraphRetriever.__new__(GraphRetriever)  # no Neo4j
    g.driver = _Driver()
    return g


def test_own_label_ignores_the_shared_entity_label():
    assert _own_label(["Entity", "Technique"]) == "Technique"
    assert _own_label(["Group", "Entity"]) == "Group"
    assert _own_label(["Entity"]) == "Unknown"
    assert _own_label(None) == "Unknown"


def test_expand_builds_the_subgraph_from_three_indexed_queries():
    g = _retriever()

    [sg] = g.expand([TECH, TECH])  # duplicates collapse

    assert len(g.driver.log) == 3
    assert all("(n:Entity {stix_id: sid})" in q for q in g.driver.log)
    assert not any("description" in q for q in g.driver.log[1:])  # edges: names only
    assert (sg.center_node.label, sg.center_node.attack_id) == ("Technique", "T1566")
    assert len(sg.center_node.description) == 300
    assert [(n.name, n.label) for n in sg.neighbors] == [("Initial Access", "Tactic"), ("APT28", "Group")]
    assert [(e.edge_label, e.source_name, e.target_name) for e in sg.edges] == [
        ("IN_TACTIC", "Phishing", "Initial Access"), ("USES", "APT28", "Phishing")]


def test_expand_with_no_seed_asks_nothing():
    g = _retriever()
    assert g.expand([]) == []
    assert g.driver.log == []
