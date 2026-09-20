"""
Unit Tests for the MITRE mapping table
=======================================
Graph-sourced candidates: tactic neighbours feed the `tactic` column, not rows.
"""

import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent.parent / "app"
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

from RAG.GraphRAG.pipeline.mitre_table import build_mitre_table
from RAG.GraphRAG.retrieval.graph_retriever import GraphEdge, GraphNode, SubgraphResult
from RAG.GraphRAG.retrieval.hybrid_retriever import GraphRAGResult


def test_tactic_neighbour_is_a_column_not_a_row():
    rsd = GraphNode("t1", "Remote System Discovery", "Technique", "T1018")
    discovery = GraphNode("ta1", "Discovery", "Tactic", "TA0007")
    result = GraphRAGResult(
        vector_results=[],
        graph_results=[
            SubgraphResult(
                center_node=rsd,
                neighbors=[discovery],
                edges=[GraphEdge("IN_TACTIC", "Remote System Discovery", "Discovery")],
            )
        ],
    )

    rows = build_mitre_table(result, "คนร้ายค้นหาเครื่องอื่น (Remote System Discovery — T1018)")

    assert [(r.technique_id, r.tactic) for r in rows] == [("T1018", "Discovery")]
