import os
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

# Add the current directory to sys.path so we can import RAG.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from RAG import GraphRAGAgent  # noqa: E402
from routers.rag import router as rag_router  # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    print("[RAG Service] Initializing RAG modules...")
    app.state.retrieval_contexts = {}

    try:
        from FlagEmbedding import BGEM3FlagModel
        from RAG.GraphRAG.config import (
            CORE_LLM_EFFECTIVE_MODEL,
            CORE_LLM_EFFECTIVE_PROVIDER,
            EMBED_MODEL,
            USE_FP16,
        )

        print(f"[RAG Service] Loading shared embedding model: {EMBED_MODEL}")
        embed_model = BGEM3FlagModel(EMBED_MODEL, use_fp16=USE_FP16)

        print(
            f"[RAG Service] LLM: {CORE_LLM_EFFECTIVE_PROVIDER}: "
            f"{CORE_LLM_EFFECTIVE_MODEL}"
        )
        app.state.rag_agent = GraphRAGAgent(embed_model=embed_model)
        print("[RAG Service] RAG modules initialized successfully.")

        # LegalRAG shares the embedding model rather than loading its own — the
        # production host runs both pipelines on CPU, where a second copy of
        # BGE-M3 is felt. It is initialised separately and allowed to fail on
        # its own: statute suggestions are an enhancement, and losing them must
        # not take the MITRE mapping down with them.
        try:
            from RAG.LegalRAG.pipeline import LegalRAG

            app.state.legal_rag = LegalRAG(embed_model=embed_model)
            app.state.legal_rag.warmup()
            print("[RAG Service] LegalRAG ready (thai_law_sections).")
        except Exception as legal_error:
            print(f"[RAG Service] LegalRAG unavailable: {legal_error}")
            app.state.legal_rag = None
    except Exception as e:
        print(f"[RAG Service] Error initializing RAG modules: {e}")
        import traceback

        traceback.print_exc()
        app.state.rag_agent = None
        app.state.legal_rag = None

    yield

    if app.state.rag_agent:
        app.state.rag_agent.close()
    print("[RAG Service] RAG modules shut down.")


app = FastAPI(title="Cybercase RAG Service", lifespan=lifespan)
app.include_router(rag_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
