"""
Unit Tests for the MITRE mapping table
=======================================
Graph-sourced candidates: tactic neighbours feed the `tactic` column, not rows.
Row descriptions: the two channels store the same entity differently — Qdrant
keeps the embedding text (``"{label}: {name}. " + description``), Neo4j keeps
the raw description — and must still produce one identical row description.
Entity lookup: in production a graph neighbour carries no description and a
tactic arrives only with its technique's own subgraph, so the table asks each
kept entity's node for both.
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
    """Prefix aside, both channels normalise the same stored text identically.

    A graph *centre* carries its description; a neighbour does not — that
    production path is covered by the lookup tests below.
    """
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


def _neighbour_hit(name, label, attack_id, stix_id):
    """A neighbour as `GraphRetriever.expand` returns it: no description."""
    centre = GraphNode("sid-centre", "Remote Services", "Technique", "T1021", "")
    return SubgraphResult(
        center_node=centre,
        neighbors=[GraphNode(stix_id, name, label, attack_id)],
        edges=[],
    )


class _Lookup:
    """Stands in for `GraphRetriever.entity_details`, recording each call."""

    def __init__(self, nodes):
        self.nodes = nodes
        self.calls = []

    def __call__(self, stix_ids):
        self.calls.append(list(stix_ids))
        return {sid: self.nodes[sid] for sid in stix_ids if sid in self.nodes}


def test_graph_neighbour_row_takes_its_description_from_the_lookup():
    """The Valid Accounts row reached the UI empty: neighbours carry no text."""
    lookup = _Lookup({"sid-va": {"description": _POWERSHELL_DESC, "tactics": []}})
    result = GraphRAGResult(
        vector_results=[],
        graph_results=[_neighbour_hit("Valid Accounts", "Technique", "T1078", "sid-va")],
    )

    rows = build_mitre_table(result, "คนร้ายใช้ Valid Accounts (T1078)", entity_details=lookup)

    assert [(r.source, r.description) for r in rows] == [("graph", _POWERSHELL_DESC)]


def test_both_channels_agree_once_the_lookup_answers():
    """The production form of the parity check: a neighbour arrives empty."""
    lookup = _Lookup({"sid-1": {"description": _POWERSHELL_DESC, "tactics": []}})
    answer = "คนร้ายใช้ PowerShell (T1059.001)"

    from_vector = build_mitre_table(
        GraphRAGResult(
            vector_results=[
                _vector_hit("PowerShell", "Subtechnique", "T1059.001", _POWERSHELL_DESC)
            ],
            graph_results=[],
        ),
        answer,
        entity_details=lookup,
    )
    from_graph = build_mitre_table(
        GraphRAGResult(
            vector_results=[],
            graph_results=[_neighbour_hit("PowerShell", "Subtechnique", "T1059.001", "sid-1")],
        ),
        answer,
        entity_details=lookup,
    )

    assert from_vector[0].description == from_graph[0].description == _POWERSHELL_DESC


def test_every_tactic_of_a_technique_is_listed():
    """Without its own subgraph a technique had no tactic; with it, only one."""
    lookup = _Lookup({
        "sid-1": {
            "description": _POWERSHELL_DESC,
            "tactics": ["Initial Access", "Persistence", "Privilege Escalation", "Stealth"],
        }
    })
    result = GraphRAGResult(
        vector_results=[_vector_hit("Valid Accounts", "Technique", "T1078", _POWERSHELL_DESC)],
        graph_results=[],
    )

    rows = build_mitre_table(result, "คนร้ายใช้ Valid Accounts (T1078)", entity_details=lookup)

    assert rows[0].tactic == "Initial Access, Persistence, Privilege Escalation, Stealth"


def test_node_without_tactics_does_not_borrow_one_by_name():
    """The edge map is keyed by name; the node's own answer overrides it."""
    lookup = _Lookup({"sid-1": {"description": "A tool.", "tactics": []}})
    result = GraphRAGResult(
        vector_results=[_vector_hit("Discovery Tool", "Software", "S9999", "A tool.")],
        graph_results=[
            SubgraphResult(
                center_node=GraphNode("sid-t", "Other", "Technique", "T9999"),
                neighbors=[],
                edges=[GraphEdge("IN_TACTIC", "Discovery Tool", "Discovery")],
            )
        ],
    )

    rows = build_mitre_table(result, "คนร้ายใช้ Discovery Tool (S9999)", entity_details=lookup)

    assert rows[0].tactic is None


def test_lookup_is_asked_once_and_only_for_rows_that_are_shown():
    """An uncited neighbour is dropped, so Neo4j is never asked about it."""
    lookup = _Lookup({})
    result = GraphRAGResult(
        vector_results=[
            _vector_hit("PowerShell", "Subtechnique", "T1059.001", _POWERSHELL_DESC)
        ],
        graph_results=[_neighbour_hit("Unrelated Group", "Group", "G9999", "sid-dropped")],
    )

    build_mitre_table(result, "คนร้ายใช้ PowerShell (T1059.001)", entity_details=lookup)

    assert lookup.calls == [["sid-1"]]


def test_entity_the_lookup_misses_keeps_what_retrieval_carried():
    """A failed or empty lookup must leave the table as it was without one."""
    rsd = GraphNode("t1", "Remote System Discovery", "Technique", "T1018", _POWERSHELL_DESC)
    result = GraphRAGResult(
        vector_results=[],
        graph_results=[
            SubgraphResult(
                center_node=rsd,
                neighbors=[],
                edges=[GraphEdge("IN_TACTIC", "Remote System Discovery", "Discovery")],
            )
        ],
    )

    rows = build_mitre_table(
        result, "คนร้ายค้นหาเครื่องอื่น (T1018)", entity_details=_Lookup({})
    )

    assert [(r.tactic, r.description) for r in rows] == [("Discovery", _POWERSHELL_DESC)]
