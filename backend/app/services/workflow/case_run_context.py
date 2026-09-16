from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from dataclasses import replace
from uuid import UUID

from sqlalchemy import select

from app.models.rag_context import RagContext
from app.services.case_analysis.contracts import CaseAnalysisTrace
from app.services.case_materials import build_rag_query
from app.services.workflow.case_mitre_augmentation import (
    CaseMitreAugmentation,
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


async def load_existing_rag_context(
    session_factory: Callable | None,
    case_run_id: UUID,
) -> CaseRagContextPayload | None:
    if session_factory is None:
        return None
    async with session_factory() as db:
        existing_row = await db.scalar(
            select(RagContext).where(RagContext.case_run_id == case_run_id)
        )
        if existing_row is None:
            return None
        return CaseRagContextPayload(
            retrieval_context_id=existing_row.retrieval_context_id,
            context=existing_row.context_text,
            mitre_table=tuple(existing_row.mitre_table or []),
        )


async def persist_case_rag_context(
    session_factory: Callable | None,
    claimed: ClaimedCaseRun,
    rag_payload: CaseRagContextPayload,
    query_text: str | None = None,
) -> None:
    if session_factory is None:
        return
    effective_query = (
        query_text.strip()
        if isinstance(query_text, str) and query_text.strip()
        else build_rag_query(claimed.source_bundle)
    )
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
                    query_text=effective_query,
                    context_text=str(rag_payload.context),
                    mitre_table=list(rag_payload.mitre_table),
                )
            )


async def resolve_case_technical_context(
    claimed: ClaimedCaseRun,
    applicability_gate,
    rag_request,
    session_factory: Callable | None = None,
) -> CaseMitreAugmentation:
    existing_rag_context = await load_existing_rag_context(
        session_factory,
        claimed.id,
    )

    async def on_rag_validated(
        rag_payload: CaseRagContextPayload,
        query_text: str | None = None,
    ) -> None:
        await persist_case_rag_context(
            session_factory,
            claimed,
            rag_payload,
            query_text,
        )

    return await run_case_mitre_augmentation(
        run_id=claimed.id,
        source_bundle=claimed.source_bundle,
        applicability_gate=applicability_gate,
        rag_request=rag_request,
        on_rag_validated=on_rag_validated if session_factory is not None else None,
        reused_context=existing_rag_context,
    )


def attach_case_augmentation_receipt(
    output,
    augmentation: CaseMitreAugmentation | None,
):
    if augmentation is None:
        return output
    associations = (
        tuple(output.trace.mitre_associations)
        if isinstance(output.trace, CaseAnalysisTrace)
        else ()
    )
    status = augmentation.status
    if status == "retrieved_from_rag" and associations:
        status = "retrieved_with_matches"
    resolved_augmentation = replace(
        augmentation,
        associations=associations,
        status=status,
    )
    receipt = deepcopy(output.execution_receipt or {})
    receipt["technical_augmentation"] = resolved_augmentation.to_metadata()
    return replace(output, execution_receipt=receipt)


async def attach_case_augmentation(
    output,
    claimed: ClaimedCaseRun,
    applicability_gate,
    rag_request,
    session_factory: Callable | None = None,
):
    augmentation = await resolve_case_technical_context(
        claimed,
        applicability_gate,
        rag_request,
        session_factory=session_factory,
    )
    merged_trace = merge_case_mitre_trace(
        output.trace,
        augmentation,
        claimed.source_bundle,
    )
    updated = replace(output, trace=merged_trace)
    return attach_case_augmentation_receipt(updated, augmentation)


__all__ = [
    "CaseRunExecutionError",
    "attach_case_augmentation",
    "attach_case_augmentation_receipt",
    "resolve_case_technical_context",
]
