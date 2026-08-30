# บทที่ 3 วิธีการดำเนินงานและการออกแบบระบบ

## 3.1 ภาพรวมระบบ CyberCase

CyberCase เป็นระบบหลายบริการสำหรับรับข้อมูลคดีจากผู้ใช้ สร้างหลักฐานดิบที่มีขอบเขตชัดเจน เพิ่มบริบททางเทคนิคเมื่อเกี่ยวข้อง วิเคราะห์ข้อมูลด้วย LLM ประเมินช่องว่าง ถามข้อมูลเพิ่ม และสร้างรายงานที่บันทึกไว้ แนวคิดศูนย์กลางคือผลวิเคราะห์เป็น derived state ซึ่งต้องย้อนกลับไปยัง input ที่ได้รับอนุญาต ไม่ใช่แหล่งหลักฐานใหม่

เส้นทางเชิงแนวคิดมีดังนี้

```text
ข้อความข้อมูลคดีจากผู้ใช้
          ↓
Raw Evidence Snapshot ──────────────┐
          ↓                         │ authoritative
Optional MITRE Retrieval            │ evidence boundary
          ↓ external context        │
Main Case Analysis                  │
          ↓                         │
AnalysisTrace + visible prose       │
          ↓                         │
Gap Analysis → Follow-up question ──┘ เมื่อผู้ใช้ตอบ
          ↓
Persisted analysis / Report snapshot
```

ภาพสถาปัตยกรรมฉบับสร้างจากโค้ดอยู่ที่ [architecture.mmd](diagrams/architecture.mmd) โดยแยก frontend, backend, PostgreSQL, provider และ RAG service ออกจากกัน จุดสำคัญคือ browser ไม่ติดต่อ Qdrant, Neo4j หรือ model provider โดยตรง แต่เรียก backend API ภายใต้ `/api/v1` และ backend เป็นผู้ประสาน service boundary

## 3.2 ผู้ใช้งานระบบ

ผู้ใช้งานเชิงเป้าหมายคือผู้ปฏิบัติงานที่ต้องทบทวนข้อมูลคดี เช่น ผู้สืบสวนหรืออัยการ แต่ repository ปัจจุบันไม่มี user model, authentication หรือ role-based access control ดังนั้นคำว่า “อัยการ/ผู้สืบสวน” ในบทนี้หมายถึง persona สำหรับออกแบบ ไม่ใช่ role ที่ถูกบังคับใช้ในซอฟต์แวร์

### ตารางที่ 3-1 ผู้เกี่ยวข้องและความรับผิดชอบ

| ผู้เกี่ยวข้อง | การกระทำ | ข้อจำกัด |
|---|---|---|
| ผู้ใช้ | สร้าง thread, ส่งคำบรรยายคดี, ตอบ clarification, เพิ่มข้อมูล, ถามผลวิเคราะห์, ดูรายงาน | ต้องตรวจทานผลลัพธ์; ระบบไม่มีบัญชีผู้ใช้แยก |
| Frontend | แสดง workspace, สถานะ, source popover, technical context และ report | ไม่เป็นผู้ตัดสิน authority ของ evidence |
| Backend | จัดเก็บข้อมูล, สร้าง evidence snapshot, ประสาน workflow และ validate outputs | เป็น service boundary หลัก |
| LLM provider | สร้าง structured analysis/gap/policy output | ไม่มี authority เหนือข้อมูลคดี |
| RAG service | ค้นและจัดเตรียม MITRE context | ใช้เฉพาะ external technical context |
| PostgreSQL | เก็บ thread/message/run/context/report | ไม่มี per-user tenant boundary |

## 3.3 Use Case Diagram

Use cases หลักประกอบด้วยการสร้างพื้นที่คดี ส่งคำบรรยาย วิเคราะห์ ทบทวนแหล่งที่มา ถามคำถาม เพิ่มข้อมูล ตอบ clarification ดู technical context สร้างรายงาน ดูประวัติรายงาน และดาวน์โหลด PDF แผนภาพ PlantUML อยู่ที่ [use_case.puml](diagrams/use_case.puml)

การใช้คำว่า “case” ใน UI หมายถึงพื้นที่ทำงานของ chat thread ไม่ได้หมายความว่ามีตาราง `cases` หรือ standalone case API ข้อแตกต่างนี้ต้องรักษาไว้เพื่อไม่ให้ design diagram ขัดกับ persistence model จริง

## 3.4 คำอธิบายกรณีใช้งาน

### ตารางที่ 3-2 กรณีใช้งานหลัก

| Use case | Preconditions | Main flow | ผลลัพธ์/ข้อผิดพลาด |
|---|---|---|---|
| UC-01 สร้างพื้นที่คดี | backend/database พร้อม | ผู้ใช้สร้าง chat thread | ได้ thread ID และสถานะ idle |
| UC-02 ส่งคำบรรยายแรก | thread ยังไม่มี initial narrative | บันทึก user message และสร้าง run แบบ 202 Accepted | worker ประมวลผล หรือ run failed พร้อม error metadata |
| UC-03 ทบทวนผลวิเคราะห์ | มี assistant analysis | frontend แสดง summary, claims, gaps และ source links ที่อ่านได้ | v3 provenance บางหน้าจอยัง integration partial |
| UC-04 ตอบ clarification | thread awaiting follow-up | คำตอบถูกบันทึกเป็น user clarification answer และสร้าง fresh run | raw evidence ใหม่รวมคำตอบและวิเคราะห์อีกครั้ง |
| UC-05 เพิ่มข้อมูลคดี | มี initial case | ผู้ใช้เลือก add-information action | ข้อมูลใหม่เป็น authoritative user evidence และสร้าง fresh run |
| UC-06 ถามเกี่ยวกับผลวิเคราะห์ | มี completed analysis context | ส่ง action=ask | ใช้ context ที่บันทึกไว้ ไม่เรียก RAG ใหม่ |
| UC-07 ดู technical context | มี retrieval/MITRE data | UI แสดง technique candidates และเหตุผล | ข้อมูลถูกติดป้าย external reference |
| UC-08 สร้างรายงาน | มี latest completed analysis/context | backend สร้าง snapshot, template report, validate และ persist | ได้ report version หรือ conflict/failure ที่มีรหัส |
| UC-09 ดาวน์โหลด PDF | มี report ที่สำเร็จ | เรียก endpoint PDF | ได้ไฟล์แบบ no-store หรือ error |
| UC-10 preview เอกสาร | working-tree ingestion route เปิดใช้ | อัปโหลด PDF/DOCX/PNG/JPEG เพื่อ preview | ได้ข้อความ/region และ warning; ไม่เข้าสำนวน |

## 3.5 สถาปัตยกรรมระบบ

### 3.5.1 Frontend

Frontend ใช้ Next.js App Router และ React แบ่งเส้นทางภายใต้ `/chat/[threadId]` เป็น Intake, Overview, Materials, Technical Context, Chat และ Report การเรียก backend รวมไว้ใน client libraries ส่วนข้อมูลที่ต้องแปลงเพื่อ presentation ใช้ modules เช่น `case-overview.ts`, `technical-context.ts` และ `case-evidence.ts`

### 3.5.2 Backend API

FastAPI ให้ route ด้าน health, chats และ document-ingestion preview ภายใต้ `/api/v1` เส้นทาง chat ครอบคลุม thread CRUD, `POST /chats/{thread_id}/messages`, run status และ chat-scoped reports Backend ใช้ Pydantic contracts และ async SQLAlchemy session ผ่าน dependency เดียวกัน การส่งข้อความคืน `202 Accepted` แล้วเพิ่ม background task เพื่อประมวลผล run

Backend แบ่งบริการตาม responsibility ได้แก่ `chat` สำหรับ persistence และ evidence reconstruction, `workflow` สำหรับ run lifecycle, `case_analysis` สำหรับ Main Analysis, `followup` สำหรับ gap/policy, `clients` สำหรับเรียก RAG service, `reports` สำหรับ snapshot/template/PDF และ `llm` สำหรับ provider abstraction

### 3.5.3 Database

PostgreSQL เป็นแหล่ง persistence หลักและ Alembic baseline ปัจจุบันสร้างห้าตาราง: `chat_threads`, `chat_messages`, `chat_runs`, `rag_contexts` และ `chat_reports` ไม่มีกลุ่มตาราง Case State รุ่นเก่า แบบจำลอง ER แบบย่ออยู่ที่ [er_diagram.mmd](diagrams/er_diagram.mmd)

### 3.5.4 LLM Provider Boundary

Backend มี provider abstraction และ model registry รองรับการตั้งค่าผ่าน environment ปัจจุบัน default config ชี้ OpenRouter model alias ที่ repository กำหนด แต่ thesis ไม่ผูก contribution กับผู้ให้บริการรายหนึ่ง เพราะ model สามารถเปลี่ยนได้ตาม configuration Main Analysis, Gap Analysis และ Follow-up Policy ใช้ structured output contracts แยกกัน เพื่อให้ตรวจผลลัพธ์และเปลี่ยน prompt version ได้

### 3.5.5 RAG Service

RAG service เป็น FastAPI แยก process รับ `POST /query` แล้วเรียก GraphRAG ใน worker thread เพราะ pipeline ภายในเป็น synchronous และมีทรัพยากร model/database ของตนเอง Qdrant จัดเก็บ dense/sparse vectors ส่วน Neo4j จัดเก็บความสัมพันธ์จาก STIX บริการคืน `retrieval_context_id`, context และ MITRE table ไปยัง backend; generated technical answer ภายในไม่ได้ถูกส่งเป็นคำตอบ HTTP หลักของ product

### 3.5.6 Report Service

Report service สร้าง `ReportInputSnapshot` จาก raw evidence, analysis message, retrieval context และ unresolved gaps จาก metadata จากนั้น `build_template_report` สร้าง structured report เจ็ดส่วนโดยไม่เรียก LLM Validator ตรวจลำดับส่วน แหล่งอ้างอิง และ technique IDs ก่อน persist เป็น report version ใหม่

## 3.6 การไหลของข้อมูล

### 3.6.1 Initial Case Analysis

1. ผู้ใช้สร้าง thread และส่งข้อความแรกพร้อม action สำหรับ fresh analysis
2. `ChatMessageService` ตรวจ thread state, กำหนด ordinal และบันทึก message/run ใน transaction
3. Background worker ยึด lease ของ run และสร้าง raw evidence snapshot
4. Backend เรียก RAG `/query` ด้วยข้อความหลักฐาน ไม่ใช่ข้อความผู้ช่วย
5. ผล retrieval ถูกตรวจและจัดเป็น `RagContext`
6. Main Analysis สร้าง provider output, parser สร้าง AnalysisTrace และ validator ตรวจ provenance
7. Gap Analysis ประเมิน raw evidence กับผลวิเคราะห์ โดยถือผลวิเคราะห์/RAG เป็น derived context
8. Policy เลือกถามหนึ่งข้อหรือดำเนินต่อ
9. Outcome persist `RagContext` และ assistant message พร้อม metadata แล้วปิด run

ลำดับนี้อยู่ที่ [initial_analysis_sequence.mmd](diagrams/initial_analysis_sequence.mmd)

### 3.6.2 Ask Question

โหมด ask ใช้เมื่อผู้ใช้ถามเกี่ยวกับผลวิเคราะห์ที่มีอยู่ ข้อความนี้ถูกบันทึก แต่ไม่ถูกรวมเป็นหลักฐานคดี `pipeline_execution` ค้น completed analysis context ล่าสุดและเรียก Main Analysis ใน `question_answer` mode โดยนำ context ที่บันทึกไว้กลับมาใช้ ไม่เรียก RAG ใหม่ Metadata ของ outcome ระบุ `fresh_rag_invoked=false` และ `retrieval_context_reused=true` หากไม่มี analysis context ที่เหมาะสม request ต้องล้มเหลวแทนการสร้างคำตอบจากข้อมูลที่ไม่ผูกกับสถานะเดิม

### 3.6.3 Add Information

เมื่อผู้ใช้เลือกเพิ่มข้อมูล ระบบบันทึก message เป็น `added_case_information` ซึ่งเป็น authoritative evidence แล้วสร้าง fresh run ใหม่ Raw evidence snapshot รุ่นใหม่ประกอบด้วย initial narrative, clarification answers และ added information ตามลำดับ ordinal Evidence hash จึงเปลี่ยนและ RAG/Main Analysis ถูกเรียกใหม่บนข้อมูลรวมทั้งหมด

### 3.6.4 Clarification Answer

เมื่อ policy ถามคำถาม assistant message จะมี metadata ผูกคำถามกับ retrieval context และ thread เข้าสถานะ awaiting follow-up คำตอบถัดไปที่ตรง chain ถูกจัดชนิด `clarification_answer` และเข้า raw evidence จากนั้นระบบรัน fresh analysis ใหม่ ขั้นตอนนี้ต่างจาก ask เพราะคำตอบ clarification เป็นข้อมูลที่ผู้ใช้ยืนยันเพื่อใช้เป็นหลักฐานของสำนวน ขณะที่ ask เป็นคำถามต่อ derived analysis

ลำดับ add-information และ clarification รวมอยู่ที่ [followup_sequence.mmd](diagrams/followup_sequence.mmd)

### 3.6.5 Generate Report

การสร้างรายงานเริ่มจาก `POST /chats/{thread_id}/reports` บริการเลือก latest completed retrieval context และ analysis message ที่สัมพันธ์กัน สร้าง source snapshot และ hash กำหนด idempotency key จาก request หรือ snapshot hash ตรวจ conflict และสร้าง report ด้วย template Validator จำกัด source IDs ให้อยู่ใน evidence snapshot และ MITRE technique IDs ให้อยู่ในรายการที่ระบบยอมรับ เมื่อผ่านจึง persist report กับ version number และให้ endpoint แยกสำหรับ PDF ลำดับอยู่ที่ [report_sequence.mmd](diagrams/report_sequence.mmd)

## 3.7 Evidence Trust Boundary

Evidence trust boundary เป็นข้อกำหนดสำคัญที่สุดของระบบ เนื่องจากแยกว่าอะไรสามารถรองรับข้ออ้างเกี่ยวกับคดีได้

### ตารางที่ 3-3 การจัดชั้นข้อมูล

| ชั้นข้อมูล | ตัวอย่าง | สถานะ | ใช้รองรับ claim คดีโดยตรง |
|---|---|---|---|
| Authoritative user-authored evidence | initial narrative, clarification answer, added case information | หลักฐานต้นทางในขอบเขตระบบ | ได้ |
| User ask | คำถามว่า “เหตุใดระบบจึงสรุปเช่นนี้” | interaction | ไม่ได้ |
| Assistant messages | analysis, clarification question, answer | derived output | ไม่ได้ |
| RAG/MITRE context | technique description, retrieved STIX relations | external technical context | ไม่ได้โดยลำพัง |
| AnalysisTrace | claims, status, associations | derived structured state | ใช้ชี้และจัดรูป แต่ authority มาจาก source IDs |
| Report | template projection of snapshot | derived artifact | ไม่เพิ่มหลักฐานใหม่ |
| Document preview | OCR/DOCX extracted text | untrusted preview | ยังไม่ได้ |

Raw evidence builder ใช้ข้อความผู้ใช้แรกเป็น `INITIAL CASE NARRATIVE` และเพิ่มเฉพาะข้อความภายหลังที่ถูกทำเครื่องหมายเป็น clarification answer หรือ added information User ask ทั่วไปถูกข้ามโดยตั้งใจ และไม่มี assistant message ผ่าน filter นี้ หลังสร้างข้อความรวม ระบบคำนวณ SHA-256 และเก็บ source IDs ตามลำดับ ข้อกำหนดนี้ป้องกัน feedback loop ที่ผลสร้างของโมเดลถูกป้อนกลับและค่อย ๆ กลายเป็น “ข้อเท็จจริง” โดยไม่มีผู้ใช้รับรอง

ขอบเขตนี้ไม่ได้ยืนยันว่าข้อมูลผู้ใช้เป็นความจริงในโลกภายนอก แต่กำหนดว่าในระบบ ข้อมูลใดเป็นคำกล่าวที่ผู้ใช้ให้ไว้และสามารถใช้เป็นฐานวิเคราะห์ ดังนั้นคำว่า authoritative ใน thesis หมายถึง authority ภายใน workflow ไม่ใช่ความน่าเชื่อถือทางพยานหลักฐานหรือข้อยุติทางกฎหมาย

## 3.8 LLM Analysis Module

### 3.8.1 Input

โหมด `case_overview` รับ raw evidence และ optional external context ที่ผ่าน boundary โหมด `question_answer` รับคำถามผู้ใช้พร้อม analysis context ที่บันทึกไว้ Prompt builder ประกอบ trust instructions, mode instructions และข้อความ context โดยใช้ version `main_case_analysis_v4` ใน working tree ปัจจุบัน

### 3.8.2 Prompt Builder

Trust instructions ระบุว่าเนื้อหาอาจเป็นคดีทั่วไป เช่น ทรัพย์สิน การฉ้อโกง ความรุนแรง หรือคดีไซเบอร์ และห้ามบังคับใช้ cyber taxonomy เมื่อไม่เกี่ยวข้อง นอกจากนี้ยังสั่งให้แยก reported information, analytical inference และ unknown; ห้ามเปลี่ยน external context เป็นหลักฐาน; ห้ามสรุป guilt, liability หรือ legal conclusion; และห้ามอนุมาน causality จากลำดับเวลาเพียงอย่างเดียว

### 3.8.3 Structured Output

Provider schema v3 มี `answer`, `summary`, `claims` และ `mitre_associations` โดยไม่ให้ provider สร้าง evidence hash, retrieval binding หรือ gaps ฟิลด์ระบบเหล่านี้ถูกเติมโดย backend เพื่อลดโอกาสที่โมเดลจะสร้าง identifier ที่ไม่มีอยู่จริง แต่ละ claim มี ID, type, text, epistemic status, supporting/contradicting source IDs และ optional reasoning summary

### 3.8.4 AnalysisTrace

AnalysisTrace v3 มี version discriminator, analysis mode, summary, claims, gaps, MITRE associations, evidence SHA-256, retrieval-context ID และ validation status Repository ยังเก็บ contract v2 และ compatibility reader เพราะข้อมูลเก่าและ consumer บางส่วนยังอาศัย v2 การย้ายสัญญาจึงใช้ sibling contract แทนการเปลี่ยน shape เดิมแบบเงียบ ๆ

### 3.8.5 Epistemic Status

- `reported`: ข้อมูลปรากฏในข้อความผู้ใช้
- `suspected`: ข้ออนุมานที่มีฐานแต่ยังไม่ยืนยัน
- `contradicted`: มีข้อมูลต้นทางขัดแย้ง
- `not_established`: หลักฐานปัจจุบันยังไม่ตั้งข้อดังกล่าวได้
- `unknown`: ไม่สามารถระบุสถานะสาระได้
- `not_confirmed`: ยังไม่มีการยืนยันจากข้อมูลปัจจุบัน

สถานะเหล่านี้ไม่ได้เป็นค่าความน่าจะเป็น และไม่ถูกแปลงเป็นคะแนน confidence เพราะยังไม่มี calibration evidence

### 3.8.6 Provenance Validation

Validator ตรวจ ID uniqueness, source membership, disjoint support/contradiction roles, required support สำหรับ reported/inference, required reasoning สำหรับ inference และ candidate MITRE technique IDs เทียบกับ retrieval context หาก source ID ไม่อยู่ใน raw evidence ถือว่า trust boundary ถูกละเมิดและ workflow ล้มเหลวแบบ fail-closed

### 3.8.7 Failure Handling

Parser แยกความล้มเหลวเชิงโครงสร้างออกจาก provenance violation ในบางกรณี visible prose ที่มีประโยชน์สามารถคงอยู่พร้อม metadata ว่า trace ไม่ผ่าน เพื่อให้ UI แสดงผลโดยไม่แอบอ้างว่า structured trace valid แต่หากพบ provenance ที่ผิด ระบบยกข้อผิดพลาดและไม่ยอมรับ trace การแยกนี้ช่วยให้ผู้ใช้เห็นความล้มเหลวตรงประเภท

### 3.8.8 ข้อจำกัดของ Current Implementation

Main provider output ไม่สร้าง gaps และ response parser ใส่ `gaps=[]` ขณะที่ Gap Analysis stage สร้าง gap ภายใต้ `chat_followup.gap_analysis` นอกจากนี้ frontend/report reader หลายจุดยังอ่าน `source_message_ids` แบบ v2 แทน `supporting_source_message_ids` และ `contradicting_source_message_ids` ของ v3 ดังนั้น backend trace v3 ใช้งานแล้ว แต่การแสดง provenance และการจัดทำรายงานจาก trace v3 ยังไม่สมบูรณ์

### 3.8.9 Proposed Generalized Analysis Architecture

ส่วนนี้เป็น **แนวทางการพัฒนาที่เสนอ/งานบูรณาการต่อเนื่อง** มิใช่ระบบที่เสร็จแล้ว เป้าหมายคือให้ Claim, Evidence, Gap และ Follow-up ใช้ identifier และ lifecycle เดียวกัน

```text
Claim ───── supported_by / contradicted_by ───── Evidence
  │                                                  │
  └──── leaves_unresolved ─── Gap ─── asks ─── Follow-up
                                   │
                                   └── answer becomes new Evidence
```

สถาปัตยกรรมเป้าหมายควรย้าย gap ที่ validated แล้วเข้า AnalysisTrace canonical โดยแต่ละ gap ระบุ `related_claim_ids`, `source_message_ids`, status, priority, askable และ resolution state Policy ควรเลือก gap จาก object เดียวกันและเมื่อได้รับคำตอบให้บันทึก resolution event แทนการคำนวณความสัมพันธ์ใหม่จากข้อความ การออกแบบนี้จะรองรับ claim/evidence review matrix และ contradiction resolution UI ได้ แต่ยังต้องกำหนด migration/compatibility plan ก่อน implement

## 3.9 Gap Analysis และ Follow-up

Gap Analysis ปัจจุบันเป็น structured-output call แยกจาก Main Analysis รับ raw evidence, analysis text/trace และ external context โดย prompt ย้ำว่ามีเพียง raw evidence ที่ authoritative ผลลัพธ์ประกอบด้วยรายการ gaps ตาม taxonomy สี่ค่าและคำแนะนำเชิงโครงสร้าง ไม่มีการอนุญาตให้ใช้ analysis prose เป็นหลักฐาน

Follow-up policy รับ gap analysis และสถานะการสนทนา เลือกได้สูงสุดหนึ่ง gap ที่ถามได้และมี priority เหมาะสม Guard เชิง deterministic ตรวจว่า provider ไม่ข้าม gap ที่ material และ eligible อย่างไม่มีเหตุผล รวมถึงป้องกัน duplicate questions และ explicit-unavailable answers Config ปัจจุบันจำกัดสูงสุดสองรอบ

หาก provider ของ Gap Analysis หรือ Policy ล้มเหลว workflow ส่วนนี้ใช้ fail-open-to-proceed พร้อม metadata/logging เพื่อไม่ให้การวิเคราะห์หลักติดค้าง ข้อแลกเปลี่ยนคือผู้ใช้อาจไม่ได้รับคำถามที่ควรถาม แต่ระบบไม่สร้างคำถามจาก fallback ที่ไม่มีการตรวจ ใน thesis ต้องแยก behavior นี้จาก fail-closed provenance validation ของ Main Analysis เพราะมีวัตถุประสงค์ความปลอดภัยต่างกัน

ข้อจำกัดปัจจุบันคือ gap ไม่ได้เป็นส่วน canonical ของ Main Analysis trace, การติดตาม resolution อาศัย metadata/ข้อความ และยังไม่มีการประเมินกับผู้เชี่ยวชาญว่าคำถามมีความจำเป็นหรือกระทบ downstream report อย่างไร

## 3.10 MITRE ATT&CK Retrieval Module

RAG pipeline เริ่มจากการเตรียมและแตก query ในภาษาต้นฉบับ ปัจจุบันไม่แปล input เป็นอังกฤษโดยอัตโนมัติทุกครั้งเพราะ BGE-M3 รองรับหลายภาษา ระบบค้น dense และ sparse candidates ใน Qdrant รวมอันดับแบบ native RRF แบ่ง quota ระหว่างหลาย query และ rerank ด้วย cross-encoder จากนั้นขยายเพื่อนบ้านโดยตรงใน Neo4j

Context evaluator ให้ผล `SUFFICIENT` หรือ `INSUFFICIENT` หากไม่พอ pipeline สามารถ rewrite/broaden query ภายใต้งบ retry สูงสุดสองรอบ แล้วจึง reasoning/translation ตามเงื่อนไข เส้นทาง route ที่แยก general explanation มีโครงอยู่ แต่ edge ปัจจุบันบังคับเข้า incident path ดังนั้นไม่ควรอ้างว่า router รองรับสอง workflow เต็มรูปแบบ

Backend รับเฉพาะ retrieval context กับ MITRE table ที่บริการคืนมา Association ใน AnalysisTrace ต้องอ้าง technique IDs ที่ยอมรับจาก context และติดสถานะ `candidate_only` กับ support role `external_technical_context` หากคดีไม่เกี่ยวกับไซเบอร์ Main Analysis ไม่ควรถูกบังคับให้สร้าง MITRE association ถึงแม้ fresh workflow ปัจจุบันยังเรียก cyber RAG service ซึ่งเป็น cyber-specific coupling ที่ต้องแก้ใน generalization ระยะถัดไป

## 3.11 Report Generation

รายงานปัจจุบันมี version `preliminary_analysis_report_v1` และสถานะ `provisional_unverified` ประกอบด้วยเจ็ด section IDs ได้แก่ case summary, indicators found, MITRE mapping, mapping rationale, evidence to examine, preliminary recommendations และ system limitations Claims ในรายงานมี support type, source message IDs และ MITRE IDs

Report generation ไม่เรียก LLM แต่ฉายข้อมูลจาก snapshot เข้าแม่แบบอย่าง deterministic จุดนี้ลด nondeterminism ระหว่างการสร้างซ้ำ Validator บังคับลำดับส่วนและขอบเขต identifier Report persistence คำนวณ snapshot hash, ตรวจ idempotency key, สร้าง version number และบันทึก analysis/retrieval bindings หาก key เดิมถูกใช้กับ snapshot ต่างกัน ระบบคืน conflict แทนการเขียนทับ

ข้อจำกัดสำคัญคือ `_extract_trace_claims` ใน report template ยังอ่าน `source_message_ids` แบบ v2 เมื่อได้รับ claim v3 จึงอาจไม่รักษา supporting/contradicting sources แบบละเอียดและอาจ fallback เป็น prose chunk ที่อ้าง evidence กว้างกว่าเดิม รายงานจึง implement แล้วในฐานะ deterministic chat-scoped report แต่ v3 provenance integration เป็นงานค้างที่ต้องแก้ก่อนอ้างความสมบูรณ์

## 3.12 การออกแบบฐานข้อมูล

### ตาราง `chat_threads`

เก็บชื่อ สถานะ ordinal ถัดไป และ timestamps สถานะ thread ครอบคลุม idle, processing, awaiting follow-up, answered และ failed ตาม model ปัจจุบัน

### ตาราง `chat_messages`

เก็บ thread ID, ordinal, role, content และ metadata มี unique constraint ต่อ `(thread_id, ordinal)` และ `(thread_id, id)` เพื่อให้ลำดับชัดเจนและรองรับ composite references

### ตาราง `chat_runs`

เก็บ request message, idempotency key, status, lease/attempt และ failure fields Constraint ป้องกัน idempotency key ซ้ำใน thread และมี partial uniqueness สำหรับ active run ใน migration เพื่อหลีกเลี่ยงการประมวลผลคู่ขนานที่ขัดกัน

### ตาราง `rag_contexts`

เก็บ retrieval context ต่อ run แบบ one-to-one พร้อม context payload, MITRE table, model metadata และ timing มี foreign keys ไป thread/run

### ตาราง `chat_reports`

เก็บ version, idempotency, snapshot hash, analysis message, retrieval context, report payload, validation/failure metadata และ timing มี unique version กับ idempotency ต่อ thread

ฐานข้อมูลไม่มี Case State tables ที่เลิกใช้แล้ว และไม่มี user/organization ownership แผนภาพ ER จึงต้องแสดงเพียงห้าตารางดังกล่าว ไม่สร้าง entity เชิงแนวคิดที่ไม่ได้ persist

## 3.13 Sequence Diagrams

แผนภาพลำดับที่จัดทำจาก code path ปัจจุบันมีดังนี้

1. [Initial analysis](diagrams/initial_analysis_sequence.mmd): แสดง message/run transaction, RAG, Main Analysis, Gap/Policy และ persistence
2. [Ask question](diagrams/ask_sequence.mmd): แสดงการ reuse context และไม่เรียก RAG
3. [Add information และ clarification answer](diagrams/followup_sequence.mmd): แสดงความแตกต่างของ evidence action
4. [Generate report](diagrams/report_sequence.mmd): แสดง snapshot, idempotency, validation และ PDF

## 3.14 Error Handling และ Reliability

### 3.14.1 Structured-output validation

Pydantic ปฏิเสธ field เกิน type ผิด และ enumeration ไม่ถูกต้อง หลัง parse แล้ว domain validator ตรวจ cross-field invariants และ source provenance Prompt version/provider/model/decoding metadata ถูกบันทึกเพื่อช่วยวิเคราะห์ความล้มเหลว

### 3.14.2 Idempotency และ transaction

การสร้าง message/run และ report ใช้ idempotency key กับ unique constraints เพื่อให้ retry จาก client ไม่สร้างวัตถุซ้ำ Report ตรวจว่า key เดิมผูก snapshot เดิมจริง มิฉะนั้นคืน conflict การจัด ordinal และ active-run constraints ลด race condition ในระดับฐานข้อมูล

### 3.14.3 Retries และ bounded loops

RAG evaluator มี rewrite/broaden loop ที่ถูกจำกัด ไม่ให้เกิด self-reflection ไม่สิ้นสุด Chat run มี lease/attempt state สำหรับ recovery จาก worker failure ส่วน follow-up ถูกจำกัดจำนวนรอบ ไม่มีการเพิ่ม LLM repair calls ใน Main Analysis หาก output ล้มเหลวเกิน contract ปัจจุบัน

### 3.14.4 Safe error display

Backend แปลง domain errors เป็น code/message ที่กำหนด Frontend มี error modal และ client-side error normalization เพื่อไม่ต้องแสดง raw stack trace แก่ผู้ใช้ แต่รายละเอียดสำหรับ debugging ยังต้องตรวจ backend logs ในการทดสอบ live

### 3.14.5 Evidence hash และ stale binding

Analysis trace และ report snapshot ผูก evidence SHA-256 กับ retrieval-context ID เมื่อ evidence เปลี่ยน เช่น ผู้ใช้เพิ่มข้อมูล hash ใหม่ทำให้สามารถตรวจได้ว่าผลเดิม stale อย่างไรก็ตาม UI/currentness behavior ทั้งหมดต้องทดสอบ end-to-end เพิ่มเติม เพราะการมี hash ใน schema ไม่ได้พิสูจน์ว่าทุกหน้าจอจัดการ stale state ครบ

### ตารางที่ 3-4 สรุป failure policy

| Boundary | Behavior | เหตุผล |
|---|---|---|
| Main Analysis provenance invalid | Fail closed | ห้ามรับ trace ที่อ้างแหล่งผิด |
| Main Analysis structural trace failure บางกรณี | คง prose + failure metadata | แยก usability จาก validated structure |
| Gap/Policy provider failure | Proceed with metadata | ไม่ให้ thread ค้างเพราะ optional clarification stage |
| RAG insufficient | bounded broaden/rewrite หรือ acknowledge limit | จำกัดต้นทุนและ loop |
| Report validation failure | Persist failure/ไม่คืน validated report | ป้องกัน report ที่อ้าง source/technique นอก snapshot |
| Idempotency conflict | HTTP conflict | ไม่เขียนทับผลจาก snapshot ต่างกัน |

โดยสรุป วิธีการออกแบบมุ่งให้ทุก stage มี input/output contract และ failure policy ที่สัมพันธ์กับความเสี่ยงของ stage นั้น หลักฐานคดียังคงเป็นข้อความผู้ใช้ที่ระบุชนิดได้ ขณะที่ analysis, external context และ report เป็นชั้น derived ที่ตรวจและสร้างใหม่ได้

