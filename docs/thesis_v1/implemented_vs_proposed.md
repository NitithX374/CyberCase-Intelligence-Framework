# Implemented vs Proposed Matrix

สถานะอ้างอิงจาก working tree วันที่ 27 สิงหาคม 2569 ซึ่งมีงานที่ยังไม่ commit จึงไม่ควรตีความว่าเป็น release ที่เผยแพร่แล้ว

| Feature | Current status | Repository evidence | Thesis section | Can be described as implemented? | Notes |
|---|---|---|---|---|---|
| Raw evidence reconstruction | IMPLEMENTED | `backend/app/services/chat/raw_evidence.py::build_raw_evidence_snapshot` | 3.7, 4.4 | Yes | รับเฉพาะ initial narrative, clarification answer และ added case information จากผู้ใช้ |
| Main Case Analysis | IMPLEMENTED IN WORKING TREE | `case_analysis_executor.py`, `case_analysis_prompt_config.py` | 3.8, 4.5 | Yes, with status qualifier | provider-backed one-call structured analysis; work remains uncommitted |
| AnalysisTrace v2 | IMPLEMENTED/LEGACY READER CONTRACT | `contracts.py::AnalysisTraceV2`, `compatibility.py` | 3.8, 4.6 | Yes | ยังมีผู้อ่านใน frontend/report ที่ผูกกับ v2 |
| AnalysisTrace v3 | IMPLEMENTED IN WORKING TREE | `contracts.py::AnalysisTraceV3`, `validation.py::validate_analysis_trace_v3` | 3.8, 4.6 | Yes, with status qualifier | backend main analysis produces v3; cross-layer adoption incomplete |
| Source provenance | IMPLEMENTED, INTEGRATION PARTIAL | v3 claim source fields, `validation.py`, `raw_evidence.py` | 3.7, 4.6 | Yes, with limitation | message-level; frontend/report v2-shaped fields can lose claim-level v3 links |
| MITRE RAG | IMPLEMENTED, CYBER-SPECIFIC | `rag_service/app/routers/rag.py`, `hybrid_retriever.py`, `vector_retriever.py` | 3.10, 4.9 | Yes | external context only; not general-case ontology |
| Gap Analysis | IMPLEMENTED AS SEPARATE STAGE | `backend/app/services/followup/gap_analysis.py`, `prompts.py` | 3.9, 4.7 | Yes | gap data persists under `chat_followup`; v3 trace `gaps` remains empty in main parser |
| Follow-up | IMPLEMENTED | `followup/decision.py`, `policy.py`, workflow pipeline | 3.9, 4.8 | Yes | at most one question per decision; bounded by configured rounds |
| Explicitly Unknown handling | IMPLEMENTED | `GapStatus.EXPLICITLY_UNKNOWN`, policy guard | 3.9, 4.8 | Yes | non-askable; avoids repeating questions about stated unavailable information |
| Claim/Evidence Matrix | PARTIAL | v3 claim source arrays and validation | 3.8.x, 6.4 | Not as a complete UI/workflow | contract exists, dedicated matrix/review interface does not |
| General case analysis | IMPLEMENTED IN BACKEND WORKING TREE | domain-neutral prompt and cross-domain tests | 3.8, 4.5 | Yes, as ongoing generalization | cyber RAG still runs on fresh analysis; UI terms remain partly cyber-oriented |
| Contradiction review | PARTIAL | v3 `contradicting_source_message_ids`, `contradicted` status | 3.8.x, 4.6 | Only contract/validation | no complete reviewer workflow for resolving contradictions |
| Report generation | IMPLEMENTED, V3 INTEGRATION PARTIAL | `reports/report_generation.py`, `report_template.py`, `report_persistence.py` | 3.11, 4.10 | Yes, with limitation | deterministic, versioned, idempotent; claim source reader still expects v2 field |
| PDF/document ingestion | IMPLEMENTED AS PREVIEW ONLY | `routers/document_ingestion.py`, `services/document_ingestion/` | 2.10, 4.4 | Yes, preview-only | PDF/DOCX/PNG/JPEG; no case persistence or analysis handoff |
| OCR | IMPLEMENTED AS PREVIEW | `TyphoonOcrAdapter`, ingestion route/config | 2.10, 4.4 | Yes, preview-only | full-page routed OCR; output is untrusted preview |
| HTR | NOT IMPLEMENTED | HTR recognizer and UI state return manual review/disabled | 2.10, 6.3–6.4 | No | handwriting requires manual review |
| Legal RAG | OUT OF SCOPE / NOT IMPLEMENTED | backend route surface and project decisions | 1.4, 6.4 | No | belongs to a separate product/research decision |
| Legal conclusions/guilt determination | OUT OF SCOPE | analysis prompt guardrails | 1.4, 3.7 | No | system is decision support only |
| User authentication/ownership | NOT IMPLEMENTED | README, models/routes | 1.4, 6.3 | No | current product is single-user local/development-oriented |
| Production deployment | NOT VERIFIED | development Docker Compose configuration | 4.1, 6.3 | No | no operational deployment evidence inspected |

