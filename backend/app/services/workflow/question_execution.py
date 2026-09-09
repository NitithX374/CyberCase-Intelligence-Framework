from app.services.case_analysis.case_analysis_prompt_config import CaseAnalysisFailure
from app.services.workflow.analysis_pipeline_context import (
    bind_pipeline_outcome,
    coerce_analysis_result,
)
from app.services.workflow.outcome import AssistantOutcome, question_outcome


async def _run_question(claimed, analysis_request) -> AssistantOutcome:
    if claimed.analysis_context is None:
        raise CaseAnalysisFailure(
            "analysis_context_missing",
            "No completed analytical context is available for ASK",
        )
    context = dict(claimed.analysis_context)
    context["source_message_ids"] = [str(value) for value in claimed.source_message_ids]
    context["_source_text_by_message_id"] = {
        str(source.message_id): source.content for source in claimed.evidence_sources
    }
    if claimed.document_source_context:
        context["document_source_context"] = list(claimed.document_source_context)
    result = coerce_analysis_result(
        await analysis_request(
            mode="question_answer",
            raw_evidence=claimed.raw_evidence,
            analysis_context=context,
            question=claimed.content,
            user_message=claimed.content,
        )
    )
    outcome = question_outcome(
        result.answer,
        analysis_context=context,
        evidence_sha256=claimed.evidence_sha256,
        source_message_ids=claimed.source_message_ids,
        trace=result.trace,
        trace_failure=result.trace_failure,
    )

    return bind_pipeline_outcome(outcome, result, {"pipeline": "raw_direct"})
