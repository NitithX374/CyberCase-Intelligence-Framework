from __future__ import annotations;

from datetime import datetime, timezone
import re
from typing import Final

from app.services.reports.report_view_model_contracts import IndicatorViewRow

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
