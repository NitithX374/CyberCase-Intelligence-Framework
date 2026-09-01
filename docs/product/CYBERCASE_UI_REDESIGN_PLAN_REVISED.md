# CyberCase UI Redesign Plan

Status: revised after source-code audit  
Baseline: `main` at `58f2302`, dirty working tree, 2026-09-01  
Scope: frontend product architecture and interaction design; no implementation in this document

## 1. Product outcome

CyberCase should feel like an evidence-grounded case review workspace with an optional inquiry assistant, not a chatbot with several reporting tabs.

The primary experience is:

1. Submit and review case material.
2. Read a domain-neutral case dossier.
3. Resolve one focused clarification when useful.
4. Inspect the source material behind each finding.
5. Use optional cyber threat context only when the case supports it.
6. Generate a provisional report.

## 2. Verified current-system constraints

The redesign must be based on these live contracts:

- A new case is currently an empty chat thread followed by a separate initial evidence message. `POST /api/v1/chats` creates the thread; `POST /api/v1/chats/{thread_id}/messages` accepts the narrative and returns HTTP 202 with a message and run. The frontend then polls the thread and run.
- User-message semantics are stateful. The first message is the initial narrative. While awaiting clarification, the next message is a clarification answer. After analysis is answered, the request must explicitly choose `ask` or `add_case_info`.
- Only the initial narrative, clarification answers, and added case information are authoritative case evidence. Analyst questions, assistant output, RAG, and MITRE are not evidence.
- `analysis_trace_v3` exposes a summary, claims, supporting and contradicting source-message IDs, structured gaps, optional MITRE associations, and validation metadata.
- A `reported` claim means that a source reported the assertion. It is not independently confirmed or proven.
- Current source provenance is message-level. The system cannot truthfully claim that a finding is supported by a particular PDF page or bounding box.
- Current OCR intake supports one reviewed document-derived narrative. It persists bounded document provenance and quality metadata with the submitted narrative, but it does not persist a reusable document object or file library.
- Reports are `preliminary_analysis_report_v1` with status `provisional_unverified`. They are not official reports or legal determinations.
- MITRE is gated optional external context. General case analysis must remain useful when MITRE is irrelevant, unavailable, or returns no context.

## 3. Audit decision

### Keep from the supplied plan

- Make the dossier the primary surface.
- Put clarification beside the unresolved issue.
- Separate inquiry from evidence submission.
- Remove mandatory cyber language from general cases.
- Consume `analysis_trace_v3` directly.
- Use progressive disclosure for sources, reasoning, conflicts, and MITRE.
- Reduce persistent navigation complexity.

### Correct before implementation

1. Do not label `reported` as **Confirmed**. Use **Reported in case material**. Confirmation requires a product rule and evidence state the backend does not currently provide.
2. Do not call the generated PDF **official**. Use **Provisional case analysis report**.
3. Do not promise page-level citations, document counts, stored files, re-OCR, or document verification history. Those require durable document and excerpt models.
4. Do not present claim-array order as a chronology. `analysis_trace_v3` does not contain a timeline contract; the current “Attack Story” is an ordered list of claims, not verified event chronology.
5. Do not add a “Skip clarification” action unless its evidence semantics are defined. The supported action is an explicit answer such as “Unknown / not available,” submitted as the clarification response.
6. Do not add “Re-run analysis” unless a supported retry/re-analysis command exists. Current retries preserve an idempotency key for the same logical request.
7. Do not describe report generation as optional while the thread is `awaiting_followup`; the current frontend blocks generation in that state.
8. Do not say the initial message endpoint returns an `AnalysisTraceV3`. It returns an accepted message/run, and the frontend obtains the final trace by polling persisted thread state.
9. Remove prosecutor-specific and statutory language. The analysis contract prohibits guilt, prosecution, and legal conclusions.
10. Treat passing unit tests as regression evidence, not proof that the complete runtime is operational.

## 4. Simpler target architecture

Use three persistent case views and one utility surface:

| Surface | Purpose | Persistence |
|---|---|---|
| Case Dossier | Summary, findings, conflicts, gaps, clarification, optional MITRE | Existing messages and analysis metadata |
| Evidence & Sources | Authoritative user messages and available document-source quality metadata | Existing message metadata |
| Report | Provisional report generation, history, preview, and PDF download | Existing chat-report API |
| Ask about this case | Non-authoritative inquiry over current case context | Existing `ask` message path |

The new-case intake remains a full-page empty-thread state. It should disappear from persistent case navigation after initial evidence is submitted. This is smaller and safer than introducing a modal lifecycle immediately.

The inquiry utility may remain a dedicated screen during the first implementation slice. Convert it to an accessible drawer only after the contract repair and inline clarification are stable.

## 5. Interaction contract

### 5.1 New case

1. User selects **New case**.
2. Frontend creates an empty thread with the existing endpoint.
3. Full-page new-case view accepts a typed narrative or one OCR-reviewed narrative draft.
4. OCR text remains editable and displays confidence availability and warnings.
5. **Analyze case** submits the first authoritative message.
6. Frontend navigates to the dossier and polls until the persisted run reaches a terminal state.

Do not describe document preview as attached evidence before the user submits the narrative.

### 5.2 Ask about this case

- The inquiry composer is always labeled **Ask about this case**.
- Supporting text states: “Questions do not add or change case evidence.”
- It always sends `action: "ask"`.
- It must not accept uploads or present “paste incident logs” copy.

### 5.3 Add case information

- Use an explicit **Add case information** action in Evidence & Sources or the dossier header.
- Open a focused panel with a clear authoritative-evidence notice.
- In the first slice, support typed information only and send `action: "add_case_info"`.
- Adding another stored document is deferred until the backend owns multiple document records.

### 5.4 Clarification

- When `threadStatus === "awaiting_followup"`, render the active persisted question in an Actionable Clarification Card at the top of the dossier.
- Reuse `activeChatFollowUpForThread` and `followUpGapDetailForMessage` rather than inventing a second gap selector.
- Submit through the existing follow-up path so the answer retains its structural question linkage.
- Provide an explicit **Information not available** response that submits those exact user-authored semantics. Do not silently dismiss the question.
- Disable inquiry and evidence-add actions while the clarification answer is being submitted.

## 6. Case Dossier specification

### 6.1 Executive summary

- Show `AnalysisTraceV3.summary` directly.
- Use neutral wording: **Case summary · สรุปภาพรวมสำนวน**.
- Do not require cyber, attack, prosecution, or legal framing.

### 6.2 Key findings

Render claims as the main review structure. Preserve both `claim_type` and `epistemic_status`.

| Backend meaning | Primary label | Detail on expansion |
|---|---|---|
| `claim_type=reported`, `epistemic_status=reported` | Reported in case material | A supplied source states this; not independently confirmed |
| `claim_type=analytical_inference` | Analytical inference | Show qualified reasoning summary and supporting sources |
| `epistemic_status=contradicted` or contradicting IDs present | Conflicting evidence | Show supporting and contradicting sources separately |
| `not_established`, `not_confirmed`, `unknown`, or `suspected` | Not established / Unconfirmed | Explain the exact backend status in secondary detail |

Never collapse `reported` into **Confirmed**.

### 6.3 Source disclosure

- Source chips open the existing source-message inspector.
- Label the current precision honestly: **Initial narrative**, **Clarification response**, or **Additional case information**.
- If `document_sources` exists, show filename, extraction method, review status, confidence status, and warnings as provenance metadata.
- Do not display page numbers or source excerpts finer than the persisted message unless a future backend contract supplies them.

### 6.4 Open questions

- Project `analysis_trace_v3.gaps` directly.
- Show topic, status, why it matters, affected claims, priority, and whether it is askable.
- Merge the current “What Remains Unclear” and derived “Investigation Points” into one **Open questions & next evidence** section.
- Only the currently selected persisted clarification receives an inline answer control.

### 6.5 Event sequence

- Remove **Attack Story**.
- Do not create a timeline from claim-array position.
- Until a typed timeline contract exists, use an optional **Reported events** group without chronological claims, or omit this section entirely.

### 6.6 Optional technical enrichment

Drive visibility from persisted `mitre_applicability`, `rag_attempt`, validated associations, and MITRE table data.

| State | Dossier behavior |
|---|---|
| Gate skipped | Omit MITRE completely |
| Retrieval used with admitted associations | Show collapsed **External cyber reference** section |
| Applicable but no admitted association | Quiet note; general analysis remains complete |
| Retrieval unavailable | Non-blocking note that external cyber lookup was unavailable |

Every visible MITRE element must say **External reference — not case evidence**.

## 7. Evidence & Sources specification

The first implementation represents authoritative evidence messages, not a fictional document-management system.

Each row may show:

- Source type and message ordinal.
- Submission timestamp.
- Full user-authored content.
- Claims that cite the source at message level.
- Document-derived narrative metadata when present.
- OCR uncertainty and warnings when present.

Supported primary action: **Add case information**.

Deferred until a backend product decision:

- Multiple stored files per case.
- Original-file download or preview after submission.
- Page-level and bounding-box citations.
- Re-OCR and OCR version history.
- Human verification records.
- Document deletion, replacement, and chain-of-custody controls.

## 8. Report specification

- Title the surface **Provisional report · รายงานวิเคราะห์เบื้องต้น**.
- Preserve version history, deterministic generation, preview, and PDF download.
- Show a truthful readiness panel derived from existing state:
  - initial evidence exists;
  - validated case overview exists;
  - no run is processing;
  - no clarification is currently awaiting an answer;
  - thread is not failed.
- If clarification is active, link directly to the dossier card instead of calling it optional.
- Do not use “official,” “final determination,” “prosecution recommendation,” or equivalent language.

## 9. User-facing states

| State | Copy | Action |
|---|---|---|
| Empty thread | Start a new case | Enter or review the initial narrative |
| Processing | Analyzing case material… | View submitted material; no fake pipeline-step claims |
| Awaiting clarification | One clarification can improve this analysis | Answer in the dossier |
| Ready | Case dossier updated | Review findings, add information, ask, or open report |
| Optional RAG unavailable | External cyber reference was unavailable | Continue using evidence-grounded analysis |
| Trace unavailable | A narrative response is available, but structured findings could not be validated | Show safe response and supported retry guidance only |
| Request failed | Analysis could not be completed | Use the existing retry semantics and preserve idempotency |

## 10. Delivery phases

### P0 — Contract and trust repair

1. Make `case-overview.ts` recognize validated `analysis_trace_v3`.
2. Parse `supporting_source_message_ids`, `contradicting_source_message_ids`, `reasoning_summary`, and top-level `gaps`.
3. Delete markdown-section parsing from the v3 path; keep legacy parsing isolated to legacy traces only.
4. Replace **Established/Confirmed** language with truthful claim labels.
5. Stop deriving chronology from claim order.
6. Replace always-on MITRE loading and helper copy with domain-neutral language.

Acceptance:

- A persisted validated v3 overview renders without regex parsing.
- Supporting and contradicting sources remain distinct.
- A reported allegation is never presented as confirmed fact.
- A non-cyber case contains no visible MITRE label when the gate skipped.

### P1 — Action placement and navigation

1. Add an inline clarification card that reuses the existing follow-up selector and submission path.
2. Make inquiry explicitly non-authoritative.
3. Move add-information into an explicit evidence action.
4. Reduce persistent case navigation to Dossier, Evidence & Sources, and Report.
5. Keep the intake view only for an empty/new case.
6. Demote technical context into the conditional dossier section.

Acceptance:

- Users never choose evidence semantics with adjacent radio pills.
- Clarification can be answered without leaving the dossier.
- Ask cannot mutate the evidence snapshot.
- Add case information always triggers canonical re-analysis.
- Existing `/api/v1/chats` and report routes remain unchanged.

### P2 — Progressive disclosure and responsive utility UI

1. Add expandable finding details for reasoning and source conflicts.
2. Improve source inspector accessibility: focus containment, focus restoration, keyboard navigation, and responsive behavior.
3. Convert inquiry into a global drawer only if usability testing supports it.
4. Add report-readiness explanations using existing state.

### P3 — Document platform expansion

Only after an explicit backend/data-model decision, add `Case -> N Documents -> N extracted contents -> consolidated case representation`, durable file records, page-level citations, verification history, and reprocessing.

## 11. Actual frontend working set

Primary files for P0/P1:

- `frontend/src/lib/case-overview.ts`
- `frontend/src/lib/case-evidence.ts`
- `frontend/src/lib/chat-followup.ts`
- `frontend/src/components/common/types.ts`
- `frontend/src/features/chat/routing/chat-route.ts`
- `frontend/src/components/ChatWorkspace.tsx`
- `frontend/src/components/ChatWorkspaceLayout.tsx`
- `frontend/src/components/layout/WorkspaceSidebar.tsx`
- `frontend/src/components/overview/CaseOverviewView.tsx`
- `frontend/src/components/overview/EstablishedVsUnclearSection.tsx`
- `frontend/src/components/overview/AttackStoryTimeline.tsx`
- `frontend/src/components/overview/MitreExplainedSimply.tsx`
- `frontend/src/components/overview/SourceEvidencePopover.tsx`
- `frontend/src/components/conversation/ChatPanel.tsx`
- `frontend/src/components/conversation/ChatTranscript.tsx`
- `frontend/src/components/materials/CaseMaterialsView.tsx`
- `frontend/src/components/report/ChatReportView.tsx`

Likely new component:

- `frontend/src/components/overview/ClarificationActionCard.tsx`

No backend or `rag_service/**` change is required for P0/P1 if the UI stays within the verified contracts above.

## 12. Validation plan

### Automated

- Selector tests for native v3, legacy v2, invalid traces, missing sources, conflicts, and gaps.
- Component tests for empty, processing, awaiting clarification, ready, failed, RAG-skipped, RAG-unavailable, and cyber-context states.
- Integration tests proving `ask`, `add_case_info`, and follow-up submit distinct payloads and preserve evidence semantics.
- Route tests for all retained deep links and mobile navigation.
- Accessibility tests for dialog/drawer focus, labels, keyboard operation, and reduced motion.
- Full frontend tests, ESLint, TypeScript, and production build.

The existing stale TypeScript test fixtures must be repaired before claiming the frontend validation gate is clean.

### Manual browser scenarios

1. General theft case with no MITRE.
2. Financial fraud case with an active clarification.
3. Cyber case with admitted MITRE context.
4. Cyber case with optional RAG unavailable.
5. OCR-derived initial narrative with confidence unavailable and warnings.
6. Added case information followed by a revised dossier.
7. Analyst inquiry that leaves the evidence hash unchanged.
8. Mobile and keyboard-only navigation.

## 13. Non-goals

- No standalone case, upload, or report APIs.
- No change to authoritative evidence semantics.
- No legal conclusions or prosecution recommendations.
- No mandatory MITRE experience.
- No entity graph or giant knowledge graph UI.
- No internal hashes, retrieval IDs, provider scores, token counts, or raw failure codes in primary UI.
- No multi-document promise before durable document persistence exists.

## 14. Release verdict

Implement P0 before visual redesign. The largest current failure is not styling or tab count; it is that the frontend does not faithfully project the validated v3 evidence contract. After that trust repair, P1 is a bounded frontend-only reorganization over existing routes and persistence.
