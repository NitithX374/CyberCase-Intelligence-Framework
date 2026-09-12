from __future__ import annotations

import hashlib
from copy import deepcopy
from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case
from app.models.caseMaterials import CaseEvidenceSnapshot
from app.models.caseRun import CaseAnalysisResult as PersistedAnalysisResult, CaseRun
from app.models.chat import ChatMessage, ChatThread
from app.models.ragContext import RagContext
from app.schemas.messageMetadata import serialize_message_metadata
from app.services.case_analysis.contracts import (
    CaseAdmittedSource,
    CaseAnalysisFailure,
    CaseAnalysisGap,
    CaseAnalysisResult as AnalysisOutput,
    CaseAnalysisTrace,
)
from app.services.case_analysis.validation import validate_case_trace
from app.services.followup.caseClarification import supersede_prior_clarifications


def trace_source_ids(trace: CaseAnalysisTrace) -> list[str]:
    ids: list[str] = []
    for claim in trace.claims:
        ids.extend(claim.supporting_source_ids)
        ids.extend(claim.contradicting_source_ids)
    return list(dict.fromkeys(ids))


def technical_augmentation(output: AnalysisOutput) -> dict[str, object] | None:
    receipt = output.execution_receipt
    value = receipt.get("technical_augmentation") if isinstance(receipt, dict) else None
    return value if isinstance(value, dict) else None


def mitre_table_from_output(output: AnalysisOutput) -> list[dict[str, object]]:
    value = (technical_augmentation(output) or {}).get("mitre_table", [])
    return [dict(item) for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def rag_invoked(augmentation: dict[str, object]) -> bool:
    applicability = augmentation.get("applicability")
    return isinstance(applicability, dict) and applicability.get("decision") == "RETRIEVE"


def rag_attempt(augmentation: dict[str, object]) -> dict[str, object]:
    status = augmentation.get("status")
    failure_code = augmentation.get("failure_code")
    status_map = {
        "not_applicable": "no_applicable_context",
        "insufficient_context": "no_applicable_context",
        "retrieved_without_supported_match": "no_applicable_context",
        "retrieved_with_matches": "used",
        "failed": "unavailable",
    }
    metadata: dict[str, object] = {
        "status": status_map.get(status, "no_applicable_context"),
    }
    if isinstance(failure_code, str):
        metadata["failure_code"] = failure_code
    return metadata


def augmentation_message_metadata(
    augmentation: dict[str, object],
    is_present: bool,
) -> dict[str, object]:
    if not is_present:
        return {}
    return {
        "mitre_table": deepcopy(augmentation.get("mitre_table", [])),
        "mitre_applicability": deepcopy(augmentation.get("applicability", {})),
        "rag_attempt": rag_attempt(augmentation),
        "technical_augmentation": deepcopy(augmentation),
    }


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
    status = str(existing.get("status") or (gap.status if gap else "NOT_PROVIDED"))
    if status not in {"NOT_PROVIDED", "EXPLICITLY_UNKNOWN", "AMBIGUOUS", "CONFLICTING"}:
        status = "NOT_PROVIDED"
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
        "status": status,
        "description": description,
        "affects": affects,
        "reason": reason,
        "priority": priority,
        "askable": askable,
    }


def build_followup_message_metadata(
    *,
    result_id: UUID,
    clarification_id: UUID,
    snapshot_id: UUID,
    clarification_topic: str,
    gap_id: str,
    gap_key: str,
    thread_ordinal: int,
    augmentation_payload: dict[str, object],
    is_augmentation_present: bool,
    run_pipeline_config: dict[str, object],
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

    chat_followup: dict[str, object] = {
        "kind": "clarification",
        "action": "ask_followup",
        "root_ordinal": thread_ordinal,
        "round": 1,
        "selected_gap_detail": selected_gap_detail,
    }
    if isinstance(existing_followup, dict):
        for key in ("policy_version", "prompt_version", "provider", "model", "decision", "reason_code", "stop_reason"):
            if key in existing_followup:
                chat_followup[key] = existing_followup[key]

    return {
        "analysis_kind": "clarification_question",
        "analysis_result_id": str(result_id),
        "clarification_id": str(clarification_id),
        "evidence_snapshot_id": str(snapshot_id),
        "gap_id": gap_id,
        "gap_key": gap_key,
        "chat_followup": chat_followup,
        **augmentation_message_metadata(augmentation_payload, is_augmentation_present),
        "chat_action": {
            "action": "initial_analysis",
            "route": "analysis",
            "rag_invoked": rag_invoked(augmentation_payload),
            "retrieval_context_reused": False,
            "analysis_mode": "case_overview",
            "prompt_version": run_pipeline_config.get("version", "main_case_analysis_v1"),
        },
    }


class CaseRunCompletionError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


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
        if not _owns_run(run, case.id, claimed_attempt):
            return False
        snapshot = await db.get(CaseEvidenceSnapshot, run.snapshot_id)
        if snapshot is None or snapshot.case_id != case.id:
            raise CaseRunCompletionError("case_snapshot_missing", "Pinned Case evidence snapshot is missing")
        trace = _validated_output(output, snapshot)
        augmentation = technical_augmentation(output)
        augmentation_payload = augmentation or {}
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
                lease_owner=None,
                lease_expires_at=None,
                updated_at=now,
            )
            .returning(CaseRun.id)
        )
        if completion.scalar_one_or_none() is None:
            return False
        provider_metadata = {
            "source_reference_type": "case_evidence_source",
            "snapshot_id": str(run.snapshot_id),
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
            snapshot_id=run.snapshot_id,
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
                    evidence_snapshot_id=run.snapshot_id,
                    query_text=query_str,
                    query_sha256=hashlib.sha256(query_str.encode("utf-8")).hexdigest(),
                    context_text=str(augmentation.get("context", "")),
                    mitre_table=deepcopy(augmentation.get("mitre_table", [])),
                )
                db.add(rag_context)
        await db.flush()

        has_followup = output.followup_question is not None
        thread = await db.scalar(select(ChatThread).where(ChatThread.case_id == case.id).with_for_update())
        if has_followup:
            if thread is None:
                thread = ChatThread(case_id=case.id, title=case.title, user_id=case.user_id)
                db.add(thread)
                await db.flush()
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
            followup_message_meta = build_followup_message_metadata(
                result_id=result.id,
                clarification_id=followup_message_id,
                snapshot_id=run.snapshot_id,
                clarification_topic=topic,
                gap_id=gap_id,
                gap_key=gap_key,
                thread_ordinal=thread.next_message_ordinal,
                augmentation_payload=augmentation_payload,
                is_augmentation_present=augmentation is not None,
                run_pipeline_config=run.pipeline_config,
                trace=trace,
                existing_followup=existing_followup,
            )
            question = ChatMessage(
                id=followup_message_id,
                thread_id=thread.id,
                ordinal=thread.next_message_ordinal,
                role="assistant",
                content=output.followup_question.strip(),
                message_kind="followup_question",
                analysis_result_id=result.id,
                metadata_json=serialize_message_metadata(followup_message_meta),
            )
            db.add(question)
            await db.flush()
            thread.next_message_ordinal += 1

        await supersede_prior_clarifications(
            db,
            case_id=case.id,
            result_id=result.id,
        )
        if thread is not None:
            thread.status = "awaiting_followup" if has_followup else "answered"
            thread.updated_at = now
        case.latest_analysis_result_id = result.id
        case.updated_at = now
        await db.flush()
    return True


def _owns_run(run: CaseRun | None, case_id: UUID, claimed_attempt: int) -> bool:
    return bool(
        run is not None
        and run.case_id == case_id
        and run.status == "running"
        and run.attempt_count == claimed_attempt
    )


def _validated_output(
    output: AnalysisOutput,
    snapshot: CaseEvidenceSnapshot,
) -> CaseAnalysisTrace:
    trace = output.trace
    if not isinstance(trace, CaseAnalysisTrace):
        raise CaseRunCompletionError("analysis_trace_missing", "Case analysis did not produce a validated trace")
    if not output.answer.strip():
        raise CaseRunCompletionError("analysis_answer_missing", "Case analysis answer is empty")
    if trace.evidence_sha256 != snapshot.text_sha256:
        raise CaseRunCompletionError("analysis_trace_invalid", "Analysis trace is not bound to the pinned evidence snapshot")
    try:
        return validate_case_trace(
            trace,
            _snapshot_sources(snapshot),
            _snapshot_document_context(snapshot),
            mitre_table=mitre_table_from_output(output),
        )
    except CaseAnalysisFailure as error:
        raise CaseRunCompletionError(error.code, error.message) from error


def _snapshot_sources(snapshot: CaseEvidenceSnapshot) -> tuple[CaseAdmittedSource, ...]:
    if not isinstance(snapshot.manifest_json, list):
        raise CaseRunCompletionError("case_snapshot_invalid", "Pinned Case snapshot manifest is invalid")
    sources: list[CaseAdmittedSource] = []
    for entry in snapshot.manifest_json:
        if not isinstance(entry, dict):
            raise CaseRunCompletionError("case_snapshot_invalid", "Pinned Case snapshot source entry is invalid")
        source_id = entry.get("source_id")
        revision = entry.get("revision")
        content = entry.get("exact_text")
        text_sha256 = entry.get("text_sha256")
        if not isinstance(source_id, str) or not isinstance(revision, int) or not isinstance(content, str) or not isinstance(text_sha256, str):
            raise CaseRunCompletionError("case_snapshot_invalid", "Pinned Case snapshot source reference is incomplete")
        if hashlib.sha256(content.encode("utf-8")).hexdigest() != text_sha256:
            raise CaseRunCompletionError("case_snapshot_invalid", "Pinned Case snapshot source hash is invalid")
        sources.append(CaseAdmittedSource(source_id, revision, content, text_sha256))
    return tuple(sources)


def _snapshot_document_context(snapshot: CaseEvidenceSnapshot) -> list[dict[str, object]]:
    context: list[dict[str, object]] = []
    for entry in snapshot.manifest_json:
        if not isinstance(entry, dict):
            continue
        provenance = entry.get("provenance")
        if not isinstance(provenance, dict):
            continue
        document_id = entry.get("document_id")
        filename = entry.get("filename")
        pages = provenance.get("pages")
        if isinstance(document_id, str) and isinstance(filename, str) and isinstance(pages, list):
            context.append(
                {
                    "source_id": entry.get("source_id"),
                    "documents": [{"document_id": document_id, "filename": filename, "page_spans": pages}],
                }
            )
    return context


completeCaseRun = complete_case_run

__all__ = ["CaseRunCompletionError", "completeCaseRun", "complete_case_run"]
