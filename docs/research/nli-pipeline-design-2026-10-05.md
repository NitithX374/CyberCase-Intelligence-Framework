# Attribution, traceability และ NLI สำหรับ CyberCase

2026-10-05 — ข้อเสนอเพื่อการอภิปรายจาก primary papers และผลทดลองที่บันทึกไว้ ไม่ใช่ผลรันใหม่หรือการอนุมัติ implementation

Code baseline ที่ตรวจ: `5b6c03e14ea3200af0f159f1cfa886eb0ea4bcc2` สคริปต์ NLI อยู่ใน `research/analysis_baseline/`; ไม่พบ runtime NLI verifier ใน `backend/app/` ที่ baseline นี้

## คำตอบหลัก

งานที่ใช้ NLI พัฒนาคุณภาพได้สามระดับ: ฝึกโมเดลให้เหมาะกับงาน, ปรับ premise/hypothesis ที่โมเดลอ่าน, และปรับวิธีรวมคะแนน/ตัดสินใจ การปรับสองระดับหลังเป็นวิธีพัฒนา verification pipeline ได้โดยใช้ NLI checkpoint เดิม

สำหรับ CyberCase ควรเริ่มจากโมเดลคงที่และทดสอบการสร้าง input จากหลักฐานที่ bind แล้ว พร้อมรักษาผู้กล่าว บทบาท และสถานะความไม่แน่นอน ประโยชน์ที่คาดหวังยังต้องทดสอบกับ label ที่ตรงกับ semantic support

## งานเดิมเพิ่มอะไร

| งาน | การปรับ | ระดับที่ปรับ | สิ่งที่นำมาทดสอบได้ |
|---|---|---|---|
| [SummaC, TACL 2022](https://aclanthology.org/2022.tacl-1.10/) | แบ่ง source/summary เป็นหน่วยประโยค แล้วรวมคะแนน NLI; SummaCConv เรียนรู้ชั้น aggregation | input และ aggregation; มี learned aggregation แต่ไม่ใช่การ fine-tune NLI backbone ในวิธีนี้ | เปรียบเทียบ quote ล้วนกับประโยคที่ครอบ quote และ bounded context; เลือก threshold บน validation |
| [FIZZ, EMNLP 2024](https://aclanthology.org/2024.emnlp-main.3/) | แก้ coreference, แตก summary เป็น atomic facts, และขยาย source context เมื่อหลักฐานประโยคเดียวไม่ entail | decomposition และ evidence context | ทดลอง claim ที่มีความหมายเดียว และขยายบริบทอย่างมีขอบเขตจากตำแหน่งอ้างอิง |
| [FactCC, EMNLP 2020](https://aclanthology.org/2020.emnlp-main.750/) | สร้าง training data ด้วย paraphrase, negation, entity/pronoun/number swaps; ฝึก consistency และ span extraction | task-specific training และ explanation | สร้าง challenge set ที่สลับชื่อ ตัวเลข บทบาท หรือปฏิเสธ โดยตรวจว่าการเปลี่ยนทำให้ support หายจริง |
| [VitaminC, NAACL 2021](https://aclanthology.org/2021.naacl-main.52/) | ฝึกด้วย evidence pairs ที่เกือบเหมือนกัน แต่ support claim ต่างกัน จาก Wikipedia revisions และ synthetic revisions | contrastive training | hard negatives ที่ lexical overlap สูง เช่น ตัวเลขมีอยู่ใน source แต่เป็นของคนละ party |
| [AlignScore, ACL 2023](https://aclanthology.org/2023.acl-long.634/) | รวม 15 datasets จาก 7 tasks เพื่อเรียน information alignment; แบ่ง context เป็น chunks และ claim เป็น sentences | training diversity และ input aggregation | ใช้เป็น comparator สำหรับ factual support; ไม่ถือว่าคะแนน alignment เป็นความน่าจะเป็นของความจริง |
| [MiniCheck, EMNLP 2024](https://aclanthology.org/2024.emnlp-main.499/) | สร้าง synthetic training examples ที่ต้องตรวจทุกข้อเท็จจริงใน claim และผสานหลักฐานหลายประโยค | task-specific training ของ verifier ขนาดเล็ก | positive/negative pairs ที่ต่างกันตรง support ของ atomic fact เพียงบางส่วน |

FactCC และ MiniCheck เป็น factual-support verifiers ที่เกี่ยวข้องกับ NLI; ไม่ใช่ทุกตัวคืน entailment/neutral/contradiction สามคลาสเหมือน NLI มาตรฐาน

แหล่ง method ที่อ่านเพิ่มเติม: [SummaC §3](https://aclanthology.org/2022.tacl-1.10.pdf), [FIZZ §3](https://aclanthology.org/2024.emnlp-main.3.pdf), [FactCC §3](https://aclanthology.org/2020.emnlp-main.750.pdf), [AlignScore §3](https://aclanthology.org/2023.acl-long.634.pdf), [MiniCheck preprint v2 §3](https://arxiv.org/html/2404.10774v2)

## ข้อจำกัดในการวาง contribution

[Attribute First, then Generate, ACL 2024](https://aclanthology.org/2024.acl-long.182.pdf) ใช้ AUTOAIS ซึ่งเป็น NLI-based attribution metric อยู่แล้วในส่วน evaluation และเปรียบเทียบโมเดลกับ human judgments ใน Appendix B เช่นเดียวกับ [ALCE, EMNLP 2023 §3.3](https://aclanthology.org/2023.emnlp-main.398.pdf) ที่ใช้ NLI ตรวจ citation quality

ดังนั้นการเพิ่ม NLI scorer อย่างเดียวไม่เพียงพอสำหรับอ้าง method novelty สิ่งที่ CyberCase อาจศึกษาได้คือการใช้ source-bound claims เป็นหน่วยตรวจ, รักษาสถานะความไม่แน่นอน, ตรวจสองความสัมพันธ์ในกระบวนการ และเก็บ provenance ของคำเตือน ผลได้เปรียบและความใหม่ของ protocol นี้ยัง UNCONFIRMED

## Pipeline ที่เสนอ

`Case sources → reading/claims + candidate quotes → locator/binder → semantic checks → judgement/summary → optional output checks`

1. **Bind ก่อนตรวจความหมาย:** หา candidate quote ใน source จริงและรักษา source/document/page identity หากผูกไม่ได้ให้คงผลการ binding ไว้; NLI ไม่สร้างหลักฐานยืนยันขึ้นแทน
2. **Source → claim:** premise มาจากข้อความต้นฉบับที่ครอบ quote และบริบทจาก source เดียวกัน; hypothesis เป็น claim โดยรักษาผู้กล่าวและระดับความแน่นอน ขยาย context เฉพาะกรณีที่กำหนดไว้ และบันทึกช่วงข้อความที่ NLI อ่าน
3. **รักษา text ที่ถูกละไว้:** หาก quote มี ellipsis ให้ตรวจด้วย full enclosing source span รวม skipped text ไม่ใช้การต่อ quote pieces ที่ตัดคำปฏิเสธออกแล้ว
4. **Claim → generated unit:** เป็นการตรวจอีกจุดหนึ่งหลัง generation โดยใช้เฉพาะ claims ที่ unit อ้าง พร้อมสถานะจริงของแต่ละ claim เพื่อพบการเพิ่มตัวเลข บทบาท หรือความแน่นอนระหว่างสังเคราะห์

ตัวอย่างสมมติ: source ระบุว่า “พยานเห็นนาย ก. ใกล้ที่เกิดเหตุ แต่ยังไม่ยืนยันว่าเป็นผู้ลงมือ” hypothesis ว่า “พยานระบุว่าเห็นนาย ก. ใกล้ที่เกิดเหตุ” มีฐานสนับสนุน ส่วน “นาย ก. เป็นผู้ลงมือ” ยังไม่ได้รับการยืนยัน การไม่ยืนยันไม่เท่ากับการปฏิเสธว่าไม่ได้ทำ จึงไม่ควรบังคับให้ทุกกรณีที่ไม่ entail เป็น contradiction

การตีความผลที่เสนอ:

| ผล | ความหมายที่อนุญาตให้รายงาน |
|---|---|
| quote bound | พบข้อความอ้างอิงใน source ตามกติกา locator |
| NLI entailment | โมเดลประเมินว่า premise สนับสนุน hypothesis; ไม่รับรองความจริงในโลก |
| NLI contradiction | candidate `possible_conflict` ที่ต้องประเมินความแม่นยำบนงานจริง |
| NLI neutral | support ยังไม่ชัด อาจเกิดจาก context ไม่พอ; ไม่ใช่ข้อพิสูจน์ว่า claim เท็จ |
| not evaluated | ไม่ได้ตรวจ พร้อมเหตุผล และนับแยกจากผลที่โมเดลตรวจแล้ว |

เก็บ semantic verdict แยกจาก `epistemic_status` ที่ baseline ปัจจุบัน อย่าเลื่อน claim เป็น confirmed จาก NLI label และอย่าซ่อนความขัดแย้งระหว่างหลายแหล่งด้วยการเลือกเฉพาะ source ที่ให้คะแนนสูงสุด

## สิ่งที่ผลเดิมใน repo บอกได้

ผลด้านล่างอ่านจากไฟล์ที่มีอยู่ ไม่ได้ rerun และไม่ใช่ผลของ production NLI ที่ deploy แล้ว

| ทดลอง | ผลที่บันทึก | ขอบเขตการสรุป |
|---|---|---|
| [Numeric V1, English confirmation](</F:/Cybercase Framework/research/analysis_baseline/results/value_binding_nli.md>) | NLI entailment 3/20 เมื่ออ่าน quotes และ 18/20 เมื่ออ่าน quotes + source sentence | input context เปลี่ยนคำตอบของโมเดลอย่างมาก; ไม่ได้พิสูจน์ว่า 18 คำตอบถูกต้องโดย human gold |
| [Summary certainty strengthening](</F:/Cybercase Framework/research/analysis_baseline/results/nli_summary_units.md>) | evaluation: ใส่ status ใน premise ทำให้ตรวจ planted strengthening จาก 4/10 เป็น 7/10 ใน EN และ 3/14 เป็น 12/14 ใน TH | signal ที่สนับสนุนการทดลอง status rendering; sample เล็ก และ original units ไม่มี semantic gold |
| [Ellipsis confirmation](</F:/Cybercase Framework/research/analysis_baseline/results/nli_ellipsis_confirm.md>) | full-span premise + contradiction-only: planted warnings 58/60 EN, 55/60 TH; control warnings 0/60 ต่อภาษา | หลักฐานเฉพาะ constructed negation-gap task; ไม่ใช่ real-case warning precision |
| [FIZZ-style widening](</F:/Cybercase Framework/research/analysis_baseline/results/value_binding_nli_fizz.md>) | ไฟล์ระบุ partial cache/interim; EN confirmation detection 0.940 เทียบ P3 0.950, alert rate 0.057 เทียบ 0.064 | ยังไม่ใช่ผลครบทุกชุดหรือคำตัดสินให้เปลี่ยน design; quote-anchored ±1 window ต่างจาก FIZZ ต้นฉบับ |

โมเดลที่สคริปต์เหล่านี้ระบุคือ `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` [author model card](https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7) ระบุ multilingual training แต่ต้องวัด Thai case/OCR performance แยกจาก English

`nli_eval_confirm.md` ใช้ CASIE realis เป็น proxy ในบางการวิเคราะห์ ไม่ควรเรียก realis ว่า semantic-support ground truth โดยอัตโนมัติ

## การเปรียบเทียบที่เสนอ โดยยังไม่รัน

ใช้ cached readings, claims, source text และ NLI checkpoint/revision เดียวกัน แบ่งตาม Case ก่อนเลือก parameter

| Arm | สิ่งที่เปลี่ยน |
|---|---|
| A | attribution + locator/binder ที่มีอยู่ ไม่มี NLI warnings |
| B | A + NLI โดย premise เป็น quote ที่ผูกแล้ว |
| C | B + source-anchored context/full ellipsis span และ bounded conditional widening |
| D | C + rendering ที่รักษา claim status/ผู้กล่าวในคู่ข้อความที่จะตรวจ |

C เทียบ B วัดการสร้าง evidence context; D เทียบ C วัด status rendering อย่าเปลี่ยน NLI model ใน contrast เดียวกัน เลือก decision rule บน development แล้ว freeze ก่อน held-out test; ไม่กำหนด 0.5 หรือค่า threshold อื่นจากความรู้สึก

วัดแยก: source-location coverage, adjudicated semantic warning precision/recall, planted-error detection, alert rate บน real unlabeled outputs, fraction evaluated, runtime และ annotated information coverage ในสำนวน จำนวน real alerts ไม่ใช่ false-positive rate จนกว่าจะมี gold

หาก NLI เพียงให้คำเตือน ผลทดลองรองรับความสามารถในการตรวจ ไม่ใช่การลดข้อผิดพลาดของ generator หากจะอ้างว่าภาพรวมสำนวนดีขึ้น ต้องกำหนดว่าคำเตือนเปลี่ยน generation/review อย่างไร แล้ววัด downstream quality และ coverage ด้วย

ข้อเสนอเริ่มต้นคือวัดวิธีสร้าง input และกติกาการใช้ NLI ด้วยโมเดลเดิมก่อน การ fine-tune เป็นขั้นถัดไปเมื่อพบ error ที่ยังเหลือหลังแก้ input และมี training/test labels แยกกัน ไม่ต้องสร้าง verifier ensemble หรือ agent loop เพื่อเริ่มศึกษาประเด็นนี้

## วิธีที่เสนอและสิ่งที่จะวัด — follow-up 2026-10-05

ผู้ใช้ยืนยันแนวทางพัฒนา “วิธีให้โมเดลตรวจหลักฐาน” ยังไม่ได้เลือกให้รัน experiment หรือ deploy

**คำถามวิจัยที่เสนอ:** การสร้างคู่ evidence–claim จากตำแหน่งอ้างอิง บริบทที่สมบูรณ์ และสถานะความไม่แน่นอน ช่วยให้ NLI checkpoint เดิมตรวจ semantic support ได้ดีขึ้นหรือไม่ และมีต้นทุนเพิ่มเท่าใด

**วิธีที่เสนอ:** ใช้ quote ที่ bind แล้วเป็น anchor; สร้าง premise จาก source จริงโดยคืนข้อความระหว่าง ellipsis และขยายบริบทเท่าที่ protocol อนุญาต; สร้าง hypothesis ที่รักษาผู้กล่าวและความแน่นอนของ claim; เก็บ input span/claim ID/model revision ของแต่ละการตรวจ และรายงานการข้ามแยกจาก verdict

### หน่วยและ gold ที่ต้องตรึง

หน่วยทดลองคือ `(claim หรือ generated unit, evidence ที่อนุญาตให้อ้าง)` กำหนดขอบเขต evidence และความหมายเต็มของ claim รวมสถานะ ก่อนเปรียบเทียบทุก arm Gold ต้องอิงขอบเขตต้นฉบับเดียวกัน ไม่เปลี่ยนตาม premise ที่แต่ละ arm ป้อนให้ NLI และไม่ใช้ verdict ของ NLI ตัวที่ทดสอบเป็น gold

สำหรับผลหลักแบบ warning ให้ positive class คือ **ข้อความที่ evidence ที่อ้างรองรับไม่ได้** รวม contradiction และ insufficient support ตามคู่มือ annotation ไม่ใช่ “ข้อความที่เท็จในโลก” หากจะอ้างการแยก contradiction จาก neutral ต้องมี gold สำหรับทั้งสองประเภทและรายงาน confusion matrix/macro-F1 เพิ่ม

### ตัววัดหลักและตัววัดประกอบ

| ตัววัด | นิยาม | ใช้ตอบอะไร |
|---|---|---|
| Warning precision | TP / (TP + FP), เมื่อ TP เป็นคำเตือน unsupported ที่ตรงกับ gold | คำเตือนเชื่อถือได้แค่ไหน |
| Error recall | TP / ข้อผิดพลาดตาม gold ทั้งหมดในชุดเป้าหมาย | จับข้อผิดพลาดได้ครบแค่ไหน |
| Error F1 — proposed primary | 2PR / (P + R), โดยประกาศ positive class ข้างต้น | สมดุลระหว่างจับผิดกับเตือนผิด |
| False-warning rate | warnings บน supported controls / supported controls ทั้งหมด | ทำให้ข้อความที่มีหลักฐานถูกเตือนผิดมากขึ้นหรือไม่ |
| Check coverage | จำนวน target units ที่ตรวจเสร็จ / target units ที่กำหนดทั้งหมด | ข้ามคู่ยากจนคะแนนดูดีหรือไม่ |
| Trace completeness | คำเตือนที่ย้อนถึง original source, input span และ claim ID ได้ / คำเตือนทั้งหมด | ตรวจคำตัดสินย้อนหลังได้หรือไม่ |
| Cost | NLI calls/pairs ต่อ Case, เวลา p50/p95 และ peak memory ใน workload เดียวกัน | gain คุ้มกับงานที่เพิ่มหรือไม่ |

รายงาน TP/FP/FN และจำนวน skipped ด้วย กรณีไม่มีคำเตือน precision เป็น undefined ไม่ให้คะแนนเป็น 1 เป้าหมายแบบ end-to-end ให้นับ missed errors ที่ถูก skip ในตัวหาร recall; conditional performance เฉพาะคู่ที่ประเมินแล้วต้องรายงานคู่กับ coverage และ failure rate

[SummaC §4.3](https://aclanthology.org/2022.tacl-1.10.pdf) เลือก balanced accuracy เพื่อรองรับ class imbalance และเลือก thresholds บน validation สำหรับข้อเสนอนี้ F1 เป็นตัววัดหลักของการเตือน; balanced accuracy หรือ PR curve เป็นตัววัดประกอบได้ แต่ควรประกาศ primary endpoint ก่อนอ่าน held-out result

### Baseline ที่ตรงกับคำถาม NLI

| Arm | Input ที่ใช้ โดยคง checkpoint และกติกา warning |
|---|---|
| N0 | quote-only NLI |
| N1 | source context ที่มีขอบเขต/conditional widening แบบทั่วไป ระบุการดัดแปลงจาก FIZZ ให้ชัด |
| P | source-anchored/full-gap context พร้อม claim status และ provenance ตามวิธีที่เสนอ |

แยก ablation `P - status` กับ `P - full-gap restoration` เฉพาะส่วนที่เป็น contribution ของข้ออ้างนั้น หาก N1 ใช้ context builder เดียวกับ P ก็ให้ contrast P–N1 อ้างได้เฉพาะส่วน status ที่เพิ่ม อย่าเรียก FIZZ-style variant ว่า reproduction ของ FIZZ ต้นฉบับ

Pipeline ที่ไม่มี NLI เป็นระบบอ้างอิงสำหรับ traceability/downstream task ไม่ใช่ classifier baseline ที่มี semantic-warning F1 โดยอัตโนมัติ รักษา source/claims รุ่นเดียวกันและ warning policy เดียวกันเมื่อต้องการวัดผลของ input construction โดยตรง

### ข้อมูลสองชั้น

1. **Controlled challenge set:** supported controls และ known-label edits เรื่องตัวเลข/ชื่อ/บทบาท, negation ใน ellipsis และการเพิ่มความมั่นใจ ต้องตรวจว่า transformation เปลี่ยน support จริง; การเปลี่ยนข้อความไม่ได้ทำให้เป็น negative เสมอไป วัด detection และ false warnings แยก error type/EN/TH ผล F1 ในชุดนี้ใช้กล่าวได้เฉพาะ challenge set และ class mixture ที่สร้าง
2. **Real outputs:** นำคู่จาก output เดิมมาทดสอบ และให้คนตรวจชุดย่อยแบบอิสระหากต้องการ precision/recall บนงานจริง หากยังไม่มี labels รายงานได้เพียง alert rate, coverage, trace completeness และ cost ไม่เรียก alert rate ว่า false-positive rate และไม่ประเมิน recall จากการตรวจเฉพาะ alerts

ถ้าสุ่ม real pairs แบบแบ่ง strata หรือ oversample alerts ให้ใช้ sampling weights เมื่อต้องประมาณ performance ทั้งชุด; ตรวจทั้ง flagged และ unflagged units อย่าอนุมาน prevalence จาก challenge set ที่ตั้งใจเติมข้อผิดพลาด

แบ่ง development/test ตาม Case หรือ original document ก่อนสร้าง OCR variants และ synthetic edits ไม่แบ่งแบบสุ่ม pairs จาก source เดียวกัน ปรับ threshold/context budget บน development แล้ว freeze; เปรียบเทียบแบบ paired และให้ confidence interval ด้วย bootstrap ตาม Case แยก English/Thai และ error types โดยไม่นับทุก pair เป็นข้อมูลอิสระ

### ข้ออ้างที่ผลรองรับ

ผลหลักที่ต้องการคือ **ตรวจ unsupported statements ดีขึ้นด้วย NLI โมเดลเดิม พร้อมรักษา coverage และการย้อนตรวจหลักฐาน** ต้องดู precision/recall และ false-warning tradeoff ร่วมกัน การเตือนมากขึ้นหรือน้อยลงอย่างเดียวไม่เป็นความสำเร็จ

ถ้า NLI ยังเป็น warning/shadow check ให้กล่าวถึง detection capability หากใช้คำเตือนเปลี่ยน generation/review แล้ว จึงเพิ่มการวัด semantic faithfulness ของสำนวนและ annotated information coverage โดย gold อิสระ เพื่อดูว่าข้อผิดพลาดลดลงโดยไม่ลบข้อมูลสำคัญทิ้ง

## วิธีตรวจหลักฐานในงานวิจัยที่มีอยู่ — survey follow-up 2026-10-05

ขอบเขตคือวิธีวิจัยที่เข้าถึงและตรวจแหล่งต้นฉบับได้ถึง 2026-10-05 การแบ่งกลุ่มต่อไปนี้เป็น synthesis เพื่ออธิบาย ไม่ใช่ taxonomy มาตรฐานหรือรายการครบทุกงาน และกลุ่มต่าง ๆ ประกอบกันได้ แยกการตรวจ semantic support, ความถูกต้องของ source attribution และ evidence dependency ออกจากการพิสูจน์ว่าแหล่งข้อมูลเป็นความจริงในโลก

| แนวทาง | กลไกที่เปลี่ยน | ตัวอย่างและขอบเขต |
|---|---|---|
| Entailment / NLI | เทียบ evidence เป็น premise กับ claim เป็น hypothesis แล้วตัดสิน support/conflict/insufficient support; แบ่ง sentence pairs และรวมคะแนนตาม protocol | [SummaC, 2022](https://aclanthology.org/2022.tacl-1.10/) §3; E/C/N เป็นความสัมพันธ์ของคู่ข้อความ ไม่ใช่การยืนยัน source truth |
| Granularity และ context construction | แยกหน่วยที่ตรวจและเลือกบริบทต้นฉบับที่เพียงพอ; จัดการ coreference และขยาย context แบบมีขอบเขต | [FIZZ, 2024](https://aclanthology.org/2024.emnlp-main.3/) §3: coreference, atomic facts, sentence matching และ bounded neighboring context; decomposition มีความเสี่ยงทำ qualifier หาย |
| Atomic claim verification | แยกหลาย assertions ในคำตอบแล้วตรวจทีละ claim เพื่อระบุว่าองค์ประกอบใดไม่มีหลักฐาน | [FActScore, 2023](https://aclanthology.org/2023.emnlp-main.741/) ใช้สัดส่วน atomic facts ที่ source รองรับ; [FENICE, 2024](https://aclanthology.org/2024.findings-acl.841/) จับคู่ claims ที่แยกจาก summary กับ source ด้วย NLI |
| QA-based verification | เลือก answer units จาก summary, สร้างคำถาม, ให้ QA ตอบจาก source แล้วเทียบ answer/support | [QAFactEval, 2022](https://aclanthology.org/2022.naacl-main.187/) §3.2 เปลี่ยน answer selection, question generation, answerability/filtering และ answer-overlap model; ไม่ใช่การถาม LLM จากความจำเฉย ๆ |
| Evidence-conditioned LLM judge | ให้ generative LLM อ่าน context และ statements แล้วให้ verdict พร้อมคำอธิบายตามกติกาที่ระบุ | [RAGAs, 2024](https://aclanthology.org/2024.eacl-demo.16/) §3 faithfulness: แยก statements แล้วตรวจ entailment ด้วย prompted LLM; brief explanation ไม่เป็นหลักฐานอิสระว่าผลตัดสินถูก |
| Train a specialized verifier | ปรับ training examples/objective ให้เรียนรู้ข้อผิดพลาดและการสังเคราะห์หลาย source sentences | [FactCC, 2020](https://aclanthology.org/2020.emnlp-main.750/), [AlignScore, 2023](https://aclanthology.org/2023.acl-long.634/), [MiniCheck, 2024](https://aclanthology.org/2024.emnlp-main.499/); เป็น model adaptation คนละตัวแปรกับการเปลี่ยน input ของ checkpoint เดิม |
| Structured facts และ relations | แทน claim ด้วย roles/arguments/modifiers และตรวจ temporal/causal/conditional relations หรือ qualifiers แยกได้ | [Structured Discourse Representation, 2025](https://aclanthology.org/2025.findings-acl.46/) §4–6: clause tuples + discourse relations + FDSpotter; [TriQua, 2026](https://arxiv.org/html/2608.05228v1) §3: triples with qualifiers + component-level LLM verification |
| Source-aware attribution | จำกัด/route evidence ตาม source identity และตรวจว่าคำตอบอ้างว่า fact มาจาก source ที่เหมาะสมหรือไม่ | [ALCE, 2023](https://aclanthology.org/2023.emnlp-main.398/) §3.3 citation support/necessity; [ProvenanceGuard, 2026](https://arxiv.org/html/2606.18037v3) §III.3–6 แยก routed semantic support จาก attribution/conflation |
| Counterfactual evidence verification | ถอดหลักฐานที่ใช้ตัดสินแล้วตรวจอีกครั้ง หรือฝึก full/ablated context ให้ decision สะท้อน evidence availability | [FAE / REAL, 2026](https://arxiv.org/html/2609.08943v1) §4–5; negative ablation ต้องกำจัด supporting alternatives จริง มิฉะนั้น verdict ที่คงเดิมอาจถูกต้อง |
| Retrieval/search policies | ให้ verifier สร้าง query, ดึงหลักฐานเพิ่มเติม และเลือกว่าจะค้นต่อหรือหยุด; อาจแชร์หลักฐานระหว่าง claims | [SAFE, 2024](https://arxiv.org/abs/2403.18802) ใช้ multi-step search เพื่อตรวจ individual facts; [EAVer, 2026](https://arxiv.org/html/2609.22223v1) ฝึก grouping/routing/evidence reuse ด้วย SFT และ decision-focused DPO |

การสร้างคำตอบแล้วตรวจและแก้เป็น workflow ที่วางทับ verifier ได้: [RARR, 2023](https://aclanthology.org/2023.acl-long.910/) ค้น attribution และแก้ unsupported text; [CoVe, 2024](https://aclanthology.org/2024.findings-acl.212/) draft -> verification questions -> independent answers -> revised response โดย CoVe ต้นฉบับไม่ได้รับประกันการผูกกับเอกสารสำนวนที่ผู้ใช้ส่ง

[SelfCheckGPT, 2023](https://aclanthology.org/2023.emnlp-main.557/) เป็นแนว zero-resource sampling/consistency ที่ไม่มี external evidence database เหมาะอธิบายเป็นสัญญาณ hallucination/uncertainty อีกประเภทหนึ่ง การตอบซ้ำสอดคล้องกันไม่ยืนยันว่าเอกสารที่อ้างรองรับ claim

### งานใหม่ที่เปลี่ยนการตีความข้อเสนอเดิม

- TriQua (arXiv v1, 2026-08-05) มี qualifiers สำหรับเวลา เงื่อนไข causality และ provenance อยู่แล้ว; การเก็บ modifier/โครงสร้างโดยตัวมันเองไม่ยืนยันความใหม่ของ CyberCase งานระบุด้วยว่า direct verification ของ short claims ที่ให้ evidence อยู่แล้วทำได้ดีกว่า decomposition โดยรวมในชุดทดลองนั้น จึงไม่ควรตั้งสมมติฐานว่าแยกละเอียดขึ้นต้องดีขึ้นเสมอ
- ProvenanceGuard (arXiv v3, 2026-08-27; first v1 2026-06-16) ตรวจ support และความถูกต้องของ source attribution แยกกันอยู่แล้ว; ขอบเขตงานเป็น MCP-agent traces ไม่ใช่การทำสำนวนแบบ CyberCase แต่เป็น prior art ที่ใกล้กับ source-aware NLI
- FAE/REAL (arXiv v1, 2026-09-08; manuscript ระบุ CIKM'26) วัด/ฝึก evidence dependency โดย removal ไม่ใช่แค่ label accuracy; §5.2 อธิบายปัญหา gold evidence ไม่ exhaustive และปรับ evidence annotations ก่อนสร้าง negatives
- EAVer (arXiv v1, 2026-09-02) เป็น trained agentic search policy ไม่ใช่การทำ NLI pair checking อย่างเดียว; ไม่ควรนำ policy นี้มาใส่ prototype โดยไม่มีคำถามวิจัยเกี่ยวกับ search efficiency

อ่านวิธีจาก full-text QAFactEval/RAGAs/Structured Discourse และ arXiv HTML ของ TriQua/ProvenanceGuard/REAL/EAVer; FActScore/FENICE/RefChecker/SelfCheckGPT/SAFE/RARR/CoVe ตรวจ primary abstract/official source สำหรับคำอธิบายระดับ framework ใน follow-up นี้ ส่วนวิธี NLI/FIZZ/FactCC/AlignScore/MiniCheck/ALCE มี receipts การอ่านจากรอบก่อน ไม่มีการยืนยัน bibliographic lock ใหม่หรือ benchmark recomputation ในรอบนี้ และไม่เรียกผล preprint ว่า peer-reviewed โดยอัตโนมัติ

### ตำแหน่ง CyberCase ที่เสนอหลัง survey

เริ่มจาก source-bound claims ที่มีอยู่ + source-anchored context construction + status-preserving semantic verification โดย checkpoint เดิม งานเทียบที่ใกล้คือ FENICE/FIZZ สำหรับ unit/context, TriQua สำหรับ modifiers และ ProvenanceGuard สำหรับ source identity การเลือกนี้เป็นข้อเสนอสำหรับ bounded empirical comparison ไม่ใช่ข้อสรุปว่าให้ผลดีกว่าหรือเป็นแนวทางใหม่

ถ้าต้องการตรวจว่าโมเดลใช้หลักฐานจริง ให้เพิ่ม controlled evidence-removal test: เมื่อไม่มี decisive evidence และไม่มี alternative support เหลือแล้ว verifier ควรแสดง insufficient support ต้องประเมินทั้ง correct-label behavior และ evidence dependency; removal ไม่ใช่การแก้ประโยคให้กลายเป็น contradiction และความรู้ทั่วไปของโมเดลไม่ใช่หลักฐานเหตุการณ์ในสำนวน
