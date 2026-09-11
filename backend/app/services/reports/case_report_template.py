from __future__ import annotations

import time

from app.schemas.reports import (
    PRELIMINARY_REPORT_SECTION_HEADINGS,
    ReportClaim,
    ReportSection,
    StructuredReport,
)
from app.services.case_analysis.contracts import CaseAnalysisTrace
from app.services.reports.case_report_contracts import (
    CaseReportInputSnapshot,
    native_source_ids,
)
from app.services.reports.report_contracts import ReportRunResult
from app.services.reports.report_validation import validate_case_structured_report

CASE_REPORT_PROMPT_VERSION = "deterministic_case_evidence_report_v1"


async def run_case_report_generation(snapshot: CaseReportInputSnapshot) -> ReportRunResult:
    started = time.perf_counter()
    try:
        report = build_case_template_report(snapshot)
        trace = CaseAnalysisTrace.model_validate(snapshot.analysis_trace)
        validate_case_structured_report(
            report,
            source_evidence_ids=native_source_ids(snapshot),
            mitre_ids={association.technique_id for association in trace.mitre_associations},
        )
        return ReportRunResult(
            status="completed",
            report=report,
            prompt_version=CASE_REPORT_PROMPT_VERSION,
            provider="deterministic",
            model="case-template",
            latency_ms=round((time.perf_counter() - started) * 1000, 3),
        )
    except Exception as error:
        return ReportRunResult(
            status="failed",
            report=None,
            prompt_version=CASE_REPORT_PROMPT_VERSION,
            provider="deterministic",
            model="case-template",
            validation_errors=(str(error),),
            failure_code="case_report_generation_failed",
            failure_message="The Case report could not be generated from the selected analysis.",
            latency_ms=round((time.perf_counter() - started) * 1000, 3),
        )


def build_case_template_report(
    snapshot: CaseReportInputSnapshot,
) -> StructuredReport:
    trace = NativeCaseAnalysisTrace.model_validate(snapshot.analysis_trace)
    association_by_claim: dict[str, list[str]] = {}
    for association in trace.mitre_associations:
        for claim_id in association.claim_ids:
            association_by_claim.setdefault(claim_id, []).append(association.technique_id)
    source_items = [
        _source_item(source.source_id, source.revision, source.filename, source.exact_text)
        for source in snapshot.sources
    ]
    claims = [
        ReportClaim(
            claim_id=claim.claim_id,
            section_id="case_summary",
            text=claim.text,
            support_type=_support_type(claim.claim_type),
            source_evidence_ids=list(dict.fromkeys(claim.supporting_source_ids + claim.contradicting_source_ids)),
            mitre_technique_ids=list(dict.fromkeys(association_by_claim.get(claim.claim_id, []))),
        )
        for claim in trace.claims
    ]
    mitre_items = _technical_items(snapshot, trace)
    rationale = _technical_rationale(snapshot, trace)
    gaps = snapshot.unresolved_issues or ["ไม่พบข้อขาดหายที่ตรวจพบในผลวิเคราะห์ฉบับนี้"]
    limitations = [
        "รายงานนี้เป็นรายงานสรุปผลการวิเคราะห์เบื้องต้น (Provisional / Unverified)",
        f"Analysis result: {snapshot.analysis_result_id}",
        f"Evidence snapshot: {snapshot.evidence_snapshot_id} (revision {snapshot.evidence_revision})",
        f"Evidence text SHA-256: {snapshot.evidence_sha256}",
        f"Evidence manifest SHA-256: {snapshot.manifest_sha256}",
        "แหล่งอ้างอิงของรายงานใช้ Case evidence source/revision โดยตรง ไม่ใช้รหัสข้อความสนทนาแทนหลักฐาน",
        *_technical_limitations(snapshot),
    ]
    sections = [
        ReportSection(
            section_id="case_summary",
            heading=PRELIMINARY_REPORT_SECTION_HEADINGS["case_summary"],
            paragraphs=[snapshot.analysis_summary, snapshot.analysis_answer],
        ),
        ReportSection(
            section_id="indicators_found",
            heading=PRELIMINARY_REPORT_SECTION_HEADINGS["indicators_found"],
            items=source_items,
        ),
        ReportSection(
            section_id="mitre_attack_mapping",
            heading=PRELIMINARY_REPORT_SECTION_HEADINGS["mitre_attack_mapping"],
            items=mitre_items,
        ),
        ReportSection(
            section_id="mapping_rationale",
            heading=PRELIMINARY_REPORT_SECTION_HEADINGS["mapping_rationale"],
            items=rationale,
        ),
        ReportSection(
            section_id="evidence_to_examine",
            heading=PRELIMINARY_REPORT_SECTION_HEADINGS["evidence_to_examine"],
            items=gaps,
        ),
        ReportSection(
            section_id="preliminary_recommendations",
            heading=PRELIMINARY_REPORT_SECTION_HEADINGS["preliminary_recommendations"],
            items=[
                "ควรตรวจสอบและเก็บรักษาข้อมูลต้นฉบับเพื่อยืนยันข้อเท็จจริงของเหตุการณ์",
                "ควรตรวจสอบข้อขาดหายและข้อขัดแย้งก่อนใช้ข้อสันนิษฐานเชิงวิเคราะห์ในทางคดี",
            ],
        ),
        ReportSection(
            section_id="system_limitations",
            heading=PRELIMINARY_REPORT_SECTION_HEADINGS["system_limitations"],
            items=limitations,
        ),
    ]
    return StructuredReport(
        report_version="preliminary_analysis_report_v1",
        status="provisional_unverified",
        title=snapshot.thread_title or "CyberCase Preliminary Analysis",
        sections=sections,
        claims=claims,
        limitations=limitations,
    )


def _source_item(source_id: object, revision: int, filename: str | None, text: str) -> str:
    label = f"Evidence {source_id} · revision {revision}"
    if filename:
        label += f" · {filename}"
    return f"{label}: {text}"


def _support_type(claim_type: str) -> str:
    return {
        "reported": "user_reported",
        "analytical_inference": "analytical_inference",
        "unknown": "unknown",
    }[claim_type]


def _technical_items(
    snapshot: CaseReportInputSnapshot,
    trace: NativeCaseAnalysisTrace,
) -> list[str]:
    augmentation = snapshot.technical_augmentation
    if augmentation is None:
        return ["Technical augmentation outcome was not persisted for this historical result; no MITRE association is asserted."]
    if augmentation.status == "not_applicable":
        return ["MITRE augmentation was not applicable to this Case; no external retrieval was performed."]
    if augmentation.status == "insufficient_context":
        return ["MITRE augmentation was requested, but retrieved context was insufficient; no Case association is asserted."]
    if augmentation.status == "retrieved_without_supported_match":
        return ["MITRE context was retrieved, but no supported Case association was validated."]
    if augmentation.status == "failed":
        return [f"MITRE augmentation failed; no Case association is asserted. Failure code: {augmentation.failure_code}"]
    return [f"{association.technique_id}: {association.reason}" for association in trace.mitre_associations]


def _technical_rationale(
    snapshot: CaseReportInputSnapshot,
    trace: NativeCaseAnalysisTrace,
) -> list[str]:
    augmentation = snapshot.technical_augmentation
    if augmentation is not None and augmentation.status == "retrieved_with_matches":
        return [f"{association.technique_id}: validated against the persisted Case evidence mapping" for association in trace.mitre_associations]
    if augmentation is not None and augmentation.status == "failed":
        return [f"MITRE mapping was withheld because technical augmentation failed ({augmentation.failure_code})."]
    if augmentation is not None and augmentation.status == "retrieved_without_supported_match":
        return ["Retrieved MITRE rows remain external context because no Case-supported mapping passed validation."]
    if augmentation is not None and augmentation.status == "insufficient_context":
        return ["MITRE mapping was not attempted because the retrieved technical context was insufficient."]
    if augmentation is not None and augmentation.status == "not_applicable":
        return ["MITRE retrieval was skipped by the applicability gate."]
    return ["The technical augmentation outcome was not persisted; no mapping was inferred from historical metadata."]


def _technical_limitations(snapshot: CaseReportInputSnapshot) -> list[str]:
    augmentation = snapshot.technical_augmentation
    if augmentation is None:
        return ["Technical augmentation outcome: unavailable in the persisted historical result."]
    detail = f"; failure code {augmentation.failure_code}" if augmentation.failure_code else ""
    return [f"Technical augmentation outcome: {augmentation.status}{detail}."]


__all__ = [
    "CASE_REPORT_PROMPT_VERSION",
    "build_case_template_report",
    "run_case_report_generation",
]
