# Open Questions for Version 2

คำถามเหล่านี้มีผลต่อวิทยานิพนธ์อย่างมีนัยสำคัญ แต่ไม่ขัดขวาง Version 1

1. ชื่อโครงงานภาษาไทยและภาษาอังกฤษฉบับที่อาจารย์อนุมัติคืออะไร
2. ชื่อนักศึกษา รหัสนักศึกษา ชื่ออาจารย์ที่ปรึกษา หลักสูตร ภาควิชา คณะ และปีการศึกษาที่ถูกต้องคืออะไร
3. เอกสารนี้เป็น “โครงงานพิเศษ”, “ปริญญานิพนธ์”, “สหกิจศึกษา” หรือรูปแบบอื่นตามระเบียบ KMUTNB และ template ฉบับใด
4. สถานะที่จะ freeze เป็น product baseline สำหรับ thesis คือ commit ใด งาน AnalysisTrace v3/document ingestion ใน dirty working tree จะ commit ก่อน freeze หรือไม่
5. เป้าหมายผลิตภัณฑ์ฉบับสุดท้ายยังใช้ MITRE RAG ทุก fresh run หรือจะเพิ่ม cyber-applicability gate ก่อน Version 2
6. Canonical Analysis Module จะให้ `AnalysisTraceV3.gaps` เป็นแหล่งเดียว หรือคง `chat_followup.gap_analysis` แยก และจะ migrate v2 อย่างไร
7. Frontend/report v3 integration จะเสร็จก่อนถ่าย screenshots หรือ thesis ต้องแสดง current limitation ในภาพ
8. Document ingestion ถือเป็น scope ส่งมอบของนักศึกษาหรือเป็นงานต่อยอด และจะหยุดที่ preview หรือมี human-confirmed admission เข้าสำนวน
9. การทดลองใดจะเป็นผลหลักของ Chapter 5: current exploratory artifacts, one-bounded-clarification study ที่วางแผนไว้ หรือ end-to-end v3 evaluation ใหม่
10. Final evaluation dataset มาจากที่ใด มี license/permission อย่างไร จำนวน case/domain/language เท่าใด และใครสร้าง gold claims/gaps/source links
11. มีผู้เชี่ยวชาญอัยการ ผู้สืบสวน นิติวิทยาศาสตร์ หรืออาจารย์กี่คนที่จะประเมินผล และมี ethics/consent/data-governance requirement ใด
12. Report final scope ต้องเป็น preliminary cyber analysis report เจ็ดส่วนเดิม หรือ general case report ที่ไม่บังคับ MITRE sections
13. ต้องการรวม Legal RAG ในเอกสารในฐานะ “งานของโครงการอื่น” หรือไม่ หากรวม ใครเป็นเจ้าของ scope และมีหลักฐานแยกอย่างไร
14. มี environment ที่อนุญาตให้รัน live end-to-end กับ PostgreSQL, Qdrant, Neo4j และ LLM เพื่อเก็บ validation receipts และ screenshots หรือไม่
15. ภาพหน้าจอใดต้องใช้ภาษาไทยทั้งหมด และมีข้อมูลสังเคราะห์มาตรฐานสำหรับ demo หรือยัง
16. รูปแบบบรรณานุกรมของสถาบันคือ IEEE, APA, Vancouver หรือรูปแบบเฉพาะ และรองรับ Pandoc citation keys หรือไม่

