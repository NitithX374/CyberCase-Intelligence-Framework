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

        # Legal provisions come from an external service now, so there is no
        # corpus, no model and nothing to warm up here — only a client. It is
        # built unconditionally and reports itself unconfigured when no
        # endpoint is set, because an unset provider is a valid deployment.
        from RAG.legal_reference import ThanoyClient

        app.state.legal_client = ThanoyClient()
        print(
            "[RAG Service] Legal reference: "
            + (f"{app.state.legal_client.url}" if app.state.legal_client.configured
               else "ไม่ได้ตั้งค่า THANOY_API_URL — ฟิลด์ legal_reference จะว่าง")
        )
    except Exception as e:
        print(f"[RAG Service] Error initializing RAG modules: {e}")
        import traceback

        traceback.print_exc()
        app.state.rag_agent = None
        app.state.legal_client = None

    yield

    if app.state.rag_agent:
        app.state.rag_agent.close()
    print("[RAG Service] RAG modules shut down.")


app = FastAPI(title="Cybercase RAG Service", lifespan=lifespan)
app.include_router(rag_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
