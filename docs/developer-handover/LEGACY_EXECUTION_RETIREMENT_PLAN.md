# Legacy Execution Retirement Plan

วันที่: 2026-09-10
สถานะ: Draft implementation handoff — ยังไม่ implement หรืออนุมัติ cutover

## 1. เป้าหมายและขอบเขต

ให้ Case เป็นเจ้าของ execution เพียงเส้นทางเดียวสำหรับงานใหม่ ทั้ง analysis, clarification continuation และ Chat Q&A แล้วถอด legacy execution/frontend branch ที่หมดหน้าที่ โดยรักษาการอ่านข้อมูลเก่าที่จำเป็น

General Case Summarization เป็นงานหลัก MITRE ATT&CK RAG เป็น requirement แบบ conditional external augmentation ไม่เรียกทุกคดี ไม่ใช้แทนหลักฐานคดี Chat ยังคง optional และต้องมี assistant analysis result หลังวิเคราะห์สำเร็จ

แผนนี้ supersede ลำดับความสำคัญ cleanup ใน POST_LUNA_CLEANUP_IMPLEMENTATION_PLAN.md: พักการรวมไฟล์/generated schema grouping/rename เชิงสไตล์ไว้ก่อน ย้ายเฉพาะ logic ที่จำเป็นต่อการเลิกใช้ legacy ไม่ redesign report sections, OCR, authentication หรือ rag_service

ทางเลือกที่เล็กที่สุด: เก็บ API/reader ที่จำเป็น แต่ถอด old writer และ old worker เมื่อ native parity ผ่าน ไม่ต้องลบทุกไฟล์ที่มีคำว่า chat และไม่ต้อง migrate ประวัติทั้งหมดให้เป็น native โดยสร้าง provenance ปลอม

## 2. หลักฐานจาก checkout และสิ่งที่ยังไม่ยืนยัน

- backend/app/routers/chat.py: create_chat_message แยก Case-linked thread ไป process_case_run และ thread ที่ไม่ผูก Case ไป ChatMessageService/process_chat_run; get_chat_run ยังใช้ ChatRunRead
- backend/app/main.py: เปิด recovery ของทั้ง ChatRun และ CaseRun
- workflow/pipeline_execution.py: มี applicability gate และ dependency สำหรับ RAG; ต้องย้ายความสามารถที่จำเป็นก่อนลบ
- workflow/case_run_execution.py -> case_analysis_executor.py -> case_native_analysis.py: native route ที่ตรวจยังไม่พิสูจน์ conditional retrieval; native assembly มี mitre_associations=[] และ case_run_completion.py มี rag_invoked=False
- frontend/src/app/chat/layout.tsx: redirect /chat ไป /case แต่ยัง mount ChatWorkspace; ChatWorkspace/ChatWorkspaceLayout ยังคง native/legacy branches
- Case report และ Chat report ใช้ source contracts ต่างกัน; case_report_persistence.py ยังนำ serializer จาก report_persistence.py มาใช้

นี่เป็น static trace ไม่ใช่ผล live E2E ยังไม่ได้ตรวจ census ข้อมูลจริงหรือ rerun ชุดทดสอบ Luna อย่างอิสระ ห้ามอ้างว่าไม่มี legacy rows จากข้อมูลตรวจครั้งก่อน การอ่านไฟล์ pipeline_stages.py ล้มเหลวเพราะไม่มีไฟล์นี้; ไม่ใช้เป็น dependency ในแผน

## 3. Invariants ที่ห้ามเสีย

1. รักษา dirty changes ทั้งหมด ไม่ reset/checkout ทับ ไม่ stage/commit/push/deploy โดยไม่ได้รับคำสั่ง
2. ขนาดไฟล์เป็นแนวทาง ไม่ใช่ hard limit 300 บรรทัด ตามผู้ใช้ยืนยันล่าสุด: 400–500 บรรทัดยอมรับได้เมื่อมี responsibility ที่สัมพันธ์กัน อ่านและทดสอบง่าย ไม่รวมหน้าที่ที่ไม่เกี่ยวกันหรือเพิ่ม abstraction โดยไม่จำเป็น แยกไฟล์เมื่อช่วยลดความซับซ้อนจริง ไม่สร้างไฟล์หนึ่ง interface เพียงเพื่อให้ผ่านตัวเลข
3. Case ownership/auth ต้องถูกบังคับก่อนทุก read/write; authenticated transaction tests ต้องใช้ auth dependency จริง ไม่ mock ข้าม DB lookup
4. Snapshot/revision/fingerprint ถูก pin ตาม run; retry ห้ามเปลี่ยน input หรือข้าม newer/active run guards
5. Exact citation binding และ supporting/contradicting source coverage คงเดิม; ห้าม invent source IDs, page numbers, backfills หรือ historical snapshots
6. Result + assistant publication atomic/exactly-once ต่อ logical completion; retry/recovery ไม่สร้าง duplicate message
7. ASK ไม่กลายเป็น authoritative evidence และไม่แทน latest case analysis; clarification ที่รับเข้าเป็น evidence ต้องผ่านเส้นทาง explicit admission
8. ผู้ใช้ทำงานจาก Case ได้เมื่อ Chat ปิด; state/history อยู่ DB ไม่เพิ่ม history selector
9. Failed dependency ต้องมีสถานะและ error ชัดเจน ไม่ silent fallback หรือเรียก legacy worker แทน native
10. การลบ Chat optional ไม่ cascade ลบ Case/evidence/results/reports; การลบ Case รักษาสัญญาที่อนุมัติไว้

## 4. แผนเป็น checkpoint

### A — Baseline และ inventory ทั้ง frontend/backend

Complexity M; risk สูงถ้าข้าม

งาน:

- ยืนยันไม่มี agent เขียนชุดไฟล์เดียวกัน จับ git HEAD/status/diff-name-status และ hash dirty/untracked baseline
- อ่าน AGENTS.md, Case-first implementation plan, audit และ receipts ของ Luna; แยก agent-reported จาก independently verified
- สร้าง retirement inventory แถวละ symbol/module: runtime caller, test caller, dynamic/framework registration, data/history dependency, replacement, disposition
- ครอบคลุม backend routers, services ทุก package, models, schemas, main/lifespan, scripts, migrations, config, tests; frontend routes/layouts, hooks, API client/types, components, storage และ tests
- Read-only PostgreSQL census: Case-linked/unlinked ChatThreads; ChatRun status/lease; reports ตาม binding/snapshot format; RAG contexts; FK/orphan checks รายงานจำนวนไม่ dump เนื้อหาคดี
- รัน baseline regressions แบบ isolated PostgreSQL schemas ไม่แตะ public rows และ capture OpenAPI/route surface

Exit A:

- มี baseline receipt และ exact candidate list ไม่ใช่ grep คำว่า legacy แล้วลบ
- ทราบว่ามี historical/unlinked data หรือไม่ และมีรายการ policy ที่ต้องตัดสิน
- ถ้า regression หลักล้มเหลว ต้องแก้/แยก blocker ก่อนแตะเส้นทางนั้น; ห้ามลบทดสอบเพื่อให้เขียว

### B — Native capability parity โดยเฉพาะ MITRE

Complexity L; risk สูงสุด

ขอบเขตที่คาดว่าจะเกี่ยวข้อง: workflow/case_run_execution.py, case_run_completion.py, case_ask_completion.py, case_analysis/mitre_applicability_*, case_native_contracts/validation, clients/rag_client.py, Case result/report readers และ technical-context UI

งาน:

1. ทำ capability matrix ของ legacy เทียบ native: summary, analysis, response language, bounded follow-up, ASK, applicability, retrieval, report export, source inspection, retry, failure/recovery
2. ให้ native analysis สร้าง source-bound findings ก่อน แล้วประเมิน applicability จาก findings/evidence ที่รับเข้า ใช้ gate/client ที่มีอยู่ ไม่สร้าง RAG stack คู่ขนาน
3. เก็บ applicability rationale, claim refs, retrieval outcome และ context identity ที่พิสูจน์ได้ใน Case-owned result/run contract; ตรวจ schema เดิมก่อนตัดสินใจ additive migration
4. แยก not_applicable, insufficient_context, retrieved_with_matches, retrieved_without_supported_match, failed ให้ตรวจได้ ไม่ใช้ rag_invoked=False ครอบทุกสถานการณ์
5. Mapping ต้องมี case claim support และ retrieved ATT&CK support; external content ห้ามเปลี่ยน case facts ห้ามอ้างว่า gate ผ่านแปลว่าเหตุการณ์จริง
6. บันทึก summary ที่สำเร็จและ augmentation outcome อย่างชัดเจนเมื่อ RAG ล้มเหลว กำหนด publication timing แบบเดียวก่อน implementation: หนึ่ง canonical result ที่มีสถานะ augmentation และหนึ่ง assistant message ไม่ publish draft แล้วเขียนทับแบบไร้ประวัติ
7. ถ้ารองรับ augmentation retry ต้อง pin snapshot/result และป้องกัน duplicate; หากยังไม่รองรับ ให้รายงานข้อจำกัดตรง ๆ ไม่แอบ rerun evidence admission
8. TechnicalContextView และ report อ่าน canonical Case result/context โดยไม่พึ่งการเปิด Chat; เก็บ message เป็น publication ของ result ไม่เป็น source of truth
9. Review ASK native context: ใช้ pinned case result/evidence ตาม policy; ห้ามนำคำถามธรรมดาหรือ retrieved output ไป admit เป็นหลักฐาน

Exit B:

- Fixtures ผ่านทั้ง nontechnical, technical, ambiguous, empty retrieval และ transport error
- Technical input ทำให้ client ถูกเรียกจริงใน integration test (mock เฉพาะ HTTP boundary); nontechnical ไม่เรียก
- Case-only UI/report อ่านสถานะเดียวกับ DB เมื่อ Chat ปิด และหลัง reload
- Fail-closed source/technique validation; ไม่มี synthetic provenance; no fallback to legacy
- Live provider verification แยกจาก mocked tests ต้องมี authorization/secrets และรายงานหากไม่ได้ทำ ไม่อ้าง E2E provider success จาก mocks

### C — Cutover writers, readers และ frontend callers

Complexity L; risk สูง

งาน:

- API งานใหม่ทั้งหมด dispatch CaseRun; Chat endpoint ยังคงสำหรับข้อความ/ประวัติได้ แต่ไม่สร้าง ChatRun ใหม่
- ปรับ client polling/retry ให้เลือก CaseRun ด้วย explicit contract ไม่ใช้ ID coincidence; เก็บ get legacy run เป็น read-only หากจำเป็น
- ย้าย legacy clarification transport ไป Case clarification continuation พร้อม durable history และ round budget เดิม; Q&A คงเป็น Chat
- /chat compatibility URLs ต้อง resolve Case ownership/id ก่อน redirect ไม่สมมติว่า UUID เท่ากันสำหรับข้อมูลเก่าทุกแถว; old /chat/{id}/chat leaf ต้องมี mapping ชัดเจน ไม่ replace prefix แล้วได้ invalid view
- Redirect layout ต้องไม่ mount legacy workspace และไม่ยิง requests ก่อน redirect; verify Back/Forward และ bookmarks
- เลิกใช้ caseFirstMode สองระบบหลัง route cutover ผ่าน; Case เป็นฐาน workspace ส่วน Chat panel เป็น optional consumer
- ปรับ intake/materials/report ให้ใช้ Case contracts เท่านั้นสำหรับงานใหม่; คง historical read view ที่จำเป็นโดย explicit routing ไม่ silent inference
- ตัด optional field compatibility เฉพาะที่พิสูจน์ว่าไม่จำเป็น ไม่แก้ types โดย cast เพื่อซ่อน payload mismatch; regeneration OpenAPI types ตาม generator ปัจจุบัน ไม่จัดกลุ่มไฟล์รอบนี้

Policy สำหรับ unlinked historical threads ที่เสนอ:

- อ่านข้อมูลเก่าได้ แต่ไม่สร้างงานผ่าน old writer
- ถ้าผู้ใช้ต้องการวิเคราะห์ใหม่ ให้ explicit Case creation/admission จาก material ที่ตรวจรับรองได้ ไม่แปลง assistant/RAG เป็น evidence
- ห้าม silently relink หรือ manufacture Case snapshot; final HTTP response/code และ UX ต้องยืนยันใน contract review ก่อน cutover

Exit C:

- ไม่มี supported new-write path สร้าง ChatRun; native routes auth/ownership ผ่าน
- Lost response retry, reload, account switch, Case switch, Chat-open/closed และ clarification ผ่าน
- Legacy URLs ไม่ 404 สำหรับ mapping ที่ตกลงรักษา และไม่ mount old workspace
- Policy unlinked data/API clients ได้รับความเห็นชอบก่อนตัด compatibility; ถ้ายังไม่ตกลง ให้หยุดเฉพาะ cutover นี้ ไม่เดาอนุมัติทิ้งข้อมูล

### D — Drain และเลิกใช้ legacy execution

Complexity M; risk สูงด้าน concurrency

ขั้น rehearsal ก่อน live:

1. ปิด admission ของ old writes ตาม C ก่อนตรวจจำนวนงาน; ป้องกันช่วงแข่งที่ตรวจ zero แล้วมี writer เก่าสร้างงานใหม่
2. บน disposable populated PostgreSQL จำลอง queued/running/failed legacy jobs และ mixed old/new application workers
3. กำหนดการจัดการงานเก่าที่ค้าง: drain ด้วย version เก่าจน terminal หรือ explicit interrupted/reanalysis policy ที่ตกลงแล้ว ห้าม convert เป็น native run โดยสร้าง snapshot ปลอม
4. เมื่อไม่มี queued/running legacy และไม่มี supported retry เข้า old worker จึงถอด startup recovery และ execution dispatch
5. ตรวจไม่มีสอง worker versions แข่ง publish; lease ownership/expired-run behavior ถูกต้อง

Exit D:

- Read-only live/pre-cutover receipt ยืนยันไม่มี old admission/in-flight jobs ตาม protocol ไม่ใช่แค่ count=0 ครั้งเดียว
- รายการ failed legacy retry disposition ชัดเจน; ไม่มีงานค้างไร้ทางออก
- Deployment/drain จริงต้องได้รับอนุญาตเพิ่มเติม ไม่ restart Docker หรือเปลี่ยน DB ใน planning phase

### E — ลบ dead execution และ legacy UI ตามหลักฐาน

Complexity M; risk กลางถึงสูง

ตารางเป็น candidates ไม่ใช่คำสั่งลบทั้งชุด:

| พื้นที่ | Candidate disposition หลัง B-D | สิ่งที่ต้องรักษา |
|---|---|---|
| workflow/pipeline_execution.py และ process_chat_run ใน pipeline.py | ลบ old executor หลังย้าย capability ที่จำเป็น | process_case_run, common result coercion, applicability/client ที่ถูกใช้งาน |
| workflow/chat_run_store, claim, completion, failure, locks; run_recovery/run_heartbeat | ลบเฉพาะ old execution-only functions เมื่อ caller เป็นศูนย์ | contracts/constants ที่ native ยัง import ต้องย้าย dependency ก่อน ไม่ลบตาม prefix |
| chat/chat_run_creation.py, chat_run_retry.py | ลบ old writer/retry เมื่อ policy ผ่าน | message CRUD, ownership, publication, native case_chat และ read-only historical serialization |
| chat/raw_evidence.py, clarification_chain.py, analysis_run_config.py, document_provenance.py | Trace แล้วแยก shared vs old-only ก่อนตัดสิน | legacy reader/research baseline ที่ยังอยู่ใน scope และ document provenance |
| case_analysis legacy v3 parser/config/claim_anchored helpers | ไม่เหมารวมว่า legacy ทั้งหมด | historical trace readers, reusable semantic modules, research baselines; แยก runtime retirement จากลบ methodology baseline |
| reports/report_generation.py, report_snapshot.py, ChatReportService writer | retire old writer หากไม่มี caller | historical report serialization/read/PDF export; native ยังใช้ serializer ต้องย้ายก่อน |
| models/chat.py, report.py, rag_context.py; schemas | ตัดเฉพาะ unused symbols ที่ไม่มี ORM/API/history dependency | ChatMessage/Thread, persisted schema และ registration; ไม่ drop tables ใน cleanup นี้ |
| frontend legacy submission/polling branches | ลบเมื่อ CaseRun transport ครบ | Chat Q&A, durable submission identity, account-scoped storage |
| ChatReportView, legacy intake/materials branches | ลบ active legacy view เมื่อ compatibility policy ผ่าน | shared UI and historical report access ตามที่ตกลง |
| /chat route files | คง compatibility redirects ที่รองรับ | Next framework route discovery; ไฟล์เล็กไม่ใช่ dead code |

หลังแต่ละ batch: imports/re-exports/scripts/test patch paths/OpenAPI/docs ต้องตรง; ใช้ source ownership manifest ตรวจว่าไม่ได้ลบ dirty work ของคนอื่น No broad directory delete, no purge scratch datasets และ no deletion of migrations

Exit E:

- ทุกไฟล์ที่ลบมี last caller + replacement + data policy + regression receipt
- old runtime symbols ไม่มี production caller; historical readers ที่คงอยู่มีเหตุผลและ fixtures
- ไม่เหลือ legacy execution fallback หรือ tests ที่ผ่านโดยทดสอบ obsolete path อย่างเดียว

### F — Final verification และ cutover decision

Complexity M; risk ตาม surface ที่ย้าย

Backend:

- Full pytest บน isolated real PostgreSQL; test transactions ต้องผ่าน actual authentication path
- Retry concurrency/supersession/fingerprints, leases/recovery/cancellation, duplicate request/publication, snapshot immutability และ role citation coverage
- Preserved history: populated old report อ่าน/export ได้, Case result/snapshot bindings ไม่เปลี่ยน, Chat deletion ไม่ทำลาย Case
- Migration head unchanged หากไม่มี additive migration; ถ้ามีต้อง rehearsal populated upgrade และข้อจำกัด rollback ห้าม silent data transformation
- Ruff/compile/import checks และ API contract diff มี disposition ทุก endpoint

Frontend:

- npm test; npx tsc --noEmit; npm run check:api-types; scoped/full lint แยก pre-existing errors; npm run build
- Authenticated browser: create Case -> upload/extract/admit -> analyze with Chat closed -> clarification -> completion -> open Chat พบหนึ่ง analysis message -> Q&A -> report/PDF/source inspection
- Technical/nontechnical cases, augmentation failure, old URL redirect, refresh, lost-response retry, user/Case switching

Cutover:

- แยก code verification จาก live deployment; ไม่อ้างว่า deploy แล้วจาก build success
- ตรวจ old writers disabled, drain complete, backup/restore readiness ที่ทดสอบได้ และ application version ที่เข้ากัน
- Rollback เป็น explicit application rollback ไม่ runtime fallback; ถ้ามีงาน native ใหม่ ห้าม rollback ไป version ที่อ่านไม่ได้ ต้องมี compatibility matrix ก่อน
- ไม่มี auto rollback DB/data หรือการลบ volume; old tables/migrations เก็บไว้จนมีคำสั่งงานแยก

Exit F: ส่งผลผ่าน/ไม่ผ่าน/ไม่ได้ทดสอบ, exact commands, environment, deleted/retained list, remaining blockers และ rollback constraints ก่อนเสนอ cutover

## 5. Acceptance matrix ขั้นต่ำ

| Test | Expected |
|---|---|
| General case, Chat closed | Native summary/result/report สำเร็จ ไม่เรียก MITRE |
| Technical case with admitted behavior | Conditional retrieval; mapping cites case + external sources separately |
| Digital channel only / ambiguous context | ไม่ force mapping; explicit applicability rationale |
| RAG empty/timeout | แยกสถานะ ไม่ปลอม mapping ไม่ทิ้ง grounded summary ที่สำเร็จ |
| Analysis completion retry | ไม่มี duplicate result publication |
| Active/newer run then old retry | ปฏิเสธตาม guard ไม่ overwrite latest result |
| Clarification on Case page | Persist answer/evidence/history; bounded rounds; ไม่ต้องเปิด Chat |
| ASK | ไม่เพิ่ม evidence revision หรือแทน latest analysis |
| Old deep link | Correct owned Case mapping หรือ explicit historical state ไม่ mount legacy writer |
| Historical report | อ่าน/export จากต้นทางเดิม ไม่มี manufactured snapshot |
| Unlinked old thread | Explicit policy; no hidden legacy execution |
| Drain race / mixed versions | ไม่มี old run ใหม่หลัง freeze ไม่มี duplicate worker publication |
| Cross-user request | ถูกปฏิเสธ ไม่ leak existence/content |

## 6. ข้อกำชับสำหรับผู้ implement

- ทำ A -> B -> C -> D -> E -> F ตามลำดับ ห้ามเริ่มจากลบไฟล์
- แต่ละ checkpoint แนบ evidence และข้อจำกัด ก่อนข้าม gate
- ทุก scope expansion เช่น Legal RAG, report redesign, table purge, generated regrouping หรือ deployment ต้องแยกอนุมัติ
- Complexity รวม L / regression risk สูง เพราะเปลี่ยน execution owner ไม่ใช่ mechanical rename; B และ C เป็นงานใหญ่สุด ยังไม่ประมาณเวลาเป็นวันจน A เสร็จ
- ความสำเร็จคือไม่มี legacy execution สำหรับงานใหม่และ requirement เดิมครบ ไม่ใช่จำนวนไฟล์ที่ลดลงสูงสุด

## 7. สถานะการตรวจในรอบร่างแผน

อ่าน ledger/skill และ source entrypoints จริง ประกอบผล static audit ก่อนหน้า ยังไม่ได้ implement, รัน PostgreSQL/full suites/provider/browser หรือ cutover ในรอบนี้ ไม่รับรองผล Luna ซ้ำจาก notification
