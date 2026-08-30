import re

from app.schemas.reports import (
    PRELIMINARY_REPORT_SECTION_HEADINGS,
    ReportClaim,
    ReportSection,
    StructuredReport,
)
from app.services.reports.report_contracts import ReportInputSnapshot


def _extract_summary_paragraphs(analysis_answer: str) -> list[str]:
    if not analysis_answer.strip():
        return []
    sec1_match = re.search(
        r"###\s*1\.\s*[^\n]+\n(.*?)(?=\n###\s*\d|\Z)",
        analysis_answer,
        re.DOTALL,
    )
    if sec1_match:
        text = sec1_match.group(1).strip()
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        if paragraphs:
            return paragraphs
    first_part = analysis_answer.split("###")[0].strip()
    if first_part and len(first_part) > 20:
        return [p.strip() for p in first_part.split("\n\n") if p.strip()]
    return [analysis_answer.strip()]


def _extract_progression_claims(snapshot: ReportInputSnapshot) -> list[ReportClaim]:
    claims: list[ReportClaim] = []
    source_ids = [str(message.message_id) for message in snapshot.source_messages]
    valid_source_set = set(source_ids)

    # 1. From snapshot.analysis_trace claims
    trace_claims = (
        snapshot.analysis_trace.get("claims", [])
        if isinstance(snapshot.analysis_trace, dict)
        else []
    )
    for idx, c in enumerate(trace_claims):
        if isinstance(c, dict) and c.get("text"):
            raw_sources = c.get("source_message_ids")
            if raw_sources is not None and isinstance(raw_sources, list):
                c_sources = [str(s) for s in raw_sources if str(s).strip()]
            else:
                c_sources = list(source_ids)
            claims.append(
                ReportClaim(
                    claim_id=f"CLM-{idx+1:02d}",
                    section_id="case_summary",
                    text=c["text"],
                    support_type=(
                        "user_reported"
                        if c.get("epistemic_status") == "reported"
                        else "analytical_inference"
                    ),
                    source_message_ids=c_sources,
                    mitre_technique_ids=[],
                )
            )

    # 2. If no trace claims, extract sequence from analysis_answer
    if not claims and snapshot.analysis_answer:
        sec2_match = re.search(
            r"###\s*2\.\s*[^\n]+\n(.*?)(?=\n###\s*\d|\Z)",
            snapshot.analysis_answer,
            re.DOTALL,
        )
        if sec2_match:
            raw_lines = sec2_match.group(1).strip().split("\n")
            for idx, line in enumerate(raw_lines):
                clean = line.strip()
                clean = re.sub(r"^[-*•]\s+", "", clean)
                clean = re.sub(r"^\d+\.\s+", "", clean)
                clean = re.sub(r"\*\*(.*?)\*\*", r"\1", clean).strip()
                if clean and len(clean) > 5 and not clean.startswith("#"):
                    claims.append(
                        ReportClaim(
                            claim_id=f"CLM-{idx+1:02d}",
                            section_id="case_summary",
                            text=clean,
                            support_type="analytical_inference",
                            source_message_ids=source_ids,
                            mitre_technique_ids=[],
                        )
                    )

    if not claims:
        claims.append(
            ReportClaim(
                claim_id="R-01",
                section_id="case_summary",
                text="The case summary is based on the latest completed analysis of the accumulated user-authored evidence.",
                support_type="analytical_inference",
                source_message_ids=source_ids,
                mitre_technique_ids=[],
            )
        )
    return claims


def build_template_report(snapshot: ReportInputSnapshot) -> StructuredReport:
    source_items = [
        f"Message {message.ordinal}: {message.content}"
        for message in snapshot.source_messages
    ]
    mitre_items = [
        f"{row.technique_id} — {row.name or row.technique_id}"
        + (f" ({row.tactic})" if row.tactic else "")
        + (f": {row.reason}" if row.reason else "")
        for row in snapshot.mitre_rows
    ]
    unresolved = snapshot.unresolved_issues or [
        "ไม่พบข้อขัดแย้งหรือประเด็นขาดหายที่ตรวจพบในสแนปช็อตนี้"
    ]
    summary_paragraphs = _extract_summary_paragraphs(snapshot.analysis_answer)

    sections = [
        ReportSection(
            section_id="case_summary",
            heading=PRELIMINARY_REPORT_SECTION_HEADINGS["case_summary"],
            paragraphs=summary_paragraphs or [snapshot.analysis_answer],
        ),
        ReportSection(
            section_id="indicators_found",
            heading=PRELIMINARY_REPORT_SECTION_HEADINGS["indicators_found"],
            items=source_items,
        ),
        ReportSection(
            section_id="mitre_attack_mapping",
            heading=PRELIMINARY_REPORT_SECTION_HEADINGS["mitre_attack_mapping"],
            items=mitre_items or ["ไม่มีรายการเทคนิค MITRE ATT&CK ที่ตรวจพบ"],
        ),
        ReportSection(
            section_id="mapping_rationale",
            heading=PRELIMINARY_REPORT_SECTION_HEADINGS["mapping_rationale"],
            items=[
                f"{row.technique_id}: {row.reason or 'ข้อสันนิษฐานเชิงวิเคราะห์จากฐานข้อมูล MITRE ATT&CK'}"
                for row in snapshot.mitre_rows
            ] or ["ไม่มีเหตุผลการเชื่อมโยง"],
        ),
        ReportSection(
            section_id="evidence_to_examine",
            heading=PRELIMINARY_REPORT_SECTION_HEADINGS["evidence_to_examine"],
            items=unresolved,
        ),
        ReportSection(
            section_id="preliminary_recommendations",
            heading=PRELIMINARY_REPORT_SECTION_HEADINGS["preliminary_recommendations"],
            items=[
                "ควรตรวจสอบและเก็บรักษาข้อมูลบันทึกเหตุการณ์ต้นฉบับ (Original Logs) เพื่อยืนยันความถูกต้องของเหตุการณ์",
                "ควรตรวจสอบประเด็นที่ยังขาดข้อมูลให้ชัดเจนก่อนนำข้อสันนิษฐานเชิงวิเคราะห์ไปใช้สรุปผลทางคดี",
            ],
        ),
        ReportSection(
            section_id="system_limitations",
            heading=PRELIMINARY_REPORT_SECTION_HEADINGS["system_limitations"],
            items=[
                "รายงานนี้เป็นรายงานสรุปผลการวิเคราะห์เบื้องต้น (Provisional / Unverified)",
                "ข้อมูลเหตุการณ์อ้างอิงจากข้อความที่ผู้ใช้ส่งเข้าสู่ระบบ การวิเคราะห์และข้อมูล MITRE ATT&CK เป็นการอนุมานทางเทคนิคภายนอก ไม่ใช่พยานหลักฐานยืนยันว่าเหตุการณ์เกิดขึ้นจริง",
                f"Evidence snapshot SHA-256: {snapshot.evidence_sha256}",
            ],
        ),
    ]
    claims = _extract_progression_claims(snapshot)
    return StructuredReport(
        report_version="preliminary_analysis_report_v1",
        status="provisional_unverified",
        title=snapshot.thread_title or "CyberCase Preliminary Analysis",
        sections=sections,
        claims=claims,
        limitations=sections[-1].items,
    )


__all__ = ["build_template_report"]
