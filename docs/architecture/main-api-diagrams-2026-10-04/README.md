# CyberCase — API หลักแยกตามระบบ

ตรวจจากโค้ดที่ HEAD `5fdfb4d6` และ live OpenAPI วันที่ 2026-10-04

แต่ละรูปแสดง frontend → HTTP API → backend → persistence/processing → response → frontend consumer

- เปิด `index.html` เพื่อดูทั้ง 7 รูป
- เปิด `cybercase-main-api-diagrams.drawio` ใน draw.io เพื่อแก้ไขทั้ง 7 หน้า
- แต่ละระบบมีไฟล์ `.drawio` แยก พร้อมภาพ `.png` / `.svg` และหน้า `.html`

| ระบบ | ไฟล์แก้ไข | ภาพ |
|---|---|---|
| 1. เข้าสู่ระบบและ Session | [draw.io](01-auth.drawio) | [PNG](01-auth.png) |
| 2. จัดการเคส | [draw.io](02-cases.drawio) | [PNG](02-cases.png) |
| 3. เพิ่มข้อความ เอกสาร และเปิดหลักฐาน | [draw.io](03-sources-documents.drawio) | [PNG](03-sources-documents.png) |
| 4. วิเคราะห์เคส | [draw.io](04-analysis.drawio) | [PNG](04-analysis.png) |
| 5. แชตทั่วไปกับเคส | [draw.io](05-chat.drawio) | [PNG](05-chat.png) |
| 6. ตอบคำถามเพิ่มเติมและวิเคราะห์ต่อ | [draw.io](06-followup.drawio) | [PNG](06-followup.png) |
| 7. รายงานและดาวน์โหลด PDF / HTML | [draw.io](07-reports.drawio) | [PNG](07-reports.png) |

API base: `http://localhost:8000/api/v1`  
Frontend: `http://localhost:3000`  
เส้น frontend/backend ส่ง session cookie; Analysis และ Chat POST ใช้ SSE

Chat และ Follow-up ใช้ `POST /cases/{case_id}/chat/messages` ร่วมกัน โดย backend เลือกทางตาม pending question. Follow-up เก็บเป็น ChatMessage / QA context. RAG เป็นการเรียกภายในจาก backend ไป `rag-service:8001/query`.

Analysis ปัจจุบันทำ `case_reading → bound_claims → case_judgement → bound_references`. Judgement รับ checked reading, follow-up QA และ optional technical context. Report สร้างจาก snapshot ของ analysis ที่เลือก.

## จุดอ้างอิงในโค้ด

- **1. เข้าสู่ระบบและ Session**: `frontend/src/features/auth/api.ts`, `backend/app/auth/routes.py`, `frontend/src/features/auth/useAuth.ts`
- **2. จัดการเคส**: `frontend/src/features/cases/api.ts`, `backend/app/cases/routes.py`
- **3. เพิ่มข้อความ เอกสาร และเปิดหลักฐาน**: `frontend/src/features/sources/api.ts`, `frontend/src/features/sources/useCaseSourceActions.ts`, `backend/app/sources/routes.py`, `backend/app/sources/ingestion/service.py`
- **4. วิเคราะห์เคส**: `frontend/src/features/analysis/api.ts`, `frontend/src/features/analysis/useRunCaseAnalysis.ts`, `backend/app/analysis/routes.py`, `backend/app/analysis/run.py`, `backend/app/analysis/pipeline.py`, `backend/app/analysis/write.py`, `backend/app/analysis/store.py`
- **5. แชตทั่วไปกับเคส**: `frontend/src/features/chat/api.ts`, `frontend/src/features/chat/useCaseChat.ts`, `backend/app/chat/routes.py`, `backend/app/chat/reply.py`, `backend/app/chat/answer.py`, `backend/app/chat/compose.py`
- **6. ตอบคำถามเพิ่มเติมและวิเคราะห์ต่อ**: `frontend/src/features/chat/useCaseChat.ts`, `backend/app/chat/reply.py`, `backend/app/followup/clarification.py`, `backend/app/analysis/run.py`
- **7. รายงานและดาวน์โหลด PDF / HTML**: `frontend/src/features/reports/api.ts`, `backend/app/reports/routes.py`, `backend/app/reports/generate.py`

## การตรวจสอบ

ดู [VERIFICATION.md](VERIFICATION.md). นิยามข้อความใน [diagram-specs.json](diagram-specs.json) ตรงกับ Mermaid ที่ส่งให้ draw.io MCP. ไฟล์ draw.io เขียนเป็น native XML; ภาพ PNG rasterize จาก SVG ด้วย Edge headless.

