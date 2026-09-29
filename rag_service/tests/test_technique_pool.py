"""
Unit Tests for the technique pool (config.TECHNIQUE_POOL)
=========================================================
Which vector hits may evidence a technique, the parent-technique slot key,
and that retrieve() / retrieve_multi_quota() filter and dedup by it.
"""

import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent.parent / "app"
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

from RAG.GraphRAG.retrieval.hybrid_retriever import (
    GraphRAGResult,
    HybridRetriever,
    in_technique_pool,
)
from RAG.GraphRAG.retrieval.vector_retriever import VectorResult

AP_PARENT = "attack-pattern--parent"
AP_SUB = "attack-pattern--sub"


def node(sid, name, label, score=0.5, attack_id=""):
    md = {"entity_type": "Node", "node_label": label, "name": name, "attack_id": attack_id}
    return VectorResult(document=name, metadata=md, score=score, stix_id=sid)


def rel(sid, source_id, target_id, score=0.5):
    md = {"entity_type": "Relationship", "edge_label": "USES",
          "source_id": source_id, "target_id": target_id}
    return VectorResult(document=sid, metadata=md, score=score, stix_id=sid)


def retriever(attack_ids=None):
    r = HybridRetriever.__new__(HybridRetriever)  # no models, no DB
    r._attack_ids = attack_ids if attack_ids is not None else {AP_PARENT: "T1566", AP_SUB: "T1566.001"}
    return r


class TestInTechniquePool:
    def test_techniques_and_subtechniques_are_kept(self):
        assert in_technique_pool(node("t", "Phishing", "Technique"), "q")
        assert in_technique_pool(node("s", "Spearphishing Attachment", "Subtechnique"), "q")

    def test_relationship_with_a_technique_end_is_kept(self):
        assert in_technique_pool(rel("r", "intrusion-set--apt", AP_SUB), "q")

    def test_relationship_without_a_technique_end_is_dropped(self):
        assert not in_technique_pool(rel("r", "intrusion-set--apt", "malware--x"), "q")

    def test_unnamed_group_and_software_are_dropped(self):
        assert not in_technique_pool(node("g", "APT29", "Group"), "the attacker sent mail")
        assert not in_technique_pool(node("s", "Mimikatz", "Software"), "dumped passwords")

    def test_group_or_software_named_in_the_query_is_kept(self):
        assert in_technique_pool(node("s", "Mimikatz", "Software"), "คนร้ายใช้ mimikatz ดึงรหัสผ่าน")

    def test_a_short_name_is_not_matched_inside_other_words(self):
        assert not in_technique_pool(node("s", "at", "Software"), "the attacker")

    def test_tactics_and_mitigations_are_dropped(self):
        assert not in_technique_pool(node("x", "Discovery", "Tactic"), "q")
        assert not in_technique_pool(node("m", "Audit", "Mitigation"), "q")


class TestTechniqueKey:
    def test_subtechnique_node_keys_to_its_parent(self):
        assert retriever()._technique_key(node("s", "SA", "Subtechnique", attack_id="T1566.001")) == "T1566"

    def test_relationship_keys_to_the_parent_of_its_technique_end(self):
        assert retriever()._technique_key(rel("r", "intrusion-set--apt", AP_SUB)) == "T1566"

    def test_unknown_technique_end_falls_back_to_its_stix_id(self):
        assert retriever({})._technique_key(rel("r", "intrusion-set--apt", AP_SUB)) == AP_SUB

    def test_named_software_keys_to_itself(self):
        assert retriever()._technique_key(node("malware--m", "Mimikatz", "Software")) == "malware--m"


class TestRetrieveFiltersAndDedups:
    def _retriever(self, hits):
        r = retriever()
        r.vector_retriever = type("V", (), {"search_all": lambda self, q, top_k: list(hits)})()
        r.reranker = type("R", (), {"rerank": lambda self, q, res, top_k: sorted(
            res, key=lambda h: h.score, reverse=True)})()
        return r

    def test_pool_and_one_slot_per_technique(self):
        hits = [
            rel("r1", "intrusion-set--apt", AP_SUB, score=0.9),
            node(AP_PARENT, "Phishing", "Technique", score=0.8, attack_id="T1566"),
            node("intrusion-set--apt", "APT29", "Group", score=0.95),
            node("attack-pattern--other", "Valid Accounts", "Technique", score=0.4, attack_id="T1078"),
        ]
        out = self._retriever(hits).retrieve("incident", expand_graph=False, technique_pool=True)
        # The group is out of the pool; the node and the relationship share
        # T1566, and the node wins it after the type re-weight (0.8 × 1.2 > 0.9).
        assert [vr.stix_id for vr in out.vector_results] == [AP_PARENT, "attack-pattern--other"]

    def test_pool_off_keeps_everything(self):
        hits = [rel("r1", "intrusion-set--apt", AP_SUB, 0.9),
                node("intrusion-set--apt", "APT29", "Group", 0.95)]
        out = self._retriever(hits).retrieve("incident", expand_graph=False, technique_pool=False)
        assert len(out.vector_results) == 2


class TestQuotaMergeDedups:
    def _retriever(self, per_query):
        r = retriever()
        calls = iter(per_query)
        r.retrieve = lambda query, **kwargs: next(calls)
        return r

    def _queries(self):
        q1 = GraphRAGResult(vector_results=[rel("r1", "intrusion-set--apt", AP_SUB, 0.9)], graph_results=[])
        q2 = GraphRAGResult(vector_results=[node(AP_PARENT, "Phishing", "Technique", 0.8, "T1566")],
                            graph_results=[])
        return [q1, q2]

    def test_same_technique_from_two_sub_queries_takes_one_slot(self):
        merged = self._retriever(self._queries()).retrieve_multi_quota(
            ["a", "b"], technique_pool=True)
        assert [vr.stix_id for vr in merged.vector_results] == ["r1"]

    def test_without_the_pool_each_document_takes_a_slot(self):
        merged = self._retriever(self._queries()).retrieve_multi_quota(
            ["a", "b"], technique_pool=False)
        assert [vr.stix_id for vr in merged.vector_results] == ["r1", AP_PARENT]
