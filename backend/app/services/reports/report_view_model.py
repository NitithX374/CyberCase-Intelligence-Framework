"""Deterministic presentation view model builder for CyberCase incident reports.

Supports both Thai ('th') and English ('en') formal investigative reports.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import re
from typing import Any, Final, Literal
from uuid import UUID

from app.schemas.reports import (
    ChatReportRead,
    ReportClaim,
    ReportSection,
    StructuredReport,
)

ReportLanguage = Literal["th", "en"]

RELATION_TEMPLATES_TH: Final[dict[str, str]] = {
    "accessed_without_authorization": "{subject} เข้าถึง {object} โดยไม่ได้รับอนุญาต",
    "accessed": "{subject} เข้าถึง {object}",
    "used": "{subject} ใช้ {object}",
    "placed": "{subject} วาง {object}",
    "searched_for": "{subject} ค้นหา {object}",
    "controls": "{subject} ควบคุม {object}",
    "connected_to": "{subject} เชื่อมต่อไปยัง {object}",
    "communicated_with": "{subject} สื่อสารกับ {object}",
    "executed": "{subject} สั่งทำงาน {object}",
    "downloaded": "{subject} ดาวน์โหลด {object}",
    "exfiltrated": "{subject} ส่งข้อมูลออกไปยัง {object}",
    "compromised": "{subject} ถูกบุกรุกโดย {object}",
    "associated_with": "{subject} มีความเกี่ยวข้องกับ {object}",
    "belongs_to": "{subject} เป็นของ {object}",
    "targeted": "{subject} พุ่งเป้าไปที่ {object}",
    "modified": "{subject} ปรับแต่งหรือเปลี่ยนแปลง {object}",
    "created": "{subject} สร้าง {object}",
    "deleted": "{subject} ลบ {object}",
    "injected": "{subject} ฉีดคำสั่งหรือโค้ดลงใน {object}",
    "delivered": "{subject} ส่งต่อหรือปล่อย {object}",
    "impersonated": "{subject} สวมรอยเป็น {object}",
    "scanned": "{subject} สแกนหรือสำรวจ {object}",
}

RELATION_TEMPLATES_EN: Final[dict[str, str]] = {
    "accessed_without_authorization": "{subject} accessed {object} without authorization",
    "accessed": "{subject} accessed {object}",
    "used": "{subject} used {object}",
    "placed": "{subject} placed {object}",
    "searched_for": "{subject} searched for {object}",
    "controls": "{subject} controls {object}",
    "connected_to": "{subject} connected to {object}",
    "communicated_with": "{subject} communicated with {object}",
    "executed": "{subject} executed {object}",
    "downloaded": "{subject} downloaded {object}",
    "exfiltrated": "{subject} exfiltrated data to {object}",
    "compromised": "{subject} was compromised by {object}",
    "associated_with": "{subject} is associated with {object}",
    "belongs_to": "{subject} belongs to {object}",
    "targeted": "{subject} targeted {object}",
    "modified": "{subject} modified {object}",
    "created": "{subject} created {object}",
    "deleted": "{subject} deleted {object}",
    "injected": "{subject} injected code/commands into {object}",
    "delivered": "{subject} delivered {object}",
    "impersonated": "{subject} impersonated {object}",
    "scanned": "{subject} scanned {object}",
}

I18N_STRINGS: Final[dict[str, dict[str, str]]] = {
    "th": {
        "org_header": "CYBERCASE INTELLIGENCE FRAMEWORK",
        "doc_title": "รายงานวิเคราะห์เหตุการณ์เบื้องต้น",
        "running_header": "รายงานวิเคราะห์เหตุการณ์เบื้องต้น / PROVISIONAL",
        "page_label": "หน้า",
        "end_of_report": "สิ้นสุดรายงาน — CyberCase Intelligence Framework (Provisional / Unverified)",
        # Meta
        "lbl_case_title": "กรณี / หัวข้อ:",
        "lbl_generated_date": "วันที่จัดทำรายงาน:",
        "lbl_report_status": "สถานะรายงาน:",
        "status_provisional": "รายงานเบื้องต้น / ยังไม่ได้รับการยืนยัน (Provisional / Unverified)",
        # Section Headings
        "sec_5_1": "5.1 สรุปเหตุการณ์",
        "sec_5_2": "5.2 ลำดับเหตุการณ์",
        "sec_5_3": "5.3 หลักฐานและตัวบ่งชี้สำคัญ",
        "sec_5_4": "5.4 ความสัมพันธ์ของเหตุการณ์และองค์ประกอบในคดี",
        "sec_5_5": "5.5 ผลการวิเคราะห์และ MITRE ATT&CK Mapping",
        "sec_5_6": "5.6 ประเด็นที่ยังไม่สามารถยืนยันและสิ่งที่ควรตรวจสอบเพิ่มเติม",
        "sec_5_7": "5.7 ข้อจำกัดและข้อมูลการตรวจสอบย้อนกลับ",
        # Subheaders & Tables
        "sub_evidence_reg": "ทะเบียนหลักฐาน (Evidence Register)",
        "sub_iocs": "ตัวบ่งชี้ความเสี่ยงทางไซเบอร์ (Indicators of Compromise / Technical Indicators)",
        "sub_relationships": "โครงสร้างความเชื่อมโยงระหว่างผู้เกี่ยวข้อง ระบบ พฤติการณ์ และหลักฐานในคดีที่ตรวจพบ:",
        "sub_mitre_intro": "การวิเคราะห์เปรียบเทียบพฤติกรรมในเหตุการณ์กับฐานข้อมูลเทคนิคและยุทธวิธีการโจมตี MITRE ATT&CK:",
        "sub_unresolved": "ประเด็นที่ยังไม่สามารถยืนยันได้ (Unestablished / Gaps)",
        "sub_next_steps": "สิ่งที่ควรตรวจสอบเพิ่มเติม (Investigative Next Steps)",
        "sub_limitations": "ข้อจำกัดของรายงาน (Report Limitations)",
        "sub_provenance": "ข้อมูลการตรวจสอบย้อนกลับ (Provenance & Traceability)",
        # Table Columns
        "col_order": "ลำดับ",
        "col_time": "เวลา",
        "col_event": "เหตุการณ์",
        "col_source_evidence": "แหล่งข้อมูล / หลักฐาน",
        "col_item": "รายการ",
        "col_type": "ประเภท",
        "col_description": "รายละเอียด",
        "col_source": "แหล่งข้อมูล",
        "col_ioc_type": "ประเภท",
        "col_ioc_value": "ค่าตัวบ่งชี้",
        "col_ioc_note": "หมายเหตุ / ความเกี่ยวข้อง",
        "col_finding": "ข้อค้นพบ / แท็กติก",
        "col_case_support": "ข้อมูลสนับสนุนจากคดี",
        "col_mitre": "MITRE ATT&CK",
        "col_mapping_status": "สถานะการ Mapping",
        "col_prov_item": "รายการตรวจสอบ",
        "col_prov_value": "ค่าระบุตัวตน / ข้อมูลสถิติ",
        # Fallbacks
        "empty_summary": "ไม่มีข้อมูลสรุปเหตุการณ์ที่บันทึกไว้ในสแนปช็อตนี้",
        "empty_timeline": "ไม่พบข้อมูลลำดับเหตุการณ์ที่บันทึกไว้ในสแนปช็อตนี้",
        "empty_evidence": "ไม่พบรายการหลักฐานที่บันทึกไว้ในสแนปช็อตนี้",
        "empty_relationships": "ไม่พบความสัมพันธ์เชิงโครงสร้างระหว่างองค์ประกอบที่บันทึกไว้ในสแนปช็อตนี้",
        "empty_mitre": "ไม่พบข้อมูลการ Mapping เทคนิค MITRE ATT&CK ที่บันทึกไว้ในสแนปช็อตนี้",
        "empty_gaps": "ไม่พบข้อขัดแย้งหรือประเด็นขาดหายที่ตรวจพบในสแนปช็อตนี้",
        "actor_prefix": "ผู้เกี่ยวข้อง",
        "status_candidate": "Candidate (ผู้สืบค้นแนะนำ)",
        "status_reported_analysis": "Reported in Analysis (อ้างอิงในบทวิเคราะห์)",
        "retrieval_source": "แหล่งสืบค้น",
    },
    "en": {
        "org_header": "CYBERCASE INTELLIGENCE FRAMEWORK",
        "doc_title": "Preliminary Incident Analysis Report",
        "running_header": "PRELIMINARY INCIDENT ANALYSIS REPORT / PROVISIONAL",
        "page_label": "Page",
        "end_of_report": "End of Report — CyberCase Intelligence Framework (Provisional / Unverified)",
        # Meta
        "lbl_case_title": "Case / Title:",
        "lbl_generated_date": "Generated Date:",
        "lbl_report_status": "Report Status:",
        "status_provisional": "Provisional / Unverified Incident Analysis Report",
        # Section Headings
        "sec_5_1": "5.1 Incident Summary",
        "sec_5_2": "5.2 Chronological Timeline",
        "sec_5_3": "5.3 Evidence & Key Indicators",
        "sec_5_4": "5.4 Case Elements & Relationships",
        "sec_5_5": "5.5 Technical Analysis & MITRE ATT&CK Mapping",
        "sec_5_6": "5.6 Unestablished Issues & Recommended Next Steps",
        "sec_5_7": "5.7 System Limitations & Provenance",
        # Subheaders & Tables
        "sub_evidence_reg": "Evidence Register",
        "sub_iocs": "Technical Indicators of Compromise (IOCs)",
        "sub_relationships": "Identified structural relationships between actors, systems, actions, and evidence:",
        "sub_mitre_intro": "Analytical mapping between observed incident behaviors and the MITRE ATT&CK knowledge base:",
        "sub_unresolved": "Unestablished Issues (Gaps)",
        "sub_next_steps": "Investigative Next Steps",
        "sub_limitations": "Report Limitations",
        "sub_provenance": "Provenance & Traceability",
        # Table Columns
        "col_order": "No.",
        "col_time": "Time",
        "col_event": "Event Description",
        "col_source_evidence": "Source / Evidence Reference",
        "col_item": "Item",
        "col_type": "Type",
        "col_description": "Description",
        "col_source": "Source",
        "col_ioc_type": "Indicator Type",
        "col_ioc_value": "Indicator Value",
        "col_ioc_note": "Context / Association",
        "col_finding": "Finding / Tactic",
        "col_case_support": "Supporting Case Evidence",
        "col_mitre": "MITRE ATT&CK",
        "col_mapping_status": "Mapping Status",
        "col_prov_item": "Audit Item",
        "col_prov_value": "Identifier / Value",
        # Fallbacks
        "empty_summary": "No incident summary records were persisted for this snapshot.",
        "empty_timeline": "No timeline events were persisted for this snapshot.",
        "empty_evidence": "No evidence items were persisted for this snapshot.",
        "empty_relationships": "No structural relationships were persisted for this snapshot.",
        "empty_mitre": "No MITRE ATT&CK mapping candidates were persisted for this snapshot.",
        "empty_gaps": "No analytical gaps or contradictions were identified for this snapshot.",
        "actor_prefix": "Actors",
        "status_candidate": "Candidate (Suggested Retrieval)",
        "status_reported_analysis": "Reported in Analysis",
        "retrieval_source": "Retrieval Source",
    },
}

_IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
_DOMAIN_RE = re.compile(
    r"\b(?:[a-zA-Z0-9-]+\.)+(?:com|net|org|io|co|th|info|biz|cc|xyz|top|site)\b",
    re.IGNORECASE,
)
_URL_RE = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)
_HASH_SHA256_RE = re.compile(r"\b[a-fA-F0-9]{64}\b")
_HASH_MD5_RE = re.compile(r"\b[a-fA-F0-9]{32}\b")
_FILE_EXT_RE = re.compile(
    r"\b[a-zA-Z0-9_.-]+\.(?:exe|dll|ps1|bat|vbs|sh|py|php|jsp|asp|aspx|zip|rar|tar|gz|7z|bin|elf)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class TimelineViewRow:
    order: int
    time_display: str
    event: str
    source_evidence: str
    actors: str = ""
    status: str = "reported"


@dataclass(frozen=True)
class EvidenceViewRow:
    item_id: str
    title: str
    artifact_type: str
    description: str
    source_type: str
    confidence: str


@dataclass(frozen=True)
class IndicatorViewRow:
    indicator_type: str
    value: str
    note: str


@dataclass(frozen=True)
class RelationshipViewRow:
    statement: str
    subject_name: str
    predicate: str
    object_name: str
    status: str
    confidence: str


@dataclass(frozen=True)
class MitreMappingViewRow:
    finding: str
    case_evidence_support: str
    technique_id: str
    technique_name: str
    status_display: str
    tactic: str
    source: str
    relevance: str


@dataclass(frozen=True)
class UnresolvedIssueViewRow:
    description: str
    category: str
    reason: str = ""


@dataclass(frozen=True)
class VerificationActionViewRow:
    order: int
    action: str


@dataclass(frozen=True)
class ProvenanceViewRow:
    label: str
    value: str


@dataclass(frozen=True)
class ReportViewModel:
    report_id: str
    case_title: str
    generated_date: str
    report_status: str
    version_label: str
    language: ReportLanguage
    i18n: dict[str, str]

    # 5.1 สรุปเหตุการณ์ / Incident Summary
    summary_paragraphs: list[str] = field(default_factory=list)

    # 5.2 ลำดับเหตุการณ์ / Chronological Timeline
    timeline_rows: list[TimelineViewRow] = field(default_factory=list)

    # 5.3 หลักฐานและตัวบ่งชี้สำคัญ / Evidence & Key Indicators
    evidence_rows: list[EvidenceViewRow] = field(default_factory=list)
    has_indicators: bool = False
    indicator_rows: list[IndicatorViewRow] = field(default_factory=list)

    # 5.4 ความสัมพันธ์ของเหตุการณ์และองค์ประกอบในคดี / Relationships
    has_relationships: bool = False
    relationship_rows: list[RelationshipViewRow] = field(default_factory=list)
    relationship_graph_image: str | None = None

    # 5.5 ผลการวิเคราะห์และ MITRE ATT&CK Mapping / Technical Analysis
    has_mitre_mappings: bool = False
    mitre_rows: list[MitreMappingViewRow] = field(default_factory=list)

    # 5.6 ประเด็นที่ยังไม่สามารถยืนยันและสิ่งที่ควรตรวจสอบเพิ่มเติม / Gaps & Next Steps
    unresolved_issues: list[UnresolvedIssueViewRow] = field(default_factory=list)
    verification_actions: list[VerificationActionViewRow] = field(default_factory=list)

    # 5.7 ข้อจำกัดและข้อมูลการตรวจสอบย้อนกลับ / Limitations & Provenance
    limitations: list[str] = field(default_factory=list)
    provenance_rows: list[ProvenanceViewRow] = field(default_factory=list)


def _strict_marked_fields(
    value: str,
    markers: tuple[str, ...],
    *,
    terminal_period: bool = False,
    leading_empty: bool = False,
) -> tuple[str, ...] | None:
    if any(value.count(marker) != 1 for marker in markers):
        return None
    fields: list[str] = []
    remainder = value
    for marker in markers:
        field_part, separator, remainder = remainder.partition(marker)
        if not separator:
            return None
        fields.append(field_part)
    if terminal_period:
        if not remainder.endswith("."):
            return None
        remainder = remainder[:-1]
    fields.append(remainder)
    if leading_empty:
        if fields[0] != "":
            return None
        fields = fields[1:]
    if not fields or any(field_item == "" for field_item in fields):
        return None
    return tuple(fields)


def _format_datetime(dt: datetime | None) -> str:
    if dt is None:
        return "N/A"
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _extract_indicators_from_text(
    text: str,
    note: str,
    seen: set[str],
) -> list[IndicatorViewRow]:
    rows: list[IndicatorViewRow] = []

    for match in _URL_RE.finditer(text):
        val = match.group(0).rstrip(".,;)\"'>")
        if val and val not in seen:
            seen.add(val)
            rows.append(IndicatorViewRow(indicator_type="URL", value=val, note=note))

    for match in _IP_RE.finditer(text):
        val = match.group(0)
        if val not in seen:
            seen.add(val)
            rows.append(IndicatorViewRow(indicator_type="IP Address", value=val, note=note))

    for match in _DOMAIN_RE.finditer(text):
        val = match.group(0)
        if val not in seen and not any(val in r.value for r in rows if r.indicator_type == "URL"):
            seen.add(val)
            rows.append(IndicatorViewRow(indicator_type="Domain", value=val, note=note))

    for match in _HASH_SHA256_RE.finditer(text):
        val = match.group(0)
        if val not in seen:
            seen.add(val)
            rows.append(IndicatorViewRow(indicator_type="SHA-256 Hash", value=val, note=note))

    for match in _HASH_MD5_RE.finditer(text):
        val = match.group(0)
        if val not in seen and len(val) == 32:
            seen.add(val)
            rows.append(IndicatorViewRow(indicator_type="MD5 Hash", value=val, note=note))

    for match in _FILE_EXT_RE.finditer(text):
        val = match.group(0)
        if val not in seen:
            seen.add(val)
            rows.append(IndicatorViewRow(indicator_type="Filename / Artifact", value=val, note=note))

    return rows


def build_report_view_model(
    report: ChatReportRead,
    *,
    thread_title: str = "CyberCase Investigation",
    language: ReportLanguage = "th",
) -> ReportViewModel:
    """Deterministically transform persisted ChatReportRead into ReportViewModel."""

    lang = language if language in ("th", "en") else "th"
    i18n = I18N_STRINGS[lang]
    rel_templates = RELATION_TEMPLATES_EN if lang == "en" else RELATION_TEMPLATES_TH

    structured = report.report
    sections_by_id: dict[str, ReportSection] = {}
    if structured:
        for sec in structured.sections:
            sections_by_id[sec.section_id] = sec

    title = structured.title if structured and structured.title.strip() else thread_title
    report_status_display = i18n["status_provisional"]
    generated_date_str = _format_datetime(report.created_at)
    version_label_str = f"Version {report.version_number}"

    # -------------------------------------------------------------------------
    # Parse Items from Sections
    # -------------------------------------------------------------------------
    # Evidence items
    evidence_rows: list[EvidenceViewRow] = []
    seen_iocs: set[str] = set()
    indicator_rows: list[IndicatorViewRow] = []

    raw_evidence_items = []
    for sec_id in ("evidence_findings", "indicators_found"):
        if sec_id in sections_by_id:
            raw_evidence_items.extend(sections_by_id[sec_id].items)

    for item in raw_evidence_items:
        parsed = _strict_marked_fields(
            item,
            (
                " | Title: ",
                " | Description: ",
                " | Artifact type: ",
                " | Status: ",
                " | Confidence: ",
                " | Source type: ",
            ),
            terminal_period=True,
        )
        if parsed is not None:
            ev_id, ev_title, ev_desc, art_type, ev_status, ev_conf, src_type = parsed
            evidence_rows.append(
                EvidenceViewRow(
                    item_id=ev_id,
                    title=ev_title,
                    artifact_type=art_type,
                    description=ev_desc,
                    source_type=src_type,
                    confidence=ev_conf,
                )
            )
            note_text = (
                f"Observed in {ev_id} ({ev_title})"
                if lang == "en"
                else f"พบในหลักฐาน {ev_id} ({ev_title})"
            )
            iocs = _extract_indicators_from_text(
                f"{ev_title} {ev_desc}",
                note=note_text,
                seen=seen_iocs,
            )
            indicator_rows.extend(iocs)
        elif "No evidence" not in item:
            evidence_rows.append(
                EvidenceViewRow(
                    item_id="-",
                    title=item,
                    artifact_type="Note" if lang == "en" else "บันทึกข้อความ",
                    description=item,
                    source_type="User Reported" if lang == "en" else "รายงานผู้ใช้",
                    confidence="candidate",
                )
            )

    # Timeline, Entities, and Relationships
    timeline_rows: list[TimelineViewRow] = []
    relationship_rows: list[RelationshipViewRow] = []
    entity_name_map: dict[str, str] = {}

    raw_examine_items = []
    for sec_id in ("chronological_timeline", "individuals_accounts_systems_roles", "evidence_to_examine"):
        if sec_id in sections_by_id:
            raw_examine_items.extend(sections_by_id[sec_id].items)

    timeline_order = 1
    for item in raw_examine_items:
        tl_parsed = _strict_marked_fields(
            item,
            (
                " | Time: ",
                " | Event: ",
                " | Actors: ",
                " | Linked evidence: ",
                " | Status: ",
                " | Confidence: ",
            ),
            terminal_period=True,
        )
        if tl_parsed is not None:
            tl_id, tl_time, tl_event, tl_actors, tl_ev, tl_status, tl_conf = tl_parsed
            timeline_rows.append(
                TimelineViewRow(
                    order=timeline_order,
                    time_display=tl_time,
                    event=tl_event,
                    source_evidence=f"{tl_ev} ({tl_id})",
                    actors=tl_actors if tl_actors != "none persisted" else "-",
                    status=tl_status,
                )
            )
            timeline_order += 1
            continue

        ent_parsed = _strict_marked_fields(
            item,
            (
                "Entity | Name: ",
                " | Type: ",
                " | Reported role: ",
                " | Persisted status: ",
                " | Confidence: ",
            ),
            terminal_period=True,
            leading_empty=True,
        )
        if ent_parsed is not None:
            name, e_type, role, p_status, conf = ent_parsed
            entity_name_map[name] = name
            if e_type in {"ip", "domain", "url", "hash", "file", "host", "account"}:
                if name not in seen_iocs:
                    seen_iocs.add(name)
                    indicator_rows.append(
                        IndicatorViewRow(
                            indicator_type=e_type.upper(),
                            value=name,
                            note=(
                                f"Role: {role}"
                                if lang == "en"
                                else f"ระบุในบทบาท: {role}"
                            ),
                        )
                    )
            continue

        if item.startswith("Relationship | "):
            rel_content = item[len("Relationship | ") :]
            rel_parsed = _strict_marked_fields(
                rel_content,
                (
                    " | Statement: ",
                    " | Status: ",
                    " | Confidence: ",
                ),
                terminal_period=True,
            )
            if rel_parsed is not None:
                rel_triplet, statement, status, conf = rel_parsed
                if rel_triplet.count(" -> ") == 2:
                    sub, pred, obj = rel_triplet.split(" -> ")
                    pred_clean = pred.strip().lower()
                    if pred_clean in rel_templates:
                        stmt_display = rel_templates[pred_clean].format(subject=sub, object=obj)
                    elif statement.strip():
                        stmt_display = statement.strip()
                    else:
                        stmt_display = f"{sub} -> {pred} -> {obj}"
                    relationship_rows.append(
                        RelationshipViewRow(
                            statement=stmt_display,
                            subject_name=sub,
                            predicate=pred,
                            object_name=obj,
                            status=status,
                            confidence=conf,
                        )
                    )
                    continue

        if "chronological_timeline" in sections_by_id and item in sections_by_id["chronological_timeline"].items:
            if "No timeline" not in item:
                timeline_rows.append(
                    TimelineViewRow(
                        order=timeline_order,
                        time_display="Unspecified" if lang == "en" else "ไม่ระบุเวลา",
                        event=item,
                        source_evidence="User Reported" if lang == "en" else "รายงานผู้ใช้",
                        actors="-",
                        status="reported",
                    )
                )
                timeline_order += 1

    has_indicators = len(indicator_rows) > 0
    has_relationships = len(relationship_rows) > 0

    # -------------------------------------------------------------------------
    # MITRE ATT&CK Mappings
    # -------------------------------------------------------------------------
    mitre_view_rows: list[MitreMappingViewRow] = []
    raw_mitre_items = []
    for sec_id in ("technical_analysis_mitre", "mitre_attack_mapping"):
        if sec_id in sections_by_id:
            raw_mitre_items.extend(sections_by_id[sec_id].items)

    for item in raw_mitre_items:
        m_parsed = _strict_marked_fields(
            item,
            (
                " | Name: ",
                " | Mapping status: ",
                " | Source: ",
                " | Relevance: ",
                " | Score: ",
                " | Tactic: ",
                " | Entity type: ",
                " | Description: ",
            ),
        )
        if m_parsed is not None:
            t_id, t_name, m_status, m_src, m_rel, m_score, m_tactic, e_type, m_desc = m_parsed
            finding_title = f"{m_tactic}: {t_name}"
            status_display = i18n["status_candidate"]
            if m_rel == "cited_in_answer" or "cited" in m_rel:
                status_display = i18n["status_reported_analysis"]

            mitre_view_rows.append(
                MitreMappingViewRow(
                    finding=finding_title,
                    case_evidence_support=(
                        m_desc
                        if m_desc != "No description was persisted."
                        else ("No additional details." if lang == "en" else "ไม่มีรายละเอียดเพิ่มเติม")
                    ),
                    technique_id=t_id,
                    technique_name=t_name,
                    status_display=status_display,
                    tactic=m_tactic,
                    source=m_src,
                    relevance=m_rel,
                )
            )
        elif "No MITRE" not in item:
            mitre_view_rows.append(
                MitreMappingViewRow(
                    finding=item[:60],
                    case_evidence_support=item,
                    technique_id="MITRE Candidate",
                    technique_name=item[:40],
                    status_display=i18n["status_candidate"],
                    tactic="General",
                    source="extraction",
                    relevance="candidate",
                )
            )

    has_mitre_mappings = len(mitre_view_rows) > 0

    # -------------------------------------------------------------------------
    # 5.1 สรุปเหตุการณ์ / Incident Summary
    # -------------------------------------------------------------------------
    summary_paragraphs: list[str] = []
    bg_items = []
    for sec_id in ("case_background_scope", "case_summary", "executive_summary"):
        if sec_id in sections_by_id:
            for p in sections_by_id[sec_id].paragraphs:
                p_clean = p.strip()
                if p_clean and not p_clean.startswith("Snapshot scope:") and not p_clean.startswith("This preliminary report"):
                    summary_paragraphs.append(p_clean)
            for item in sections_by_id[sec_id].items:
                if "Message " in item and "): " in item:
                    _, _, content = item.partition("): ")
                    if content:
                        bg_items.append(content.strip())
                elif "Generation method:" not in item and "Ordered user" not in item:
                    bg_items.append(item.strip())

    if bg_items:
        first_item = bg_items[0]
        if lang == "th":
            prefix = "มีการรายงานว่า " if not first_item.startswith("มี") and not first_item.startswith("พบ") else ""
            summary_paragraphs.append(f"{prefix}{first_item}")
            if len(bg_items) > 1:
                summary_paragraphs.append(f"จากข้อมูลที่ได้รับ: {'; '.join(bg_items[1:])}")
        else:
            summary_paragraphs.append(f"Initial report indicates: {first_item}")
            if len(bg_items) > 1:
                summary_paragraphs.append(f"Subsequent reported activity: {'; '.join(bg_items[1:])}")

    if not summary_paragraphs:
        summary_paragraphs.append(i18n["empty_summary"])

    # -------------------------------------------------------------------------
    # 5.6 ประเด็นที่ยังไม่สามารถยืนยันและสิ่งที่ควรตรวจสอบเพิ่มเติม
    # -------------------------------------------------------------------------
    unresolved_issues: list[UnresolvedIssueViewRow] = []
    limitations: list[str] = []
    if structured and structured.limitations:
        for lim in structured.limitations:
            if lim.startswith("Extraction warning: "):
                warning_text = lim[len("Extraction warning: ") :]
                unresolved_issues.append(
                    UnresolvedIssueViewRow(
                        description=warning_text,
                        category="Warning / Gap" if lang == "en" else "ข้อสังเกต / คำเตือน",
                        reason=(
                            "Ambiguity or inconsistency detected in reported data"
                            if lang == "en"
                            else "พบความคลุมเครือหรือความไม่สอดคล้องในข้อมูลที่ได้รับ"
                        ),
                    )
                )
            else:
                limitations.append(lim)

    if not unresolved_issues:
        unresolved_issues.append(
            UnresolvedIssueViewRow(
                description=i18n["empty_gaps"],
                category="Normal" if lang == "en" else "สถานะปกติ",
                reason="-",
            )
        )

    verification_actions: list[VerificationActionViewRow] = []
    for sec_id in ("preliminary_recommendations", "conclusions_limitations_next_steps"):
        if sec_id in sections_by_id:
            for item in sections_by_id[sec_id].items:
                if item and "Review every candidate" not in item:
                    verification_actions.append(
                        VerificationActionViewRow(order=len(verification_actions) + 1, action=item)
                    )

    if not verification_actions:
        if lang == "en":
            verification_actions = [
                VerificationActionViewRow(
                    order=1,
                    action="Examine original digital artifacts (e.g., server logs, PCAP, disk images) to confirm reported indicators and timestamps.",
                ),
                VerificationActionViewRow(
                    order=2,
                    action="Verify connections between involved user accounts and endpoints to determine the full scope of impact.",
                ),
                VerificationActionViewRow(
                    order=3,
                    action="Correlate observed behaviors against MITRE ATT&CK techniques to establish appropriate mitigation controls.",
                ),
                VerificationActionViewRow(
                    order=4,
                    action="Preserve forensic copies of all relevant digital evidence following standard chain-of-custody protocols.",
                ),
            ]
        else:
            verification_actions = [
                VerificationActionViewRow(
                    order=1,
                    action="ตรวจพิสูจน์พยานหลักฐานต้นฉบับ (เช่น Server Logs, PCAP, Disk Image) เพื่อยืนยันตัวบ่งชี้และเวลาที่แท้จริง",
                ),
                VerificationActionViewRow(
                    order=2,
                    action="ตรวจสอบความสัมพันธ์ระหว่างบัญชีผู้ใช้และอุปกรณ์ปลายทางที่เกี่ยวข้องเพื่อยืนยันขอบเขตความเสียหาย",
                ),
                VerificationActionViewRow(
                    order=3,
                    action="เปรียบเทียบพฤติกรรมในระบบกับ MITRE ATT&CK Techniques ที่ตรวจพบเพื่อกำหนดมาตรการสกัดกั้นที่เหมาะสม",
                ),
                VerificationActionViewRow(
                    order=4,
                    action="เก็บรักษาสำเนาพยานหลักฐานดิจิทัลตามระเบียบสายการครอบครองพยานหลักฐาน (Chain of Custody)",
                ),
            ]

    # -------------------------------------------------------------------------
    # 5.7 ข้อจำกัดและข้อมูลการตรวจสอบย้อนกลับ (Limitations & Provenance)
    # -------------------------------------------------------------------------
    if not limitations:
        if lang == "en":
            limitations = [
                "This report is a provisional, unverified preliminary analysis designed for investigative orientation.",
                "Portions of incident details originate from user-submitted statements and have not been independently confirmed with raw evidence.",
                "The automated analysis reflects only the snapshot data provided and does not replace a comprehensive digital forensics examination.",
                "Associated MITRE ATT&CK techniques represent retrieval mapping candidates and require expert validation.",
            ]
        else:
            limitations = [
                "รายงานนี้เป็นรายงานสรุปผลการวิเคราะห์เบื้องต้น (Provisional / Unverified Report) สำหรับใช้เป็นแนวทางการสืบสวน",
                "ข้อมูลเหตุการณ์บางส่วนมาจากข้อความที่ผู้ใช้หรือผู้แจ้งเหตุรายงาน และยังไม่ได้รับการตรวจสอบยืนยันกับพยานหลักฐานดิจิทัลต้นฉบับโดยตรง",
                "ระบบประมวลผลตามสแนปช็อตข้อมูลที่ได้รับเท่านั้น ไม่สามารถทดแทนกระบวนการตรวจพิสูจน์พยานหลักฐานทางนิติวิทยาศาสตร์ดิจิทัลอย่างเป็นทางการได้",
                "เทคนิคและยุทธวิธี MITRE ATT&CK ที่ปรากฏเป็นผลจากการจับคู่เชิงวิเคราะห์ (Candidate Mapping) ต้องอาศัยผู้เชี่ยวชาญยืนยันก่อนใช้เป็นข้อสรุปทางคดี",
            ]

    provenance_rows: list[ProvenanceViewRow] = [
        ProvenanceViewRow(label="Report ID", value=str(report.report_id)),
        ProvenanceViewRow(label="Report Version", value=f"v{report.version_number} ({report.report.report_version if report.report else 'preliminary_analysis_report_v1'})"),
        ProvenanceViewRow(label="Generated Date (UTC)", value=generated_date_str),
        ProvenanceViewRow(label="Source Snapshot Hash", value=report.source_snapshot_hash),
        ProvenanceViewRow(label="Extraction Version", value=report.extraction_version),
        ProvenanceViewRow(label="Prompt Version", value=report.prompt_version),
        ProvenanceViewRow(label="Template Provider", value=f"{report.provider} ({report.model})"),
        ProvenanceViewRow(label="Verification Status", value="Validated against frozen case state"),
    ]

    return ReportViewModel(
        report_id=str(report.report_id),
        case_title=title,
        generated_date=generated_date_str,
        report_status=report_status_display,
        version_label=version_label_str,
        language=lang,
        i18n=i18n,
        summary_paragraphs=summary_paragraphs,
        timeline_rows=timeline_rows,
        evidence_rows=evidence_rows,
        has_indicators=has_indicators,
        indicator_rows=indicator_rows,
        has_relationships=has_relationships,
        relationship_rows=relationship_rows,
        relationship_graph_image=None,
        has_mitre_mappings=has_mitre_mappings,
        mitre_rows=mitre_view_rows,
        unresolved_issues=unresolved_issues,
        verification_actions=verification_actions,
        limitations=limitations,
        provenance_rows=provenance_rows,
    )
