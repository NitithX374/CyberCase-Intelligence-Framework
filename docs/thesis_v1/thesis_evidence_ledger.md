# Thesis Evidence Ledger

## วิธีอ่าน

- **VERIFIED** หมายถึงพบหลักฐานตรงใน current checkout หรือผลรันปัจจุบัน
- **PARTIAL** หมายถึงส่วนหนึ่งทำงาน แต่มีขอบเขตหรือ integration gap ที่ต้องกล่าวร่วมกัน
- **TODO** หมายถึงยังไม่มีหลักฐานพอและห้ามเขียนเป็นสิ่งที่เสร็จแล้ว
- หมายเลขบรรทัดมีโอกาสเปลี่ยนใน working tree จึงใช้ symbol และ commit เป็นหลัก

| ID | Claim | Chapter/section | Repository file / symbol / commit | Evidence type | Confidence |
|---|---|---|---|---|---|
| E01 | ระบบเป็น persisted chat application ที่มี thread, message, run, retrieval context และ report | 1.4, 3.5 | `backend/app/models/`; Alembic baseline `0001_raw_evidence_chat.py` | Code + migration | VERIFIED |
| E02 | browser ติดต่อ backend เท่านั้นใน workflow หลัก | 3.5 | `frontend/src/lib/api-client.ts`; backend route surface tests | Code + test | VERIFIED |
| E03 | ข้อความผู้ใช้แรกเป็น initial case narrative | 3.7 | `raw_evidence.py::build_raw_evidence_snapshot` | Code | VERIFIED |
| E04 | เฉพาะ clarification answer และ added case information ภายหลังถูกเพิ่มใน raw evidence | 3.7, 4.4 | `raw_evidence.py`; `chat/clarification_chain.py` | Code | VERIFIED |
| E05 | ข้อความผู้ช่วยและ user ask ทั่วไปไม่เป็น authoritative evidence | 1.4, 3.7 | `raw_evidence.py`; tests `test_chat_raw_pipeline.py` | Code + test | VERIFIED |
| E06 | evidence snapshot มี SHA-256 และ source message IDs | 3.7, 3.14 | `RawEvidenceSnapshot`; `raw_evidence.py` | Code | VERIFIED |
| E07 | fresh analysis เรียก RAG ก่อน Main Analysis | 3.6 | `workflow/pipeline_execution.py::_execute_fresh_analysis` | Code | VERIFIED |
| E08 | ask mode ใช้ analysis context ที่บันทึกไว้และไม่เรียก RAG ใหม่ | 3.6, 4.8 | `pipeline_execution.py::_execute_ask`; `outcome.py` metadata | Code | VERIFIED |
| E09 | Main Analysis v3 ใช้ prompt แบบ domain-neutral | 3.8, 4.5 | `case_analysis_prompt_config.py::CASE_ANALYSIS_TRUST_INSTRUCTIONS`; cross-domain tests | Code + test | VERIFIED |
| E10 | Main Analysis แยก reported, analytical inference และ unknown | 2.8, 3.8 | `contracts.py::ClaimType`; prompt instructions | Code | VERIFIED |
| E11 | v3 มี epistemic status หกค่า | 3.8 | `contracts.py::EpistemicStatus` | Code | VERIFIED |
| E12 | v3 claim เก็บ supporting และ contradicting source message IDs | 3.8, 4.6 | `contracts.py::AnalysisClaimV3` | Code | VERIFIED |
| E13 | inference ต้องมี supporting source และ reasoning summary | 3.8, 4.6 | `validation.py::validate_analysis_trace_v3` | Code + tests | VERIFIED |
| E14 | provenance ที่ผิดทำให้ analysis fail-closed | 3.8, 3.14 | `case_analysis_response_parser.py`; `validation.py`; structured-output tests | Code + tests | VERIFIED |
| E15 | ความล้มเหลวเชิงโครงสร้างบางชนิดอนุญาตให้คง visible prose พร้อม failure metadata | 3.8, 3.14 | `case_analysis_response_parser.py` | Code | VERIFIED |
| E16 | Provider output v3 ไม่สร้าง gap; backend สร้าง trace โดย `gaps=[]` | 3.8, 3.9 | `ProviderCaseAnalysisV3`; response parser | Code | VERIFIED |
| E17 | Gap Analysis เป็น LLM stage แยกจาก Main Analysis | 3.9, 4.7 | `followup/gap_analysis.py`; `prompts.py` | Code | VERIFIED |
| E18 | Gap taxonomy คือ NOT_PROVIDED, EXPLICITLY_UNKNOWN, AMBIGUOUS, CONFLICTING | 2.9, 3.9 | `followup/contracts.py::GapStatus` | Code | VERIFIED |
| E19 | follow-up policy เลือกคำถามสำคัญได้สูงสุดหนึ่งข้อในหนึ่ง decision | 3.9, 4.8 | `followup/policy.py`; `decision.py` | Code + tests | VERIFIED |
| E20 | EXPLICITLY_UNKNOWN ไม่ถูกถามซ้ำ | 3.9, 4.8 | policy prompt/guard; `test_chat_followup_policy.py` | Code + test | VERIFIED |
| E21 | จำนวน follow-up rounds สูงสุดปัจจุบันเป็น 2 | 3.9 | `backend/app/config.py::max_followup_rounds` | Configuration | VERIFIED |
| E22 | RAG/MITRE เป็น external technical context ไม่ใช่ evidence | 1.4, 3.7, 3.10 | analysis/follow-up prompts; association support role | Code + prompt | VERIFIED |
| E23 | RAG service รับ `/query` และคืน retrieval context กับ MITRE table โดยไม่คืน generated answer | 3.10 | `rag_service/app/routers/rag.py` | Code | VERIFIED |
| E24 | vector retrieval ใช้ BGE-M3 dense+sparse, RRF และ cross-encoder reranking | 2.4, 3.10 | `rag_service/.../retrieval/vector_retriever.py`; requirements | Code + config | VERIFIED |
| E25 | current hybrid path ขยาย Neo4j เพื่อนบ้านโดยตรง 1-hop | 2.5, 3.10 | `hybrid_retriever.py` direct incoming/outgoing neighbor query | Code | VERIFIED |
| E26 | main RAG flow ค้นภาษาต้นฉบับและไม่แปล input ทุกครั้ง | 3.10 | `agent_graph.py::_node_prepare` | Code | VERIFIED |
| E27 | ATT&CK data มาจาก STIX 2.1 Enterprise/Mobile/ICS assets | 2.6, 3.10 | ingestion/config paths; `Mitre_ATT&CK Doc/` | Data + code | VERIFIED |
| E28 | report ใช้ template deterministic ไม่เรียก LLM | 3.11, 4.10 | `report_generation.py::ReportGenerationService`; model=`template` | Code + tests | VERIFIED |
| E29 | report snapshot, version และ idempotency ถูกบันทึก | 3.11, 3.14 | `report_persistence.py`; `ChatReport` model; commit `cdb6697` | Code + history | VERIFIED |
| E30 | report validation จำกัด source IDs และ MITRE IDs ให้อยู่ใน snapshot ที่ยอมรับ | 3.11 | `report_validation.py` | Code + tests | VERIFIED |
| E31 | report reader ยังอ่าน claim source ผ่าน `source_message_ids` แบบ v2 | 4.10, 6.3 | `report_template.py::_extract_trace_claims` | Code | PARTIAL |
| E32 | frontend overview/technical context ยังอ่าน claim provenance แบบ v2 | 4.3, 6.3 | `frontend/src/lib/case-overview.ts`, `technical-context.ts`, `mitre-candidate.ts` | Code | PARTIAL |
| E33 | document ingestion รองรับ preview ของ PDF/DOCX/PNG/JPEG | 2.10, 4.4 | `routers/document_ingestion.py`; ingestion tests | Code + tests | VERIFIED |
| E34 | OCR ใช้ Typhoon ใน preview pipeline | 2.10, 4.4 | `TyphoonOcrAdapter`; config; requirements | Code + config | VERIFIED |
| E35 | HTR ถูกปิดและลายมือต้องตรวจด้วยคน | 2.10, 6.3 | ingestion recognizer/UI; tests | Code + UI | VERIFIED |
| E36 | ingestion output ยังไม่ persist และไม่เข้า analysis/RAG/MITRE | 4.4, 5.1 | ingestion route/UI/store; absence of workflow binding | End-to-end trace | VERIFIED |
| E37 | route surface ไม่มีกลุ่ม case/user/top-level report API | 1.4, 3.5 | `backend/app/main.py`; `routers/chat.py`; `test_route_surface.py` | Code + test | VERIFIED |
| E38 | ยังไม่มี authentication และ per-user ownership | 1.4, 6.3 | README, models, route dependencies | Code/docs | VERIFIED |
| E39 | Docker Compose เป็น development stack และไม่ใช่หลักฐาน production deployment | 4.1, 6.3 | `docker-compose.yml` dev target, reload/bind mounts | Configuration | VERIFIED |
| E40 | Backend test suite ปัจจุบันผ่าน 147 tests และ 2 subtests | 4.12, 5.4 | command run 2026-08-27 | Tool outcome | VERIFIED |
| E41 | Frontend ผ่าน 88 tests ใน 23 files และ ESLint ผ่าน | 4.12, 5.4 | command run 2026-08-27 | Tool outcome | VERIFIED |
| E42 | ไม่ได้รัน live E2E ในงาน thesis รอบนี้ | 5.4, 5.6 | execution log for this drafting task | Tool boundary | VERIFIED |
| E43 | representation pilot B0/B1/B2 ใช้ 28 English generation cases; B1 เหลือ 25 valid | 5.5 | `experiments/representation_analysis/outputs/pilot_28/report.md` | Executed artifact | VERIFIED |
| E44 | B3 pilot ได้ ROUGE-L 0.335292 และ SBERT 0.680145 บน 28 cases | 5.5 | `pilot_28_b3/report.md` | Executed artifact | VERIFIED |
| E45 | context refinement 28 cases มี SBERT 0.702320 แต่ทำ protected spans หาย 12/19 | 5.5 | ignored local `tmp/context_refinement_run_20260823/report.md` | Local exploratory artifact | PARTIAL |
| E46 | 50-case SEvenLLM pilot เปรียบเทียบโมเดลต่างสถาปัตยกรรม/ความสามารถ จึงเป็น confounded comparison | 5.5 | `pilot_1_en_50_report.md` | Executed artifact | VERIFIED |
| E47 | semantic verification 100 synthetic cases/800 pairs ตรวจ fixture integrity ไม่ใช่ model quality | 5.5 | `experiments/semantic_verification/reports/summary.md` | Executed artifact | VERIFIED |
| E48 | follow-up pilot มีเพียง synthetic M365 cases และพิสูจน์ workflow เท่านั้น | 5.5 | `experiments/followup_pilot/README.md` + result JSONs | Executed artifact | VERIFIED |
| E49 | ยังไม่มี prosecutor/expert user study หรือ legal correctness evaluation | 5.6, 6.3 | absence in inspected research/experiments + planning docs say no outcome | Repository audit | VERIFIED |
| E50 | proposed claim-evidence-gap review loop ยังไม่เป็น workflow เดียวครบวงจร | 3.8.x, 6.4 | v3 gap empty, separate follow-up gap, v2-shaped readers | Cross-layer audit | PARTIAL |
| E51 | Legal RAG อยู่นอกขอบเขตและไม่ถูก implement | 1.4, 6.4 | route/code search and project decision | Repository audit | VERIFIED |
| E52 | ชื่อไทย ชื่อนักศึกษา อาจารย์ และรูปแบบสถาบันยังต้องยืนยัน | Front matter | no source in repository | Missing metadata | TODO |
| E53 | ประสิทธิผลต่อเวลา/คุณภาพงานของอัยการหรือผู้สืบสวน | 5.6 | no user study | Missing evaluation | TODO |

