import httpx

from app.services.case_analysis.case_analysis_executor import MainCaseAnalysisService
from app.services.case_analysis.case_analysis_prompt_builder import (
    _validate_analysis_request,
    build_analysis_prompt,
    build_case_analysis_prompt,
)
from app.services.case_analysis.case_analysis_prompt_config import (
    CASE_ANALYSIS_PROMPT_VERSION,
    CaseAnalysisFailure,
)
from app.services.case_analysis.contracts import AnalysisMode, CaseAnalysisResult
from app.services.llm.core_llm import resolve_core_llm_target


async def request_case_analysis(
    *,
    mode: AnalysisMode,
    raw_evidence: str,
    analysis_context: dict[str, object],
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


__all__ = [
    "AnalysisMode",
    "CASE_ANALYSIS_PROMPT_VERSION",
    "CaseAnalysisFailure",
    "MainCaseAnalysisService",
    "build_analysis_prompt",
    "build_case_analysis_prompt",
    "request_case_analysis",
    "resolve_core_llm_target",
]
