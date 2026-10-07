# Full-text reading receipts, 2026-09-30

Primary PDFs and extracted page-tagged text are cached at `C:/Users/kkham/AppData/Local/Temp/cybercase-positioning-20260930-7cgxxgpj`. The manifest records hashes. Full-text reading means methods, results, discussion and supplied appendices; reference lists are not treated as research evidence. No provider calls or application changes.

## DeepFaith: read complete (9 PDF pages)

- Phan, Nguyen and Bauschert, arXiv:2607.24348v1 (2026), preprint; no independently verified publication venue.
- Input Auditd/Zeek telemetry -> provenance graphs -> DeepStage/DeepXplain -> deterministic evidence serialization -> LLaMA2-13B reports -> faithfulness rejection/regeneration. Not narrative case documents.
- Section V-D, PDF p5: claim/fact membership score; concrete implementation of extraction/matching is not specified. Do not label it exact-string quote binding or NLI. Section VII-C, p6: objective approximated through prompting/decoding, not end-to-end training.
- Self-built CALDERA scenarios and model-derived evidence, not independent human gold. Same backbone/scenarios variants template, vanilla, CoT and full; not isolated one-call versus two-call reading/judgement.
- Section VIII-A, p7: faithfulness .92 versus .68, unsupported-claim rate .08 versus .32; temporal consistency .88 versus .60. Table II, p8: without verification .86 versus full .92. No public dataset/code URL specified.

## Wen et al.: read complete main and appendix (10 pages)

- Wen, Ogot, Li and Bai, arXiv:2607.07751v1 (2026), preprint.
- 10,994 victim narratives, eight public sources; deterministic field extraction + field/narrative fallback + narrative extraction + Claude Haiku4.5 semantic indicators. Four tiers are heterogeneous extraction responsibilities, not a matched two-call ablation.
- Section IV-F, p5 permits quote or close paraphrase in rationales. Appendix A p10 Tier4 explicitly asks exact 15-60-word quotes for positive labels. No deterministic quote-occurrence checker reported.
- Mixed label provenance: bulk structured fields/LLM labels plus 228 cases independently annotated by two coauthors. Table V p5: human-human kappa .68, LLM-human .69. Do not describe as LLM gold only.
- Table VI p6: pretext association Cramer's V .685. No single/multi-stage matched experiment. Public release claimed at https://research.zkwen.site/scamschema, actual access pending.

## Cadet et al.: read complete main and appendices (21 pages)

- PDF arXiv:2603.18196v3, 4 May2026. Venue CAIS2026 claimed, independently published/reviewed status pending metadata verification.
- Suricata, Zeek, Windows logs/PCAP -> deterministic query filtering and aggregation -> semantic chunking/FAISS -> per-question LLM -> assembled report/summary. CITED CHUNKS is source-file attribution; no verbatim quote or entailment checker described.
- Malware references from independent expert challenge solutions plus authors' manual log review; AD timeline self-built exhaustive log review. Not exclusively self-built or exclusively independent public gold.
- Same-model RAG/no-RAG and retrieval-k controls; no reading/judgement one/two-call experiment. Raw baseline sees only 0.6-4.3% of logs, so treatment also changes available evidence.
- Section6/Table1 p6: 17 scenarios/129 questions/218 reference indicators; mean recall Claude94%, DeepSeek89%, Llama81%. Table4 p7 FakeAuth Claude100 versus50 no-RAG. Table6 p8 AD up to96% recall, 100% precision. Table5 p8 cost excludes local hardware and uses estimates, not present-day pricing.
- Appendix H/I p20-21 discusses incompleteness of references and manual scoring for nonstandard outputs. Public code, reports and query library https://github.com/neu-nds2/llm-sec-incident-analysis; public malware captures, AD release not specified.

## Kramer et al.: read complete main and appendices (17 PDF pages)

- SOUPS2025 peer-reviewed proceedings, USENIX, printed pp133-148 (PDF includes cover).
- Real closed incident tickets with analyst narrative comments and metadata, XML input -> Gemini1.5Flash short summary -> optional human editing. Narrative input therefore already present in incident research.
- No verbatim citation protocol or automated source/semantic verification; humans review/edit.
- 18 analysts, 50 incidents. Independent expert preferences versus frozen human summaries; in-house sensitive data, not public gold dataset.
- Table2 printed139/PDF8: 73/211 comparison judgements flag omissions (35%), 89/211 factuality issues (42%). These are judgement counts, NOT 35/42% of 50 unique incidents.
- Table7 printed143/PDF12: 116/150 AI-assisted preferred,17/150 ties,17/150 human preferred. Table6 printed141/PDF10: editing easier36/75; time250 vs310 sec p=.208, not statistically supported speed gain.
- Same tickets and model for autonomous/assisted; human intervention is the treatment, not two autonomous LLM stages. Private Google incident tickets.

## AEC: read complete (8 pages, printed30880-30887)

- Guo, Wang, Zhang, Zhang, Kang, Tian and Yan. Extracting Events Like Code: A Multi-Agent Programming Framework for Zero-Shot Event Extraction. AAAI2026; DOI pending resolver. arXiv:2511.13118 is preprint version.
- Unstructured narrative text, five human-annotated event benchmarks INCLUDING CASIE. Retrieval self-generates examples (not external RAG) -> planning hypotheses -> code generation -> verification -> bounded patch/backtrack, k=t=3.
- PDF4/printed30883: trigger occurrence plus contextual similarity, datatype/schema/format validation. Semantic matcher implementation underspecified; cannot claim structural rules guarantee factual truth. No attached verbatim evidentiary quotes.
- PDF5/printed30884: same LLM/backbone/test split, three independent runs. 250 test instances per dataset, CASIE50 instances. TextEE protocol, not necessarily full-document case summarization.
- ALL baselines adapted to schema-conformant outputs with common Verification added if absent. DirectEE is a single-step core but overall evaluated pipeline is not clean unverified one-call. DirectEE has no argument scores.
- Table1 CASIE Llama3-8B EI DirectEE47.6/AEC55.7; AC GuidelineEE27.8/DecomposeEE25.1/AEC28.5. Llama3-70B EI62.4/65.9; AC31.6/31.9/33.9. Table2 GPT4o CASIE AC Guideline35.3/Decompose36.5/AEC37.8. Exact span/type/role micro F1, NOT CyberCase mention recall. AEC not uniformly best: 8B CASIE AI31.7 guideline versus30.7 AEC; GPT3.5 CASIE AC30.8 guideline versus26.7 AEC.
- This meets user's narrative + same-model workflow comparison + independent human gold criterion. MUST baseline for the extraction claim, with article-level adaptation and fair metric specified.
- Code https://github.com/UESTC-GQJ/AEC (redirect/access pending). Public benchmark availability varies by dataset (ACE licensed); CASIE public download does not settle licence.

## RAEE: read complete main and appendices (17 pages)

- Beyond Exact Match: Semantically Reassessing Event Extraction by Large Language Models, arXiv:2410.09418v2 (4March2025; first2024), Yi-Fan Lu et al. NOT the separate NAACL2025 BEMEAE paper. Venue pending.
- LLM judge precision/recall versus event annotation, meta-evaluation800 pieces/three humans excludes easy exact matches. Table1 p4 DeepSeek-R1 EAE precision agreement79.72% and recall93.49%; do not generalize agreement to all outputs.
- Section4/5 pp5-8 uses ten existing human-annotated datasets, including CASIE; reassesses eight fine-tuned extractors plus six LLMs. Table4 p7 CASIE PAIE argument F1 changes64.00 exact to87.78 semantic; Table7 p8 pooled GPT4o EAE15.89 exact/77.89 semantic. These are DIFFERENT metrics, not a model improvement. No single-versus-decomposed workflow experiment. Public RAEE toolkit is linked in PDF introduction; benchmark licences vary.
- Appendix Tables13-15 pp16-17 make role/event compatibility part of semantic criteria. Our mention matcher lacks these checks; relaxing span matching alone does not establish correct roles or negation.

## Air-gapped analysis: read complete body (25-page publisher PDF)

- Sunghun Jang, MyoungRak Lee, Taeshik Shon (2026). Local LLM-Based Cyber Incident Analysis in Air-Gapped Networks via Teacher-Student Knowledge Distillation and Agentic Orchestration. Electronics15(13):2949; DOI10.3390/electronics15132949; published6July2026, peer-reviewed journal.
- Input Sysmon/Windows/firewall telemetry; offline GPT4 teacher reasoning -> LoRA-distilled Llama3-8B -> normalization -> hybrid candidate filter -> inference/confidence -> report -> verification/HITL. Narrative CTI is a training source, not the principal evaluation input.
- Section3.3 p12 programmatic Traceability Matrix anchors EventID/timestamp/processID; missing anchors removed or audited. Section4.4 p16 uses learned FactCC-style factuality classifier. No verbatim quote occurrence algorithm described; anchor occurrence is not semantic support.
- Evaluation3500 author-generated Atomic Red Team scenarios, split2500/500/500 byAtomicTestID, labels inherited from attacks and teacher-generated reasoning. Not independent human-annotated narrative gold.
- Same distilled student and500 test cases for component ablations (Table13 p18): fullaccuracy88.4%/ATT&CKF1.91/hallucination6.2%; noagent74.2%/.72/18.5%; noverification86.1%/.88/14.1%. Shows same-model workflow/verification controls already exist. Table11 p17 cross-model results additionally conflate training and orchestration.
- Audit100 sentences/Table18 p22 reports6.2% hallucination,93.8% citation; denominator/rounding for6.2% on100 not explained. Cite reported figures with no independent numerical replication claim. Uncertain31/500 is a distinct endpoint even though6.2% also.
- Public Atomic Red Team source; processed scenarios/scripts only on request subject to institutional restrictions (Data Availability p24).

## Agentic traffic reports: read complete body and appendices (35 pages)

- Chia-Hong Chou, Arjun Sudheer, Younghee Park (2026). An LLM-Based Agentic Network Traffic Incident-Report Approach Towards Explainable-AI Network Defense. Journal of Sensor and Actuator Networks15(2):32; DOI10.3390/jsan15020032; published7April2026, peer-reviewed journal.
- 71-dimensional numeric flow features -> binaryRF -> ML ensembleRF/XGB/MLP -> SHAP -> Llama3.1-8B ReAct tools(Tavily/arXiv/Chroma) -> report with tool/query citations. No quoted source spans or deterministic quote binder.
- Section3.7.2 pp12-14/4.3 p23: same Llama3.1-8B judge family, custom RAGAS prompts, claim support score2 for faithfulness; sentence score>=1 for groundedness. 176/200 evaluated reports,24errors excluded. No independent human semantic gold; flow labels do not label report facts. No matched single/multi-stage or retrieval/SHAP ablation, explicitly future work pp29-30.
- Table7 p23: groundedness1.0000,faithfulness.6391; means judge decisions under thresholds, NOT proven zero hallucinations. Table5 p18 ensembleaccuracy99.7971%,RF99.8163%; classification accuracy is not report accuracy. Table6 p22 UDP F1.4828MLP/.9515ensemble.
- Public ACI IoT dataset IEEE DataPort DOI10.21227/qacj-3x32; report/reference/evaluator outputs release not specified.

## Shiri et al.: read complete (9-page arXiv manuscript; published venue verified)

- Decompose, Enrich, and Extract! Schema-aware Event Extraction using LLMs. FUSION2024, pp1-8, DOI10.23919/FUSION59988.2024.10706385; arXiv2406.01045v1 is manuscript read. Published author order differs from first-page preprint layout: use Crossref record.
- Narrative ACE05 sentence news, WikiEvents documents, synthetic MaritimeEvent. PromptED->promptEAE with schema-specific retrieved labelled demonstrations. No verbatim quote verification/report rendering.
- SectionVI-1 pp6-7 compares sameGPT3.5, sameACE data, samefive-shotRAE, withoutdecomp versusdecomposed. TableII p7 Arg-C45.43->50.07; Trigger69.19->74.55. The prose incorrectly mentions8.3triggergain: tabledifference5.36, don'trepeatincorrectarithmetic. WikiEvents comparison lackswithoutdecomp row.
- ACE human gold and single/multi-stage matched comparison, so ALSO meets baseline condition. Maritime goldLLMsynthetic; do not label wholeevaluationindependentgoldonly. CASIE not used in original paper, AEC later adapts.
- No original code or MaritimeEvent download link specified. ACElicensed; WikiEvents public.

## Quote-Tuning: read complete main and supplement (21 publisher pages)

- Jingyu Zhang, Marc Marone, Tianjian Li, Benjamin Van Durme, Daniel Khashabi (2025). Verifiable by Design: Aligning Language Models to Quote from Pre-Training Data. NAACL2025 Long,3748-3768, DOI10.18653/v1/2025.naacl-long.191. Published proceedings supersedes provisional preprint-only status above.
- Quote preference tuning uses DATA PORTRAITS Bloom-filter corpus membership of25-character ngrams, QUIP, then DPO. Deterministic approximate corpus membership, not an exact full-quote source-specific Binder; Bloom false positives possible. No incident narratives or reading/judgement ablation.
- Section2 p2 +Table2 p5 NQ QUIP34.9->54.5;Table4 p6 completion25.7->59.2. Goldforquotingcorpusoccurrence, NQhumananswers; TruthfulQAgenerativeendpoint GPTjudgestrainedonhumanlabels (AppendixC p16). Do not describe entireevaluationjudgefree.
- Limitations p10 quotes don't guarantee completeness/usefulness, symbolic source attribution futurework. Code https://github.com/JHU-CLSP/verifiable-by-design.

## Clinical quote evaluation: read complete main and methodological appendix (23 pages)

- Jiashuo Zhang, Yuling Chen, Yvonne Commodore-Mensah, Michael Oberst (2026). Verifiable by Construction: Claim-Level Evaluation of Verbatim Citation in Clinical Question Answering. arXiv2609.15964v2,17Sep2026, preprint.
- Four clinicalguidelines -> one sharedretrieval set ->12modelsanswer222syntheticquestionswithquotes -> deterministicexact/normalized/elided checks -> LLMclaimfilter andsemanticjudge. No workflowablation (Discussion p7).
- Section3.2 pp3-4/AppendixA.6 p13: EXACTcharacter match,normalizedUnicode/case/quotes/dashes/whitespaceandmarkup,orderedellipsisfragments>=10chars with>=2fragments. Very close to Binder verification; this is already known independently of cyber setting.
- Semanticgoldnotindependentpublicgold: GPT4ominiqueries and DeepSeekjudge, calibrated against70pairs labelledbytwocoauthors blinded tojudge; kappas .858/.810,HH.853 p5/AppendixA.13p16.
- Table1 p5 Opus5 98.0%ofclaimscarryverifiedquotes versus37.1%ofallclaimsstrictfullysupported; NOT98.0%VCR(thelatter100.0%Table2 p6). Quoteoccurrenceandclaimsupportedaredifferentmetrics. Code/data promised at https://github.com/oberst-lab/verifiable-by-construction; liveaccesspending.

## Fresh metadata receipts

- 2026-09-30 primary Crossref title queries verified AEC DOI10.1609/aaai.v40i37.40346, CadetDOI10.1145/3786335.3813136 (CAIS2026 proceedings103-123), and ShiriFUSION DOI. Cadet is a published conference paper, NOT merelyarxivpreprint; numeric locators refer to arxivv3 fulltext read.
- Local requests downloaded publisher Quote-Tuning and separate BEMEAE PDF; BEMEAE notyetread, do notuseasverifiedclaimsupport. PMC Relins request returned ananti-botpage165chars; UAS403; notfullaccess.

## Local experimental receipts (read, not rerun)

- main_20260929_233326_b2.md: single .667, single_late .688, two-stage .779. Published receipt table: late-single delta+.021 p=.5471; two-stage-late delta+.091 unadjusted p=.0468, Holm=.0936. Supersedes the earlier overprecise decimal transcription. This does NOT rule out field-order effects; residual multiplicity-adjusted evidence is weaker.
- report_fidelity/runs/main/summary.json: 30 selected,26 successfully traced; 26 traces x3 reports=78 reports per arm.585 distinct frozen trace claims x3=1755 claim-rendering instances. Deterministic585/585 per render,1755/1755 combined,26/26 identical across three renders; LLM0/26 identical,2/78 malformed.
- Same deterministic report receipt also source_ids1092/1728=.6319 and contradiction_sources0/3. Hence do NOT call all provenance preserved. Need inspect newer receipts for source-ID fixes.
- Held-out user-run currently produces main_20260930_020141.jsonl, completion UNCONFIRMED. Do not use interim metric or call replication successful.

## Dehing forensic reports: full author manuscript read (10 pages)

- Published DFDS2026 DOI10.1145/3785318.3785330, publisher pagination1-11. Publisher/university PDF403; full10-page author manuscript obtained from NFI's public repository Paper.pdf, with placeholder DOI in its header. Locators refer to this manuscript; never claim final publisher PDF read.
- Synthetic CrystalClear one case,171 conversations/seven devices/240681tokens; chunk-level summaries with exact TraceIDs -> LLM report synthesis. Source occurrence checker for IDs is code generated by an auxiliary prompt; semantic report/timeline scoring is LLM-assisted with manual checks, not a source-quote entailment guarantee.
- Section4.5 p5 says no manual correction of Gemini-generated gold; Section5 p6 describes validation against factual-case document. Regardless of wording, reference report is LLM-generated, not independent human argument annotations.
- Table3 p7: single Gemini reference14IDs, stagedGemini13/14(.93). Table4 p8: staged12correcttimelineevents/14reference,1missed,6wrong extra events; such counts use reference matching, not a frozen-trace deterministic renderer test.
- Same model appears as single reference versus staged output, but different-purpose reference creation is not a clean independent-gold workflow ablation. High forensic/stage-loss proximity, does not meet all three mandatory-baseline criteria.
- Public author code/prompts/dataset/output repo verified via GitHub API. Symposium publication verified Crossref/university; review protocol not independently inspected.

## Pending (supersedes older pending list)

- Seven requested and five closest added papers read. Relins remains abstract only, UAS not verified fulltext; separate BEMEAE downloaded but not used as read evidence.
- Eleven DOI metadata records freshly verified (Crossref7/DataCite4); arXiv API initial429/timeouts preserved in citation_lock_initial_attempt.json. Kramer publisher verification handled separately without inventing DOI/arxiv. Final key/link/hash checks pending.
