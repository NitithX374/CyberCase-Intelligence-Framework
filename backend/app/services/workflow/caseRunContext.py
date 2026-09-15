from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from dataclasses import replace

from sqlalchemy import select

from app.models.ragContext import RagContext
from app.services.case_analysis.contracts import build_case_source_registry
from app.services.case_analysis.pipelineConfig import read_pipeline
from app.services.workflow.caseMitreAugmentation import (
    CaseRagContextPayload,
    merge_case_mitre_trace,
    run_case_mitre_augmentation,
)
from app.services.workflow.caseRunService import ClaimedCaseRun


class CaseRunExecutionError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def build_analysis_context(claimed: ClaimedCaseRun) -> dict[str, object]:
    document_context = []
    for entry in claimed.manifest:
        provenance = entry.get("provenance")
        if not isinstance(provenance, dict):
            continue
        document_id = entry.get("document_id")
        filename = entry.get("filename")
        pages = provenance.get("pages")
        if not isinstance(document_id, str) or not isinstance(filename, str) or not isinstance(pages, list):
            continue
        document_entry = {
            "document_id": document_id,
            "filename": filename,
            "page_spans": pages,
        }
        for quality_key in (
            "extraction_method",
            "provider",
            "verification_status",
            "confidence_status",
            "minimum_confidence",
            "warnings",
        ):
            if quality_key in provenance:
                document_entry[quality_key] = provenance[quality_key]
        document_context.append(
            {
                "source_id": str(entry["source_id"]),
                "documents": [document_entry],
            }
        )
    return {
        "source_ids": list(claimed.source_ids),
        "source_reference_type": "case_evidence_source",
        "_source_text_by_source_id": dict(claimed.source_text_by_id),
        "document_source_context": document_context,
        "_analysis_pipeline": dict(claimed.pipeline_config),
    }


async def attach_case_augmentation(
    output,
    claimed: ClaimedCaseRun,
    applicability_gate,
    rag_request,
    mapping_request,
    session_factory: Callable | None = None,
):
    context = build_analysis_context(claimed)
    config = read_pipeline(claimed.pipeline_config)
    calls = output.execution_receipt.get("calls", []) if isinstance(output.execution_receipt, dict) else []
    if not isinstance(calls, list):
        raise CaseRunExecutionError("analysis_receipt_invalid", "Case analysis receipt calls are invalid")

    existing_rag_context: CaseRagContextPayload | None = None
    if session_factory is not None:
        async with session_factory() as db:
            existing_row = await db.scalar(
                select(RagContext).where(RagContext.case_run_id == claimed.id)
            )
            if existing_row is not None:
                existing_rag_context = CaseRagContextPayload(
                    retrieval_context_id=existing_row.retrieval_context_id,
                    context=existing_row.context_text,
                    mitre_table=tuple(existing_row.mitre_table or []),
                )

    async def persist_rag_context(rag_payload: CaseRagContextPayload) -> None:
        if session_factory is None:
            return
        async with session_factory() as db, db.begin():
            existing = await db.scalar(
                select(RagContext).where(
                    (RagContext.case_run_id == claimed.id)
                    | (RagContext.retrieval_context_id == rag_payload.retrieval_context_id)
                )
            )
            if existing is None:
                db.add(
                    RagContext(
                        retrieval_context_id=rag_payload.retrieval_context_id,
                        case_id=claimed.case_id,
                        case_run_id=claimed.id,
                        query_text=claimed.input_text,
                        context_text=str(rag_payload.context),
                        mitre_table=list(rag_payload.mitre_table),
                    )
                )

    augmentation = await run_case_mitre_augmentation(
        run_id=claimed.id,
        input_text=claimed.input_text,
        manifest=claimed.manifest,
        base_trace=output.trace,
        config=config,
        applicability_gate=applicability_gate,
        rag_request=rag_request,
        mapping_request=mapping_request,
        calls=calls,
        on_rag_validated=persist_rag_context,
        reused_context=existing_rag_context,
    )
    merged_trace = merge_case_mitre_trace(
        output.trace,
        augmentation,
        build_case_source_registry(context),
        context.get("document_source_context", []),
    )
    receipt = deepcopy(output.execution_receipt or {})
    receipt["technical_augmentation"] = augmentation.to_metadata()
    return replace(output, trace=merged_trace, execution_receipt=receipt)


__all__ = ["attach_case_augmentation", "build_analysis_context"]
