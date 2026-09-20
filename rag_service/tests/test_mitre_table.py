"""
Unit Tests for the MITRE mapping table
=======================================
Graph-sourced candidates: tactic neighbours feed the `tactic` column, not rows.
Row descriptions: the two channels store the same entity differently — Qdrant
keeps the embedding text (``"{label}: {name}. " + description``), Neo4j keeps
the raw description — and must still produce one identical row description.
"""

import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent.parent / "app"
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

from RAG.GraphRAG.pipeline.mitre_table import (
    _MAX_DESCRIPTION_CHARS,
    _TRUNCATION_MARKER,
    build_mitre_table,
)
from RAG.GraphRAG.retrieval.graph_retriever import GraphEdge, GraphNode, SubgraphResult
from RAG.GraphRAG.retrieval.hybrid_retriever import GraphRAGResult
from RAG.GraphRAG.retrieval.vector_retriever import VectorResult

_POWERSHELL_DESC = (
    "Adversaries may abuse PowerShell commands and scripts for execution. "
    "PowerShell is a powerful interactive command-line interface included in "
    "the Windows operating system."
)


def _vector_hit(name, label, attack_id, description, score=0.9, stix_id="sid-1"):
    """A Qdrant hit as `vector_loader` stores it: description behind a header."""
    return VectorResult(
        document=f"{label}: {name}. {description}",
        metadata={
            "entity_type": "Node",
            "node_label": label,
            "name": name,
            "attack_id": attack_id,
        },
        score=score,
        stix_id=stix_id,
    )


def _graph_hit(name, label, attack_id, description, stix_id="sid-1"):
    """A Neo4j node as `graph_loader` stores it: the raw description."""
    return SubgraphResult(
        center_node=GraphNode(stix_id, name, label, attack_id, description),
        neighbors=[],
        edges=[],
    )


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


def test_both_channels_describe_an_entity_identically():
    """A row must not read differently depending on which channel surfaced it."""
    answer = "คนร้ายใช้ PowerShell (T1059.001)"
    args = ("PowerShell", "Subtechnique", "T1059.001", _POWERSHELL_DESC)

    from_vector = build_mitre_table(
        GraphRAGResult(vector_results=[_vector_hit(*args)], graph_results=[]), answer
    )
    from_graph = build_mitre_table(
        GraphRAGResult(vector_results=[], graph_results=[_graph_hit(*args)]), answer
    )

    assert [r.description for r in from_vector] == [r.description for r in from_graph]
    assert from_vector[0].description == _POWERSHELL_DESC


def test_vector_description_does_not_open_with_the_entity_label():
    """The frontend's short summary is the first sentence — it must carry meaning.

    Before the fix that sentence was "Subtechnique: PowerShell." — a label.
    """
    result = GraphRAGResult(
        vector_results=[
            _vector_hit("PowerShell", "Subtechnique", "T1059.001", _POWERSHELL_DESC)
        ],
        graph_results=[],
    )

    rows = build_mitre_table(result, "คนร้ายใช้ PowerShell (T1059.001)")

    assert not rows[0].description.startswith("Subtechnique:")
    first_sentence = rows[0].description.split(". ")[0]
    assert first_sentence == "Adversaries may abuse PowerShell commands and scripts for execution"


def test_prefix_strip_spares_a_description_that_begins_with_a_colon():
    """Only the header ingestion added is dropped, never the description's own text."""
    description = "Note: adversaries may abuse scheduled tasks for persistence."
    result = GraphRAGResult(
        vector_results=[_vector_hit("Scheduled Task", "Technique", "T1053.005", description)],
        graph_results=[],
    )

    rows = build_mitre_table(result, "คนร้ายตั้ง Scheduled Task (T1053.005)")

    assert rows[0].description == description


def test_document_without_the_header_is_left_untouched():
    """A document stored under a different format must not lose its opening words."""
    hit = _vector_hit("PowerShell", "Subtechnique", "T1059.001", _POWERSHELL_DESC)
    hit.document = _POWERSHELL_DESC  # no "{label}: {name}. " header at all
    result = GraphRAGResult(vector_results=[hit], graph_results=[])

    rows = build_mitre_table(result, "คนร้ายใช้ PowerShell (T1059.001)")

    assert rows[0].description == _POWERSHELL_DESC


def test_citation_markers_and_links_are_stripped():
    description = (
        "Adversaries may abuse PowerShell.(Citation: TechNet PowerShell) It ships "
        "with [Windows](https://microsoft.com) by default."
    )
    result = GraphRAGResult(
        vector_results=[_vector_hit("PowerShell", "Subtechnique", "T1059.001", description)],
        graph_results=[],
    )

    rows = build_mitre_table(result, "คนร้ายใช้ PowerShell (T1059.001)")

    assert rows[0].description == (
        "Adversaries may abuse PowerShell. It ships with Windows by default."
    )


def test_long_description_is_marked_and_cut_on_a_word_boundary():
    """A consumer must be able to tell a shortened description from a complete one."""
    description = "Adversaries abuse trustworthy binaries repeatedly. " * 60
    result = GraphRAGResult(
        vector_results=[_vector_hit("PowerShell", "Subtechnique", "T1059.001", description)],
        graph_results=[],
    )

    rows = build_mitre_table(result, "คนร้ายใช้ PowerShell (T1059.001)")
    got = rows[0].description

    assert got.endswith(_TRUNCATION_MARKER)
    assert len(got) <= _MAX_DESCRIPTION_CHARS + len(_TRUNCATION_MARKER)
    assert description.startswith(got[: -len(_TRUNCATION_MARKER)])  # no half word


def test_short_description_carries_no_truncation_marker():
    result = GraphRAGResult(
        vector_results=[
            _vector_hit("PowerShell", "Subtechnique", "T1059.001", _POWERSHELL_DESC)
        ],
        graph_results=[],
    )

    rows = build_mitre_table(result, "คนร้ายใช้ PowerShell (T1059.001)")

    assert not rows[0].description.endswith(_TRUNCATION_MARKER)
