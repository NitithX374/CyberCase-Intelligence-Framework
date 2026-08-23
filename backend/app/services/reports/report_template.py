from __future__ import annotations

from app.schemas.reports import ReportClaim, ReportSection, StructuredReport
from app.services.reports.report_contracts import ReportInputSnapshot


def build_template_report(snapshot: ReportInputSnapshot) -> StructuredReport:
    source_items = [
        f"Message {message.ordinal}: {message.content}"
        for message in snapshot.source_messages
    ]
    mitre_items = [
        " ".join(
            part
            for part in (row.technique_id, row.name, row.reason)
            if part.strip()
        )
        for row in snapshot.mitre_rows
    ]
    unresolved = snapshot.unresolved_issues or [
        "No explicit unresolved issue was persisted; investigators should verify all analytical inferences against original evidence."
    ]
    source_ids = [str(message.message_id) for message in snapshot.source_messages]
    sections = [
        ReportSection(
            section_id="case_summary",
            heading="5.1 สรุปคดี",
            paragraphs=[snapshot.analysis_answer],
        ),
        ReportSection(
            section_id="indicators_found",
            heading="5.2 ตัวบ่งชี้ที่พบ",
            items=source_items,
        ),
        ReportSection(
            section_id="mitre_attack_mapping",
            heading="5.3 MITRE ATT&CK Mapping",
            items=mitre_items or ["No MITRE ATT&CK technique was admitted by the bound retrieval context."],
        ),
        ReportSection(
            section_id="mapping_rationale",
            heading="5.4 เหตุผลของการ mapping",
            items=[
                f"{row.technique_id}: {row.reason or 'Candidate association from external MITRE retrieval context.'}"
                for row in snapshot.mitre_rows
            ] or ["No mapping rationale is available."],
        ),
        ReportSection(
            section_id="evidence_to_examine",
            heading="5.5 หลักฐานที่ควรตรวจสอบ",
            items=unresolved,
        ),
        ReportSection(
            section_id="preliminary_recommendations",
            heading="5.6 คำแนะนำเบื้องต้น",
            items=[
                "Preserve and authenticate the original digital evidence referenced by the user.",
                "Resolve the listed information gaps before treating candidate MITRE associations as established case facts.",
            ],
        ),
        ReportSection(
            section_id="system_limitations",
            heading="5.7 ข้อจำกัดของระบบ",
            items=[
                "This report is provisional and unverified.",
                "User-authored messages are incident evidence; MITRE retrieval and model analysis are external interpretation, not proof that an event occurred.",
                f"Evidence snapshot SHA-256: {snapshot.evidence_sha256}",
            ],
        ),
    ]
    claims = [
        ReportClaim(
            claim_id="R-01",
            section_id="case_summary",
            text="The case summary is based on the latest completed analysis of the accumulated user-authored evidence.",
            support_type="analytical_inference",
            source_message_ids=source_ids,
            mitre_technique_ids=[],
        )
    ]
    return StructuredReport(
        report_version="preliminary_analysis_report_v1",
        status="provisional_unverified",
        title=snapshot.thread_title or "CyberCase Preliminary Analysis",
        sections=sections,
        claims=claims,
        limitations=sections[-1].items,
    )


__all__ = ["build_template_report"]
