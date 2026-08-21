from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.services.case_state.delta_models import CaseStateDelta, CaseStateDeltaInput
from app.services.case_state.delta_config import CASE_STATE_DELTA_PROMPT_VERSION

@dataclass(frozen=True)
class CaseStateDeltaRunResult:
    status: Literal["candidate", "failed"]
    delta: CaseStateDelta | None
    failure_code: str | None
    failure_message: str | None
    raw_response: str | None
    input_tokens: int | None
    output_tokens: int | None
    latency_ms: float
    provider: str
    model: str

    def metadata(self, delta_input: CaseStateDeltaInput) -> dict[str, object]:
        metadata: dict[str, object] = {
            "status": self.status,
            "prompt_version": CASE_STATE_DELTA_PROMPT_VERSION,
            "provider": self.provider,
            "model": self.model,
            "validation_status": (
                "validated" if self.status == "candidate" else "failed"
            ),
            "latency_ms": self.latency_ms,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "source_message_ids": [str(delta_input.source_message_id)],
            "raw_response": safe_raw_response(self.raw_response),
        }
        if self.delta is not None:
            metadata["delta"] = self.delta.model_dump(mode="json")
        else:
            metadata["failure_code"] = self.failure_code or "case_state_delta_failed"
            metadata["failure_message"] = self.failure_message or (
                "The Case State delta did not pass validation"
            )
        return metadata

def safe_raw_response(value: str | None) -> str | None:
    from app.services.extraction.llm_extraction import _safe_retained_response
    return _safe_retained_response(value)
