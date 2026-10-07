# Attribute First, then Generate: การปรับใช้ข้ามโดเมนและตำแหน่งของ CyberCase

วันที่ตรวจ: 2026-10-04 • CyberCase HEAD: `5fdfb4d6608477ed748afbf687a804c4930c7f21`

## ข้อค้นพบหลัก

การนำหลัก “เลือกหลักฐานก่อนสร้างผลลัพธ์” ไปใช้ในโดเมนเฉพาะ มักเพิ่ม **หน่วยข้อมูลที่เหมาะกับงาน เกณฑ์ตัดสิน โครงสร้างงานปลายทาง และการประเมินที่ตรงกับงานนั้น** มากกว่าการเปลี่ยนลำดับ extract → generate เพียงอย่างเดียว ตัวอย่างที่ชัดคือ Default Assistant: เปลี่ยนการสร้างข้อความที่มี citation ให้เป็นการตรวจข้อกำหนดของสำนวนทีละข้อ และวัดผลว่าคนตรวจสำนวนทำงานได้ถูกต้องและเร็วขึ้นหรือไม่

อย่างไรก็ตาม **การอ้าง paper AfG ไม่เท่ากับการนำวิธี AfG ไปใช้** ในชุดที่ตรวจนี้ Default Assistant ใช้โดยตรง; Spectrum ระบุว่าใช้กระบวนทัศน์ร่วมกัน; Generation Programs ต่อแนวคิดการวางแผนด้วยโปรแกรม; AgentGEO/CiteLab ใช้เป็น engine หรือ workflow; MedGraphRAG ใช้เป็น baseline; FinRAGBench-V อ้างเป็น background แต่สร้างคำตอบกับ citations พร้อมกัน งานการศึกษาและนิติวิทยาศาสตร์มี workflow ใกล้เคียง แต่ยังไม่ยืนยันสายการต่อยอดจาก AfG

สำหรับ CyberCase ตำแหน่งที่อธิบายได้จากโค้ดปัจจุบันคือ **การจัดข้อความจากหลักฐานให้เป็น claims ที่มีประเภท สถานะ และ provenance แล้วให้ parties/timeline/impacts ใช้ claim IDs ร่วมกัน ก่อนสังเคราะห์ภาพรวมสำนวน** หลักฐาน source quotes ยังคงอยู่ ผล contribution ต้องมาจากการทดลองว่ากระบวนการนี้รักษาการย้อนตรวจและความครอบคลุมข้อมูลได้อย่างไร ไม่ใช่อนุมานความใหม่หรือประสิทธิผลจากการมี JSON schema

## ขอบเขตและความเข้มของหลักฐาน

- ดาวน์โหลด PDF ฉบับเต็มได้ **12 ฉบับ**: งานต้นฉบับ 1 และงานเปรียบเทียบ 11 อ่าน method/evaluation/appendix ที่เกี่ยวกับข้ออ้างในรายงาน ไม่ได้อ้างว่าอ่านทุกหน้าของทุก appendix
- อีก **1 งาน** คือ Auditable Evidence Trails อ่านได้จาก indexed excerpts ของ PDF ต้นฉบับ; direct download ติด HTTP 403/browser challenge จึงแยกสถานะ partial access และไม่รับรอง acceptance หรือผลทดลองฉบับเต็ม
- ค้นชื่อวิธีและชื่อผู้แต่ง ผ่าน primary repositories, ค้น forward citations ด้วย OpenAlex และลอง Semantic Scholar ดัชนีได้ไม่ครบ: ACL record มี 14 citing records, arXiv record มี 2 ที่ซ้ำ และ Semantic Scholar ติด 404/429 ผลนี้ไม่ใช่รายการผู้ใช้วิธีทั้งหมด
- พบชื่อเรื่องด้าน fire-safety compliance, scientific-profile narratives และ medical evidence-driven CoT แต่เข้า method จาก IEEE ไม่ได้ จึงไม่ใช้ชื่อเหล่านั้นยืนยันการปรับ AfG ดู [access notes](<F:/Cybercase Framework/docs/research/attribute-first-domain-survey-2026-10-04/ACCESS_NOTES.md>)
- ตรวจ metadata ของ 12 scholarly records สดจาก Crossref/arXiv และเก็บ hash ใน `citation_lock.json`; การตรวจ metadata ไม่ได้ทำ semantic claim verification อัตโนมัติ การจัดความสัมพันธ์ด้าน method มาจากการอ่านต้นฉบับ
- เก็บ PDF, extracted text และภาพหน้าเอกสารไว้ใน `literature/` ซึ่ง `.gitignore` กันไว้จากการ stage ตามปกติ ไม่ได้ commit/push/publish ต้นฉบับเหล่านี้

ตารางที่นำไปใช้ต่อ: [CSV](<F:/Cybercase Framework/docs/research/attribute-first-domain-survey-2026-10-04/comparison_matrix.csv>) • [JSON](<F:/Cybercase Framework/docs/research/attribute-first-domain-survey-2026-10-04/comparison_matrix.json>) • [BibTeX](<F:/Cybercase Framework/docs/research/attribute-first-domain-survey-2026-10-04/references.bib>) • [validation receipts](<F:/Cybercase Framework/docs/research/attribute-first-domain-survey-2026-10-04/VERIFICATION.md>)

## 1. ต้องหักสิ่งที่งานต้นฉบับมีอยู่แล้วออกก่อน

คำว่า Attribute ในชื่องานหมายถึง **attribution: ระบุว่าเนื้อหามาจากหลักฐานใด** ไม่ใช่การ extract attributes/features สำหรับ domain schema

[Slobodkin et al., ACL 2024](https://aclanthology.org/2024.acl-long.182/) ทำสามขั้น: เลือก source spans → จัด spans เป็น ordered sentence clusters → สร้างประโยคตามแผนโดยเห็นข้อความก่อนหน้า ICL implementation ตรวจ spans ด้วย string matching และละทิ้ง spans ที่หาไม่เจออยู่แล้ว งานยังมี fine-tuned variants และ constrained copying สำหรับ spans/plans

ดังนั้น intermediate representation, multi-document input, fine-grained citation, แยก selection จาก generation, ตรวจการคัดลอก และ fine-tuning **ไม่ใช่สิ่งที่งาน domain เพิ่มขึ้นโดยอัตโนมัติ** ต้องระบุว่าปรับชนิด representation หรือหน้าที่ของการตรวจอย่างไร

ผลต้นฉบับมี trade-off: PDF p.7 Table 3 ใน MDS เวลา verification 47 → 22 วินาที แต่ human AIS 89.3 → 79.9; Table 4 ใน LFQA เวลา 59 → 35 วินาที และ AIS 87.6 → 94.4 จึงไม่ควรสรุปว่าวิธีนี้เพิ่ม attribution accuracy ทุกงาน อ้าง numbers ตาม task/variant และหน่วยในตาราง ไม่ขยายเป็นเวลาเฉลี่ยตรวจสำนวนทั้งเรื่อง

หลักฐาน: PDF pp.3–5 §§3.1–3.3; pp.6–8 Tables 1–4

## 2. เทียบหลายโดเมน: เค้าเปลี่ยนอะไร

| งาน / โดเมน | ความสัมพันธ์กับ AfG | สิ่งที่เพิ่มหรือเปลี่ยนจากการสร้างข้อความที่มี citation | หลักฐานการประเมิน |
|---|---|---|---|
| [Default Assistant — กฎหมาย](https://arxiv.org/abs/2607.01256) | นำมาใช้โดยตรง | หลักฐานต่อ legal subrequirement; quotes + tables; dependency graph; ตรวจตำแหน่งและคัดลอกจากต้นฉบับ; Satisfied/Not Satisfied พร้อมคำอธิบาย | majority labels รายข้อ + randomized human-assistance study |
| [Spectrum — medical QA / การอธิบายให้อ่านง่าย / multihop](https://arxiv.org/abs/2411.17375) | ระบุว่าใช้ paradigm ร่วมกัน | ควบคุมระดับ quotation/paraphrase/entailment/abstraction โดยใช้ quotes เดียวกัน; เลือกความย่อและรูปแบบให้เหมาะกับงาน | utility, fluency, citation coverage/precision และ time-to-verify แยกตามงาน |
| [MedGraphRAG — เวชระเบียนและความรู้แพทย์](https://aclanthology.org/2025.acl-long.1381/) | AfG เป็น baseline | medical entities + UMLS types; graph แยก patient/source/definition; hierarchical retrieval และ refinement | medical QA/fact-checking + long-form evaluation โดย clinicians/laypersons |
| [FinRAGBench-V / RGenCite — การเงิน](https://aclanthology.org/2025.emnlp-main.211/) | background citation; วิธีหลักต่างกัน | หน่วยอ้างอิงเป็น page image และ bounding box ของกราฟ/ตาราง; arithmetic/time/multipage tasks; visual citation evaluator | retrieval, answer accuracy, page/block citation precision/recall |
| [LLM Specialists / SynSciQA — ESG และ climate QA](https://aclanthology.org/2024.acl-long.105/) | evidence-based QA สายเกี่ยวข้อง; ไม่ยืนยันต่อจาก AfG | ฝึกจากข้อมูลที่กรอง source relevance, citation format และ entailment; ทดสอบ domain transfer กับรายงาน sustainability และ IPCC/IPBES | in-domain/OOD source quality และ attributability; human audit ของตัวกรอง |
| [Dehing et al. — นิติวิทยาศาสตร์แชต](https://doi.org/10.1145/3785318.3785330) | workflow สองขั้นใกล้เคียง; ไม่ยืนยันสาย AfG | timestamp/participant/fact/TraceID records → รายงาน actors/roles/timeline; local-model context splitting; แยกข้อเท็จจริงกับสมมติฐาน | entity, role, timeline, Trace ID, factual consistency และ reasoning |
| [Auditable Evidence Trails — การศึกษา](https://openreview.net/pdf/18fca98950e6d2957a20e706f0480ddb67b588a4.pdf) | workflow ใกล้เคียง; เข้าถึงบางส่วน | subrubric ที่ยังไม่มีคะแนน → scoring records พร้อม source/rationale/flags; ตรวจคะแนนและ source presence; lecturer calibration | อ่าน method excerpts ได้; ยังไม่ตรวจ evaluation ทั้งฉบับ |
| [AgentGEO — เว็บและ GEO](https://arxiv.org/abs/2603.09296) | ใช้ AfG เป็น evaluation engine | เพิ่มระบบ diagnose → repair → retest บน HTML/content และรวม edits ข้าม queries; train/test เป็นระดับหน้าเว็บ | citation visibility และการรักษาเนื้อหาหน้าเว็บ; held-out queries |

### 2.1 Default Assistant: เปลี่ยนจากประโยคที่มี citation เป็นข้อเสนอแนะตามเกณฑ์งาน

ต้นฉบับล่าสุดที่ตรวจคือ **AI Assistance for Human Review of Default Judgments**, arXiv:2607.01256v1 ไม่ใช้ numbers ปนกับ Stanford manuscript เก่าที่ชื่อและชุดข้อมูลต่างกัน

สิ่งที่ domain เพิ่มมีสามชั้น: **task decomposition** เป็นเจ็ด legal requirements/subrequirements; **evidence handling** สำหรับเอกสารสำนวนที่มี OCR/table/page structure; และ **decision output** ที่แจ้ง Satisfied/Not Satisfied พร้อมเหตุผลให้ผู้ตรวจพิจารณา โหนดที่ขึ้นต่อกันใช้ข้อมูลจากโหนดก่อนหน้าได้

ในการ cited generation ระบบเลือก quotes/tables ก่อน ใช้ fuzzy whitespace-agnostic matching กับ quotes และ regex ของค่าตารางเพื่อหาต้นฉบับ แล้วแทน candidate ด้วยข้อความที่คัดลอกจาก source จริงก่อนส่งให้ generator นี่เป็นการปรับการหา/รักษาหลักฐานให้เข้ากับเอกสารศาล; หลักการตรวจว่า quote อยู่ใน source มีใน AfG เดิมแล้ว

ชุดข้อมูล 188 cases ใช้สามผู้ annotator และ two-thirds majority; 66 law students ถูกสุ่มให้ตรวจแบบไม่มีหรือมี assistant Table 2 รายงาน accuracy เพิ่ม **5.3 percentage points** และเวลาลด **25.9%** ผลนี้สนับสนุนประโยชน์ของ **ระบบช่วยตรวจทั้งระบบ** ไม่แยก causal effect ของ AfG และไม่ใช่การทดลองกับผู้พิพากษาที่ใช้งานจริงทั้งหมด [ต้นฉบับ pp.3–6](https://arxiv.org/pdf/2607.01256v1)

บทเรียนต่อ CyberCase: ต้องบอกว่า claim/status/reference จะช่วยให้ผู้ใช้ทำงานใดสำเร็จ ไม่จบที่มี citation ถูก format

### 2.2 Spectrum: เพิ่มการควบคุมการแปลงหลักฐานให้เหมาะกับผู้ใช้

งานนี้ไม่สร้าง medical ontology แต่แยกระดับการแปลงข้อความ: quote, paraphrase, ย่อ/อนุมานภายในหลักฐาน และ abstraction ที่เพิ่มข้อมูลได้ สร้าง quoted generation ก่อน แล้วให้ variants อื่น rewrite โดยเห็น quoted generation แทน raw snippets ใช้ชุด quotes ร่วมกันเพื่อควบคุมการเปรียบเทียบ

ด้าน medical MASH ใช้ gold snippets จาก WebMD; ด้าน Eta3G ให้ตอบในรูปแบบเด็กประถม; ด้าน multihop ต้องรวม premises ข้ามแหล่ง งานวัด 480 queries, 7 systems, 31 MTurk annotators **perceived utility ไม่ใช่ clinical correctness** เมื่อทำข้อความย่อและลื่นขึ้น coverage/verification effort อาจเสียไป Section 6.2 ยกปัญหาคำตอบแพทย์ที่ quote ยาวแต่ paraphrase อย่างเดียวไม่ช่วยตัดส่วนเกิน [ต้นฉบับ §§4–6,10.1](https://arxiv.org/pdf/2411.17375v1)

บทเรียนต่อ CyberCase: ภาพรวมสำนวนย่อกว่าหลักฐานได้ แต่ต้องวัดสิ่งที่ตกหล่นและการย้อนตรวจ ไม่สมมติว่าการย่อดีขึ้นพร้อม grounding โดยไม่มี trade-off

### 2.3 MedGraphRAG: เพิ่มโครงสร้างความรู้และการแยกแหล่งอำนาจ

แยก graphs ของข้อมูลผู้ใช้ เอกสารทางการแพทย์ และคำจำกัดความ UMLS แล้วเชื่อม entity/reference/definition; graph summaries มี tags ทางเวชระเบียน ใช้ U-Retrieval ค้นจากภาพรวมลงสู่รายละเอียดแล้ว refine กลับขึ้นด้านบน

หน่วยนี้ต่างจาก source quote: entity มี name/type/context และ graph links ใช้ semantic similarity สิ่งที่เพิ่มเป็น **retrieval/knowledge representation** วิธีหลักไม่ได้ใช้ three-stage AfG pipeline; §3.3.2 ระบุ ATTR-FIRST เป็น comparator ประเมินทั้ง medical choices, health fact-checking และ long-form responses โดย 7 clinicians/5 laypersons [ต้นฉบับ pp.2–8](https://aclanthology.org/2025.acl-long.1381.pdf)

บทเรียนต่อ CyberCase: การเชื่อมข้อมูลคดีเข้าความรู้ภายนอกต้องรักษาว่าอะไรเป็น case evidence และอะไรเป็น analytical context การมี graph link ไม่รับรอง entailment หรือความจริงของข้อสรุป

### 2.4 FinRAGBench-V: เพิ่มการอ้างอิงที่มองเห็นตำแหน่งหลักฐานได้

โจทย์การเงินต้องอ่าน table/chart และบางคำตอบต้องคำนวณหรือรวมหลายหน้า จึงให้ citation เป็น page ID + block coordinates ไม่ใช่ source text อย่างเดียว และมี evaluator ระดับ page/block ทั้ง bounding-box และ image-crop

QA pairs ถูกสร้างแล้วตรวจคุณภาพ เหลือ 1,394 ข้อจาก corpus 60,780 หน้าภาษาจีนและ 51,219 หน้าอังกฤษ §5.2 ระบุ **answer และ visual citations ถูกสร้างพร้อมกัน** และ §2 บอกว่าปรับวิธี visual citation ของ VISA จึงไม่ใช่หลักฐานว่าการเงินนำ AfG มาแก้โจทย์โดยตรง [ต้นฉบับ pp.3–7](https://aclanthology.org/2025.emnlp-main.211.pdf)

บทเรียนต่อ CyberCase: provenance ควรระบุตำแหน่งหลักฐานที่ผู้ใช้ตรวจได้ แต่ page/block locator เป็นคนละเรื่องกับการยืนยันว่าข้อความนั้นสนับสนุน claim

### 2.5 LLM Specialists: เพิ่มคุณภาพข้อมูลและการทดสอบข้ามโดเมน

ตัวกรองแยก source relevance, citation format และ answer entailment; AttrScore สองโมเดลต้องเห็นตรงกันจึงรับข้อมูลเป็น attributable มี relevant/irrelevant source mixes และเงื่อนไขยอมรับว่าไม่มีคำตอบเมื่อ sources ไม่ตอบโจทย์

ChatReport test มาจาก corporate sustainability reports ส่วน ClimateQA test มาจาก IPCC/IPBES ถือเป็น **OOD evaluation ของ evidence-based QA specialists** ไม่ใช่การเพิ่ม AfG inference pipeline สำหรับสองโดเมน ไม่พบ AfG/Slobodkin ใน extracted PDF ฉบับที่ตรวจ [ต้นฉบับ pp.2–8](https://aclanthology.org/2024.acl-long.105.pdf)

บทเรียนต่อ CyberCase: การบอกว่ารองรับ general cases ต้องมีผลจากข้อมูลที่ห่างจากโดเมนพัฒนา; การมี schema ใช้ร่วมกันหรือมี text-to-JSON ที่รันได้ยังไม่พิสูจน์ generalization

### 2.6 Dehing: prior work ที่ใกล้ “อ่านหลักฐาน → ภาพรวมสำนวน” มาก

Stage 1 สร้าง timestamp/participants/fact/TraceID records จาก chat parts; Stage 2 รวมเป็นรายงาน actors/roles/timeline พร้อม exact Trace IDs ใช้ context-bounded chunks สำหรับ local LLMs และมี policy แยก facts/hypotheses และระบุ uncertainty อยู่แล้ว

จึงไม่ควรอ้างว่า **สองขั้น, actor table, timeline หรือการระบุความไม่แน่นอน** เป็นของใหม่จาก CyberCase เพียงลำพัง ในส่วน evaluation งานนี้แยก entity/role/time/Trace ID/factual/reasoning quality แต่ทดลองจาก simulated case เดียว Crystal Clear และเปรียบเทียบกับ model-produced reference

มีความขัดแย้งใน author manuscript: §4.1 กล่าวถึง manual verification แต่ §4.5 ระบุชัดว่าไม่ได้ manual validation/correction ของ ground truth จึงไม่รับรองว่า reference นี้เป็น independent human gold ผู้ประเมินบางส่วนตรวจ model outputs เป็นอีกขั้นหนึ่ง [author manuscript pp.3–6](https://raw.githubusercontent.com/NetherlandsForensicInstitute/local-llm-chat-report-benchmark/main/Paper.pdf)

บทเรียนต่อ CyberCase: จุดที่อธิบายเพิ่มได้คือ claim object และ IDs ที่แชร์ระหว่างมุมมอง พร้อมสถานะ/provenance ที่ backend ตรวจและเก็บ; จุดที่ต้องพิสูจน์คือ traceability และ coverage บนหลาย cases ที่มี gold labels ไม่สร้าง gold จากคำตอบโมเดลเดียว

### 2.7 การศึกษา: เพิ่มเกณฑ์และสัญญาของการตัดสินที่ audit ได้

indexed method p.3 ของ Auditable Evidence Trails แยกสร้าง response-specific subrubric โดย **ห้ามให้คะแนนในขั้นแรก** จาก marking agent ที่ให้คะแนนพร้อม label/max/mark/source/rationale/flags orchestrator ตรวจ source presence, score bounds และ incomplete-response flags รวม deterministic tests ได้ และ rubric author ใช้ traces ตรวจและปรับ calibration

งานนี้ระบุว่าการตรวจเชิงกลไม่รับรอง semantic entailment; หลักฐานอาจเป็น code line/notebook output/test result ไม่จำกัด quote prose ความสัมพันธ์กับ AfG และ acceptance ยัง UNCONFIRMED เพราะอ่านเต็มฉบับไม่ได้ [indexed PDF ต้นฉบับ](https://openreview.net/pdf/18fca98950e6d2957a20e706f0480ddb67b588a4.pdf)

บทเรียนต่อ CyberCase: การแยกขั้นที่ “อ่าน/จัด representation” ออกจากขั้นที่ “ตัดสิน” มี prior ใกล้เคียง การอธิบาย ownership ของแต่ละขั้นและข้อผิดพลาดที่ตรวจพบจึงสำคัญกว่าจำนวน agents/calls

### 2.8 AgentGEO: เพิ่ม optimizer รอบ engine เดิม

Appendix E.5 มี attribution-first engine ชัดเจน: เลือก sentence/chunk indices → thematic clustering → cluster-wise attributed generation ส่วน contribution ใหม่คือแก้หน้าเว็บที่ไม่ถูก cite: วิเคราะห์ fetching/parsing/relevance/content failures → เลือก repair tool → retest → รวม edits ข้าม queries

MIMIQ ใช้ 204 webpages และ 12,240 queries แยก training/held-out queries; Table 2 ใน AfG engine citation rate 60.20 → 70.00% เทียบ vanilla **นี่คือ visibility ของหน้าเว็บ** ไม่ใช่ความจริงหรือ semantic support ของข้อสรุป ค่า faithfulness ในงานวัดการรักษาเนื้อหาหน้าเว็บหลัง edit; ไม่ใช่ CyberCase traceability metric [ต้นฉบับ §§3–6, Appendix E.5](https://arxiv.org/pdf/2603.09296)

บทเรียนต่อ CyberCase: ระบุให้ชัดว่ากำลังเปลี่ยน generator, intermediate representation, verifier หรือองค์ประกอบรอบระบบ ไม่รวมทุก improvement ไว้ใต้ชื่อ AfG

## 3. งานต่อยอดเชิงวิธี: สิ่งที่มีมากกว่า domain prompt

| งาน | สิ่งที่เพิ่ม | สิ่งที่หลักฐานยังไม่ยืนยัน |
|---|---|---|
| [Generation Programs](https://arxiv.org/abs/2506.14580) | executable operation trees; extract/paraphrase/compress/fuse พร้อม instructions; execution traces; entailment-guided repair เฉพาะ module | main baseline เป็น ALCE จึงไม่ใช่ผลชนะ AfG โดยตรง; program trace ยังไม่รับรอง outputs ของ neural modules |
| [FRONT](https://aclanthology.org/2024.findings-acl.838/) | synthetic attributable data + Grounding Guided Generation + consistency-aware DPO | ใกล้ quote-first paradigm แต่ไม่พบ direct AfG lineage ใน PDF; fine-tuning อย่างเดียวไม่ใช่ความต่างเพราะ AfG มีอยู่แล้ว |
| [CiteLab](https://aclanthology.org/2025.acl-demo.47/) | นำ AfG มาประกอบใน modular workflow framework; attribution diagnostics หลาย granularities; human-LLM workflow modification | demo ที่ปรับดีขึ้นเริ่มจาก self-RAG; ไม่มีผลที่แยก causal benefit ของ UI หรือ domain-specific AfG adaptation |

Generation Programs น่าสนใจสำหรับคำอธิบาย “เราเปลี่ยน representation อย่างไร”: เริ่มจาก sentence clusters แล้วเพิ่ม **ชนิด operation, instructions และ executable edges** ทำให้ใช้ trace ตรวจและซ่อมเฉพาะจุดได้ การประเมิน module-level repair ใน PDF p.8 Table 3 มีผลต่อ attribution F1 ขณะที่ task correctness ต้องพิจารณาแยก ไม่ควรยืมคำว่า contributive attribution มารับรองว่าการ reconstructed trace เป็นประวัติ computation จริงของ arbitrary prior answer

## 4. หลักร่วมที่เห็นจากหลายโดเมน

ตารางต่อไปนี้เป็น **การสังเคราะห์ของผู้ตรวจ** จากงานข้างต้น ไม่ใช่ taxonomy ที่ผู้เขียนงาน AfG เสนอไว้

| ชั้นที่เปลี่ยน | ตัวอย่างจากงานอื่น | คำถามที่ CyberCase ต้องตอบ |
|---|---|---|
| Task definition | legal requirements; rubric criteria; financial arithmetic | “ภาพรวมสำนวนที่ดี” ต้องแสดง facts/uncertainty/views ใด และวัดสำเร็จอย่างไร |
| Evidence unit | quote/table; page/block; TraceID record; test result | claim เก็บ source evidence และ locator อย่างไร; แยกข้อความรายงานกับ inference อย่างไร |
| Intermediate representation | requirement dependencies; graph triples; executable program; subrubric | claims/parties/timeline/impacts ใช้ IDs เดียวกันแล้วลดการหลุด/ขัดแย้งได้จริงหรือไม่ |
| Rules and verification | table relocation; score bounds; local entailment checks | rule แต่ละตัวพิสูจน์ source occurrence, reference integrity หรือ semantic support ระดับใด |
| Downstream output | legal flag; score; scientific/medical answer; forensic report | reading สร้างอะไร judgement เพิ่มอะไรและแก้ข้อมูล reading ได้หรือไม่ |
| Evaluation | human assistance; time-to-verify; visual support; role/time labels; OOD | baseline อยู่บน case/input/model/decoding เดียวกันหรือไม่; วัด coverage พร้อม traceability/time/cost หรือไม่ |

## 5. CyberCase: อธิบายความเปลี่ยนแปลงให้ตรงกับโค้ด

### 5.1 Evidence ยังเป็น quote; claim เป็นหน่วยข้อมูลกลางเพิ่มเข้ามา

ควรพูดว่า **เพิ่ม case claim layer ครอบ source evidence** ไม่ใช่เปลี่ยน quote ให้กลายเป็น truth

| AfG ต้นฉบับ | CyberCase ที่ตรวจใน checkout นี้ |
|---|---|
| source spans ที่จะใช้สร้างประโยค | claim text + type/status + supporting/contradicting sources/citations |
| ordered span clusters สำหรับ sentence plan | claims และ case views ที่เชื่อมผ่าน claim IDs |
| fused attributed prose | reading-owned parties/timeline/impacts และ judgement-owned summary/gaps/MITRE associations |
| ตรวจ span copying และวัด attribution | backend source-occurrence/reference binding; ประเมิน traceability และ annotated-fact coverage ตาม protocol ของโครงการ |

หลักฐานโค้ด: [CaseClaimFields](<F:/Cybercase Framework/backend/app/trace/claims.py:169>) มี `claim_id`, `claim_type`, `text`, `epistemic_status`, source IDs; provider citations เก็บ `exact_quote`; [case views](<F:/Cybercase Framework/backend/app/trace/trace.py:22>) ใช้ `claim_ids`; [stage contracts](<F:/Cybercase Framework/backend/app/trace/trace.py:168>) แยก reading จาก judgement

### 5.2 สถานะมีความหมายต่อการเขียนภาพรวม แต่ไม่ได้ทำ semantic verification เอง

`claim_type` แยก `reported`, `analytical_inference`, `unknown`; `epistemic_status` มี `reported`, `suspected`, `contradicted`, `not_established`, `unknown`, `not_confirmed` การเก็บ supporting/contradicting sources เปิดทางให้ synthesis ไม่กลบข้อมูลที่ขัดแย้งกัน แต่ enum ไม่รับรองว่าโมเดลเลือกสถานะถูกต้อง

ปัจจุบัน [confirmed_status](<F:/Cybercase Framework/backend/app/trace/bind.py:337>) เปลี่ยนเฉพาะ reported claim ที่ไม่มี verified supporting quote ให้เป็น `not_confirmed` ไม่ใช่ตัวตัดสินว่าผู้พูดจริงหรือไม่ หรือ source นั้น entails ข้อความ claim จริงหรือไม่

ตัวอย่างสมมติ: เอกสารหนึ่งระบุยอดความเสียหาย อีกเอกสารระบุยอดไม่ตรงกัน ระบบต้องเก็บว่าใครรายงานอะไรและอ้างจากที่ใด แล้วให้ timeline/impact/summary อธิบายข้อแตกต่างโดยอ้าง claim ที่เกี่ยวข้อง การพบข้อความตัวเลขทั้งสองใน sources ยังไม่พอพิสูจน์ว่าเป็นธุรกรรมเดียวกัน หรือเลือกค่าหนึ่งเป็นข้อเท็จจริงได้ ตัวอย่างนี้อธิบายเป้าหมายของ representation; ไม่ใช่ผลทดลองว่าระบบทำได้เสมอ

### 5.3 Reading และ judgement เป็นสัญญาของข้อมูลคนละส่วน

โค้ด [write_trace](<F:/Cybercase Framework/backend/app/analysis/write.py:35>) เรียก reading → checked reading/bound claims → judgement Reading เห็น sources และ answered follow-up context ส่วน judgement เห็น checked reading, follow-up context และ optional technical context; `case_sources` ไม่อยู่ใน judgement request ปัจจุบัน

[joined_trace](<F:/Cybercase Framework/backend/app/analysis/write.py:178>) ประกอบผลโดยคง reading-owned fields เป้าหมายนี้ใกล้กับการศึกษาในแง่การแยก interpretation จาก judgement และใกล้ Dehing ในแง่ evidence analysis ก่อน report synthesis ความต่างที่ต้องชี้คือ **data contract ของ case claim/status/shared references และข้อผิดพลาดที่ตรวจ/ประเมินได้** ไม่ใช่เพียงเรียกโมเดลสองครั้ง

## 6. Contribution ต้องยืนบนผลชนิดใด

### 6.1 Traceability และ coverage ตอบคำถามต่างกัน

- **Traceability:** ข้อความ claim ที่ระบบนำเสนอชี้กลับไปข้อความใน source ที่มีอยู่จริงได้หรือไม่ source ID/quote/page เป็นของสำนวนนี้หรือไม่
- **Annotated-fact coverage:** ข้อมูลที่ผู้ annotator ระบุว่าสำคัญปรากฏใน output ตามเกณฑ์ที่กำหนดหรือไม่ ต้องนับข้อที่ตกหล่นด้วย ไม่ใช้เฉพาะ claims ที่โมเดลเลือกมาแล้ว
- **Semantic support:** cited source สนับสนุน claim จริงหรือไม่ ใครเป็นผู้กระทำ/ผู้รับ เหตุการณ์ไหนเกิดเมื่อไร เป็นคำถามเพิ่มที่ source occurrence และ lexical coverage ไม่ตอบ

M1 ใน [PROVENANCE](<F:/Cybercase Framework/research/analysis_baseline/PROVENANCE.md:42>) นับ reported หลัง binding หารด้วย reported + claims ที่ถูก demote เป็น not_confirmed และ pooled เฉพาะ completed cases จึงไม่ใช่ recall ของข้อมูลทุกอย่างในคดี หากระบบสร้าง claims น้อยลง คะแนนนี้ยังดูสูงได้ ต้องอ่านควบคู่ coverage และ completion

[M4b](<F:/Cybercase Framework/research/analysis_baseline/PROVENANCE.md:184>) ต้องมี quote overlap กับ gold span และ lexical mention ของ gold item **ภายใน claim เดียวกัน** ทำให้เข้มกว่าใช้ citation position อย่างเดียว แต่ยังไม่ตรวจ event-role/time binding หรือ semantic entailment อย่างเต็มรูปแบบ

[QASemConsistency, TACL 2026](https://aclanthology.org/2026.tacl-1.6/) แสดงว่าชื่อ entity ที่อยู่ใน source กับ relation ที่ถูกต้องเป็นคนละเรื่อง โดยแตก output เป็น predicate-argument QA assertions และตรวจ supported/unsupported ทีละ relation งานนี้เป็น evaluator ไม่ใช่ AfG generator ใช้เพื่ออธิบายขอบเขต metrics ของ CyberCase; ไม่จำเป็นต้องเพิ่ม evaluator ใหม่ในงานรอบนี้

### 6.2 ข้อสรุปที่ผลทดลองแบบใดรองรับ

| ผลที่มี | ข้ออ้างที่รองรับ | ข้ออ้างที่ยังไม่รองรับ |
|---|---|---|
| Same cases/model/decoding: one-call vs reading-then-judgement | ผลของ workflow ทั้งชุดภายใต้ protocol นั้น | representation มี causal effect แยกจาก extra call/tokens |
| สร้าง claims สถานะครบพร้อม citations | feasibility ของ contract และ source binding | ถูกต้องเชิงเหตุการณ์/กฎหมาย/บทบาท |
| traceability สูงและ coverage ไม่ลด | workflow รักษาข้อมูลที่วัดตาม operational definitions | source truth หรือความครบถ้วนทุก domain |
| annotated corpus หลาย cases | evidence ของ task performance ใน corpus นั้น | general-case superiority ข้ามโดเมนที่ไม่ได้ทดสอบ |
| human verification/usability study | user effort หรือ task performance ที่วัดตรง | objective factual accuracy หากผู้ใช้เพียงให้คะแนนความชอบ |

ถ้าจะอ้างว่า **case representation เอง** ทำให้ดีขึ้น ต้องมี controls ที่คุม model calls/compute และปรับเฉพาะ representation ตามสมมติฐาน เช่น generic evidence-selection pipeline เทียบกับ typed case claims ภายใต้ budget เดียวกัน หากผลปัจจุบันเป็น one-call vs two-call ให้รายงานว่าเป็น **workflow-level comparison** การออกแบบ controls นี้เป็นข้อเสนอสำหรับตีความ/เขียน ไม่ได้เลือกหรือรันการทดลองใหม่

งานที่ใกล้สุดสำหรับการวางตำแหน่งคือ AfG (generation principle), Default Assistant (domain decision workflow), Dehing (case evidence → report) และ Auditable Evidence Trails (separate contracts + audit rules; partial access) ไม่มีหลักฐานจากการค้นนี้ว่าชุดรวมของ CyberCase เป็น ontology หรือ attribution algorithm ที่ใหม่เป็นครั้งแรก และยังไม่ได้ benchmark ชนะระบบเหล่านี้

## 7. ข้อความสำหรับใช้ในงานเขียน

> งานนี้ศึกษาการปรับกระบวนการ attribution-first generation สำหรับการวิเคราะห์สำนวน โดยเพิ่ม representation ของ claims ที่เก็บประเภท สถานะ และการเชื่อมกลับไปยังข้อความหลักฐาน แล้วใช้ claims ร่วมกันในการจัดข้อมูลผู้เกี่ยวข้อง ลำดับเหตุการณ์ และผลกระทบ กระบวนการแยกการอ่านหลักฐาน การตรวจการอ้างอิง และการสังเคราะห์ภาพรวมผ่านสัญญาข้อมูลที่กำหนดไว้ การประเมินมุ่งตรวจว่าการออกแบบดังกล่าวรักษาความสามารถในการย้อนตรวจและความครอบคลุมข้อมูลที่มี annotation ได้เพียงใด ภายใต้เงื่อนไขเปรียบเทียบที่ระบุชัด

ข้อความนี้เป็น **proposed contribution framing** จากหลักฐานโค้ดและ prior work ต้องเติมตัวเลขตาม experimental snapshot ที่ตรงกับ implementation/protocol และใช้ชื่อ metrics ตามนิยามจริง การรวม case views เป็นหลักฐานของระบบที่สร้างได้; claim ว่าดีกว่า baseline ต้องมาจากผลทดลอง

## แฟ้มหลักฐานและการใช้ต่อ

- [comparison_matrix.csv](<F:/Cybercase Framework/docs/research/attribute-first-domain-survey-2026-10-04/comparison_matrix.csv>): domain, relationship, representation, additions, evaluation, pages และข้อจำกัด สำหรับเปิดใน Excel
- [comparison_matrix.json](<F:/Cybercase Framework/docs/research/attribute-first-domain-survey-2026-10-04/comparison_matrix.json>): ข้อมูลเดียวกันพร้อม source/access/hash
- [citation_requests.json](<F:/Cybercase Framework/docs/research/attribute-first-domain-survey-2026-10-04/citation_requests.json>) และ [citation_lock.json](<F:/Cybercase Framework/docs/research/attribute-first-domain-survey-2026-10-04/citation_lock.json>): primary metadata และ claim-support record
- [download_receipts.json](<F:/Cybercase Framework/docs/research/attribute-first-domain-survey-2026-10-04/download_receipts.json>): URL ที่ขอ/ได้รับ, byte count, PDF pages, SHA-256 และ explicit errors
- `literature/papers/`, `literature/text/`, `literature/previews/`: downloaded PDFs, page-labelled extraction และ visual spot checks; ignored local research cache

ไม่ได้แก้ application, เรียก inference, rerun experiments หรือเปลี่ยน thesis scope ในงานนี้
