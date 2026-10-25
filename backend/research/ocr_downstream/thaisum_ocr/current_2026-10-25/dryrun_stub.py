"""Dry run of run_current.py with NO network: a local stub answers every model call. Its output is FAKE.

  python dryrun_stub.py --articles 2 --results-dir <a folder outside the repository>

The stub replaces the provider transport (app.llm.request.transport, the one seam every model call takes) with an
httpx.MockTransport. Every socket connect, connect_ex and getaddrinfo to a non-loopback host, and every
create_connection, raises, so any path that would reach the network fails the dry run instead of reaching it
(loopback stays open only because asyncio's Windows event loop connects a local socket pair to itself). The stub's replies are built from the request it
is sent (it copies Source unit text into claims), so the scores of a dry run mean nothing; they only show that the
harness and the scorer run end to end on the current trace shape.
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse  # noqa: E402
import asyncio  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import socket  # noqa: E402

NETWORK_ATTEMPTS: list[str] = []


LOOPBACK = ("127.0.0.1", "::1")


def refuse(name, original, address_at):
    def blocked(*args, **kwargs):
        address = args[address_at] if len(args) > address_at else None
        host = address[0] if isinstance(address, tuple) else address
        if host in LOOPBACK and name != "create_connection":
            return original(*args, **kwargs)
        NETWORK_ATTEMPTS.append(f"{name} {host!r}")
        raise OSError(f"dry run: network blocked ({name})")
    return blocked


socket.socket.connect = refuse("socket.connect", socket.socket.connect, 1)
socket.socket.connect_ex = refuse("socket.connect_ex", socket.socket.connect_ex, 1)
socket.create_connection = refuse("create_connection", socket.create_connection, 0)
socket.getaddrinfo = refuse("getaddrinfo", socket.getaddrinfo, 0)

os.environ["OPENROUTER_CYBERCASE"] = "dry-run-stub-not-a-key"
os.environ["OPENROUTER_MESSAGES_URL"] = "http://stub.invalid/api/v1/messages"

import httpx  # noqa: E402
import run_current  # noqa: E402

from app.llm import request as provider  # noqa: E402
from app.trace.sentences import segmenter_identity  # noqa: E402

STUB_CALLS: list[str] = []


def reading_reply(content: dict) -> dict:
    claims = []
    for source in content["case_sources"]:
        units = [u for u in source["evidence_units"] if u["text"].strip()]
        for index, unit in enumerate(units[:10]):
            status = "suspected" if index == 3 else "unknown" if index == 5 else "reported"
            claims.append({"claim_id": f"A-{len(claims) + 1:02d}", "claim_type": "reported",
                           "text": unit["text"].strip()[:4000], "epistemic_status": status,
                           "supporting_citations": [{"source_id": source["source_id"],
                                                     "evidence_unit_ids": [unit["unit_id"]]}],
                           "contradicting_citations": []})
        claims.append({"claim_id": f"A-{len(claims) + 1:02d}", "claim_type": "reported", "text": "stub claim",
                       "epistemic_status": "reported",
                       "supporting_citations": [{"source_id": source["source_id"], "evidence_unit_ids": ["U999"]}],
                       "contradicting_citations": []})
    return {"claims": claims}


def judgement_reply(content: dict) -> dict:
    claims = content["reading"]["claims"][: content["summary_sentence_limit"]]
    summary = " ".join(f"{claim['text'][:80]} [{claim['claim_id']}]." for claim in claims)
    return {"summary": summary or "stub summary", "gaps": [{
        "gap_id": "G-01", "gap_key": "when", "topic": "stub", "status": "NOT_PROVIDED",
        "description": "stub gap description", "affected_claim_ids": [claims[0]["claim_id"]] if claims else [],
        "reason": "stub", "priority": "low", "askable": True, "clarification_question": "stub question?"}]}


def views_reply(content: dict) -> dict:
    claims = content["claims"]
    first = claims[0]
    return {"parties": [{"name": first["text"][:20], "role": None, "claim_ids": [first["claim_id"]]}],
            "timeline": [{"time": None, "event": c["text"], "claim_ids": [c["claim_id"]]} for c in claims[:5]],
            "impacts": [{"description": claims[-1]["text"], "claim_ids": [claims[-1]["claim_id"]]},
                        {"description": "dropped: unknown claim", "claim_ids": ["A-99"]}]}


def stub_handler(request: httpx.Request) -> httpx.Response:
    payload = json.loads(request.content)
    content = json.loads(payload["messages"][0]["content"])
    if "case_sources" in content:
        stage, reply = "case_reading", reading_reply(content)
    elif "reading" in content:
        stage, reply = "case_judgement", judgement_reply(content)
    else:
        stage, reply = "case_views", views_reply(content)
    STUB_CALLS.append(stage)
    text = json.dumps(reply, ensure_ascii=False)
    input_tokens = provider.token_count(payload)
    output_tokens = provider.token_count(reply)
    cost = input_tokens * run_current.PRICE["input"] + output_tokens * run_current.PRICE["output"]
    return httpx.Response(200, json={
        "id": "stub", "type": "message", "role": "assistant", "model": payload["model"], "provider": "DRY-RUN-STUB",
        "content": [{"type": "text", "text": text}], "stop_reason": "end_turn",
        "usage": {"input_tokens": input_tokens, "output_tokens": output_tokens, "cost": cost}})


provider.transport = httpx.MockTransport(stub_handler)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--articles", type=int, default=2)
    parser.add_argument("--results-dir", required=True)
    args = parser.parse_args()
    report = asyncio.run(run_current.main(["--articles", str(args.articles), "--cap-usd", "0.05",
                                           "--confirm-spend", "--concurrency", "3",
                                           "--expect-segmenter", segmenter_identity().split(":")[0],
                                           "--results-dir", args.results_dir]))
    print(json.dumps({"FAKE_STUB_OUTPUT": True, "stub_calls": STUB_CALLS, "network_attempts": NETWORK_ATTEMPTS,
                      "spent_usd_stub": report["spent_usd"]}, indent=1))
    if NETWORK_ATTEMPTS:
        raise SystemExit("a network attempt was made during the dry run")


if __name__ == "__main__":
    main()
