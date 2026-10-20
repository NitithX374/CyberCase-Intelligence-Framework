from __future__ import annotations

import json

import httpx

from app.config import settings
from app.llm import request

from research.attribution_benchmark.propagation_metrics import propagation_metrics


class ResponseCapture(httpx.AsyncBaseTransport):
    def __init__(self, directory):
        self.directory = directory
        self.counter = 0

    async def handle_async_request(self, item):
        async with httpx.AsyncHTTPTransport() as transport:
            response = await transport.handle_async_request(item)
            body = await response.aread()
        self.counter += 1
        text = body.decode("utf-8", errors="replace")
        key = settings.openrouter_cybercase
        if key:
            text = text.replace(key, "[REDACTED]")
        path = self.directory / f"provider_response_{self.counter:02d}.json"
        path.write_text(text, encoding="utf-8")
        return response


async def execute_arm(
    directory,
    cluster,
    accepted,
    payload,
    config,
    outcome,
    persist,
    judge,
    *,
    record_only=False,
):
    outcome["status"] = "running"
    persist(directory / "outcome.json", outcome)
    previous = request.transport
    request.transport = ResponseCapture(directory)
    try:
        judgement = await judge(payload, config, outcome["calls"])
        persist(directory / "judgement.json", judgement.model_dump(mode="json"))
        outcome["propagation"] = propagation_metrics(
            cluster, accepted, judgement.summary
        )
        outcome["status"] = (
            "completed"
            if outcome["propagation"]["protocol_valid"]
            else "protocol_violation"
        )
        if outcome["status"] == "protocol_violation" and not record_only:
            raise ValueError("Judgement citation protocol violation")
    except Exception as error:
        outcome.update(error_type=type(error).__name__, error=str(error))
        if outcome["status"] != "protocol_violation":
            outcome["status"] = "failed"
        if not record_only:
            raise
    finally:
        request.transport = previous
        persist(directory / "outcome.json", outcome)
    return outcome["status"] == "completed"


def existing_outcome(directory, expected):
    path = directory / "outcome.json"
    if not path.exists():
        return None
    saved = json.loads(path.read_text(encoding="utf-8"))
    if any(
        saved[key] != expected[key]
        for key in (
            "cluster",
            "arm",
            "accepted_claim_ids",
            "payload_sha256",
            "admission",
        )
    ):
        raise ValueError("Resumed arm differs from fixed original inputs")
    return saved
