# Chat analysis contract

## Raw evidence input

Main Case Analysis receives:

- a rendered chronological packet of included user messages;
- the exact included `source_message_ids`;
- the projection SHA-256;
- the persisted external retrieval context and admitted MITRE table;
- optional question text for ordinary asks.

`raw_direct` is the only analysis input mode. No structured Case State or extraction payload is accepted.

## Output

The structured trace is `analysis_trace_v2` and binds:

- `analysis_mode`: `case_overview` or `question_answer`;
- `retrieval_context_id`;
- `evidence_sha256`;
- validated claims;
- candidate-only MITRE associations.

A reported claim must cite one or more allowed `source_message_ids`. Analytical inferences remain explicitly typed. MITRE associations may reference only technique IDs admitted by the exact persisted retrieval table and cannot be labeled confirmed.

Validation rejects obsolete Case State, entity, relationship, evidence-item, and timeline-item reference keys.

## Action semantics

- First message: incident evidence and fresh RAG.
- Clarification answer: incident evidence and fresh RAG over accumulated evidence.
- `add_case_info`: incident evidence and fresh RAG over accumulated evidence.
- `ask`: excluded from incident evidence; reuses latest completed `RagContext`; no RAG call.

The action is persisted as message metadata. A clarification answer is recognized from the thread's awaiting-follow-up state and the prior assistant clarification metadata.

## Trust boundary

RAG output, MITRE ATT&CK descriptions, assistant prose, and model knowledge are analytical context only. They never become reported incident evidence or source-message provenance.
