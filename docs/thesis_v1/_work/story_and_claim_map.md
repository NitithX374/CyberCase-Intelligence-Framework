# Story and claim map

## แกนเรื่อง

ข้อมูลคดีแบบข้อความยาวและไม่เป็นโครงสร้างทำให้การทบทวนยากขึ้น แต่การส่งข้อมูลทั้งหมดให้ LLM ทั่วไปสร้างคำตอบทันทีทำให้แยกข้อเท็จจริง การอนุมาน และความไม่แน่นอนได้ยาก CyberCase จึงจัด workflow รอบขอบเขตความน่าเชื่อถือของข้อมูล: สร้าง raw evidence จากข้อความผู้ใช้ วิเคราะห์เป็น claims ที่ย้อนกลับไปยังแหล่งที่มา แยก gap/follow-up ออกจาก Main Analysis ใช้ MITRE เป็นบริบทภายนอกสำหรับคดีไซเบอร์ และสร้างรายงานแบบ deterministic จาก snapshot ที่บันทึกไว้

## Claims หลักที่อนุญาต

1. ระบบปัจจุบันมี persisted chat workflow, run, retrieval context และ chat-scoped report
2. Raw evidence ไม่รวมข้อความผู้ช่วยและไม่รวมคำถาม ask ทั่วไปของผู้ใช้
3. Main Analysis v3 ใน working tree เป็น domain-neutral และแยก reported/inference/unknown
4. Provenance v3 ผ่าน `supporting_source_message_ids` และ `contradicting_source_message_ids` พร้อม fail-closed validation
5. Gap Analysis และ follow-up เป็น stages แยกต่างหาก; taxonomy มี 4 สถานะและห้ามถามสิ่งที่ explicitly unknown
6. RAG/MITRE เป็น external technical context ไม่ใช่หลักฐานคดี
7. Report generation เป็น template/deterministic, versioned และ idempotent แต่ report/frontend readers บางส่วนยัง v2-shaped
8. Document ingestion ปัจจุบันเป็น preview-only; OCR มี Typhoon; HTR ยังไม่รองรับและไม่ป้อนผลเข้าการวิเคราะห์
9. Automated tests ผ่านตามผลรันวันที่ 2026-08-27 แต่ไม่ได้แทน live end-to-end หรือ user study
10. ผลทดลองที่มีเป็น exploratory และไม่พิสูจน์ประสิทธิผลของ product ปัจจุบัน

## Claims ที่ห้ามใช้

- ระบบแม่นยำหรือปลอด hallucination
- รองรับงานอัยการจริงหรือผ่านการประเมินผู้เชี่ยวชาญแล้ว
- ทำ legal reasoning / Legal RAG / ตัดสินความผิด
- ingestion บันทึกเอกสารเข้าสำนวนหรือเชื่อม analysis แล้ว
- graph expansion หลักเป็น 2-hop หรือระบบแปลไทยเป็นอังกฤษก่อนค้นเสมอ
- มี production deployment, multi-user authentication หรือ per-user authorization

