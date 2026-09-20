"""
Context Builder
================
Assembles the final context from Vector + Graph retrieval results
into a structured prompt for the LLM.
"""

from ..config import FINAL_TOP_K
from ..retrieval.hybrid_retriever import GraphRAGResult


def build_context(
    result: GraphRAGResult,
    max_context_length: int = 10000,
    max_vector: int | None = None,
    max_graph: int = 3,
) -> str:
    """Build a structured context string from GraphRAG results.

    The context is formatted for optimal LLM consumption:
    1. Semantic matches with scores (most relevant first)
    2. Graph context showing structured relationships

    Args:
        result: The GraphRAGResult from hybrid retrieval.
        max_context_length: Maximum character length of context.
        max_vector: How many vector results to render (defaults to FINAL_TOP_K).
            Pass a larger value with quota retrieval so every decomposed
            sub-query's technique survives into the context.
        max_graph: How many subgraphs to render.

    Returns:
        Formatted context string.
    """
    sections = []

    # ── Section 1: Top Semantic Matches ───────────────────────────────────
    sections.append("=" * 60)
    sections.append("RETRIEVED CONTEXT FROM MITRE ATT&CK KNOWLEDGE BASE")
    sections.append("=" * 60)

    sections.append("\n--- Semantic Search Results ---")

    for i, vr in enumerate(result.vector_results[: (max_vector or FINAL_TOP_K)], 1):
        entity_type = vr.metadata.get("entity_type", "Unknown")
        node_label = vr.metadata.get("node_label", vr.metadata.get("edge_label", ""))
        name = vr.metadata.get("name", vr.metadata.get("source_name", ""))
        attack_id = vr.metadata.get("attack_id", "")

        header = f"[{i}] {entity_type}: {node_label}"
        if name:
            header += f" — {name}"
        if attack_id:
            header += f" ({attack_id})"
        header += f" | relevance: {vr.score:.3f}"

        sections.append(f"\n{header}")

        # Include document text (truncated)
        doc_text = vr.document[:600].replace("\n", " ").strip()
        sections.append(f"  {doc_text}")

    # ── Section 2: Graph Context ──────────────────────────────────────────
    # Whole subgraphs or nothing. Slicing the joined text at the budget cut
    # the first oversized subgraph mid-line and silently dropped every one
    # after it; skipping a subgraph that does not fit lets the smaller,
    # lower-priority ones behind it still land.
    context = "\n".join(sections)
    graph_blocks: list[str] = []
    retrieved_names = _retrieved_names(result)
    header = "\n\n--- Graph Context (Structured Relationships) ---"
    used = len(context) + 1 + len(header)

    for sg in result.graph_results[:max_graph]:
        text = sg.to_text(priority_names=retrieved_names)
        if not text:
            continue
        block = f"\n{text}"
        if used + 1 + len(block) > max_context_length:
            continue
        graph_blocks.append(block)
        used += 1 + len(block)

    if graph_blocks:
        context = "\n".join([context, header, *graph_blocks])

    # ── Safety net: the semantic section alone can exceed the budget ─────
    if len(context) > max_context_length:
        context = (
            context[:max_context_length] + "\n\n... [context truncated for length]"
        )

    return context


def _retrieved_names(result: GraphRAGResult) -> set[str]:
    """Entity names already present in the retrieval, used to order neighbour
    lists so a capped list keeps the neighbours that connect to the incident."""
    names: set[str] = set()
    for vr in result.vector_results:
        md = vr.metadata or {}
        names.update(filter(None, (md.get("name"), md.get("source_name"), md.get("target_name"))))
    for sg in result.graph_results:
        if sg.center_node and sg.center_node.name:
            names.add(sg.center_node.name)
    return names



def build_generation_prompt(
    context: str,
    original_query: str,
    english_query: str,
    respond_in_thai: bool = True,
) -> str:
    """Build the final prompt for LLM generation.

    Args:
        context: The assembled context from build_context().
        original_query: The user's original query (may be Thai).
        english_query: The translated English query (for reference).
        respond_in_thai: Whether to respond in Thai.

    Returns:
        The complete user prompt for the LLM.
    """
    parts = []

    parts.append(context)

    parts.append("\n" + "=" * 60)
    parts.append("USER QUESTION")
    parts.append("=" * 60)

    if original_query != english_query:
        parts.append(f"Original (Thai): {original_query}")
        parts.append(f"Translated (English): {english_query}")
    else:
        parts.append(f"Question: {original_query}")

    parts.append("\n" + "=" * 60)
    parts.append("INSTRUCTIONS")
    parts.append("=" * 60)

    if respond_in_thai:
        parts.append(
            "อธิบายเหตุการณ์ข้างต้นโดยอ้างอิงจากข้อมูล Context ที่ให้มาเท่านั้น\n"
            "ใช้ภาษาที่เข้าใจง่ายสำหรับผู้ที่ไม่มีพื้นฐานเทคนิค\n"
            "คงศัพท์เทคนิคและ ATT&CK ID ไว้เป็นภาษาอังกฤษ"
        )
    else:
        parts.append(
            "Using ONLY the provided context, explain the incident in plain language "
            "for prosecutors and law enforcement officers who have no cybersecurity background.\n"
            "Follow the four-section format from your instructions exactly.\n"
            "Cite ATT&CK IDs for every technique mentioned."
        )

    return "\n".join(parts)
