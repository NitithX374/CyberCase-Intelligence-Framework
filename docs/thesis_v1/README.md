# CyberCase Intelligence Framework — Thesis Version 1

เอกสารชุดนี้เป็น **Thesis Version 1 — complete structural draft based on current repository evidence** สำหรับโครงงานระดับปริญญาตรี โดยใช้สถานะ repository ณ วันที่ 27 สิงหาคม 2569 (2026) เป็นฐาน ไม่ใช่ฉบับพร้อมส่ง และไม่ใช่เอกสารรับรองประสิทธิผลทางกฎหมายหรือทางปฏิบัติการ

## ขอบเขตสถานะที่ใช้ในการเขียน

- `main` และ `origin/main` อยู่ที่ commit `cdb66972dce7a9e475f3fbfd1ad7c04c9d511160`
- working tree มีงานของผู้ใช้ที่ยังไม่ commit โดยเฉพาะ AnalysisTrace v3, general case analysis และ document-ingestion preview
- เนื้อหาแยกคำว่า **ใช้งานแล้ว**, **ใช้งานแล้วเฉพาะคดีไซเบอร์**, **อยู่ระหว่างบูรณาการ**, และ **แนวทางที่เสนอ**
- ตัวเลขทดสอบมาจากการรันปัจจุบัน: backend 147 tests ผ่านและ 2 subtests ผ่าน; frontend 88 tests ใน 23 files ผ่าน; ESLint ผ่าน
- ไม่ได้รัน live end-to-end กับ PostgreSQL, LLM provider, Qdrant และ Neo4j ในงานเขียนรอบนี้

## ไฟล์ตัวบท

1. [ส่วนต้น](00_frontmatter.md)
2. [บทที่ 1 บทนำ](01_chapter_1_introduction.md)
3. [บทที่ 2 ทฤษฎีและงานที่เกี่ยวข้อง](02_chapter_2_related_theory.md)
4. [บทที่ 3 วิธีการดำเนินงานและการออกแบบระบบ](03_chapter_3_methodology.md)
5. [บทที่ 4 การพัฒนาระบบ](04_chapter_4_implementation.md)
6. [บทที่ 5 ผลการดำเนินงาน](05_chapter_5_results.md)
7. [บทที่ 6 สรุปผลและแนวทางการพัฒนาต่อ](06_chapter_6_conclusion.md)

## ไฟล์กำกับความจริงและการแก้ไข

- [Evidence ledger](thesis_evidence_ledger.md)
- [Implemented vs proposed](implemented_vs_proposed.md)
- [แผนภาพและตาราง](figures_and_tables_plan.md)
- [ตรวจบรรณานุกรม](references_review.md)
- [คำถามเปิด](open_questions.md)
- [บันทึกการแก้ไข Version 2](thesis_revision_notes.md)
- [BibTeX](references.bib)

## โครงร่างสาระ

บทที่ 1 วางปัญหา วัตถุประสงค์ ขอบเขต และประโยชน์โดยไม่อ้างภาระงานของบุคลากรเกินหลักฐาน บทที่ 2 อธิบาย LLM, structured generation, RAG, retrieval, knowledge graph, ATT&CK, provenance, uncertainty, clarification และ document understanding บทที่ 3 อธิบายสถาปัตยกรรมและ trust boundary ตาม code path จริง บทที่ 4 อธิบายการพัฒนาและจุดบูรณาการที่ยังไม่สมบูรณ์ บทที่ 5 รายงานสิ่งที่ทำงาน ผลทดสอบ และ exploratory experiments บทที่ 6 สรุปข้อจำกัดและแผนระยะสั้น/ยาว

## วิธีใช้ร่างนี้

ก่อน Version 2 ให้ตอบคำถามใน `open_questions.md`, สร้างภาพหน้าจอตาม `figures_and_tables_plan.md`, ตัดสินใจว่าจะใช้ผลทดลองใดเป็นผลหลัก และตรวจภาษา/รูปแบบตามคู่มือสถาบัน จากนั้นตรวจทุก claim ที่แก้ไขกับ `thesis_evidence_ledger.md` อีกครั้ง

