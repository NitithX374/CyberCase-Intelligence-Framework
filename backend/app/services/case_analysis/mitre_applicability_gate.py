from __future__ import annotations

import json
import logging
from collections.abc import Sequence
from uuid import UUID

import httpx

from app.config import settings
from app.services.case_analysis.case_analysis_response_utils import (
    _extract_visible_text,
)
from app.services.case_analysis.mitre_applicability_contracts import (
    MITRE_APPLICABILITY_GATE_VERSION,
    MitreApplicabilityRecord,
    ProviderMitreApplicability,
    skipped_mitre_applicability,
)
from app.services.case_analysis.mitre_applicability_prompt import (
    MITRE_APPLICABILITY_SYSTEM_PROMPT,
    build_mitre_applicability_prompt,
)
from app.services.case_analysis.mitre_applicability_validation import (
    validate_mitre_applicability,
)
from app.services.chat.raw_evidence import RawEvidenceSource
from app.services.llm.core_llm import resolve_core_llm_target
from app.services.llm.structured_output_request_router import (
    structured_output_request_options,
)
from app.services.llm.structured_output_router import structured_output_schema


logger = logging.getLogger("app.chat")


class MitreApplicabilityFailure(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


class MitreApplicabilityGate:
    def __init__(self, *, client: httpx.AsyncClient | None = None) -> None:
        self._client = client

    async def evaluate(
        self,
        evidence_sources: Sequence[RawEvidenceSource],
    ) -> MitreApplicabilityRecord:
        target = resolve_core_llm_target(settings.chat_ask_model)
        request_payload = {
            "model": target.model,
            **structured_output_request_options(
                provider=target.provider,
                feature="mitre_applicability",
                configured_max_tokens=512,
                temperature=0.0,
            ),
            "system": MITRE_APPLICABILITY_SYSTEM_PROMPT,
            "messages": [
                {
                    "role": "user",
                    "content": build_mitre_applicability_prompt(evidence_sources),
                }
            ],
            "output_config": {
                "format": {
                    "type": "json_schema",
                    "schema": structured_output_schema(
                        ProviderMitreApplicability,
                        provider=target.provider,
                    ),
                }
            },
        }
        if self._client is not None:
            response = await self._post(
                self._client,
                target.messages_url,
                target.headers,
                request_payload,
            )
        else:
            async with httpx.AsyncClient(
                timeout=max(0.01, settings.chat_ask_timeout_seconds)
            ) as client:
                response = await self._post(
                    client,
                    target.messages_url,
                    target.headers,
                    request_payload,
                )
        return validate_mitre_applicability(
            _parse_provider_response(response),
            evidence_sources,
        )

    @staticmethod
    async def _post(
        client: httpx.AsyncClient,
        url: str,
        headers: dict[str, str],
        payload: dict[str, object],
    ) -> httpx.Response:
        try:
            return await client.post(url, headers=headers, json=payload)
        except httpx.TimeoutException as error:
            raise MitreApplicabilityFailure(
                "mitre_applicability_timeout",
                "MITRE applicability provider timed out",
            ) from error
        except httpx.RequestError as error:
            raise MitreApplicabilityFailure(
                "mitre_applicability_provider_error",
                "MITRE applicability provider request failed",
            ) from error


async def evaluate_mitre_applicability(
    *,
    source_run_id: UUID,
    evidence_sources: Sequence[RawEvidenceSource],
    gate: MitreApplicabilityGate | None = None,
) -> MitreApplicabilityRecord:
    try:
        result = await (gate or MitreApplicabilityGate()).evaluate(evidence_sources)
        if result.failure_code is not None:
            logger.warning(
                "MITRE applicability failed closed gate_version=%s "
                "source_run_id=%s failure_code=%s",
                MITRE_APPLICABILITY_GATE_VERSION,
                source_run_id,
                result.failure_code,
            )
        return result
    except MitreApplicabilityFailure as error:
        failure_code = error.code
    except Exception:
        failure_code = "mitre_applicability_provider_error"
    logger.warning(
        "MITRE applicability failed closed gate_version=%s source_run_id=%s "
        "failure_code=%s",
        MITRE_APPLICABILITY_GATE_VERSION,
        source_run_id,
        failure_code,
    )
    return skipped_mitre_applicability(failure_code)


def _parse_provider_response(response: httpx.Response) -> dict[str, object]:
    if not 200 <= response.status_code < 300:
        raise MitreApplicabilityFailure(
            "mitre_applicability_provider_error",
            "MITRE applicability provider returned an error",
        )
    try:
        payload = response.json()
    except (TypeError, ValueError) as error:
        raise MitreApplicabilityFailure(
            "mitre_applicability_invalid_output",
            "MITRE applicability provider response was invalid",
        ) from error
    if not isinstance(payload, dict) or payload.get("stop_reason") in {
        "refusal",
        "max_tokens",
        "length",
        "pause_turn",
    }:
        raise MitreApplicabilityFailure(
            "mitre_applicability_invalid_output",
            "MITRE applicability provider did not return a complete object",
        )
    raw_text = _extract_visible_text(payload).strip()
    try:
        parsed = json.loads(raw_text)
    except (TypeError, ValueError) as error:
        raise MitreApplicabilityFailure(
            "mitre_applicability_invalid_output",
            "MITRE applicability output was not strict JSON",
        ) from error
    if not isinstance(parsed, dict):
        raise MitreApplicabilityFailure(
            "mitre_applicability_invalid_output",
            "MITRE applicability output was not an object",
        )
    return parsed


__all__ = [
    "MitreApplicabilityFailure",
    "MitreApplicabilityGate",
    "evaluate_mitre_applicability",
]
