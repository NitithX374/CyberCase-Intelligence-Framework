from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case
from app.models.case_run import CaseAnalysisResult as PersistedAnalysisResult, CaseRun
from app.models.chat import ChatMessage
from app.models.rag_context import RagContext
from app.schemas.message_metadata import serialize_message_metadata
from app.services.case_analysis.contracts import (
    CaseAnalysisGap,
    CaseAnalysisFailure,
    CaseAnalysisOutput as AnalysisOutput,
    CaseAnalysisTrace,
)
from app.services.case_analysis.validation import validate_case_trace
from app.services.case_materials import CaseSourceBundle, load_case_source_bundle


class CaseRunCompletionError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def technical_augmentation(output: AnalysisOutput) -> dict[str, object] | None:
    receipt = output.execution_receipt
    value = receipt.get("technical_augmentation") if isinstance(receipt, dict) else None
    return value if isinstance(value, dict) else None


def mitre_table_from_output(output: AnalysisOutput) -> list[dict[str, object]]:
    value = (technical_augmentation(output) or {}).get("mitre_table", [])
    return [dict(item) for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def build_clarification_metadata(
    output: AnalysisOutput,
    trace: CaseAnalysisTrace,
) -> dict[str, object]:
    metadata = deepcopy(output.followup_metadata or {})
    if not metadata.get("gap_id") or not metadata.get("topic") or not metadata.get("gap_key"):
        gap = next((item for item in trace.gaps if item.askable), None)
        if gap is not None:
            metadata.setdefault("gap_id", gap.gap_id)
            metadata.setdefault("topic", gap.topic)
            metadata.setdefault("gap_key", f"{gap.gap_id}:{gap.topic.strip().lower()}")
    return metadata


def build_selected_gap_detail(
    clarification_topic: str,
    gap: CaseAnalysisGap | None,
    existing_detail: dict[str, object] | None = None,
) -> dict[str, object]:
    existing = existing_detail or {}
    topic = str(existing.get("topic") or (gap.topic if gap else clarification_topic)).strip()
    gap_status = str(existing.get("status") or (gap.status if gap else "NOT_PROVIDED"))
    if gap_status not in {"NOT_PROVIDED", "EXPLICITLY_UNKNOWN", "AMBIGUOUS", "CONFLICTING"}:
        gap_status = "NOT_PROVIDED"
    description = str(
        existing.get("description")
        or (gap.description if gap else f"Additional investigative information is required for {topic}.")
    ).strip()
    reason = str(
        existing.get("reason")
        or (gap.reason if gap else f"Clarifying {topic.lower()} is required to substantiate findings.")
    ).strip()

    raw_affects = str(existing.get("affects") or "").strip()
    if raw_affects and raw_affects != "case-level context" and not raw_affects.startswith("A-"):
        affects = raw_affects
    elif gap and gap.affected_claim_ids:
        affects = f"Clarifying {topic.lower()} addresses missing investigative evidence for: {', '.join(gap.affected_claim_ids)}."
    elif raw_affects:
        affects = f"Clarifying {topic.lower()} addresses missing investigative evidence for: {raw_affects}."
    else:
        affects = f"Clarifying this information helps establish facts and complete the case analysis for {topic.lower()}."

    priority = str(existing.get("priority") or (gap.priority if gap else "high")).lower()
    if priority not in {"high", "medium", "low"}:
        priority = "high"

    askable = bool(existing.get("askable", gap.askable if gap else True))

    return {
        "topic": topic,
        "status": gap_status,
        "description": description,
        "affects": affects,
        "reason": reason,
        "priority": priority,
        "askable": askable,
    }


def build_followup_message_metadata(
    *,
    clarification_topic: str,
    gap_id: str,
    gap_key: str,
    thread_ordinal: int,
    trace: CaseAnalysisTrace,
    existing_followup: dict[str, object] | None = None,
) -> dict[str, object]:
    gap = next(
        (
            item for item in trace.gaps
            if item.gap_id == gap_id or item.topic.strip().lower() == clarification_topic.strip().lower()
        ),
        next((item for item in trace.gaps if item.askable), None),
    )
    existing_detail = existing_followup.get("selected_gap_detail") if isinstance(existing_followup, dict) else None
    existing_detail_dict = existing_detail if isinstance(existing_detail, dict) else None
    selected_gap_detail = build_selected_gap_detail(clarification_topic, gap, existing_detail_dict)
    topic = str(selected_gap_detail["topic"])

    chat_followup: dict[str, object] = {
        "root_ordinal": thread_ordinal,
        "round": 1,
        "gap_id": gap_id,
        "gap_key": gap_key,
        "topic": topic,
        "selected_gap_detail": selected_gap_detail,
    }

    return {
        "action": "follow_up",
        "chat_followup": chat_followup,
    }


async def complete_case_run(
    db: AsyncSession,
    run_id: UUID,
    claimed_attempt: int,
    output: AnalysisOutput,
) -> bool:
    now = datetime.now(timezone.utc)
    async with db.begin():
        run_case = await db.scalar(select(CaseRun.case_id).where(CaseRun.id == run_id))
        if run_case is None:
            return False
        case = await db.scalar(select(Case).where(Case.id == run_case).with_for_update())
        if case is None:
            return False
        run = await db.scalar(select(CaseRun).where(CaseRun.id == run_id).with_for_update())
        if not owns_run(run, case.id, claimed_attempt):
            return False

        if run.evidence_revision != case.evidence_revision:
            await mark_superseded(run, now)
            return False
        source_bundle = await load_case_source_bundle(db, case_id=case.id, user_id=None)
        trace = validated_output(output, source_bundle)
        if run.evidence_revision != case.evidence_revision:
            await mark_superseded(run, now)
            return False
        augmentation = technical_augmentation(output)
        completion = await db.execute(
            update(CaseRun)
            .where(
                CaseRun.id == run_id,
                CaseRun.status == "running",
                CaseRun.attempt_count == claimed_attempt,
            )
            .values(
                status="completed",
                error_code=None,
                error_message=None,
                finished_at=now,
                updated_at=now,
            )
            .returning(CaseRun.id)
        )
        if completion.scalar_one_or_none() is None:
            return False
        provider_metadata = {
            "source_reference_type": "case_source",
            "evidence_revision": run.evidence_revision,
        }
        if augmentation is not None:
            provider_metadata.update(
                {
                    "mitre_table": deepcopy(augmentation.get("mitre_table", [])),
                    "technical_augmentation": deepcopy(augmentation),
                }
            )
        if output.followup_question:
            provider_metadata["followup_question"] = output.followup_question.strip()
            if output.followup_metadata:
                provider_metadata["followup_metadata"] = deepcopy(output.followup_metadata)
        result = PersistedAnalysisResult(
            case_id=case.id,
            run_id=run.id,
            evidence_revision=run.evidence_revision,
            schema_version=trace.version,
            status="validated",
            answer=output.answer.strip(),
            summary=trace.summary,
            trace_json=trace.model_dump(mode="json"),
            execution_receipt_json=deepcopy(output.execution_receipt),
            retrieval_context_id=trace.retrieval_context_id,
            pipeline_config=deepcopy(run.pipeline_config),
            provider_metadata_json=provider_metadata,
        )
        db.add(result)
        if augmentation is not None and trace.retrieval_context_id:
            existing_rag = await db.scalar(
                select(RagContext).where(
                    (RagContext.retrieval_context_id == trace.retrieval_context_id)
                    | (RagContext.case_run_id == run.id)
                )
            )
            if existing_rag is None:
                query_str = str(augmentation.get("query", augmentation.get("trigger_text", "")))
                rag_context = RagContext(
                    retrieval_context_id=trace.retrieval_context_id,
                    case_id=case.id,
                    case_run_id=run.id,
                    query_text=query_str,
                    context_text=str(augmentation.get("context", "")),
                    mitre_table=deepcopy(augmentation.get("mitre_table", [])),
                )
                db.add(rag_context)
        await db.flush()

        has_followup = output.followup_question is not None
        if has_followup:
            followup_metadata_raw = output.followup_metadata or {}
            existing_followup = (
                followup_metadata_raw.get("chat_followup")
                if isinstance(followup_metadata_raw, dict)
                else None
            )
            clarification_meta = build_clarification_metadata(output, trace)
            gap_id = str(clarification_meta.get("gap_id") or "G-001")
            topic = str(clarification_meta.get("topic") or "")
            gap_key = str(clarification_meta.get("gap_key") or f"{gap_id}:{topic.lower()}")
            followup_message_id = uuid4()
            next_ordinal = (
                await db.scalar(
                    select(func.coalesce(func.max(ChatMessage.ordinal), 0)).where(
                        ChatMessage.case_id == case.id
                    )
                )
                + 1
            )
            followup_message_meta = build_followup_message_metadata(
                clarification_topic=topic,
                gap_id=gap_id,
                gap_key=gap_key,
                thread_ordinal=next_ordinal,
                trace=trace,
                existing_followup=existing_followup,
            )
            question = ChatMessage(
                id=followup_message_id,
                case_id=case.id,
                ordinal=next_ordinal,
                role="assistant",
                content=output.followup_question.strip(),
                message_kind="followup_question",
                analysis_result_id=result.id,
                metadata_json=serialize_message_metadata(followup_message_meta),
            )
            db.add(question)
            await db.flush()

        case.latest_analysis_result_id = result.id
        case.updated_at = now
        await db.flush()
    return True


async def mark_superseded(
    run: CaseRun,
    finished_at: datetime,
) -> None:
    run.status = "failed"
    run.error_code = "case_run_superseded"
    run.error_message = "Case evidence changed while this run was executing. Retry analysis."
    run.finished_at = finished_at
    run.updated_at = finished_at


def owns_run(run: CaseRun | None, case_id: UUID, claimed_attempt: int) -> bool:
    return bool(
        run is not None
        and run.case_id == case_id
        and run.status == "running"
        and run.attempt_count == claimed_attempt
    )


def validated_output(
    output: AnalysisOutput,
    source_bundle: CaseSourceBundle,
) -> CaseAnalysisTrace:
    trace = output.trace
    if not isinstance(trace, CaseAnalysisTrace):
        raise CaseRunCompletionError("analysis_trace_missing", "Case analysis did not produce a validated trace")
    if not output.answer.strip():
        raise CaseRunCompletionError("analysis_answer_missing", "Case analysis answer is empty")
    try:
        return validate_case_trace(
            trace,
            source_bundle,
            mitre_table=mitre_table_from_output(output),
        )
    except CaseAnalysisFailure as error:
        raise CaseRunCompletionError(error.code, error.message) from error


__all__ = [
    "CaseRunCompletionError",
    "build_clarification_metadata",
    "build_followup_message_metadata",
    "complete_case_run",
    "mitre_table_from_output",
    "technical_augmentation",
]
