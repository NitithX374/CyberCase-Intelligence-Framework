# CyberCase: full-text positioning review

2026-09-30. ขอบเขต: Task A/B/C ตามข้อความแนบ ไม่แก้ application ไม่เรียกโมเดล ไม่เพิ่ม annotation หรือ LLM judge

**ข้อสรุป:** ถ้าขายว่า “multi-stage LLM + post-hoc validation” เป็น method ใหม่ ข้อวิจารณ์นี้มีน้ำหนักมาก เพราะแต่ละส่วนและการเปรียบเทียบ workflow บน narrative ที่มี human gold มีอยู่แล้ว สิ่งที่ยังพอขายได้คือ **empirical system study เรื่องการเก็บข้อมูลที่ถูก annotate และการสูญเสียข้อมูลระหว่าง trace กับ report** ภายใต้ขอบเขตที่วัดได้ แต่หลักฐานปัจจุบันยังไม่พออ้างว่าดีกว่า prior methods: ต้องเทียบ Shiri และ AEC และแยกผลทดลองเก่าจากรุ่นปัจจุบัน

อ่าน full text ของ 7 งานที่ผู้ใช้ระบุ และ 5 งานเพิ่ม รวม 12 งาน Methods/results/discussion และ appendices ที่ให้มา ดู version/hash/access ใน [paper_inventory.json](<F:/Cybercase Framework/docs/research/cybercase-positioning-fulltext-2026-09-30/paper_inventory.json>) และ locators ใน [reading_notes.md](<F:/Cybercase Framework/docs/research/cybercase-positioning-fulltext-2026-09-30/reading_notes.md>) เว้นแต่ระบุ printed page ตัวเลขหน้าเป็นหน้า PDF ที่อ่าน ไม่จำเป็นต้องตรงกับ pagination ฉบับตีพิมพ์

## A. ตาราง 9 คอลัมน์: 7 งานที่ระบุ

| 1. งาน / venue / peer review | 2. Input | 3. Pipeline | 4. Evidence / citations | 5. Verification | 6. Evaluation gold | 7. Same model + data: workflow comparison? | 8. Main numbers + locator | 9. Public data? |
|---|---|---|---|---|---|---|---|---|
| [DeepFaith — Phan et al.](https://arxiv.org/abs/2607.24348), 2026 **preprint**; ไม่ยืนยัน venue ตีพิมพ์ | Auditd/Zeek telemetry → provenance graphs | DeepStage detector → explanation/evidence serialization → LLaMA2 report → rejection/regeneration | Facts จาก graph/explanation; ไม่มี protocol ให้ verbatim source quotes | Claim/fact membership score; **ไม่ระบุ implementation พอให้จัดว่า exact-string, LLM หรือ NLI checker** | CALDERA/scenarios ที่ผู้วิจัยสร้าง และ evidence จากระบบ; ไม่ใช่ independent human narrative gold | มี same-backbone template/vanilla/CoT/full ablations; ไม่แยก one-call vs reading/judgement | §VIII-A p7: faithfulness **.92 vs .68**, unsupported-claim rate **.08 vs .32**; Table II p8: no-verifier **.86**, full **.92** | ไม่พบ dataset/code release URL ในบทความ |
| [Cadet et al.](https://doi.org/10.1145/3786335.3813136), **CAIS 2026, published peer-reviewed conference**, pp103–123; อ่าน arXiv v3 | PCAP, Suricata/Zeek/Windows logs | Query filtering/aggregation → chunk retrieval → per-question LLM → assembled report | CITED CHUNKS / source filenames | ไม่พบ verbatim quote occurrence หรือ entailment checker; evaluation มี manual review/parsing | **Mixed:** expert challenge answers + authors' manual review; AD timeline สร้างเอง | มี same-model RAG/no-RAG และ retrieval-k controls; ไม่ใช่ reading/judgement ablation และ baseline raw logs เห็นเพียง .6–4.3% ของข้อมูล | Table1 p6: 17 scenarios,129 questions,218 indicators; Claude recall **94%**; Table6 p8 AD **96% recall /100% precision** เฉพาะตัวชี้วัดที่ประเมิน | Public malware captures, code/query/reports; AD evaluation data release ไม่ระบุ |
| [Kramer et al.](https://www.usenix.org/conference/soups2025/presentation/kramer), **SOUPS 2025, peer-reviewed**, pp133–148 | **Narrative incident tickets**: analyst comments + metadata | Gemini summary → optional analyst editing | Summary จาก ticket; ไม่มี verbatim citation protocol | Human assessment/editing; ไม่มี automatic Binder | Frozen human summaries + expert comparative judgements; ไม่ใช่ public argument gold | Same tickets/model autonomous vs analyst-assisted; treatment คือมนุษย์ ไม่ใช่ autonomous two-LLM stages | 18 analysts/50 incidents; Table2 printed139/PDF8: omissions **73/211 (35%)**, factuality **89/211 (42%)** เป็น judgement counts; Table7 printed143/PDF12 assisted preferred **116/150 (77%)** | Tickets ของ Google ไม่สาธารณะ; มี prompts/instrument |
| [Jang et al., Air-Gapped Analysis](https://doi.org/10.3390/electronics15132949), **Electronics 2026 15(13):2949, peer-reviewed journal** | Sysmon/Windows/firewall logs; CTI/IR narratives เป็นส่วนของ training | Offline teacher → LoRA student → normalization/filter → inference/confidence → report → verification/HITL | Traceability Matrix: EventID/time/PID anchors | Programmatic anchor checks **และ learned FactCC-style factuality classifier**; ไม่ใช่ verbatim quote Binder (§3.3 p12/§4.4 p16) | 3,500 author-generated Atomic Red Team scenarios + attack labels/teacher reasoning | **มี** same distilled student/500 test cases full vs no-agent/no-verifier; ไม่ใช่ human narrative benchmark | Table13 p18: accuracy full **88.4%**, no-agent **74.2%**; reported hallucination full **6.2%**, no-verifier **14.1%** | Atomic Red Team สาธารณะ; processed scenarios/scripts **on request มีข้อจำกัด** |
| [Chou et al., Agentic Traffic Reports](https://doi.org/10.3390/jsan15020032), **JSAN 2026 15(2):32, peer-reviewed journal** | 71-dimensional numeric network-flow features | RF/ML ensemble → SHAP → ReAct retrieval/tools → Llama3.1 report | Tool/query citations ไม่ใช่ source quote spans | **LLM judge**, custom RAGAS thresholds; model familyเดียวกับ writer | Flow classification labels ไม่ใช่ report-fact gold; report support ให้ LLM judge | **ไม่มี** controlled single/multi or SHAP/RAG ablation; §4.6 pp29–30 เสนอเป็น future work | Table7 p23: **176/200 reports**, groundedness **1.0000**, faithfulness **.6391**; อีก24 errorsถูกตัดออก จึงไม่ใช่ zero-hallucination proof | ACI dataset สาธารณะ (10.21227/qacj-3x32); report/evaluator outputs releaseไม่ระบุ |
| [Wen et al.](https://arxiv.org/abs/2607.07751), 2026 **preprint** | **10,994 victim narratives**,8 public sources | Four-tier deterministic fields / fallback / narrative / LLM semantic extraction | Rationale quote OR paraphrase; Appendix A ขอ exact quotes ใน positive Tier4 | ไม่พบ deterministic source-occurrence checker; human coding สำหรับ validation subset | **Mixed:** bulk structured/LLM labels **และ 228 cases โดย2 human annotators**; ห้ามเรียกว่า LLM goldทั้งหมด | ไม่มี matched single/multi-stage experiment | TableV p5: H-H κ **.68**, LLM-H κ **.69**; TableVI p6 pretext Cramér's V **.685** | Release page สาธารณะ → OSF; ไม่ได้ตรวจครบทุก download หรือ licence ของ underlying sources |
| [Lu et al., RAEE](https://arxiv.org/abs/2410.09418), first2024/v2Mar2025 **preprint** | Event-extraction text benchmarks **รวม CASIE** | Existing extractor outputs → adaptive semantic precision/recall evaluation | เทียบ predicted triggers/arguments กับ annotations; ไม่มี claim/quote/report | **LLM semantic judge**, role/event-aware criteria | Existing human benchmark labels + meta-eval 800 items/3 humans | ไม่มี matched one/multi-stage design; เป็น metric reassessment | Table4 p7 CASIE PAIE argument F1 **64.00 exact →87.78 semantic** = เปลี่ยน metric ไม่ใช่ modelดีขึ้น; Table1 p4 DeepSeek-R1 EAE recall agreement **93.49%** ใน meta subset | RAEE toolkit linked; benchmark access/licencesแตกต่างกัน |

**RAEE ต้องไม่สับสนกับ BEMEAE:** arXiv2410.09418 คือ Lu et al. ไม่ใช่งาน NAACL2025 DOI10.18653/v1/2025.naacl-long.295 ของ Fane et al. ตัวหลังถูก download เพื่อแยก metadata แต่ไม่ได้ใช้เป็น full-read evidence ในคำตอบนี้

**สิ่งที่อ่านแล้วต้องระวัง:** DeepFaith ไม่เปิดวิธี matching ละเอียด; Cadet มีทั้ง independent expert answers และ self-built references; Kramer ใช้ 211/150 judgement units; Airgap ใช้ learned classifier; Traffic ใช้ LLM judge และตัด failed reports; Wen มี human subsetจริง; RAEE แสดง metric sensitivity ไม่ได้อนุญาตให้ substring matching ถูกเรียกว่า fact correctness

## B. งานที่ใกล้กว่า: citations เต็มและเหตุผล

1. **Fatemeh Shiri, Farhad Moghimifar, Reza Haffari, Yuan-Fang Li, Van Nguyen, and John Yoo. 2024. _Decompose, Enrich, and Extract! Schema-aware Event Extraction using LLMs._ 27th International Conference on Information Fusion (FUSION), pp1–8. [DOI10.23919/FUSION59988.2024.10706385](https://doi.org/10.23919/FUSION59988.2024.10706385); อ่าน author manuscript [arXiv2406.01045](https://arxiv.org/abs/2406.01045). Published conference paper.** แยก event detection → argument extraction พร้อม schema/retrieved examples; **high** เพราะมี same GPT3.5/data/five-shot comparison และ ACE human gold (§VI-1/TableII p7 Arg-C45.43→50.07) ตรงกับข้อเสนอว่าแบ่งงานช่วย extraction แต่ไม่มี claim quotes/report และ original paperไม่ได้ใช้ CASIE Maritime subsetเป็น synthetic gold จึงไม่ใช่ทุก dataset ที่ independent human

2. **Quanjiang Guo, Sijie Wang, Jinchuan Zhang, Ben Zhang, Zhao Kang, Ling Tian, and Ke Yan. 2026. _Extracting Events Like Code: A Multi-Agent Programming Framework for Zero-Shot Event Extraction._ Proceedings of AAAI 40(37), pp30880–30887. [DOI10.1609/aaai.v40i37.40346](https://doi.org/10.1609/aaai.v40i37.40346). Published peer-reviewed conference paper.** AEC ทำ retrieval/planning/coding/verification บน event benchmarks; **high มากสำหรับ extraction baseline** เพราะรวม CASIE และเทียบ workflowด้วย backboneเดียวกัน/3runs Table1 p5 CASIE70B AC: Decompose31.9/AEC33.9; Table2 p6 GPT4o AC: Guideline35.3/Decompose36.5/AEC37.8 แต่ไม่ได้ดีสุดทุกแถว **DirectEEไม่มี argument score และทุกbaselineถูกเพิ่ม common Verification** จึงห้ามอธิบายว่าเป็นการเทียบ unverified one-callกับverified multi-stageอย่างสะอาด

3. **Jingyu Zhang, Marc Marone, Tianjian Li, Benjamin Van Durme, and Daniel Khashabi. 2025. _Verifiable by Design: Aligning Language Models to Quote from Pre-Training Data._ NAACL Long Papers, pp3748–3768. [DOI10.18653/v1/2025.naacl-long.191](https://doi.org/10.18653/v1/2025.naacl-long.191). Published peer-reviewed conference paper.** Quote-Tuning ใช้ DATA PORTRAITS/Bloom-filter25-character ngrams และ DPOให้quoteจากcorpus; **high สำหรับ quoting prior art, medium สำหรับระบบรวม** เพราะการเช็ก occurrence มีอยู่ก่อน แต่เป็น approximate corpus membership ไม่ใช่ source-specific full-quote Binder และไม่รับรอง entailment Table2 p5 NQ QUIP34.9→54.5;บาง evaluation endpointใช้GPTjudges

4. **Jiashuo Zhang, Yuling Chen, Yvonne Commodore-Mensah, and Michael Oberst. 2026. _Verifiable by Construction: Claim-Level Evaluation of Verbatim Citation in Clinical Question Answering._ [arXiv2609.15964v2](https://arxiv.org/abs/2609.15964), 17September2026. PREPRINT.** แยก exact/normalized/elided quote occurrence จาก semantic claim support; **high มากสำหรับ Binderและmetric boundary** เพราะวิธี deterministic checkใกล้กันโดยตรง (§3.2/AppendixA.6 pp3–4/13) แต่ใช้ LLM judges/calibration humans ไม่ใช่ judge-free workflow ablation Table1 p5: Opus5 **98.0%claimsมีverifiedquote แต่37.1%fullysupported**; 98.0%ไม่ใช่ VCR (VCR100%อยู่Table2) Code repositoryเปิดได้จริง

5. **Ying Dehing, Hans Henseler, Timo Meconi, Marcel Worring, and Harm van Beek. 2026. _Structured Report Generation using Local LLMs for Chat-Based Digital Forensics._ Proceedings of the 2nd Digital Forensics Doctoral Symposium (DFDS2026), article6, pp1–11. [DOI10.1145/3785318.3785330](https://doi.org/10.1145/3785318.3785330). Published symposium paper; review protocolไม่ได้ตรวจอิสระ.** Two-stage chat extraction/synthesis สร้าง actor/role/timelineพร้อมTraceIDs; **high สำหรับ forensic workflowและstage loss** แต่ไม่ครบ independent gold: referenceสร้างด้วยGeminiและscoringใช้LLM-assisted/manualchecks Table3 author-manuscriptp7: Gemini single reference14IDs, staged13/14;ไม่มี deterministic renderer comparisonบนfrozen traces อ่าน full10-page manuscriptจาก [author repository](https://github.com/NetherlandsForensicInstitute/local-llm-chat-report-benchmark/blob/main/Paper.pdf); หน้า/ตัวเลขอ้าง versionนี้ ไม่สวมว่าอ่าน publisher11-page version

**Baseline verdict:** Shiri และ AEC **ต้องเข้ามาเป็น published extraction baselines** หากจะเคลม improvementเทียบงานเดิม เพราะผ่าน narrative + matched workflow + independent human gold แล้ว AECยิ่งมีCASIEโดยตรง ต้อง rerun/adaptบนmodel/news/metricเดียวกับเรา ไม่เอาpaper F1มาเทียบกับmention recall หากงบไม่พอทำทั้งคู่ ให้ลดเคลมเป็น internal workflow ablation และระบุ external comparisonยังไม่ได้ทำ

**Discovery ที่ไม่ใช้สนับสนุน verdict:** Relins, Birks & Lloyd, _Using Instruction-Tuned Large Language Models to Identify Indicators of Vulnerability in Police Incident Narratives_, JQC2025, [DOI10.1007/s10940-025-09611-z](https://doi.org/10.1007/s10940-025-09611-z): **abstract only** (Springer/PMC accessไม่สำเร็จ;HTTP200ที่ได้เป็นanti-botpage) และ Youla Yang, _LLM-Assisted Incident Coding for UAS Safety: Reliability-Aware Human-Factor Extraction and Operational Risk Analytics_, [DOI10.20944/preprints202602.0324.v1](https://doi.org/10.20944/preprints202602.0324.v1),2026 **preprint**: **not verified full text** (403) ไม่ใช้snippetอนุมานimplementationหรือผล

ไม่พบในการอ่านชุดนี้ว่างานใดเปรียบเทียบ **deterministic trace projection vs LLM rewriteจากfrozen tracesเดียวกันด้วยการนับclaim/source/status retentionตรงๆ** DeepFaithมีtemplate baselineและDehingวัดtimeline/TraceID loss จึงเป็นpriorที่ต้องอภิปราย ประโยคนี้เป็นผลจากขอบเขตการค้นครั้งนี้ **ไม่ใช่หลักฐานว่าไม่มีงานอื่นหรือ“first ever”**

## C. Verdict และขอบเขตของ delta

### ส่วนที่ known แล้ว

- Narrative incident summarization: Kramer; victim reports + quoted rationale: Wen; narrative forensic multi-stage reports + citation IDs: Dehing
- Decomposed extraction และ same-model/human-gold workflow experiments: Shiri และ AEC
- Evidence-conditioned incident reports + post-hoc rejection: DeepFaith; agentic workflow + verification ablations: Jang
- Deterministic quote occurrence: ClinicalQuotesใกล้ Binderโดยตรง; Quote-Tuningเป็นcorpus-membership prior
- Existing CASIE human labels/LLM evaluation: AEC/RAEE; independent human goldเป็นevaluation resource ไม่ใช่ algorithmic novelty
- Template rendering/structured evidence serialization: DeepFaithมีtemplate baseline; การใช้code renderเองจึงไม่ใช่novelmethod สิ่งที่อาจเพิ่มคือ **การวัดlossบนidentical frozen tracesอย่างชัดเจน**

### Delta ที่ยัง defend ได้

**Research question ที่ชัดที่สุด:** ภายใต้narrative cyber-newsชุดหนึ่ง workflowใดเก็บ *annotated arguments* ได้มากกว่า และเมื่อเก็บanalysisเป็นtraceแล้ว rendererแบบใดรักษาcontent/provenanceของtraceได้เพียงใด

1. **Narrative input:** แยกเราจากDeepFaith/Cadet/Trafficหลักๆ แต่ไม่แยกจากKramer/Wen/Dehingหรือevent-extraction work ห้ามใช้เป็นnoveltyโดดๆ
2. **Existing independent human goldโดยไม่สร้างjudgeใหม่:** ช่วยให้evaluationทำได้ภายใต้ข้อจำกัด แต่ Shiri/AECทำมาก่อน คำว่าjudge-freeหมายถึงmetricของเรา ไม่ใช่วัดทุกclaimว่าtrue
3. **Workflow comparison:** contributionเชิงempiricalภายใต้model/data/prompts/งบที่ระบุ แต่ **calls,prompts,available intermediate evidenceเปลี่ยนพร้อมกัน** จึงระบุcauseเฉพาะrepresentation/decompositionไม่ได้ Paired casesคุมcase variability แต่ไม่ได้ทำให้copy bias,length,model memorization,providersและprompt effectsหักล้างกันอัตโนมัติ
4. **Frozen-trace report comparison:** เป็นmeasurementที่ตรงกับriskเพิ่มข้อมูล/ตกหล่นตอนrewrite และแยกจากการทำanalysisถูกผิดได้ อย่างไรก็ดี deterministic repeatabilityคาดได้จากcodeอยู่แล้ว ต้องขายผ่าน **measured preservation contractและfailure modes** ไม่ใช่ความมหัศจรรย์ของdeterminism

### หลักฐานใน repo ทำให้ต้องแก้เคลมสี่จุด

**(i) “single_late rules out order” แรงเกินหลักฐาน**

[Saved B2 receipt](<F:/Cybercase Framework/research/analysis_baseline/results/main_20260929_233326_b2.md>) ระบุ single .667 /single_late .688 /two-call .779:
- late−single **+.021**,95%CI[-.043,.083],p=.5471: ไม่พบdifference ไม่ใช่พิสูจน์ไม่มีeffect
- two−late **+.091**,95%CI[.004,.182],p=.0468 แต่ **Holm=.0936**
- late armรันสองวันหลังarmเดิม จึงมีdate/provider confoundด้วย

คำที่ใช้ได้: “Moving the summary last did not yield a detectable improvement in this dev sample; evidence for the remaining two-call margin weakened after multiplicity correction.” ห้ามสรุปว่าทดสอบจนตัดorderออกได้ทั้งหมด

**(ii) Metric วัด mention/citation occurrence ไม่ใช่ semantic facts**

[run.py](<F:/Cybercase Framework/research/analysis_baseline/run.py>) ให้creditเมื่อgoldstringอยู่ที่ไหนก็ได้ในowntext ไม่ตรวจrole/event binding เช่นVictimชื่อFacebookยังได้creditแม้เขียนFacebookเป็นattacker Gold-span citation coverageให้creditquoteoverlapแม้ไม่ได้statefactนั้น “stated-and-cited recall”ที่เพิ่มเป็นintersectionยังไม่พิสูจน์ว่าquoteรองรับclaim และrole-inversion lexiconเป็นdiagnosticแคบๆ ไม่ใช่role-aware F1 ดูimplementationใน [heldout_analysis.py](<F:/Cybercase Framework/research/analysis_baseline/heldout_analysis.py>)

CASIEยังใช้ได้เพื่อวัดannotated-argument coverage;เพิ่มnative role/event tuple exact-matchเฉพาะoutputsที่mapได้โดยไม่ใช้LLMjudgeได้ แต่ต้องประกาศเป็นmetricอีกตัวและอย่าอ้างว่าจับparaphrases/negation/ทุกfactได้ครบ CASIEไม่มีgoldสำหรับgaps/judgement/summaryทุกข้อ จึงไม่ใช้ยืนยันสิ่งเหล่านี้

**Recall-onlyยังมีปัญหาobjective:** การคัดข่าวทั้งชิ้นย่อมเก็บgoldstringsได้สูงโดยไม่ต้องวิเคราะห์ Saved A3พบtwo-call owntextยาวอย่างน้อยเท่าบทความใน37/48completedcases;articleleadที่ใช้wordbudgetเท่ากันได้recall .990 (descriptive) ขณะที่two-calloverall .779รวมfailures ตัวเลขสองนี้มีdenominator/estimandต่างกันจึงห้ามใช้เป็นpairedperformanceclaim แต่ชัดว่าmentionrecallอย่างเดียวไม่ใช่summarizationqualityหรือcompressionquality ให้แสดงcopy/leadsanitybaselineและlength/cost พร้อมmetricที่ตรวจrole/eventหรือprecisionได้ในsubsetที่มีgoldตรงtask ไม่ขาย+.112เป็นหลักฐานว่าanalysisดีกว่าทุกด้าน

**(iii) ตอนนี้ไม่ได้วัดว่า LLM2 เปลี่ยน atomic factsจากLLM1หรือไม่**

[write.py](<F:/Cybercase Framework/backend/app/analysis/write.py>): judgementได้รับ **original sources + reading** และ [joined_trace](<F:/Cybercase Framework/backend/app/analysis/write.py:103>) **copy claims/parties/timeline/impactsจากreading**; judgementให้summary/gaps/MITREเท่านั้น Atomic-record retentionจึงเกิดจากcode invariant หากจะศึกษาว่าข้อมูลหาย/บิดในLLM2summary ต้องแยกscore summaryเทียบfrozen reading/source ไม่ใช้claimarrayที่copyมาเป็นหลักฐานว่าLLM2faithful

**(iv) Report1,755เป็นv1เก่า และมีprovenance lossที่ต้องเปิดเผย**

[summary.json](<F:/Cybercase Framework/research/report_fidelity/runs/main/summary.json>), [RUN_NOTES](<F:/Cybercase Framework/research/report_fidelity/RUN_NOTES.md>):
- selected30cases,traceสำเร็จ26,failed4ไม่replace
- **585distinctclaimrecords ×3renderings =1,755claim-renderinginstances** ไม่ใช่1,755 independent facts/cases
- deterministic1755/1755claimsและ26/26byte-identical;LLM1707/1755claims (.9726),0/26byte-identical,2/78malformed
- LLMstatus_changed **0/1707**; “byteต่าง”ไม่เท่ากับfactmeaningเปลี่ยนทุกครั้ง มีตัวอย่างdateผิดที่ตรวจได้จริงหนึ่งเคส
- deterministic sourceIDs **1092/1728=.6319**,contradictionSources0/3;LLMsourceIDs1680/1728=.9722 ดังนั้นไม่ได้ชนะทุกdimension
- ใช้ **one-call DeepSeek4.1Flash trace**,ไม่ใช่two-call Gemmadev50;ห้ามนำมาต่อกันเป็นผลcurrentend-to-end

[PROTOCOL_V2](<F:/Cybercase Framework/research/report_fidelity/PROTOCOL_V2.md>) exportcurrentreportcode4aa8b18และอ่านGemmatwo-callheldouttraces แก้source-label/gap-displayไปแล้วแต่ **main evaluationยังไม่พบcompletedreceipt** dryrunไม่ใช่main evidence ส่วนheldoutanalysisต้องรายงานstatusจาก [project_inventory.md](<F:/Cybercase Framework/docs/research/cybercase-positioning-fulltext-2026-09-30/project_inventory.md>) และไม่ใช้interimmetrics

### Strongest defensible contribution: 3 sentences

> เรานำเสนอ empirical study ของระบบวิเคราะห์ narrative cyber incidents ที่เก็บการอ่านเป็น source-linked trace และแยกการสร้าง judgement กับการ render report เพื่อศึกษาการคงอยู่และการสูญเสียข้อมูลในแต่ละขั้น ภายใต้ existing CASIE human annotations และ deterministic metrics ที่ไม่ใช้ LLM judge ผล dev50ของโมเดลหนึ่งพบ two-call workflowมี annotated-argument mention recall .779 เทียบsingle-call .667 ขณะที่การทดลองreportรุ่นก่อนวัดการเก็บclaim/source/statusบนfrozen tracesเดียวกันโดยแยกข้อผิดพลาดแต่ละประเภท หลักฐานนี้รองรับข้อสรุปเฉพาะ coverageและtrace-to-report preservationในsettingที่ทดสอบ โดย external-method comparisonและผลheld-out/current-renderer replicationยังไม่ครบ จึงไม่ใช่เคลม methodใหม่หรือ semantic factuality guarantee

เป็นstatementที่ใช้กับหลักฐาน **ตอนนี้** ได้ หากheldout/baselinesไม่ยืนยัน ให้ลดstatementตามผล ไม่เติม“consistent improvement”ล่วงหน้า

### Claims ที่ห้ามทำจาก evidence ปัจจุบัน

- “First narrative/case analysis”, “first multi-stage extraction”, “first exact-quote verification”, “first CASIE LLM evaluation”
- “Two-stage more factually correct by11.2%”: deltaคือ **.112 recall points/11.2percentagepoints** ในmetricmention ไม่ใช่relativefactual-accuracygain
- “Order does not explain the gain”, “structured representation alone causes the gain”, “same-model/data cancels all biases”
- “Binder guarantees support/truth”, “grounded recall guarantees claim entailment”, “zero hallucinations”
- “LLM2 preserved all facts”จากjoinedtraceที่copyมา หรือ“ทุกLLMreportบิดfacts”จากbyteinequality
- “1,755 independent observations”, “allprovenance retained”, “current Gemma end-to-endpreservation100%”, “LLMalwayshardensstatus”
- “General/Thai/multi-source case effectiveness”, “gaps/judgement/MITREquality validated”,“100heldout replicated”ก่อนcompletedreceipt
- “CASIEไม่มีlicenceจึงevaluation-onlyallowed”: missinglicenceไม่ให้สิทธิ์โดยอัตโนมัติ publicaccessไม่เท่ากับredistributionrights

### สิ่งที่ทำได้โดยไม่ละเมิดข้อจำกัด no human evaluation

ขั้นต่ำเพื่อstrengthen paperคือexternalbaselineShiri/AECภายใต้budgetที่ตกลง,จบheldoutและv2reportโดยรายงานfailures/CI/provider/cost,และแยกnativeevent-rolemetricsกับmention/occurrence/retention หากต้องการisolate“decompositionช่วยเหนืออีกmodelcall”จริง ต้องมีequal-budget two-callgenericdraft/revise controlด้วย;นี่เป็น **proposal ไม่ได้ทำหรือเรียกโมเดลให้** ผู้ใช้ไม่ได้อนุญาตexperimentเพิ่มในrequestนี้

ไม่มีautomaticmetricจากCASIEที่ทำให้ตรวจsemanticclaimaccuracy,gapqualityหรือentailmentทุกข้อได้ครบโดยไม่มีgoldตรงtask ห้ามปิดช่องนี้ด้วยการrenameproxy

## Related Work: English draft

LLM-based incident analysis already extends beyond telemetry. [Kramer et al. (2025)](https://www.usenix.org/conference/soups2025/presentation/kramer) study real incident narratives, finding omissions and inaccuracies in autonomous summaries and benefits from analyst editing. [Wen et al. (2026, preprint)](https://arxiv.org/abs/2607.07751) analyze victim reports with quoted rationales and validate a subset against dual human annotations. [Dehing et al. (2026)](https://doi.org/10.1145/3785318.3785330) generate forensic chat reports through chunk-level extraction and synthesis, but evaluate against a Gemini-generated reference using LLM-assisted scoring. Decomposition under independent event annotations is also established: [Shiri et al. (2024)](https://doi.org/10.23919/FUSION59988.2024.10706385) compare direct and decomposed extraction under matched conditions, while [Guo et al. (2026)](https://doi.org/10.1609/aaai.v40i37.40346) evaluate multi-agent event extraction, including CASIE, with shared-backbone workflow baselines. Therefore, narrative input, decomposition, and existing human gold do not individually distinguish CyberCase. For evidence verification, [Zhang et al. (2026, preprint)](https://arxiv.org/abs/2609.15964) distinguish deterministic exact, normalized, and elided quote matching from semantic support; locating a quote does not establish entailment. CyberCase investigates information preservation across narrative analysis and report rendering. It compares analysis workflows using existing CASIE annotations and separately measures preservation when deterministic and LLM writers consume identical stored traces. Its automatic metrics cover annotated-argument mentions, citation occurrence, and trace-to-report retention, rather than unrestricted factual correctness. The study claims empirical evidence within this setting, not a novel multi-stage architecture or guaranteed semantic faithfulness.

Draftนี้อธิบายdesign/evaluation scope ไม่ประกาศผลheldoutหรือv2mainว่าเสร็จแล้ว Bibliographic keysและidentifiersอยู่ใน [references.bib](<F:/Cybercase Framework/docs/research/cybercase-positioning-fulltext-2026-09-30/references.bib>); metadata verificationแยกจากsentence-supportใน [citation_requests.json](<F:/Cybercase Framework/docs/research/cybercase-positioning-fulltext-2026-09-30/citation_requests.json>) และ [VERIFICATION.md](<F:/Cybercase Framework/docs/research/cybercase-positioning-fulltext-2026-09-30/VERIFICATION.md>)

