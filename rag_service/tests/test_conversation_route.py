"""The case conversation over HTTP."""

from __future__ import annotations

from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient
from RAG.GraphRAG.pipeline.conversation import (
    ANALYSIS,
    ANSWER,
    ASSISTANT,
    CASE,
    FACTS,
    QUESTION,
    USER,
    Analysis,
    Conversation,
    ConversationBusy,
    Turn,
)
from RAG.GraphRAG.pipeline.mitre_table import EvidenceSpan, MitreTableRow
from routers import conversation as conversation_router
from routers import rag as rag_router

CASE_FILE = "คนร้ายส่งคำสั่งฐานข้อมูลแทรกเข้าทางหน้าเว็บ"
ROW = MitreTableRow(
    technique_id="T1190", name="Exploit Public-Facing Application", entity_type="Technique",
    evidence=[EvidenceSpan(text=CASE_FILE, start=0, end=len(CASE_FILE), basis="reread")],
)


class FakeChat:
    """The turns, without the models behind them."""

    def __init__(self) -> None:
        self.said: list[tuple[str, str]] = []
        self.busy = False

    def open(self, case_file: str) -> Conversation:
        analysis = Analysis(case_text=case_file, answer="## สรุปเหตุการณ์", context="ctx",
                            mitre_table=[ROW])
        conversation = Conversation(case_file=case_file, analysis=analysis)
        conversation.turns += [Turn(USER, CASE, case_file),
                               Turn(ASSISTANT, ANALYSIS, analysis.answer, seconds=61.26)]
        return conversation

    def say(self, conversation: Conversation, text: str, kind: str = QUESTION) -> Turn:
        if self.busy:
            raise ConversationBusy(conversation.id)
        self.said.append((text, kind))
        if kind == FACTS:
            conversation.analysis = Analysis(case_text=f"{conversation.case_file}\n{text}",
                                             answer="## วิเคราะห์ใหม่", context="ctx", mitre_table=[])
            reply = Turn(ASSISTANT, ANALYSIS, "## วิเคราะห์ใหม่", rows_removed=["T1190"])
            conversation.turns += [Turn(USER, FACTS, text), reply]
            return reply
        reply = Turn(ASSISTANT, ANSWER, "คำตอบ", lookup_queries=["q"], lookup_ids=["T1105"])
        conversation.turns += [Turn(USER, QUESTION, text), reply]
        return reply


def client_with(chat: FakeChat | None = None) -> tuple[TestClient, FakeChat]:
    app = FastAPI()
    chat = chat or FakeChat()
    app.state.rag_agent = SimpleNamespace(reasoning_llm=object())
    app.state.case_chat = chat
    app.state.legal_client = None  # the legal lookup then reports itself degraded
    app.include_router(rag_router.router)
    app.include_router(conversation_router.router)
    return TestClient(app), chat


def test_opening_returns_the_analysis_the_table_and_both_turns() -> None:
    client, _ = client_with()

    response = client.post("/conversations", json={"case_file": CASE_FILE})

    assert response.status_code == 200
    body = response.json()
    assert body["analysis"]["case_text"] == CASE_FILE
    assert body["analysis"]["answer"] == "## สรุปเหตุการณ์"
    assert body["analysis"]["mitre_table"][0]["technique_id"] == "T1190"
    assert body["analysis"]["mitre_table"][0]["evidence"] == [
        {"text": CASE_FILE, "start": 0, "end": len(CASE_FILE), "basis": "reread"}
    ]
    # No legal service configured: the field says so instead of failing the request.
    assert body["analysis"]["legal_reference"]["provisions"] == []
    assert body["analysis"]["legal_reference"]["degraded"]
    assert [(t["role"], t["kind"]) for t in body["turns"]] == [("user", "case"), ("assistant", "analysis")]
    assert body["turns"][1]["seconds"] == 61.3

    again = client.get(f"/conversations/{body['conversation_id']}")
    assert again.status_code == 200 and again.json() == body


def test_a_question_is_answered_without_touching_the_analysis() -> None:
    client, chat = client_with()
    conversation_id = client.post("/conversations", json={"case_file": CASE_FILE}).json()["conversation_id"]

    response = client.post(f"/conversations/{conversation_id}/messages", json={"text": "T1105 คืออะไร"})

    assert response.status_code == 200
    body = response.json()
    assert chat.said == [("T1105 คืออะไร", "question")]
    assert body["analysis"] is None
    assert body["reply"]["kind"] == "answer" and body["reply"]["text"] == "คำตอบ"
    assert body["reply"]["lookup_queries"] == ["q"] and body["reply"]["lookup_ids"] == ["T1105"]
    stored = client.get(f"/conversations/{conversation_id}").json()
    assert [t["kind"] for t in stored["turns"]] == ["case", "analysis", "question", "answer"]
    assert stored["analysis"]["answer"] == "## สรุปเหตุการณ์"


def test_added_facts_return_the_new_analysis() -> None:
    client, chat = client_with()
    conversation_id = client.post("/conversations", json={"case_file": CASE_FILE}).json()["conversation_id"]

    response = client.post(
        f"/conversations/{conversation_id}/messages", json={"text": "ไฟล์ถูกเข้ารหัส", "kind": "facts"}
    )

    assert response.status_code == 200
    body = response.json()
    assert chat.said == [("ไฟล์ถูกเข้ารหัส", "facts")]
    assert body["reply"]["kind"] == "analysis" and body["reply"]["rows_removed"] == ["T1190"]
    assert body["analysis"]["answer"] == "## วิเคราะห์ใหม่"
    assert body["analysis"]["case_text"] == f"{CASE_FILE}\nไฟล์ถูกเข้ารหัส"
    assert body["analysis"]["mitre_table"] == []
    assert body["analysis"]["legal_reference"]["degraded"]


def test_requests_that_are_refused() -> None:
    client, chat = client_with()
    conversation_id = client.post("/conversations", json={"case_file": CASE_FILE}).json()["conversation_id"]
    messages = f"/conversations/{conversation_id}/messages"

    assert client.post("/conversations", json={"case_file": "   "}).status_code == 422
    assert client.post("/conversations", json={"case_file": CASE_FILE, "model": "x"}).status_code == 422
    assert client.post(messages, json={"text": ""}).status_code == 422
    assert client.post(messages, json={"text": "x", "kind": "reanalyse"}).status_code == 422
    assert client.post("/conversations/unknown/messages", json={"text": "x"}).status_code == 404
    assert client.get("/conversations/unknown").status_code == 404

    chat.busy = True
    assert client.post(messages, json={"text": "x"}).status_code == 409


def test_a_deleted_conversation_is_gone() -> None:
    client, _ = client_with()
    conversation_id = client.post("/conversations", json={"case_file": CASE_FILE}).json()["conversation_id"]

    assert client.delete(f"/conversations/{conversation_id}").status_code == 204
    assert client.get(f"/conversations/{conversation_id}").status_code == 404
    assert client.delete(f"/conversations/{conversation_id}").status_code == 404


def test_no_agent_or_no_model_is_unavailable_not_an_error() -> None:
    for agent in (None, SimpleNamespace(reasoning_llm=None)):
        app = FastAPI()
        app.state.rag_agent = agent
        app.include_router(conversation_router.router)

        assert TestClient(app).post("/conversations", json={"case_file": CASE_FILE}).status_code == 503


def test_a_failing_pipeline_is_reported_and_leaves_no_conversation() -> None:
    class Failing(FakeChat):
        def open(self, case_file: str) -> Conversation:
            raise RuntimeError("model unavailable")

    client, _ = client_with(Failing())

    response = client.post("/conversations", json={"case_file": CASE_FILE})

    assert response.status_code == 500 and "model unavailable" in response.json()["detail"]
    assert len(getattr(client.app.state, "conversations", [])) == 0


def test_the_page_is_served_and_talks_to_these_routes() -> None:
    client, _ = client_with()

    response = client.get("/chat")

    assert response.status_code == 200 and response.headers["content-type"].startswith("text/html")
    assert "/conversations" in response.text


def test_query_route_knows_nothing_of_conversations() -> None:
    """The backend's contract: the conversation router adds routes, and takes
    none away or over."""
    paths = {route.path for route in rag_router.router.routes}
    added = {route.path for route in conversation_router.router.routes}

    assert paths == {"/health", "/query", "/retrieval-contexts/{context_id}"}
    assert not paths & added
