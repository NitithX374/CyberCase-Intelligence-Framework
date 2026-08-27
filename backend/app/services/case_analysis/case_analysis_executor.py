from __future__ import annotations

import hashlib

import httpx

from app.config import settings
from app.services.case_analysis.case_analysis_prompt_builder import (
    _validate_analysis_request,
    build_case_analysis_prompt,
)
from app.services.case_analysis.case_analysis_prompt_config import (
    CaseAnalysisFailure,
    _ANALYSIS_TRACE_OUTPUT_PROMPT,
    _CASE_ANALYSIS_TRUST_PROMPT,
    _PERSONALIZED_RESPONSE_PROMPT,
    _TASK_PROMPTS,
)
from app.services.case_analysis.contracts import (
    AnalysisMode,
    CaseAnalysisResult,
    ProviderCaseAnalysisV3,
)
from app.services.case_analysis.case_analysis_response_parser import (
    parse_case_analysis_response,
)
from app.services.case_analysis.personalization import resolve_response_language
from app.services.llm.core_llm import resolve_core_llm_target
from app.services.llm.structured_output_request_router import structured_output_request_options
from app.services.llm.structured_output_router import structured_output_schema


class MainCaseAnalysisService:
    """Run internal analysis without retrieval, persistence, or state mutation."""

    def __init__(self, *, client: httpx.AsyncClient | None = None) -> None:
        self._client = client

    async def analyze(
        self,
        *,
        mode: AnalysisMode,
        raw_evidence: str,
        analysis_context: dict[str, object] | None,
        question: str | None,
        user_message: object,
    ) -> CaseAnalysisResult:
        """Analyze defensive snapshots of Case Narrative and retrieval context."""

        validated_mode, validated_question = _validate_analysis_request(
            mode,
            question,
        )
        try:
            response_language = resolve_response_language(user_message)
        except ValueError as error:
            raise CaseAnalysisFailure(
                "analysis_response_language_unsupported",
                str(error),
            ) from error
        prompt = build_case_analysis_prompt(
            mode=validated_mode,
            raw_evidence=raw_evidence,
            analysis_context=analysis_context,
            question=validated_question,
            response_language=response_language,
        )
        target = resolve_core_llm_target(settings.chat_ask_model)
        request_payload = {
            "model": target.model,
            **structured_output_request_options(
                provider=target.provider,
                feature="case_analysis",
                configured_max_tokens=max(1, settings.chat_ask_max_output_tokens),
            ),
            "system": (
                _CASE_ANALYSIS_TRUST_PROMPT
                + "\n"
                + _TASK_PROMPTS[validated_mode]
                + "\n"
                + _PERSONALIZED_RESPONSE_PROMPT
                + "\n"
                + _ANALYSIS_TRACE_OUTPUT_PROMPT
            ),
            "messages": [{"role": "user", "content": prompt}],
            "output_config": {
                "format": {
                    "type": "json_schema",
                    "schema": structured_output_schema(
                        ProviderCaseAnalysisV3,
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
                timeout=max(0.01, settings.chat_ask_timeout_seconds),
            ) as owned_client:
                response = await self._post(
                    owned_client,
                    target.messages_url,
                    target.headers,
                    request_payload,
                )

        trusted_context = analysis_context or {}
        raw_source_ids = trusted_context.get("source_message_ids", [])
        source_message_ids = {
            value.strip() for value in raw_source_ids if isinstance(value, str)
        } if isinstance(raw_source_ids, list) else set()
        return parse_case_analysis_response(
            response,
            source_message_ids=source_message_ids,
            analysis_context=trusted_context,
            analysis_mode=validated_mode,
            evidence_sha256=hashlib.sha256(
                raw_evidence.strip().encode("utf-8")
            ).hexdigest(),
        )

    @staticmethod
    async def _post(
        client: httpx.AsyncClient,
        messages_url: str,
        headers: dict[str, str],
        request_payload: dict[str, object],
    ) -> httpx.Response:
        try:
            return await client.post(
                messages_url,
                headers=headers,
                json=request_payload,
            )
        except httpx.TimeoutException as exc:
            raise CaseAnalysisFailure(
                "analysis_timeout",
                "The post-answer analysis request timed out",
            ) from exc
        except httpx.RequestError as exc:
            raise CaseAnalysisFailure(
                "analysis_transport_error",
                "The post-answer analysis request failed",
            ) from exc


async def request_case_analysis(
    *,
    mode: AnalysisMode,
    raw_evidence: str,
    analysis_context: dict[str, object] | None,
    question: str | None,
    user_message: object,
    client: httpx.AsyncClient | None = None,
) -> CaseAnalysisResult:
    validated_mode, validated_question = _validate_analysis_request(mode, question)
    return await MainCaseAnalysisService(client=client).analyze(
        mode=validated_mode,
        raw_evidence=raw_evidence,
        analysis_context=analysis_context,
        question=validated_question,
        user_message=user_message,
    )


__all__ = ["MainCaseAnalysisService", "request_case_analysis"]
