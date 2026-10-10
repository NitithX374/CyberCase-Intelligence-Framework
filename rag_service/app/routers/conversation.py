"""The case conversation over HTTP — mounted only when STANDALONE_CHAT is on.

    POST   /conversations                  the case file → analysis, a new conversation
    GET    /conversations/{id}             the conversation as it stands
    POST   /conversations/{id}/messages    a question, or added facts
    DELETE /conversations/{id}             forget it now
    GET    /chat                           the page that talks to the four above

``POST /query`` and the backend that calls it know nothing of these.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from anyio import to_thread
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from RAG.GraphRAG.pipeline.conversation import (
    ANALYSIS,
    Analysis,
    CaseChat,
    Conversation,
    ConversationBusy,
    ConversationStore,
    Turn,
)
from schemas.conversation import (
    AnalysisView,
    ConversationView,
    MessageRequest,
    MessageResponse,
    OpenConversationRequest,
    TurnView,
)

from routers.rag import _get_query_limiter, _legal_reference, _run_pipeline

logger = logging.getLogger(__name__)

router = APIRouter(tags=["conversation"])

_PAGE = Path(__file__).with_name("conversation_page.html")


def _store(req: Request) -> ConversationStore:
    store = getattr(req.app.state, "conversations", None)
    if store is None:
        store = ConversationStore()
        req.app.state.conversations = store
    return store


def _chat(req: Request) -> CaseChat:
    """The chat for this process's agent, built on first use."""
    chat = getattr(req.app.state, "case_chat", None)
    if chat is not None:
        return chat
    rag_agent = getattr(req.app.state, "rag_agent", None)
    if not rag_agent:
        raise HTTPException(status_code=503, detail="RAG Agent not available")
    if getattr(rag_agent, "reasoning_llm", None) is None:
        raise HTTPException(status_code=503, detail="No language model is configured")
    chat = CaseChat.for_agent(rag_agent, _analyse_with(rag_agent))
    req.app.state.case_chat = chat
    return chat


def _analyse_with(rag_agent: Any):
    """A case analysed exactly as POST /query analyses it: same graph, same
    re-read, same table."""

    def analyse(case_text: str) -> Analysis:
        agent_response, mitre_table = _run_pipeline(rag_agent, case_text)
        return Analysis(
            case_text=case_text,
            answer=agent_response.answer,
            context=agent_response.context,
            mitre_table=list(mitre_table),
        )

    return analyse


def _turn_view(turn: Turn) -> TurnView:
    return TurnView(
        role=turn.role,
        kind=turn.kind,
        text=turn.text,
        created_at=turn.created_at,
        seconds=round(turn.seconds, 1),
        lookup_queries=list(turn.lookup_queries),
        lookup_ids=list(turn.lookup_ids),
        rows_added=list(turn.rows_added),
        rows_removed=list(turn.rows_removed),
    )


def _analysis_view(analysis: Analysis) -> AnalysisView:
    return AnalysisView(
        case_text=analysis.case_text,
        answer=analysis.answer,
        mitre_table=list(analysis.mitre_table),
        legal_reference=analysis.legal_reference,
    )


def _conversation_view(conversation: Conversation) -> ConversationView:
    return ConversationView(
        conversation_id=conversation.id,
        created_at=conversation.created_at,
        analysis=_analysis_view(conversation.analysis),
        turns=[_turn_view(turn) for turn in conversation.turns],
    )


def _known(req: Request, conversation_id: str) -> Conversation:
    conversation = _store(req).get(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.post("/conversations", response_model=ConversationView)
async def open_conversation(body: OpenConversationRequest, req: Request):
    chat = _chat(req)
    try:
        # The whole pipeline, tens of seconds of blocking work: on a worker
        # thread, under the limiter POST /query shares.
        conversation = await to_thread.run_sync(
            chat.open, body.case_file, limiter=_get_query_limiter(req)
        )
    except Exception as exc:
        logger.exception("POST /conversations failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
    conversation.analysis.legal_reference = await _legal_reference(req, body.case_file)
    _store(req).add(conversation)
    return _conversation_view(conversation)


@router.get("/conversations/{conversation_id}", response_model=ConversationView)
async def get_conversation(conversation_id: str, req: Request):
    return _conversation_view(_known(req, conversation_id))


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def post_message(conversation_id: str, body: MessageRequest, req: Request):
    chat = _chat(req)
    conversation = _known(req, conversation_id)
    try:
        reply = await to_thread.run_sync(
            chat.say, conversation, body.text, body.kind, limiter=_get_query_limiter(req)
        )
    except ConversationBusy:
        raise HTTPException(
            status_code=409, detail="The conversation is still answering the previous message"
        )
    except Exception as exc:
        logger.exception("POST /conversations/%s/messages failed: %s", conversation_id, exc)
        raise HTTPException(status_code=500, detail=str(exc))

    if reply.kind != ANALYSIS:
        return MessageResponse(conversation_id=conversation.id, reply=_turn_view(reply))
    # The case was analysed again, so its provisions are looked up again too.
    analysis = conversation.analysis
    analysis.legal_reference = await _legal_reference(req, analysis.case_text)
    return MessageResponse(
        conversation_id=conversation.id, reply=_turn_view(reply), analysis=_analysis_view(analysis)
    )


@router.delete("/conversations/{conversation_id}", status_code=204)
async def delete_conversation(conversation_id: str, req: Request):
    if not _store(req).delete(conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    return Response(status_code=204)


@router.get("/chat", response_class=HTMLResponse, include_in_schema=False)
async def chat_page():
    return HTMLResponse(_PAGE.read_text(encoding="utf-8"))
