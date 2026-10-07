from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from time import perf_counter

from app.llm import request as provider


class EvaluationBudgetExceeded(Exception):
    pass


@dataclass
class Budget:
    cap_usd: float
    input_price: float
    output_price: float
    spent: float = 0.0
    reserved: float = 0.0
    requests: int = 0
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    async def reserve(self, payload: dict) -> float:
        tokens = await asyncio.to_thread(provider.token_count, payload)
        reservation = (
            tokens * 2 * self.input_price + payload["max_tokens"] * self.output_price
        )
        async with self.lock:
            if self.spent + self.reserved + reservation > self.cap_usd:
                raise EvaluationBudgetExceeded(
                    "Research request reservation cap reached"
                )
            self.reserved += reservation
            self.requests += 1
        return reservation

    async def release(self, reservation: float, actual: float) -> None:
        async with self.lock:
            self.reserved -= reservation
            self.spent += actual


def recorded_post(original, budget: Budget, responses: list[dict]):
    async def post(target, payload, *, stage, timeout):
        reservation = await budget.reserve(payload)
        started = perf_counter()
        actual = reservation
        try:
            response = await original(target, payload, stage=stage, timeout=timeout)
            try:
                decoded = response.json()
            except ValueError:
                decoded = {"non_json_response": response.text}
            usage = provider.usage_summary(decoded)
            actual = (usage.get("input_tokens") or 0) * budget.input_price + (
                usage.get("output_tokens") or 0
            ) * budget.output_price
            if (
                not usage.get("input_tokens")
                and not usage.get("output_tokens")
                and response.status_code < 400
            ):
                actual = reservation
            responses.append(
                {
                    "stage": stage,
                    "status_code": response.status_code,
                    "seconds": perf_counter() - started,
                    "usage": usage,
                    "estimated_usd": actual,
                    "response": decoded,
                }
            )
            return response
        except Exception as error:
            responses.append(
                {
                    "stage": stage,
                    "seconds": perf_counter() - started,
                    "error": type(error).__name__,
                    "reserved_usd_charged": actual,
                }
            )
            raise
        finally:
            await budget.release(reservation, actual)

    return post
