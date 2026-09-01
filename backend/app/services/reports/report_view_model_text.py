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
        "doc_title": "รายงานสรุปผลการวิเคราะห์คดีเบื้องต้น",
        "running_header": "รายงานสรุปผลการวิเคราะห์คดี / ฉบับเบื้องต้น",
        "page_label": "หน้า",
        "end_of_report": "สิ้นสุดรายงาน - เอกสารฉบับเบื้องต้น",
        # Meta
        "lbl_case_title": "กรณี / หัวข้อ:",
        "lbl_generated_date": "วันที่จัดทำรายงาน:",
        "lbl_report_status": "สถานะรายงาน:",
        "status_provisional": "รายงานเบื้องต้น / ยังไม่ได้รับการยืนยัน (Provisional / Unverified)",
        # Section Headings (Standalone 1..7)
        "sec_1": "1. บทสรุปคดี",
        "sec_2": "2. ลำดับเหตุการณ์สำคัญ",
        "sec_3": "3. ข้อเท็จจริงที่รายงานและแหล่งอ้างอิง",
        "sec_4": "4. บริบททางเทคนิคภายนอก (ถ้ามี)",
        "sec_5": "5. ประเด็นที่ต้องยืนยันเพิ่มเติม",
        "sec_6": "6. แนวทางตรวจสอบเพิ่มเติม",
        "sec_7": "7. ขอบเขตและข้อจำกัด",
        # Backward-compat aliases
        "sec_5_1": "1. ภาพรวมเหตุการณ์",
        "sec_5_2": "2. ลำดับเหตุการณ์สำคัญ",
        "sec_5_3": "3. ข้อเท็จจริงและหลักฐานสำคัญ",
        "sec_5_4": "4. ข้อมูลอ้างอิง MITRE ATT&CK ที่เกี่ยวข้อง",
        "sec_5_5": "4. ข้อมูลอ้างอิง MITRE ATT&CK ที่เกี่ยวข้อง",
        "sec_5_6": "5. ประเด็นที่ยังไม่สามารถยืนยันได้",
        "sec_5_7": "7. ข้อจำกัดของรายงาน",
        # Subheaders & Tables
        "sub_evidence_reg": "รายการข้อเท็จจริงจากบทวิเคราะห์ที่ผูกกับข้อมูลต้นทาง",
        "sub_iocs": "ตัวบ่งชี้ทางเทคนิคที่พบในสำนวน (Technical Indicators / IOCs)",
        "sub_mitre_intro": "MITRE ATT&CK เป็นข้อมูลอ้างอิงทางเทคนิคภายนอก การเชื่อมโยงเหล่านี้เป็นผลการวิเคราะห์เบื้องต้น และไม่ใช่หลักฐานยืนยันว่าเทคนิคดังกล่าวเกิดขึ้นจริงในคดี",
        "sub_unresolved": "ประเด็นที่ยังไม่สามารถยืนยันได้ (Unconfirmed Information / Gaps)",
        "sub_next_steps": "ประเด็นที่ควรตรวจสอบเพิ่มเติม (Investigative Next Steps)",
        "sub_limitations": "ข้อจำกัดของรายงาน (Report Limitations)",
        "sub_provenance": "ภาคผนวก: ข้อมูลตรวจสอบย้อนกลับของรายงาน",
        # Table Columns
        "col_order": "ลำดับ",
        "col_time": "วัน / เวลา",
        "col_event": "เหตุการณ์",
        "col_source_evidence": "แหล่งข้อมูล / หลักฐาน",
        "col_item": "รายการ",
        "col_type": "ประเภท",
        "col_description": "รายละเอียด",
        "col_source": "แหล่งข้อมูล",
        "col_ioc_type": "ประเภท",
        "col_ioc_value": "ค่าตัวบ่งชี้",
        "col_ioc_note": "หมายเหตุ / บริบท",
        "col_finding": "ข้อค้นพบ / แท็กติก",
        "col_case_support": "เหตุผลที่เกี่ยวข้องกับคดี",
        "col_mitre": "MITRE ATT&CK",
        "col_mapping_status": "สถานะการวิเคราะห์",
        "col_prov_item": "รายการตรวจสอบ",
        "col_prov_value": "ค่าระบุตัวตน / ข้อมูลสถิติ",
        # Fallbacks
        "empty_summary": "ไม่มีข้อมูลสรุปเหตุการณ์ที่บันทึกไว้ในสแนปช็อตนี้",
        "empty_timeline": "ไม่พบข้อมูลลำดับเหตุการณ์ที่บันทึกไว้ในสแนปช็อตนี้",
        "empty_evidence": "ไม่พบรายการหลักฐานที่บันทึกไว้ในสแนปช็อตนี้",
        "empty_mitre": "ไม่ใช้บริบท MITRE ATT&CK กับกรณีนี้",
        "empty_gaps": "ไม่พบข้อขัดแย้งหรือประเด็นขาดหายที่ตรวจพบในสแนปช็อตนี้",
        "actor_prefix": "ผู้เกี่ยวข้อง",
        "status_candidate": "ข้อสันนิษฐานเชิงวิเคราะห์ (Candidate analytical association)",
        "status_reported_analysis": "อ้างอิงในบทวิเคราะห์ (Reported in Analysis)",
        "retrieval_source": "แหล่งอ้างอิง",
    },
    "en": {
        "org_header": "CYBERCASE INTELLIGENCE FRAMEWORK",
        "doc_title": "Preliminary Case Analysis Report",
        "running_header": "CASE ANALYSIS REPORT / PRELIMINARY",
        "page_label": "Page",
        "end_of_report": "End of report - preliminary document",
        # Meta
        "lbl_case_title": "Case / Title:",
        "lbl_generated_date": "Generated Date:",
        "lbl_report_status": "Report Status:",
        "status_provisional": "Provisional / Unverified Case Analysis Report",
        # Section Headings
        "sec_1": "1. Case Summary",
        "sec_2": "2. Key Chronology",
        "sec_3": "3. Reported Facts and Source References",
        "sec_4": "4. External Technical Context (if applicable)",
        "sec_5": "5. Matters Requiring Verification",
        "sec_6": "6. Further Verification Actions",
        "sec_7": "7. Scope and Limitations",
        # Backward-compat aliases
        "sec_5_1": "1. Incident Summary",
        "sec_5_2": "2. Key Incident Progression",
        "sec_5_3": "3. Key Facts & Case Evidence",
        "sec_5_4": "4. Relevant MITRE ATT&CK Context",
        "sec_5_5": "4. Relevant MITRE ATT&CK Context",
        "sec_5_6": "5. Unconfirmed Information & Gaps",
        "sec_5_7": "7. Report Limitations",
        # Subheaders & Tables
        "sub_evidence_reg": "Analysis findings linked to source material",
        "sub_iocs": "Technical Indicators of Compromise (IOCs)",
        "sub_mitre_intro": "MITRE ATT&CK is external technical reference knowledge. Associated techniques represent preliminary analytical correlations and are not proof that the technique occurred in the incident.",
        "sub_unresolved": "Unconfirmed Information & Gaps",
        "sub_next_steps": "Points for Further Investigation",
        "sub_limitations": "Report Limitations",
        "sub_provenance": "Appendix: Report Traceability",
        # Table Columns
        "col_order": "No.",
        "col_time": "Date / Time",
        "col_event": "Event Description",
        "col_source_evidence": "Source Evidence Reference",
        "col_item": "Item",
        "col_type": "Type",
        "col_description": "Description",
        "col_source": "Source",
        "col_ioc_type": "Indicator Type",
        "col_ioc_value": "Indicator Value",
        "col_ioc_note": "Context / Association",
        "col_finding": "Finding / Tactic",
        "col_case_support": "Case Association Rationale",
        "col_mitre": "MITRE ATT&CK",
        "col_mapping_status": "Analytical Status",
        "col_prov_item": "Audit Item",
        "col_prov_value": "Identifier / Value",
        # Fallbacks
        "empty_summary": "No incident summary records were persisted for this snapshot.",
        "empty_timeline": "No incident progression events were persisted for this snapshot.",
        "empty_evidence": "No evidence items were persisted for this snapshot.",
        "empty_mitre": "MITRE ATT&CK context is not applicable to this case.",
        "empty_gaps": "No analytical gaps or contradictions were identified for this snapshot.",
        "actor_prefix": "Actors",
        "status_candidate": "Candidate analytical association",
        "status_reported_analysis": "Reported in Analysis",
        "retrieval_source": "Reference Source",
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
