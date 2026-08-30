# Thesis Revision Notes — Version 1 to Version 2

## สถานะเอกสาร

Version 1 เป็นร่างเชิงโครงสร้างครบส่วน โดยอ้าง current repository evidence ณ 27 สิงหาคม 2569 ไม่ใช่ฉบับพร้อมส่ง จุดแข็งคือ trust boundary, current-vs-proposed separation, architecture/code-path trace และการจำกัดความหมายของ experimental results จุดที่ยังอ่อนคือภาพหน้าจอ metadata สถาบัน product freeze และ final evaluation

## Consistency audit

| Check | Result | Action |
|---|---|---|
| Title vs scope | PARTIAL | working title กล่าว evidence-grounded/general case อย่างเหมาะสม แต่ต้องอนุมัติชื่อไทย/อังกฤษ |
| Objectives vs implementation | CONSISTENT WITH QUALIFIERS | objective general analysis/report มี integration limitations ที่ระบุแล้ว |
| Architecture vs code | CONSISTENT | ใช้ chat routes/5 tables/direct 1-hop/native-language retrieval; ไม่ใช้ obsolete Case State |
| Chapter 3 vs Chapter 4 | CONSISTENT | design claims มี implementation evidence หรือ label proposed |
| Claimed features vs implemented | CONSISTENT | matrix ระบุ v3/report/frontend/ingestion partial |
| Experiments vs artifacts | CONSISTENT | แยก exploratory และ fixture validation; ไม่อ้าง product effectiveness |
| Conclusions vs evidence | CONSISTENT | สรุป engineering baseline ไม่สรุป accuracy/legal benefit |
| References | MOSTLY STABLE | academic metadata verified; OCR/workload references ยังไม่มี |
| Figures | INCOMPLETE | diagram sources มีแล้ว; screenshots ทั้งหมดยังขาด |
| Runtime validation | INCOMPLETE | automated tests ผ่าน; live E2E ไม่ได้รัน |

## ความไม่สอดคล้องที่ค้นพบใน repository

1. Main Analysis backend สร้าง `analysis_trace_v3` แต่ `mitre-candidate.ts` รับ v2 เท่านั้น และ Overview/Technical Context อ่าน source field แบบ v2
2. Report template อ่าน `source_message_ids` แบบ v2 ไม่ใช่ supporting/contradicting arrays ของ v3
3. `AnalysisTraceV3` มี gaps แต่ provider/parser ปัจจุบันสร้าง `gaps=[]`; operational gaps อยู่ใน `chat_followup.gap_analysis`
4. Main Analysis prompt เป็น domain-neutral แต่ fresh workflow ยังเรียก cyber RAG ทุกครั้งและ UI/report terminology ยัง cyber-oriented
5. RAG architecture documents บางไฟล์กล่าวถึง Thai→English/dual-query และ 2-hop graph expansion แต่ current code ใช้ native-language prepare และ direct-neighbor 1-hop
6. Root README ยังไม่สะท้อน document-ingestion preview ใน dirty working tree
7. Research/deliverable บางชุดอธิบาย Case State หรือ client-side report รุ่นเก่า จึงเป็น historical artifacts ไม่ใช่ current architecture
8. Automated tests ผ่านแม้ v3 consumer semantics ยังขาด แสดงว่า contract tests ข้าม backend/frontend ยังไม่ครอบคลุม
9. Compose มี production-capable Dockerfile stages บางส่วน แต่ composition ปัจจุบันเป็น development; ไม่ควรสรุป production deployment
10. Local context-refinement result อยู่ใน ignored `tmp/` ทำให้ reproducibility/archival status ต่ำกว่าผล tracked

## Top 10 actions before Version 2

1. Freeze commit/branch และจัดการ dirty Analysis v3/document-ingestion work ให้มีสถานะที่อ้างอิงได้
2. ตกลงชื่อเรื่อง ข้อมูลนักศึกษา/อาจารย์ และรูปแบบรายงานสถาบัน
3. แก้ frontend/report v3 readers ผ่าน compatibility normalization กลางและเพิ่ม semantic contract tests
4. ตัดสิน canonical gap model และบันทึก ADR/migration plan ก่อนเปลี่ยน schema
5. ตัดสิน general-case product boundary: cyber applicability gate, UI terminology และ report schema
6. เลือก final evaluation question/dataset/baseline/treatment แล้ว preregister/freeze protocol ก่อนรัน
7. รัน live end-to-end และ failure-injection tests พร้อมเก็บ versions/log receipts โดยไม่เปิดเผย secrets
8. สร้าง screenshots ทั้งหมดจาก synthetic demo data หลัง freeze UI และตรวจ PDF/Thai typography
9. เพิ่ม/คัดเลือก references ด้าน investigative workload, document OCR/HTR และ human-AI decision support เฉพาะ claim ที่จะใช้จริง
10. ตรวจภาษาไทย ความสอดคล้อง citation/figure numbering และจัดรูปเล่ม DOCX/PDF ตาม template ในรอบถัดไป

## ส่วนที่ค่อนข้างเสถียร

- evidence trust boundary และ raw evidence rules
- persisted chat/run/context/report model ห้าตาราง
- route boundaries และ ask-vs-add-vs-clarification semantics
- RAG/MITRE ในฐานะ external context
- deterministic report/idempotency concept
- limitations ที่ไม่มี authentication/legal correctness/expert evaluation

## ส่วนที่ขึ้นกับ implementation

- AnalysisTrace v3 status และ exact prompt version
- frontend/report provenance presentation
- canonical gap/follow-up integration
- document ingestion admission
- cyber applicability gate และ general report shape

## ส่วนที่ขึ้นกับ evaluation

- ข้อสรุปเกี่ยวกับ grounding quality, gap accuracy และ clarification benefit
- ค่า latency/cost บน final model/environment
- Thai-language behavior และ domain transfer
- usefulness, workload และ error detection โดยผู้เชี่ยวชาญ
- legal/forensic correctness ซึ่งอาจอยู่นอกขอบเขตแม้ใน Version 2

