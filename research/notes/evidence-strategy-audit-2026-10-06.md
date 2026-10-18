# CyberCase: evidence strategy audit and bounded experiment proposal

Checked: 2026-10-06. Live source baseline: main at 5b6c03e14ea3200af0f159f1cfa886eb0ea4bcc2.

Scope: ตรวจโค้ดปัจจุบัน ผลทดลองที่บันทึกไว้ และ method sections ของ paper ที่เกี่ยวข้อง เพื่อประเมิน design knobs สำหรับ General Case Summarization. งานนี้ไม่ได้เปลี่ยน application, เรียก provider, รัน NLI, rerun scorer หรือยืนยัน deployment health.

## 1. ข้อสรุปจากระบบปัจจุบัน

Evidence handling เป็นแกนทดลองที่เข้ากับ CyberCase แต่ evidence-first มีทั้ง prior art และ baseline ใน repo แล้ว ข้อเสนอที่มีประโยชน์ต่อคือแยกกลไกการสร้าง source anchors ออกจากนโยบายเมื่อ anchor ใช้ไม่ได้ แล้ววัด final output และข้อมูลที่สูญเสียด้วย denominator ที่รวม failures.

Current production core:

    Source bundle
      -> case_reading: claims + status + copied quotes + parties/timeline/impacts
      -> bound_claims: locate/canonicalize quotes; demote unbound reported claims
      -> case_judgement: summary from checked reading
      -> bound_references: derive final summary units and check claim references

Production ยังมี gap assessment/follow-up และ conditional MITRE/RAG รอบ core นี้ แต่การทดลอง evidence handling ควร freeze หรือปิดส่วนเหล่านี้เหมือนกันทุก arm.

| ประเด็น | หลักฐานในโค้ด | ผลต่อการตีความ |
|---|---|---|
| Reading กับ synthesis แยกกันแล้ว | [write.py](../../backend/app/analysis/write.py#L35) | Quote binding เกิดหลัง reading แต่ก่อน final summary จึงควรระบุว่า post-reading binding |
| Judgement ไม่รับ raw case_sources | [judgement_request](../../backend/app/analysis/write.py#L117), [reading_payload](../../backend/app/analysis/write.py#L160) | Summary รับ claims/status/located quotes; citation context และ unverified metadata ถูกซ่อน แต่ QA และ technical context ยังเป็น separate inputs |
| ไม่ใช่ free-form intermediate | [CaseProviderReading](../../backend/app/trace/trace.py#L168), [claims](../../backend/app/trace/claims.py#L169) | มี structured claims/status/shared claim references อยู่แล้ว แม้ไม่ได้สร้าง explicit SVO plan |
| Binder ไม่ลบ claim เพราะ quote ไม่พบ | [bound_claims](../../backend/app/trace/bind.py#L70), [confirmed_status](../../backend/app/trace/bind.py#L336) | เปลี่ยน reported เป็น not_confirmed เมื่อไม่มี supporting quotation ที่ bind ได้; inference/unknown ไม่ได้รับการ demote แบบเดียวกัน |
| Binding ไม่ใช่ semantic entailment | [located_quote](../../backend/app/trace/bind.py#L351), [added_citations](../../backend/app/trace/bind.py#L428) | หาและดึงข้อความจาก source จริงได้ แต่ claim อาจตีความ quote ผิดได้ |
| ตรวจ reference ของ summary แล้ว | [bound_references](../../backend/app/trace/bind.py#L104), [summary_units](../../backend/app/trace/bind.py#L135) | รู้ว่า unit ชี้ claim ใดและ claim มี citation หรือไม่; ไม่ได้พิสูจน์ว่า unit สรุปความหมาย claim ถูก |

Prompt สั่งให้ไม่รายงาน not_confirmed เป็น established fact และให้ทุก summary sentence อ้าง claim ID: [prompts.py](../../backend/app/analysis/prompts.py#L239). Binding ยังเก็บ final text ที่ model สร้างและรายงาน support ของ units; prompt compliance ต้องวัดจาก output.

คำว่า unsupported ต้องระบุ detector: quote-unlocated, source-ID-invalid และ semantically-unsupported เป็นคนละสถานะ. ตัวอย่างเช่น quote คัดลอกผิดแต่ claim มี support ใน source เป็นเหตุผลให้แก้ anchor หรือ label; ไม่ใช่หลักฐานว่า claim เท็จ.

## 2. Arms ที่มีจริงแล้ว

| Strategy | สถานะ | สิ่งที่มี / สิ่งที่ยังขาด |
|---|---|---|
| Direct source -> summary | มี research runner และ saved outputs | [direct_summary.py](../../research/analysis_baseline/direct_summary.py), ไม่ใช่ backend arm ชื่อ direct |
| Claims + generated quotes -> binder -> retain/label -> summary | Production ปัจจุบัน | ใช้ checked reading และ claim IDs ใน summary |
| Select copied source spans -> generation | มี Attribute First CoT research baseline | [attrfirst_cot.py](../../research/analysis_baseline/attrfirst_cot.py#L110); copy/match/retry selection และ fusion in context |
| Hard remove unbound reported claims before synthesis | ยังไม่พบใน production/registered analysis arms | ต้องนิยาม filtering rule และจัดการ references ของ parties/timeline/impacts; ไม่เท่ากับลบ semantically unsupported units |
| Select enumerated source IDs -> materialize source text -> synthesis | ยังไม่พบ generation arm นี้ในเส้นทางที่ตรวจ | เป็น proposed controlled adaptation; source materialization และ final citation checks ต้องเกิดในโค้ด |
| Quote repair | มี bounded research arm | [revise](../../backend/experiments/analysis_arms.py#L134) ลองแก้ unfound quotes ตาม prompt; ไม่ใช่ runtime NLI repair แบบ uMedSum |

ชื่อ arm มี collision: [backend direct](../../backend/experiments/analysis_arms.py#L53) เรียก write_analysis ซึ่งปัจจุบันยังทำ bound_claims ภายใน write_trace. มันจึงไม่ใช่ no-provenance direct summary baseline. ชื่อ verify/single/revise ต้องอ่าน composition และ pinned revision ก่อนใช้ใน paper.

AF baseline ไม่ใช่ evidence-only: fic_prompt ให้ document ที่ mark highlights และตัดหลัง highlight สุดท้าย จึงยังมี unselected text ก่อนหน้านั้น: [attrfirst_cot.py](../../research/analysis_baseline/attrfirst_cot.py#L146).

## 3. ผลทดลองเดิมที่เกี่ยวข้อง

แหล่งหลัก: [pipeline_table.md](../../research/analysis_baseline/results/pipeline_table.md), [protocol/results in README](../../research/analysis_baseline/README.md#L4509), [Gemma AF run.json](../../research/analysis_baseline/results/raw_attrfirst_cot_main_20261004_041927/run.json), [Direct run.json](../../research/analysis_baseline/results/raw_direct_summary_20261004_053633/run.json).

เป็น historical runs วันที่ 2026-10-04 บน 50 English CASIE + 50 Thai ThaiSum; งานวันนี้อ่านผลเดิมและนับ saved AF records ไม่ได้รันโมเดลหรือ recompute metric scores. A ในตารางเป็น production ก่อน claims-only change; C ใกล้ current shipped composition. ไม่ถือว่ารันซ้ำที่ current HEAD.

| Saved measure | Direct D | Claims-only C | Attribute First CoT AF |
|---|---:|---:|---:|
| Completed items | 100/100 | 100/100 | 92/100 |
| English key-fact coverage, full | 0.548 | 0.629 | 0.625 |
| English key-fact coverage at A's length | 0.455 | 0.574 | 0.593 |

AF coverage ใช้ completed cases ซึ่งไม่ใช่ชุดเดียวกับ C ทั้งหมด. Paired C minus AF full coverage เป็น +0.023, 95% interval [-0.042, +0.094]. ผลนี้ยังไม่ establish superiority หรือ equivalence. Coverage เป็น lexical matching ของ annotated facts; ไม่ใช่ human semantic faithfulness.

นับ raw Gemma AF records วันนี้:

- 4/50 English และ 4/50 Thai ไม่สำเร็จ; run.json ระบุทุกเคสว่า selection traceability validation ไม่ผ่านหลัง 5 attempts.
- Final summary ต่างจาก concatenated attributed planning sentences หลังตัด whitespace ใน 11/46 English และ 8/46 Thai ที่สำเร็จ. นี่เป็น textual mismatch ไม่ใช่ข้อพิสูจน์ว่าเนื้อหา unsupported แต่ห้ามย้าย planning citations ไปอ้าง final summary โดยไม่ตรวจ alignment.
- Total run = 231 calls / 100 attempted cases = 2.31 calls ต่อ attempted case. ค่า 2.08 ใน pipeline table เป็น mean ต่อ completed item ซึ่งไม่รวมต้นทุนของ failed cases.

ข้อควรระวังเมื่อหยิบผลเดิม:

- [attrfirst_cot.md](../../research/analysis_baseline/results/attrfirst_cot.md) ปัจจุบัน header ชี้ Gemini Flash Lite run. ใช้ raw directory และ model ใน run.json ยืนยันทุกครั้ง; อย่านำไฟล์นี้มาอ้างว่าเป็น Gemma table.
- pipeline_table.py นับ C citation_share จาก known claim IDs และ AF จาก planning highlights: [scoring code](../../research/analysis_baseline/pipeline_table.py#L84). ค่า 1.000 จึงไม่ใช่ 100% semantic support และ AF ยังมี final/planning mismatch.
- AF uses temperature 0.1, few-shot demos และ retry cap 5; Direct ไม่ระบุ temperature และมี transport retry. Old table เป็น system comparison ไม่ใช่ isolated evidence-order experiment.
- Prefix truncation เป็น post-hoc length diagnostic และอาจเอื้อ source-order/news-lead outputs. Experiment ใหม่ควรกำหนด output budget ก่อน generate.

## 4. Paper anchors: อ้างได้แค่ไหน

| Primary source inspected 2026-10-06 | Method evidence | ขอบเขตการอ้าง |
|---|---|---|
| [CoPERLex, Findings NAACL 2025](https://aclanthology.org/2025.findings-naacl.57.pdf), §3 | Content selection -> SVO/event plan -> summary from selected content + plan; MemSum selection และ trained plan/generation models | รองรับ planning/representation เป็น substantive design axis; LLM-generated SVO ใน CyberCase จะเป็น adaptation ไม่ใช่ exact replication |
| [TracSum, EMNLP 2025](https://aclanthology.org/2025.emnlp-main.43.pdf), §5-6 / Appendix G | Trained tracker selects sentences, summarizer uses selected evidence หรือ selected evidence + full abstract; §6.2 รายงาน context variant ช่วย claim recall | รองรับการแยก evidence selection และ context exposure; ผลใน medical aspect task ไม่รับรอง trade-off เดียวกันใน CyberCase |
| [uMedSum, ACL 2025](https://aclanthology.org/2025.acl-long.134.pdf), §3.2-3.3 | Atomic-unit NLI removal แล้ว key-information extraction/coverage detection/insertion | ใกล้ remove-then-add correction; ไม่ใช่หลักฐานว่า quote binding ตรวจ semantic support หรือเป็น exact quote-repair loop |
| [Attribute First, then Generate, ACL 2024](https://aclanthology.org/2024.acl-long.182.pdf), §3.1-3.2 | Select source spans -> plan -> generate; ICL copied spans are located by string matching; CoT combines planning/generation | Prior evidence-first attribution และ repo baseline ที่ใกล้ที่สุด; อ้างว่า evidence-first paradigm เป็นของใหม่ไม่ได้ |

UKCP จากข้อความที่ส่งมายังระบุ work/identifier ไม่ได้ชัดเจนหลัง bounded search; ไม่ใช้เป็น paper anchor จนทราบชื่อ/URL. ตารางนี้เป็น content inspection memo ไม่ใช่ submission bibliography/citation lock.

## 5. Design ที่แนะนำสำหรับขอบเขตประมาณหนึ่งสัปดาห์

Research question ของผู้ใช้ใช้ได้ในฐานะ system-strategy question:

> How do different evidence-grounding strategies affect the trade-off between information preservation and source traceability in LLM-based case summarization?

แต่ A Direct / B retain / C drop / D evidence-first เปลี่ยนทั้ง source representation, stage inputs และ failure policy. ใช้รายงาน comparative system behavior ได้; จะสรุป causal effect ของ evidence ordering เพียงอย่างเดียวไม่ได้.

แนะนำทำ source anchoring เป็น primary knob และ hard removal เป็น optional policy contrast:

1. เก็บ Direct และ current CyberCase เป็น reference systems; current CyberCase เป็น measured arm ที่มีประโยชน์อยู่แล้ว.
2. ใช้ existing sentence_spans สร้าง catalog ก่อน model work: evidence_id, source_id, start/end, source text และ source snapshot identity. Evidence ID เป็น local to the frozen snapshot; ไม่เพิ่ม database table หรือ production schema.
3. Evidence selector อ่าน catalog แล้วคืน existing IDs เท่านั้น. โค้ด validate IDs และ materialize original source slices. Unknown IDs หรือ no evidence เป็น explicit run outcome ตาม frozen protocol; ไม่ silently substitute full document.
4. Synthesis รับ selected evidence และคืน final summary units พร้อม evidence IDs ของแต่ละ unit. ตรวจ references ของ final units ที่ส่งออกจริง; ไม่ reuse citations จาก planning text ที่ต่างจาก final text.
5. สำหรับ causal Copy-vs-ID comparison ให้ทั้งคู่เลือกจาก sentence catalog เดียวกัน, ใช้ sentence granularity เดียวกัน และใช้ common synthesis/output/retry settings. E-Quote คืนข้อความของ selected sentences แล้ว locator bind; E-ID คืน IDs แล้วโค้ดดึง text. ถ้าใช้ arbitrary copied spans เทียบ whole sentence IDs จะมี granularity confound.
6. ผล comparison ระหว่าง E-ID กับ current claims/status architecture ยังเป็น system-level comparison เพราะ intermediate content ต่างกัน. ถ้าอยากทดสอบ retain/drop ให้ reuse identical cached written+bound reading, เปลี่ยนเฉพาะ treatment ของ originally reported claims ที่ไม่มี verified supporting quote แล้วใช้ common synthesis.

Hard-remove ต้องจัดการ dangling references จาก dropped claims โดย explicit policy และบันทึก dropped IDs. อนุญาต inference/unknown และ contradiction ตาม common task definition; ไม่ตั้งกฎว่า quote-unlocated แปลว่า false. ไม่เรียก gate นี้ semantic verifier ถ้าใช้แค่ binder.

Source-ID construction guarantee จำกัดที่ข้อความ evidence มาจาก input snapshot และ reference เป็น known ID. Model ยังเลือก evidence ผิดหรือสรุปเพิ่มความหมายผิดได้. คำว่า LLM ห้ามออกนอก evidence เป็น instruction; semantic compliance ต้องประเมินแยก.

Evidence + full context ควรเป็น follow-up contrast ที่ reuse selected evidence ชุดเดิมและเพิ่มเฉพาะ context payload. ไม่เปลี่ยน selector ไปพร้อมกัน. ไม่จำเป็นต้องเพิ่ม NER, event extractor, reranker หรือ ATT&CK variant ใน study นี้.

Implementation ที่จะพิจารณาควรอยู่ฝั่ง research/experiments และ reuse pure source/sentence utilities; app ไม่ import experiments. Case/document distinction, source authority, source revision และ production API/trace contracts ยังเป็น invariants. งานนี้ไม่ได้ implement design ดังกล่าว.

## 6. Measurement contract ที่ต้องตรึงก่อน run

| Endpoint | Operational definition / denominator |
|---|---|
| Information preservation | Gold required fact recall in final summary against original sources, not selected evidence; failed cases score zero in all-attempted primary results |
| Semantic faithfulness | Atomic final units judged supported/contradicted/unsupported with original evidence scope and status/modality; independent adjudicated labels for a bounded balanced sample, or label automatic NLI explicitly as proxy |
| Structural traceability | Final delivered unit -> known reference -> actual source slice in frozen snapshot; report full-chain coverage plus broken/unknown refs; citation presence alone is insufficient |
| Information loss | Separate missed facts at selection from selected-but-not-stated facts after synthesis; for drop policy report relevant source-supported items lost using independent labels |
| Reliability/cost | Completion per attempted case, all attempts/tokens/time/cost including retries and failures; separate conditional completed-case quality |

Controls: same case split, source text/extraction version, model/provider, decoding and retry budget, summary length target, language, evidence scope and evaluation rules. Fixed QA/technical context or none for all arms. Cached artifacts have source/code/prompt/config hashes and exact model/run identities. Pair comparisons by case with uncertainty intervals.

Existing outputs can support retrospective/exploratory analysis. New confirmatory claims need a protocol fixed before running and cases not used to tune the new design. Gold missing from CASIE annotations does not mean a generated fact is false; Thai reference similarity is not semantic support. Report English/Thai task-specific measures separately.

Within one week prioritize completing final-unit trace checks and a bounded semantic audit before adding further variants. If gold/cost/time is insufficient, report traceability, annotated preservation and reliability with their exact scope rather than assert unmeasured faithfulness gains.

## 7. Audit receipts

- Read workspace ledger, root AGENTS.md, architecture guidance, current write/bind/prompt/trace contracts, registered experiment compositions and saved scoring definitions.
- Git baseline: main 5b6c03e1; four pre-existing deleted tracked files and existing untracked documentation preserved. No app/test/dependency edits.
- Read four primary paper PDFs and relevant method/evaluation sections; no provider calls, NLI inference, paid experiment, app tests, training, installation or deployment health checks.
- Recounted saved Gemma AF item/failure/final-planning mismatch counts using JSON fields; other reported scores are read from the saved pipeline table, not recomputed.
- Wrote this audit memo and updated CONTINUITY.md. Validation checks and path/hash receipts are recorded in the ledger.
