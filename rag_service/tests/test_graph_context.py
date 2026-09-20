"""
Unit Tests for the graph section of the LLM context
====================================================
Subgraph rendering (direction, cap, no procedure text), whole-subgraph context
budgeting, and technique-first subgraph selection under quota retrieval.
"""

import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent.parent / "app"
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

from RAG.GraphRAG.pipeline.context_builder import build_context
from RAG.GraphRAG.retrieval.graph_retriever import GraphEdge, GraphNode, SubgraphResult
from RAG.GraphRAG.retrieval.hybrid_retriever import GraphRAGResult, HybridRetriever
from RAG.GraphRAG.retrieval.vector_retriever import VectorResult


def node(sid, name, label, attack_id=""):
    return GraphNode(stix_id=sid, name=name, label=label, attack_id=attack_id)


def subgraph(center, edges):
    return SubgraphResult(center_node=center, neighbors=[], edges=edges)


def node_hit(sid, name, label, score):
    md = {"entity_type": "Node", "node_label": label, "name": name}
    return VectorResult(document=name, metadata=md, score=score, stix_id=sid)


def rel_hit(sid, source_id, source, target_id, target, score):
    md = {
        "entity_type": "Relationship",
        "edge_label": "USES",
        "source_id": source_id,
        "source_name": source,
        "target_id": target_id,
        "target_name": target,
    }
    return VectorResult(document=f"{source} uses {target}", metadata=md, score=score, stix_id=sid)


class TestSubgraphToText:
    def test_labels_follow_edge_direction(self):
        sg = subgraph(
            node("g1", "FIN7", "Group", "G0046"),
            [
                GraphEdge("USES", "FIN7", "Mimikatz", "FIN7 has used Mimikatz."),
                GraphEdge("ATTRIBUTED_TO", "Campaign X", "FIN7"),
            ],
        )
        text = sg.to_text()
        assert "├── Uses: Mimikatz" in text
        assert "Used by" not in text
        assert "├── Attributed from: Campaign X" in text

    def test_procedure_descriptions_are_not_rendered(self):
        sg = subgraph(
            node("t1", "Web Shell", "Subtechnique", "T1505.003"),
            [GraphEdge("USES", "China Chopper", "Web Shell", "China Chopper is a web shell.")],
        )
        text = sg.to_text()
        assert "China Chopper is a web shell" not in text
        assert "└──" not in text

    def test_cap_keeps_retrieved_names_first(self):
        edges = [GraphEdge("USES", f"Tool{i}", "Screen Capture") for i in range(30)]
        edges.append(GraphEdge("USES", "AsyncRAT", "Screen Capture"))
        sg = subgraph(node("t2", "Screen Capture", "Technique", "T1113"), edges)

        text = sg.to_text(max_names=3, priority_names={"AsyncRAT"})

        assert "├── Used by: AsyncRAT, Tool0, Tool1 (+28 more)" in text


class TestBuildContextGraphBudget:
    def test_oversized_subgraph_is_skipped_whole_and_later_ones_still_render(self):
        big = subgraph(
            node("g1", "FIN7", "Group", "G0046"),
            [GraphEdge("USES", "FIN7", f"LongNeighbourName{i:04d}") for i in range(10)],
        )
        small = subgraph(
            node("t1", "Exploit Public-Facing Application", "Technique", "T1190"),
            [GraphEdge("IN_TACTIC", "Exploit Public-Facing Application", "Initial Access")],
        )
        result = GraphRAGResult(
            vector_results=[node_hit("v1", "Web Shell", "Subtechnique", 0.9)],
            graph_results=[big, small],
        )
        base = len(build_context(result, max_graph=0))
        budget = base + 200  # room for the small subgraph only

        context = build_context(result, max_context_length=budget, max_graph=8)

        assert "## Technique: Exploit Public-Facing Application (T1190)" in context
        assert "FIN7" not in context
        assert "truncated" not in context
        assert len(context) <= budget

    def test_no_graph_header_when_nothing_is_rendered(self):
        result = GraphRAGResult(
            vector_results=[node_hit("v1", "Web Shell", "Subtechnique", 0.9)],
            graph_results=[subgraph(node("t1", "Web Shell", "Subtechnique"), [])],
        )
        assert "Graph Context" not in build_context(result, max_graph=0)


class TestQuotaGraphSelection:
    def _retriever(self, per_query):
        retriever = HybridRetriever.__new__(HybridRetriever)  # no models, no DB
        calls = iter(per_query)
        retriever.retrieve = lambda query, **kwargs: next(calls)
        return retriever

    def test_technique_subgraphs_fill_the_cap_before_groups(self):
        fin7 = node("g1", "FIN7", "Group", "G0046")
        shim = node("t1", "Application Shimming", "Subtechnique", "T1546.011")
        rsd = node("t2", "Remote System Discovery", "Technique", "T1018")
        # Query 1 (the whole incident): a weak relationship hit seeds a group
        # first, then the technique. Query 2: a strong technique hit.
        q1 = GraphRAGResult(
            vector_results=[rel_hit("r1", "g1", "FIN7", "t1", "Application Shimming", 0.1)],
            graph_results=[subgraph(fin7, []), subgraph(shim, [])],
        )
        q2 = GraphRAGResult(
            vector_results=[node_hit("t2", "Remote System Discovery", "Technique", 0.85)],
            graph_results=[subgraph(rsd, [])],
        )

        merged = self._retriever([q1, q2]).retrieve_multi_quota(
            ["incident", "sub-query"], per_query_k=3, max_graph=2
        )

        assert [sg.center_node.name for sg in merged.graph_results] == [
            "Remote System Discovery",
            "Application Shimming",
        ]

    def test_groups_fill_remaining_slots(self):
        fin7 = node("g1", "FIN7", "Group", "G0046")
        shim = node("t1", "Application Shimming", "Subtechnique", "T1546.011")
        q1 = GraphRAGResult(
            vector_results=[rel_hit("r1", "g1", "FIN7", "t1", "Application Shimming", 0.1)],
            graph_results=[subgraph(fin7, []), subgraph(shim, [])],
        )

        merged = self._retriever([q1]).retrieve_multi_quota(["incident"], max_graph=8)

        assert [sg.center_node.name for sg in merged.graph_results] == [
            "Application Shimming",
            "FIN7",
        ]
