# บทที่ 5 ผลการดำเนินงาน

## 5.1 ผลการพัฒนาระบบ

ผลการดำเนินงานด้านวิศวกรรมคือระบบเว็บที่รักษาการสนทนาและสถานะการวิเคราะห์ในฐานข้อมูล มี workflow สำหรับ fresh analysis, clarification, add information และ ask แยกจากกัน มี RAG service สำหรับ ATT&CK context และมี chat-scoped report ที่สร้างจาก persisted snapshot ระบบไม่ได้มีเพียงหน้าสนทนา แต่มีพื้นที่ Intake, Overview, Case Materials, Technical Context, Chat และ Report ซึ่งใช้ข้อมูล persistence ชุดเดียวกัน

องค์ประกอบที่มีหลักฐานว่าทำงานใน current checkout ได้แก่ thread/message/run persistence, raw evidence reconstruction, evidence hashing, GraphRAG client contract, Main Analysis v3 parsing/validation, gap/follow-up policy, report version/idempotency/PDF route และ document preview การทดสอบอัตโนมัติยืนยัน contract paths เหล่านี้ในระดับที่ fixtures/mocks ครอบคลุม

สถานะของระบบมิได้เท่ากันทุกส่วน Main Analysis v3 และ document ingestion อยู่ใน dirty working tree ยังไม่เป็น commit บน `main`; frontend/report readers ยังรับ v3 ไม่ครบ; gap ของ Main Analysis กับ gap ของ follow-up ยังไม่เป็น canonical object เดียว; ingestion ยังไม่ persist; และไม่มี authentication การกล่าวว่า “พัฒนาระบบสำเร็จ” ในบทนี้จึงหมายถึงได้ functional development baseline และ components ที่ทดสอบได้ ไม่หมายถึง production readiness หรือความสมบูรณ์ของ product

### ตารางที่ 5-1 ผลการพัฒนาตามองค์ประกอบ

| องค์ประกอบ | ผลปัจจุบัน | สถานะ |
|---|---|---|
| Persisted chat/run | CRUD, message action, run status และ metadata | ทำงานแล้ว |
| Raw evidence | user-authored evidence filtering + source IDs + hash | ทำงานแล้ว |
| Main Analysis | domain-neutral v3 contract/prompt/validation | ทำงานใน working tree |
| Gap/follow-up | 4-status taxonomy, one question/decision, bounded rounds | ทำงานแล้ว แต่ data model แยกจาก v3 gaps |
| MITRE RAG | dense+sparse+graph context และ candidate mapping | ทำงานแล้วเฉพาะ cyber context |
| Overview/Technical UI | workspace และ source-oriented views | ทำงาน แต่ v3 reader integration ไม่ครบ |
| Report | deterministic 7-section versioned report + PDF | ทำงาน แต่ claim provenance v3 partial |
| Document ingestion | PDF/DOCX/image preview + OCR | preview-only |
| HTR | manual-review state | ยังไม่ implement |
| Legal RAG | ไม่มี | นอกขอบเขต |

## 5.2 การแสดงผลของระบบ

Version 1 ไม่มีภาพหน้าจอที่ผู้ใช้จัดเตรียมให้ จึงใช้ placeholder แทนการประดิษฐ์ภาพ ทุกภาพควรถ่ายจาก current checkout หลัง frontend/report v3 integration ถูกตัดสินสถานะแล้ว

### 5.2.1 Case Intake

หน้า Intake เป็นจุดเริ่มของพื้นที่คดี ผู้ใช้กรอกคำบรรยายในภาษาธรรมชาติแล้วส่งเพื่อสร้าง initial analysis ใน working tree มีส่วนอัปโหลดเอกสารเพื่อ preview และแสดงชัดว่าเนื้อหาที่ยังไม่ยืนยันจะไม่ถูกส่งเข้าการวิเคราะห์

[FIGURE NEEDED: Case Intake ก่อนส่งคำบรรยาย แสดง input, action และ navigation]

[FIGURE NEEDED: Document preview แสดงหน้า/region, OCR warning และข้อความว่าไม่ถูกส่งเข้า analysis]

### 5.2.2 Case Overview / Case Review

หน้า Overview ตั้งใจตอบคำถามระดับผู้ใช้ ได้แก่ เกิดอะไรขึ้น ลำดับเรื่องเป็นอย่างไร อะไรยืนยันแล้ว อะไรยังไม่ชัด และควรตรวจอะไรเพิ่ม Source popover เชื่อมรายการกับข้อความต้นทาง การ filtering ปัจจุบันไม่ให้ suspected/unknown/contradicted claims ปรากฏใน attack story แต่ v3 source field mismatch ยังทำให้ source refs ของ claims บางรายการหายได้

[FIGURE NEEDED: Overview ของคดีทั่วไป แสดง summary, reported claims, unclear items และ source popover]

### 5.2.3 Chat

หน้า Chat แสดง persisted messages และสถานะ processing/awaiting follow-up ผู้ใช้สามารถถามเกี่ยวกับผลเดิม เพิ่มข้อมูล หรือส่งคำตอบต่อ clarification Action เหล่านี้มีความหมายต่อ evidence ต่างกัน แม้ปรากฏในพื้นผิวสนทนาเดียวกัน

[FIGURE NEEDED: Chat ระหว่าง awaiting follow-up และคำตอบของผู้ใช้]

### 5.2.4 Case Materials

หน้า Case Materials แสดงข้อความที่ผู้ใช้ส่งพร้อม label ของชนิดแหล่ง เช่น initial narrative, clarification answer หรือ added information จุดประสงค์คือให้ตรวจ raw material แยกจาก derived analysis

[FIGURE NEEDED: Case Materials พร้อม source labels และ ordinals]

### 5.2.5 Technical Context

หน้า Technical Context แสดง technique ID, ชื่อ, tactic, คำอธิบาย และเหตุผลที่เกี่ยวข้องกับคดี พร้อมติดป้ายว่าเป็น external reference ไม่ใช่ evidence สำหรับคดีที่ไม่ใช่ไซเบอร์ หน้านี้ควรแสดง empty/not-applicable state แทนการพยายามสร้าง ATT&CK mapping

[FIGURE NEEDED: Technical Context ของคดีไซเบอร์ แสดง candidate mapping และ evidence basis]

[FIGURE NEEDED: Technical Context empty state สำหรับคดีทั่วไป]

### 5.2.6 Report

หน้า Report สร้างรายงาน ดู report version/history แสดงสถานะ provisional/unverified และดาวน์โหลด PDF รายงานมีส่วนสรุป ลำดับเหตุการณ์/หลักฐาน MITRE context ประเด็นยังไม่ยืนยัน ประเด็นตรวจเพิ่ม และข้อจำกัด

[FIGURE NEEDED: Report workspace พร้อม version selector และ generate action]

[FIGURE NEEDED: PDF report ภาษาไทยหนึ่งหน้า แสดง provenance/limitations]

### 5.2.7 Error Handling

Frontend ใช้ modal เพื่อแสดง code/message ที่ผู้ใช้เข้าใจได้ เช่น idempotency conflict, report generation failure หรือ ingestion validation error และไม่แสดง raw stack trace

[FIGURE NEEDED: Error modal จาก controlled report idempotency conflict]

## 5.3 ตัวอย่าง Workflow การใช้งาน

ตัวอย่างนี้เป็น **กรณีสังเคราะห์เพื่ออธิบาย workflow** โดยนำแนวคิดจาก cross-domain test fixture มาขยาย ไม่ใช่ผลลัพธ์จาก live LLM run และไม่ใช้เป็นผลประเมิน

### 5.3.1 Input

ผู้ใช้ส่งข้อความ S1:

> เจ้าของร้านแจ้งว่าจักรยานสีดำที่จอดไว้หน้าร้านหายไปเมื่อมาถึงร้านเวลา 08.30 น. กล้องหน้าร้านบันทึกภาพบุคคลหนึ่งเข็นจักรยานออกจากจุดจอด แต่ภาพไม่ชัดพอระบุตัวบุคคลได้ เจ้าของไม่ทราบเวลาที่จักรยานถูกนำออกแน่นอน

Raw evidence builder จัดข้อความนี้เป็น initial narrative, source ID `S1` และคำนวณ evidence hash

### 5.3.2 Analysis

AnalysisTrace เชิงตัวอย่างอาจจัดข้อมูลดังนี้ โดยไม่เพิ่มผู้ต้องสงสัยหรือเวลาที่ไม่มีใน S1:

| Claim | Type | Status | Support |
|---|---|---|---|
| เจ้าของร้านรายงานว่าจักรยานสีดำหายจากหน้าร้าน | reported | reported | S1 |
| กล้องบันทึกบุคคลหนึ่งเข็นจักรยานออก | reported | reported | S1 |
| ตัวบุคคลในภาพคือผู้กระทำ | unknown | not_established | ไม่มี |
| เวลาที่นำจักรยานออก | unknown | not_established | ไม่มี |

ตัวอย่างนี้จงใจไม่สร้าง causal claim ว่าบุคคลในภาพ “ขโมย” จักรยาน เพราะ S1 ระบุเพียงภาพการเข็นจักรยานและยังไม่ระบุตัวบุคคล

### 5.3.3 Gap

Gap Analysis ควรแยกสถานะอย่างน้อยสองรายการ:

- ตัวบุคคลในภาพ: `NOT_PROVIDED` หรือ `AMBIGUOUS` ตามรายละเอียดจริงและถามได้หากข้อมูลมีอยู่
- เวลาที่นำจักรยานออก: `EXPLICITLY_UNKNOWN` เพราะผู้ใช้บอกชัดว่าไม่ทราบ จึงไม่ควรถามซ้ำว่า “เกิดเวลาใดแน่นอน”

### 5.3.4 Follow-up

หาก gap ที่ material และ answerable คือช่วงเวลาจากข้อมูลกล้อง นโยบายอาจถามเพียงหนึ่งข้อ เช่น:

> มีช่วงเวลาของไฟล์กล้องหรือบันทึกการเคลื่อนไหวที่ช่วยจำกัดช่วงที่บุคคลเข็นจักรยานออกหรือไม่

คำถามนี้ต้องไม่สมมติว่าบุคคลในภาพเป็นผู้กระทำ และหากผู้ใช้ตอบว่าไม่มีข้อมูลดังกล่าว ระบบควรบันทึก explicit-unavailable state และหยุดถามซ้ำ

### 5.3.5 Updated output

สมมติผู้ใช้เพิ่มข้อความ S2 ว่า:

> ผู้ดูแลกล้องตรวจพบว่าคลิปช่วง 07.52–07.55 น. แสดงการเข็นจักรยานออก แต่ยังระบุตัวบุคคลไม่ได้

S2 เป็น clarification answer และเข้าสู่ raw evidence snapshot ใหม่ ผลวิเคราะห์ที่ปรับแล้วสามารถรายงานช่วงเวลา 07.52–07.55 น. โดยอ้าง S2 ขณะที่ identity claim ยังเป็น `not_established` ไม่ควรถูกเปลี่ยนเป็น reported หรือ suspected หากไม่มีข้อมูลเพิ่ม

```text
Input S1
   ↓
Reported/unknown claims
   ↓
Gap: exact interval absent; identity not established
   ↓
One bounded follow-up
   ↓
User answer S2 becomes evidence
   ↓
Updated time claim cites S2; identity remains unresolved
```

workflow นี้แสดงเจตนาของ general Analysis Module แต่ยังต้องทดสอบ live กับ provider และ UI หลัง v3 integration เสร็จ จึงไม่ใช่หลักฐานว่าโมเดลจะสร้างข้อความเดียวกับตัวอย่างทุกครั้ง

## 5.4 System Testing

### ตารางที่ 5-2 ผล automated tests ที่ยืนยันเมื่อ 27 สิงหาคม 2569

| ชุดตรวจ | คำสั่ง | ผล | ขอบเขต |
|---|---|---|---|
| Backend | `.\env_mitre\Scripts\python.exe -m pytest backend\tests -q` | 147 passed, 2 subtests passed, 2 warnings | services/contracts/routes ผ่าน fixtures และ test clients |
| Frontend | `npm run test` | 23 files, 88 tests passed | components/view-models ด้วย Vitest/jsdom |
| Frontend lint | `npm run lint` | exit 0 | ESLint static checks |

คำเตือน backend ไม่ทำให้ test fail: หนึ่งรายการเป็น Starlette deprecation ที่แนะนำ `httpx2`; อีกหนึ่งรายการเป็น pytest cache permission และไม่กระทบ assertions Test count นี้เป็น snapshot ของ dirty working tree จึงควรรันใหม่หลัง commit/merge ก่อน Version 2

ไม่มีการรันในรอบนี้สำหรับ Docker Compose end-to-end, database migration from zero, live LLM calls, live Qdrant/Neo4j, report PDF visual QA หรือ browser automation ตัวเลขในตารางจึงไม่ควรถูกขยายความว่าเป็นระบบ production-tested

## 5.5 ผลการทดลองที่มีอยู่

ทุก subsection ในส่วนนี้ถูกจัดเป็น **Exploratory Experiment** เว้นแต่ระบุเป็น fixture validation และไม่มี subsection ใดประเมิน product v3 แบบ end-to-end ใน current checkout

### 5.5.1 Exploratory Experiment: B0/B1/B2 Representation Comparison

**วัตถุประสงค์:** สำรวจผลของรูป representation ต่อ generation tasks  
**ข้อมูล:** 28 English generation cases จาก fixed SEvenLLM selection  
**เงื่อนไข:** B0 raw narrative, B1 Case State representation, B2 GLiNER2 structure  
**โมเดล/metric:** ตาม experiment manifest; ROUGE-L และ multilingual SBERT  

| Condition | n | ROUGE-L | SBERT | Mean chars |
|---|---:|---:|---:|---:|
| B0 | 28 | 0.326070 | 0.699460 | 946.1 |
| B1 | 25 | 0.332002 | 0.704340 | 11,479.0 |
| B2 | 28 | 0.203042 | 0.567078 | 122.1 |

B1 มีเพียง 25 valid cases และ input ยาวกว่า B0 มาก จึงไม่ควรสรุปจากค่าเฉลี่ยเล็กน้อยว่า Case State เหนือกว่า raw narrative B2 สูญเสียบริบทมากและคะแนนต่ำกว่า ผลนี้เกี่ยวกับ representation pipeline รุ่นทดลอง มิใช่ current raw-message product architecture

### 5.5.2 Exploratory Experiment: B3 Raw Narrative plus Events

**วัตถุประสงค์:** สำรวจการเพิ่ม event structure เข้ากับ raw narrative  
**ข้อมูล:** 28 cases ชุดเดียวกัน  
**เงื่อนไข:** B0 raw, B2 structure-only, B3 raw+GLiNER2 events  

| Condition | ROUGE-L | SBERT | Mean chars |
|---|---:|---:|---:|
| B0 | 0.326070 | 0.699460 | 946.1 |
| B2 | 0.203042 | 0.567078 | 122.1 |
| B3 | 0.335292 | 0.680145 | 1,117.2 |

B3 เพิ่ม ROUGE-L 0.009222 จาก B0 แต่ SBERT ลด 0.019315 และจำนวน cases ที่ดีขึ้น/แย่ลงใกล้กัน ผลจึงเป็น mixed signal ไม่ใช่หลักฐานว่า event augmentation ให้ประโยชน์สม่ำเสมอ

### 5.5.3 Exploratory Experiment: Context Refinement

**วัตถุประสงค์:** เปรียบเทียบ raw context กับ LLMLingua2-refined context  
**ข้อมูล:** 28 paired English generation cases  
**โมเดล:** `meta-llama/llama-3.1-8b-instruct` ผ่าน OpenRouter; compressor `microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank`  
**ผล:** B0 ROUGE-L/SBERT = 0.326070/0.699460; refined = 0.325878/0.702320  

ค่า character retention เฉลี่ย 1.010582 แสดงว่าไม่ได้เกิด compression โดยรวม และ protected cyber spans หาย 12 จาก 19 (CVE 6, domain 4, time 2) Artifact อยู่ใน ignored local `tmp/context_refinement_run_20260823/` ไม่ใช่ tracked research result จึงใช้เป็นหลักฐานเตือนเรื่อง information loss เท่านั้นและต้องย้าย/ทำ reproducibility bundle หากเลือกใช้ใน thesis final

### 5.5.4 Exploratory Experiment: 50-Case SEvenLLM Pilot

**วัตถุประสงค์:** ตรวจ zero-shot capability reference ก่อน fine-tuning  
**ข้อมูล:** 50 English rows; 49 generation และ 1 extraction จากหก categories  
**เงื่อนไข:** B0 Llama 3.1 8B Instruct ผ่าน OpenRouter เทียบ B1 vanilla mT5-base local  
**ผล generation:** B0 ROUGE-L 0.278951, SBERT 0.672995; B1 0.049092, 0.284877  

ทั้งสองเงื่อนไขต่าง architecture, scale และ generation behavior อย่างมาก mT5 มักคืน sentinel fragments จึงเป็น capability-reference comparison ที่ confounded ไม่สามารถนำ gap ไปอธิบายผล representation หรือ product architecture ได้ Extraction มีเพียงหนึ่ง case และทั้งคู่ F1=0

### 5.5.5 Exploratory Experiment: Attribute-First Reasoning Pilot

**วัตถุประสงค์:** สำรวจว่าการทำนาย attributes ก่อนตอบช่วย cyber QA หรือไม่  
**ข้อมูล:** 33 benchmark items  
**โมเดล:** Llama 3.1 8B Instruct, temperature 0  
**เงื่อนไข:** B0 direct, A1 predicted attributes สอง calls, A2 oracle attributes  

ผล automatic ได้แก่ JSON parse 33/33, answerability accuracy 60.6%, epistemic-state accuracy 66.7%, question-type accuracy 78.8% และ evidence-selection F1 0.764 ผลคะแนนที่เรียกว่า manual scoring ใน artifact ให้ mean correctness B0/A1/A2 เท่ากับ 1.27/1.21/1.67 จาก 2 แต่ไม่มีหลักฐานว่า scorer เป็นอัยการหรือผู้เชี่ยวชาญอิสระ A1 ใช้ latency เฉลี่ย 5,541.6 ms เทียบ B0 3,074.1 ms และไม่ดีขึ้นด้านคะแนนเฉลี่ย ผลจึงชี้ bottleneck เชิงสำรวจ ไม่ใช่การยืนยันวิธี attribute-first

### 5.5.6 Exploratory Experiment: No-RAG Diagnostic

**วัตถุประสงค์:** วินิจฉัย Main Analysis เมื่อ production RAG เริ่มไม่ได้  
**ข้อมูล:** 12 cyber fixtures, 570 atomic claims  
**การประเมิน:** LLM judges สองรอบที่ใช้ model เดียวกัน  
**ผลรอบ A:** supported 535 (93.9%), unsupported 15, contradicted 1, unclear 19; support-status agreement ระหว่าง judges 96.7%  

Artifact ระบุชัดว่า retrieval ถูก skip และไม่สามารถประเมิน RAG-grounded flow, source-role contamination หรือ MITRE grounding ได้ นอกจากนี้ judge ไม่เป็นอิสระด้าน model และพบ self-referential analytical claims จึงไม่ควรใช้ 93.9% เป็น “ความแม่นยำ” ของ CyberCase คุณค่าหลักของผลนี้คือการพบ error modes เช่น certainty strengthening, attribution overclaim และ unsupported technical interpretation

### 5.5.7 Fixture Validation: Offline Semantic Verification Dataset

**วัตถุประสงค์:** ตรวจความสมบูรณ์ของ synthetic benchmark fixtures  
**ข้อมูล:** 100 cases (ไทย 50/อังกฤษ 50), 800 pairs, supported/unsupported อย่างละ 400  
**ผล:** positive gold-fact slot coverage 100%, integrity failures ไม่มี  

นี่เป็น deterministic construction validator ไม่ได้รัน semantic verifier หรือ product model จึงรายงานได้เฉพาะคุณภาพของ fixture generation logic ไม่ใช่ model quality

### 5.5.8 Exploratory Experiment: Follow-up Pilot

**วัตถุประสงค์:** ตรวจตำแหน่งของ clarification ก่อน/หลัง RAG และจำนวน calls  
**ข้อมูล:** synthetic Microsoft 365 phishing fixtures  
**เงื่อนไข:** no-followup, historical post-RAG adaptive, pre-RAG adaptive  

ใน insufficient pre-RAG result policy ถูกเรียก 2 ครั้ง ถาม 1 ข้อ และเรียก RAG 1 ครั้งหลังได้คำตอบ ใน sufficient result policy ถูกเรียก 1 ครั้ง ไม่ถาม และเรียก RAG 1 ครั้ง ผลนี้ยืนยันว่า harness/workflow สามารถงด RAG ก่อน clarification ใน fixture ที่กำหนดได้ แต่มีเพียงกรณีสังเคราะห์จำนวนน้อยและ production workflow ปัจจุบันเป็น post-RAG fresh path จึงไม่พิสูจน์ประสิทธิผลหรือเป็นผลของ product ปัจจุบัน

### ตารางที่ 5-3 สรุปสถานะหลักฐานทดลอง

| Artifact | Executed | Aligns with current product | ใช้สนับสนุนได้ |
|---|---|---|---|
| 28-case representation | Yes | ต่ำ/ระบบ Case State เดิม | trade-off ของ representation เท่านั้น |
| B3 events | Yes | บางส่วน | mixed exploratory signal |
| Context refinement | Yes, local ignored | ต่ำ | warning เรื่อง span loss |
| 50-case model pilot | Yes | ต่ำ | model preflight ไม่ใช่ product comparison |
| Attribute-first 33 items | Yes | เชิงแนวคิด | bottleneck/error analysis |
| No-RAG diagnostic | Yes | บางส่วนแต่ไม่มี RAG | error-mode diagnosis |
| Semantic fixture validator | Yes | infrastructure only | fixture integrity |
| Follow-up pilot | Yes | historical workflow | feasibility only |

## 5.6 ข้อจำกัดของการประเมินปัจจุบัน

1. ยังไม่มี benchmark ที่ประเมิน end-to-end current AnalysisTrace v3, gap/follow-up, frontend review และ deterministic report ร่วมกัน
2. หลายชุดข้อมูลเป็น synthetic หรือเป็น benchmark cyber QA ไม่ใช่สำนวนจริง และไม่ครอบคลุมโดเมนคดีทั่วไป
3. ตัวอย่างภาษาไทยมีใน fixture validator แต่ยังไม่มี product-quality study ภาษาไทยที่มี human gold analysis
4. การประเมินบางชุดใช้ LLM judge และบางครั้งเป็นโมเดลเดียวกับ judge รอบอื่น ทำให้ agreement ไม่เท่ากับความถูกต้อง
5. “manual scoring” ใน artifact ไม่ได้ระบุว่าเป็นผู้เชี่ยวชาญด้านอัยการ/สืบสวนหรือ blind independent annotation
6. ไม่มีการประเมิน legal correctness, evidentiary admissibility, fairness, privacy หรือผลกระทบต่อการตัดสินใจ
7. ไม่มีการวัดเวลาที่ผู้ใช้ประหยัดได้ ความเข้าใจ provenance ภาระคำถาม หรือความพึงพอใจของผู้ปฏิบัติงาน
8. การทดลองเก่าบางชุดใช้ Case State representation ที่ระบบปัจจุบันลบออกแล้ว จึงมี domain shift ทางสถาปัตยกรรม
9. Model/provider dependence สูง และ model IDs/config สามารถเปลี่ยนได้ ผลจาก Llama 3.1 8B หรือโมเดลอื่นไม่ถ่ายโอนไป default model ปัจจุบันโดยอัตโนมัติ
10. ยังไม่มี live failure/recovery study สำหรับ database outage, provider timeout, Qdrant/Neo4j failure หรือ background worker restart

ดังนั้นบทที่ 5 สรุปได้ว่าระบบมีองค์ประกอบที่ทำงานและผ่าน automated tests ตามขอบเขตที่ระบุ มี exploratory evidence หลายชุดที่ช่วยระบุปัญหาและออกแบบการทดลองต่อไป แต่ยังไม่มีหลักฐานเพียงพอสำหรับข้อสรุปว่าระบบเพิ่มความแม่นยำ ลดเวลา หรือเหมาะกับการใช้งานคดีจริง

