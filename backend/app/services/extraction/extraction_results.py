from __future__ import annotations;

from dataclasses import dataclass
from typing import Literal

from app.services.extraction.extraction_config import (
    BASELINE_EXTRACTION_MODE,
    BASELINE_EXTRACTION_PROMPT_VERSION,
    BASELINE_EXTRACTION_VERSION,
)
from app.services.extraction.extraction_contracts import (
    CaseState,
    ExtractionInput,
)

@dataclass(frozen=True)
class ExtractionRunResult:
    status: Literal["candidate", "failed"]
    extraction: CaseState | None
    failure_code: str | None
    failure_message: str | None
    raw_response: str | None
    input_tokens: int | None
    output_tokens: int | None
    latency_ms: float
    provider: str
    model: str
    prompt_version: str = BASELINE_EXTRACTION_PROMPT_VERSION

    def metadata(self, extraction_input: ExtractionInput) -> dict[str, object]:
        """Return the JSON-safe metadata persisted beside the assistant answer."""

        from app.services.extraction.extraction_utils import safe_retained_response

        source_message_ids = [
            str(message.message_id) for message in extraction_input.messages
        ]
        metadata: dict[str, object] = {
            "version": BASELINE_EXTRACTION_VERSION,
            "mode": BASELINE_EXTRACTION_MODE,
            "status": self.status,
            "prompt_version": self.prompt_version,
            "provider": self.provider,
            "model": self.model,
            "validation_status": (
                "validated" if self.status == "candidate" else "failed"
            ),
            "latency_ms": self.latency_ms,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "source_message_ids": source_message_ids,
            "raw_response": safe_retained_response(self.raw_response),
        }
        if self.extraction is not None:
            metadata.update(self.extraction.model_dump(mode="json"))
        else:
            metadata["failure_code"] = self.failure_code or "extraction_failed"
            metadata["failure_message"] = self.failure_message or (
                "The extraction did not produce a validated result"
            )
        return metadata
