from __future__ import annotations

from app.reports.contracts import CaseReportInput
from app.trace.trace import CaseAnalysisTrace

CLARIFICATION_LIMITATIONS = {
    "max_rounds_reached": (
        "ระบบใช้สิทธิ์ถามข้อมูลเพิ่มเติมจนครบจำนวนรอบที่กำหนดแล้ว "
        "ประเด็นที่ยังค้างอยู่ในหัวข้อข้อมูลที่ยังขาด จึงยังไม่ได้ถาม ไม่ใช่ว่าไม่จำเป็นต้องถาม"
    ),
    "gaps_exhausted": ("ระบบถามทุกประเด็นที่ถามได้แล้ว ประเด็นที่ยังค้างอยู่คือสิ่งที่ผู้ใช้ตอบไม่ได้ หรือหลักฐานที่มีตอบไม่ได้"),
    "no_eligible_gap": (
        "ประเด็นที่ยังค้างอยู่ไม่มีข้อใดที่การถามผู้ใช้จะช่วยได้ "
        "เพราะเป็นเรื่องที่ผู้ใช้ระบุว่าไม่ทราบ หรือต้องยืนยันจากหลักฐานเพิ่มเติมแทนการสอบถาม"
    ),
}


def clarification_limitation(trace: CaseAnalysisTrace) -> str | None:
    return CLARIFICATION_LIMITATIONS.get(trace.stop_reason or "")


def report_limitations(report_input: CaseReportInput) -> list[str]:
    limitations = [
        "รายงานนี้เป็นการวิเคราะห์เบื้องต้นจากหลักฐานที่ถูกนำเข้าสู่ Case และยังต้องตรวจสอบโดยผู้ปฏิบัติงาน",
        "ข้อเท็จจริงและตัวบ่งชี้อ้างอิงได้เฉพาะหลักฐานของคดีและคำตอบที่ผู้ใช้ให้ไว้ในคำถามติดตามผล "
        "คำตอบเหล่านั้นเป็นคำบอกเล่าของผู้ใช้ ยังไม่ได้ผ่านการตรวจสอบกับหลักฐาน "
        "และไม่รวมข้อมูลภายนอกอื่นใด",
        "ระบบไม่ใช่ผู้วินิจฉัยข้อเท็จจริงหรือข้อกฎหมาย และไม่ควรใช้รายงานนี้แทนการใช้ดุลยพินิจของพนักงานสอบสวนหรืออัยการ",
        "หากเอกสารต้นฉบับไม่ครบ อ่านไม่ชัด หรือมีข้อมูลขัดแย้ง รายงานอาจสะท้อนข้อจำกัดดังกล่าว",
    ]
    augmentation = report_input.technical_augmentation
    if augmentation is None:
        limitations.append("ผลการเสริมข้อมูล MITRE ไม่พร้อมใช้งาน จึงไม่มีการยืนยัน mapping จากข้อมูลภายนอก")
    elif augmentation.status == "not_applicable":
        limitations.append("ระบบไม่พบเงื่อนไขที่จำเป็นต้องใช้ MITRE ATT&CK กับคดีนี้")
    elif augmentation.status == "insufficient_context":
        limitations.append("ข้อมูลทางเทคนิคภายนอกไม่เพียงพอสำหรับการจัดทำ mapping")
    elif augmentation.status == "retrieved_from_rag":
        limitations.append(
            "ระบบยอมรับรายการ MITRE ทั้งหมดจาก RAG service เป็นบริบททางเทคนิคภายนอก โดยไม่ถือเป็นหลักฐานของคดีหรือการเชื่อมโยงกับ claim"
        )
    elif augmentation.status == "failed":
        limitations.append("การเสริมข้อมูล MITRE ขัดข้อง จึงไม่ควรใช้ส่วน mapping เป็นข้อสรุปของคดี")
    else:
        limitations.append("MITRE ATT&CK ในรายงานเป็นบริบทภายนอกเพื่อช่วยจัดหมวดพฤติกรรม ไม่ใช่หลักฐานของคดี")

    clarification = clarification_limitation(report_input.analysis_trace)
    if clarification is not None:
        limitations.append(clarification)
    meaning = meaning_pointer_limitation(report_input.analysis_trace)
    if meaning is not None:
        limitations.append(meaning)
    limitations.extend(source_check_limitations(report_input.analysis_trace))
    return limitations


MEANING_POINTER_REASONS = {
    "weights_missing": "ไม่พบไฟล์น้ำหนักของโมเดล",
    "libraries_missing": "ไม่ได้ติดตั้งไลบรารีที่โมเดลต้องใช้",
    "weights_hash_mismatch": "ไฟล์น้ำหนักของโมเดลไม่ตรงกับรุ่นที่กำหนด",
    "label_mapping_mismatch": "ลำดับป้ายผลของโมเดลไม่ตรงกับที่คาดไว้",
}


def meaning_pointer_limitation(trace: CaseAnalysisTrace) -> str | None:
    grounding = trace.grounding
    if grounding is None or not grounding.meaning_pointer_unavailable:
        return None
    reason = grounding.meaning_pointer_unavailable_reason or ""
    shown = MEANING_POINTER_REASONS.get(reason, "โมเดลโหลดหรือทำงานไม่สำเร็จ")
    return (
        "การหาข้อความในต้นฉบับจากความหมายสำหรับข้อที่ยังไม่ยืนยันใช้ไม่ได้ในการวิเคราะห์นี้ "
        f"({shown}) จึงไม่มีข้อความที่อาจเกี่ยวข้องให้ตรวจสำหรับ "
        f"{grounding.meaning_pointer_unavailable} รายการ"
    )


def source_check_limitations(trace: CaseAnalysisTrace) -> list[str]:
    checks = [claim.semantic_grounding for claim in trace.claims if claim.semantic_grounding]
    limitations = []
    if any(check.verdict == "not_supported" for check in checks):
        limitations.append(
            "ป้ายเตือนจากตัวตรวจอัตโนมัติว่า Source รองรับข้อค้นพบหรือไม่ เป็นเพียงสัญญาณคัดกรอง "
            "ไม่ใช่คำตัดสินว่าข้อค้นพบถูกหรือผิด"
        )
    if any(check.reason == "verifier_unavailable" for check in checks):
        limitations.append(
            "ตัวตรวจอัตโนมัติว่า Source รองรับข้อค้นพบหรือไม่ ไม่พร้อมใช้งานในการวิเคราะห์นี้ "
            "ข้อค้นพบจึงยังไม่ได้ผ่านการตรวจดังกล่าว"
        )
    return limitations
