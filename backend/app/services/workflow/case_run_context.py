from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from dataclasses import replace

from sqlalchemy import select

from app.models.rag_context import RagContext
from app.services.case_materials import build_rag_query
from app.services.workflow.case_mitre_augmentation import (
    CaseRagContextPayload,
    merge_case_mitre_trace,
    run_case_mitre_augmentation,
)
from app.services.workflow.case_run_service import ClaimedCaseRun


class CaseRunExecutionError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


async def attach_case_augmentation(
    output,
    claimed: ClaimedCaseRun,
    applicability_gate,
    rag_request,
    session_factory: Callable | None = None,
):
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
                        query_text=build_rag_query(claimed.source_bundle),
                        context_text=str(rag_payload.context),
                        mitre_table=list(rag_payload.mitre_table),
                    )
                )

    augmentation = await run_case_mitre_augmentation(
        run_id=claimed.id,
        source_bundle=claimed.source_bundle,
        applicability_gate=applicability_gate,
        rag_request=rag_request,
        on_rag_validated=persist_rag_context,
        reused_context=existing_rag_context,
    )
    merged_trace = merge_case_mitre_trace(
        output.trace,
        augmentation,
        claimed.source_bundle,
    )
    receipt = deepcopy(output.execution_receipt or {})
    receipt["technical_augmentation"] = augmentation.to_metadata()
    return replace(output, trace=merged_trace, execution_receipt=receipt)


__all__ = ["CaseRunExecutionError", "attach_case_augmentation"]
