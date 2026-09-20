"""
Neo4j Graph Retriever
======================
Expands subgraphs from Neo4j given STIX IDs retrieved from vector search.
Implements the "Graph Expansion" step of the GraphRAG architecture.

For a given entity (e.g., Technique T1566), fetches:
  - Groups that USE it
  - Software that USES it
  - Campaigns that USE it
  - Mitigations that MITIGATE it
  - Subtechniques (SUBTECHNIQUE_OF)
  - Tactics it belongs to (IN_TACTIC)
  - DataComponents that DETECT it
"""

from dataclasses import dataclass, field
from typing import Any, Optional, cast

from neo4j import GraphDatabase, Query

from ..config import GRAPH_CONTEXT_MAX_NAMES, NEO4J_PASSWORD, NEO4J_URI, NEO4J_USER


@dataclass
class GraphNode:
    """A node from the graph expansion."""

    stix_id: str
    name: str
    label: str
    attack_id: str = ""
    description: str = ""


@dataclass
class GraphEdge:
    """An edge from the graph expansion."""

    edge_label: str
    source_name: str
    target_name: str
    description: str = ""


@dataclass
class SubgraphResult:
    """Result of a graph expansion query."""

    center_node: Optional[GraphNode] = None
    neighbors: list[GraphNode] = field(default_factory=list)
    edges: list[GraphEdge] = field(default_factory=list)

    def to_text(
        self,
        max_names: int = GRAPH_CONTEXT_MAX_NAMES,
        priority_names: Optional[set[str]] = None,
    ) -> str:
        """Format the subgraph as readable text for LLM context.

        Names only, capped per relation. Edge descriptions (the per-procedure
        "X has used Y to …" text) are deliberately not rendered: they were ~90%
        of the output, a single well-known group ran to 16K characters, and the
        first subgraph alone used up the whole context budget. The procedure
        text the incident actually matches already reaches the LLM as
        relationship documents in the semantic section.

        Args:
            max_names: Neighbour names listed per relation before "(+N more)".
                A technique can have hundreds of USES neighbours; the structure
                worth keeping (tactic, parent, mitigations) is short.
            priority_names: Names that are also in the retrieved context. They
                are listed first, so the cap drops unrelated neighbours rather
                than an arbitrary slice of Neo4j's row order.
        """
        if not self.center_node:
            return ""

        center = self.center_node.name
        priority = priority_names or set()
        lines = [f"## {self.center_node.label}: {center} ({self.center_node.attack_id})"]

        # Group by relation AND direction: "FIN7 USES X" and "Y USES FIN7" read
        # differently, and labelling both "Used by" inverted what a group does.
        groups: dict[tuple[str, bool], list[str]] = {}
        for e in self.edges:
            outgoing = e.source_name == center
            name = e.target_name if outgoing else e.source_name
            names = groups.setdefault((e.edge_label, outgoing), [])
            if name and name not in names:
                names.append(name)

        for (edge_label, outgoing), names in groups.items():
            out_display, in_display = _EDGE_DISPLAY.get(edge_label, (edge_label, edge_label))
            display = out_display if outgoing else in_display
            ordered = [n for n in names if n in priority] + [n for n in names if n not in priority]
            shown = ", ".join(ordered[:max_names])
            hidden = len(ordered) - max_names
            if hidden > 0:
                shown += f" (+{hidden} more)"
            lines.append(f"  ├── {display}: {shown}")

        return "\n".join(lines)


# Edge label → (display when the centre is the source, when it is the target).
_EDGE_DISPLAY = {
    "USES": ("Uses", "Used by"),
    "MITIGATES": ("Mitigates", "Mitigated by"),
    "IN_TACTIC": ("Belongs to tactic", "Techniques in tactic"),
    "SUBTECHNIQUE_OF": ("Parent technique", "Subtechniques"),
    "DETECTS": ("Detects", "Detected by"),
    "HAS_COMPONENT": ("Has component", "Component of"),
    "ATTRIBUTED_TO": ("Attributed to", "Attributed from"),
}


class GraphRetriever:
    """Expands subgraphs from Neo4j for GraphRAG context enrichment."""

    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        print(f"[GRAPH] Connected to {NEO4J_URI}")

    def close(self):
        self.driver.close()

    def expand(self, stix_ids: list[str]) -> list[SubgraphResult]:
        """Expand subgraphs for a list of STIX IDs.

        For each ID, fetches the center node and its immediate neighborhood.
        Delegates to the batched implementation: instead of 3 Cypher queries
        per seed in its own session (3N round-trips to a cloud DB — the
        dominant retrieval cost), it issues 3 UNWIND queries total.
        """
        return self.expand_batch(stix_ids)

    def expand_batch(self, stix_ids: list[str]) -> list[SubgraphResult]:
        """Batched graph expansion — 3 Cypher queries for the whole seed list.

        Behaviour-equivalent to looping ``_expand_single`` (same center nodes,
        same neighbour/edge sets, subgraphs in input order, only ids with a
        matching center returned), but collapses 3N sequential Neo4j
        round-trips into 3. Neo4j's row order within a seed is not guaranteed
        identical to the per-seed query, so neighbour LIST order within a
        subgraph may differ; the retrieved-id SET is unchanged.
        """
        ordered = list(dict.fromkeys(stix_ids))  # dedupe, preserve order
        if not ordered:
            return []

        with self.driver.session() as session:
            # ── 1. Center nodes ───────────────────────────────────────────
            by_sid: dict[str, SubgraphResult] = {}
            centers = session.run(
                Query("""
                UNWIND $ids AS sid
                MATCH (n {stix_id: sid})
                RETURN sid AS sid, n AS n, labels(n) AS labels
                """),
                ids=ordered,
            )
            for rec in centers:
                node_data = dict(rec["n"])
                labels = rec["labels"]
                sr = SubgraphResult()
                sr.center_node = GraphNode(
                    stix_id=node_data.get("stix_id", ""),
                    name=node_data.get("name", ""),
                    label=labels[0] if labels else "Unknown",
                    attack_id=node_data.get("attack_id", ""),
                    description=(node_data.get("description") or "")[:300],
                )
                by_sid.setdefault(rec["sid"], sr)

            hit_ids = list(by_sid.keys())

            # ── 2. Outgoing relationships ─────────────────────────────────
            outgoing = session.run(
                Query("""
                UNWIND $ids AS sid
                MATCH (n {stix_id: sid})-[r]->(m)
                RETURN sid AS sid, type(r) AS rel_type, r.description AS rel_desc,
                       m.stix_id AS target_id, m.name AS target_name,
                       m.attack_id AS target_attack_id, labels(m) AS target_labels
                """),
                ids=hit_ids,
            )
            for rec in outgoing:
                sr = by_sid.get(rec["sid"])
                if not sr:
                    continue
                target_label = (
                    rec["target_labels"][0] if rec["target_labels"] else "Unknown"
                )
                sr.neighbors.append(GraphNode(
                    stix_id=rec["target_id"] or "",
                    name=rec["target_name"] or "",
                    label=target_label,
                    attack_id=rec["target_attack_id"] or "",
                ))
                sr.edges.append(GraphEdge(
                    edge_label=rec["rel_type"] or "",
                    source_name=sr.center_node.name,
                    target_name=rec["target_name"] or "",
                    description=rec["rel_desc"] or "",
                ))

            # ── 3. Incoming relationships ─────────────────────────────────
            incoming = session.run(
                Query("""
                UNWIND $ids AS sid
                MATCH (m)-[r]->(n {stix_id: sid})
                RETURN sid AS sid, type(r) AS rel_type, r.description AS rel_desc,
                       m.stix_id AS source_id, m.name AS source_name,
                       m.attack_id AS source_attack_id, labels(m) AS source_labels
                """),
                ids=hit_ids,
            )
            for rec in incoming:
                sr = by_sid.get(rec["sid"])
                if not sr:
                    continue
                source_label = (
                    rec["source_labels"][0] if rec["source_labels"] else "Unknown"
                )
                sr.neighbors.append(GraphNode(
                    stix_id=rec["source_id"] or "",
                    name=rec["source_name"] or "",
                    label=source_label,
                    attack_id=rec["source_attack_id"] or "",
                ))
                sr.edges.append(GraphEdge(
                    edge_label=rec["rel_type"] or "",
                    source_name=rec["source_name"] or "",
                    target_name=sr.center_node.name,
                    description=rec["rel_desc"] or "",
                ))

        # Preserve input order, only ids that matched a center node.
        return [by_sid[sid] for sid in ordered if sid in by_sid]

    def _expand_single(self, stix_id: str) -> SubgraphResult:
        """Expand a single node's subgraph."""
        result = SubgraphResult()

        with self.driver.session() as session:
            # Get center node
            center = session.run(
                Query("""
                MATCH (n {stix_id: $stix_id})
                RETURN n, labels(n) AS labels
                """),
                stix_id=stix_id,
            ).single()

            if not center:
                return result

            node_data = dict(center["n"])
            labels = center["labels"]

            result.center_node = GraphNode(
                stix_id=node_data.get("stix_id", ""),
                name=node_data.get("name", ""),
                label=labels[0] if labels else "Unknown",
                attack_id=node_data.get("attack_id", ""),
                description=node_data.get("description", "")[:300],
            )

            # Get all outgoing relationships
            outgoing = session.run(
                Query("""
                MATCH (n {stix_id: $stix_id})-[r]->(m)
                RETURN type(r) AS rel_type, r.description AS rel_desc,
                       m.stix_id AS target_id, m.name AS target_name,
                       m.attack_id AS target_attack_id, labels(m) AS target_labels
                """),
                stix_id=stix_id,
            )

            for record in outgoing:
                target_label = (
                    record["target_labels"][0] if record["target_labels"] else "Unknown"
                )

                result.neighbors.append(
                    GraphNode(
                        stix_id=record["target_id"] or "",
                        name=record["target_name"] or "",
                        label=target_label,
                        attack_id=record["target_attack_id"] or "",
                    )
                )

                result.edges.append(
                    GraphEdge(
                        edge_label=record["rel_type"] or "",
                        source_name=result.center_node.name,
                        target_name=record["target_name"] or "",
                        description=record["rel_desc"] or "",
                    )
                )

            # Get all incoming relationships
            incoming = session.run(
                Query("""
                MATCH (m)-[r]->(n {stix_id: $stix_id})
                RETURN type(r) AS rel_type, r.description AS rel_desc,
                       m.stix_id AS source_id, m.name AS source_name,
                       m.attack_id AS source_attack_id, labels(m) AS source_labels
                """),
                stix_id=stix_id,
            )

            for record in incoming:
                source_label = (
                    record["source_labels"][0] if record["source_labels"] else "Unknown"
                )

                result.neighbors.append(
                    GraphNode(
                        stix_id=record["source_id"] or "",
                        name=record["source_name"] or "",
                        label=source_label,
                        attack_id=record["source_attack_id"] or "",
                    )
                )

                result.edges.append(
                    GraphEdge(
                        edge_label=record["rel_type"] or "",
                        source_name=record["source_name"] or "",
                        target_name=result.center_node.name,
                        description=record["rel_desc"] or "",
                    )
                )

        return result

    def query_cypher(self, cypher: str, params: Optional[dict] = None) -> list[dict]:
        """Execute an arbitrary Cypher query and return results as dicts."""
        with self.driver.session() as session:
            result = session.run(Query(cast(Any, cypher)), parameters=params or {})
            return [dict(record) for record in result]

    def get_multi_hop_path(
        self, start_name: str, end_name: str, max_hops: int = 4
    ) -> str:
        """Find paths between two named entities.

        Useful for questions like "What is the relationship between
        Lazarus Group and WannaCry?"
        """
        with self.driver.session() as session:
            query = f"""
                MATCH path = shortestPath(
                    (a {{name: $start_name}})-[*1..{max_hops}]-(b {{name: $end_name}})
                )
                RETURN [n IN nodes(path) | n.name] AS node_names,
                       [r IN relationships(path) | type(r)] AS rel_types
                LIMIT 3
                """
            result = session.run(
                Query(cast(Any, query)),
                start_name=start_name,
                end_name=end_name,
            )

            paths = []
            for record in result:
                names = record["node_names"]
                rels = record["rel_types"]
                # Format: "A -[USES]-> B -[SUBTECHNIQUE_OF]-> C"
                parts = []
                for i, name in enumerate(names):
                    parts.append(name)
                    if i < len(rels):
                        parts.append(f"-[{rels[i]}]->")
                paths.append(" ".join(parts))

            if paths:
                return "\n".join(paths)
            return f"No path found between '{start_name}' and '{end_name}'"
