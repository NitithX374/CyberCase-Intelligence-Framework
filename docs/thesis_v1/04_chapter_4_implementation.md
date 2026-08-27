# บทที่ 4 การพัฒนาระบบ

## 4.1 เครื่องมือที่ใช้ในการพัฒนา

เทคโนโลยีในตารางนี้มาจาก manifests, Dockerfiles และ configuration ปัจจุบัน เครื่องหมาย `>=` หรือ `^` สะท้อน constraint ใน repository มิใช่การยืนยัน installed version ของ production environment เอกสารอย่างเป็นทางการของ Next.js, FastAPI, Pydantic, SQLAlchemy, PostgreSQL, Qdrant และ Neo4j ถูกบันทึกเป็นแหล่งอ้างอิงทางเทคนิค [@nextjsDocs; @fastapiDocs; @pydanticDocs; @sqlalchemyDocs; @postgresqlDocs; @qdrantDocs; @neo4jDocs]

### ตารางที่ 4-1 เทคโนโลยีที่ใช้

| กลุ่ม | เทคโนโลยี/เวอร์ชันที่ตรวจได้ | บทบาท | หลักฐาน |
|---|---|---|---|
| Frontend | Next.js `^16.2.10` | App Router และ server/client application | `frontend/package.json` |
| Frontend | React/React DOM `19.2.4` | component rendering | `frontend/package.json` |
| Frontend | TypeScript `^5` | static typing | `frontend/package.json` |
| Frontend | Tailwind CSS `^4.2.4` | utility-first styling | `frontend/package.json` |
| Frontend | TanStack Query `^5.101.2` | server-state fetching/cache | `frontend/package.json` |
| Frontend validation | Zod `^4.4.3` | runtime client validation | `frontend/package.json` |
| Backend runtime | Python 3.11 image | FastAPI service container | `backend/Dockerfile` |
| Backend | FastAPI `>=0.115.0` | HTTP API | `backend/requirements.txt` |
| Backend schema | Pydantic `>=2.13.0` | request/response/structured output contracts | requirements |
| ORM/migration | SQLAlchemy `>=2.0.0`, Alembic `>=1.17.1` | async persistence และ migration | requirements |
| Database driver | asyncpg `>=0.31.0` | async PostgreSQL connection | requirements |
| Database | PostgreSQL 16 Alpine | relational persistence | `docker-compose.yml` |
| Report | Jinja2 `>=3.1.0`, ReportLab `>=4.2.0`, pypdf `>=5.0.0` | HTML/view model และ PDF handling | requirements/report services |
| Document preview | python-docx `>=1.1.2`, pypdfium2 `>=4.30.0`, Pillow `>=11.0.0` | DOCX/PDF/image extraction | requirements |
| OCR | typhoon-ocr `0.4.1` | OCR adapter | requirements/config |
| Vector DB | Qdrant | dense/sparse retrieval | RAG retrieval/config |
| Graph DB | Neo4j | STIX relationship expansion | RAG retrieval/config |
| Embedding | BAAI/bge-m3 | multilingual 1,024-dimension embeddings | RAG config/retriever |
| Reranker | cross-encoder/mmarco-mMiniLMv2-L12-H384-v1 | candidate reranking | RAG config |
| AI provider | provider abstraction; OpenRouter default config | structured LLM calls | backend/RAG model registry |
| Containers | Docker/Docker Compose | local multi-service environment | Dockerfiles/Compose |
| Secrets | Doppler command/environment integration | local secret injection | project commands/Compose environment |
| Tests | pytest `>=8`, Vitest `^4.1.9`, Testing Library | backend/frontend automation | manifests/tests |

Docker Compose ปัจจุบันใช้ frontend development target และมี bind mount/reload behavior จึงอธิบายเป็นสภาพแวดล้อมพัฒนา ไม่ใช่ production topology ส่วน frontend Dockerfile มี production runner stage แต่การมี image stage ไม่ใช่หลักฐานว่าระบบถูก deploy จริง

## 4.2 การพัฒนา Backend

### 4.2.1 Route boundary

Backend entrypoint ลงทะเบียน health, chat และ document-ingestion routers ด้วย prefix `/api/v1` Route หลักของผลิตภัณฑ์อยู่ที่ `/chats`: list/get/create/update/delete thread, create message, inspect run, create/list/get report และ download PDF ไม่มี `/cases`, top-level `/reports`, user หรือ standalone RAG proxy ใน route surface ปัจจุบัน

การส่ง message ใช้ HTTP 202 เนื่องจากการวิเคราะห์ทำใน background task ส่วนการอ่าน run และ thread เป็นวิธีให้ frontend poll สถานะ การออกแบบนี้ช่วยไม่ให้ HTTP request เปิดค้างตลอด LLM/RAG pipeline แต่ background task แบบ process-local ยังมีข้อจำกัดด้าน reliability เมื่อเทียบกับ durable queue ซึ่งควรพิจารณาหากระบบขยายสู่ deployment หลาย instance

### 4.2.2 Service architecture

`ChatService` จัดการ thread CRUD ส่วน `ChatMessageService` จัด message/run transaction `workflow` รับผิดชอบ lease, execution และ completion การแยกนี้ทำให้ route ไม่บรรจุ domain workflow ทั้งหมดไว้ในไฟล์เดียว Main Analysis, follow-up, RAG client และ reports มี package ของตนเองและส่งข้อมูลผ่าน typed contracts

Async database session ถูก inject ผ่าน `get_db` และ service methods ใช้ async SQLAlchemy การสร้าง message/run ต้องรักษา ordinal ของ thread, idempotency และ active-run constraints พร้อมกัน จึงทำใน transaction ก่อนเพิ่ม background task

### 4.2.3 Persistence and migrations

Alembic ใช้ baseline migration เดียวสำหรับ raw-evidence chat architecture Constraint จำนวนมากอยู่ที่ฐานข้อมูล ไม่ได้พึ่ง application checks อย่างเดียว เช่น unique ordinal, unique run/report idempotency, one RagContext per run และ positive version numbers วิธีนี้ช่วยป้องกันข้อมูลผิดรูปเมื่อมี concurrent requests

### 4.2.4 Provider abstraction

LLM service แยก request routing, provider client และ model settings ทำให้ Main Analysis, Gap Analysis และ follow-up policy เลือก model ผ่าน config ได้ โดยไม่ฝัง vendor-specific calls ลงใน domain services Working tree ปัจจุบันมี default `openai/gpt-5.6-luna` ผ่าน OpenRouter ทั้ง backend และ RAG registry แต่ thesis ถือค่านี้เป็น configuration snapshot ไม่ใช่เงื่อนไขถาวรหรือผลรับรองโมเดล

## 4.3 การพัฒนา Frontend

Frontend ใช้โครง App Router และ workspace navigation ที่ผู้ใช้มองเห็นตามงาน ไม่ได้สร้างแบบฟอร์มตามตารางฐานข้อมูลโดยตรง หน้า Intake ใช้รับคำบรรยายและ preview เอกสาร หน้า Overview สรุป “เกิดอะไรขึ้น”, claims, สิ่งที่ยืนยันแล้ว และสิ่งที่ยังไม่ชัด Materials แสดงข้อความต้นทาง Technical Context อธิบาย ATT&CK ในฐานะ external reference Chat รองรับ ask/add information/clarification และ Report แสดงรายงานกับประวัติ version

ระบบออกแบบภาพลักษณ์แบบ dossier/document ใช้สี monochrome ร่วมกับ oxblood accent ตาม `DESIGN.md` มีสถานะ loading/processing, source popover และ error modal แทนการแสดง JSON schema โดยตรง ผู้ใช้จึงเห็น label เช่น “ข้อมูลที่ผู้ใช้ให้” หรือ “บริบทภายนอก” มากกว่า field name ภายใน

Client modules แปลง persisted messages เป็น view models การแยกนี้ช่วยให้ components ไม่ต้องรู้ metadata shape ทุกจุด แต่เป็นจุดที่เกิด integration gap ปัจจุบันด้วย: `case-overview.ts` และ `technical-context.ts` ยังอ่าน `source_message_ids` แบบ v2 ขณะที่ Main Analysis v3 ใช้ `supporting_source_message_ids` และ `contradicting_source_message_ids`; `mitre-candidate.ts` ยังยอมรับ trace version v2 เท่านั้น ดังนั้น UI สามารถหา assistant analysis จาก `analysis_kind` ได้ แต่ provenance บางรายการอาจว่างหรือ MITRE candidate view ไม่ปรากฏเมื่อข้อมูลเป็น v3

## 4.4 Case Intake และ Document Preview

Case Intake รับข้อความคำบรรยายแรกและสร้าง persisted workflow ส่วน document-ingestion preview เป็น feature ใน working tree ที่แยกจาก evidence pipeline Route ตรวจ MIME/extension และขนาดไฟล์ แปลง PDF/DOCX/image เป็นหน้า ส่งผ่าน whole-page region segmentation/routing และใช้ OCR ตามชนิดที่รองรับ Config ปัจจุบันกำหนดขนาดสูงสุด 20 MB และสูงสุด 50 หน้า

ผลลัพธ์ preview ประกอบด้วยข้อความที่สกัด region/route และคำเตือน Frontend เก็บผลใน client store สำหรับการแสดงผลเท่านั้น ข้อความใน UI ระบุว่า output ยังไม่ถูกส่งไป case analysis, RAG หรือ MITRE และ HTR ถูกปิด การออกแบบนี้ลดความเสี่ยงที่ OCR error จะกลายเป็น authoritative evidence โดยอัตโนมัติ แต่ยังไม่ครบเป้าหมาย document ingestion เพราะไม่มี document record, page/span provenance, user confirmation หรือ handoff ไป raw evidence

## 4.5 Main Case Analysis

### 4.5.1 การประกอบคำสั่ง

Prompt builder เลือก mode config และ trust instructions แล้วแนบ raw evidence กับ external context การวิเคราะห์ทั่วไปถูกออกแบบให้ไม่สมมติ cyber actors หรือ ATT&CK หาก input ไม่เกี่ยวข้อง ขณะเดียวกัน optional MITRE context ยังสามารถใช้กับคดีไซเบอร์ในฐานะข้อมูลอ้างอิง

ตัวอย่างแกนของสัญญา claim ซึ่งย่อจาก `contracts.py` แสดงว่าระบบเก็บทั้งแหล่งสนับสนุนและขัดแย้ง:

```python
class AnalysisClaimV3(BaseModel):
    claim_id: str
    claim_type: ClaimType
    text: str
    epistemic_status: EpistemicStatus
    supporting_source_message_ids: list[str]
    contradicting_source_message_ids: list[str]
    reasoning_summary: str | None = None
```

โครงสร้างนี้มีความสำคัญเพราะ source ไม่ได้เป็น citation ต่อท้าย prose อย่างเดียว แต่เป็นส่วนของ contract ที่ validator ใช้ตัดสินว่าจะยอมรับ trace หรือไม่

### 4.5.2 การเรียกแบบจำลองและ parsing

Executor ส่ง structured-output request หนึ่งครั้งและรับ `ProviderCaseAnalysisV3` Parser แปลง provider object เป็น AnalysisTrace v3 โดย backend เติม `evidence_sha256` และ `retrieval_context_id` ไม่ให้โมเดลสร้างค่าเหล่านี้เอง หาก JSON parse หรือ schema validation ล้มเหลว error จะถูกจัดประเภทเพื่อ persistence/response ตาม policy ปัจจุบัน ไม่มี repair call หรือ retry LLM เพิ่มใน Main Analysis

### 4.5.3 General-case tests

working tree เพิ่ม tests สำหรับหลายโดเมนและ invariants ของ v3 เช่น theft/property/fraud/physical incident เพื่อยืนยันว่า prompt/schema ไม่บังคับ cyber fields Tests เหล่านี้ตรวจ contract behavior ไม่ใช่ความถูกต้องเชิงสาระจาก model จริง เพราะใช้ fixtures/fakes เป็นหลัก

## 4.6 AnalysisTrace และ Provenance

Validator v3 ทำงานหลัง schema parse และก่อน persist trace หลักการสำคัญมีดังนี้

1. Claim IDs และ association IDs ไม่ซ้ำ
2. ทุก source ID ต้องอยู่ใน evidence snapshot
3. supporting กับ contradicting IDs ต้องไม่ทับกัน
4. reported และ analytical inference ต้องมี supporting source
5. analytical inference ต้องมี reasoning summary
6. gap source/related claim references ต้อง resolve และ explicit unknown ต้องไม่ askable
7. MITRE association ต้องอ้าง claim ที่มีอยู่และ technique ที่ retrieval ยอมรับ

ตัวอย่างตรรกะสำคัญแบบย่อ:

```python
unknown_supporting_sources = supporting_sources - evidence_source_ids
unknown_contradicting_sources = contradicting_sources - evidence_source_ids
if unknown_supporting_sources or unknown_contradicting_sources:
    raise CaseAnalysisValidationError("claim_source_not_in_evidence")

if supporting_sources & contradicting_sources:
    raise CaseAnalysisValidationError("claim_source_role_conflict")
```

การตรวจนี้เป็น message-level grounding ไม่ได้อ่านข้อความใน source เพื่อพิสูจน์ entailment แบบอัตโนมัติ ดังนั้น source ID ที่อยู่ใน evidence set อาจยังไม่รองรับข้อความเชิงความหมายได้ครบ ในอนาคตต้องเพิ่ม human review และอาจใช้ span-level alignment หรือ verifier ที่ผ่านการประเมิน โดยไม่ให้ verifier กลายเป็นผู้ตัดสินสุดท้าย

## 4.7 Gap Analysis

Gap Analysis มี contracts และ prompts ของตนเอง ให้โมเดลจัด gap ตาม status, topic, description, affects, priority และ askable Prompt สั่งให้พิจารณาว่าข้อมูล “ไม่ให้มา”, “แจ้งว่าไม่ทราบ”, “กำกวม” หรือ “ขัดแย้ง” แตกต่างกัน และห้ามสร้างช่องว่างเพื่อเก็บ optional enrichment หรือข้อกฎหมายที่อยู่นอกคำขอ

ผล Gap Analysis ปัจจุบันบันทึกใน metadata ของ chat follow-up ไม่ได้ถูก merge เข้ากับ `AnalysisTraceV3.gaps` นี่เป็นความซ้ำซ้อนเชิงสัญญาที่ช่วยให้ migration เกิดแบบ incremental แต่ทำให้ consumer ต้องรู้ตำแหน่งข้อมูลมากกว่าหนึ่งแห่ง และเสี่ยงต่อ status drift

## 4.8 Follow-up Workflow

Decision service ตรวจรอบก่อนหน้า คำตอบ explicit-unavailable คำถามซ้ำ และผล provider policy จากนั้นเลือก ask/proceed Guard แบบ deterministic บังคับให้ material eligible gap ไม่ถูกข้ามเพราะ provider ตอบ proceed โดยไม่มีเหตุผล ในหนึ่ง decision ถามได้หนึ่งข้อ และ config จำกัด total rounds เป็นสอง

เมื่อผู้ใช้ตอบ clarification `clarification_chain` ทำให้ข้อความนั้นได้รับ evidence role ที่ถูกต้อง Raw evidence builder จึงรวมคำตอบใน snapshot รุ่นใหม่และรัน full fresh analysis อีกครั้ง การเพิ่มข้อมูลใช้เส้นทางคล้ายกันแต่ไม่ต้องมี pending clarification ส่วน ask mode ไม่เข้า evidence และไม่เรียก RAG ใหม่ ความแตกต่างสาม action นี้เป็นแกนของความถูกต้องด้าน lifecycle

หาก Gap Analysis/Policy provider ล้มเหลว ระบบ proceed พร้อม failure metadata แทนการสร้าง fallback question จุดนี้ควรมี monitoring และทดสอบ live เพิ่มเติมเพราะการ fail open อาจทำให้ผู้ใช้เห็น analysis ที่ยังมี gap โดยไม่มีคำถาม แต่ไม่ทำให้ระบบสร้างคำถามที่ไม่มีฐาน

## 4.9 MITRE Technical Context

RAG service โหลด STIX bundles เพื่อสร้าง Qdrant collection และ Neo4j graph Query path ใช้ BGE-M3 ในภาษาต้นฉบับ สร้าง multi-query candidates ทำ dense/sparse search รวม RRF จัด quota และ rerank จากนั้นดึงความสัมพันธ์เพื่อนบ้านโดยตรงจาก Neo4j Context builder สร้างข้อความสำหรับ evaluator/reasoner และระบบจำกัด rewrite iterations

การเรียกจาก backend ทำผ่าน GraphRAG client ซึ่งตรวจ response schema ก่อนสร้าง `RagContext` Main Analysis สามารถสร้าง MITRE associations ได้เฉพาะ technique IDs ที่ปรากฏใน admitted table Association ต้องเชื่อม claim IDs และมีเหตุผล แต่ยังติดป้าย `candidate_only` เสมอ

ข้อจำกัดการ generalize คือ fresh workflow ยังเรียก RAG service แม้คดีไม่ใช่ไซเบอร์ แม้ prompt หลักจะไม่บังคับใช้ผลก็ตาม แนวทางระยะใกล้คือเพิ่ม explicit applicability gate ก่อน cyber retrieval หรือทำ external-context provider เป็น optional plugin โดยคง interface เดิม

## 4.10 Report Generation

Report service ดำเนินงานสี่ขั้น ได้แก่ snapshot construction, deterministic template generation, validation และ persistence Snapshot ระบุ source messages, analysis text/trace, retrieval context, MITRE rows และ unresolved issues แล้วคำนวณ canonical hash

`StructuredReport` กำหนดเจ็ด sections และสถานะ `provisional_unverified` ชัดเจน ไม่เรียกผลลัพธ์ว่า final report Claims แยก support type ได้แก่ user reported, analytical inference, general technical knowledge, MITRE mapping candidate และ unknown เมื่อผ่าน validator จึง render เป็น view model/HTML/PDF

Idempotency behavior มีสองกรณี: หาก key เดิมสัมพันธ์กับ snapshot เดิม ระบบคืน report เดิม; หากสัมพันธ์กับ snapshot ต่างกัน ระบบคืน `report_idempotency_conflict` การเปลี่ยน evidence จึงควรสร้าง report version ใหม่ ไม่ overwrite artifact เดิม

V3 integration gap อยู่ที่ template extractor ซึ่งยังอ่าน `source_message_ids` ของ v2 ใน claim การแก้ควรผ่าน compatibility reader กลางที่แปลง v2/v3 เป็น internal report claim type แทนเพิ่ม condition กระจายใน template และต้องมี regression tests ว่า supporting/contradicting roles ไม่ถูกทำให้สูญหาย

## 4.11 Error Handling และ Idempotency

### ตารางที่ 4-2 ตัวอย่างการจัดการข้อผิดพลาด

| เหตุการณ์ | การจัดการปัจจุบัน | สิ่งที่ผู้ใช้เห็น/ผล persistence |
|---|---|---|
| ส่ง message ซ้ำด้วย key เดิม | unique/idempotency path | ไม่สร้าง run ซ้ำ |
| มี active run อยู่ | state/constraint rejection | conflict/actionable error |
| RAG HTTP/schema error | GraphRAG client error → failed run | thread/run failed พร้อม code |
| Main trace source ปลอม | fail-closed validation | ไม่ยอมรับ validated trace |
| Gap/policy error | proceed + metadata | analysis อาจเสร็จโดยไม่ถาม |
| Report ไม่มี completed analysis | report domain error | 404/409 ตามชนิด |
| Report key ผูก snapshot อื่น | conflict | ไม่ overwrite |
| PDF rendering error | report error mapping | error modal/message |
| Document เกินขนาด/ชนิดไม่รองรับ | upload validation | HTTP error พร้อมรายละเอียดจำกัด |

Frontend normalize error response และใช้ modal เพื่อไม่ให้ error ถูกกลบในพื้นที่ทำงาน การทดสอบ current checkout ครอบคลุม error contract หลายกรณี แต่การยืนยันว่า log, timeout และ service recovery ทำงานภายใต้ network failure จริงยังต้อง live testing

## 4.12 การทดสอบ

เมื่อวันที่ 27 สิงหาคม 2569 ได้รันชุดทดสอบบน working tree ปัจจุบันด้วยคำสั่งต่อไปนี้:

```powershell
.\env_mitre\Scripts\python.exe -m pytest backend\tests -q
cd frontend
npm run test
npm run lint
```

ผล backend คือ `147 passed, 2 subtests passed` ใช้เวลา 4.95 วินาที มีคำเตือน 2 รายการ ได้แก่ Starlette TestClient deprecation และ pytest cache เขียนไม่ได้เพราะ permission ผล frontend คือ 23 test files และ 88 tests ผ่าน ใช้เวลา 53.45 วินาที ESLint exit code 0 โดยไม่มี output

ชุด backend ครอบคลุม chat raw pipeline, follow-up policy, structured output, AnalysisTrace v2/v3, general-case analysis, report behavior, route surface และ document ingestion tests ชุด frontend ครอบคลุม workspace components และ view-model helpers รวมถึง ingestion preview อย่างไรก็ตาม tests จำนวนมากใช้ mocks/fakes และไม่เรียก external model/database services จริง

การทดสอบในรอบเขียน thesis ไม่ได้รัน Docker Compose end-to-end, Alembic upgrade บนฐานข้อมูลใหม่, live RAG `/query`, live LLM provider หรือ browser journey เต็มเส้นทาง จึงไม่ควรเขียนว่า “ระบบผ่านการทดสอบทั้งหมด” แต่ควรระบุว่าชุด automated tests ที่มีผ่าน และ live integration ยัง pending

## 4.13 สรุปการพัฒนา

โครงสร้างปัจจุบันแสดงการแยก service responsibilities และ trust boundary ที่ชัดเจนขึ้นจากระบบ cyber chat รุ่นแรก Backend general analysis v3, provenance validation, bounded follow-up และ deterministic report เป็นแกนที่มี code/test evidence ส่วนงานค้างหลักมิใช่การสร้างโมดูลใหม่ทั้งหมด แต่เป็นการทำให้ contracts ระหว่าง backend, frontend และ reports ใช้ความหมายเดียวกัน รวมถึงยก document preview ไปสู่ admitted evidence ด้วยขั้นยืนยันและ provenance ที่เหมาะสม
