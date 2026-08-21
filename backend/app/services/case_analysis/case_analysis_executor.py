from __future__ import annotations

import json
import logging
from collections.abc import Mapping

import httpx
from pydantic import ValidationError

from app.config import settings
from app.services.case_analysis.case_analysis_prompt_builder import (
    AnalysisInputMode, CaseAnalysisFailure, _TASK_PROMPTS, _validate_analysis_request,
    build_case_analysis_prompt,
)
from app.services.case_analysis.case_analysis_prompt_config import (
    _ANALYSIS_TRACE_OUTPUT_PROMPT,
    _CASE_ANALYSIS_TRUST_PROMPT,
    _PERSONALIZED_RESPONSE_PROMPT,
)
from app.services.case_analysis.contracts import (
    AnalysisMode, AnalysisTraceFailureMetadata, CaseAnalysisResult, ProviderCaseAnalysis,
)
from app.services.case_analysis.validation import (
    AnalysisTraceProvenanceError, AnalysisTraceStructureError, detect_forbidden_provenance, validate_analysis_trace,
)
from app.services.llm.structured_output_request_router import structured_output_request_options
from app.services.llm.structured_output_router import structured_output_schema
from app.services.case_analysis.case_analysis_response_utils import (
    _extract_visible_text,
    _log_response_shape,
)
from app.services.case_analysis.personalization import resolve_response_language

logger = logging.getLogger("app.case_analysis")

class MainCaseAnalysisService:
    """Run internal analysis without retrieval, persistence, or state mutation."""

    def __init__(self, *, client: httpx.AsyncClient | None = None) -> None:
        self._client = client

    async def analyze(
        self,
        *,
        mode: AnalysisMode,
        case_narrative: dict[str, object] | str | None = None,
        case_evidence: dict[str, object] | str | None = None,
        case_state_json: dict[str, object] | None = None,
        raw_case_narrative: str | None = None,
        analysis_input_mode: AnalysisInputMode | str | None = None,
        analysis_context: dict[str, object],
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
            case_narrative=case_narrative,
            case_evidence=case_evidence,
            case_state_json=case_state_json,
            raw_case_narrative=raw_case_narrative,
            analysis_input_mode=analysis_input_mode,
            analysis_context=analysis_context,
            question=validated_question,
            response_language=response_language,
        )
        from app.services.case_analysis import service as compatibility_service

        target = compatibility_service.resolve_core_llm_target(settings.chat_ask_model)
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
                        ProviderCaseAnalysis,
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

        membership_state = case_state_json
        if membership_state is None and isinstance(case_narrative, dict):
            membership_state = case_narrative
        if membership_state is None and isinstance(case_evidence, dict):
            membership_state = case_evidence
        if membership_state is None:
            raise CaseAnalysisFailure(
                "analysis_context_missing",
                "Analysis Trace validation requires the bound Case State",
            )
        return self._parse_response(
            response,
            case_state_json=membership_state,
            analysis_context=analysis_context,
            analysis_mode=validated_mode,
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

    @staticmethod
    def _parse_response(
        response: httpx.Response,
        *,
        case_state_json: Mapping[str, object],
        analysis_context: Mapping[str, object],
        analysis_mode: AnalysisMode,
    ) -> CaseAnalysisResult:
        if not 200 <= response.status_code < 300:
            raise CaseAnalysisFailure(
                "analysis_provider_error",
                "The post-answer analysis provider returned an error",
            )
        try:
            response_payload = response.json()
        except (TypeError, ValueError) as exc:
            raise CaseAnalysisFailure(
                "analysis_invalid_response",
                "The post-answer analysis provider response was invalid",
            ) from exc
        if not isinstance(response_payload, dict):
            raise CaseAnalysisFailure(
                "analysis_invalid_response",
                "The post-answer analysis provider response was invalid",
            )
        _log_response_shape(response.status_code, response_payload)
        if isinstance(response_payload.get("error"), dict):
            raise CaseAnalysisFailure(
                "analysis_provider_error",
                "The post-answer analysis provider returned an error",
            )
        if response_payload.get("stop_reason") in {
            "refusal",
            "max_tokens",
            "length",
            "pause_turn",
        }:
            raise CaseAnalysisFailure(
                "analysis_incomplete",
                "The post-answer analysis provider did not complete",
            )
        content = response_payload.get("content")
        if content is not None and not isinstance(content, (list, str)):
            raise CaseAnalysisFailure(
                "analysis_invalid_response",
                "The post-answer analysis provider response was invalid",
            )
        raw_text = _extract_visible_text(response_payload).strip()
        if not raw_text:
            raise CaseAnalysisFailure(
                "analysis_invalid_response",
                "The post-answer analysis provider returned no answer",
            )
        try:
            raw_analysis = json.loads(raw_text)
        except (TypeError, ValueError) as exc:
            raise CaseAnalysisFailure(
                "analysis_invalid_response",
                "The post-answer analysis provider did not return structured JSON",
            ) from exc
        if not isinstance(raw_analysis, dict):
            raise CaseAnalysisFailure(
                "analysis_invalid_response",
                "The post-answer structured analysis must be an object",
            )
        raw_answer = raw_analysis.get("answer")
        if not isinstance(raw_answer, str) or not raw_answer.strip():
            raise CaseAnalysisFailure(
                "analysis_invalid_response",
                "The post-answer structured analysis returned no safe prose",
            )
        try:
            detect_forbidden_provenance(raw_analysis)
        except AnalysisTraceProvenanceError as exc:
            raise CaseAnalysisFailure(exc.code, str(exc)) from exc
        try:
            parsed = ProviderCaseAnalysis.model_validate(raw_analysis)
        except ValidationError as exc:
            logger.warning("Case analysis trace validation failed: %s | keys: %s", exc, list(raw_analysis.keys()) if isinstance(raw_analysis, dict) else type(raw_analysis))
            failure_code = (
                "analysis_trace_version_unsupported"
                if raw_analysis.get("version") != "analysis_trace_v1"
                else "analysis_trace_structure_invalid"
            )
            return CaseAnalysisResult(
                answer=raw_answer.strip(),
                trace=None,
                trace_failure=AnalysisTraceFailureMetadata(
                    failure_code=failure_code,
                ),
            )
        try:
            trace = validate_analysis_trace(
                parsed,
                case_state_json=case_state_json,
                mitre_table=analysis_context.get("mitre_table", []),
                analysis_mode=analysis_mode,
            )
        except AnalysisTraceStructureError as exc:
            logger.warning("Case analysis trace structure error: %s (code=%s)", exc, exc.code)
            return CaseAnalysisResult(
                answer=parsed.answer,
                trace=None,
                trace_failure=AnalysisTraceFailureMetadata(
                    failure_code=exc.code,
                ),
            )
        except AnalysisTraceProvenanceError as exc:
            logger.warning("Case analysis trace provenance error: %s (code=%s)", exc, exc.code)
            raise CaseAnalysisFailure(exc.code, str(exc)) from exc
        return CaseAnalysisResult(answer=parsed.answer, trace=trace)
