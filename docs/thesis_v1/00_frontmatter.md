# ส่วนต้น

## ชื่อโครงงาน

**ชื่อภาษาไทย (ฉบับใช้งานใน Version 1):** กรอบงานไซเบอร์เคสสำหรับช่วยวิเคราะห์ข้อมูลคดีด้วยปัญญาประดิษฐ์โดยคงการอ้างอิงแหล่งข้อมูล

**English Title (Version 1 working title):** CyberCase Intelligence Framework: An Evidence-Grounded AI-Assisted Case Analysis System

> [VERIFY: ชื่อภาษาไทยและภาษาอังกฤษฉบับสุดท้ายต้องได้รับความเห็นชอบจากนักศึกษาและอาจารย์ที่ปรึกษา]

**จัดทำโดย:** [ชื่อนักศึกษา — PLACEHOLDER]  
**รหัสนักศึกษา:** [PLACEHOLDER]  
**อาจารย์ที่ปรึกษา:** [PLACEHOLDER]  
**หลักสูตร/ภาควิชา/คณะ:** [PLACEHOLDER]  
**มหาวิทยาลัย:** มหาวิทยาลัยเทคโนโลยีพระจอมเกล้าพระนครเหนือ [VERIFY]  
**ปีการศึกษา:** [PLACEHOLDER]

---

## บทคัดย่อ

โครงงาน CyberCase Intelligence Framework มีวัตถุประสงค์เพื่อพัฒนาระบบเว็บสำหรับช่วยผู้ปฏิบัติงานทบทวนข้อมูลคดีที่อยู่ในรูปข้อความ สนับสนุนการสรุปเชิงวิเคราะห์ที่ย้อนกลับไปยังข้อความต้นทางได้ และแยกข้อมูลที่ผู้ใช้รายงานออกจากข้ออนุมานของแบบจำลองภาษาขนาดใหญ่ ระบบมีต้นกำเนิดจากบริบทเหตุการณ์ความมั่นคงปลอดภัยไซเบอร์ จึงมีโมดูลค้นคืนความรู้จาก MITRE ATT&CK เป็นบริบททางเทคนิคภายนอก ขณะเดียวกัน โมดูลวิเคราะห์หลักในสถานะการพัฒนาปัจจุบันกำลังถูกทำให้เป็นกลางต่อโดเมนเพื่อรองรับข้อมูลคดีทั่วไป โดยไม่ทำการวินิจฉัยข้อกฎหมาย ไม่ชี้ความผิด และไม่ใช้ข้อมูลที่แบบจำลองสร้างขึ้นเป็นหลักฐานของคดี

สถาปัตยกรรมของระบบแบ่งเป็นเว็บส่วนติดต่อผู้ใช้ บริการ FastAPI สำหรับจัดเก็บการสนทนาและประสาน workflow ฐานข้อมูล PostgreSQL บริการ GraphRAG แยกต่างหากซึ่งใช้ Qdrant และ Neo4j และบริการสร้างรายงานแบบแม่แบบ ข้อความผู้ใช้ที่มีชนิดเป็นคำบรรยายคดี คำตอบต่อคำถามขอข้อมูลเพิ่ม หรือข้อมูลคดีที่เพิ่มภายหลัง ถูกนำมาสร้างเป็น raw evidence snapshot พร้อมค่าแฮชและรหัสแหล่งที่มา ข้อความผู้ช่วย คำตอบจาก RAG และคำถามทั่วไปในโหมด ask ไม่ถือเป็นหลักฐาน authoritative โมดูล Main Case Analysis สร้างข้อความวิเคราะห์และ AnalysisTrace แบบมีโครงสร้าง ประกอบด้วย analytical claims สถานะทางญาณวิทยา และรหัสข้อความที่สนับสนุนหรือขัดแย้ง จากนั้นโมดูล Gap Analysis และนโยบาย follow-up จะพิจารณาว่าควรถามข้อมูลเพิ่มหรือดำเนินการต่อ รายงานถูกสร้างแบบ deterministic จาก snapshot ที่บันทึกไว้ พร้อม version และ idempotency

ผลการตรวจสอบ current checkout เมื่อวันที่ 27 สิงหาคม 2569 พบว่าชุดทดสอบ backend ผ่าน 147 รายการและ 2 subtests ชุดทดสอบ frontend ผ่าน 88 รายการใน 23 test files และ ESLint ผ่าน อย่างไรก็ดี การตรวจนี้ไม่ได้รวมการทดสอบ live end-to-end ที่เชื่อมต่อ LLM, PostgreSQL, Qdrant และ Neo4j พร้อมกัน งานที่ยังไม่สมบูรณ์ประกอบด้วยการทำให้ frontend และ report readers รองรับ AnalysisTrace v3 ครบถ้วน การรวม gap ให้เป็น canonical model เดียว การเชื่อม document ingestion เข้าสู่ข้อมูลคดี และการประเมินกับผู้เชี่ยวชาญ ผลทดลองที่มีอยู่ใน repository ถูกนำเสนอเป็นการทดลองเชิงสำรวจเท่านั้นและไม่ถูกใช้เพื่ออ้างประสิทธิผลของระบบต่อการทำงานจริง

**คำสำคัญ:** การวิเคราะห์ข้อมูลคดี, แบบจำลองภาษาขนาดใหญ่, การอ้างอิงแหล่งข้อมูล, การสร้างแบบเสริมการค้นคืน, MITRE ATT&CK, คำถามขอข้อมูลเพิ่ม

---

## Abstract

CyberCase Intelligence Framework is a web-based, AI-assisted system for reviewing narrative case information, producing source-traceable analytical summaries, and separating user-reported information from language-model inference. The project originated in a cybersecurity incident-analysis setting and therefore includes optional MITRE ATT&CK retrieval as external technical context. Its current Analysis Module is being generalized toward broader investigative case analysis. The system does not make binding legal decisions, determine guilt, or treat model-generated material as case evidence.

The architecture comprises a Next.js user interface, a FastAPI orchestration and persistence backend, PostgreSQL, a separate GraphRAG service backed by Qdrant and Neo4j, and deterministic report generation. Authoritative raw evidence is reconstructed only from qualifying user-authored case messages and is bound to source-message identifiers and a SHA-256 digest. The Main Case Analysis stage produces prose and a structured AnalysisTrace containing analytical claims, epistemic statuses, and supporting or contradicting source identifiers. Separate gap-analysis and follow-up stages determine whether one focused clarification is required. Persisted reports are generated from an immutable input snapshot with versioning and idempotency controls.

On the repository checkout inspected on 27 August 2026, 147 backend tests and two subtests passed; 88 frontend tests across 23 test files passed; and ESLint passed. These results do not constitute a live end-to-end validation with all databases and model providers. Remaining work includes complete AnalysisTrace v3 adoption by report and frontend readers, canonical integration of analytical gaps, persistent document ingestion, and expert evaluation. Existing repository experiments are reported only as exploratory evidence and do not establish operational or legal effectiveness.

**Keywords:** case analysis, large language model, source provenance, retrieval-augmented generation, MITRE ATT&CK, clarification question

---

## กิตติกรรมประกาศ

[PLACEHOLDER: นักศึกษาเขียนกิตติกรรมประกาศ โดยระบุเฉพาะบุคคลและหน่วยงานที่มีส่วนสนับสนุนจริง]

---

## สารบัญฉบับร่าง

1. บทที่ 1 บทนำ
   - 1.1 ความเป็นมาและความสำคัญ
   - 1.2 ปัญหาที่ต้องการแก้ไข
   - 1.3 วัตถุประสงค์
   - 1.4 ขอบเขต
   - 1.5 ประโยชน์ที่คาดว่าจะได้รับ
2. บทที่ 2 ทฤษฎีและงานที่เกี่ยวข้อง
3. บทที่ 3 วิธีการดำเนินงานและการออกแบบระบบ
4. บทที่ 4 การพัฒนาระบบ
5. บทที่ 5 ผลการดำเนินงาน
6. บทที่ 6 สรุปผลและแนวทางการพัฒนาต่อ
7. บรรณานุกรม

> [TODO: สร้างเลขหน้าอัตโนมัติเมื่อจัดทำ DOCX/PDF ใน Version ถัดไป]

## สารบัญภาพฉบับร่าง

- รูปที่ 3-1 สถาปัตยกรรมระบบ CyberCase
- รูปที่ 3-2 ขอบเขตความน่าเชื่อถือของข้อมูล
- รูปที่ 3-3 แผนภาพ Use Case
- รูปที่ 3-4 ลำดับการวิเคราะห์คดีครั้งแรก
- รูปที่ 3-5 ลำดับการถามคำถามเกี่ยวกับผลวิเคราะห์
- รูปที่ 3-6 ลำดับการเพิ่มข้อมูลและตอบ clarification
- รูปที่ 3-7 ลำดับการสร้างรายงาน
- รูปที่ 3-8 แบบจำลองความสัมพันธ์ฐานข้อมูล
- รูปที่ 5-1 ถึง 5-10 ภาพหน้าจอพื้นที่ทำงานของระบบ [FIGURE NEEDED]

## สารบัญตารางฉบับร่าง

- ตารางที่ 1-1 ขอบเขตและสถานะของโครงงาน
- ตารางที่ 2-1 ความสัมพันธ์ระหว่างทฤษฎีกับการตัดสินใจออกแบบ
- ตารางที่ 3-1 ผู้เกี่ยวข้องและสิทธิการกระทำเชิงแนวคิด
- ตารางที่ 3-2 คำอธิบายกรณีใช้งานหลัก
- ตารางที่ 3-3 การจัดชั้นข้อมูลตาม trust boundary
- ตารางที่ 3-4 สรุป failure policy
- ตารางที่ 4-1 เทคโนโลยีที่ใช้ในการพัฒนา
- ตารางที่ 4-2 วิธีจัดการความล้มเหลว
- ตารางที่ 5-1 ผลการพัฒนาตามองค์ประกอบ
- ตารางที่ 5-2 ผลการทดสอบอัตโนมัติ
- ตารางที่ 5-3 ผลการทดลองเชิงสำรวจ
