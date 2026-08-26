"""
LegalRAG configuration
======================
Read from the environment here rather than imported from GraphRAG's config, on
purpose. LegalRAG must stay runnable, testable and breakable on its own: the
moment it imports `..GraphRAG.config` it also pulls in that package's __init__,
which loads the embedding and reranker models, and a statute parser that cannot
run without a GPU-sized import is not a statute parser anyone will run.

The values that must match GraphRAG (embedding model and dimension) are matched
deliberately, because both write vectors to the same Qdrant instance and a
mismatch would only surface as bad search results.
"""

from __future__ import annotations

import os

# Must equal GraphRAG's EMBED_MODEL/EMBED_DIM — same Qdrant, same vector space.
EMBED_MODEL = "BAAI/bge-m3"
EMBED_DIM = 1024

QDRANT_URL = os.getenv("QDRANT_URL", "")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# Statutes live in their own collection. Mixing them into the MITRE collections
# would make a case narrative match "มาตรา" where a technique belongs, and both
# retrievers get worse.
QDRANT_COLLECTION_LEGAL = os.getenv("QDRANT_COLLECTION_LEGAL", "thai_law_sections")

# Collections this module must never create, write to, or delete. The MITRE data
# is ingested by a separate pipeline and re-ingesting it is expensive; deleting
# it costs a full STIX rebuild. Guarded by name rather than by convention.
PROTECTED_COLLECTIONS = ("mitre_entities", "mitre_relationships")
PROTECTED_PREFIXES = ("mitre",)


def assert_writable(collection: str) -> None:
    """Refuse to touch anything that is not the legal collection.

    Called before every create, upsert and delete. This is deliberately stricter
    than "don't delete MITRE": the collection name is checked against an
    allow-list of one, so a typo in QDRANT_COLLECTION_LEGAL cannot land statute
    vectors in a collection that something else owns.
    """
    name = collection.strip()
    lowered = name.lower()
    if lowered in PROTECTED_COLLECTIONS or lowered.startswith(PROTECTED_PREFIXES):
        raise SystemExit(
            f"[LEGAL] ปฏิเสธ: '{collection}' เป็น collection ของ MITRE — LegalRAG ห้ามแตะ"
        )
    if name != QDRANT_COLLECTION_LEGAL:
        raise SystemExit(
            f"[LEGAL] ปฏิเสธ: '{collection}' ไม่ใช่ collection ของ LegalRAG "
            f"(ต้องเป็น '{QDRANT_COLLECTION_LEGAL}')"
        )


# ── Legal LLM ─────────────────────────────────────────────────────────────
# The same provider selection GraphRAG uses, read independently. The service
# injects its own chat model; this exists so the module can be exercised from a
# CLI without importing GraphRAG and dragging in the embedding stack.
CORE_LLM_PROVIDER = os.getenv("CORE_LLM_PROVIDER", "openrouter").strip().lower()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENROUTER_CYBERCASE = os.getenv("OPENROUTER_CYBERCASE", "")
CORE_LLM_ANTHROPIC_MODEL = os.getenv("CORE_LLM_ANTHROPIC_MODEL", "claude-haiku-4-5")
CORE_LLM_OPENROUTER_MODEL = os.getenv("CORE_LLM_OPENROUTER_MODEL", "openai/gpt-5.6-luna")
CORE_LLM_OPENROUTER_BASE_URL = os.getenv(
    "CORE_LLM_OPENROUTER_BASE_URL", "https://openrouter.ai/api"
).rstrip("/")


def create_legal_chat_model(temperature: float = 0.0, max_tokens: int = 2048):
    """Fallback chat model for CLI use. The service passes its own instead."""
    from langchain_anthropic import ChatAnthropic

    openrouter = CORE_LLM_PROVIDER == "openrouter"
    api_key = OPENROUTER_CYBERCASE if openrouter else ANTHROPIC_API_KEY
    if not api_key:
        raise RuntimeError(
            f"CORE_LLM_PROVIDER={CORE_LLM_PROVIDER} requires "
            + ("OPENROUTER_CYBERCASE" if openrouter else "ANTHROPIC_API_KEY")
        )
    kwargs: dict = {
        "model_name": CORE_LLM_OPENROUTER_MODEL if openrouter else CORE_LLM_ANTHROPIC_MODEL,
        "api_key": api_key,
        "temperature": temperature,
        "max_tokens_to_sample": max(max_tokens, 4096) if openrouter else max_tokens,
    }
    if openrouter:
        kwargs["base_url"] = CORE_LLM_OPENROUTER_BASE_URL
        kwargs["default_headers"] = {"Authorization": f"Bearer {api_key}"}
    return ChatAnthropic(**kwargs)
