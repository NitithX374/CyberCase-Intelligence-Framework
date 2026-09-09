from copy import deepcopy
from dataclasses import replace

from app.services.case_analysis.case_analysis_prompt_config import CaseAnalysisFailure
from app.services.case_analysis.claim_anchored.failure import ClaimAnchoredFailure
from app.services.case_analysis.contracts import CaseAnalysisResult
from app.services.case_analysis.mitre_applicability_contracts import (
    MitreApplicabilityRecord,
)
from app.services.case_analysis.pipeline_config import read_pipeline
from app.services.workflow.outcome import AssistantOutcome
from app.services.workflow.rag_routing import (
    RagAttempt,
    attempt_mitre_applicability,
    attempt_optional_rag,
)


async def prepare_analysis_context(claimed, applicability_gate, rag_request):
    config = read_pipeline(getattr(claimed, "analysis_pipeline", None))
    if config.pipeline == "claim_anchored":
        applicability = MitreApplicabilityRecord(
            decision="SKIP", failure_code="technical_augmentation_disabled_phase1"
        )
        attempt = RagAttempt(
            status="unavailable",
            context=None,
            failure_code="technical_augmentation_disabled_phase1",
        )
    else:
        applicability = await attempt_mitre_applicability(claimed, applicability_gate)
        attempt = (
            await attempt_optional_rag(claimed, rag_request)
            if applicability.decision == "RETRIEVE"
            else RagAttempt(status="no_applicable_context", context=None)
        )
    context = attempt.context.to_analysis_context() if attempt.context else {}
    context.update(
        {
            "source_message_ids": [str(value) for value in claimed.source_message_ids],
            "_source_text_by_message_id": {
                str(source.message_id): source.content
                for source in claimed.evidence_sources
            },
        }
    )
    if claimed.document_source_context:
        context["document_source_context"] = list(claimed.document_source_context)
    return config, applicability, attempt, context


def bind_pipeline_outcome(
    outcome: AssistantOutcome,
    result: CaseAnalysisResult,
    configuration: dict[str, object],
) -> AssistantOutcome:
    config = read_pipeline(configuration)
    metadata = deepcopy(outcome.metadata_json)
    metadata["analysis_pipeline"] = {
        "pipeline": config.pipeline,
        "version": config.version,
    }
    if config.pipeline == "claim_anchored":
        metadata["analysis_pipeline"] = config.model_dump(mode="json")
        if result.trace is None or result.execution_receipt is None:
            raise ClaimAnchoredFailure(
                "claim_anchored_trace_missing",
                "Attribute-first requires its trace and receipt",
                result.execution_receipt,
            )
        metadata["analysis_execution"] = deepcopy(result.execution_receipt)
        metadata["technical_augmentation"] = {"status": "disabled_phase1"}
        action = metadata.get("chat_action", {})
        action.update(
            {"analysis_mode": "case_overview", "prompt_version": config.version}
        )
        metadata["chat_action"] = action
    return replace(outcome, metadata_json=metadata)


def coerce_analysis_result(value: object) -> CaseAnalysisResult:
    if isinstance(value, CaseAnalysisResult) and value.answer.strip():
        return value
    if isinstance(value, str) and value.strip():
        return CaseAnalysisResult(answer=value.strip(), trace=None)
    raise CaseAnalysisFailure(
        "analysis_invalid_response",
        "The Main Case Analysis returned no answer",
    )
