# CyberCase: current-code overengineering audit

ตรวจวันที่ 2026-10-04 ที่ HEAD `5fdfb4d6608477ed748afbf687a804c4930c7f21`

## ข้อสรุป

มี abstraction ที่ลดได้ชัดเจน โดยเฉพาะ service classes ที่ถือเพียง `db`, Settings ที่ใช้เจ็ด mixins และ adapter ใน production workflow ที่รองรับผลจาก substituted pipelines อีกชนิดหนึ่ง จุดเหล่านี้เพิ่มชื่อและรูปแบบที่ต้องจำ โดยไม่ได้เพิ่ม state หรือ behavior สำหรับ production ปกติ

การยุบที่แนะนำคือเปลี่ยน class เป็น module functions, รวม config ใน Settings เดียว และทำให้ workflow รับผลชนิดเดียว คงความรับผิดชอบของ routes, persistence, computation และ provenance ไว้ การลดจำนวนไฟล์/functions ทั้งหมดไม่ได้เป็นเกณฑ์ตัดสิน

คำว่า overengineering ในรายงานนี้หมายถึงความซับซ้อนที่เพิ่มโดยมีประโยชน์ต่อพฤติกรรมปัจจุบันน้อย ไม่ได้หมายความว่าพบ runtime defect ในทุกข้อ หรือพิสูจน์ว่า refactor แล้วเร็วขึ้น

## ขอบเขตและวิธีตรวจ

- อ่าน root/frontend instructions, continuity ledger และ architecture docs
- ตรวจ Git baseline และ inventory Python AST/TypeScript source files เพื่อหา classes, inheritance และ wrappers
- ไล่ callers จาก routes ไป services, analysis advance/read/store, experiment arms และหน้า frontend ที่ใช้ hooks
- ตรวจ RAG served path เทียบ offline translation/chain callers เฉพาะประเด็น class namespace
- ตรวจชื่อและส่วนที่เกี่ยวข้องของ tests เพื่อระบุผลกระทบ ไม่ได้รัน tests, provider calls, DB queries หรือ benchmark
- Inventory คัดกรองเบื้องต้นได้ backend/app 83 files, frontend/src 99 files และ rag_service/app 33 files; ตัวเลขนี้ไม่รวม generated/test/evaluation/ingestion/docs directories ตามตัวกรอง จึงไม่ใช่จำนวนโค้ดทั้ง repo
- เป็นการตรวจ structural complexity ตามเส้นทางที่ระบุ ไม่ใช่ exhaustive correctness/security audit ของทุก branch

## F1: สาม service classes ถือเพียง db — เปลี่ยนเป็น async functions ได้

หลักฐาน:

- [CaseService](<F:/Cybercase Framework/backend/app/cases/service.py:30>): constructor เขียนเพียง `self.db`; CRUD routes สร้าง instance แล้วเรียก method เดียว เช่น [get_case route](<F:/Cybercase Framework/backend/app/cases/routes.py:31>)
- [SourceService](<F:/Cybercase Framework/backend/app/sources/service.py:29>): constructor เขียนเพียง `self.db`; [source routes](<F:/Cybercase Framework/backend/app/sources/routes.py:26>) สร้าง instance เพื่อเรียก service
- [CaseReportService](<F:/Cybercase Framework/backend/app/reports/generate.py:31>): constructor เขียนเพียง `self.db`; [report routes](<F:/Cybercase Framework/backend/app/reports/routes.py:25>) สร้าง instance เพื่อเรียก method
- AST ตรวจทั้งสาม classes ไม่พบ base classes หรือ assignment ไป instance attribute อื่นนอกจาก `db` และไม่มี subclass ของ services เหล่านี้ใน current application callers ที่ตรวจ

ตัวอย่างการลด indirection ที่เสนอ ยังไม่ได้แก้จริง:

```python
await CaseService(db).get_case(case_id, user_id=user.id)
```

เปลี่ยนเป็น:

```python
await get_case_record(db, case_id, user_id=user.id)
```

คง business functions ใน service module เดิม รับ `db` เป็น argument การแยก module นี้ยังมีหน้าที่ ส่วน instance ที่มีแต่ dependency เป็นตัวเลือกที่ลดได้ ไม่จำเป็นต้องย้าย SQL เข้า routes หรือเพิ่ม Repository/Manager/Factory มาแทน

ผลดี: ลด constructor/self/instance surface และทำให้ dependency เห็นตรง signature ผลที่ไม่ได้วัด: latency/throughput/LOC savings หลัง implementation

ความเสี่ยงและสิ่งที่ต้องคง: Case CRUD commits, Source routes' transaction ownership, report generation's transaction, `owned_case`, source revision/token budget, report versioning/snapshot และ off-thread PDF render

Callers/tests ที่กระทบ: cases/sources/reports routes, `test_case_ownership_postgres.py`, `test_case_sources_provenance_postgres.py`, `test_source_limits_postgres.py`, `test_case_document_content_route.py` ที่ patch class methods และ `test_case_report_postgres.py`

ข้อเสนอนี้เป็น simplification ที่มีความเสี่ยงค่อนข้างต่ำเมื่อแก้ callers/tests ครบ ความเป็น class ปัจจุบันยังให้การจัดกลุ่ม operations; ไม่ใช่ correctness bug

## F2: Settings ใช้เจ็ด config mixins ที่ไม่มีผู้ใช้แยก

[Settings](<F:/Cybercase Framework/backend/app/config.py:111>) สืบทอด `DatabaseConfig`, `CORSConfig`, `AuthConfig`, `LLMProviderConfig`, `CaseAnalysisConfig`, `ReportConfig`, `DocumentIngestionConfig` และ `BaseSettings`

ค้นชื่อ mixins ใน current Python sources พบเพียง definitions, Settings inheritance และ `__all__` ของไฟล์เดียว ไม่มี caller ที่สร้าง/รับ mixin แต่ละชนิดแยกกัน ส่วน application ใช้ `settings` และ tests ใช้ `Settings`

ข้อเสนอ: ย้าย fields/properties/validator เข้า `Settings(BaseSettings)` เดียว และลบชื่อ mixins ที่ไม่ใช่ contract ของ callers ปัจจุบัน ปัจจุบันไฟล์มี 144 lines จึงไม่มีเหตุผลเชิงขนาดที่ต้องแบ่งเป็น inheritance graph นี้

ผลดี: เปิด class เดียวแล้วเห็น config contract ทั้งหมด ลดเจ็ดชื่อและ multiple-inheritance lookup ที่ต้องตามอ่าน คง environment names, defaults, `SettingsConfigDict`, URL/CORS properties และ model-selector validation ทุกอย่าง

ความเสี่ยงต่ำถึงกลาง: ต้องเทียบ field definitions และ env loading หลังย้าย มี tests สำหรับ Settings/model/provider อยู่แล้วที่ `test_case_analysis_model_config.py`, `test_core_llm_provider.py`; ไม่มีการรันหรือยืนยัน field/schema parity ของ refactor ในการตรวจนี้

## F3: UnassessedAdvance เพิ่มรูปแบบผลลัพธ์ใน production runner เพื่อรองรับ substituted pipelines

Production [advance_case](<F:/Cybercase Framework/backend/app/analysis/pipeline.py:68>) คืน `AnalysisAdvance` ทั้งกรณี Ask และ Proceed

แต่ [think](<F:/Cybercase Framework/backend/app/analysis/run.py:63>) ยอมรับผลชนิด `AnalysisArtifacts` อีกชนิดหนึ่ง แล้วสร้าง `UnassessedAdvance` ซึ่งเป็น empty subclass พร้อม assessment ว่าง/Proceed decision จากนั้น [store_outcome](<F:/Cybercase Framework/backend/app/analysis/run.py:103>) ตรวจ subclass เพื่อเว้น stop_reason

หลักฐานการใช้: `test_analysis_pipeline.py:304` ทดสอบ substituted pipeline นี้โดยตรง และหลาย PostgreSQL tests ส่ง fake pipeline ที่คืน `AnalysisArtifacts` ส่วน experiment arms คืน `ArmArtifacts` และเรียก computational steps โดยตรง; ไม่พบ production caller ที่แทน default pipeline เป็น arm เหล่านั้น

ข้อเสนอ: กำหนดให้ runner รับ `AnalysisAdvance` แบบเดียว แล้วทำให้ substituted tests/adapters คืน contract นี้อย่างชัดเจน ถ้าต้องส่ง experiment arm ผ่าน runner ให้ adapter อยู่ฝั่ง experiment แทนการให้ production runner ตรวจสองรูปแบบผล

ผลดี: ลด empty subclass, conversion branch และ special case ตอนเก็บผล ความเสี่ยงกลาง: ต้องตัดสิน semantics ของ assessment/stop_reason สำหรับ fake/experiment outputs และปรับ tests ให้รักษา expectation เดิมอย่างตั้งใจ ห้ามเพียงลบ branch แล้วปล่อย tests ที่จำลอง pipeline คนละ contract พัง

ข้อเสนอนี้ไม่ใช่การรวม read/think/store transactions และไม่ใช่การลดจำนวน model calls

## F4: Narrative submission เขียน mutation lifecycle เอง

[useCaseSourceActions](<F:/Cybercase Framework/frontend/src/features/sources/useCaseSourceActions.ts:12>) ใช้ `useUploadCaseDocument` สำหรับ upload แต่ narrative เก็บ pending ใน `useState`, เรียก API เอง และจัด `try/catch/finally`/invalidation เองที่ lines 31–52

Flow ที่ตรวจ: [SourcesPage](<F:/Cybercase Framework/frontend/src/features/sources/SourcesPage.tsx:22>) → actions → direct addCaseSource → refreshAfterSourceChange → boolean ให้ dialog ตัดสินการปิด ส่วน upload ใช้ [useMutation](<F:/Cybercase Framework/frontend/src/features/sources/queries.ts:23>) อยู่แล้ว

ข้อเสนอ: ใช้ `useMutation` สำหรับ narrative ภายใน hook เดิม โดยใช้ invalidation helper เดิม; ไม่ต้องเพิ่ม abstraction framework หรือหลาย hooks เพื่อ operation เดียว คง boolean success/failure ที่ UI ใช้และการปิด/ล้าง error modal แยกเป็น UI state ที่ชัดเจน

ผลดี: มี owner ของ request pending/error/lifecycle ที่สอดคล้องกับ upload ลด manual flag updates และ duplicated failure plumbing หากต้องให้ pending อยู่ข้าม page unmount ต้องกำหนด mutation key และอ่าน mutation cache ตาม pattern ที่ analysis ใช้อยู่ด้วย; `useMutation` อย่างเดียวไม่พิสูจน์ว่า remount จะเห็น pending เดิม

ความเสี่ยงกลาง: ต้องตรวจ pending/double-click guards, error modal reset, success false/true, dialog close และ invalidation ทั้งสาม query keys เป็นการปรับ lifecycle ไม่ควรนับเป็นการเปลี่ยน syntax อย่างเดียว `SourcesPage.test.tsx` mock upload hook อยู่ จึงต้องดูให้การตรวจหลังแก้ครอบคลุม hook จริงด้วย

## F5: RAG served path ใช้ CrossLingualLayer เป็น namespace ของ static methods

[CrossLingualLayer](<F:/Cybercase Framework/rag_service/app/RAG/GraphRAG/pipeline/cross_lingual.py:216>) ผสม translation client ที่มี `self.llm` กับ static prompt/language methods เช่น [get_reasoning_system_prompt](<F:/Cybercase Framework/rag_service/app/RAG/GraphRAG/pipeline/cross_lingual.py:274>) และ [should_respond_in_thai](<F:/Cybercase Framework/rag_service/app/RAG/GraphRAG/pipeline/cross_lingual.py:338>)

[GraphRAGAgent](<F:/Cybercase Framework/rag_service/app/RAG/GraphRAG/pipeline/agent_graph.py:189>) ใช้เฉพาะ static methods ของ layer นี้ ไม่สร้าง translation instance ส่วน `chain.py` และ crosslingual benchmark scripts ยังสร้าง translation client จริง

ข้อเสนอรอง: ให้ pure prompt/language logic เป็น module functions/constants ใน module เดิม แล้วให้ translation class ถือเฉพาะ client/translation behavior อัปเดต agent/chain/tests/benchmarks imports ครบ

ผลดี: แยก namespace ที่ไม่มี state จาก client ที่มี state ลดความจำเป็นที่ served path ต้องอ้าง class เพื่ออ่าน constants ความเสี่ยงกลางและคุ้มรองจาก backend เพราะมี offline callers; ห้ามลบ translation class หรือ GraphRAGChain ทั้งชุดจากการไม่อยู่ใน HTTP path

## จุดเล็กที่ยังไม่คุ้มจัดเป็น finding หลัก

- `configured_pipeline()` คืน AnalysisPipelineConfig หนึ่งตัว แต่เป็น config entrypoint ที่ caller หลายส่วนใช้ และ pipeline รับ factory นี้สำหรับ substitution ได้ การ inline ทุก caller ลดชื่อเพียงหนึ่งชื่อและกระจาย construction ไปหลายที่
- `handleSelectSource` ใน Findings/Details/TechnicalContextView เป็น forwarding callback ที่ pack arguments ให้ drawer จริง สามารถให้ hook เปิดรับ signature นี้เพื่อลด wrappers ได้ แต่ขนาดผลประโยชน์เล็ก
- `get_report_pdf/html → stored_report → report` เป็นหลาย functions แต่ stored_report แชร์ ownership/validation ระหว่าง HTML และ PDF ถ้าปรับ class เป็น functions ให้คง helper ที่แชร์นี้ได้; ไม่ต้อง inline จนเช็คสิทธิ์ซ้ำ

## จุดที่แยกไว้มีหน้าที่จริง

| โครงสร้าง | เหตุผลที่คงไว้จากโค้ด/callers |
|---|---|
| [read → think → store](<F:/Cybercase Framework/backend/app/analysis/run.py:48>) | read/store ใช้คนละ short transaction; model work อยู่ระหว่าง sessions; [revision guard](<F:/Cybercase Framework/backend/app/analysis/store.py:131>) ปฏิเสธผลเมื่อ sources เปลี่ยน |
| [AnalysisInput/Artifacts/Advance](<F:/Cybercase Framework/backend/app/analysis/pipeline.py:37>) | input/result contracts แยก computational workflow จาก DB; อย่าสรุปว่า dataclass ที่ไม่มี methods ต้องถูกลบ |
| [pipeline stage functions](<F:/Cybercase Framework/backend/app/analysis/pipeline.py:109>) | direct/verify/single arms และ research runner เรียก technical/write/bind แยกจริง และเปลี่ยน writer ได้ผ่าน request argument |
| [provider vs bound schemas](<F:/Cybercase Framework/backend/app/trace/trace.py:178>) | provider reply กับ bound reading/trace มี fields/authority ต่างกัน; การรวม type เปลี่ยน structured-output contract |
| [QuoteSearch](<F:/Cybercase Framework/backend/app/trace/bind.py:380>) / [IndexedText](<F:/Cybercase Framework/backend/app/trace/quotes.py:80>) | มี indexes และ cached search/context results ใช้ซ้ำภายใน analysis; class มี state จริง |
| [DocumentIngestionService](<F:/Cybercase Framework/backend/app/sources/ingestion/service.py:43>) | ถือ recognizer/client, limits, policy และ resource-close lifecycle; upload ปิด recognizer ก่อน DB write |
| [useCaseOverview](<F:/Cybercase Framework/frontend/src/features/analysis/useCaseOverview.ts:6>) | shared projection ที่ Layout/Summary/Findings/Details/Questions ใช้ซ้ำ; แต่ละ caller ไม่ควร copy logic นี้ การเรียก query hook หลายที่ไม่ใช่หลักฐานว่ามี duplicate HTTP requests |
| [useRunCaseAnalysis](<F:/Cybercase Framework/frontend/src/features/analysis/useRunCaseAnalysis.ts:13>) | หลาย Analyze buttons แชร์ guard ต่อ analysis/followup ที่ pending จึงไม่ใช่ forwarding wrapper ล้วน |

## ลำดับที่แนะนำหากเลือกทำ refactor ภายหลัง

1. รวม Settings mixins หรือเปลี่ยน CaseService เป็น functions เป็นงานเล็กที่ review ได้ง่าย คง API/behavior เดิม
2. ค่อยเปลี่ยน SourceService/CaseReportService โดยรักษา transaction ownership และ tests ที่ patch methods
3. ลด substituted-pipeline result compatibility โดยกำหนด contract/stop_reason semantics ให้ชัด
4. ปรับ narrative mutation lifecycle พร้อมตรวจ UI behavior
5. ค่อยย้าย RAG static helpers หากมีงานใน RAG scope อยู่แล้ว

ไม่มี implementation ถูกเลือกหรือทำใน audit นี้; การลด LOC, runtime overhead และ regression-free behavior หลัง refactor ยังไม่ได้วัด

## Verification

- ตรวจ AST ของสาม service classes: instance assignments มีเพียง `db`; no base classes
- rg ตรวจ callers ของ config mixins/UnassessedAdvance/service classes และ stage wrappers รวม production/tests/experiments ที่ระบุ
- ตรวจ Git HEAD/baseline ก่อนอ่าน; pre-existing deleted/untracked paths คงอยู่
- ตรวจ local source links/line locators 27 รายการ: valid ทั้งหมด; git diff --check ผ่าน และ tracked application/test/dependency paths ไม่มี diff
- root thaisum_main.md และ thaisum_master.md ปรากฏเป็น untracked เพิ่มระหว่างตรวจ; ไม่ได้เขียนหรือแก้โดยงาน audit นี้
- ได้สร้างเฉพาะรายงานนี้และอัปเดต CONTINUITY.md; application sources/tests/config/dependencies ไม่ได้แก้
- ไม่มี application tests, DB work, runtime/provider call, installation หรือ benchmark; static findings ไม่ใช่ผลการทดสอบ refactor
