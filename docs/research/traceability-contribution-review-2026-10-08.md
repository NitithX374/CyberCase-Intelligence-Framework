# Traceability: evaluator contribution versus generation-workflow contribution

Checked: 2026-10-08, Asia/Taipei. Scope: source-to-output attribution in generated summaries/reports and its relevance to CyberCase. This is a focused literature review, not a systematic census of the field.

## Answer

มีทั้งงานที่เสนอ metric/checker และงานที่เสนอ generation workflow จริง งานกลุ่มหลังใช้ consistency/attribution เป็นหนึ่งในตัววัดผลร่วมกับความครบถ้วน คุณภาพข้อความ และต้นทุนการตรวจสอบ จึงไม่จำเป็นต้องสร้าง consistency metric ใหม่เพื่อทำงานวิจัยเกี่ยวกับ traceable summarization

การมีหลายขั้นตอนยังไม่บอกชนิด contribution: AIS มี annotation pipeline และ FIZZ มี evaluation pipeline แต่ผลผลิตหลักของสองงานนี้คือการประเมิน ส่วน Attribute First, then Generate และ RARR เปลี่ยนวิธีสร้างหรือแก้ข้อความ งาน SmartBook และ Dehing et al. ศึกษา workflow ของผู้ใช้และรายงานในโดเมนเฉพาะ

ชุดนี้มี 12 งานที่เกี่ยวข้องโดยตรงและ 1 งานเปรียบเทียบแนวคิด verify-then-generate จาก tutoring จัดตาม contribution หลักได้เป็น evaluator/checker 5 งาน, benchmark/data 3 งาน, generation/report workflow 4 งาน และ analogy 1 งาน หมวดทับซ้อนกันได้ และจำนวนนี้ใช้สรุปว่า “งานส่วนใหญ่ในวงการ” เป็นประเภทใดไม่ได้ เพราะคัดงานที่ใกล้คำถามและระบบปัจจุบัน

## Search and reading boundary

ค้นสามรอบ: (1) attribution/consistency definitions and evaluators, (2) attributed generation and report workflows, (3) วิธีทดลองและข้อจำกัดจาก method/evaluation sections ใช้ ACL Anthology, arXiv, DOI metadata และ repository ของผู้เขียน ไม่รวมงาน data lineage ของ training corpus หรือ reasoning transparency ที่ไม่เชื่อม output กลับไปยัง supporting source

ตรวจ DOI metadata ผ่าน Crossref 12 งาน และ arXiv metadata 1 งาน พร้อมอ่าน abstract และส่วน method/evaluation ที่รองรับข้อความด้านล่าง การตรวจ metadata ไม่ใช่การพิสูจน์ว่าผลทดลองของ paper ถูกต้อง จึงแยก bibliography verification ออกจากการตีความ contribution

## Properties that must be separated

| Property | Question | How to measure |
|---|---|---|
| Addressability / traceability | Pointer กลับไปหา Source ต้นฉบับได้จริงไหม? | Deterministic ID resolution, offset/text equality, reference closure |
| Source-relative semantic support | Source ที่อ้างรองรับ factual statement ครบไหม? | Human support labels; validated semantic evaluator |
| Coverage | ข้อมูลที่จำเป็นและรองรับได้ตกหล่นแค่ไหน? | Independent relevant-fact set or explicit reference coverage protocol |
| Verification utility | ผู้ใช้ตรวจข้อค้นพบได้เร็ว/แม่นขึ้นไหม? | Timed human study, correction accuracy, editing effort |
| External factual truth | Source เองถูกต้องตามโลกจริงไหม? | Separate corroboration; source support alone cannot establish this |

AIS นิยามการ attribution ต่อแหล่งข้อมูลที่ระบุไว้ จึงช่วยแยกความรองรับจาก Source ออกจากความจริงภายนอก [Rashkin et al., 2023](https://aclanthology.org/2023.cl-4.2/). ALCE ตรวจ semantic support ของข้อความกับ cited passages รวมกัน ไม่ใช่แค่มี citation token หรือ ID ที่ parse ได้ [Gao et al., 2023, ALCE](https://aclanthology.org/2023.emnlp-main.398/).

## Paper map

ตารางนี้บอก contribution และวิธีประเมิน ไม่ได้จัดอันดับคะแนนข้าม paper ซึ่งใช้คนละข้อมูลและ metric

| Work / version | Primary contribution | Operational method | Evaluation / boundary |
|---|---|---|---|
| [AIS — Computational Linguistics 2023](https://aclanthology.org/2023.cl-4.2/) | Definition and human evaluation framework | ประเมิน interpretability แล้วประเมิน attribution ต่อ identified sources | Human annotation protocol; ไม่ใช่ generator ใหม่ |
| [SummaC — TACL 2022](https://aclanthology.org/2022.tacl-1.10/) | Consistency detector and benchmark | Sentence-pair NLI แล้ว aggregate เป็น summary score | Gold consistency classification; ไม่ได้ควบคุม generation โดยตัวมันเอง |
| [FActScore — EMNLP 2023](https://aclanthology.org/2023.emnlp-main.741/) | Atomic factual-precision metric and estimator | แยก generated text เป็น atomic facts แล้วตรวจกับ knowledge source | Supported-fact proportion and agreement with human evaluation; knowledge-source setting ต่างจาก Case material |
| [FIZZ — EMNLP 2024](https://aclanthology.org/2024.emnlp-main.3/) | Factual-inconsistency evaluator | Coreference/atomic facts, NLI matching, ขยายบริบท Source ที่ใช้ตรวจ | Annotated inconsistency benchmark; decomposition/context aggregation เป็นส่วนของ evaluator |
| [MiniCheck — EMNLP 2024](https://aclanthology.org/2024.emnlp-main.499/) | Small trained fact-checker, synthetic training data, LLM-AggreFact | ฝึก checker ให้ตรวจ grounded claim รวมการสังเคราะห์ข้ามประโยค | Checker accuracy and inference cost; checker quality ไม่เท่ากับ downstream benefit |
| [ALCE — EMNLP 2023](https://aclanthology.org/2023.emnlp-main.398/) | End-to-end citation-generation benchmark and evaluators | Retrieval → answer with citations; เปรียบเทียบ generation strategies | Fluency, answer correctness, citation precision/recall; benchmark ไม่ใช่ runtime gate โดยอัตโนมัติ |
| [AttributionBench — Findings ACL 2024](https://aclanthology.org/2024.findings-acl.886/) | Attribution-evaluator benchmark | เปรียบเทียบ support classifiers บน labelled attribution examples | Macro-F1 and evaluator comparisons; ไม่ได้ทดสอบผลของ gate ต่อรายงาน |
| [WiCE — EMNLP 2023](https://aclanthology.org/2023.emnlp-main.470/) | Claim/subclaim entailment data and verification method | Wikipedia claims + cited content + minimal supporting sentence annotations | Entailment/evidence labels and claim-decomposition experiments; ไม่มี Case report generator |
| [Attribute First, then Generate — ACL 2024](https://aclanthology.org/2024.acl-long.182/) | Attribution-driven generation method | Select source spans → plan sentences → sequential generation | Output quality, NLI attribution, citation granularity, human checking effort; semantic support ไม่ได้ชนะทุก setting |
| [RARR — ACL 2023](https://aclanthology.org/2023.acl-long.910/) | Post-generation attribution repair | Generate search queries → retrieve → assess agreement → minimally revise | Human attribution/preservation and automatic proxies; สนับสนุนข้อความโดยรักษาเนื้อหาเดิม ไม่ใช่ลบทุกอย่าง |
| [SmartBook — arXiv v3, updated 2024-05-27](https://arxiv.org/html/2303.14337v3) | Analyst-oriented situation-report workflow | News/events → questions → claims → grounded summaries → report interface | Expert/content studies, NLI citation metrics and editing study; cited version is a preprint |
| [Dehing et al. — DFDS 2026](https://doi.org/10.1145/3785318.3785330) | Feasibility/model comparison within forensic report workflow | Per-part chat extraction with Trace IDs → cross-part report synthesis | Entity/role/Trace-ID/timeline/factual/reasoning evaluation; model-generated reference report with human verification |
| [Daheim et al. — EMNLP 2024](https://aclanthology.org/2024.emnlp-main.478/) | Intermediate verification followed by tutor generation | Verify student error description/alignment → generate remediation | Verifier evaluation plus downstream teacher assessment; tutoring analogy, not Case-source attribution evidence |

## What generation/workflow papers actually do

### 1. Select supporting content before generation

Attribute First, then Generate เลือก spans จากหลายเอกสาร จัด spans เป็นกลุ่มสำหรับประโยค แล้วสร้างข้อความจากกลุ่มนั้น วิธีนี้ทำให้ attribution เป็นส่วนหนึ่งของการสร้างข้อความ ไม่ใช่ติด citation ทีหลัง วัดทั้ง ROUGE-L/BERTScore, NLI-based attribution, ความยาว citation, ข้อความที่ไม่มี attribution และเวลาที่คนใช้ตรวจ งานไม่ได้เสนอ NLI ใหม่เพื่อให้ contribution ด้าน generation ใช้งานได้ และผล semantic support ไม่ได้เหนือ baseline ในทุกเงื่อนไข [Paper, method and evaluation sections](https://aclanthology.org/2024.acl-long.182.pdf).

ใน implementation ของ paper มี verbatim span selection/string matching แต่สิ่งที่นำมาใช้กับ CyberCase คือแนวคิดเลือก supporting content ก่อน synthesis ไม่ใช่การเปลี่ยนสัญญา deterministic unit IDs กลับไปเป็น model-generated exact quotes

### 2. Repair attribution after generation

RARR เริ่มจากข้อความที่มีอยู่แล้ว ค้น supporting sources ตรวจ agreement แล้วแก้เฉพาะส่วนที่ต้องแก้ วัด attribution คู่กับ preservation รวมถึงมนุษย์ตรวจทั้งสองมิติ วิธีประเมินแยก automatic NLI proxy ออกจาก human assessment และระบุว่าการเพิ่ม attribution อย่างเดียวอาจทำได้ด้วยการแทนข้อความเดิมทั้งหมด ซึ่งไม่ตอบเป้าหมายการรักษาเนื้อหา [Paper, sections 2–3 and appendices B–C](https://aclanthology.org/2023.acl-long.910.pdf).

### 3. Make a useful report workflow, then measure several outcomes

SmartBook ศึกษาปัญหาของ intelligence analysts สร้าง question-driven claim extraction และรายงานที่เชื่อมไปยัง Source แล้วประเมินความเกี่ยวข้อง คุณภาพ citation และการแก้รายงานโดยผู้เชี่ยวชาญ การทดลองมี direct query-focused summarization เป็น comparison ของขั้น claim extraction ด้วย จึงไม่ได้ขายแค่หน้าจอหรือจำนวน citation [Paper, sections 2–3](https://arxiv.org/html/2303.14337v3).

ตัวอย่างสำคัญ: paper รายงานว่าประโยค 97% มี citation แต่ NLI-estimated citation precision อยู่ที่ 64.7% และ recall 69.2% ตัวเลขใช้คนละนิยามและตัวหาร จึงหักลบกันเพื่อคำนวณ unsupported-fact rate ไม่ได้ แต่แสดงชัดว่าการมี citation กับการได้รับ semantic support ต้องวัดแยก [Section 3.2](https://arxiv.org/html/2303.14337v3).

Dehing et al. อยู่ใกล้ Case reporting มากที่สุดในชุดนี้: แยก chat corpus ตาม context limit ทำ extraction พร้อม Trace IDs แล้วรวมเป็นรายงาน มีทั้ง entity, role, timeline และ source-reference evaluation งานเปรียบเทียบ local models ใน workflow ที่กำหนด ไม่ได้พิสูจน์ causal benefit ของ NLI gate แบบ CyberCase และ reference report สร้างด้วย Gemini ก่อนตรวจโดยมนุษย์ จึงไม่ใช่ independent all-human gold [Author repository and paper](https://github.com/NetherlandsForensicInstitute/local-llm-chat-report-benchmark).

Repository PDF มี DOI/ISBN placeholders; ใช้ DOI record ยืนยัน publication identity แทน footer ใน PDF ไม่ใช้ placeholder เป็น citation [Published record](https://doi.org/10.1145/3785318.3785330).

### 4. Validate intermediate information, then evaluate its effect on generation

Daheim et al. แยก verifier ออกจาก tutor generator แล้วประเมินทั้งคุณภาพ verifier และคำตอบที่เกิดขึ้น downstream การตรวจ reasoning ของนักเรียนต่างจากการตรวจ Case claim ต่อ Source จึงใช้อ้างแนวทางการออกแบบ experiment ได้ แต่ใช้อ้างว่า NLI gate ของ CyberCase ป้องกันข้อมูลคดีผิดไม่ได้ และ verifier error สามารถทำให้คำตอบปลายทางผิดทิศทางได้ [Paper, section 7](https://aclanthology.org/2024.emnlp-main.478.pdf).

## How this positions CyberCase

ข้อเสนอด้าน framing ต่อไปนี้เป็นการตีความจาก literature และ code ปัจจุบัน ไม่ใช่ข้อพิสูจน์ novelty หรือผลทดลองใหม่

**Candidate contribution:** a traceable Case summarization workflow with deterministic source addressing and pre-generation Claim admission, evaluated for unsupported-information propagation, factual retention and verification cost.

Production boundary inspected during this review:

```text
Case → N Sources / follow-up source content
     → addressable source units → Reader → canonical Claims
     → deterministic binding → frozen B1-LR support gate
     → admitted Claims → Views / Judgement → summary with Claim references
```

- Claim เป็น factual primitive และเก็บ original Source provenance; unit resolution เป็น structural check
- Gate ใช้ MPNet filtering, mDeBERTa และ WiCE TRAIN-fitted LR ที่มีอยู่แล้ว ต้องอ้างว่า reuse/integrate/evaluate ไม่ใช่เสนอ NLI model ใหม่
- Judgement ปัจจุบันยังได้รับ supporting/contradicting Source text ที่แนบกับ admitted Claims แม้ metadata ของ Source/unit/document ถูกตัดออกแล้ว จึงยังไม่ใช่ strict Claim-text-only generation
- Claim-ID closure ป้องกันการอ้าง withheld/unknown Claim IDs แต่ไม่พิสูจน์ว่าข้อความทุกประโยคใน summary ได้รับการรองรับ หรือว่าข้อมูลจาก citation context จะไม่ถูกขยายออกมา
- หากไม่มี admitted Claims ระบบ abstain; ตัววัด support ต้องรายงาน coverage/abstention ด้วย

Code pointers: [claim gate](../../backend/app/analysis/claim_gate.py), [analysis orchestration](../../backend/app/analysis/write.py), [Judgement Claim payload](../../backend/app/trace/claims.py). Paths are relative to this document.

### Contribution is the tested mechanism, not the inventory of the application

การมี Reader, NLI, frontend, database และ Docker ครบ ไม่ทำให้เกิด research contribution โดยตัวมันเอง ต้องบอกว่ากลไกใดแก้ปัญหาใด และการทดลองแยกผลของกลไกนั้นได้แค่ไหน สำหรับ CyberCase คำถามที่ตรงที่สุดคือ:

1. Gate ลด unsupported Claims ที่เข้า synthesis และถูกนำไปใช้ downstream แค่ไหน?
2. แลกกับ supported-fact retention, coverage, abstention และ latency เท่าไร?
3. Source links/Claim references ช่วยผู้ใช้ตรวจข้อมูลได้จริงไหม? ข้อนี้ต้องมี human task หากจะกล่าวอ้าง user benefit

ไม่จำเป็นต้อง train model ใหม่หรือสร้าง metric ใหม่ แต่การเรียก workflow ว่า novel ต้องมี related-method comparison ที่ชัด การรีวิวนี้ไม่ได้ตรวจครบทุก method และไม่ได้รันการเปรียบเทียบโดยตรง

## Minimum defensible evaluation, using existing work first

| Layer | Immediate deterministic measurement | Requires independent semantic/task gold |
|---|---|---|
| Source addressing | Resolution/invalid/duplicate rates, exact offset reconstruction, source ownership, unresolved Claims | Source passage actually supports Claim content |
| Claim admission | Counts admitted/withheld/unassessed, verifier calls, timing, abstention | False acceptance/rejection, supported retention, unsupported escape |
| Downstream synthesis | Cited Claim-ID usage and reference closure | Unsupported factual statements in final prose; facts outside the cited Claim text |
| Completeness | Output/admission counts | Relevant supported-fact coverage, including important omissions |
| User traceability | Availability of resolvable Source links | Checking time, correctness, correction effort |

ที่มีอยู่แล้ว: frozen verifier evaluation และ paired No-Gate/B1-LR Judgement replay สามารถใช้เริ่มรายงาน classifier/admission และ cited-ID utilization ได้ ผลเดิมไม่ได้เป็น final-prose semantic audit และไม่ได้วัดประโยชน์ต่อผู้ใช้ ต้องแยกสิ่งที่มีผลแล้วออกจากสิ่งที่ยังไม่พิสูจน์ [Current results and limitations](../../research/attribution_benchmark/B1_RESULTS_2026-10-07.md).

หากจะประเมินผลของ gate ต่อ generator ให้ replay **Reading/Claims เดียวกัน**, ใช้ **Judgement model/prompt/config เดียวกัน**, ต่างกันเฉพาะ admission; รายงาน failed generations และ abstentions อย่างชัดเจน หากจะประเมิน citation-context leakage ให้ถือเป็นอีก ablation ที่ตรึง admission ไว้และเปลี่ยนเฉพาะ attached Source text งานสองแบบตอบคนละคำถาม

Baseline ที่มีเหตุผล: direct summarization เป็น overall workflow comparison; same Claims with No Gate เป็น gate ablation; same admitted Claims with/without attached Source text เป็น context ablation เก็บ coverage/cost ควบคู่ semantic support เพื่อไม่ให้วิธีที่ลบข้อเท็จจริงเกือบทั้งหมดดูเหมือนชนะ

No Gate เป็น internal component ablation ไม่ใช่ published-method baseline หากจะกล่าวอ้าง improvement ต่อวิธีวิจัยเดิม ต้องมี comparator ที่ระบุจาก paper และปรับให้ใช้ข้อมูล/งานเดียวกันอย่างโปร่งใส เช่น attribution-first generation หรือ forensic extraction/synthesis ตามขอบเขตที่เลือก ไม่ถือ current CyberCase implementation เป็นงานต้นฉบับจาก literature และไม่เรียกการนำบางขั้นตอนของ Dehing มาใช้ว่า exact replication

นี่คือข้อเสนอการตีความและการออกแบบ ไม่ได้รัน experiment เพิ่มในรอบนี้ และต้องอนุมัติงบก่อน paid reruns ตามข้อจำกัดของผู้ใช้

## Conclusions and limits

สิ่งที่ literature review นี้รองรับ:

- มีเส้นทาง contribution ทั้ง evaluator/checker, benchmark และ attributed generation/report workflow
- Generation-workflow contribution สามารถใช้ evaluator/model ที่มีอยู่ แต่ต้องวัดผลที่ workflow เปลี่ยนจริง
- Traceability เชิง pointer, semantic support, coverage และ human verification utility เป็นคนละ outcome
- Source support ไม่ใช่ legal correctness หรือ external factual truth

สิ่งที่ยังไม่รองรับ: สัดส่วนว่า “ส่วนใหญ่” ของงานทั้งหมดเป็นประเภทใด, novelty ของ CyberCase, superiority ต่อ methods ที่รีวิว, native Thai/case-domain generalization, final-summary semantic correctness และการลดเวลาตรวจของผู้ใช้

## Verification receipts

- `tmp/traceability-review-20261008/citation_requests.json`: 13 scoped claim-support records and primary identifiers
- `tmp/traceability-review-20261008/citation_lock.json`: fresh Crossref/arXiv metadata records; all 13 verified by the metadata tool
- `tmp/traceability-review-20261008/citation_keys.md`: key-validation fixture; citation-lock check passed
- `tmp/traceability-review-20261008/dehing2026.{pdf,txt}`: inspected author-repository copy; kept in ignored local storage
- No production code, tests, models, datasets or database records changed for this review. No OpenRouter generation or Translation API requests; public paper/metadata retrieval only.
