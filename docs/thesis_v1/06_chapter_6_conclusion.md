# บทที่ 6 สรุปผลและแนวทางการพัฒนาต่อ

## 6.1 สรุปผลการดำเนินงาน

โครงงาน CyberCase Intelligence Framework พัฒนาระบบช่วยทบทวนข้อมูลคดีโดยใช้การสนทนาเป็นพื้นผิว แต่จัดการงานวิเคราะห์ผ่าน workflow หลายขั้น ระบบบันทึก thread, messages, runs, retrieval contexts และ reports ใน PostgreSQL สร้าง raw evidence เฉพาะจากข้อความข้อมูลคดีที่ผู้ใช้ให้ เรียกความรู้ MITRE ATT&CK เป็นบริบทภายนอก วิเคราะห์ข้อมูลด้วย LLM ในรูปข้อความและ AnalysisTrace ประเมิน gap/clarification และสร้างรายงานแบบ deterministic จาก persisted snapshot

ผลสำคัญด้านการออกแบบคือการกำหนด evidence trust boundary ให้ข้อความผู้ช่วยและ RAG context ไม่กลายเป็นหลักฐานของคดี การเก็บ source message IDs และ evidence hash ทำให้ผลวิเคราะห์ผูกกับ input ที่ตรวจย้อนกลับได้ การใช้ epistemic statuses ทำให้ระบบแสดง reported, suspected, contradicted และสิ่งที่ยังไม่ยืนยันโดยไม่ต้องสร้างคะแนน confidence ที่ยังไม่ผ่าน calibration ส่วน follow-up policy แยก explicit unknown ออกจาก missing information และจำกัดคำถาม

ระบบยังรักษาความสามารถเฉพาะคดีไซเบอร์ผ่าน GraphRAG ที่ใช้ Qdrant, Neo4j และ MITRE ATT&CK STIX 2.1 แต่ได้เริ่มเปลี่ยน Main Analysis เป็น domain-neutral ใน working tree ปัจจุบัน การเปลี่ยนผ่านนี้ยังไม่ครบ เพราะ fresh workflow ยังเรียก cyber RAG และ consumer บางส่วนยังอ่าน AnalysisTrace v2

Automated tests ที่รันบน snapshot ปัจจุบันผ่าน 147 backend tests กับ 2 subtests และ 88 frontend tests ใน 23 files พร้อม ESLint ผ่าน ผลนี้สนับสนุนว่า contracts และ components ที่ทดสอบทำงานตาม assertions แต่ไม่ใช่หลักฐาน operational effectiveness หรือ live end-to-end readiness

## 6.2 ปัญหาที่พบระหว่างการพัฒนา

### 6.2.1 ความซับซ้อนของ Case State รุ่นก่อน

ประวัติ repository และ research artifacts แสดงว่าระบบเคยใช้ Case State representation ที่มีโครงสร้างใหญ่และ cyber-first ผล pilot B1 มี input เฉลี่ย 11,479 characters เทียบ raw B0 946.1 characters และมีเพียง 25 จาก 28 cases ที่ valid ขณะที่คะแนนไม่ได้ดีขึ้นสม่ำเสมอ การพัฒนาปัจจุบันจึงกลับมาให้ raw user-authored evidence เป็น authority และเก็บ analysis เป็น derived trace การเปลี่ยนนี้ลดโครงสร้าง intermediate ที่อาจถูกเข้าใจผิดว่าเป็นหลักฐาน แต่ทิ้ง compatibility debt ในเอกสาร/experiments บางชุด

### 6.2.2 Provenance correctness มากกว่า schema correctness

การให้โมเดลคืน JSON ที่ parse ได้ไม่เพียงพอ เพราะโมเดลอาจสร้าง source IDs ที่ไม่มีอยู่หรือใช้ external context เป็น source Repository จึงเพิ่ม validation สำหรับ source membership, support/contradiction roles และ MITRE admission พร้อม tests สำหรับ source ปลอม ปัญหานี้ทำให้สถาปัตยกรรมต้องแยก backend-bound fields ออกจาก provider-generated fields และเลือก fail-closed เมื่อ provenance ผิด

### 6.2.3 การแยก RAG ออกจาก evidence

ระบบรุ่น cyber-first มีแนวโน้มให้ผล retrieval และ technical reasoning อยู่ใกล้กับข้อเท็จจริงคดีมากเกินไป No-RAG diagnostic พบ unsupported technical interpretations และ attribution overclaims แม้ไม่มี retrieval จึงยิ่งเน้นว่าความรู้ทั่วไปต้องถูกติดป้ายภายนอก การออกแบบปัจจุบันใช้ `candidate_only` และ `external_technical_context` แต่ frontend/report ต้องรักษาป้ายนี้ทุกจุด

### 6.2.4 Structured-output failures

โมเดลอาจคืน JSON ผิด schema หรือขาด field แม้ prompt ระบุชัด Current parser แยก safe trace failure จาก provenance violation และไม่มี repair call เพิ่มเพื่อลดความซับซ้อน/ค่าใช้จ่าย ปัญหาที่เหลือคือผู้ใช้จะเห็น prose โดยไม่มี validated trace ในบางกรณี UI จึงต้องแสดงสถานะ validation failure อย่างตรงไปตรงมา ไม่ควรแสดง source affordance ราวกับ trace สมบูรณ์

### 6.2.5 Report idempotency และ snapshot identity

การสร้างรายงานซ้ำเปิดปัญหาว่า request เดิมควรคืน artifact เดิมหรือสร้าง version ใหม่ Commit ล่าสุด `cdb6697` แก้ report idempotency ให้สัมพันธ์กับ snapshot ปัจจุบัน ระบบจึงตรวจทั้ง key และ snapshot hash ปัญหานี้สะท้อนว่าการทำรายงาน deterministic ยังต้องกำหนด identity/lifecycle ชัดเจน ไม่ใช่เพียงใช้ template

### 6.2.6 Frontend complexity และ contract drift

Frontend มี view-model readers หลายไฟล์ที่ parse metadata ด้วยตนเอง เมื่อ backend เปลี่ยนจาก `source_message_ids` ใน v2 ไปเป็น supporting/contradicting arrays ใน v3 ผู้อ่านบางส่วนยังคงรูปเดิม แม้ tests ทั้งหมดผ่านเพราะ fixtures ส่วนใหญ่เป็น v2 หรือไม่ตรวจ semantics ของ v3 provenance ปัญหานี้แสดงความจำเป็นของ discriminated compatibility reader กลางและ contract tests ข้าม backend/frontend

### 6.2.7 Cyber-specific coupling

Prompt Main Analysis ถูกทำให้ domain-neutral และ tests ครอบคลุม theft, fraud, assault, property และ cybercrime แล้ว แต่ชื่อส่วน UI เช่น attack story, technical context และ fresh RAG call ยังมี cyber assumption การ generalize จึงไม่จบเพียงแก้ prompt แต่ต้องแก้ retrieval applicability, terminology, empty states, report sections และ evaluation dataset ด้วย

### 6.2.8 Document ingestion และ authority admission

การสกัดข้อความจากเอกสารสร้างคำถามว่า output เมื่อใดจะถือเป็นข้อมูลคดี Working tree เลือก preview-only และปิด HTR เพื่อไม่ให้ OCR error เข้าสู่ evidence โดยเงียบ ๆ ปัญหาที่ยังต้องแก้คือการยืนยันโดยผู้ใช้ การเก็บ file/page/span locator การแก้ไขข้อความ และการแสดง confidence/warning ที่มีความหมาย

## 6.3 ข้อจำกัดของระบบ

1. **ความเสี่ยงจาก LLM:** structured output และ validator ลดข้อผิดพลาดบางประเภท แต่ไม่กำจัด hallucination หรือพิสูจน์ semantic entailment ของทุก claim
2. **Provenance ละเอียดระดับข้อความ:** source message อาจยาวและมีหลายประเด็น ยังไม่มี page/span-level citations
3. **ไม่มีข้อรับรองทางกฎหมาย:** ระบบไม่ตรวจ legal correctness, admissibility หรือ guilt และไม่ควรใช้แทนการตัดสินของผู้เชี่ยวชาญ
4. **Generalization ยังไม่ครบ:** Main Analysis v3 เป็นกลางต่อโดเมน แต่ RAG, UI และ report ยังมี cyber-specific shapes
5. **Frontend/report v3 integration partial:** source links และ MITRE views อาจไม่สะท้อน v3 claims ครบ
6. **Gap models แยกกัน:** `AnalysisTraceV3.gaps` กับ `chat_followup.gap_analysis` ยังไม่เป็น canonical state เดียว
7. **Document ingestion จำกัด:** เป็น preview-only, ไม่ persist, ไม่เชื่อม raw evidence และไม่มี handwriting recognition
8. **Single-user architecture:** ไม่มี authentication, per-user ownership, audit identity หรือ access control
9. **Background execution:** ใช้ FastAPI BackgroundTasks/lease workflow ยังไม่มี durable external queue ที่ยืนยันสำหรับ multi-instance recovery
10. **External service dependence:** fresh cyber analysis พึ่ง LLM provider, Qdrant และ Neo4j; ยังไม่มี live resilience evaluation ใน thesis รอบนี้
11. **Development deployment:** Compose ใช้ development target และไม่มีหลักฐาน production deployment/security hardening
12. **Evaluation จำกัด:** ไม่มี expert gold analysis, prosecutor study, real-case evaluation หรือ end-to-end product benchmark
13. **Privacy/governance:** ยังไม่มี documented retention, redaction, consent, data residency หรือ sensitive-case governance ที่พร้อมใช้งานจริง
14. **Model/config drift:** model IDs และ provider behavior เปลี่ยนได้ การ reproducibility ต้อง freeze manifest ต่อ experiment/release

## 6.4 แนวทางการพัฒนาต่อ

### 6.4.1 ระยะใกล้

**1. ปิด v3 integration gap**  
สร้าง compatibility normalization module ที่แปลง AnalysisTrace v2/v3 เป็น internal view model เดียว แล้วให้ Overview, Technical Context, MITRE candidate และ Report ใช้ module นี้ เพิ่ม contract fixtures ที่มี supporting/contradicting source IDs และตรวจ source popover จริง

**2. รวม canonical Claim–Evidence–Gap model**  
กำหนด gap IDs, related claim IDs, evidence references, status, priority, askability และ resolution state ใน contract กลาง เลือกว่าจะ migrate metadata เดิมอย่างไร และให้ follow-up policy อ่าน object เดียวกับ UI/report

**3. เพิ่ม claim-evidence review interface**  
ให้ผู้ใช้เห็น claim แต่ละข้อ แหล่งสนับสนุน แหล่งขัดแย้ง epistemic status และเหตุผล แยก action “รับทราบ/ต้องตรวจ/ขัดแย้ง” จากการแก้ evidence โดยตรง การ review ไม่ควรแก้ raw user message แบบเงียบ ๆ

**4. เพิ่ม applicability gate สำหรับ external context**  
ก่อนเรียก MITRE RAG ให้ตรวจว่า case/request ต้องการ cyber technical enrichment หรือไม่ คง interface เป็น optional external-context provider เพื่อให้ Main Analysis ทั่วไปไม่ผูกกับ ATT&CK

**5. ทำ document admission workflow**  
สร้าง persisted document/page/region records, แสดง OCR output ให้ผู้ใช้ตรวจและแก้, จากนั้นสร้าง user-confirmed evidence statement พร้อม locator เท่านั้น ห้ามนำ preview เข้า analysis อัตโนมัติ

**6. เพิ่ม live integration tests**  
ทดสอบ Alembic จากฐานข้อมูลว่าง, Compose health, fresh analysis, clarification, ask reuse, add information, report idempotency และ PDF visual rendering โดยบันทึก exact versions/seeds/provider manifests

**7. ทำ error/currentness UX ให้ครบ**  
แสดงว่าผลวิเคราะห์/report ผูก evidence hash ใดและ stale เมื่อใด แสดง trace validation failure แยกจาก run failure และอย่าให้ source affordance ปรากฏเมื่อ provenance ไม่ validated

### 6.4.2 ระยะยาว

**1. Page/span provenance**  
ขยายจาก message IDs ไปสู่ document ID, page, bounding box และ character offsets พร้อม viewer ที่ highlight source span โดยต้องรักษา original artifact/hash และ chain of transformations

**2. OCR/HTR และ layout understanding**  
ประเมิน OCR แยกตามภาษา ชนิดเอกสาร และคุณภาพภาพ ก่อนเลือก HTR library/model เพิ่ม human correction loop และวัด character/word error rate รวมถึง provenance retention

**3. การประเมินที่กว้างขึ้น**  
สร้าง frozen dataset ของคดีสังเคราะห์และข้อมูลที่ได้รับอนุญาต ครอบคลุมไทย/อังกฤษและหลายโดเมน มี expert-authored claims, evidence links, gaps และ acceptable follow-up targets ประเมิน baseline กับ proposed workflow แบบ paired และรายงาน confidence intervals/descriptive uncertainty ตามขนาดตัวอย่าง

**4. Human factors study**  
เมื่อผ่าน ethics/data governance ให้ผู้เชี่ยวชาญประเมิน traceability, error detection, question burden, usefulness และ time-on-task โดยไม่ใช้ข้อมูลคดีจริงที่ไม่ได้รับอนุญาต และไม่ใช้ความพึงพอใจแทน correctness

**5. Legal retrieval เป็นงานแยกขอบเขต**  
หากองค์กรต้องการ Legal RAG ต้องมีเจ้าของ scope, corpus governance, jurisdiction/version control, citation policy และ legal-expert evaluation แยกจาก Analysis Module ปัจจุบัน ไม่ควรเพิ่มฐานกฎหมายเข้ามาเพียงเพราะระบบถูกใช้ในบริบทอัยการ

**6. Calibrated confidence เฉพาะเมื่อมีความหมาย**  
ไม่ควรเพิ่มเปอร์เซ็นต์ confidence เพื่อความสวยงาม หากจะใช้ต้องกำหนด target event, dataset, calibration metric เช่น ECE/Brier score และ policy ว่าผู้ใช้ควรทำอะไรกับแต่ละช่วงค่า Categorical epistemic status ควรคงอยู่แม้มี calibration เพิ่ม

**7. Security, privacy และ deployment hardening**  
เพิ่ม authentication/authorization, tenant isolation, encrypted secrets, audit logs, retention/redaction policy, rate limits, durable worker queue, backup/restore และ threat model ก่อนใช้กับข้อมูลอ่อนไหว

## 6.5 ข้อเสนอการประเมิน Version ถัดไป

การประเมินที่สอดคล้องกับ contribution ปัจจุบันควรแยก engineering verification จาก empirical evaluation

### Engineering verification

- contract compatibility v2/v3
- evidence source membership และ contradiction role
- stale hash/report version behavior
- failure injection ต่อ provider/RAG/database
- PDF/Thai font visual checks
- document preview/admission provenance

### Empirical evaluation

- claim support precision/recall ระดับ atomic claim
- source attribution correctness/completeness
- epistemic status accuracy
- gap necessity และ target-gap match
- unnecessary/unanswerable/repeated question rate
- report required-finding recall และ unsupported-claim rate
- latency, token/model calls และ user burden
- expert agreement/adjudication พร้อมเปิดเผย domain และจำนวนผู้ประเมิน

Baseline ควรใช้ raw evidence + direct analysis/report ที่มี schema เดียวกับ treatment ส่วน treatment เพิ่มเพียงองค์ประกอบที่ต้องการศึกษา เช่น one bounded clarification หรือ canonical claim-gap loop ต้อง freeze model, prompt, decoding, dataset และ scoring ก่อนดูผล และรายงานผลลัพธ์เชิงลบ/ไม่ชัดเจนด้วย

## 6.6 บทสรุป

CyberCase แสดงให้เห็นการพัฒนาระบบช่วยวิเคราะห์ที่วาง provenance และ trust boundary ไว้เป็นองค์ประกอบของสถาปัตยกรรม ไม่ใช่ข้อความเตือนท้ายคำตอบ ระบบปัจจุบันมีฐานที่ทำงานได้และมี tests รองรับ แต่ความสำเร็จของโครงงาน ณ Version 1 อยู่ที่การสร้าง workflow ที่ตรวจสอบและพัฒนาต่อได้ มิใช่การพิสูจน์ว่า AI วิเคราะห์คดีแทนมนุษย์ได้

งานสำคัญก่อนฉบับถัดไปคือทำให้ v3 contract ครบทุกชั้น รวม gap เป็น canonical state เชื่อมเอกสารผ่าน human-confirmed provenance และออกแบบการประเมินกับข้อมูล/ผู้ประเมินที่เหมาะสม จนกว่างานเหล่านี้เสร็จ ผลลัพธ์ของระบบควรถูกเรียกว่า provisional AI-assisted analysis ที่ต้องได้รับการตรวจทาน ไม่ใช่ข้อยุติของคดีหรือรายงานพร้อมใช้งานทางกฎหมาย

