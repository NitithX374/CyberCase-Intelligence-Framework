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
    if result.graph_results:
        sections.append("\n\n--- Graph Context (Structured Relationships) ---")

        for sg in result.graph_results[:max_graph]:
            text = sg.to_text()
            if text:
                sections.append(f"\n{text}")

    # ── Combine ───────────────────────────────────────────────────────────
    context = "\n".join(sections)

    if len(context) > max_context_length:
        context = (
            context[:max_context_length] + "\n\n... [context truncated for length]"
        )

    return context



def build_generation_prompt(
    context: str,
    original_query: str,
    english_query: str,
    respond_in_thai: bool = True,
    gap_note: str = "",
) -> str:
    """Build the final prompt for LLM generation.

    Args:
        context: The assembled context from build_context().
        original_query: The user's original query (may be Thai).
        english_query: The translated English query (for reference).
        respond_in_thai: Whether to respond in Thai.
        gap_note: What the evaluator judged to be missing. The model answers
            with whatever the context does support and closes by naming the
            gap, instead of declining to answer at all.

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

    if gap_note:
        # The evaluator judged something missing. Answer anyway, to the extent
        # the context allows, and say what would be needed to go further - a
        # partial mapping the reader can check beats a refusal they cannot use.
        if respond_in_thai:
            parts.append(
                "\nข้อมูลที่ยังขาด: " + gap_note + "\n"
                "ให้วิเคราะห์เท่าที่ข้อมูลที่มีรองรับ — ระบุเฉพาะเทคนิคที่ Context "
                "สนับสนุนจริง ห้ามเดาส่วนที่ไม่มีข้อมูล\n"
                "แล้วปิดท้ายด้วยหัวข้อ '## ข้อมูลที่ต้องการเพิ่มเติม' "
                "ระบุเป็นข้อ ๆ ว่าต้องการรายละเอียดใดเพิ่มจึงจะสรุปได้ครบถ้วน\n"
                "ห้ามปฏิเสธที่จะตอบ"
            )
        else:
            parts.append(
                "\nKnown gap: " + gap_note + "\n"
                "Analyse as far as the available context supports — name only techniques "
                "the context actually evidences, and do not guess at the rest.\n"
                "Then close with a section '## ADDITIONAL INFORMATION NEEDED' listing, "
                "as bullet points, what further detail would be required for a complete mapping.\n"
                "Do not decline to answer."
            )

    return "\n".join(parts)
