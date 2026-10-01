from __future__ import annotations

import json
from contextlib import asynccontextmanager
from functools import partial
from types import SimpleNamespace

import httpx
import pytest
from case_chat_support import GAP, NARRATIVE, SETTLED, seeded_case
from httpx import ASGITransport, AsyncClient
from isolated_database import isolated_database
from sqlalchemy import select

import app.analysis.routes as analysis_router
import app.chat.routes as chat_router
from app.analysis.run import run_case_analysis
from app.auth.guard import get_current_user
from app.chat.reply import send_case_message
from app.config import settings
from app.database import get_db
from app.llm import request as provider
from app.llm.openrouter import CoreLlmTarget
from app.main import app
from app.models.chat_message import ChatMessage
from app.models.source import CaseSource
from app.trace import bind
from app.trace.quotes import MAX_QUOTE_CHARS

pytestmark = pytest.mark.asyncio

NO_GAPS = {"version": "case_assessment_v1", "gaps": []}
ASKING = {"version": "case_assessment_v1", "gaps": [GAP]}
HEAD = "The attacker logged in to the VPN gateway."
TAIL = "The attacker exfiltrated the payroll archive."
STAGES = {"suggestion": "answer", "summary": "judge", "gaps": "assess"}
JUDGED = {
    "version": "case_analysis_trace_v1",
    "summary": "Files on the shared drive were encrypted.",
    "gaps": [],
    "mitre_associations": [],
}


def reading(*claims: dict) -> dict:
    return {
        "version": "case_analysis_trace_v1",
        "involved_parties": [],
        "timeline": [],
        "claims": list(claims),
        "impacts": [],
    }


def claim(claim_id: str, source_id: str, quote: str) -> dict:
    return {
        "claim_id": claim_id,
        "claim_type": "reported",
        "text": "The incident was reported.",
        "epistemic_status": "reported",
        "supporting_source_ids": [source_id],
        "contradicting_source_ids": [],
        "supporting_citations": [{"source_id": source_id, "exact_quote": quote}],
        "contradicting_citations": [],
    }


def general(text: str) -> dict:
    return {
        "units": [{"text": text, "basis": "general", "claim_ids": [], "quotes": []}],
        "suggestion": "none",
    }


def down(_content: dict) -> httpx.Response:
    return httpx.Response(503, json={"error": "unavailable"})


def slowed(_content: dict) -> httpx.Response:
    return httpx.Response(429, json={"error": "rate limited"})


def refused(_content: dict) -> httpx.Response:
    return httpx.Response(401, json={"error": "bad key"})


def timing_out(_content: dict) -> httpx.Response:
    raise httpx.ReadTimeout("slow")


def disconnecting(_content: dict) -> httpx.Response:
    raise httpx.ConnectError("connection reset")


def off_schema(_content: dict) -> dict:
    return {"version": "case_analysis_trace_v1", "summary": "Half an answer."}


def unreadable(_content: dict) -> httpx.Response:
    return httpx.Response(200, text="<html>upstream page</html>")


def erring(_content: dict) -> httpx.Response:
    return httpx.Response(200, json={"error": {"message": "upstream failed"}})


def cut_short(_content: dict) -> httpx.Response:
    return httpx.Response(200, json={"stop_reason": "max_tokens", "content": []})


def declined(_content: dict) -> httpx.Response:
    return httpx.Response(200, json={"stop_reason": "refusal", "content": []})


def rejected(_content: dict) -> httpx.Response:
    return httpx.Response(400, json={"error": "bad request"})


class Model:
    def __init__(self, **replies: list) -> None:
        self.replies = {stage: list(script) for stage, script in replies.items()}
        self.calls: list[tuple[str, dict]] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content)
        if "output_config" in payload:
            properties = payload["output_config"]["format"]["schema"]["properties"]
            stage = next(name for key, name in STAGES.items() if key in properties)
        else:
            stage = "read"
        content = json.loads(payload["messages"][0]["content"])
        self.calls.append((stage, content))
        script = self.replies[stage]
        reply = script.pop(0) if len(script) > 1 else script[0]
        if callable(reply):
            reply = reply(content)
        if isinstance(reply, httpx.Response):
            return reply
        return httpx.Response(200, json={"output_text": json.dumps(reply)})

    def stages(self) -> list[str]:
        return [stage for stage, _ in self.calls]


@pytest.fixture
def model(monkeypatch):
    monkeypatch.setattr(provider, "TRANSPORT_RETRY_DELAY_SECONDS", 0)
    monkeypatch.setattr(
        provider,
        "resolve_core_llm_target",
        lambda model: CoreLlmTarget(
            model=model, messages_url="https://provider.test/v1/messages", headers={}
        ),
    )
    monkeypatch.setattr(settings, "mitre_gate_mode", "never")

    def answering(**replies: list) -> Model:
        scripted = Model(**replies)
        monkeypatch.setattr(provider, "transport", httpx.MockTransport(scripted))
        return scripted

    return answering


@asynccontextmanager
async def signed_in(monkeypatch, factory, user_id):
    monkeypatch.setattr(
        analysis_router, "run_case_analysis", partial(run_case_analysis, session_factory=factory)
    )
    monkeypatch.setattr(
        chat_router, "send_case_message", partial(send_case_message, session_factory=factory)
    )

    async def request_session():
        async with factory() as session:
            yield session

    fastapi_app = app.app
    fastapi_app.dependency_overrides[get_db] = request_session
    fastapi_app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=user_id)
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app, raise_app_exceptions=False),
            base_url="http://test/api/v1",
        ) as client:
            yield client
    finally:
        fastapi_app.dependency_overrides.pop(get_db, None)
        fastapi_app.dependency_overrides.pop(get_current_user, None)


async def stored_kinds(factory, case_id) -> list[str]:
    async with factory() as db:
        rows = await db.scalars(
            select(ChatMessage).where(ChatMessage.case_id == case_id).order_by(ChatMessage.ordinal)
        )
        return [message.message_kind for message in rows]


FILLER = " ".join(f"Routine log line {n} recorded nothing unusual." for n in range(80))
LONG_TEXT = f"{HEAD} {FILLER} {TAIL}"
MARKED_WORDS = [f"tok{n:03d}" for n in range(250)]
MARKED_TEXT = "\n\n".join(f"**{word}**" for word in MARKED_WORDS)


async def case_with_source(factory, text: str) -> tuple:
    case_id, user_id, _ = await seeded_case(factory, trace=None)
    async with factory() as db, db.begin():
        db.add(CaseSource(case_id=case_id, source_kind="narrative", exact_text=text))
    return case_id, user_id


def citing(text: str, quote: str):
    def cite(content: dict) -> dict:
        [source_id] = [s["source_id"] for s in content["case_sources"] if s["text"] == text]
        return reading(claim("A-01", source_id, quote))

    return cite


async def test_an_elided_quote_that_spans_too_much_of_a_source_is_dropped_not_a_500(
    monkeypatch, model
):
    async with isolated_database() as factory:
        case_id, user_id = await case_with_source(factory, LONG_TEXT)
        model(assess=[NO_GAPS], read=[citing(LONG_TEXT, f"{HEAD} ... {TAIL}")], judge=[JUDGED])
        async with signed_in(monkeypatch, factory, user_id) as client:
            ran = await client.post(f"/cases/{case_id}/analysis")
            stored = await client.get(f"/cases/{case_id}/analysis")

        assert ran.status_code == 200, ran.text
        assert ran.json()["status"] == "completed"
        trace = stored.json()["trace_json"]
        assert [c["claim_id"] for c in trace["claims"]] == ["A-01"], "the claim is kept"
        assert trace["claims"][0]["supporting_citations"] == []
        assert trace["grounding"]["citations_verified"] == 0
        assert trace["grounding"]["citations_duplicated"] == 0


async def test_a_trace_the_binder_cannot_store_is_a_coded_server_error(monkeypatch, model):
    async with isolated_database() as factory:
        case_id, user_id = await case_with_source(factory, MARKED_TEXT)
        monkeypatch.setattr(bind, "MAX_QUOTE_CHARS", 10 * MAX_QUOTE_CHARS)
        quote = " ".join(MARKED_WORDS)
        model(assess=[NO_GAPS], read=[citing(MARKED_TEXT, quote)], judge=[JUDGED])
        async with signed_in(monkeypatch, factory, user_id) as client:
            ran = await client.post(f"/cases/{case_id}/analysis")
            stored = await client.get(f"/cases/{case_id}/analysis")

        assert ran.status_code == 500
        assert ran.json()["detail"]["code"] == "case_bind_invalid"
        assert stored.json() is None


@pytest.mark.parametrize(
    ("failure", "status_code", "code"),
    [
        (down, 502, "analysis_provider_down"),
        (slowed, 504, "analysis_provider_timeout"),
        (timing_out, 504, "case_reading_timeout"),
        (disconnecting, 502, "case_reading_transport"),
        (off_schema, 502, "case_reading_invalid"),
        (unreadable, 502, "analysis_invalid_response"),
        (erring, 502, "analysis_provider_error"),
        (cut_short, 502, "case_reading_invalid"),
        (refused, 409, "analysis_provider_unauthorized"),
        (declined, 409, "case_reading_incomplete"),
        (rejected, 409, "analysis_provider_error"),
    ],
)
async def test_a_provider_that_fails_for_now_is_a_server_error_the_client_may_retry(
    monkeypatch, model, failure, status_code, code
):
    async with isolated_database() as factory:
        case_id, user_id, _ = await seeded_case(factory, trace=None)
        model(assess=[NO_GAPS], read=[failure], judge=[JUDGED])
        async with signed_in(monkeypatch, factory, user_id) as client:
            response = await client.post(f"/cases/{case_id}/analysis")

        assert response.status_code == status_code
        assert response.json()["detail"]["code"] == code


async def test_an_answer_whose_round_met_an_outage_is_retryable_and_the_retry_resumes_it(
    monkeypatch, model
):
    async with isolated_database() as factory:
        case_id, user_id, _ = await seeded_case(factory)
        scripted = model(assess=[NO_GAPS], read=[down], judge=[JUDGED])
        send = {"content": "Around two in the morning.", "client_request_id": "send-1"}
        async with signed_in(monkeypatch, factory, user_id) as client:
            failed = await client.post(f"/cases/{case_id}/chat/messages", json=send)
            scripted.replies["read"] = [reading()]
            retried = await client.post(f"/cases/{case_id}/chat/messages", json=send)

        assert failed.status_code == 502
        assert failed.json()["detail"]["code"] == "analysis_provider_down"
        assert retried.status_code == 200
        assert retried.json()["analysis"]["status"] == "validated"


async def test_an_analysis_stored_while_a_question_waits_retires_the_question(monkeypatch, model):
    async with isolated_database() as factory:
        case_id, user_id, _ = await seeded_case(factory, trace=None)
        scripted = model(
            assess=[ASKING, NO_GAPS],
            read=[reading()],
            judge=[JUDGED],
            answer=[general("T1059 is Command and Scripting Interpreter.")],
        )
        async with signed_in(monkeypatch, factory, user_id) as client:
            asked = await client.post(f"/cases/{case_id}/analysis")
            analysed = await client.post(f"/cases/{case_id}/analysis")
            chat = await client.get(f"/cases/{case_id}/chat")
            sent = await client.post(
                f"/cases/{case_id}/chat/messages", json={"content": "What does ATT&CK T1059 mean?"}
            )

        assert asked.json()["status"] == "need_followup"
        assert analysed.json()["status"] == "completed"
        assert chat.json()["pending_question_id"] is None
        assert sent.status_code == 200, sent.text
        assert [m["message_kind"] for m in sent.json()["messages"]] == [
            "conversation",
            "conversation",
        ], "the next message is a question about the case, not an answer to a retired question"
        assert sent.json()["analysis"] is None
        assert scripted.stages().count("read") == 1


async def asked_twice_then_lost(client, scripted: Model, case_id) -> httpx.Response:
    first = await client.post(f"/cases/{case_id}/analysis")
    second = await client.post(f"/cases/{case_id}/analysis")
    assert (first.json()["status"], second.json()["status"]) == ("need_followup", "need_followup")
    lost = await client.post(
        f"/cases/{case_id}/chat/messages",
        json={"content": "Around two in the morning.", "client_request_id": "send-1"},
    )
    assert lost.json()["detail"]["code"] == "analysis_provider_down"
    scripted.replies["read"] = [reading()]
    return lost


async def test_a_round_asked_twice_resumes_when_its_answer_is_sent_again(monkeypatch, model):
    async with isolated_database() as factory:
        case_id, user_id, _ = await seeded_case(factory, trace=None)
        scripted = model(assess=[ASKING], read=[down], judge=[JUDGED])
        async with signed_in(monkeypatch, factory, user_id) as client:
            await asked_twice_then_lost(client, scripted, case_id)
            retried = await client.post(
                f"/cases/{case_id}/chat/messages",
                json={"content": "Around two in the morning.", "client_request_id": "send-1"},
            )

        assert retried.status_code == 200
        assert retried.json()["analysis"] is not None, "the retry must run the round's analysis"
        assert scripted.stages().count("read") == 2


async def test_a_round_asked_twice_resumes_when_the_case_is_analysed_again(monkeypatch, model):
    async with isolated_database() as factory:
        case_id, user_id, _ = await seeded_case(factory, trace=None)
        scripted = model(assess=[ASKING], read=[down], judge=[JUDGED])
        async with signed_in(monkeypatch, factory, user_id) as client:
            await asked_twice_then_lost(client, scripted, case_id)
            analysed = await client.post(f"/cases/{case_id}/analysis")

        assert analysed.json()["status"] == "completed", "the answered gap was asked again"
        assert analysed.json()["result"]["trace_json"]["stop_reason"] == "gaps_exhausted"
        _, read = scripted.calls[-2]
        assert [item["qa_id"] for item in read["followup_history"]] == ["QA-01"]
        assert (await stored_kinds(factory, case_id)).count("followup_question") == 1


async def test_a_chat_answer_keeps_the_follow_up_answer_its_claim_rests_on(monkeypatch, model):
    async with isolated_database() as factory:
        case_id, user_id, _ = await seeded_case(factory)
        reply = "Around two in the morning."

        def cite_the_reply(content: dict) -> dict:
            [answered] = content["followup_history"]
            [narrative] = [s["source_id"] for s in content["case_sources"]]
            return reading(
                claim("A-01", answered["qa_id"], reply), claim("A-02", narrative, NARRATIVE)
            )

        model(
            assess=[NO_GAPS],
            read=[cite_the_reply],
            judge=[JUDGED],
            answer=[
                {
                    "units": [
                        {
                            "text": "It began around two.",
                            "basis": "case_fact",
                            "claim_ids": ["A-01"],
                            "quotes": [],
                        }
                    ],
                    "suggestion": "none",
                }
            ],
        )
        async with signed_in(monkeypatch, factory, user_id) as client:
            closed = await client.post(f"/cases/{case_id}/chat/messages", json={"content": reply})
            asked = await client.post(
                f"/cases/{case_id}/chat/messages", json={"content": "When did it begin?"}
            )

        analysed = closed.json()["analysis"]["trace_json"]["claims"][0]
        assert analysed["supporting_source_ids"] == ["QA-01"]
        answer_trace = asked.json()["messages"][1]["metadata_json"]["analysis_trace"]
        [answered_claim] = answer_trace["claims"]
        assert answered_claim["supporting_source_ids"] == ["QA-01"]
        assert [c["source_id"] for c in answered_claim["supporting_citations"]] == ["QA-01"]
        assert answer_trace["grounding"]["citations_unfound"] == 0


async def test_an_answer_too_long_to_store_is_a_coded_bad_gateway(monkeypatch, model):
    async with isolated_database() as factory:
        answerable = {
            **SETTLED,
            "claims": [
                {
                    "claim_id": "A-01",
                    "claim_type": "reported",
                    "text": "Files were encrypted.",
                    "epistemic_status": "reported",
                }
            ],
        }
        case_id, user_id, _ = await seeded_case(factory, trace=answerable, asking=False)
        unit = {"text": "x" * 3_900, "claim_ids": ["A-01"]}
        model(answer=[{"units": [unit] * 7, "suggestion": "none"}])
        async with signed_in(monkeypatch, factory, user_id) as client:
            response = await client.post(
                f"/cases/{case_id}/chat/messages", json={"content": "What happened?"}
            )

        assert response.status_code == 502, response.text
        assert response.json()["detail"]["code"] == "chat_answer_invalid"


async def test_a_blank_answer_is_refused_and_the_question_still_waits(monkeypatch, model):
    async with isolated_database() as factory:
        case_id, user_id, question_id = await seeded_case(factory)
        scripted = model(assess=[NO_GAPS], read=[reading()], judge=[JUDGED])
        async with signed_in(monkeypatch, factory, user_id) as client:
            refused_answer = await client.post(
                f"/cases/{case_id}/chat/messages", json={"content": "   "}
            )
            chat = await client.get(f"/cases/{case_id}/chat")

        assert refused_answer.status_code == 422
        assert refused_answer.json()["detail"]["code"] == "case_chat_content_empty"
        assert chat.json()["pending_question_id"] == str(question_id)
        assert await stored_kinds(factory, case_id) == ["followup_question"]
        assert scripted.calls == []


async def test_nul_in_pasted_text_is_dropped_and_in_a_record_is_refused(monkeypatch, model):
    async with isolated_database() as factory:
        case_id, user_id, _ = await seeded_case(factory, trace=SETTLED, asking=False)
        model(answer=[general("Noted.")])
        async with signed_in(monkeypatch, factory, user_id) as client:
            pasted = await client.post(
                f"/cases/{case_id}/sources", json={"exact_text": "copied\u0000text"}
            )
            in_value = await client.post(
                f"/cases/{case_id}/sources",
                json={"exact_text": "clean", "provenance_json": {"note": ["a\u0000b"]}},
            )
            in_key = await client.post(
                f"/cases/{case_id}/sources",
                json={"exact_text": "clean", "source_metadata_json": {"a\u0000b": 1}},
            )
            asked = await client.post(
                f"/cases/{case_id}/chat/messages", json={"content": "what\u0000now?"}
            )
            keyed = await client.post(
                f"/cases/{case_id}/chat/messages",
                json={"content": "hello", "client_request_id": "send\u00001"},
            )
            listed = await client.get(f"/cases/{case_id}/sources")

        assert pasted.status_code == 201, pasted.text
        assert pasted.json()["exact_text"] == "copiedtext"
        assert (in_value.status_code, in_key.status_code) == (422, 422)
        assert asked.status_code == 200, asked.text
        assert asked.json()["messages"][0]["content"] == "whatnow?"
        assert keyed.status_code == 422
        assert [source["exact_text"] for source in listed.json()] == [NARRATIVE, "copiedtext"]


async def test_nul_in_an_answer_to_a_question_is_dropped(monkeypatch, model):
    async with isolated_database() as factory:
        case_id, user_id, question_id = await seeded_case(factory)
        model(assess=[NO_GAPS], read=[reading()], judge=[JUDGED])
        async with signed_in(monkeypatch, factory, user_id) as client:
            answered = await client.post(
                f"/cases/{case_id}/chat/messages", json={"content": "Around\u0000 two."}
            )

        assert answered.status_code == 200, answered.text
        [answer] = [
            m for m in answered.json()["messages"] if m["message_kind"] == "followup_answer"
        ]
        assert answer["content"] == "Around two."
        assert answer["in_reply_to_message_id"] == str(question_id)


async def test_nul_in_a_case_title_is_dropped(monkeypatch):
    async with isolated_database() as factory:
        case_id, user_id, _ = await seeded_case(factory, trace=None)
        async with signed_in(monkeypatch, factory, user_id) as client:
            created = await client.post("/cases", json={"title": "Payroll\u0000 leak"})
            renamed = await client.patch(f"/cases/{case_id}", json={"title": "Drive\u0000 lock"})
            emptied = await client.patch(f"/cases/{case_id}", json={"title": "\u0000"})
            kept = await client.get(f"/cases/{case_id}")

        assert (created.status_code, created.json()["title"]) == (201, "Payroll leak")
        assert (renamed.status_code, renamed.json()["title"]) == (200, "Drive lock")
        assert emptied.status_code == 422
        assert kept.json()["title"] == "Drive lock"


async def test_before_an_analysis_the_chat_quotes_the_source_it_answers_from(monkeypatch, model):
    async with isolated_database() as factory:
        case_id, user_id, _ = await seeded_case(factory, trace=None)

        def quote_the_narrative(content: dict) -> dict:
            [source] = content["case_sources"]
            return {
                "units": [
                    {
                        "text": "The narrative records it.",
                        "basis": "case_fact",
                        "claim_ids": [],
                        "quotes": [{"source_id": source["source_id"], "exact_quote": NARRATIVE}],
                    },
                    {
                        "text": "It may be ransomware.",
                        "basis": "interpretation",
                        "claim_ids": [],
                        "quotes": [],
                    },
                ],
                "suggestion": "run_analysis",
            }

        scripted = model(answer=[quote_the_narrative])
        async with signed_in(monkeypatch, factory, user_id) as client:
            asked = await client.post(
                f"/cases/{case_id}/chat/messages", json={"content": "What happened?"}
            )

        assert asked.status_code == 200, asked.text
        _, read = scripted.calls[-1]
        assert read["analysis"] is None
        assert read["analysis_status"] == "none"
        metadata = asked.json()["messages"][1]["metadata_json"]
        fact, reading = metadata["answer_units"]
        assert [c["exact_quote"] for c in fact["supporting_citations"]] == [NARRATIVE]
        assert reading["basis"] == "interpretation"
        assert metadata["suggestion"] == "run_analysis"
