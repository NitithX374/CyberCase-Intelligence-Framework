from __future__ import annotations;

import httpx

from app.services.case_analysis.case_analysis_prompt_builder import _validate_analysis_request
from app.services.case_analysis.case_analysis_prompt_config import (
    AnalysisInputMode,
    AnalysisMode,
    CaseAnalysisFailure,
)
from app.services.case_analysis.case_analysis_executor import MainCaseAnalysisService
from app.services.case_analysis.case_analysis_response_utils import _extract_visible_text
from app.services.case_analysis.contracts import CaseAnalysisResult

async def request_case_analysis(
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
    client: httpx.AsyncClient | None = None,
) -> CaseAnalysisResult:
    """Call the default internal Main Case Analysis service."""

    validated_mode, validated_question = _validate_analysis_request(
        mode,
        question,
    )
    return await MainCaseAnalysisService(client=client).analyze(
        mode=validated_mode,
        case_narrative=case_narrative,
        case_evidence=case_evidence,
        case_state_json=case_state_json,
        raw_case_narrative=raw_case_narrative,
        analysis_input_mode=analysis_input_mode,
        analysis_context=analysis_context,
        question=validated_question,
        user_message=user_message,
    )
