# Citation audit จาก backend CyberCase ปัจจุบัน

วันที่ตรวจ: 30 กันยายน 2026  
Code baseline: `main`, commit `4aa8b18ba61c3f94738169d5f54d12d8f480a622`  
ขอบเขต: อ่าน code paths ของ analysis, source extraction, follow-up, grounding, conditional technical augmentation, chat และ report; คัดงานจาก primary sources แล้วตรวจ metadata และคำอ้างที่แต่ละงานรองรับ ไม่ได้รัน model experiments หรือรับรองผลทดลองเดิมใน workspace

## 1. ข้อเสนอหลักจากโค้ด

CyberCase ควรถูกเล่าว่าเป็น **ระบบ General Case Summarization ที่อ่านข้อมูลคดีเป็นโครงสร้างพร้อมหลักฐาน ประเมินข้อมูลที่ขาดและถามเพิ่ม แล้วเขียนบทสรุป/การวิเคราะห์ ตรวจอ้างอิงกลับไปยัง case sources และแปลงผลที่เก็บไว้เป็นรายงาน** MITRE/RAG เป็น conditional technical augmentation เมื่อมีข้อมูลที่เกี่ยวข้องกับ technical/cyber context.

จากโค้ด production ที่ตรวจ:

`Case sources + answered follow-ups → gaps-only assessment → Ask / Proceed → conditional MITRE/RAG → case_reading → case_judgement → deterministic source binding → revision-checked persistence → report projection`

ถ้า policy เลือก Ask จะหยุดก่อน gate/RAG และสอง main-analysis calls. คำว่า “สอง stages” หมายถึง reading/judgement ไม่ได้หมายถึง workflow ทั้งหมดมีเพียงสอง model calls. ทั้งสองใช้ config/model selector เดียวกันและยังไม่ใช่หลักฐานว่ามีสองคนละโมเดลหรือ multi-agent collaboration.

**งานหลักที่ควรอ่านก่อนมี 12 งาน**: Attribute First, AIS, ALCE, FActScore, ACU/RoSE, Default Assistant, Michelet/Breitinger, Dehing et al., relay fidelity, Clarify When Necessary, MediQ และ Typhoon OCR. งานในชุดนี้ทั้งหมด 35 รายการ; งานปี 2026 ที่ใช้ arXiv ต้องแยกสถานะ preprint จากงานฉบับ proceedings.

## 2. กลไกจริง → ข้ออ้าง → citation

| กลไกที่ยืนยันจากโค้ด | หลักฐานใน repo | งานที่เหมาะ | ขอบเขตคำอ้าง |
|---|---|---|---|
| รวม sources ของ Case และส่ง context ที่ผูก revision | [bundle.py:28](<F:/Cybercase Framework/backend/app/sources/bundle.py:28>), [store.py:88](<F:/Cybercase Framework/backend/app/analysis/store.py:88>) | Attribute First; AIS เป็น rationale | Case รับได้หลาย sources; ยังไม่ใช่ผลพิสูจน์ multi-document reconciliation |
| Reading ให้ claims, parties, timeline, impacts ก่อน judgement | [write.py:15](<F:/Cybercase Framework/backend/app/analysis/write.py:15>), [trace.py:137](<F:/Cybercase Framework/backend/app/trace/trace.py:137>) | Attribute First; Default Assistant; Dehing | เป็นการแยกหน้าที่ extraction/generation; ไม่ใช่ implementation เดียวกับ papers |
| Judgement รับ raw sources + reading + optional technical context | [write.py:57](<F:/Cybercase Framework/backend/app/analysis/write.py:57>) | Relay fidelity; Huang; CriticBench | ใช้เป็นเหตุผลที่ต้องวัดผลของ downstream stage; ไม่รับประกัน self-correction |
| เก็บ reading fields และรับ summary/gaps/MITRE จาก judgement | [write.py:103](<F:/Cybercase Framework/backend/app/analysis/write.py:103>) | Relay fidelity; FActScore; ACU | การคง fields ตามโค้ดต่างจากความคงเดิมเชิงความหมายใน summary |
| ตรวจ quote กับ registry และแนบ document/page locators | [bind.py:254](<F:/Cybercase Framework/backend/app/trace/bind.py:254>), [quotes.py:168](<F:/Cybercase Framework/backend/app/trace/quotes.py:168>) | AIS; ALCE; Default Assistant | quote localization และ source integrity; ยังไม่ใช่ semantic entailment |
| ประเมิน gaps-only ก่อนการวิเคราะห์หลัก | [pipeline.py:63](<F:/Cybercase Framework/backend/app/analysis/pipeline.py:63>), [prompts.py:277](<F:/Cybercase Framework/backend/app/analysis/prompts.py:277>) | Clarify When Necessary; MediQ; InsufficiencyBench | คำอ้างของเมื่อควรถามต้องทดสอบกับ complete/deficient cases |
| เลือก high + askable + ไม่เคยถาม ภายใต้ budget | [clarification.py:44](<F:/Cybercase Framework/backend/app/followup/clarification.py:44>) | Clarify; Rao & Daumé เป็น comparison | bounded policy; ไม่ใช่ EVPI หรือ uncertainty calibration |
| Gate เลือก llm / encoder / never; shadow เป็น observation | [gate.py:21](<F:/Cybercase Framework/backend/app/analysis/technical_context/gate.py:21>) | RAGate; XLM-R; LADDER | branch มีจริง; active deployment mode ยัง UNCONFIRMED |
| Technique ต้องอยู่ใน retrieved context และมี known claim ID | [bind.py:114](<F:/Cybercase Framework/backend/app/trace/bind.py:114>) | AnnoCTR; LADDER; CTI Unreliable | membership/link validity; ไม่รับประกันความถูกต้องของ ATT&CK mapping |
| Native document text / per-page OCR และ metadata | [service.py:98](<F:/Cybercase Framework/backend/app/sources/ingestion/service.py:98>), [recognition.py:73](<F:/Cybercase Framework/backend/app/sources/ingestion/recognition.py:73>) | Typhoon OCR; van Strien | provider integration และ OCR error propagation; serving checkpoint ยัง UNCONFIRMED |
| Chat สร้าง answer units พร้อม basis/claims/quotes | [compose.py:127](<F:/Cybercase Framework/backend/app/chat/compose.py:127>), [compose.py:286](<F:/Cybercase Framework/backend/app/chat/compose.py:286>) | AIS; ALCE | unknown citations ถูกตัด แต่ unit text ยังอาจอยู่ ต้องประเมิน semantic support |
| Report มาจาก stored analysis/follow-up/source snapshot | [generate.py:176](<F:/Cybercase Framework/backend/app/reports/generate.py:176>), [display.py:98](<F:/Cybercase Framework/backend/app/reports/display.py:98>) | Wiseman; AGIR; forensic-report studies | deterministic projection ไม่มี report-stage LLM; ความครบต้องทดสอบตาม projection contract |
| JSON/Pydantic boundary และ stage input budget | [request.py:228](<F:/Cybercase Framework/backend/app/llm/request.py:228>), [request.py:293](<F:/Cybercase Framework/backend/app/llm/request.py:293>) | Format Restrictions | schema validity แยกจากความถูกต้องของสาระ |
| อ่าน/คิด/เขียนแยก transactions, source revision guard | [run.py:81](<F:/Cybercase Framework/backend/app/analysis/run.py:81>), [store.py:131](<F:/Cybercase Framework/backend/app/analysis/store.py:131>) | code และ official framework docs | เป็น engineering evidence ไม่ใช่ contribution ที่ต้องหา paper มารับรองทุก function |

## 3. รายละเอียด paper ทั้ง 35 งาน

การระบุ relation ใน claim-support records เป็นความสัมพันธ์ระหว่าง paper กับ **ประโยคที่ให้ cite** ไม่ใช่คำยืนยันว่า backend implements paper นั้น. “Direct” ของ AIS/ALCE/FActScore จึงหมายถึงนิยาม/วิธีประเมิน ไม่ใช่การทำงานของ binder.

### 01. Attribute First, then Generate: Locally-attributable Grounded Text Generation

**ACL 2024 · แกนหลัก · key: `attribute_first`**  
[Primary source](https://aclanthology.org/2024.acl-long.182/) · identifier: `doi:10.18653/v1/2024.acl-long.182`  
ระดับที่ตรวจเนื้อหา: abstract และวิธีใน PDF หน้า 2–3

- **ควร cite เพื่อ:** เป็นงานหลักสำหรับเหตุผลที่ให้โมเดลเลือกข้อมูลจาก source ก่อนเขียนสรุป งานต้นฉบับแยก content selection, sentence planning และ sentence generation และใช้ span ที่เลือกเป็น attribution.
- **โยงโค้ด:** [write.py:15](<F:/Cybercase Framework/backend/app/analysis/write.py:15>), [write.py:45](<F:/Cybercase Framework/backend/app/analysis/write.py:45>)
- **ขอบเขต/ความต่าง:** CyberCase มี reading และ judgement แต่ไม่ได้ทำ sentence planning/generation ตาม paper และยัง bind quote หลัง judgement จึง cite เป็นแนวคิดและงานเปรียบเทียบ ไม่เขียนว่า implement Attribute First ครบ.
- **ใช้ประเมินอะไร:** เทียบ direct generation กับ reading-first; วัดความครบของสาระ ความถูกต้องของ quote และเวลาตรวจหลักฐานของผู้ใช้.

### 02. Measuring Attribution in Natural Language Generation Models

**Computational Linguistics 49(4), 2023 · แกนหลัก · key: `ais`**  
[Primary source](https://aclanthology.org/2023.cl-4.2/) · identifier: `doi:10.1162/coli_a_00486`  
ระดับที่ตรวจเนื้อหา: abstract และคำอธิบาย AIS จากหน้า publisher

- **ควร cite เพื่อ:** ใช้ให้นิยามว่า generated statement ต้องรองรับด้วย identifiable source และแยกการอ่านเข้าใจข้อความออกจากการตัดสินว่า source รองรับข้อความนั้น.
- **โยงโค้ด:** [bind.py:43](<F:/Cybercase Framework/backend/app/trace/bind.py:43>), [bind.py:254](<F:/Cybercase Framework/backend/app/trace/bind.py:254>), [compose.py:286](<F:/Cybercase Framework/backend/app/chat/compose.py:286>)
- **ขอบเขต/ความต่าง:** Binder ตรวจว่า quote มีอยู่และอ้างถึง source ที่รู้จัก ไม่ได้ตรวจ semantic support ตาม AIS; ข้อมูลที่ผู้แจ้งรายงานก็ยังไม่ใช่ข้อเท็จจริงที่พิสูจน์แล้วในโลกจริง.
- **ใช้ประเมินอะไร:** ให้ผู้ประเมินตรวจ source → claim และ source → summary แยกจากอัตราหา quote พบ.

### 03. Enabling Large Language Models to Generate Text with Citations

**EMNLP 2023 · แกนหลัก · key: `alce`**  
[Primary source](https://aclanthology.org/2023.emnlp-main.398/) · identifier: `doi:10.18653/v1/2023.emnlp-main.398`  
ระดับที่ตรวจเนื้อหา: PDF §3.3 หน้า 4 และ human evaluation หน้า 8

- **ควร cite เพื่อ:** ใช้รองรับการประเมิน citation recall และ precision เชิงความหมาย พร้อมแยก correctness และ fluency; เป็นงานหลักเมื่ออธิบายว่ามี citation แล้วยังต้องตรวจสิ่งที่ citation รองรับ.
- **โยงโค้ด:** [trace.py:89](<F:/Cybercase Framework/backend/app/trace/trace.py:89>), [bind.py:141](<F:/Cybercase Framework/backend/app/trace/bind.py:141>), [compose.py:255](<F:/Cybercase Framework/backend/app/chat/compose.py:255>)
- **ขอบเขต/ความต่าง:** citations_verified ใน CyberCase เป็นจำนวน quote ที่ bind ได้ ไม่ใช่ ALCE citation precision/recall; หน้า summary ไม่มีการบังคับ citation ครบทุกประโยค.
- **ใช้ประเมินอะไร:** ประเมิน statement ที่มีหลักฐานรองรับทั้งหมด และ citation ที่ไม่เกี่ยวข้อง; เก็บ invalid quote rate เป็นอีก metric หนึ่ง.

### 04. FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation

**EMNLP 2023 · แกนหลัก · key: `factscore`**  
[Primary source](https://aclanthology.org/2023.emnlp-main.741/) · identifier: `doi:10.18653/v1/2023.emnlp-main.741`  
ระดับที่ตรวจเนื้อหา: official abstract

- **ควร cite เพื่อ:** ใช้รองรับการแบ่ง long-form output เป็น atomic facts แล้วตรวจสัดส่วนที่ source รองรับ เหมาะกับ claims และข้ออ้างใน summary.
- **โยงโค้ด:** [claims.py:179](<F:/Cybercase Framework/backend/app/trace/claims.py:179>), [trace.py:106](<F:/Cybercase Framework/backend/app/trace/trace.py:106>)
- **ขอบเขต/ความต่าง:** งานเดิมประเมิน biography ด้วย reliable knowledge source; ถ้าปรับเป็น case registry ให้เรียก metric ที่ดัดแปลงจาก FActScore และไม่ถือ supporting_citation ที่ locate ได้ว่าเป็น supported fact โดยอัตโนมัติ.
- **ใช้ประเมินอะไร:** วัด supported atomic precision คู่กับ coverage; output สั้นมากสามารถ precision สูงแต่ขาดสาระสำคัญได้.

### 05. On Faithfulness and Factuality in Abstractive Summarization

**ACL 2020 · ประกอบ/ประเมินผล · key: `faithful_summarization`**  
[Primary source](https://aclanthology.org/2020.acl-main.173/) · identifier: `doi:10.18653/v1/2020.acl-main.173`  
ระดับที่ตรวจเนื้อหา: official abstract

- **ควร cite เพื่อ:** เป็นงานพื้นฐานแยกความลื่นไหลของสรุปออกจากความซื่อตรงต่อ input และรองรับเหตุผลที่ ROUGE หรือความอ่านง่ายอย่างเดียวไม่เพียงพอ.
- **โยงโค้ด:** [write.py:32](<F:/Cybercase Framework/backend/app/analysis/write.py:32>), [bind.py:217](<F:/Cybercase Framework/backend/app/trace/bind.py:217>)
- **ขอบเขต/ความต่าง:** ผลจากโมเดลและชุดข้อมูลปี 2020 ไม่ใช่อัตราความผิดของโมเดลที่ CyberCase ใช้วันนี้.
- **ใช้ประเมินอะไร:** ตรวจ unsupported statements, การสลับผู้กระทำ/ผู้รับผล และข้อความที่ดูสมเหตุสมผลแต่ source ไม่รองรับ.

### 06. Revisiting the Gold Standard: Grounding Summarization Evaluation with Robust Human Evaluation

**ACL 2023 · แกนหลัก · key: `acu`**  
[Primary source](https://aclanthology.org/2023.acl-long.228/) · identifier: `doi:10.18653/v1/2023.acl-long.228`  
ระดับที่ตรวจเนื้อหา: PDF §3 หน้า 3–4

- **ควร cite เพื่อ:** ใช้สร้าง protocol วัด summary salience/coverage จาก Atomic Content Units ใน reference ที่ผู้ประเมินเตรียมไว้ ลดการให้คะแนนแบบความประทับใจรวม.
- **โยงโค้ด:** [write.py:103](<F:/Cybercase Framework/backend/app/analysis/write.py:103>), [display.py:98](<F:/Cybercase Framework/backend/app/reports/display.py:98>)
- **ขอบเขต/ความต่าง:** ACU เป็น reference-based salience evaluation ไม่ใช่ factuality verifier; gold reference ต้องมีความครอบคลุมเหมาะกับคดีและไม่สร้างจาก model output ที่กำลังทดสอบ.
- **ใช้ประเมินอะไร:** วัดการรักษาสาระที่กำหนดว่าจำเป็น พร้อมบันทึกข้อตกลงผู้ประเมินและ effect ของความยาว.

### 07. AI Assistance for Human Review of Default Judgments

**arXiv 2026, v1; cited version ระบุ Under Review · แกนหลัก · key: `default_assistant`**  
[Primary source](https://arxiv.org/abs/2607.01256) · identifier: `arxiv:2607.01256v1`  
ระดับที่ตรวจเนื้อหา: PDF หน้า 5, Cited Generation; official abstract

- **ควร cite เพื่อ:** งานระบบที่ใกล้มาก: ใช้เอกสารคดี แยก extraction ของ quote/table ตรวจคืนกับต้นฉบับ แล้วสร้าง recommendation พร้อม citation ให้คนตรวจต่อ.
- **โยงโค้ด:** [write.py:15](<F:/Cybercase Framework/backend/app/analysis/write.py:15>), [pipeline.py:136](<F:/Cybercase Framework/backend/app/analysis/pipeline.py:136>), [bind.py:232](<F:/Cybercase Framework/backend/app/trace/bind.py:232>)
- **ขอบเขต/ความต่าง:** ต้นฉบับส่งเฉพาะ quote/table ที่ locate แล้วไปยัง generation; CyberCase ส่ง reading ไป judgement ก่อน binding อีกทั้งคดี debt collection และการทดลองกับนักศึกษากฎหมายต่างจาก general case summarization. มีหน้า author ระบุ accepted AIES แต่ชุดนี้ cite arXiv version ที่ตรวจโดยไม่สมมติ proceedings.
- **ใช้ประเมินอะไร:** ใช้เป็นแบบอย่างแยกความถูกต้องของ assistant จากความถูกต้องและเวลาตรวจของผู้ใช้; การมี cited recommendation ไม่เท่ากับใช้แทนผู้พิจารณาได้.

### 08. ChatGPT, Llama, can you write my report? An experiment on assisted digital forensics reports written using (local) large language models

**Forensic Science International: Digital Investigation 48, 2024 · แกนหลัก · key: `forensic_report_llm`**  
[Primary source](https://arxiv.org/abs/2312.14607) · identifier: `doi:10.1016/j.fsidi.2023.301683`  
ระดับที่ตรวจเนื้อหา: official arXiv abstract ของบทความฉบับตีพิมพ์

- **ควร cite เพื่อ:** ใช้รองรับปัญหาและงานที่เกี่ยวข้องของ LLM-assisted forensic report writing: วิเคราะห์รูปแบบรายงานและความสามารถในการช่วยเขียนแต่ละส่วน.
- **โยงโค้ด:** [generate.py:35](<F:/Cybercase Framework/backend/app/reports/generate.py:35>), [display.py:98](<F:/Cybercase Framework/backend/app/reports/display.py:98>)
- **ขอบเขต/ความต่าง:** ผลคือการช่วยงานที่ยังต้อง proofreading ในบริบทที่ศึกษา; CyberCase ใช้ LLM ก่อนเก็บ trace และใช้ deterministic report projection ไม่ใช่ LLM เขียน PDF ใหม่.
- **ใช้ประเมินอะไร:** แยกเวลา/คุณภาพในการเขียนรายงานจากคุณภาพการวิเคราะห์ต้นทาง และคงการตรวจโดยผู้ใช้งาน.

### 09. Structured Report Generation using Local LLMs for Chat-Based Digital Forensics

**Digital Forensics Doctoral Symposium (DFDS), 2026 · แกนหลัก · key: `structured_forensic_reports`**  
[Primary source](https://research.rug.nl/en/publications/structured-report-generation-using-local-llms-for-chat-based-digi/) · identifier: `doi:10.1145/3785318.3785330`  
ระดับที่ตรวจเนื้อหา: publisher และ official university abstract

- **ควร cite เพื่อ:** งานใกล้สำหรับ multi-stage forensic pipeline: สรุป chat เป็นส่วนย่อย แล้วรวมเป็น investigative report ที่มีผู้เกี่ยวข้อง เวลา และ trace references.
- **โยงโค้ด:** [write.py:15](<F:/Cybercase Framework/backend/app/analysis/write.py:15>), [generate.py:176](<F:/Cybercase Framework/backend/app/reports/generate.py:176>)
- **ขอบเขต/ความต่าง:** เป็น local-model chat corpus, มี chunk summarization และ report generation อีก call; CyberCase ส่ง source bundle ให้ reading/judgement และ report เป็น template. งานเดิมเทียบกับ reference จาก Gemini ไม่ใช่ independent ground truth จึงไม่คัดลอกคำอ้างว่าได้ forensic truth.
- **ใช้ประเมินอะไร:** เทียบ entity/role, chronology และ citation fidelity โดยสร้าง gold ที่ตรวจเอง; cite เพื่อวางตำแหน่ง contribution ไม่ใช่ยืนยันว่า two-stage เป็นสิ่งใหม่.

### 10. Large Language Models Cannot Self-Correct Reasoning Yet

**ICLR 2024; preprint ครั้งแรก 2023 · ประกอบ/ประเมินผล · key: `self_correction_limits`**  
[Primary source](https://arxiv.org/abs/2310.01798) · identifier: `arxiv:2310.01798v2`  
ระดับที่ตรวจเนื้อหา: arXiv v2 §3.3 และ OpenReview publication record

- **ควร cite เพื่อ:** ตอบคำถามว่า stage ถัดไปอาจทำคำตอบที่ถูกให้ผิดได้หรือไม่ โดยแยก correct→incorrect และ incorrect→correct ในการ intrinsic self-correction.
- **โยงโค้ด:** [write.py:32](<F:/Cybercase Framework/backend/app/analysis/write.py:32>), [write.py:103](<F:/Cybercase Framework/backend/app/analysis/write.py:103>)
- **ขอบเขต/ความต่าง:** CyberCase judgement เป็นการเขียนสรุป/วิเคราะห์จาก reading ร่วมกับ raw sources ไม่ใช่โจทย์ self-correction; ผลขึ้นกับงาน โมเดล และ prompt ที่ทดสอบ ไม่ใช้ชื่อ paper เป็นข้อสรุปว่า LLM ทุกตัวแก้คำตอบไม่ได้.
- **ใช้ประเมินอะไร:** รายงาน harm, repair, omission และ propagation แยกกัน เมื่อจัดประเภทคุณภาพข้อมูลก่อน/หลัง stage.

### 11. CriticBench: Benchmarking LLMs for Critique-Correct Reasoning

**Findings ACL 2024 · ประกอบ/ประเมินผล · key: `criticbench`**  
[Primary source](https://aclanthology.org/2024.findings-acl.91/) · identifier: `doi:10.18653/v1/2024.findings-acl.91`  
ระดับที่ตรวจเนื้อหา: official abstract และ previous primary full-text reading

- **ควร cite เพื่อ:** ใช้เป็น precedent ของการประเมิน generation, critique และ correction แยก stage และการให้โมเดลอื่นทำงานต่อจาก response ที่ตรึงไว้.
- **โยงโค้ด:** [write.py:24](<F:/Cybercase Framework/backend/app/analysis/write.py:24>), [write.py:32](<F:/Cybercase Framework/backend/app/analysis/write.py:32>)
- **ขอบเขต/ความต่าง:** benchmark เน้น reasoning ห้ากลุ่ม ไม่ใช่ preservation ของ case facts; reading/judgement ไม่ได้ implement critic loop หรือ debate.
- **ใช้ประเมินอะไร:** ตรึง stage-1 output แล้วเปลี่ยน stage-2 model/prompt เพื่อแยกผลของแต่ละ stage ไม่ให้ randomness ต้นทางปนกัน.

### 12. Faithful, Not Corrective: Model Capability Governs Message-Format Effects in Multi-Hop Agent Relays

**arXiv 2026, v2 ลงวันที่ 17 กันยายน; preprint · แกนหลัก · key: `relay_fidelity`**  
[Primary source](https://arxiv.org/abs/2607.09678) · identifier: `arxiv:2607.09678v2`  
ระดับที่ตรวจเนื้อหา: full HTML §3–5 และ official metadata

- **ควร cite เพื่อ:** ตรงกับคำถามก่อนหน้า: controlled relay ของ atomic facts มีการวัดแต่ละ hop และ paired error injection เพื่อแยกข้อมูลสูญหายจากข้อผิดพลาดที่ถูกส่งต่อ.
- **โยงโค้ด:** [write.py:94](<F:/Cybercase Framework/backend/app/analysis/write.py:94>), [write.py:103](<F:/Cybercase Framework/backend/app/analysis/write.py:103>)
- **ขอบเขต/ความต่าง:** ทดลอง pure relay หลาย hops กับข้อเท็จจริงสังเคราะห์; CyberCase มี extraction และ judgement ซึ่งเปลี่ยนหน้าที่ของงาน. ข้อมูลที่คงเดิมอาจผิดตั้งแต่ต้น และ paper นี้ยังเป็น preprint.
- **ใช้ประเมินอะไร:** ใช้ per-fact retention, role/date/amount preservation และ paired injected error โดยให้ stage-2 เห็น raw source เหมือน production; metric ของการย่อความต้องยอมรับการละรายละเอียดที่ไม่จำเป็น.

### 13. When LLMs Play the Telephone Game: Cultural Attractors as Conceptual Tools to Evaluate LLMs in Multi-turn Settings

**ICLR 2025; preprint ครั้งแรก 2024, examined arXiv v4 · ประกอบ/ประเมินผล · key: `telephone_game`**  
[Primary source](https://arxiv.org/abs/2407.04503) · identifier: `arxiv:2407.04503v4`  
ระดับที่ตรวจเนื้อหา: official abstract, full HTML และ conference PDF identity

- **ควร cite เพื่อ:** ใช้เปิดประเด็น information transformation เมื่อผล LLM ถูกส่งต่อหลายครั้ง และผลของคำสั่งต่อ text drift.
- **โยงโค้ด:** [write.py:15](<F:/Cybercase Framework/backend/app/analysis/write.py:15>)
- **ขอบเขต/ความต่าง:** วัด toxicity, positivity, difficulty และ length เป็นหลัก ไม่ใช่ correctness หรือ atomic-fact recall จึงเป็น background มากกว่าหลักฐานตรงของ factual corruption ใน CyberCase.
- **ใช้ประเมินอะไร:** อาจวัด length/style drift เป็นผลรอง; ใช้ source-grounded facts เป็นผลหลักของคดี.

### 14. Clarify When Necessary: Resolving Ambiguity Through Interaction with LMs

**Findings NAACL 2025; preprint ครั้งแรก 2023 · แกนหลัก · key: `clarify_when_necessary`**  
[Primary source](https://aclanthology.org/2025.findings-naacl.306/) · identifier: `doi:10.18653/v1/2025.findings-naacl.306`  
ระดับที่ตรวจเนื้อหา: official abstract

- **ควร cite เพื่อ:** งานหลักสำหรับ when-to-ask: ควรแยกการตัดสินใจถามออกจากการสร้างคำถาม และคิดถึงต้นทุนความรบกวนผู้ใช้.
- **โยงโค้ด:** [assess.py:13](<F:/Cybercase Framework/backend/app/analysis/assess.py:13>), [clarification.py:44](<F:/Cybercase Framework/backend/app/followup/clarification.py:44>)
- **ขอบเขต/ความต่าง:** ต้นฉบับใช้ IntentSim/entropy ของ user intents; backend ใช้ priority, askable, previously asked keys และ budget ไม่ใช่ calibrated uncertainty หรือ IntentSim.
- **ใช้ประเมินอะไร:** วัด ask/no-ask บน complete/deficient cases พร้อม unnecessary questions และประโยชน์ต่อคำตอบสุดท้าย.

### 15. MediQ: Question-Asking LLMs and a Benchmark for Reliable Interactive Clinical Reasoning

**NeurIPS 2024 · แกนหลัก · key: `mediq`**  
[Primary source](https://proceedings.neurips.cc/paper_files/paper/2024/hash/32b80425554e081204e5988ab1c97e9a-Abstract-Conference.html) · identifier: `doi:10.52202/079017-0908`  
ระดับที่ตรวจเนื้อหา: official proceedings abstract

- **ควร cite เพื่อ:** งานหลักสำหรับ acquire information ก่อนสรุปเมื่อ context ไม่ครบ และ benchmark ที่ประเมิน question asking กับ downstream reasoning ร่วมกัน.
- **โยงโค้ด:** [pipeline.py:63](<F:/Cybercase Framework/backend/app/analysis/pipeline.py:63>), [conversation.py:54](<F:/Cybercase Framework/backend/app/followup/conversation.py:54>)
- **ขอบเขต/ความต่าง:** ข้อมูลและ gold เป็น clinical reasoning; ไม่ย้ายผลทดลองมารับรองงานคดีทั่วไป. จำนวนรอบที่ backend จำกัดเป็น policy ของระบบ ไม่ใช่ policy optimal ของ MediQ.
- **ใช้ประเมินอะไร:** วัดข้อมูลที่ได้เพิ่ม ความถูกต้องหลังตอบ follow-up จำนวนคำถาม และกรณีผู้ใช้ไม่มีข้อมูล.

### 16. InsufficiencyBench: Evaluating LLM legal advice on underspecified user queries

**arXiv 2026; record กล่าวถึง ICML AI4Law workshop · ประกอบ/ประเมินผล · key: `insufficiencybench`**  
[Primary source](https://arxiv.org/abs/2608.20220) · identifier: `arxiv:2608.20220`  
ระดับที่ตรวจเนื้อหา: official abstract

- **ควร cite เพื่อ:** รองรับการมี gold สำหรับข้อมูลที่ขาดอย่างมีผลต่อคำตอบ และมี complete cases เป็น negative controls เพื่อไม่ให้โมเดลถามหรือ hedge ทุกครั้ง.
- **โยงโค้ด:** [prompts.py:18](<F:/Cybercase Framework/backend/app/analysis/prompts.py:18>), [claims.py:214](<F:/Cybercase Framework/backend/app/trace/claims.py:214>)
- **ขอบเขต/ความต่าง:** taxonomy 8 missing elements และสาม failure modes ใน US legal advice ไม่ใช่ gap keys ของ CyberCase และไม่ใช่การตรวจความครบของ case ทุกชนิด.
- **ใช้ประเมินอะไร:** สร้าง removal/ambiguity/conflict conditions จากข้อมูลที่ผู้เชี่ยวชาญกำหนดว่าจำเป็น พร้อมชุด complete control.

### 17. Detecting missing information in bug descriptions

**ESEC/FSE 2017 · ประกอบ/ประเมินผล · key: `missing_bug_information`**  
[Primary source](https://personal.utdallas.edu/~vince/papers/fse17.html) · identifier: `doi:10.1145/3106237.3106285`  
ระดับที่ตรวจเนื้อหา: official author abstract และ evaluation description

- **ควร cite เพื่อ:** งานคลาสสิกของการตรวจ missing information ที่มี content categories ชัดเจน และประเมิน absence detection ด้วย precision/recall.
- **โยงโค้ด:** [prompts.py:18](<F:/Cybercase Framework/backend/app/analysis/prompts.py:18>), [clarification.py:30](<F:/Cybercase Framework/backend/app/followup/clarification.py:30>)
- **ขอบเขต/ความต่าง:** Observed/Expected Behavior และ Steps to Reproduce เป็นองค์ประกอบ bug report; ไม่ถือเป็น forensic completeness checklist ที่ validated แล้ว.
- **ใช้ประเมินอะไร:** แยก precision/recall ของแต่ละ gap category จากคะแนนความอ่านง่ายของ follow-up question.

### 18. Giveme5W1H: A Universal System for Extracting Main Events from News Articles

**arXiv 2019 version ที่ตรวจ · ประกอบ/ประเมินผล · key: `giveme5w1h`**  
[Primary source](https://arxiv.org/abs/1909.02766) · identifier: `arxiv:1909.02766`  
ระดับที่ตรวจเนื้อหา: official abstract

- **ควร cite เพื่อ:** รองรับ vocabulary 5W1H สำหรับอธิบายเหตุการณ์ เหมาะกับส่วนเหตุผลของ checklist ที่ใช้ใน gap prompt.
- **โยงโค้ด:** [prompts.py:18](<F:/Cybercase Framework/backend/app/analysis/prompts.py:18>), [trace.py:36](<F:/Cybercase Framework/backend/app/trace/trace.py:36>)
- **ขอบเขต/ความต่าง:** ระบบเดิมเป็น rules สำหรับ English news และหา main event; backend เป็น LLM general-case analysis. 5W1H ไม่รับประกันว่าพยานหลักฐานเพียงพอ และไม่ใช่หลักฐานว่า backend ใช้ Giveme5W1H.
- **ใช้ประเมินอะไร:** ใช้เป็น background ของ field selection; ไม่ยก precision ใน news มาเป็น performance ของ Case analysis หรือ cite poster คนละปีแทนฉบับนี้.

### 19. CASIE: Extracting Cybersecurity Event Information from Text

**AAAI 2020 · เฉพาะ cyber/technical branch · key: `casie`**  
[Primary source](https://ojs.aaai.org/index.php/AAAI/article/view/6401) · identifier: `doi:10.1609/aaai.v34i05.6401`  
ระดับที่ตรวจเนื้อหา: official publisher abstract และ task description

- **ควร cite เพื่อ:** เหมาะกับบท event/argument extraction และ dataset สำหรับตรวจ entity/role preservation ใน cyber subset.
- **โยงโค้ด:** [claims.py:179](<F:/Cybercase Framework/backend/app/trace/claims.py:179>), [trace.py:36](<F:/Cybercase Framework/backend/app/trace/trace.py:36>)
- **ขอบเขต/ความต่าง:** claims/timeline ใน backend ไม่ได้เท่ากับ CASIE triggers, event hoppers และ arguments; ไม่ใช้ CASIE ชุดเดียวอ้าง general-case performance และ annotation ที่ไม่มี match ไม่เท่ากับ hallucination.
- **ใช้ประเมินอะไร:** กำหนด schema mapping ก่อนวัด actual-event/argument coverage และแยก ontology mismatch ออกจาก source-unsupported claim.

### 20. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks

**NeurIPS 2020 · เฉพาะ cyber/technical branch · key: `rag`**  
[Primary source](https://proceedings.neurips.cc/paper/2020/hash/6b493230-Abstract.html) · identifier: `arxiv:2005.11401`  
ระดับที่ตรวจเนื้อหา: official proceedings abstract

- **ควร cite เพื่อ:** ใช้รองรับหลักการ conditioning generation ด้วย retrieved external knowledge ในบท background ของ technical augmentation.
- **โยงโค้ด:** [rag_client.py:20](<F:/Cybercase Framework/backend/app/analysis/technical_context/rag_client.py:20>), [retrieve.py:102](<F:/Cybercase Framework/backend/app/analysis/technical_context/retrieve.py:102>)
- **ขอบเขต/ความต่าง:** งานเดิมใช้ dense Wikipedia retrieval และ fine-tuned formulations; backend ที่ตรวจพิสูจน์ HTTP boundary กับ context contract ไม่ได้พิสูจน์การใช้ architecture/training ของ Lewis et al. หรือ GraphRAG.
- **ใช้ประเมินอะไร:** ประเมิน technical branch แยกจาก case-fact analysis; external knowledge อธิบายบริบท ไม่เติมเหตุการณ์ที่ไม่ได้อยู่ใน case sources.

### 21. Adaptive Retrieval-Augmented Generation for Conversational Systems

**Findings NAACL 2025; preprint ครั้งแรก 2024 · เฉพาะ cyber/technical branch · key: `ragate`**  
[Primary source](https://aclanthology.org/2025.findings-naacl.30/) · identifier: `doi:10.18653/v1/2025.findings-naacl.30`  
ระดับที่ตรวจเนื้อหา: official abstract

- **ควร cite เพื่อ:** ใกล้กับหลักการ conditional retrieval: ให้ gate เลือกว่าต้องเรียก retrieval หรือไม่ และประเมินประโยชน์ของ gate.
- **โยงโค้ด:** [gate.py:21](<F:/Cybercase Framework/backend/app/analysis/technical_context/gate.py:21>), [retrieve.py:102](<F:/Cybercase Framework/backend/app/analysis/technical_context/retrieve.py:102>)
- **ขอบเขต/ความต่าง:** label ของ RAGate คือความจำเป็น/utility ของ RAG ใน conversation; local gate คือ MITRE applicability. งานนี้ไม่รับรอง local binary threshold หรือ claim ว่าเหมาะกว่า always-RAG.
- **ใช้ประเมินอะไร:** เทียบ never/always/gated ภายใต้ label และ downstream task ที่ตรงกัน พร้อม false skip, false invocation, latency และ cost.

### 22. Unsupervised Cross-lingual Representation Learning at Scale

**ACL 2020 · เฉพาะ cyber/technical branch · key: `xlmr`**  
[Primary source](https://aclanthology.org/2020.acl-main.747/) · identifier: `doi:10.18653/v1/2020.acl-main.747`  
ระดับที่ตรวจเนื้อหา: official abstract และ local checkpoint config

- **ควร cite เพื่อ:** เป็น model attribution ที่ต้อง cite เมื่ออธิบาย encoder branch: local config ระบุ XLMRobertaForSequenceClassification และ model_type xlm-roberta.
- **โยงโค้ด:** [gate_encoder.py:38](<F:/Cybercase Framework/backend/app/analysis/technical_context/gate_encoder.py:38>), [gate_encoder.py:74](<F:/Cybercase Framework/backend/app/analysis/technical_context/gate_encoder.py:74>), [config.json:3](<F:/Cybercase Framework/backend/xlmr_ladder_best/xlmr_ladder_best/config.json:3>)
- **ขอบเขต/ความต่าง:** ยืนยันได้ว่ามี branch/checkpoint แบบนี้ แต่ active deployment mode ยัง UNCONFIRMED. ความสามารถหลายภาษาของ base model ไม่รับรอง Thai relevance gate, threshold 0.1 หรือ calibration ของ checkpoint นี้.
- **ใช้ประเมินอะไร:** รายงาน base/checkpoint, preprocessing, threshold-selection split และผลแยกภาษา; อย่าอ้าง softmax เป็น calibrated confidence.

### 23. Looking Beyond IoCs: Automatically Extracting Attack Patterns from External CTI

**RAID 2023; preprint ครั้งแรก 2022 · เฉพาะ cyber/technical branch · key: `ladder`**  
[Primary source](https://arxiv.org/abs/2211.01753) · identifier: `doi:10.1145/3607199.3607208`  
ระดับที่ตรวจเนื้อหา: primary arXiv abstract และ publisher metadata

- **ควร cite เพื่อ:** รองรับ domain/task ของ attack-pattern extraction และ ATT&CK mapping; ชื่อ base ใน gate.json ระบุ LADDER sentence classifier.
- **โยงโค้ด:** [gate.json:2](<F:/Cybercase Framework/backend/xlmr_ladder_best/xlmr_ladder_best/gate.json:2>), [gate_encoder.py:74](<F:/Cybercase Framework/backend/app/analysis/technical_context/gate_encoder.py:74>)
- **ขอบเขต/ความต่าง:** gate.json ไม่ใช่หลักฐานครบของ training lineage, dataset split หรือ reproduction; extraction/mapping ของ LADDER ต่างจาก binary applicability ที่ใช้ใน production.
- **ใช้ประเมินอะไร:** ถ้ารายงานฝึกด้วย dataset นี้ให้แนบ revision/license/splits และ mapping เป็น gate labels; แยก in-domain test จาก external validation.

### 24. AnnoCTR: A Dataset for Detecting and Linking Entities, Tactics, and Techniques in Cyber Threat Reports

**LREC-COLING 2024; correct Anthology ID 2024.lrec-main.103 · เฉพาะ cyber/technical branch · key: `annoctr`**  
[Primary source](https://aclanthology.org/2024.lrec-main.103/) · identifier: `arxiv:2404.07765`  
ระดับที่ตรวจเนื้อหา: official published abstract และ arXiv identity

- **ควร cite เพื่อ:** ใช้รองรับ external cyber-domain evaluation ของเอกสารที่ annotate entities, temporal expressions และ implicit/explicit ATT&CK concepts ภายใน document context.
- **โยงโค้ด:** [gate_encoder.py:74](<F:/Cybercase Framework/backend/app/analysis/technical_context/gate_encoder.py:74>), [bind.py:114](<F:/Cybercase Framework/backend/app/trace/bind.py:114>)
- **ขอบเขต/ความต่าง:** native task เป็น span/concept linking ไม่ใช่ binary gate โดยตรง; การแปลง annotations เป็น relevance label ต้องประกาศกติกาและคง context. .720 เป็น paper อื่น.
- **ใช้ประเมินอะไร:** ประเมิน corpus shift และเทียบ document/span/technique units ให้ตรงกับสิ่งที่ระบบส่งออก โดยไม่ flatten annotations จนเปลี่ยนโจทย์.

### 25. Large Language Models Are Unreliable for Cyber Threat Intelligence

**ARES 2025 proceedings, Springer chapter · เฉพาะ cyber/technical branch · key: `cti_unreliable`**  
[Primary source](https://arxiv.org/abs/2503.23175) · identifier: `doi:10.1007/978-3-032-00627-1_17`  
ระดับที่ตรวจเนื้อหา: primary arXiv abstract และ DOI metadata

- **ควร cite เพื่อ:** ใช้รองรับความจำเป็นในการตรวจ consistency/confidence ของ CTI output และไม่พึ่งข้อความที่โมเดลพูดอย่างมั่นใจ.
- **โยงโค้ด:** [retrieve.py:155](<F:/Cybercase Framework/backend/app/analysis/technical_context/retrieve.py:155>), [bind.py:114](<F:/Cybercase Framework/backend/app/trace/bind.py:114>)
- **ขอบเขต/ความต่าง:** ข้อค้นพบของ tested models/reports ไม่ใช่คำตัดสินทุก LLM. Binder ที่ technique ID อยู่ใน retrieved table และมี claim ID ยังไม่ได้พิสูจน์ semantic correctness ของ mapping.
- **ใช้ประเมินอะไร:** เทียบ technique mapping กับ gold และตรวจความสม่ำเสมอหลาย run นอกเหนือจาก schema validity.

### 26. AGIR: Automating Cyber Threat Intelligence Reporting with Natural Language Generation

**IEEE Big Data 2023 · เฉพาะ cyber/technical branch · key: `agir`**  
[Primary source](https://arxiv.org/abs/2310.02655) · identifier: `doi:10.1109/BigData59044.2023.10386116`  
ระดับที่ตรวจเนื้อหา: primary arXiv abstract และ publisher metadata

- **ควร cite เพื่อ:** ใช้เป็นงาน related system ของ formal entity representation → template → LLM report rewriting และการประเมิน report fidelity.
- **โยงโค้ด:** [generate.py:35](<F:/Cybercase Framework/backend/app/reports/generate.py:35>), [display.py:98](<F:/Cybercase Framework/backend/app/reports/display.py:98>)
- **ขอบเขต/ความต่าง:** backend นี้ไม่ได้สร้าง STIX entity graph และไม่ได้มี LLM report rewriting. Cite เป็น comparison; ห้ามนำ recall/การประหยัดเวลาของ AGIR มาเป็นผลของ CyberCase.
- **ใช้ประเมินอะไร:** ถ้าจะเปรียบเทียบ report renderer ต้องตรึง analysis input และ declared intended content ก่อนวัด retained/changed/new facts.

### 27. Challenges in Data-to-Document Generation

**EMNLP 2017 · ประกอบ/ประเมินผล · key: `data_to_document`**  
[Primary source](https://aclanthology.org/D17-1239/) · identifier: `doi:10.18653/v1/D17-1239`  
ระดับที่ตรวจเนื้อหา: PDF §3.2 หน้า 4

- **ควร cite เพื่อ:** รองรับการแยก content selection, relation generation และ ordering เมื่อข้อมูลมีโครงสร้างถูกแปลงเป็นรายงาน.
- **โยงโค้ด:** [display.py:98](<F:/Cybercase Framework/backend/app/reports/display.py:98>), [display.py:201](<F:/Cybercase Framework/backend/app/reports/display.py:201>)
- **ขอบเขต/ความต่าง:** เดิมเป็น RotoWire record-to-document และใช้ learned extractor; ไม่ย้ายสูตร/ตัว extractor มาใช้กับคดีโดยไม่มี adaptation. Deterministic projection ยังคัดทิ้งหรือเปลี่ยนการแสดง field ได้.
- **ใช้ประเมินอะไร:** กำหนด projection contract ของ findings/status/negation/roles/sources/quotes/limitations และตรวจ snapshot → structured report → HTML/PDF.

### 28. Beyond Traditional Benchmarks: Analyzing Behaviors of Open LLMs on Data-to-Text Generation

**ACL 2024 · ประกอบ/ประเมินผล · key: `open_llm_data_to_text`**  
[Primary source](https://aclanthology.org/2024.acl-long.651/) · identifier: `doi:10.18653/v1/2024.acl-long.651`  
ระดับที่ตรวจเนื้อหา: official abstract

- **ควร cite เพื่อ:** ใช้รองรับว่าข้อความจาก structured input ต้องตรวจ semantic errors แม้ fluent และ coherent โดยศึกษา open LLMs กับข้อมูลใหม่จาก public APIs.
- **โยงโค้ด:** [write.py:32](<F:/Cybercase Framework/backend/app/analysis/write.py:32>), [display.py:98](<F:/Cybercase Framework/backend/app/reports/display.py:98>)
- **ขอบเขต/ความต่าง:** report renderer ของ CyberCase ไม่ได้เรียก LLM; ประยุกต์กับ judgement summary หรือใช้เป็นเหตุผลในการตรึง renderer ไม่ใช้ error rate ของ paper เป็นตัวเลขของระบบนี้.
- **ใช้ประเมินอะไร:** ตรวจ omission, wrong value และ unsupported addition แยกจาก readability.

### 29. Let Me Speak Freely? A Study On The Impact Of Format Restrictions On Large Language Model Performance.

**EMNLP 2024 Industry Track · ประกอบ/ประเมินผล · key: `format_restrictions`**  
[Primary source](https://aclanthology.org/2024.emnlp-industry.91/) · identifier: `doi:10.18653/v1/2024.emnlp-industry.91`  
ระดับที่ตรวจเนื้อหา: official abstract

- **ควร cite เพื่อ:** ใช้รองรับการแยก format validity จาก task accuracy และจัด format ablation อย่างระมัดระวังเมื่อ intermediate output เป็น JSON.
- **โยงโค้ด:** [request.py:228](<F:/Cybercase Framework/backend/app/llm/request.py:228>), [trace.py:137](<F:/Cybercase Framework/backend/app/trace/trace.py:137>), [trace.py:147](<F:/Cybercase Framework/backend/app/trace/trace.py:147>)
- **ขอบเขต/ความต่าง:** paper ศึกษา format restrictions ใน tested tasks/models; ไม่สรุปว่า JSON ทำให้ CyberCase แย่ลงเสมอ. Pydantic/schema-valid output ไม่รับประกัน fact correctness.
- **ใช้ประเมินอะไร:** เปรียบเทียบ JSON กับ prose/labeled text โดยตรึงเนื้อหาข้อมูล ความยาว budget และจำนวน calls; บันทึก schema failures แยก.

### 30. Typhoon OCR: Open Vision-Language Model For Thai Document Extraction

**arXiv 2026; preprint · แกนหลัก · key: `typhoon_ocr`**  
[Primary source](https://arxiv.org/abs/2601.14722) · identifier: `arxiv:2601.14722`  
ระดับที่ตรวจเนื้อหา: official abstract และ recognizer source

- **ควร cite เพื่อ:** ควร cite ในบท OCR/model dependency เพราะ backend มี TyphoonDocumentRecognizer ผ่าน HTTP; paper อธิบายการ extract เอกสารไทยและอังกฤษด้วย VLM.
- **โยงโค้ด:** [recognition.py:73](<F:/Cybercase Framework/backend/app/sources/ingestion/recognition.py:73>), [service.py:221](<F:/Cybercase Framework/backend/app/sources/ingestion/service.py:221>)
- **ขอบเขต/ความต่าง:** settings ใช้ชื่อ provider model typhoon-ocr ไม่ยืนยันว่า serving checkpoint เป็น OCR V1.5 ตาม paper. ไม่อ้างว่า CyberCase รองรับ handwriting ได้ตามประสิทธิภาพที่ paper รายงาน.
- **ใช้ประเมินอะไร:** บันทึก endpoint/model version และทดสอบ printed/scanned document ของงานจริง พร้อม semantic propagation.

### 31. Assessing the Impact of OCR Quality on Downstream NLP Tasks

**ICAART 2020 · ประกอบ/ประเมินผล · key: `ocr_downstream`**  
[Primary source](https://www.turing.ac.uk/news/publications/assessing-impact-ocr-quality-downstream-nlp-tasks) · identifier: `doi:10.5220/0009169004840496`  
ระดับที่ตรวจเนื้อหา: official author-institution abstract และ DOI metadata

- **ควร cite เพื่อ:** ใช้รองรับการประเมิน OCR แบบ extrinsic คือดูผลกระทบต่อ downstream NLP ไม่หยุดที่ character/word accuracy.
- **โยงโค้ด:** [service.py:98](<F:/Cybercase Framework/backend/app/sources/ingestion/service.py:98>), [provenance.py:5](<F:/Cybercase Framework/backend/app/sources/ingestion/provenance.py:5>), [quotes.py:53](<F:/Cybercase Framework/backend/app/trace/quotes.py:53>)
- **ขอบเขต/ความต่าง:** งานเดิมเป็น heritage text และหลาย traditional NLP tasks ไม่ใช่ LLM summarization. Quote ที่ bind ได้กับ OCR text ยังอาจตรงกับ OCR ที่อ่านผิดจากภาพต้นฉบับ.
- **ใช้ประเมินอะไร:** เทียบ clean/reference text กับ OCR ของเอกสารเดียวกัน; วัด CER ควบคู่ names, dates, amounts, negation และ downstream facts.

### 32. The Hitchhiker’s Guide to Testing Statistical Significance in Natural Language Processing

**ACL 2018 · ประกอบ/ประเมินผล · key: `statistical_tests`**  
[Primary source](https://aclanthology.org/P18-1128/) · identifier: `doi:10.18653/v1/P18-1128`  
ระดับที่ตรวจเนื้อหา: official abstract และ test-selection discussion

- **ควร cite เพื่อ:** ใช้ในบท evaluation methodology สำหรับเลือก paired tests ตาม metric และ design รวมทั้งความเป็น dependent samples ของข้อความ.
- **โยงโค้ด:** [write.py:15](<F:/Cybercase Framework/backend/app/analysis/write.py:15>)
- **ขอบเขต/ความต่าง:** การมีชื่อ statistical test ไม่แทนการกำหนด unit of analysis. หลาย claims/sentences ใน case เดียวกันไม่ควรถูกนับเป็น independent cases.
- **ใช้ประเมินอะไร:** จับคู่ configuration บน case เดียวกัน; ใช้ case-level confidence intervals/resampling และ McNemar เฉพาะ binary paired outcome ที่เหมาะสม.

### 33. With Little Power Comes Great Responsibility

**EMNLP 2020 · ประกอบ/ประเมินผล · key: `statistical_power`**  
[Primary source](https://aclanthology.org/2020.emnlp-main.745/) · identifier: `doi:10.18653/v1/2020.emnlp-main.745`  
ระดับที่ตรวจเนื้อหา: official abstract

- **ควร cite เพื่อ:** ใช้รองรับการรายงาน uncertainty/effect sizes และข้อจำกัดของชุดทดลองเล็กสำหรับ model comparisons/human evaluation.
- **โยงโค้ด:** [write.py:15](<F:/Cybercase Framework/backend/app/analysis/write.py:15>)
- **ขอบเขต/ความต่าง:** ไม่มีจำนวน sample สากลที่รับรองว่า 30/50/100 cases เพียงพอ; ต้องสัมพันธ์กับ effect ที่คาดและ design.
- **ใช้ประเมินอะไร:** กำหนด primary endpoint และ planned power/precision; ผลไม่ significant ไม่เท่ากับสองวิธีเท่ากัน.

### 34. Non-Determinism of “Deterministic” LLM System Settings in Hosted Environments

**Eval4NLP workshop 2025 · ประกอบ/ประเมินผล · key: `api_nondeterminism`**  
[Primary source](https://aclanthology.org/2025.eval4nlp-1.12/) · identifier: `doi:10.18653/v1/2025.eval4nlp-1.12`  
ระดับที่ตรวจเนื้อหา: official abstract

- **ควร cite เพื่อ:** รองรับ repeated-run controls และบันทึก provider/model/prompt/config/retry เพราะ hosted output อาจต่างแม้ตั้งค่าเหมือนเดิม.
- **โยงโค้ด:** [request.py:293](<F:/Cybercase Framework/backend/app/llm/request.py:293>), [settings.py:13](<F:/Cybercase Framework/backend/app/llm/settings.py:13>), [store.py:88](<F:/Cybercase Framework/backend/app/analysis/store.py:88>)
- **ขอบเขต/ความต่าง:** ไม่ถือ temperature=0 เป็น reproducibility guarantee. Optional usage receipt ใน request_stage ไม่ได้แปลว่า production เติม token/cost records ครบทุก stage.
- **ใช้ประเมินอะไร:** ตรึง case/source revision และ intermediate outputs ใน inter-stage tests; รายงาน repeated-run variation และจำนวน failures รวม.

### 35. Learning to Ask Good Questions: Ranking Clarification Questions using Neural Expected Value of Perfect Information

**ACL 2018 · ประกอบ/ประเมินผล · key: `clarification_evpi`**  
[Primary source](https://aclanthology.org/P18-1255/) · identifier: `doi:10.18653/v1/P18-1255`  
ระดับที่ตรวจเนื้อหา: official abstract

- **ควร cite เพื่อ:** ใช้เป็น related method ที่นิยามคำถามดีจาก usefulness ของคำตอบ และเรียนรู้การจัดอันดับ clarification questions.
- **โยงโค้ด:** [clarification.py:30](<F:/Cybercase Framework/backend/app/followup/clarification.py:30>), [clarification.py:44](<F:/Cybercase Framework/backend/app/followup/clarification.py:44>)
- **ขอบเขต/ความต่าง:** backend รับ candidates ตาม model output order และถาม candidates[0] ที่ผ่าน policy; ไม่ได้คำนวณ EVPI หรือพิสูจน์การเลือกคำถามที่ให้ข้อมูลมากที่สุด.
- **ใช้ประเมินอะไร:** วัด answer usefulness/ข้อมูลสำคัญที่ได้ต่อหนึ่งคำถาม; ใช้เป็น future comparator ถ้าจะเพิ่ม ranking method.

## 4. ตำแหน่งที่ควร cite ในงานเขียน

| ตำแหน่งในบท | Citation ที่เลือกก่อน | สิ่งที่เขียนได้ |
|---|---|---|
| ปัญหาและ related systems ของการสรุป/เขียนรายงานคดี | Michelet/Breitinger; Dehing; Default Assistant | มี prior work ใน report assistance, two-stage forensic summarization และ cited case review; ต้องวางตำแหน่ง CyberCase เทียบกับงานเหล่านี้ |
| เหตุผลของ reading ก่อน judgement | Attribute First; Default Assistant | แยก selection/extraction จาก generation เป็นแนวทางที่มี precedent; อธิบายส่วนที่เราปรับและ order ของ binder ตามจริง |
| Source grounding/citation | AIS; ALCE | นิยาม source support และ metric ของ citation; แล้วแยกสิ่งที่ backend ตรวจได้จริงออกจาก semantic evaluation |
| ความเสี่ยงเมื่อ stage ถัดไปทำงานต่อ | Relay fidelity; Huang; CriticBench | preservation, propagation, repair และ harm เป็นคนละผลลัพธ์; งาน telephone game ใช้เป็น background ของ drift |
| Information-gap/follow-up | Clarify When Necessary; MediQ; InsufficiencyBench | ประเมิน when to ask, missing information และ benefit/burden ของคำถาม; policy budget เป็นการออกแบบของ CyberCase |
| Conditional MITRE/RAG | RAGate; XLM-R; LADDER; AnnoCTR; MITRE official report | applicability gate เป็น task เฉพาะ; source case facts กับ external taxonomy มีคนละบทบาท |
| OCR | Typhoon OCR; van Strien | ระบุ provider และวัด error propagation ไปยัง facts; paper ไม่ได้แทนการบันทึก serving model version |
| Report | Wiseman; AGIR; Michelet/Breitinger | อธิบาย structured projection, preservation และ template เทียบกับ neural rewriting; ไม่กล่าวว่ามี report-stage LLM |
| Evaluation | FActScore; ACU; ALCE; Dror; Card; Atıl | atomic support + coverage + citation + uncertainty; แยก task metrics จาก system receipts |

ประโยคที่นำไปปรับใช้ได้ โดยใส่ citation ในตำแหน่งท้ายประโยค:

1. “งานก่อนหน้าเสนอให้เลือกข้อมูลหรือหลักฐานจาก source ก่อนสร้างข้อความ เพื่อให้ตรวจที่มาของเนื้อหาได้ในระดับละเอียด [Attribute First; Default Assistant] ใน CyberCase เราแยก reading และ judgement แต่ตรวจ quote แบบ deterministic หลัง judgement.”
2. “การตรวจว่า quote มีอยู่ในเอกสารเป็นการตรวจ text provenance ส่วนการประเมินว่า quote รองรับ claim ต้องตรวจ semantic attribution เพิ่มเติม [AIS; ALCE].”
3. “ระบบที่ context ไม่ครบควรประเมินทั้งความจำเป็นของการถามและประโยชน์ของข้อมูลที่ได้รับ [Clarify; MediQ] สำหรับ CyberCase การถามถูกควบคุมด้วย gap eligibility และ fixed budget.”
4. “เราใช้ atomic source-support และสาระสำคัญที่ควรปรากฏเป็นคนละมิติของการประเมินสรุป [FActScore; ACU] เพื่อไม่ให้สรุปที่สั้นแต่ขาดข้อมูลได้คะแนนสูงจาก precision อย่างเดียว.”
5. “การสร้างรายงานจาก stored analysis เป็น deterministic projection เราจึงประเมินการรักษา field และ reference ตาม report contract แยกจากคุณภาพการวิเคราะห์ต้นทาง โดยมี record-level content evaluation เป็นแนวทางประกอบ [Wiseman].”

ประโยคเหล่านี้เป็นร่างคำอธิบายและ evaluation rationale ไม่ใช่ผลทดลองของ CyberCase.

## 5. สิ่งที่ citation ยังทำให้เราอ้างไม่ได้

- **“สอง-stage ดีกว่า one-shot”**: ต้องมีผลทดลอง matched inputs/prompts/model/budgets และ control ที่มีสอง calls เช่น prose notes → judgement เพื่อไม่ให้จำนวน calls ปนกับผลของ structure.
- **“stage 2 ไม่เปลี่ยนข้อมูลจาก stage 1”**: `joined_trace` คง reading fields ตาม implementation แต่ summary ใหม่ยังเปลี่ยนคน เวลา negation หรือความแน่นอนของข้อความได้; ต้องวัดความหมาย.
- **“มี exact_quote แล้วไม่มี hallucination”**: quote อาจอยู่ใน source แต่ไม่รองรับ claim; quote ที่ไม่ผ่านถูกตัดโดยไม่ลบ claim text ทุกกรณี และ summary ไม่ถูก semantic verified ทั้งหมด.
- **“อ่านหลักฐานที่ตรวจแล้วก่อน judgement”**: order ปัจจุบัน bind หลัง judgement; ห้ามเล่ากลับลำดับให้เหมือน Default Assistant.
- **“analysis_trace เป็น Chain-of-Thought ที่ faithful”**: trace เป็น structured artifact ของข้อมูล/ข้ออ้าง/rationale ไม่ใช่หลักฐานว่าเป็น faithful internal reasoning ของโมเดล.
- **“ทำ Self-Refine / Reflexion / CoVe / trained Self-RAG / multi-agent debate”**: จาก main-analysis flow ที่ตรวจไม่มี procedure เหล่านั้น. Cite เป็น related work ได้เฉพาะเมื่ออธิบายความต่างและความเกี่ยวข้องจริง.
- **“ใช้ GraphRAG แบบงานของ Edge et al.”**: backend พิสูจน์ได้เพียง conditional HTTP call/context contract; ชื่อ library/service ไม่พอ ต้อง audit retrieval algorithms/data structures ใน service เพิ่มก่อนอ้าง.
- **“encoder + LLM ช่วยกันตัดสินแบบ ensemble”**: encoder shadow ใน config เป็น observational branch ไม่ใช่ fusion decision.
- **“XLM-R gate เข้าใจคดีไทยดี”**: base model multilingual และชื่อ checkpoint ไม่แทน external Thai evaluation/calibration.
- **“CASIE/AnnoCTR พิสูจน์ general-case summarization”**: เป็น cyber-domain evidence เท่านั้น และ ontology/unit ไม่ตรงกับ output ทุก field.
- **“รายงานคงข้อมูล 100% เพราะไม่มี LLM”**: deterministic code อาจเลือก field, clip/clean text หรือเปลี่ยน representation; ต้องเทียบกับ intended projection contract และตรวจ render stage.
- **“citation/page metadata คือ forensic chain of custody”**: เป็น provenance ของข้อความและ locator; ยังไม่พิสูจน์ authenticity, acquisition procedure หรือ integrity guarantees ของวัตถุพยานในโลกจริง.
- **“prompt บอกว่าเอกสารเป็น untrusted data จึงกัน prompt injection แล้ว”**: มี instruction boundary แต่ยังไม่ใช่ empirical resistance guarantee.

## 6. การทดลองที่ papers เหล่านี้ช่วยวางได้

ส่วนนี้เป็นข้อเสนอการประเมิน ไม่ได้รันใน audit นี้ และไม่อ้างผลจากเอกสารทดลองเดิมที่ยังไม่ได้ตรวจ artifacts.

### 6.1 Core analysis และผลของ representation

- **B0:** raw source → final analysis.
- **P1:** raw source → prose notes → final analysis.
- **B1:** raw source → structured reading → final analysis แบบที่ backend มี.
- ใช้ final schema/model, raw source availability, user language, decoding/input/output budgets และ gold เดียวกัน. บันทึก context length เพราะ reading เพิ่ม input ให้ stage 2; อย่าปล่อย truncation เป็น confound ที่ไม่รายงาน.
- Report primary outcomes: atomic source support, required-content coverage, participant/role preservation และ epistemic/negation preservation. Report schema failures, latency, token/cost และ retries เป็น supporting outcomes.
- B1 เทียบ B0 บอกประโยชน์รวมของ pipeline; B1 เทียบ P1 ช่วยแยกประโยชน์ของ structured representation จากการมี extra call. การเทียบเหล่านี้ยังต้องมีผลจริงก่อนกล่าวว่า representation ช่วย.

### 6.2 Stage-1 → stage-2 fidelity

ตรึง reading output ของ case เดียวกันแล้วรัน downstream conditions แบบจับคู่ โดยเก็บ raw sources ไว้ตาม production. แบ่งผลเป็น preserved-correct, repaired, propagated-error, newly-corrupted และ omitted. กำหนดสาระที่ “ต้องคง” ล่วงหน้า; summary ไม่จำเป็นต้องกล่าวถึงทุก claim จึงห้ามนับการละรายละเอียดทั้งหมดว่า corruption.

ทำ paired clean/injected reading ที่เปลี่ยนเฉพาะชื่อ role/date/amount/negation พร้อม gold ของ raw source โดยตรึงอย่างอื่น. ใช้ตรวจว่า downstream stage เชื่อ reading ที่ผิดหรือคืนกลับ source ได้หรือไม่; ห้ามถือ high retention อย่างเดียวเป็น high factuality.

Citation ที่ตรง: relay fidelity; Huang สำหรับ correct→incorrect/incorrect→correct; FActScore และ ACU สำหรับ support กับ coverage. ชื่อ metric ของเราเป็น adaptation ต้องบอกชัด ไม่แสร้งว่าเป็น official benchmark score.

### 6.3 Gap detection และถามเพิ่ม

ใช้ complete cases คู่กับกรณีที่ลบ essential information, ทำ ambiguous/conflicting facts และ explicitly unknown answers. Essential information ต้องมาจาก annotation criteria ไม่ใช่ให้โมเดลที่ทดสอบเป็นคนตัดสิน gold เอง.

วัด gap-category precision/recall, ask/no-ask, unnecessary asks, repeated/unavailable questions, จำนวน rounds/questions และ downstream content improvement หลังมีคำตอบ. ถ้าลบ “ช่องหนึ่ง” แล้ว gold ขึ้นตามช่องนั้น ต้องระบุว่าประเมิน controlled missing-field recovery ไม่ใช่ general readiness judgment.

Citation: Clarify, MediQ, InsufficiencyBench; Chaparro สำหรับ category-wise missing-information evaluation; Rao สำหรับ question usefulness/ranking comparison.

### 6.4 Grounding แยกสามชั้น

1. **Localization:** quote/source ID/page locator ถูกต้องหรือไม่.
2. **Support:** source/quote รองรับ claim และ generated statement หรือไม่.
3. **Coverage:** claims/summary/report ครอบคลุมข้อมูลที่สำคัญหรือไม่.

เก็บผลก่อนและหลัง binding รวม invalid/uncited output ไม่คำนวณเฉพาะ citations ที่ผ่านแล้ว เพราะจะได้ผลดีจากการ filter โดย construction. อย่าใช้ `citations_verified` เป็น semantic precision หรือ `sources_cited` เป็น content recall.

Citation: AIS; ALCE; FActScore; ACU. Source support ประเมินความซื่อตรงต่อข้อมูลคดี ไม่พิสูจน์ว่าคำกล่าวของผู้แจ้งเป็นจริง.

### 6.5 Report fidelity

ตรึง selected analysis ID/source membership/follow-up snapshot; กำหนดว่า field ใดต้องแสดงหรือเป็น intentional omission แล้วเปรียบเทียบ trace → structured report → rendered HTML/PDF. ตรวจ participant roles, chronology, claim/status/negation, source/quote locators, gaps และ limitations. การเผยให้ตรวจย้อนกลับได้กับการคง semantic content เป็นคนละ metric.

Citation: Wiseman เป็น evaluation background; AGIR, Michelet/Breitinger และ Dehing เป็น related report systems. ผู้ใช้เขียน/ตรวจเร็วขึ้นต้องมี user study ไม่อนุมานจาก code deterministic.

### 6.6 Conditional technical augmentation และ OCR

Gate: never/always/gated เป็นสาม conditions; ต้องนิยาม applicability/utility label ให้ตรงกับโจทย์ก่อนวัด false skip/false invocation. XLM-R probabilities ต้องไม่ถูกเรียก calibrated certainty โดยไม่ตรวจ; label จาก LADDER/AnnoCTR ต้องระบุ conversion. ATT&CK ID ที่อยู่ใน context ยังต้องประเมิน semantic mapping แยก.

OCR: compare clean/reference text กับ OCR ของเอกสารเดียวกัน แล้ววัด CER และความผิดของชื่อ วัน จำนวนเงิน role/negation/uncertainty ใน downstream output. Typhoon provider ไม่ยืนยัน serving revision หรือ handwriting support. การ bind กับ OCR text ไม่เท่ากับตรวจภาพต้นฉบับ.

### 6.7 Experimental reporting

- ใช้ Case เป็นหลักในการ pairing/resampling; sentences หรือ claims จาก case เดียวกันมี dependence.
- ระบุ primary endpoint, confidence interval/effect size และจำนวน samples; เลือก statistical test ให้เหมาะกับ outcome/design.
- แยก no-difference evidence จาก insufficient power; ตัวเลขที่ดูใกล้กันไม่พิสูจน์ equivalence.
- บันทึก source revision/input hash, prompt version, actual model/provider, intermediate outputs, retry/failure, input/output tokens และ repeated-run variation. Existing config snapshot ช่วยได้แต่ไม่แทน receipts ครบทั้งหมด.
- Model API run failures อยู่ใน denominator หรือรายงานแยกด้วยกติกาที่ประกาศล่วงหน้า ไม่ drop จนเหลือแต่ successful cases.

Citation: Dror; Card; Atıl.

## 7. Contribution และความใหม่ที่ควรพูดอย่างระวัง

จาก closest prior work ที่พบ **การทำ two-stage LLM, extract ก่อน generate, citations หรือ template report อย่างใดอย่างหนึ่งไม่เพียงพอเป็น novelty claim**. Attribute First, Default Assistant, Dehing และ AGIR มีองค์ประกอบใกล้เคียงอยู่แล้ว.

คำอ้างที่น่าจะปกป้องได้เมื่อมีผลทดลองคือ **การศึกษาว่า structured source-based reading ช่วยรักษาสาระ บทบาทผู้เกี่ยวข้อง และความไม่แน่นอนระหว่าง extraction → judgement สำหรับ General Case Summarization ได้หรือไม่ ภายใต้ budget ที่เทียบกันได้** พร้อมแยก gap acquisition, quote binding, OCR และ deterministic report fidelity. นี่เป็นข้อเสนอจาก code/literature ไม่ใช่การประกาศว่า contribution ใหม่ได้รับการพิสูจน์แล้ว.

CASIE/LADDER/AnnoCTR รองรับเฉพาะ cyber subset. ถ้าจะสรุปถึง general cases ต้องมีชุดข้อมูลและ ground truth ที่สอดคล้องกับ broader scope. ยังคง `1 Case → N Documents` เป็น data/interface capability แต่การอ้าง cross-document reconciliation ต้องมี test/evaluation ของความขัดแย้งและการอ้างอิงข้ามเอกสารจริง.

## 8. การตรวจ citation และ publication version

- Metadata resolved ใหม่ครบ 35/35 ผ่าน Crossref DOI หรือ official arXiv API; บันทึกใน [citation_lock.json](<F:/Cybercase Framework/docs/research/backend-citation-audit-2026-09-30/citation_lock.json>).
- Claim-support records อ่านและกำหนดขอบเขตโดยผู้ตรวจใน [citation_requests.json](<F:/Cybercase Framework/docs/research/backend-citation-audit-2026-09-30/citation_requests.json>). Script ตรวจ schema/status/hash/metadata ไม่ได้อ่าน paper แล้วพิสูจน์ semantic support ให้อัตโนมัติ.
- [references.bib](<F:/Cybercase Framework/docs/research/backend-citation-audit-2026-09-30/references.bib>) มี 35 entries: publisher BibTeX/Crossref transform เป็นหลัก; arXiv entries ใช้ metadata ที่ resolve แล้ว. Published venues ของ ICLR/NeurIPS และ AnnoCTR ตรวจแยกจากวันที่ first preprint.
- AnnoCTR published source คือ **2024.lrec-main.103**, ไม่ใช่ .720. .720 เป็น “How Good Are LLMs at Out-of-Distribution Detection?”.
- Default Assistant ใช้ชื่อจาก **arXiv: AI Assistance for Human Review of Default Judgments**; Stanford PDF ชื่อ Court Review เป็นอีก snapshot. ไม่ผสมจำนวน cases/participants/results ข้าม snapshots และไม่อ้าง proceedings ที่ยังไม่ได้ resolve.
- Clarify เป็น Findings NAACL **2025** แม้ preprint2023; RAGate เป็น Findings NAACL **2025** แม้ preprint2024. Michelet/Breitinger เป็น journal **2024** แม้ DOI/preprint มี 2023.
- Huang cite ICLR **2024** และ Perez cite ICLR **2025** ใน BibTeX published record; metadata lock ที่ resolve ด้วย arXiv เก็บ first-preprint ปี 2023/2024 ตาม provider. ทั้งสองเป็นคนละวันที่ที่ถูกต้อง ต้องไม่ปนกัน.
- Relay fidelity เป็น **v2, 17 Sep 2026**, ผู้เขียน Sicheng Zeng; ไม่ใช้ชื่อ/author จาก snapshot เก่ามาแทน.
- AIS มี David Reitter เป็นผู้เขียนลำดับท้ายด้วย; ใช้ author list ที่ตรวจใหม่ใน BibTeX.
- ไม่คัดผล performance ที่เอกสารอื่นใน workspace รายงานมาเป็นผล validated ใน audit นี้.
- การอ่าน content-depth ของแต่ละ entry ระบุไว้ด้านบน: ไม่ใช่ systematic review ที่อ่านทุก appendix หรือรับประกันว่าไม่มีงานใกล้เคียงอื่น.

## 9. Official technical reference เพิ่มเติม

การใช้ ATT&CK ควรอ้างแหล่งเจ้าของ taxonomy ด้วย ไม่ใช้ LADDER/AnnoCTR แทนการให้เครดิต ATT&CK:

Strom, B. E., Applebaum, A., Miller, D. P., Nickels, K. C., Pennington, A. G., & Thomas, C. B. **MITRE ATT&CK: Design and Philosophy**. MITRE report MP180360R1; originally July 2018, revised March 2020. [Official PDF](https://attack.mitre.org/docs/ATTACK_Design_and_Philosophy_March_2020.pdf).

[technical_references.bib](<F:/Cybercase Framework/docs/research/backend-citation-audit-2026-09-30/technical_references.bib>) เก็บ reference นี้แยกไว้. นี่เป็น official technical report ที่ตรวจ cover/metadata โดยตรง ไม่มี DOI/arXiv จึงแยกจาก 35-record DOI/arXiv lock. ใช้ version ของ taxonomy จริงจาก RAG corpus เมื่อเขียน methodology; version ปัจจุบันของ deployed corpus ยัง UNCONFIRMED. FastAPI, Pydantic, SQLAlchemy, rendering libraries และ HTTP contracts ให้อ้าง official docs/code ตามสิ่งที่ใช้งานจริง ไม่ต้องหา academic paper มารับรองทุก engineering choice.

## 10. Artifacts และการตรวจ

- [paper_inventory.json](<F:/Cybercase Framework/docs/research/backend-citation-audit-2026-09-30/paper_inventory.json>): priorities, groups และ primary URLs.
- [code_inventory.json](<F:/Cybercase Framework/docs/research/backend-citation-audit-2026-09-30/code_inventory.json>): 29 paths, SHA-256 และ AST function/class line anchors จาก baseline ที่ตรวจ.
- [citation_requests.json](<F:/Cybercase Framework/docs/research/backend-citation-audit-2026-09-30/citation_requests.json>): scoped support records.
- [citation_lock.json](<F:/Cybercase Framework/docs/research/backend-citation-audit-2026-09-30/citation_lock.json>): fresh metadata, provider URLs และ hashes.
- [references.bib](<F:/Cybercase Framework/docs/research/backend-citation-audit-2026-09-30/references.bib>): reusable bibliography.
- [metadata_sources.json](<F:/Cybercase Framework/docs/research/backend-citation-audit-2026-09-30/metadata_sources.json>) และ [bibliography_receipts.json](<F:/Cybercase Framework/docs/research/backend-citation-audit-2026-09-30/bibliography_receipts.json>): lookup provenance.
- [citation_index.txt](<F:/Cybercase Framework/docs/research/backend-citation-audit-2026-09-30/citation_index.txt>): plain-text key coverage index สำหรับตรวจ bibliography ไม่ใช่ manuscript.
- [VERIFICATION.md](<F:/Cybercase Framework/docs/research/backend-citation-audit-2026-09-30/VERIFICATION.md>): คำสั่งและผลตรวจ consistency/links/code hashes.

ไม่แก้ application code, models, data, existing thesis documents หรือ user-owned experiment-plan JSON. ไม่รัน provider inference, training, application tests หรือ model benchmarks. Ledger ถูกปรับเพื่อบันทึก task นี้; การตรวจ bibliography/artifacts เท่านั้นเป็น validation ที่ทำในรอบนี้.
