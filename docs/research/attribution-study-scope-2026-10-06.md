# Attribution classifier study: scope lock

2026-10-06 — ขอบเขตการทดลองที่เสนอจากการอภิปรายปัจจุบัน ยังไม่มีการแปลข้อมูล ฝึกโมเดล รัน benchmark หรือแก้ application ในรอบนี้

## จุดที่ล็อก

แกนวิจัยคือ **Claim–Citation Attribution Classification** ภายในระบบช่วยอ่านสำนวนคดี CyberCase ซึ่งยังมี LLM Analysis, Follow-up และ Report Generation เป็นสาม modules เดิม

คำถามหลัก: เมื่อ LLM สร้าง claim และอ้าง evidence ประกอบ evidence ที่อ้างรองรับเนื้อหาของ claim ครบถ้วนหรือไม่?

`(claim, cited_evidence_bundle) -> attributable | not_attributable`

- หน่วยประเมินใช้ claim ของ AttributionBench ตามเดิม แม้บาง claim มีหลายประโยค
- Evidence คือ references ที่มากับ claim; concat ตามลำดับเดิม ไม่ค้น source เพิ่มระหว่าง classification
- `not_attributable` รวมการรองรับไม่ครบ ไม่มีข้อมูลพอ และความขัดแย้ง; ไม่อ้างว่าจำแนกสามกรณีนี้ได้จาก binary gold
- ผลตรวจเป็นความสัมพันธ์กับ evidence ที่ป้อน ไม่ยืนยันความจริงของเหตุการณ์หรือยกระดับ epistemic status

## Research questions

- **RQ1:** วิธีตรวจ attribution แบบ pretrained multilingual NLI, multilingual encoder ที่ fine-tune เฉพาะ task และ LLM zero-shot ให้ความแม่นยำและต้นทุนต่างกันอย่างไรบน AttributionBench?
- **RQ2:** เมื่อใช้ verifier ที่ตรึงไว้กับ test units เดียวกันในภาษาอังกฤษและภาษาไทยที่แปลด้วย Google Translate คะแนนและรูปแบบข้อผิดพลาดเปลี่ยนอย่างไร?

Working title: **Comparing Attribution Verifiers for LLM-Generated Claims in English and Machine-Translated Thai**. CyberCase เป็น application context; title นี้ไม่อ้างว่า test set เป็นสำนวนคดีไทยจริง

## Dataset และเงื่อนไขภาษา

ใช้ AttributionBench `subset_balanced` เป็น benchmark หลักเพียงชุดเดียว ตัวเลขอ้างอิงจาก published Table 1:

| Split | English | Thai | การใช้ |
|---|---:|---:|---|
| Train | 13,322 | ไม่มีใน primary condition | Fine-tune วิธี B |
| Dev | 1,198 | ไม่มีใน primary condition | เลือก checkpoint, threshold และ settings |
| ID test | 1,610 | แปล 1,610 units เดียวกัน | Main paired evaluation |
| OOD test | 1,686 | แปล 1,686 units เดียวกัน | Main paired evaluation |

Thai condition เป็น cross-lingual evaluation โดยใช้ English development เท่านั้น หากเพิ่ม translated train หรือ Thai development จะเป็นอีก experimental condition และต้องบันทึกการเปลี่ยน scope

## Methods ที่เสนอให้ตรึงเป็นสามวิธี

| Method | วิธี | สิ่งที่ควบคุม |
|---|---|---|
| A | Pretrained multilingual NLI; แปลง entailment score/decision เป็น binary attribution | เลือกกติกา/threshold บน EN dev แล้ว freeze |
| B | Multilingual encoder backbone เดียวกับ A แต่ fine-tune บน EN AttributionBench train สำหรับ binary attribution | Same backbone family; เลือก checkpoint ด้วย EN dev |
| C | LLM zero-shot attribution judge | Claim/evidence เดียวกัน, prompt เดียวกันใน EN/TH, output labels และ retry budget คงที่ |

Local baseline A รันแล้วเมื่อ 2026-10-06 ตามคำสั่งผู้ใช้: `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` @ `b5113eb38ab63efdd7f280f8c144ea8b13f978ce`, fp32 บน GTX1650; claim เป็น hypothesis และ references ที่ concat ตามลำดับเป็น premise. Native context512 ตัดเฉพาะ premise; เลือก threshold `p(entailment) >= 0.15` จาก EN dev และ freeze ก่อน ID/OOD. [ผลและ protocol](../../research/attribution_benchmark/runs/nli_en_20261006T002759Z/report.md) เก็บ primary dev-selected decision และ descriptive argmax reference แยกกัน; ไม่เปลี่ยน primary ตามผล test

Revision/training recipe/resources ของ B, LLM identity/settings ของ C และ Google Translate execution budget ยัง UNCONFIRMED. รอบ local baseline ไม่แปลไทย ไม่ fine-tune และไม่แก้ application

## Google Translate preparation

1. แปล `claim` และทุกข้อความใน `references[]` EN -> TH; รักษา id, source subset, reference order, citation markers และ original gold label
2. ไม่ส่ง gold label ให้ translator และไม่สั่งแก้ claim ให้สอดคล้องกับ evidence; รักษาตัวเลข ชื่อ บทบาท คำปฏิเสธ และ qualifiers ตามต้นฉบับ
3. ใช้ Google Translate workflow เดียว บันทึก service/API configuration, วันที่แปล และ provenance; เก็บ raw output และ hash ของไฟล์ frozen ที่ทุก method ใช้ร่วมกัน
4. เสนอ bilingual audit 200 pairs: ID100/OOD100 กระจายทั้งสอง labels และ source subsets; ตรวจความหมายและ label preservation ก่อนดู verifier predictions
5. เก็บ raw translation และบันทึกการแก้ทุกจุด หากมี post-editing ให้ระบุว่าชุดประเมินผ่านการแก้คำแปล ไม่เรียกว่า raw MT ทั้งหมด; การตัด units ต้องรายงานและใช้ EN/TH paired subset เดียวกัน

การ audit เป็นการตรวจ inherited labels ไม่ใช่การสร้าง native Thai case benchmark ใหม่ ทั้งโมเดลภาษาและ translation artifacts มีผลต่อ EN–TH gap

## Metrics และการเปรียบเทียบ

Macro-F1 เป็น headline สำหรับเปรียบเทียบ task เดิม; รายงาน diagnostics ที่บอกทิศทางความผิดพลาด, paired language effects และต้นทุนประกอบ ไม่ใช้จำนวน metrics เป็นตัวแทนความแข็งแรงของการทดลอง AttributionBench Table2/3 รายงาน Macro-F1 พร้อม FP/FN percentages อยู่แล้ว

| ระดับ | สิ่งที่ต้องรายงาน | คำถามที่ตอบ |
|---|---|---|
| Primary | Macro-F1 ราย source subset พร้อม ID-average และ OOD-average ของ subset scores | วิธีใดจำแนกทั้งสอง classes ได้ดีกว่า และเทียบรูปแบบ paper ได้อย่างไร |
| Required diagnostics | Precision/recall/F1 และ gold support counts ของทั้งสอง classes; confusion counts | คะแนนรวมซ่อนความผิดพลาดของ class ใด |
| Required diagnostics | False acceptance และ false warning rates พร้อม numerator/denominator | ปล่อย claim ที่ evidence รองรับไม่ครบผ่าน หรือเตือน claim ที่รองรับครบมากเท่าไร |
| Transfer | EN/TH scores, paired `Macro-F1_TH - Macro-F1_EN` พร้อม 95% CI | พฤติกรรมเปลี่ยนบน test units ที่แปลเป็นไทยอย่างไร |
| Practical | Valid-label coverage/failure counts, end-to-end latency p50/p95, usage/cost ต่อ 1,000 attempted units | วิธีใดใช้งานได้ภายใต้เวลาและต้นทุนที่รายงาน |
| Secondary | Accuracy | สัดส่วน test units ที่ตอบถูกทั้งหมด |

กำหนด `G_N` = จำนวน gold `not_attributable`, `G_A` = จำนวน gold `attributable`, `FA` = gold N/pred A และ `FW` = gold A/pred N. รายงาน false acceptance rate = `FA/G_N` และ false warning rate = `FW/G_A`. หากรายงาน FP/FN เป็นสัดส่วนของ test ทั้งชุดเพื่อประกอบตาราง benchmark ให้แสดง `FA/(G_N+G_A)` และ `FW/(G_N+G_A)` แยกชื่อให้ชัด; ไม่ปน denominator กับ class-conditional rates หรือ precision ซึ่งมี denominator เป็น predicted class

- Primary และ Accuracy ใช้ทุก attempted unit หลัง retry budget ที่ตรึงไว้: output ที่ parse ไม่ได้หรือ execution ล้มเหลวเป็น `ERROR` bookkeeping prediction และนับ FN ของ gold class; Macro-F1 เฉลี่ยเฉพาะสอง gold classes ไม่เพิ่ม semantic class ที่สาม ไม่แปลง failure เป็น `not_attributable`. Confusion report มีคอลัมน์ ERROR พร้อม failure counts ราย gold class; valid-only scores เป็น supplementary และระบุ denominator
- ใช้ question/response-cluster paired bootstrap ภายใน source subsets สำหรับ 95% CI ของ Macro-F1 และ score differences; resample clusters เดียวกันข้าม methods และ EN/TH แล้วคำนวณ ID/OOD averages ใหม่ทุก replicate. กำหนด cluster keys และ procedure ก่อน predictions; CI นี้ไม่ครอบคลุม training-seed randomness
- Report EN-correct/TH-wrong และ EN-wrong/TH-correct พร้อม error cases ด้านจำนวน, entities/roles, negation และ qualifiers; แยก translation/label-preservation problems จาก verifier errors เมื่อ bilingual audit ระบุได้
- Latency/usage/cost รวมทุก retry และ failure; ระบุ model revision, hardware/API, batch/concurrency และ context limits. รายงาน local compute กับ API charges ตามจริง ไม่สมมติราคาเท่ากัน
- Balanced Accuracy เป็นค่าเฉลี่ย recall ของ classes; หาก gold ทั้งสอง classes มีจำนวนเท่ากันพอดีจะเท่ากับ Accuracy จึงไม่ต้องเป็น headline ซ้ำ. ใช้เพิ่มเมื่อ reporting subset มี gold distribution ไม่สมดุลจริง
- Optional ranking analysis: AUROC และ Average Precision (AP) ใช้ continuous model scores ที่ระบุวิธีสร้างก่อน test โดยให้ `not_attributable` เป็น positive สำหรับ alert ranking. NLI/fine-tuned models ที่มี scores ทำได้; LLM ที่ให้เพียง hard verdict รายงาน N/A สำหรับ ranking comparison ไม่เปลี่ยนคะแนน confidence ที่ LLM เขียนเองเป็น calibrated probability. AP ใช้นิยาม weighted precision-recall summary ไม่เรียกสลับกับ trapezoidal PR-AUC
- ใช้ claim/reference inputs ชุดเดียวกันในแต่ละภาษา; ระบุ truncation/information loss. ทำ preprocessing และเลือก checkpoint/threshold/settings บน EN dev ก่อน test; ไม่เลือกจาก Thai test และไม่ใช้ verifier ตัวที่ทดสอบเป็น gold judge

## Application boundary

Integration target: `LLM reading -> claims/quotes -> Binder -> attribution verifier -> judgement/summary -> Report`

- Verifier เป็น subcomponent ภายใน LLM Analysis; Follow-up และ Report Generation คงความรับผิดชอบเดิม
- Binder ตรวจ source occurrence/localization; verifier ตรวจ semantic support ของ cited evidence
- Application evidence มาจาก verified citations/source snapshot พร้อม provenance; final input unit/context policy ต้องกำหนดก่อน implementation
- Binding failure และ execution failure เก็บเป็นสถานะแยกจาก binary semantic verdict
- เก็บ verdict พร้อม evidence ที่ใช้ตรวจแยกจาก epistemic status; เสนอให้เริ่มด้วย warning/metadata และ Report reuse โดยยังไม่มี hard-remove/repair policy
- Benchmark scores วัด verifier; หากอ้างว่า synthesis/report ดีขึ้น ต้องมี independent output evaluation แยก เพราะ synthesis ยังอาจสร้าง claim ใหม่

## Scope boundary และข้ออ้าง

Primary study มี attribution task เดียว, benchmark เดียว, methods สามวิธี และ EN/TH test conditions สองภาษา Google Translate เป็นขั้นเตรียมข้อมูล ไม่มีการเทียบ MT engines

WiCE/ALCE เป็น related work และ supporting protocols; ไม่เพิ่มเป็น benchmark หลักใน scope นี้ Event coreference, temporal classification, salience, new follow-up classifier และ RAG/MITRE variants ไม่ใช่ตัวแปรทดลองของงานนี้ ผลทดลองเดิมใน repo ยังคงเป็นหลักฐานระบบที่มีอยู่

ข้ออ้างที่วัดได้คือ comparative attribution performance และ paired robustness บน machine-translated Thai. Native Thai case-domain generalization, source truth และ downstream summary/report improvement ยังไม่ถูกพิสูจน์จาก benchmark นี้

## Primary sources

- [AttributionBench, Findings ACL 2024](https://aclanthology.org/2024.findings-acl.886.pdf): section2.1/3, Table1/2/3 — task, optional input fields, official balanced splits and evaluation
- [Official AttributionBench dataset](https://huggingface.co/datasets/osunlp/AttributionBench): schema, English language and subset_balanced configuration
- [SeaExam and SeaBench, Findings NAACL 2025](https://aclanthology.org/2025.findings-naacl.341.pdf): AppendixA.3 — Google Translate API for English-to-Thai MMLU/MT-bench; human comparison for translated MT-bench
- [XNLI 2.0, arXiv preprint 2023](https://arxiv.org/abs/2301.06527): Google Translate for multilingual MNLI/XNLI data; ไม่อ้างเป็น peer-reviewed task-matched attribution benchmark
- [XNLI, EMNLP 2018](https://aclanthology.org/D18-1269.pdf): sections3.1-3.2 — human-translated evaluation, inherited labels and label-preservation checks
- [Translation Artifacts, EMNLP 2020](https://aclanthology.org/2020.emnlp-main.618.pdf): sections4.4-4.5/6 — translation changes model behavior and confounds language-only interpretation
- [scikit-learn F1](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.f1_score.html): per-class/macro averaging and explicit label selection for failure bookkeeping
- [scikit-learn Balanced Accuracy](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.balanced_accuracy_score.html): mean class recall; equality with Accuracy on exactly balanced gold follows from this definition
- [scikit-learn ROC AUC](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html) and [Average Precision](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html): ranking metrics use probability/decision scores; AP differs from trapezoidal PR-AUC
