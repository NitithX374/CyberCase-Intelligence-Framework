# CyberCase backend ↔ frontend integration reference

Status: current checkout audit on 2026-09-10. This document describes the Case-first code present in the working tree; it does not claim that the working tree is clean or deployed.

## What this document covers

The documentation is consolidated into this single user-facing handoff. The generated symbol inventory remains a companion maintenance artifact so the exhaustive file/function coverage can be refreshed without hand-editing this narrative.

- This file explains the architecture, API boundaries, data authority, integration pipelines, and the role of each integration-bearing file.
- [`SYMBOL_INDEX.md`](SYMBOL_INDEX.md) is the exhaustive first-party inventory. It lists every discovered source file and every named function, class, interface, type, and enum, with source line, declared inputs, and declared output where the language exposes one.

The current generated inventory covers **673 first-party source files** and **3,307 named symbols**. The live checkout contains 200 Python files under `backend/app`, 11 Alembic Python files, and 190 application TypeScript/TSX/JavaScript files under `frontend/src` after excluding tests and generated declarations. Backend tests, frontend tests, research code, tooling, and the private RAG service are also present in the index, but they are not all application runtime paths.

Generated/vendor/build material is deliberately not treated as application source: `node_modules`, `.next`, Python environments, caches, and generated OpenAPI declarations are supporting artifacts. `rag_service/**` is documented here only at its backend boundary; it is a private service and is not a browser-facing API.

## Reading the file and function inventory

Every file entry in [`SYMBOL_INDEX.md`](SYMBOL_INDEX.md) has a generated `Purpose` line. Every named symbol has a source line plus `Receives` and `Sends` fields. Those fields are the declared type contract, not a promise that the function has no side effects. Database writes, network calls, cache updates, navigation, background-task scheduling, and UI rendering are described in the integration sections below.

Use the following order when tracing a change:

1. Find the file in the index and read its `Purpose`.
2. Find the symbol and note its declared input/output.
3. Follow the integration references in this guide to the caller, callee, persistence boundary, and frontend consumer.
4. Confirm runtime registration: an import or helper test alone does not prove that a Next.js route or FastAPI route is live.

The index is intentionally generated from the current checkout. Re-run it after source changes:

```powershell
python docs/developer-handover/generate_symbol_index.py
```

## Source-of-truth documents

- Product direction: [`CURRENT_PROJECT_DIRECTION.md`](../research/CURRENT_PROJECT_DIRECTION.md)
- Long-running state and decisions: [`CONTINUITY.md`](../../CONTINUITY.md)
- Exhaustive file/function inventory: [`SYMBOL_INDEX.md`](SYMBOL_INDEX.md)
- Case-first migration and cutover receipt: [`CASE_FIRST_MIGRATION_AUDIT_2026-09-10.md`](CASE_FIRST_MIGRATION_AUDIT_2026-09-10.md)
- Existing handover context: [`README.md`](README.md)

The product contract is General Case Summarization and Grounded Analysis. Main Analysis is evidence-first and claim-anchored in its supported path. MITRE ATT&CK retrieval is conditional external technical augmentation, not incident evidence and not a prerequisite for a general case analysis or report.

## Visual overview

The diagrams are embedded in this document, so the architecture explanation and its visual references travel together. They use the repository’s warm dossier palette: oxblood for backend control, blue for durable evidence/state, and violet for optional external context. Each SVG has an accessible title and description.

### Backend/frontend architecture

<div style="overflow-x:auto;border:1px solid #d5cec1;background:#fcfaf5">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 760" width="1280" height="760" role="img" aria-labelledby="cc-arch-title cc-arch-desc">
  <title id="cc-arch-title">CyberCase backend and frontend architecture</title>
  <desc id="cc-arch-desc">The browser uses the Next.js workspace, which calls the authenticated FastAPI gateway. FastAPI checks session and ownership, persists through PostgreSQL, and starts a run workflow. The workflow may call configured language-model providers and the private RAG service. The browser has no direct path to the private RAG service.</desc>
  <style>
    .cc-zone{fill:#f6f3ea;fill-opacity:.35;stroke:#d5cec1;stroke-width:2}
    .cc-node{fill:#fcfaf5;stroke:#d5cec1;stroke-width:2}
    .cc-backend{stroke:#9a4438}
    .cc-evidence{stroke:#356c8a}
    .cc-external{stroke:#6654a3}
    .cc-zone-label{fill:#68645d;font:700 16px Georgia,serif;letter-spacing:1px}
    .cc-title{fill:#262522;font:700 18px Georgia,serif}
    .cc-copy{fill:#68645d;font:14px Arial,sans-serif}
    .cc-diagram-copy{fill:#68645d;font:14px Arial,sans-serif}
    .cc-connector{fill:none;stroke:#262522;stroke-width:2;marker-end:url(#cc-arch-arrow)}
    .cc-connector-evidence{stroke:#356c8a}
    .cc-connector-external{stroke:#6654a3}
    .cc-connector-return{stroke-dasharray:8 8}
    .cc-mask{fill:#fcfaf5}
    .cc-label{fill:#262522;font:12px Arial,sans-serif}
    .cc-rule{stroke:#9a4438;stroke-width:4}
    .cc-legend{fill:#e4ded2}
    .cc-legend-copy{fill:#262522;font:12px Arial,sans-serif}
  </style>
  <defs>
    <marker id="cc-arch-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
      <path d="M0 0 L8 4 L0 8 Z" fill="#262522"/>
    </marker>
  </defs>
  <path class="cc-connector" d="M208 308 V376"/>
  <path class="cc-connector" d="M328 434 H368 V268 H432"/>
  <path class="cc-connector" d="M512 316 V376"/>
  <path class="cc-connector" d="M688 316 V376"/>
  <path class="cc-connector cc-connector-evidence" d="M768 268 H888"/>
  <path class="cc-connector cc-connector-evidence" d="M768 420 H832 V300 H888"/>
  <path class="cc-connector" d="M768 472 H824 V434 H888"/>
  <path class="cc-connector cc-connector-external" d="M768 540 H840 V508 H1048"/>
  <path class="cc-connector cc-connector-external cc-connector-return" d="M1120 492 V604 H800 V460 H768"/>
  <rect class="cc-mask" x="224" y="328" width="112" height="24" rx="4"/>
  <text class="cc-label" x="232" y="344">renders workspace</text>
  <rect class="cc-mask" x="332" y="352" width="128" height="24" rx="4"/>
  <text class="cc-label" x="340" y="368">HTTPS + cookies</text>
  <rect class="cc-mask" x="520" y="328" width="112" height="24" rx="4"/>
  <text class="cc-label" x="528" y="344">authenticate</text>
  <rect class="cc-mask" x="676" y="328" width="104" height="24" rx="4"/>
  <text class="cc-label" x="684" y="344">dispatch run</text>
  <rect class="cc-mask" x="784" y="240" width="120" height="24" rx="4"/>
  <text class="cc-label" x="792" y="256">durable state</text>
  <rect class="cc-mask" x="784" y="376" width="136" height="24" rx="4"/>
  <text class="cc-label" x="792" y="392">run + context</text>
  <rect class="cc-mask" x="784" y="444" width="104" height="24" rx="4"/>
  <text class="cc-label" x="792" y="460">LLM call</text>
  <rect class="cc-mask" x="848" y="516" width="128" height="24" rx="4"/>
  <text class="cc-label" x="856" y="532">optional retrieval</text>
  <rect class="cc-mask" x="880" y="580" width="144" height="24" rx="4"/>
  <text class="cc-label" x="888" y="596">context returned</text>
  <rect class="cc-zone" x="56" y="144" width="304" height="448" rx="8"/>
  <rect class="cc-zone" x="400" y="144" width="424" height="448" rx="8"/>
  <rect class="cc-zone" x="856" y="144" width="368" height="448" rx="8"/>
  <text class="cc-zone-label" x="80" y="184">PUBLIC BROWSER ZONE</text>
  <text class="cc-zone-label" x="424" y="184">TRUSTED APPLICATION ZONE</text>
  <text class="cc-zone-label" x="880" y="184">DATA AND PRIVATE PROVIDERS</text>
  <rect class="cc-node" x="88" y="220" width="240" height="88" rx="8"/>
  <text class="cc-title" x="112" y="256">Browser / analyst</text>
  <text class="cc-copy" x="112" y="280">Cookie-authenticated UI user</text>
  <text class="cc-copy" x="112" y="300">submits narrative and actions</text>
  <rect class="cc-node" x="88" y="376" width="240" height="116" rx="8"/>
  <text class="cc-title" x="112" y="412">Next.js workspace</text>
  <text class="cc-copy" x="112" y="436">React Query cache + projections</text>
  <text class="cc-copy" x="112" y="460">intake, overview, report, chat</text>
  <text class="cc-copy" x="112" y="480">polls durable run state</text>
  <rect class="cc-node cc-backend" x="432" y="220" width="336" height="96" rx="8"/>
  <text class="cc-title" x="456" y="256">FastAPI /api/v1 gateway</text>
  <text class="cc-copy" x="456" y="280">auth, ownership, schemas, route contract</text>
  <text class="cc-copy" x="456" y="300">message acceptance and report access</text>
  <rect class="cc-node cc-backend" x="432" y="376" width="160" height="116" rx="8"/>
  <text class="cc-title" x="452" y="412">Auth +</text>
  <text class="cc-title" x="452" y="436">ownership</text>
  <text class="cc-copy" x="452" y="460">JWT / cookie</text>
  <text class="cc-copy" x="452" y="480">thread checks</text>
  <rect class="cc-node cc-backend" x="608" y="376" width="160" height="116" rx="8"/>
  <text class="cc-title" x="628" y="412">Run workflow</text>
  <text class="cc-copy" x="628" y="436">lease + evidence</text>
  <text class="cc-copy" x="628" y="460">analysis + follow-up</text>
  <text class="cc-copy" x="628" y="480">completion / recovery</text>
  <rect class="cc-node cc-evidence" x="888" y="220" width="304" height="96" rx="8"/>
  <text class="cc-title" x="912" y="256">PostgreSQL</text>
  <text class="cc-copy" x="912" y="280">users, threads, messages, runs</text>
  <text class="cc-copy" x="912" y="300">contexts, reports, leases, metadata</text>
  <rect class="cc-node cc-external" x="888" y="376" width="144" height="116" rx="8"/>
  <text class="cc-title" x="908" y="412">LLM</text>
  <text class="cc-title" x="908" y="436">providers</text>
  <text class="cc-copy" x="908" y="460">structured analysis</text>
  <text class="cc-copy" x="908" y="480">and answers</text>
  <rect class="cc-node cc-external" x="1048" y="376" width="144" height="116" rx="8"/>
  <text class="cc-title" x="1068" y="412">Private RAG</text>
  <text class="cc-copy" x="1068" y="436">conditional ATT&amp;CK</text>
  <text class="cc-copy" x="1068" y="460">external context only</text>
  <text class="cc-copy" x="1068" y="480">never case evidence</text>
  <line class="cc-rule" x1="88" y1="536" x2="328" y2="536"/>
  <text class="cc-diagram-copy" x="88" y="560">Boundary rule: browser requests terminate at FastAPI.</text>
  <text class="cc-diagram-copy" x="88" y="580">There is no browser-to-RAG route.</text>
  <rect class="cc-legend" x="56" y="640" width="1168" height="64" rx="8"/>
  <rect x="80" y="660" width="16" height="16" fill="#f6f3ea" stroke="#d5cec1" stroke-width="2"/>
  <text class="cc-legend-copy" x="104" y="672">UI / browser</text>
  <rect x="248" y="660" width="16" height="16" fill="#fcfaf5" stroke="#9a4438" stroke-width="2"/>
  <text class="cc-legend-copy" x="272" y="672">backend-owned control</text>
  <rect x="496" y="660" width="16" height="16" fill="#fcfaf5" stroke="#356c8a" stroke-width="2"/>
  <text class="cc-legend-copy" x="520" y="672">authoritative persistence</text>
  <rect x="752" y="660" width="16" height="16" fill="#fcfaf5" stroke="#6654a3" stroke-width="2"/>
  <text class="cc-legend-copy" x="776" y="672">optional external context</text>
  <line x1="1000" y1="668" x2="1048" y2="668" stroke="#6654a3" stroke-width="2" stroke-dasharray="8 8"/>
  <text class="cc-legend-copy" x="1064" y="672">returned context</text>
</svg>
</div>

### Message, worker, and persistence sequence

<div style="overflow-x:auto;border:1px solid #d5cec1;background:#fcfaf5">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 808" width="1280" height="808" role="img" aria-labelledby="cc-seq-title cc-seq-desc">
  <title id="cc-seq-title">CyberCase message integration sequence</title>
  <desc id="cc-seq-desc">The analyst submits a narrative through the Next.js client. FastAPI persists the message and run in PostgreSQL and returns a 202 response. A background worker claims the run, loads evidence, optionally calls language-model or RAG providers, persists the assistant outcome, and the Next.js client polls until the completed result is displayed.</desc>
  <style>
    .cc-lifeline{stroke:#d5cec1;stroke-width:2;stroke-dasharray:8 8}
    .cc-message{fill:none;stroke:#262522;stroke-width:2;marker-end:url(#cc-seq-arrow)}
    .cc-message-evidence{stroke:#356c8a}
    .cc-message-external{stroke:#6654a3}
    .cc-message-return{stroke-dasharray:8 8}
    .cc-header{fill:#fcfaf5;stroke:#d5cec1;stroke-width:2}
    .cc-header-backend{stroke:#9a4438}
    .cc-header-evidence{stroke:#356c8a}
    .cc-header-external{stroke:#6654a3}
    .cc-header-title{fill:#262522;font:700 15px Georgia,serif;text-anchor:middle}
    .cc-header-copy{fill:#68645d;font:12px Arial,sans-serif;text-anchor:middle}
    .cc-seq-mask{fill:#fcfaf5}
    .cc-seq-label{fill:#262522;font:12px Arial,sans-serif}
    .cc-seq-external-label{fill:#6654a3;font:12px Arial,sans-serif}
    .cc-activation{fill:#9a4438}
    .cc-activation-evidence{fill:#356c8a}
    .cc-fragment{fill:#f6f3ea;fill-opacity:.25;stroke:#6654a3;stroke-width:2;stroke-dasharray:8 8}
    .cc-fragment-label{fill:#6654a3;font:700 12px Arial,sans-serif;letter-spacing:1px}
    .cc-seq-legend{fill:#e4ded2}
    .cc-seq-legend-copy{fill:#262522;font:12px Arial,sans-serif}
  </style>
  <defs>
    <marker id="cc-seq-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
      <path d="M0 0 L8 4 L0 8 Z" fill="#262522"/>
    </marker>
  </defs>
  <line class="cc-lifeline" x1="112" y1="208" x2="112" y2="728"/>
  <line class="cc-lifeline" x1="344" y1="208" x2="344" y2="728"/>
  <line class="cc-lifeline" x1="576" y1="208" x2="576" y2="728"/>
  <line class="cc-lifeline" x1="808" y1="208" x2="808" y2="728"/>
  <line class="cc-lifeline" x1="1040" y1="208" x2="1040" y2="728"/>
  <rect class="cc-fragment" x="896" y="444" width="280" height="140" rx="4"/>
  <path class="cc-message" d="M112 256 H344"/>
  <path class="cc-message" d="M344 300 H576"/>
  <path class="cc-message cc-message-evidence" d="M576 344 H808"/>
  <path class="cc-message cc-message-return" d="M576 388 H344"/>
  <path class="cc-message" d="M344 432 H576"/>
  <path class="cc-message cc-message-evidence" d="M1040 476 H808"/>
  <path class="cc-message cc-message-external" d="M1040 520 H1096 V544 H1040"/>
  <path class="cc-message cc-message-evidence" d="M1040 564 H808"/>
  <path class="cc-message" d="M344 608 H576"/>
  <path class="cc-message cc-message-return" d="M576 652 H344"/>
  <path class="cc-message cc-message-return" d="M344 696 H112"/>
  <rect class="cc-seq-mask" x="128" y="232" width="168" height="24" rx="4"/>
  <text class="cc-seq-label" x="136" y="248">narrative + action</text>
  <rect class="cc-seq-mask" x="368" y="276" width="176" height="24" rx="4"/>
  <text class="cc-seq-label" x="376" y="292">POST message + key</text>
  <rect class="cc-seq-mask" x="600" y="320" width="168" height="24" rx="4"/>
  <text class="cc-seq-label" x="608" y="336">message + run commit</text>
  <rect class="cc-seq-mask" x="368" y="364" width="152" height="24" rx="4"/>
  <text class="cc-seq-label" x="376" y="380">202 accepted</text>
  <rect class="cc-seq-mask" x="368" y="408" width="152" height="24" rx="4"/>
  <text class="cc-seq-label" x="376" y="424">poll run / thread</text>
  <rect class="cc-seq-mask" x="824" y="452" width="160" height="24" rx="4"/>
  <text class="cc-seq-label" x="832" y="468">claim + load evidence</text>
  <rect class="cc-seq-mask" x="1056" y="508" width="112" height="24" rx="4"/>
  <text class="cc-seq-external-label" x="1064" y="524">LLM / RAG</text>
  <rect class="cc-seq-mask" x="824" y="540" width="144" height="24" rx="4"/>
  <text class="cc-seq-label" x="832" y="556">persist outcome</text>
  <rect class="cc-seq-mask" x="368" y="584" width="152" height="24" rx="4"/>
  <text class="cc-seq-label" x="376" y="600">poll again</text>
  <rect class="cc-seq-mask" x="368" y="628" width="168" height="24" rx="4"/>
  <text class="cc-seq-label" x="376" y="644">completed detail</text>
  <rect class="cc-seq-mask" x="128" y="672" width="184" height="24" rx="4"/>
  <text class="cc-seq-label" x="136" y="688">render projection</text>
  <text class="cc-fragment-label" x="916" y="468">OPTIONAL PROVIDER STAGE</text>
  <text class="cc-seq-external-label" x="916" y="488">Only after applicability</text>
  <rect class="cc-activation" x="336" y="296" width="16" height="96" rx="4"/>
  <rect class="cc-activation" x="568" y="296" width="16" height="96" rx="4"/>
  <rect class="cc-activation-evidence" x="800" y="336" width="16" height="32" rx="4"/>
  <rect class="cc-activation-evidence" x="800" y="556" width="16" height="32" rx="4"/>
  <rect class="cc-activation" x="1032" y="452" width="16" height="120" rx="4"/>
  <rect class="cc-header" x="48" y="144" width="128" height="64" rx="8"/>
  <text class="cc-header-title" x="112" y="172">Analyst</text>
  <text class="cc-header-copy" x="112" y="192">browser</text>
  <rect class="cc-header" x="280" y="144" width="128" height="64" rx="8"/>
  <text class="cc-header-title" x="344" y="172">Next.js</text>
  <text class="cc-header-copy" x="344" y="192">client</text>
  <rect class="cc-header cc-header-backend" x="512" y="144" width="128" height="64" rx="8"/>
  <text class="cc-header-title" x="576" y="172">FastAPI</text>
  <text class="cc-header-copy" x="576" y="192">gateway</text>
  <rect class="cc-header cc-header-evidence" x="744" y="144" width="128" height="64" rx="8"/>
  <text class="cc-header-title" x="808" y="172">PostgreSQL</text>
  <text class="cc-header-copy" x="808" y="192">durable state</text>
  <rect class="cc-header cc-header-external" x="976" y="144" width="128" height="64" rx="8"/>
  <text class="cc-header-title" x="1040" y="172">Run worker</text>
  <text class="cc-header-copy" x="1040" y="192">providers</text>
  <rect class="cc-seq-legend" x="48" y="752" width="1152" height="40" rx="8"/>
  <line x1="72" y1="772" x2="120" y2="772" stroke="#262522" stroke-width="2"/>
  <text class="cc-seq-legend-copy" x="136" y="776">request / command</text>
  <line x1="312" y1="772" x2="360" y2="772" stroke="#262522" stroke-width="2" stroke-dasharray="8 8"/>
  <text class="cc-seq-legend-copy" x="376" y="776">response / observation</text>
  <line x1="624" y1="772" x2="672" y2="772" stroke="#356c8a" stroke-width="2"/>
  <text class="cc-seq-legend-copy" x="688" y="776">durable evidence/state</text>
  <line x1="936" y1="772" x2="984" y2="772" stroke="#6654a3" stroke-width="2"/>
  <text class="cc-seq-legend-copy" x="1000" y="776">optional external context</text>
</svg>
</div>

## One-minute architecture

```text
Analyst browser
    ↓
Next.js workspace
    ↓ authenticated cookie requests
FastAPI /api/v1 gateway
    ├── session, Case and Chat ownership checks
    ├── PostgreSQL reads/writes
    ├── Case material/extraction/evidence admission
    └── background CaseRun workflow
             ├── immutable Case evidence snapshot
             ├── Main Case Analysis through configured LLM provider
             ├── optional MITRE applicability → private RAG service
             ├── clarification state and metadata
             └── AnalysisResult, lazy Chat publication, context, lease, and report inputs
    ↓
Next.js React Query cache and pure presentation projections
```

The browser does not call `rag_service` directly. The backend is the public API gateway, authenticated ownership boundary, PostgreSQL owner, document-ingestion orchestrator, and private-provider coordinator. The frontend renders persisted messages and metadata; it does not become a second analysis engine.

## Integration boundaries and authority

| Boundary | Data received | Data sent | Authority / rule |
| --- | --- | --- | --- |
| Browser → Next.js | User input, selected file, navigation events, persisted browser draft | React events and local state changes | Draft state is convenience state, not saved case evidence. |
| Next.js → FastAPI | Cookie credentials; JSON chat/thread/report requests; multipart document preview | Typed JSON, redirect navigation, or PDF blob | `frontend/src/lib/api-client.ts` and `frontend/src/lib/document-ingestion.ts` are the client transport boundary. |
| FastAPI → PostgreSQL | Authenticated user, Case, document, extraction, evidence, snapshot, CaseRun/result, clarification, Chat, context, and report operations | Durable rows and JSON metadata | PostgreSQL is the source of durable Case state and optional Chat/report history. Ownership is checked by the backend. |
| FastAPI → document providers | Uploaded bytes and selected ingestion mode | Untrusted `IngestedDocument` preview | Extraction prepares text; it does not persist case evidence or trigger analysis. |
| Run worker → LLM | Raw evidence snapshot, optional external context, mode, question, pinned pipeline | Structured analysis result or question answer | Learned output is accepted only through backend parsing and validation. |
| Run worker → private RAG | Evidence-bound technical request after applicability gate | Retrieval context and MITRE rows | RAG output is external context only; unavailable or invalid RAG degrades to no retrieval context. |
| Backend → Next.js | Case/material/evidence/snapshot/result/run/clarification data plus optional thread details and report contract | React Query caches and UI projections | The frontend may label, group, and link data, but must not upgrade uncertainty or provenance. |

### Durable data roles

| Record | Meaning | What it must not be used for |
| --- | --- | --- |
| `User` | Authenticated account identity and thread owner | Browser-only identity or an authorization guess. |
| `Case` | Canonical aggregate, evidence revision, latest successful result pointer, and ownership boundary | A mutable transcript or a substitute for immutable evidence snapshots. |
| `CaseDocument` / `DocumentExtraction` | Original bytes and untrusted extraction revisions | Automatically admitted evidence or a public file URL. |
| `EvidenceSource` / `EvidenceRevision` / `CaseEvidenceSnapshot` | Explicitly admitted evidence, exact provenance, and immutable analysis input | Assistant output, ordinary `ask`, external context, or reconstructed history. |
| `CaseRun` / `CaseAnalysisResult` | Case-owned idempotent execution, lease, immutable result, and pinned snapshot | A Chat message count or a mutable latest-transcript inference. |
| `CaseClarification` | Durable pending question and one-time answer admission state | Authoritative evidence before the answer is explicitly admitted. |
| `ChatThread` | Optional Case conversation container and transcript | The Case worker owner or a required prerequisite for analysis. |
| `ChatMessage` | Optional user interaction, clarification linkage, or persisted assistant result publication | Treating every user message as evidence. Ordinary `ask` messages are excluded from raw evidence. |
| `ChatRun` | Legacy unbound-chat compatibility execution, status, lease, error, and request payload | Ownership of Case analysis or a substitute for `CaseAnalysisResult`. |
| `RagContext` | Frozen optional retrieval context bound to the run that produced it | Incident evidence or a general-analysis admission gate. |
| Assistant `metadata_json` | Analysis trace, evidence/source IDs, follow-up, RAG status, applicability, and pipeline receipts | Unvalidated free text or a reason to infer missing facts. |
| `ChatReport` | Versioned deterministic report derived from a report snapshot | A new analysis engine or a trigger for another RAG call. |
| Browser local storage | Account-scoped drafts, route, ingestion preview state, and session-change signal | Durable case persistence, provenance, authorization, or recovery truth. |

### Evidence and provenance rule

The authoritative case material is the exact text in explicitly admitted `EvidenceRevision` rows. Initial narratives, reviewed document text, accepted clarification answers, and explicit Chat additions may create those rows through their respective Case workflows. Unreviewed extraction, ordinary analyst `ask` messages, assistant prose, model responses, MITRE rows, and RAG context are not admitted incident evidence. Document-derived page citations are accepted only when the submitted source contains a literal quote with valid hash/offset/page binding; otherwise the UI must use reviewed-narrative attribution rather than inventing a page.

## Public API contract

The backend is mounted under `/api/v1` in [`backend/app/main.py`](../../backend/app/main.py). It registers health, authentication, Case CRUD/material/evidence/snapshot/analysis/run/clarification/report routes, optional Case Chat, the compatibility chat/thread/run/report routes, and protected document-ingestion preview. Case analysis is Case-owned; Chat is loaded lazily for interaction and persisted assistant-result publication.

### Authentication routes

| Method and path | Receives | Sends / effect | Consumer |
| --- | --- | --- | --- |
| `GET /api/v1/auth/providers` | None | Configured OAuth provider names | `AccountForm` decides whether to enable Google/GitHub buttons. |
| `GET /api/v1/auth/login/{provider}` | Provider name | OAuth redirect and state cookie | `getOAuthLoginUrl` / browser navigation. |
| `GET /api/v1/auth/callback/{provider}` | OAuth `code` and `state` | Creates or resolves user, sets HTTP-only auth cookie, redirects to frontend | OAuth provider return path. |
| `GET /api/v1/auth/session` | Auth cookie if present | `UserRead` or `null`; no challenge for anonymous access | `useAuth`. |
| `GET /api/v1/auth/me` | Auth cookie or bearer token | `UserRead` or `401` | Direct profile reads. |
| `POST /api/v1/auth/register` | `RegisterRequest` | `UserRead`, sets session cookie | `AccountForm` register mode. |
| `POST /api/v1/auth/login` | `PasswordLoginRequest` | `UserRead`, sets session cookie | `AccountForm` login mode. |
| `POST /api/v1/auth/logout` | Auth cookie | Message and cookie clear | Sign-out confirmation handlers and `useAuth`. |
| `POST /api/v1/auth/dev-login` | `DevLoginRequest` | `AuthTokenResponse` and session cookie when development login is enabled | Local/test workflow only. |

Authentication is enforced by [`backend/app/services/auth/dependencies.py`](../../backend/app/services/auth/dependencies.py). The dependency accepts the bearer token or HTTP-only cookie, decodes the JWT, loads the `User`, and rejects missing/invalid sessions. Chat routes then pass the authenticated user ID into service ownership checks. The request guard also rejects unsafe cross-origin mutations and adds authentication-related response headers.

### Thread, message, run, and report routes

| Method and path | Receives | Sends |
| --- | --- | --- |
| `GET /api/v1/chats` | Authenticated user | `list[ChatThreadRead]` owned by that user. |
| `POST /api/v1/chats` | `{ "title": string }` | `ChatThreadRead`, status `201`. |
| `GET /api/v1/chats/{thread_id}` | Owned thread UUID | `ChatThreadDetail`, including ordered messages and optional retry request. |
| `PATCH /api/v1/chats/{thread_id}` | `{ "title": string }` | Updated `ChatThreadRead`. |
| `DELETE /api/v1/chats/{thread_id}` | Owned optional Chat UUID | `204`; deletes transcript-owned messages and legacy ChatRun data. Case history, CaseRun/result, snapshots, clarifications, and reports are retained; report thread linkage becomes null. |
| `POST /api/v1/chats/{thread_id}/messages` | `ChatMessageCreate` | Case-linked threads dispatch Case-owned analysis/ASK/add-info workflows; legacy unbound threads use `ChatRun`; response is `ChatMessageAccepted`, status `202`. |
| `GET /api/v1/chats/{thread_id}/runs/{run_id}` | Owned thread and run UUIDs | `ChatRunRead` with `queued`, `running`, `completed`, or `failed`. |
| `POST /api/v1/chats/{thread_id}/reports` | Optional `ChatReportCreate.idempotency_key` | Versioned `ChatReportRead`, status `201` or idempotent existing result. |
| `GET /api/v1/chats/{thread_id}/reports` | Owned thread UUID | Newest-first `list[ChatReportRead]`. |
| `GET /api/v1/chats/{thread_id}/reports/{report_id}` | Owned thread/report UUIDs | One `ChatReportRead`. |
| `GET /api/v1/chats/{thread_id}/reports/{report_id}/pdf` | Owned thread/report UUIDs | Validated PDF bytes with download filename. |

### Case-first aggregate and native analysis routes

`Case` is the canonical aggregate. A Case may have a lazily created primary ChatThread; when present, the thread shares the Case UUID to preserve existing interaction/report contracts. Case analysis and worker ownership do not depend on Chat. Case material, evidence, snapshot, run, clarification, and report APIs are consumed by the Case workspace.

| Method and path | Receives | Sends / effect | Current consumer |
| --- | --- | --- | --- |
| `GET /api/v1/cases` | Authenticated user | Owned `list[CaseRead]`. | `useCases` and Case workspace selection. |
| `GET /api/v1/cases/{case_id}` | Case UUID + authenticated owner | `CaseRead`, including derived processing/freshness state and nullable `chat_thread_id`. | Case workspace bootstrap. |
| `POST /api/v1/cases` | `{ "title": string }` | Creates a Case without requiring Chat; returns `CaseRead`, status `201`. | Case creation/intake. |
| `PATCH /api/v1/cases/{case_id}` | Case UUID + `{ "title": string }` | Updates Case title and a paired Chat title when present. | Case workspace title editing. |
| `DELETE /api/v1/cases/{case_id}` | Case UUID + authenticated owner | Deletes the Case aggregate and its owned history, status `204`. | Case deletion. |
| `POST /api/v1/cases/{case_id}/chat` | Case UUID + authenticated owner | Idempotently ensures the optional primary ChatThread. | Lazy Chat opening. |
| `GET /api/v1/cases/{case_id}/documents` / `POST .../documents` | Case ownership; multipart upload for POST | Original document metadata plus untrusted extraction revision. | Case materials workspace. |
| `POST /api/v1/cases/{case_id}/documents/{document_id}/admit` | Extraction revision ID | Explicitly admits an evidence source/revision. | Materials review/admission. |
| `GET/POST /api/v1/cases/{case_id}/evidence` and revision/archive routes | Typed evidence text/provenance | Lists or mutates admitted evidence revisions. | Materials/evidence state. |
| `POST /api/v1/cases/{case_id}/evidence/snapshot` / `GET .../snapshots/{snapshot_id}` | Case ownership | Builds or reads an immutable source manifest/input snapshot. | Analysis and citation resolution. |
| `POST /api/v1/cases/{case_id}/analysis` | Idempotency key and expected evidence revision | Queues a CaseRun without Chat or a user message, status `202`. | Case Analyze action. |
| `GET /api/v1/cases/{case_id}/analysis` / `GET .../runs/{run_id}` | Case/run ownership | Latest result with freshness or persisted run status. | Overview/polling. |
| `GET /api/v1/cases/{case_id}/clarifications` / `POST .../{clarification_id}/answers` | Case/question ownership | Durable question state and one-time answer admission/run. | Case and Chat follow-up. |
| `POST/GET /api/v1/cases/{case_id}/reports` and nested report/PDF routes | Selected result and idempotency key | Result/snapshot-bound report versions and PDF. | Case Report workspace. |

The implementation is distributed across [`backend/app/models/case.py`](../../backend/app/models/case.py), [`backend/app/models/case_materials.py`](../../backend/app/models/case_materials.py), [`backend/app/models/case_run.py`](../../backend/app/models/case_run.py), [`backend/app/routers`](../../backend/app/routers), [`backend/app/services/case_materials`](../../backend/app/services/case_materials), [`backend/app/services/workflow`](../../backend/app/services/workflow), and [`backend/app/services/reports`](../../backend/app/services/reports). Migrations `0005_case_domain` through `0010_preserve_chat_reports` are additive and were exercised on live and disposable PostgreSQL.

`ChatService` remains the compatibility facade. Its Case-linked message path delegates to Case Chat handling, while legacy unbound Chat uses the old ChatRun path. Chat deletion removes only optional transcript rows and never uses Chat as the Case deletion boundary.

### Message request and accepted response

`ChatMessageCreate` is the central frontend/backend contract:

```json
{
  "content": "The analyst-authored narrative or follow-up text",
  "idempotency_key": "browser-generated UUID retained for retry",
  "action": "ask",
  "document_sources": [
    {
      "document_id": "preview-id",
      "filename": "report.pdf",
      "extraction_method": "native_pdf",
      "page_count": 2,
      "verification_status": "native",
      "confidence_status": "not_applicable",
      "minimum_confidence": null,
      "warnings": [],
      "page_spans": [
        {
          "page_number": 1,
          "start_offset": 0,
          "end_offset": 120,
          "text_sha256": "64-lowercase-hex-character-document-text-hash"
        }
      ]
    }
  ]
}
```

The actual schema requires non-empty content and idempotency key, permits `action` `ask` or `add_case_info`, and permits at most one document source. On receipt, the backend validates the document source and persists the request before scheduling `process_chat_run`. The `202` response contains:

```json
{
  "message": "ChatMessageRead",
  "run": "ChatRunRead"
}
```

The frontend must treat this as accepted work, not as a completed answer. It uses the returned run ID to observe completion.

### Document preview route

`POST /api/v1/document-ingestion/preview` is protected by `get_current_user` at router registration. It receives a multipart `file`, query `mode` (`unified` or `routed`), optional compatibility `segmentation`, and optional case/idempotency headers. It sends an `IngestedDocument` preview containing document identity, extraction method, pages, merged text, routing summaries, confidence fields, regions, and warnings.

The preview is intentionally not a persistence or analysis endpoint. The frontend reviews the returned text, builds a `CaseNarrativeDocumentSource`, and includes that source only when the analyst submits the narrative. A preview can therefore exist in browser state without becoming a case message.

## End-to-end integration pipelines

### 1. Account bootstrap and route protection

| Stage | Frontend | Backend | Data handoff |
| --- | --- | --- | --- |
| Bootstrap | `Providers` mounts `AccountGate`; `useAuth` runs `getSession`. | `auth.get_session` uses `get_optional_user`. | Cookie → `UserRead | null`. |
| Auth route | `AccountForm` calls register/login or navigates to OAuth URL. | Password/OAuth router validates credentials/profile, creates user, and sets JWT cookie. | Form data/profile → user row + cookie. |
| Account partition | `useAuth` stores account ID/session-change marker; `useAccountState` prefixes local keys by account. | `User.id` scopes thread queries and mutations. | Account ID → cache/local-state partition and ownership filter. |
| Protected workspace | `AccountGate` redirects anonymous users to `/login` and remembers a safe route for authenticated users. | `get_current_user` rejects missing/invalid sessions. | Route intent is not authorization; backend remains authoritative. |

Important distinction: local route memory and the React Query cache help restore the interface, but a route containing a thread ID is not proof that the user owns that thread. Every chat/report request rechecks ownership in the backend.

### 2. Case workspace and lazy Chat composition

1. [`ChatWorkspace`](../../frontend/src/components/ChatWorkspace.tsx) detects Case-first routes through `chatRouteState` and keeps Case selection separate from legacy Chat selection.
2. [`useCaseWorkspaceQueries`](../../frontend/src/hooks/use-case-queries.ts) loads Case identity, documents, evidence, latest result, clarifications, and reports without requesting Chat messages.
3. [`CaseFirstIntakeView`](../../frontend/src/components/intake/CaseFirstIntakeView.tsx), [`CaseNativeMaterialsView`](../../frontend/src/components/materials/CaseNativeMaterialsView.tsx), and the native Overview/Report views consume those Case queries directly.
4. Opening the Chat panel calls `POST /cases/{case_id}/chat` only when needed, then loads the persisted transcript. Chat is not created by Case analysis and is not required for Overview.
5. [`useCaseRunPolling`](../../frontend/src/hooks/use-case-run-polling.ts) monitors the CaseRun while Chat polling remains isolated to the compatibility Chat path.

The Case-first data path is:

```text
useCases / getCase / Case workspace queries
        ↓
ChatWorkspace Case mode
        ├── CaseFirstIntakeView
        ├── CaseNativeMaterialsView
        ├── CaseOverviewView ← latest AnalysisResult + snapshot
        ├── CaseReportView ← selected result + snapshot
        └── optional Chat panel ← ensure Case Chat → persisted messages
```

The workspace does not infer analysis readiness from message count. A reload restores Case and run state from the backend even when Chat has never been opened.

### 3. Case materials, extraction and explicit admission

| Stage | Function/file | Receives | Sends |
| --- | --- | --- | --- |
| Select/upload | `CaseFirstIntakeView` and `CaseNativeMaterialsView` | Case ID and bounded browser `File` | Case document upload request. |
| Persist document | `add_case_document` → `CaseMaterialsService.add_document` | Original bytes, filename, MIME, hash | `CaseDocument` plus untrusted `DocumentExtraction` revision. |
| Review extraction | Existing ingestion preview components | Extraction text, pages, warnings, confidence | Analyst-visible review state; no automatic admission. |
| Admit | `POST /cases/{case_id}/documents/{document_id}/admit` or native evidence POST | Selected extraction revision or reviewed text | `EvidenceSource` and immutable `EvidenceRevision`; increments Case evidence revision. |
| Revise/archive | Case evidence revision/archive routes | Case-owned source ID and exact text | New immutable revision or non-destructive archive marker. |

Original bytes and extraction metadata are server-owned. A browser preview is not durable evidence, and extraction success does not start analysis. Every document/evidence access checks Case ownership and parent relationships.

### 4. Case analysis acceptance, worker execution and polling

| Stage | Owner | Input | Output / side effect |
| --- | --- | --- | --- |
| Request | Case Analyze action | Case ID, expected evidence revision, idempotency key | `POST /cases/{case_id}/analysis`, status `202`. |
| Enqueue | `enqueue_case_analysis` | Locked Case and admitted evidence | Immutable `CaseEvidenceSnapshot` plus queued `CaseRun`; no Chat/message required. |
| Claim | `claim_case_run` | CaseRun ID and worker ID | PostgreSQL row lock, lease, attempt increment, and `running` state. |
| Execute | `process_case_run` | Saved snapshot and pinned pipeline config | Main Case Analysis, optional technical augmentation, clarification decision, and outcome. |
| Complete | Case completion service | Validated outcome and lease owner | Append-only `CaseAnalysisResult`, optional clarification, one lazy ChatThread, one assistant publication, and completed CaseRun in one transaction. |
| Observe | `useCaseRunPolling` | Case/run IDs and selection guards | Case result/run cache refresh until completed/failed. |
| Recover | Case recovery worker | Expired/interrupted lease | Requeue/fail according to saved run identity; stale workers cannot publish. |

The client keeps one idempotency key across uncertain responses. A new Analyze request creates a new logical CaseRun; retry preserves the original snapshot and configuration. Browser cancellation stops polling only and does not cancel a backend run.

### 5. Native snapshot citations and source authority

`build_case_evidence_snapshot` is the authority boundary for Case analysis. It stores ordered source/revision IDs, exact admitted text, provenance hashes, input text, text hash, and manifest hash. `CaseRun.snapshot_id` and `CaseAnalysisResult.snapshot_id` pin that immutable input; the worker never rebuilds it from current materials.

The native Overview citation parser resolves typed evidence source revisions through the snapshot manifest and validates canonical manifest/input hashes before displaying page or narrative attribution. It never treats a Case evidence UUID as a `source_message_id`. Historical message/result formats are read only in their declared format; missing or invalid provenance fails closed to safe narrative attribution.

### 6. Main Case Analysis and optional RAG

`process_case_run` reads only the saved Case snapshot and pinned run configuration. It performs the configured Main Case Analysis and may invoke the existing conditional MITRE/RAG boundary. The result preserves the Case evidence hash, typed source/revision references, trace, pipeline receipt, and optional retrieval context. RAG remains external context and is not a report or evidence admission gate.

On success, the completion transaction stores the canonical `CaseAnalysisResult` first-class and then publishes its immutable answer copy as one assistant `ChatMessage` with `message_kind=analysis_result` and `analysis_result_id`. A clarification question is a separate message/state record and cannot replace the answer. Case Overview reads the result directly; Chat simply displays the persisted publication after it is lazily opened.

### 7. Clarification and ordinary ask

Clarification is Case-owned state. A generated question is persisted against its origin result and snapshot. An answer submitted from Case or Chat is admitted once as a new evidence revision only after explicit answer handling, then creates a new pinned CaseRun. Stale or superseded questions are rejected rather than attached to a different result.

An ordinary `ask` is optional Chat interaction. It creates a genuine user message and a CaseRun pinned to the selected result/snapshot, but it does not create a new canonical CaseAnalysisResult, update the latest pointer, or become evidence. Case Chat dispatch is mediated by the Case workflow; legacy unbound Chat remains on `ChatRun` compatibility behavior.

### 8. Case report generation and PDF export

New report generation is Case-scoped and reads the explicitly selected persisted result:

```text
GET Case + selected AnalysisResult
    ↓
build_case_report_snapshot
    ├── result-pinned evidence snapshot
    ├── validated AnalysisResult
    ├── optional bound RagContext
    └── typed evidence source/revision IDs
    ↓
run_report_generation
    ├── build_template_report
    └── validate structured report
    ↓
persist ChatReport with Case/result/snapshot bindings, version + idempotency key
    ↓
ChatReportRead → CaseReportView / persisted history
    ↓
optional PDF route → validate → render_chat_report_pdf
```

The report service does not call the LLM or RAG again. It is deterministic and template-first. The frontend keeps one idempotency key for one logical Generate Report operation, reads persisted Case history, and downloads the PDF as a `Blob`. Historical Chat reports remain readable through the compatibility routes; new reports cannot mix the current Case materials with an older result snapshot.

## Backend file map

This section documents why each backend application file exists and its integration handoff. The `Functions / symbols` column names the important entry points; the exhaustive source-line contract for every symbol, including private helpers and model fields, is in [`SYMBOL_INDEX.md`](SYMBOL_INDEX.md).

### Bootstrap, configuration, database, and migrations

| File | Why it exists | Receives | Sends / collaborates |
| --- | --- | --- | --- |
| [`backend/app/__init__.py`](../../backend/app/__init__.py) | Marks the backend package and defines its package surface. | Python imports. | Package resolution; no request data. |
| [`backend/app/config.py`](../../backend/app/config.py) | Composes database, CORS, auth, LLM, follow-up, analysis, report, and ingestion settings from environment configuration. | Environment variables and Pydantic field values. Key functions: `async_database_url`, `cors_origins_list`. | Typed `Settings` used by `main`, providers, routers, workers, and reports. |
| [`backend/app/database.py`](../../backend/app/database.py) | Creates the async SQLAlchemy engine/session and declarative base. | Database URL/settings; FastAPI dependency request lifecycle. Key function: `get_db`. | `AsyncSession` to routers/services; engine to lifespan and migrations. |
| [`backend/app/main.py`](../../backend/app/main.py) | Creates the FastAPI application, startup recovery, middleware, CORS, and route registration. Key function: `lifespan`. | Process settings, DB engine, router modules. | Public `/api/v1` ASGI application; startup health check, stale-run recovery, and recovery monitor. |
| [`backend/alembic/env.py`](../../backend/alembic/env.py) | Runs Alembic migrations in offline or async online mode. Key functions: `run_migrations_offline`, `do_run_migrations`, `run_migrations_online`. | Alembic config and database connection. | DDL migration execution; imports model metadata. |
| [`backend/alembic/baseline_versions/0001_raw_evidence_chat.py`](../../backend/alembic/baseline_versions/0001_raw_evidence_chat.py) | Creates the baseline chat, raw-evidence, run, and report-support tables. | Alembic connection. | Initial schema; `upgrade`/`downgrade` have no application payload. |
| [`backend/alembic/baseline_versions/0002_optional_report_retrieval_context.py`](../../backend/alembic/baseline_versions/0002_optional_report_retrieval_context.py) | Makes retrieval context optional for report persistence. | Alembic connection. | Schema alteration required for general analysis without MITRE context. |
| [`backend/alembic/baseline_versions/0003_user_oauth_and_thread_ownership.py`](../../backend/alembic/baseline_versions/0003_user_oauth_and_thread_ownership.py) | Adds users and thread ownership for authenticated workspaces. | Alembic connection. | `users` table and `chat_threads.user_id` ownership column/constraints. |
| [`backend/alembic/baseline_versions/0004_password_accounts.py`](../../backend/alembic/baseline_versions/0004_password_accounts.py) | Adds password-account storage to the user schema. | Alembic connection. | Password hash/account fields used by password auth. |
| [`backend/alembic/baseline_versions/0005_case_domain.py`](../../backend/alembic/baseline_versions/0005_case_domain.py) | Adds/backfills the first-class `cases` table and links each legacy chat thread by shared ID. | Alembic connection and existing `chat_threads` rows. | `cases` rows, indexes, title migration, and `chat_threads` foreign key; later additive migrations own native Case state. |
| [`backend/alembic/baseline_versions/0006_case_materials.py`](../../backend/alembic/baseline_versions/0006_case_materials.py) | Adds Case documents, extraction revisions, admitted evidence revisions, and immutable snapshots. | Alembic connection. | Native evidence/snapshot tables without Chat-created source IDs. |
| [`backend/alembic/baseline_versions/0007_case_runs_and_results.py`](../../backend/alembic/baseline_versions/0007_case_runs_and_results.py) | Adds Case-owned runs/results and assistant publication linkage. | Alembic connection. | CaseRun/result tables, nullable request linkage, and one-publication index. |
| [`backend/alembic/baseline_versions/0008_case_clarifications.py`](../../backend/alembic/baseline_versions/0008_case_clarifications.py) | Adds durable Case clarification questions and answer linkage. | Alembic connection. | Clarification state and CaseRun linkage. |
| [`backend/alembic/baseline_versions/0009_case_report_bindings.py`](../../backend/alembic/baseline_versions/0009_case_report_bindings.py) | Adds proven Case/result/snapshot bindings to existing reports. | Existing report/message/result rows. | Nullable bindings; unresolved historical rows remain explicitly unbound. |
| [`backend/alembic/baseline_versions/0010_preserve_reports_after_chat_delete.py`](../../backend/alembic/baseline_versions/0010_preserve_reports_after_chat_delete.py) | Makes optional Chat deletion non-destructive to frozen reports. | Existing report/thread relation. | `thread_id` nullable with `SET NULL`; Case/result/snapshot history remains. |

### ORM models

| File | Why it exists | Receives | Sends / collaborates |
| --- | --- | --- | --- |
| [`backend/app/models/__init__.py`](../../backend/app/models/__init__.py) | Imports/registers ORM models for metadata and relationship resolution. | Model imports. | Declarative metadata to SQLAlchemy/Alembic. |
| [`backend/app/models/case.py`](../../backend/app/models/case.py) | Defines the canonical `Case` aggregate and its optional one-to-one primary ChatThread relationship. | Case ID/title/user/timestamps, evidence revision, latest result, and related rows. | Case ownership, evidence/run/result/clarification relationships, and aggregate deletion boundary. |
| [`backend/app/models/case_materials.py`](../../backend/app/models/case_materials.py) | Defines original documents, extraction revisions, evidence sources/revisions, and immutable snapshots. | Case-owned material and provenance values. | Native evidence and snapshot rows consumed by analysis/citations/reports. |
| [`backend/app/models/case_run.py`](../../backend/app/models/case_run.py) | Defines CaseRun and immutable CaseAnalysisResult. | Case ID, snapshot, operation, lease, result, and pipeline metadata. | Case worker lifecycle and latest-result publication. |
| [`backend/app/models/case_clarification.py`](../../backend/app/models/case_clarification.py) | Defines durable Case clarification state. | Origin result/snapshot, gap/question, answer source/messages. | Case/Chat follow-up admission and retry linkage. |
| [`backend/app/models/user.py`](../../backend/app/models/user.py) | Defines the authenticated account and thread ownership relationship. | User identity, profile, OAuth/password fields, timestamps. | `User` rows and cascade relationship to `ChatThread`; consumed by auth dependencies and chat services. |
| [`backend/app/models/chat.py`](../../backend/app/models/chat.py) | Defines `ChatThread`, `ChatMessage`, and `ChatRun`. | Thread titles/status; message content/role/metadata; run payload/status/lease/idempotency fields. | Durable conversation and background execution state; relationships cascade from thread. |
| [`backend/app/models/rag_context.py`](../../backend/app/models/rag_context.py) | Defines the frozen retrieval context attached to a completed run. | Retrieval context ID, run/thread IDs, context text, MITRE table. | `RagContext` rows consumed by report snapshots and ordinary asks. |
| [`backend/app/models/report.py`](../../backend/app/models/report.py) | Defines versioned reports with optional legacy Chat linkage and Case/result/snapshot authority. | Frozen report snapshot, Case/result/snapshot IDs, structured report, status, validation, timing/token fields. | `ChatReport` rows serialized by Case or compatibility routes and rendered to HTML/PDF. |

### HTTP routers

| File | Why it exists | Receives | Sends / collaborates |
| --- | --- | --- | --- |
| [`backend/app/routers/__init__.py`](../../backend/app/routers/__init__.py) | Router package surface. | Router imports. | Modules imported by `main`. |
| [`backend/app/routers/health.py`](../../backend/app/routers/health.py) | Exposes service/database health. Key function: `health_check`. | DB dependency. | Health response for deployment/runtime checks. |
| [`backend/app/routers/auth.py`](../../backend/app/routers/auth.py) | Handles OAuth redirects/callbacks, session reads, logout, dev login, and provider discovery. Key functions: `oauth_login`, `oauth_callback`, `get_me`, `get_session`, `logout`, `dev_login`, `available_providers`. | Provider, OAuth code/state, request/response, DB, optional/current user, dev payload. | Redirects, `UserRead`, `AuthTokenResponse`, provider list, cookie mutation; calls auth service and OAuth adapters. |
| [`backend/app/routers/password_auth.py`](../../backend/app/routers/password_auth.py) | Handles email/password registration and login. Key functions: `register`, `login`, `start_session`. | `RegisterRequest` or `PasswordLoginRequest`, response, DB. | `UserRead` plus HTTP-only session cookie; calls scrypt password helpers and user persistence. |
| [`backend/app/routers/chat.py`](../../backend/app/routers/chat.py) | Compatibility Chat, legacy run, and chat-scoped report API. Key functions: `list_chat_threads`, `get_chat_thread`, `create_chat_thread`, `update_chat_thread`, `delete_chat_thread`, `create_chat_message`, `get_chat_run`, report handlers. | Authenticated user, UUIDs, typed request schemas, DB, `BackgroundTasks`. | Typed thread/message/run/report responses, `202` acceptance, `204` transcript deletion, PDF bytes; Case-linked messages dispatch Case workflows and legacy paths schedule `process_chat_run`. |
| [`backend/app/routers/cases.py`](../../backend/app/routers/cases.py) | Exposes canonical Case CRUD and lazy Chat creation. Key functions: `list_cases`, `get_case`, `create_case`, `update_case`, `delete_case`, `ensure_case_chat`. | Authenticated user, case UUID, `CaseCreate`/`CaseUpdate`, DB. | `CaseRead`, optional `ChatThreadRead`, or `204`; calls Case services. |
| [`backend/app/routers/case_materials.py`](../../backend/app/routers/case_materials.py) | Exposes Case document, extraction, evidence, archive, and snapshot operations. | Authenticated Case ID, upload, extraction/revision payloads. | Native Case material/evidence/snapshot contracts. |
| [`backend/app/routers/case_analysis.py`](../../backend/app/routers/case_analysis.py) | Exposes Case analysis acceptance, latest result, and run status. | Case ID, expected evidence revision, idempotency key. | `CaseRunRead`, `CaseAnalysisResultRead`, and background `process_case_run`. |
| [`backend/app/routers/case_clarifications.py`](../../backend/app/routers/case_clarifications.py) | Exposes durable Case clarification reads and answer admission. | Case/question IDs and answer payload. | Clarification plus CaseRun acceptance and background processing. |
| [`backend/app/routers/case_reports.py`](../../backend/app/routers/case_reports.py) | Exposes Case-scoped report and PDF access. | Case/result selection and report idempotency key. | Result/snapshot-bound `ChatReportRead` and PDF bytes. |
| [`backend/app/routers/document_ingestion.py`](../../backend/app/routers/document_ingestion.py) | Exposes protected, preview-only document extraction. Key functions: `_build_recognizer`, `_build_region_pipeline`, `_build_service`, `_read_limited`, `preview_document_ingestion`. | Authenticated request, bounded multipart file, mode/segmentation query, optional case/idempotency metadata. | `IngestedDocument` or typed HTTP error; calls parser/render/recognizer pipeline without persistence. |

### API schemas and cross-boundary contracts

| File | Why it exists | Receives | Sends / collaborates |
| --- | --- | --- | --- |
| [`backend/app/schemas/__init__.py`](../../backend/app/schemas/__init__.py) | Schema package surface. | Schema imports. | Shared Pydantic types to routers/services. |
| [`backend/app/schemas/cases.py`](../../backend/app/schemas/cases.py) | Defines case aggregate create/update/read API contracts. | Title, UUIDs, status, timestamps, paired `chat_thread_id`. | Strict `CaseRead` serialization for the standalone case router. |
| [`backend/app/schemas/auth.py`](../../backend/app/schemas/auth.py) | Defines `UserRead`, token response, dev-login, password-login, and registration payloads. | JSON request fields or ORM attributes. | Strict request validation and JSON response serialization for auth routes. |
| [`backend/app/schemas/chat.py`](../../backend/app/schemas/chat.py) | Defines thread, message, run, retry, and accepted-response contracts. | JSON content, idempotency key, action, document sources, thread/run IDs, ORM values. | Validation and serialization for the frontend transport; `ChatMessageAccepted` links persisted message to run. |
| [`backend/app/schemas/document_sources.py`](../../backend/app/schemas/document_sources.py) | Defines document identity, extraction confidence, warnings, and exact page-span provenance. Key validators: `validate_offsets`, `normalize_text`, `normalize_warnings`, `validate_confidence`. | Frontend document-source JSON. | Validated source metadata used by chat ingestion and citation binding. |
| [`backend/app/schemas/message_metadata.py`](../../backend/app/schemas/message_metadata.py) | Defines typed metadata shapes for actions, document sources, RAG, follow-up, and analysis. Key function: `serialize_message_metadata`. | Internal dictionaries assembled by workflow completion. | JSON-safe metadata stored on `ChatMessage.metadata_json`; consumed by frontend projections. |
| [`backend/app/schemas/rag.py`](../../backend/app/schemas/rag.py) | Mirrors the private RAG response contract and normalizes empty retrieval IDs. Key validator: `normalize_empty_retrieval_context_id`. | RAG JSON response. | `QueryRequest`/`QueryResponse`, MITRE rows, legal-reference metadata; strict `extra=forbid` protects the service boundary. |
| [`backend/app/schemas/reports.py`](../../backend/app/schemas/reports.py) | Defines structured seven-section report, claims, report-create idempotency, and report-read responses. Key validator: `normalize_idempotency_key`. | Snapshot-generated report objects and client idempotency key. | Typed report JSON consumed by report views and PDF route. |

## Backend authentication integration

| File | Function-level responsibility | Handoff |
| --- | --- | --- |
| [`backend/app/services/auth/auth_service.py`](../../backend/app/services/auth/auth_service.py) | `get_or_create_oauth_user` resolves provider subject/email identity; `get_or_create_dev_user` supports development/test identity; `build_auth_cookie_options` centralizes cookie policy. | OAuth profile/dev payload → `User` row and cookie options. |
| [`backend/app/services/auth/dependencies.py`](../../backend/app/services/auth/dependencies.py) | `_extract_token_from_request` reads bearer/cookie token; `get_optional_user` decodes and loads a user; `get_current_user` turns absent identity into `401`. | HTTP request → optional/required `User` dependency used by routers. |
| [`backend/app/services/auth/jwt.py`](../../backend/app/services/auth/jwt.py) | `create_access_token` signs user claims; `decode_access_token` verifies signature, expiry, and payload shape. | User ID/email or token string → signed token or validated claims. |
| [`backend/app/services/auth/oauth_clients.py`](../../backend/app/services/auth/oauth_clients.py) | OAuth adapter classes build authorization URLs and exchange provider codes for verified `OAuthUserProfile`; `get_oauth_client` selects provider. | Provider/state/code → verified profile. |
| [`backend/app/services/auth/passwords.py`](../../backend/app/services/auth/passwords.py) | Hashes and verifies passwords using the configured password algorithm. | Plain password / stored hash → encoded hash or boolean. |
| [`backend/app/services/auth/request_guard.py`](../../backend/app/services/auth/request_guard.py) | `guard_browser_request` protects unsafe browser mutations from cross-origin requests and adds auth cache/referrer headers. | ASGI request/response → guarded response or rejection. |

The frontend’s [`useAuth`](../../frontend/src/hooks/use-auth.ts) owns session observation and client cache cleanup, but not authorization. The backend cookie/JWT and ownership queries remain authoritative.

## Backend Case-first files

These files define the Case-owned path. The Chat package remains a compatibility interaction facade and is not the owner of native Case analysis.

| File | Why it exists | Receives | Sends / collaborates |
| --- | --- | --- | --- |
| [`backend/app/services/cases/__init__.py`](../../backend/app/services/cases/__init__.py) | Exports the case service/factory façade. | Internal imports. | `CaseService`, `serialize_case`, and `build_case_with_chat`. |
| [`backend/app/services/cases/case_factory.py`](../../backend/app/services/cases/case_factory.py) | Constructs one `Case` and one primary `ChatThread` with a shared UUID. Key function: `build_case_with_chat`. | Title and optional owner UUID. | Unsaved ORM pair added by chat/case services. |
| [`backend/app/services/cases/case_management.py`](../../backend/app/services/cases/case_management.py) | Owns Case CRUD, ownership verification, paired-thread title sync, and serialization. Key symbols: `CaseService`, `serialize_case`. | Async session, Case UUID, `CaseCreate`/`CaseUpdate`, owner UUID. | `CaseRead`; Case is the aggregate deletion boundary. |
| [`backend/app/services/case_materials/`](../../backend/app/services/case_materials/) | Persists original document bytes, extraction revisions, explicit evidence admission/revisions/archive, and immutable snapshots. | Case/material IDs, owner, exact text, provenance, extraction payload. | Native Case material/evidence/snapshot contracts; no automatic admission. |
| [`backend/app/services/workflow/case_run_service.py`](../../backend/app/services/workflow/case_run_service.py) | Owns CaseRun enqueue, currentness, result lookup, and Case-owned lease/recovery helpers. | Case ID, evidence revision, operation, idempotency/fingerprint. | Pinned CaseRun and CaseAnalysisResult lifecycle. |
| [`backend/app/services/workflow/case_run_completion.py`](../../backend/app/services/workflow/case_run_completion.py) | Atomically persists validated Case outcomes and optional Chat publication. | Claimed CaseRun, pinned snapshot, analysis outcome. | Append-only result, one assistant publication, clarification state, latest pointer. |
| [`backend/app/services/followup/case_clarification.py`](../../backend/app/services/followup/case_clarification.py) | Owns Case clarification listing and idempotent answer admission. | Case/question IDs, answer, authenticated owner. | Evidence revision and pinned follow-up CaseRun. |
| [`backend/app/services/reports/case_report_persistence.py`](../../backend/app/services/reports/case_report_persistence.py) | Generates/reads Case-scoped reports from selected result snapshots. | Case ID, result selection, report idempotency key. | Frozen Case/result/snapshot-bound report and PDF payload. |

The Case service is connected to `CaseRead`, `/cases` transport methods, and the native Case workspace. `ChatThreadRead` remains available for the optional transcript and compatibility route. A Case can be analyzed without opening Chat; Chat is ensured only when the analyst opens it or when a successful result is published.

## Backend case-analysis integration

The case-analysis package is a set of contracts and stages, not one monolithic endpoint. The worker invokes its public façade; the remaining files keep prompts, decoding, provenance, validation, pipeline selection, and claim-anchored work separable.

| File | Why it exists | Receives | Sends / collaborates |
| --- | --- | --- | --- |
| [`backend/app/services/case_analysis/__init__.py`](../../backend/app/services/case_analysis/__init__.py) | Stable package façade for analysis contracts, request execution, prompt helpers, state selection, and personalization. | Internal imports. | Public analysis symbols to workflow and tests. |
| [`backend/app/services/case_analysis/contracts.py`](../../backend/app/services/case_analysis/contracts.py) | Defines analysis modes, claims, citations, gaps, traces, failures, and provider result models. | Provider/backend dictionaries and typed field values. | Pydantic contracts used by executor, validators, workflow completion, and frontend metadata. |
| [`backend/app/services/case_analysis/citation_contracts.py`](../../backend/app/services/case_analysis/citation_contracts.py) | Defines citation/source binding structures and validation vocabulary. | Source IDs, quotes, page/span values. | Shared provenance types for parsing and trace validation. |
| [`backend/app/services/case_analysis/case_analysis_executor.py`](../../backend/app/services/case_analysis/case_analysis_executor.py) | Calls the configured core LLM or dispatches the claim-anchored service for `case_overview`. Key symbols: `MainCaseAnalysisService.analyze`, `request_case_analysis`. | Mode, raw evidence, optional analysis context, optional question, user message, optional HTTP client. | `CaseAnalysisResult`; provider request payloads never go directly to the frontend. |
| [`backend/app/services/case_analysis/case_analysis_prompt_builder.py`](../../backend/app/services/case_analysis/case_analysis_prompt_builder.py) | Builds the constrained prompt for case overview and question-answer modes. | Validated mode, raw evidence, analysis context, question, response language. | LLM prompt string; keeps evidence/context roles explicit. |
| [`backend/app/services/case_analysis/case_analysis_prompt_config.py`](../../backend/app/services/case_analysis/case_analysis_prompt_config.py) | Stores prompt/version/trust/task configuration and analysis failure type. | Settings and prompt constants. | Stable prompt instructions and failure codes to the executor. |
| [`backend/app/services/case_analysis/case_analysis_response_parser.py`](../../backend/app/services/case_analysis/case_analysis_response_parser.py) | Parses structured provider output into the internal analysis result. | HTTP/provider response, source IDs, context, mode, evidence hash. | Typed result or fail-closed analysis failure. |
| [`backend/app/services/case_analysis/case_analysis_response_utils.py`](../../backend/app/services/case_analysis/case_analysis_response_utils.py) | Extracts and normalizes provider response content before contract parsing. | Provider response content. | Normalized JSON/text pieces to the parser. |
| [`backend/app/services/case_analysis/evidence_quote_resolver.py`](../../backend/app/services/case_analysis/evidence_quote_resolver.py) | Resolves literal evidence quotes to deterministic text spans. | Evidence text and candidate quote. | Unique span or validation failure used by source binding. |
| [`backend/app/services/case_analysis/gap_assembly.py`](../../backend/app/services/case_analysis/gap_assembly.py) | Enriches analysis results with claim-linked gap state after the main trace. Key symbols: `assemble_claim_linked_gaps`, `enrich_case_analysis_result`. | Analysis result, gap stage, source IDs, MITRE table. | Canonicalized result used by follow-up evaluation and persistence. |
| [`backend/app/services/case_analysis/mitre_applicability_contracts.py`](../../backend/app/services/case_analysis/mitre_applicability_contracts.py) | Defines the applicability decision record and fail-closed skip result. | Provider decision fields and failure code. | `RETRIEVE`/`SKIP` contract consumed before RAG. |
| [`backend/app/services/case_analysis/mitre_applicability_gate.py`](../../backend/app/services/case_analysis/mitre_applicability_gate.py) | Runs the pre-retrieval technical applicability decision. | Evidence source IDs/content and configured LLM target. | Validated applicability record; provider failure is converted to `SKIP`. |
| [`backend/app/services/case_analysis/mitre_applicability_prompt.py`](../../backend/app/services/case_analysis/mitre_applicability_prompt.py) | Provides the fixed Thai/English applicability prompt and version. | Admitted evidence source descriptions. | Prompt input to the applicability provider. |
| [`backend/app/services/case_analysis/mitre_applicability_validation.py`](../../backend/app/services/case_analysis/mitre_applicability_validation.py) | Validates applicability provider output and required source attribution. | Raw applicability response. | Strict applicability record or rejection. |
| [`backend/app/services/case_analysis/personalization.py`](../../backend/app/services/case_analysis/personalization.py) | Resolves and validates the requested response language. Key symbols: `resolve_response_language`, `validate_response_language`. | User message metadata or configured language. | Supported language value used by prompt construction. |
| [`backend/app/services/case_analysis/pipeline_config.py`](../../backend/app/services/case_analysis/pipeline_config.py) | Defines the selectable analysis pipeline and reads a pinned run configuration. | Configuration dictionary or current settings. | `raw_direct` or `claim_anchored` pipeline contract used by claim and execution paths. |
| [`backend/app/services/case_analysis/response_decoder.py`](../../backend/app/services/case_analysis/response_decoder.py) | Decodes provider response payloads into a usable structured object. | Provider response. | Parsed payload for response parser/validation. |
| [`backend/app/services/case_analysis/response_identifiers.py`](../../backend/app/services/case_analysis/response_identifiers.py) | Validates and normalizes supported claim/MITRE identifiers. | Provider identifiers. | Finite identifiers for trace referential integrity. |
| [`backend/app/services/case_analysis/source_citations.py`](../../backend/app/services/case_analysis/source_citations.py) | Validates legacy source-message citation references and evidence bindings. | Historical trace citations, source IDs, evidence hash. | Declared historical citation structures or fail-closed errors. |
| [`backend/app/services/case_analysis/case_native_contracts.py`](../../backend/app/services/case_analysis/case_native_contracts.py) | Defines native Case result, typed source/revision citation, and snapshot-bound trace contracts. | Case evidence IDs, revisions, quotes, pages, trace fields. | Versioned native analysis structures with no message-ID substitution. |
| [`backend/app/services/case_analysis/case_native_analysis.py`](../../backend/app/services/case_analysis/case_native_analysis.py) | Executes native Case claim extraction/binding/selection/generation. | Saved Case snapshot context and pinned analysis configuration. | Validated Case trace and typed evidence references. |
| [`backend/app/services/case_analysis/case_native_validation.py`](../../backend/app/services/case_analysis/case_native_validation.py) | Validates native Case trace citations and snapshot/source consistency. | Native trace, admitted source registry, evidence hash. | Validated trace or fail-closed error. |
| [`backend/app/services/case_analysis/state_selector.py`](../../backend/app/services/case_analysis/state_selector.py) | Selects the latest validated legacy canonical `case_overview` where that historical format applies. | Historical message metadata, evidence hash, source-message IDs. | Declared legacy state for compatibility ASK/report readers. |
| [`backend/app/services/case_analysis/validation.py`](../../backend/app/services/case_analysis/validation.py) | Applies structural validation to analysis traces and result contracts. | Parsed result, source/context bindings. | Validated result or explicit failure; no semantic verification is claimed. |

### Claim-anchored subpackage

| File | Why it exists | Receives | Sends / collaborates |
| --- | --- | --- | --- |
| [`backend/app/services/case_analysis/claim_anchored/__init__.py`](../../backend/app/services/case_analysis/claim_anchored/__init__.py) | Stable façade for the opt-in claim-anchored implementation. | Internal imports. | Claim contracts and service symbols. |
| [`backend/app/services/case_analysis/claim_anchored/contracts.py`](../../backend/app/services/case_analysis/claim_anchored/contracts.py) | Defines extracted units, bound units, selected units, provider claims, and stage receipts. | Typed extraction/generation values. | Stage-to-stage contracts. |
| [`backend/app/services/case_analysis/claim_anchored/source_registry.py`](../../backend/app/services/case_analysis/claim_anchored/source_registry.py) | Registers immutable source text and source IDs for a run. | Raw evidence and source metadata. | Source registry used by binder and assembly. |
| [`backend/app/services/case_analysis/claim_anchored/binder.py`](../../backend/app/services/case_analysis/claim_anchored/binder.py) | Binds extracted units to unique literal evidence spans. | Units, source registry, evidence text. | Bound units or fail-closed binding error. |
| [`backend/app/services/case_analysis/claim_anchored/selector.py`](../../backend/app/services/case_analysis/claim_anchored/selector.py) | Applies deterministic coverage/token-budget selection. | Bound units and selection budget. | Selected units plus omission reasons/receipt. |
| [`backend/app/services/case_analysis/claim_anchored/prompts.py`](../../backend/app/services/case_analysis/claim_anchored/prompts.py) | Builds extraction and grounded-generation prompts. | Selected/bound units and analysis context. | Provider prompt payloads. |
| [`backend/app/services/case_analysis/claim_anchored/provider.py`](../../backend/app/services/case_analysis/claim_anchored/provider.py) | Calls the provider for decomposition and grounded generation. | Raw evidence, prompts, model/config, optional client. | Typed provider output and provider receipt. |
| [`backend/app/services/case_analysis/claim_anchored/assembly.py`](../../backend/app/services/case_analysis/claim_anchored/assembly.py) | Assembles validated generated claims into an analysis trace. | Selected units, generated claims, evidence/context bindings. | `AnalysisTraceV3` candidate. |
| [`backend/app/services/case_analysis/claim_anchored/service.py`](../../backend/app/services/case_analysis/claim_anchored/service.py) | Orchestrates extract → bind → select → generate → assemble for the opt-in path. Key symbol: `analyze_claim_anchored`. | Raw evidence, analysis context, user message, pipeline config, optional client. | `CaseAnalysisResult` with stage receipts and a trace candidate. |
| [`backend/app/services/case_analysis/claim_anchored/failure.py`](../../backend/app/services/case_analysis/claim_anchored/failure.py) | Normalizes bounded claim-pipeline failure codes and stage detail. | Stage errors. | Stable failure metadata to workflow completion. |

The frontend does not call any of these modules. It receives the persisted assistant message, `analysis_trace`, evidence IDs, source metadata, and optional RAG metadata after backend validation, then projects those fields into overview/materials/technical/report views.

## Backend chat-domain integration

| File | Why it exists | Receives | Sends / collaborates |
| --- | --- | --- | --- |
| [`backend/app/services/chat/__init__.py`](../../backend/app/services/chat/__init__.py) | Stable façade for thread, message, raw-evidence, provenance, retry, and pipeline configuration services. | Internal imports. | Symbols used by routers and workflow. |
| [`backend/app/services/chat/analysis_run_config.py`](../../backend/app/services/chat/analysis_run_config.py) | Pins legacy Chat analysis configuration and inherits it for compatibility clarifications. | Thread history, action, settings. | Legacy ChatRun payload consumed by `claim_run`. |
| [`backend/app/services/chat/chat_management.py`](../../backend/app/services/chat/chat_management.py) | Owns optional Chat transcript CRUD and user ownership filtering. Key class: `ChatService`. | Async session, thread UUID, title request, authenticated user ID. | Owned `ChatThread`/read models to router; deletion removes transcript/legacy ChatRun rows without deleting Case history. |
| [`backend/app/services/chat/chat_message.py`](../../backend/app/services/chat/chat_message.py) | Compatibility façade for message/run creation, lookup, and message reads. Key class: `ChatMessageService`. | Async session, thread/run IDs, message request. | Delegates creation to `chat_run_creation`; returns accepted/run/message records. |
| [`backend/app/services/chat/chat_run_creation.py`](../../backend/app/services/chat/chat_run_creation.py) | Atomically turns an accepted request into a persisted user message and queued run. Key symbols: `request_fingerprint`, `create_message_and_run`. | Session, thread UUID, `ChatMessageCreate`. | Idempotent message/run rows, action/evidence classification, pinned payload, processing status. |
| [`backend/app/services/chat/chat_run_retry.py`](../../backend/app/services/chat/chat_run_retry.py) | Reconstructs a safe retry request for an interrupted/failed run. | Thread detail/history and run metadata. | `ChatRetryRequest` used by frontend retry UI. |
| [`backend/app/services/chat/clarification_chain.py`](../../backend/app/services/chat/clarification_chain.py) | Reconstructs question/answer exchanges from message metadata and ordinals. | Historical messages and follow-up root ordinal. | Clarification chain for fresh analysis and follow-up policy. |
| [`backend/app/services/chat/document_provenance.py`](../../backend/app/services/chat/document_provenance.py) | Validates document source hashes/spans and retains only safe continuous provenance. | Narrative content and `CaseNarrativeDocumentSource`. | Validated document context or safe fallback attribution; never fabricates page data. |
| [`backend/app/services/chat/raw_evidence.py`](../../backend/app/services/chat/raw_evidence.py) | Builds and loads the authoritative raw-evidence snapshot. Key symbols: `RawEvidenceSnapshot`, `build_raw_evidence_snapshot`, `load_raw_evidence_snapshot`. | Message history, thread ID, optional ordinal cutoff. | Evidence text, source message IDs, document context, SHA-256 hash. |

## Backend document-ingestion integration

| File | Why it exists | Receives | Sends / collaborates |
| --- | --- | --- | --- |
| [`backend/app/services/document_ingestion/__init__.py`](../../backend/app/services/document_ingestion/__init__.py) | Stable façade for ingestion contracts, limits, service, and error types. | Internal imports. | Symbols used by the ingestion router. |
| [`backend/app/services/document_ingestion/contracts.py`](../../backend/app/services/document_ingestion/contracts.py) | Defines ingestion modes, pages, regions, confidence, routing, and preview output. | Parser/recognizer values. | `IngestedDocument` and nested typed records. |
| [`backend/app/services/document_ingestion/detection.py`](../../backend/app/services/document_ingestion/detection.py) | Detects supported media type from bytes/name. | Uploaded bytes and filename. | Document type decision for parser/render route. |
| [`backend/app/services/document_ingestion/errors.py`](../../backend/app/services/document_ingestion/errors.py) | Defines bounded ingestion error codes/messages. | Validation/provider/limit failures. | `DocumentIngestionError` mapped to HTTP status. |
| [`backend/app/services/document_ingestion/service.py`](../../backend/app/services/document_ingestion/service.py) | Orchestrates detection, native parsing, rendering, recognition, and preview assembly. | Bytes, filename, mode, configured limits/pipeline. | Untrusted `IngestedDocument`; no DB or analysis call. |
| [`backend/app/services/document_ingestion/provenance.py`](../../backend/app/services/document_ingestion/provenance.py) | Computes page/text hashes and provenance values for preview output. | Page text and document identity. | Hashes consumed by frontend source binding and backend validation. |
| [`backend/app/services/document_ingestion/rendering.py`](../../backend/app/services/document_ingestion/rendering.py) | Renders PDF/image pages for recognition when native text is unavailable. | Document bytes, media type, render limits. | Page images/recognition inputs. |
| [`backend/app/services/document_ingestion/recognized_region.py`](../../backend/app/services/document_ingestion/recognized_region.py) | Defines normalized recognized-region data. | Provider region/word values. | Region records used by merge and preview contracts. |
| [`backend/app/services/document_ingestion/region_pipeline.py`](../../backend/app/services/document_ingestion/region_pipeline.py) | Runs segmentation and recognition across regions. | Page images, segmenter, router, OCR/HTR recognizers. | Recognized regions and routing warnings. |
| [`backend/app/services/document_ingestion/merge/__init__.py`](../../backend/app/services/document_ingestion/merge/__init__.py) | Merge package surface. | Internal imports. | Reading-order helpers. |
| [`backend/app/services/document_ingestion/merge/reading_order.py`](../../backend/app/services/document_ingestion/merge/reading_order.py) | Merges recognized regions into readable page text. | Region boxes/text. | Ordered page text and merged region output. |
| [`backend/app/services/document_ingestion/parsers/__init__.py`](../../backend/app/services/document_ingestion/parsers/__init__.py) | Parser package surface. | Parser imports. | Native parser symbols. |
| [`backend/app/services/document_ingestion/parsers/docx_parser.py`](../../backend/app/services/document_ingestion/parsers/docx_parser.py) | Extracts native DOCX paragraphs/pages. | DOCX bytes. | Native document pages/text. |
| [`backend/app/services/document_ingestion/parsers/pdf_text_parser.py`](../../backend/app/services/document_ingestion/parsers/pdf_text_parser.py) | Extracts native PDF text/pages. | PDF bytes. | Native PDF pages/text, with page-level hashes. |
| [`backend/app/services/document_ingestion/recognition/__init__.py`](../../backend/app/services/document_ingestion/recognition/__init__.py) | Recognition package façade. | Recognizer imports. | `DocumentRecognizer` and provider-neutral types. |
| [`backend/app/services/document_ingestion/recognition/base.py`](../../backend/app/services/document_ingestion/recognition/base.py) | Defines the provider-neutral recognizer protocol. | Page/image bytes and metadata. | Normalized recognition result contract. |
| [`backend/app/services/document_ingestion/recognition/content_filter.py`](../../backend/app/services/document_ingestion/recognition/content_filter.py) | Filters unsafe/irrelevant recognition content before preview assembly. | Recognized text/regions. | Bounded content and warnings. |
| [`backend/app/services/document_ingestion/recognition/google_vision.py`](../../backend/app/services/document_ingestion/recognition/google_vision.py) | Adapts Google Vision OCR to the provider-neutral recognizer contract. | Image bytes and Google credentials/config. | OCR text, words, confidence, and provider metadata. |
| [`backend/app/services/document_ingestion/recognition/google_vision_response.py`](../../backend/app/services/document_ingestion/recognition/google_vision_response.py) | Parses Google Vision response JSON into normalized words/regions. | Google response payload. | Typed OCR response values. |
| [`backend/app/services/document_ingestion/recognition/typhoon.py`](../../backend/app/services/document_ingestion/recognition/typhoon.py) | Adapts Typhoon OCR to the same preview contract. | Page image/bytes and Typhoon config. | Recognized text/regions and warnings. |
| [`backend/app/services/document_ingestion/recognition/htr.py`](../../backend/app/services/document_ingestion/recognition/htr.py) | Provides explicit review-required HTR behavior. | Handwriting region. | Review-required result; HTR is disabled in the production router. |
| [`backend/app/services/document_ingestion/routing/__init__.py`](../../backend/app/services/document_ingestion/routing/__init__.py) | Routing package surface. | Router imports. | Region-router symbols. |
| [`backend/app/services/document_ingestion/routing/region_router.py`](../../backend/app/services/document_ingestion/routing/region_router.py) | Selects native/OCR/HTR/review route from region type and policy. | Region classification, mixed/unknown policy, HTR flag. | Recognition method decision and warnings. |
| [`backend/app/services/document_ingestion/segmentation/__init__.py`](../../backend/app/services/document_ingestion/segmentation/__init__.py) | Segmentation package surface. | Segmenter imports. | Segmenter protocol and implementation. |
| [`backend/app/services/document_ingestion/segmentation/base.py`](../../backend/app/services/document_ingestion/segmentation/base.py) | Defines region-segmentation protocol. | Page image/metadata. | Region candidates. |
| [`backend/app/services/document_ingestion/segmentation/whole_page.py`](../../backend/app/services/document_ingestion/segmentation/whole_page.py) | Supplies conservative whole-page segmentation. | Page image/page number. | One full-page region, avoiding unsupported handwriting inference. |
| [`backend/app/services/document_ingestion/evaluation/__init__.py`](../../backend/app/services/document_ingestion/evaluation/__init__.py) | Evaluation package surface for ingestion metrics. | Evaluation imports. | Metric helpers for offline tests/tools, not production requests. |
| [`backend/app/services/document_ingestion/evaluation/metrics.py`](../../backend/app/services/document_ingestion/evaluation/metrics.py) | Computes ingestion/OCR evaluation metrics. | Gold/predicted records. | Offline metric values/reports. |

The ingestion path ends at preview. The integration boundary into case analysis is the frontend-reviewed narrative plus validated document-source metadata in a later `POST /messages` request.

## Backend follow-up, LLM, and provider integration

### Follow-up package

| File | Why it exists | Receives | Sends / collaborates |
| --- | --- | --- | --- |
| [`backend/app/services/followup/__init__.py`](../../backend/app/services/followup/__init__.py) | Stable façade for gap/follow-up contracts and evaluation functions. | Internal imports. | Follow-up symbols used by workflow. |
| [`backend/app/services/followup/contracts.py`](../../backend/app/services/followup/contracts.py) | Defines follow-up decisions, gap records, and evaluation result contracts. | Typed gap/question/answer values. | Stable policy/evaluator input and output. |
| [`backend/app/services/followup/schemas.py`](../../backend/app/services/followup/schemas.py) | Defines structured provider output for follow-up analysis. | Provider JSON. | Validated gap/question schema. |
| [`backend/app/services/followup/prompts.py`](../../backend/app/services/followup/prompts.py) | Builds follow-up gap-analysis prompts. | Raw evidence, analysis answer, prior exchanges, context. | Provider prompt content. |
| [`backend/app/services/followup/gap_analysis.py`](../../backend/app/services/followup/gap_analysis.py) | Runs the follow-up gap analyzer and decodes its response. | Evidence, answer, context, analyzer/client. | Candidate gaps and a follow-up question. |
| [`backend/app/services/followup/gap_stage.py`](../../backend/app/services/followup/gap_stage.py) | Executes the bounded gap stage and prepares canonical analysis enrichment. | Original content, exchanges, evidence, analysis claims, policy/analyzer. | Gap-stage result consumed by case analysis and follow-up evaluation. |
| [`backend/app/services/followup/stateful.py`](../../backend/app/services/followup/stateful.py) | Applies stateful clarification decisions across a chain. | Prior gaps, new result, answer history, policy. | Keep/remove/exhaust/next-gap decision without creating a separate Case State table. |
| [`backend/app/services/followup/decision.py`](../../backend/app/services/followup/decision.py) | Normalizes one decision about whether to ask, complete, preserve, or exhaust a gap. | Candidate gap and policy state. | Typed follow-up decision. |
| [`backend/app/services/followup/policy.py`](../../backend/app/services/followup/policy.py) | Applies configured bounded clarification policy. | Gap count, attempts, criticality, settings. | Whether a question may be asked and its limits. |
| [`backend/app/services/followup/context.py`](../../backend/app/services/followup/context.py) | Builds the context supplied to follow-up analysis. | Evidence/analysis/clarification history. | Bounded context payload. |
| [`backend/app/services/followup/claim_transport.py`](../../backend/app/services/followup/claim_transport.py) | Transports validated claim summaries into the gap stage. | Analysis claims and source IDs. | Claim-linked gap input; preserves referential identity. |
| [`backend/app/services/followup/helpers.py`](../../backend/app/services/followup/helpers.py) | Small normalization and selection helpers for follow-up evaluation. | Gap/question/metadata values. | Normalized values used by policy and metadata. |
| [`backend/app/services/followup/metadata.py`](../../backend/app/services/followup/metadata.py) | Serializes follow-up questions, root ordinals, attempts, and gap state into message metadata. | Typed follow-up result and source run. | JSON metadata stored with the assistant question/result. |
| [`backend/app/services/followup/response_content.py`](../../backend/app/services/followup/response_content.py) | Selects safe user-facing follow-up content from a result. | Follow-up result/error. | Assistant question or bounded limitation text. |

The workflow calls follow-up after the fresh analysis result. The frontend reads the resulting assistant metadata through `chat-followup.ts`; it does not calculate gap exhaustion or mutate the chain itself.

### LLM and RAG client boundary

| File | Why it exists | Receives | Sends / collaborates |
| --- | --- | --- | --- |
| [`backend/app/services/llm/__init__.py`](../../backend/app/services/llm/__init__.py) | LLM service façade. | Internal imports. | Provider/model symbols to analysis and follow-up code. |
| [`backend/app/services/llm/core_llm.py`](../../backend/app/services/llm/core_llm.py) | Resolves the core analysis provider target, URL, headers, and model. | Settings and model alias. | `CoreLLMTarget` consumed by analysis executor. |
| [`backend/app/services/llm/model_registry.py`](../../backend/app/services/llm/model_registry.py) | Maps supported aliases to provider/model presets. | Alias/configuration. | Canonical model identity and provider settings. |
| [`backend/app/services/llm/structured_output.py`](../../backend/app/services/llm/structured_output.py) | Produces provider-specific structured-output request options/schema. | Pydantic output model and provider. | JSON-schema request fragments. |
| [`backend/app/services/llm/token_budget.py`](../../backend/app/services/llm/token_budget.py) | Computes bounded input/output token budgets. | Prompt text, configured limits, model context. | Budget values used before provider calls. |
| [`backend/app/services/clients/__init__.py`](../../backend/app/services/clients/__init__.py) | Client package surface. | Client imports. | RAG client symbols. |
| [`backend/app/services/clients/rag_client.py`](../../backend/app/services/clients/rag_client.py) | Calls the private RAG service and maps transport/provider failures. | Raw technical query, configured URL/timeout, optional HTTP client. | `QueryResponse` or `RagCallFailure` to `rag_routing`; no browser response is proxied directly. |

The core LLM request is a backend-to-provider call. The frontend sees only the validated assistant message and metadata. The RAG client is an internal adapter; only the workflow decides whether it may be called.

## Backend report integration

| File | Why it exists | Receives | Sends / collaborates |
| --- | --- | --- | --- |
| [`backend/app/services/reports/__init__.py`](../../backend/app/services/reports/__init__.py) | Stable report service façade and exported errors/types. | Internal imports. | `ReportService`/`ChatReportService` to router. |
| [`backend/app/services/reports/report_contracts.py`](../../backend/app/services/reports/report_contracts.py) | Defines report input snapshot, run result, and report error contracts. | Persisted data/projection values. | Typed report pipeline boundaries. |
| [`backend/app/services/reports/report_snapshot.py`](../../backend/app/services/reports/report_snapshot.py) | Builds the immutable input snapshot for one report version. | Thread messages, latest validated analysis, optional matching `RagContext`. | `ReportInputSnapshot` and source hash or a generation conflict. |
| [`backend/app/services/reports/report_generation.py`](../../backend/app/services/reports/report_generation.py) | Runs deterministic report generation. Key function: `run_report_generation`. | `ReportInputSnapshot`. | `ReportRunResult` from template build/validation; no provider call. |
| [`backend/app/services/reports/report_template.py`](../../backend/app/services/reports/report_template.py) | Builds the seven-section structured report. | Snapshot, findings, trace, optional MITRE rows, gaps/limitations. | `StructuredReport`. |
| [`backend/app/services/reports/report_validation.py`](../../backend/app/services/reports/report_validation.py) | Validates section order, claim uniqueness, source IDs, MITRE IDs, and snapshot hash. | `StructuredReport`, source/MITRE ID sets, snapshot. | Validation errors or valid report. |
| [`backend/app/services/reports/report_persistence.py`](../../backend/app/services/reports/report_persistence.py) | Owns report idempotency, version allocation, serialization, persistence, and PDF access. Key class: `ChatReportService`; key function: `serialize_chat_report`. | DB session, thread/report UUIDs, `ChatReportCreate`, report snapshot. | `ChatReportRead`, `ChatReport` rows, or PDF bytes/filename. |
| [`backend/app/services/reports/report_analysis_projection.py`](../../backend/app/services/reports/report_analysis_projection.py) | Projects validated analysis into report-friendly sections. | Analysis trace/message metadata. | Report findings, timeline, overview, and limitations inputs. |
| [`backend/app/services/reports/report_finding_projection.py`](../../backend/app/services/reports/report_finding_projection.py) | Projects finding claims and source links. | Analysis claims and source messages. | Structured report claim items. |
| [`backend/app/services/reports/report_mitre_projection.py`](../../backend/app/services/reports/report_mitre_projection.py) | Projects optional MITRE rows into an isolated appendix. | Bound retrieval context/MITRE rows. | External-context report items; does not turn them into evidence. |
| [`backend/app/services/reports/report_review_projection.py`](../../backend/app/services/reports/report_review_projection.py) | Projects open questions, review state, and limitations. | Canonical analysis gaps and validation status. | Review/limitation report items. |
| [`backend/app/services/reports/report_html.py`](../../backend/app/services/reports/report_html.py) | Renders report data to HTML presentation. | Serialized report/view model. | HTML string for review/rendering. |
| [`backend/app/services/reports/report_view_model_builder.py`](../../backend/app/services/reports/report_view_model_builder.py) | Builds the presentation view model for report HTML/PDF. | `ChatReportRead` and report sections. | View-model contract. |
| [`backend/app/services/reports/report_view_model_contracts.py`](../../backend/app/services/reports/report_view_model_contracts.py) | Defines report presentation item contracts. | Structured report presentation values. | Typed view model for templates. |
| [`backend/app/services/reports/report_view_model_items.py`](../../backend/app/services/reports/report_view_model_items.py) | Builds report cards/items from source-backed claims and sections. | Report sections, claims, references. | Renderable item list. |
| [`backend/app/services/reports/report_view_model_text.py`](../../backend/app/services/reports/report_view_model_text.py) | Normalizes report text for display. | Raw/structured report text. | Display-safe report text. |
| [`backend/app/services/reports/report_pdf.py`](../../backend/app/services/reports/report_pdf.py) | Coordinates PDF export from a persisted validated report. | Serialized report and thread title. | PDF bytes through `render_chat_report_pdf`. |
| [`backend/app/services/reports/report_pdf_story.py`](../../backend/app/services/reports/report_pdf_story.py) | Converts report view-model content into PDF story elements. | Report view model/design settings. | ReportLab story elements. |
| [`backend/app/services/reports/pdf_design.py`](../../backend/app/services/reports/pdf_design.py) | Defines PDF styles, colors, typography, and evidence cards. | Report theme/config. | ReportLab styles and layout primitives. |
| [`backend/app/services/reports/pdf_chrome.py`](../../backend/app/services/reports/pdf_chrome.py) | Provides PDF page chrome/header/footer behavior. | Page canvas and report metadata. | Rendered PDF decorations. |

### Report frontend handoff

`generate_case_report` verifies Case/result ownership, calls `CaseReportService.generate_report`, and returns the persisted result/snapshot-bound `ChatReportRead`. The frontend’s `CaseReportView` requests that contract, `PersistedReportCard` renders one row, and the Case PDF client receives a `Blob`. The compatibility Chat report path remains available for historical/unbound Chat data; the backend validates again before PDF export and the UI cannot export an arbitrary locally assembled report.

## Backend workflow integration

| File | Why it exists | Receives | Sends / collaborates |
| --- | --- | --- | --- |
| [`backend/app/services/workflow/__init__.py`](../../backend/app/services/workflow/__init__.py) | Stable façade for Case and compatibility run processing/recovery entry points. | Internal imports. | `process_case_run`, `process_chat_run`, and recovery symbols to routers/main. |
| [`backend/app/services/workflow/case_run_service.py`](../../backend/app/services/workflow/case_run_service.py) | Enqueues Case analysis, resolves currentness, and reads owned CaseRun/result state. | Case ID, owner, evidence revision, idempotency/fingerprint. | Immutable snapshot-pinned CaseRun/result records. |
| [`backend/app/services/workflow/case_run_claim.py`](../../backend/app/services/workflow/case_run_claim.py) | Claims CaseRun work with PostgreSQL locking and lease fencing. | CaseRun ID and worker ID. | Claimed CaseRun or no-op for stale/finished work. |
| [`backend/app/services/workflow/case_run_execution.py`](../../backend/app/services/workflow/case_run_execution.py) | Executes Case analysis from the saved snapshot and pinned configuration. | Claimed CaseRun and provider dependencies. | Validated Case outcome or explicit failure. |
| [`backend/app/services/workflow/case_run_completion.py`](../../backend/app/services/workflow/case_run_completion.py) | Completes CaseRun atomically with result, clarification, and optional Chat publication. | Claimed run, outcome, snapshot, worker identity. | Append-only result, one assistant publication, latest pointer, completed run. |
| [`backend/app/services/workflow/case_run_recovery.py`](../../backend/app/services/workflow/case_run_recovery.py) | Recovers expired CaseRun leases without allowing stale workers to publish. | Session factory, clock, CaseRun state. | Requeued/failed CaseRun state under the saved identity. |
| [`backend/app/services/workflow/pipeline.py`](../../backend/app/services/workflow/pipeline.py) | Builds dependency wiring and exposes Case and compatibility background-task entry points. Key symbols: `build_dependencies`, `process_case_run`, `process_chat_run`. | Run ID, DB session factory, service/provider functions. | `PipelineDependencies` and executable Case/Chat pipelines. |
| [`backend/app/services/workflow/pipeline_execution.py`](../../backend/app/services/workflow/pipeline_execution.py) | Coordinates claim, lease heartbeat, action dispatch, outcome persistence, receipt handling, and failure. Key symbols: `process_chat_run`, fresh-analysis execution. | Run ID and injected pipeline dependencies. | Completed/failed run state through claim/completion/failure modules. |
| [`backend/app/services/workflow/chat_run_contracts.py`](../../backend/app/services/workflow/chat_run_contracts.py) | Defines `ClaimedChatRun`, lease duration, and run execution data. | Persisted run/history values. | Typed handoff from claim to execution. |
| [`backend/app/services/workflow/chat_run_claim.py`](../../backend/app/services/workflow/chat_run_claim.py) | Atomically claims a queued run and reconstructs evidence, action, clarification chain, analysis context, and pinned pipeline. Key function: `claim_run`. | Async session, run UUID, worker ID. | `ClaimedChatRun` or failure state; sets `running` lease. |
| [`backend/app/services/workflow/chat_run_locks.py`](../../backend/app/services/workflow/chat_run_locks.py) | Provides row-lock helpers for owned runs and threads. | DB session, run/thread IDs, worker identity. | Lock-protected ORM rows to completion/failure. |
| [`backend/app/services/workflow/chat_run_store.py`](../../backend/app/services/workflow/chat_run_store.py) | Reads/stores run state used by workflow execution. | DB session and run identifiers. | Run records/status values. |
| [`backend/app/services/workflow/chat_run_completion.py`](../../backend/app/services/workflow/chat_run_completion.py) | Persists a successful `AssistantOutcome`, optional `RagContext`, analysis trace metadata, thread status, and run completion. Key function: `complete_run`. | DB session, run/worker IDs, `AssistantOutcome`. | Durable assistant message, context, status, and lease release. |
| [`backend/app/services/workflow/chat_run_failure.py`](../../backend/app/services/workflow/chat_run_failure.py) | Persists stable failure code/message and releases run ownership. | DB session, run/worker IDs, failure detail. | Failed `ChatRun` and thread status. |
| [`backend/app/services/workflow/outcome.py`](../../backend/app/services/workflow/outcome.py) | Defines `AssistantOutcome`, RAG payload/status, and constructors/binders for fresh, question, and follow-up results. | Analysis/follow-up/RAG results and evidence bindings. | One normalized outcome consumed by completion. |
| [`backend/app/services/workflow/analysis_pipeline_context.py`](../../backend/app/services/workflow/analysis_pipeline_context.py) | Prepares and binds analysis context, pipeline config, source IDs, and evidence hash. | Claimed run, applicability/RAG result. | Context dict for analysis and bound outcome metadata. |
| [`backend/app/services/workflow/rag_routing.py`](../../backend/app/services/workflow/rag_routing.py) | Applies the applicability gate and turns optional RAG outcomes into `used`, `no_applicable_context`, or `unavailable`. Key functions: `attempt_mitre_applicability`, `attempt_optional_rag`. | Claimed evidence and injected gate/RAG request. | Validated applicability and nullable RAG payload; RAG failure is non-fatal. |
| [`backend/app/services/workflow/question_execution.py`](../../backend/app/services/workflow/question_execution.py) | Executes ordinary `ask` against existing canonical analysis/context without fresh RAG. | Claimed run and analysis request dependency. | Response-scoped `AssistantOutcome`. |
| [`backend/app/services/workflow/analysis_execution_receipt.py`](../../backend/app/services/workflow/analysis_execution_receipt.py) | Persists stage/attempt receipts for claim-anchored execution. | Run/stage/config/timing/provider values. | Durable receipt metadata used for auditability and debugging. |
| [`backend/app/services/workflow/run_heartbeat.py`](../../backend/app/services/workflow/run_heartbeat.py) | Renews a running lease while provider work is in progress. | DB session, run/worker IDs, lease policy. | Updated lease expiry or ownership failure. |
| [`backend/app/services/workflow/run_recovery.py`](../../backend/app/services/workflow/run_recovery.py) | Recovers expired/interrupted runs at startup and through the monitor. Key symbols: `recover_expired_runs`, `monitor_interrupted_runs`. | Session factory, current time, lease/run state. | Requeued/failed runs and clean worker lifecycle. |

### Worker state machine

```text
queued
  └─ claim_run + row lock + lease → running
       ├─ ask → question_execution → AssistantOutcome
       └─ fresh/additional → applicability → optional RAG → case analysis
                                  → gap/follow-up policy → AssistantOutcome
  └─ complete_run → completed + assistant message (+ optional RagContext)
  └─ failure/recovery → failed or requeued according to lease policy
```

The background task receives only a run ID from the route. It reconstructs the rest from PostgreSQL, which prevents the request process and browser from becoming the source of truth for a long-running operation.

## Backend test and tooling map

The backend regression suite is part of the exhaustive index and is the executable documentation for boundary behavior. It is grouped here by contract rather than repeated line-by-line.

| Test group | Files / coverage | What it proves |
| --- | --- | --- |
| Auth and ownership | [`backend/tests/test_auth_jwt.py`](../../backend/tests/test_auth_jwt.py), [`test_auth_routes.py`](../../backend/tests/test_auth_routes.py), [`test_password_accounts.py`](../../backend/tests/test_password_accounts.py), [`test_account_persistence.py`](../../backend/tests/test_account_persistence.py), [`test_chat_ownership.py`](../../backend/tests/test_chat_ownership.py) | Token/cookie behavior, account persistence, login routes, and cross-user thread isolation. |
| Route/API surface | [`backend/tests/test_route_surface.py`](../../backend/tests/test_route_surface.py), [`test_cors.py`](../../backend/tests/test_cors.py), [`test_run_recovery_api.py`](../../backend/tests/test_run_recovery_api.py) | Registered public routes, CORS, and HTTP-visible run recovery. |
| Raw chat workflow | [`backend/tests/test_chat_raw_pipeline.py`](../../backend/tests/test_chat_raw_pipeline.py), [`test_raw_evidence_workflow.py`](../../backend/tests/test_raw_evidence_workflow.py), [`test_chat_followup_policy.py`](../../backend/tests/test_chat_followup_policy.py), [`test_gap_assembly.py`](../../backend/tests/test_gap_assembly.py) | Action classification, evidence inclusion/exclusion, follow-up state, and gap assembly. |
| Analysis and retirement | [`backend/tests/test_general_case_analysis.py`](../../backend/tests/test_general_case_analysis.py), [`test_main_case_analysis.py`](../../backend/tests/test_main_case_analysis.py), [`test_analysis_trace.py`](../../backend/tests/test_analysis_trace.py), [`test_analysis_trace_v3.py`](../../backend/tests/test_analysis_trace_v3.py), [`test_canonical_analysis_state.py`](../../backend/tests/test_canonical_analysis_state.py), [`test_analysis_retirement_selection.py`](../../backend/tests/test_analysis_retirement_selection.py), [`test_analysis_retirement_postgres.py`](../../backend/tests/test_analysis_retirement_postgres.py) | Trace parsing, canonical state, response-scoped ASK, and retired legacy behavior. |
| Claim-anchored path | [`backend/tests/test_claim_anchored_binding.py`](../../backend/tests/test_claim_anchored_binding.py), [`test_claim_anchored_pipeline.py`](../../backend/tests/test_claim_anchored_pipeline.py), [`test_claim_anchored_postgres.py`](../../backend/tests/test_claim_anchored_postgres.py), [`test_claim_anchored_selection.py`](../../backend/tests/test_claim_anchored_selection.py), [`test_claim_anchored_verification_boundary.py`](../../backend/tests/test_claim_anchored_verification_boundary.py), [`test_claim_anchored_workflow.py`](../../backend/tests/test_claim_anchored_workflow.py), [`test_analysis_pipeline_versioning.py`](../../backend/tests/test_analysis_pipeline_versioning.py) | Exact binding, deterministic selection, receipts, version pinning, and verifier seam. |
| Applicability/RAG | [`backend/tests/test_mitre_applicability_pipeline.py`](../../backend/tests/test_mitre_applicability_pipeline.py), [`test_mitre_applicability_provider.py`](../../backend/tests/test_mitre_applicability_provider.py), [`test_mitre_applicability_validation.py`](../../backend/tests/test_mitre_applicability_validation.py), [`test_optional_rag_pipeline.py`](../../backend/tests/test_optional_rag_pipeline.py), [`test_chat_rag_client.py`](../../backend/tests/test_chat_rag_client.py) | Gate decisions, provider failures, response validation, and nullable external context. |
| Ingestion | [`backend/tests/test_document_ingestion.py`](../../backend/tests/test_document_ingestion.py), [`test_document_ingestion_api.py`](../../backend/tests/test_document_ingestion_api.py), [`test_document_ingestion_eval.py`](../../backend/tests/test_document_ingestion_eval.py), [`test_document_ingestion_google_response.py`](../../backend/tests/test_document_ingestion_google_response.py), [`test_document_ingestion_google_service.py`](../../backend/tests/test_document_ingestion_google_service.py), [`test_document_ingestion_google_transport.py`](../../backend/tests/test_document_ingestion_google_transport.py), [`test_document_ingestion_routing.py`](../../backend/tests/test_document_ingestion_routing.py), [`test_document_ingestion_segmentation.py`](../../backend/tests/test_document_ingestion_segmentation.py), [`test_document_narrative_handoff.py`](../../backend/tests/test_document_narrative_handoff.py) | Preview-only extraction, provider-neutral OCR, routing, confidence, and source handoff. |
| Case-first PostgreSQL workflow | [`backend/tests/test_case_materials_postgres.py`](../../backend/tests/test_case_materials_postgres.py), [`test_case_runs_postgres.py`](../../backend/tests/test_case_runs_postgres.py), [`test_case_chat_postgres.py`](../../backend/tests/test_case_chat_postgres.py), [`test_case_reports_postgres.py`](../../backend/tests/test_case_reports_postgres.py) | Real-PostgreSQL locking/race behavior, pinned snapshots, atomic publication, clarification idempotency, lazy Chat, recovery, and result/snapshot-bound reports. |
| Reports and persistence | [`backend/tests/test_chat_report.py`](../../backend/tests/test_chat_report.py), [`test_report_view_model_and_pdf.py`](../../backend/tests/test_report_view_model_and_pdf.py) | Deterministic report snapshot/generation, idempotency, view model, and PDF validation. |
| Infrastructure/schema | [`backend/tests/test_database_schema.py`](../../backend/tests/test_database_schema.py), [`test_migration_chat_only_cleanup.py`](../../backend/tests/test_migration_chat_only_cleanup.py), [`test_run_recovery_postgres.py`](../../backend/tests/test_run_recovery_postgres.py), [`test_structured_output.py`](../../backend/tests/test_structured_output.py), [`test_model_registry.py`](../../backend/tests/test_model_registry.py), [`test_core_llm_provider.py`](../../backend/tests/test_core_llm_provider.py) | Database shape, migrations, leases, structured-output schemas, and model routing. |

The current Case-first migration/cutover receipt is [`CASE_FIRST_MIGRATION_AUDIT_2026-09-10.md`](CASE_FIRST_MIGRATION_AUDIT_2026-09-10.md). It records the live PostgreSQL catalog/count audit, the populated disposable 0001→0010 rehearsal, deletion preservation behavior, the coordinated Docker rebuild, and the unavailable authenticated browser smoke separately from passing route/build checks.

Repository tooling and smoke scripts are also indexed: [`backend/scripts/export_openapi.py`](../../backend/scripts/export_openapi.py) exports the backend contract, [`backend/scripts/smoke_claim_anchored.py`](../../backend/scripts/smoke_claim_anchored.py) exercises the opt-in provider path, and [`backend/manual_smoke.py`](../../backend/manual_smoke.py) is manual runtime support. These tools are not browser runtime dependencies.

## Frontend file map

The frontend is intentionally split into transport, state orchestration, pure data projections, and presentation. The rows below cover every current application file under `frontend/src` except generated declarations and tests; both excluded categories remain linked in the index.

### Next.js route entries and application shell

| File | Why it exists | Receives | Sends / collaborates |
| --- | --- | --- | --- |
| [`frontend/src/app/layout.tsx`](../../frontend/src/app/layout.tsx) | Root App Router layout, fonts, metadata, and provider wrapper. | Next children. | `Providers` around all pages. |
| [`frontend/src/app/providers.tsx`](../../frontend/src/app/providers.tsx) | Creates the React Query client and mounts `AccountGate`. | React children. | Query cache + authentication gate. |
| [`frontend/src/app/page.tsx`](../../frontend/src/app/page.tsx) | Home route entry. | None. | `HomePage`/landing UI. |
| [`frontend/src/app/login/page.tsx`](../../frontend/src/app/login/page.tsx) | Login route entry. | URL redirect query. | `AccountForm` in login mode. |
| [`frontend/src/app/register/page.tsx`](../../frontend/src/app/register/page.tsx) | Registration route entry. | URL redirect query. | `AccountForm` in register mode. |
| [`frontend/src/app/case/layout.tsx`](../../frontend/src/app/case/layout.tsx) | Case-first workspace layout. | Route children. | Renders `ChatWorkspace`; native Case data is loaded by the client workspace. |
| [`frontend/src/app/case/page.tsx`](../../frontend/src/app/case/page.tsx) | `/case` page entry. | None. | Currently returns no page content; workspace comes from layout. |
| [`frontend/src/app/case/[threadId]/page.tsx`](../../frontend/src/app/case/[threadId]/page.tsx) | Dynamic Case route entry. | Case ID route segment. | Route shell for the default workspace; `ChatWorkspace` owns data/rendering. |
| [`frontend/src/app/case/[threadId]/[view]/page.tsx`](../../frontend/src/app/case/[threadId]/[view]/page.tsx) | Dynamic Case workspace-view entry. | Case ID and view route segments. | Route shell for native Intake, Overview, Materials, Report, Technical Context, and Chat views. |
| [`frontend/src/app/chat/layout.tsx`](../../frontend/src/app/chat/layout.tsx) | Legacy chat-route compatibility layout. | Route children and pathname. | Renders `ChatWorkspace` then redirects `/chat...` to `/case...`. |
| [`frontend/src/app/chat/page.tsx`](../../frontend/src/app/chat/page.tsx) | Legacy `/chat` page entry. | None. | Placeholder content; layout handles compatibility redirect. |
| [`frontend/src/app/chat/[threadId]/page.tsx`](../../frontend/src/app/chat/[threadId]/page.tsx) | Legacy dynamic chat page entry. | Thread ID route segment. | Placeholder content under the compatibility layout. |
| [`frontend/src/app/chat/[threadId]/chat/page.tsx`](../../frontend/src/app/chat/[threadId]/chat/page.tsx) | Legacy chat subroute entry. | Async thread ID params. | Redirects `/chat/{id}/chat` to `/chat/{id}/overview`; outer layout then redirects to `/case`. |
| [`frontend/src/app/chat/[threadId]/intake/page.tsx`](../../frontend/src/app/chat/[threadId]/intake/page.tsx) | Legacy intake subroute entry. | None. | Currently returns no page content. |
| [`frontend/src/app/chat/[threadId]/materials/page.tsx`](../../frontend/src/app/chat/[threadId]/materials/page.tsx) | Legacy materials subroute entry. | None. | Currently returns no page content. |
| [`frontend/src/app/chat/[threadId]/overview/page.tsx`](../../frontend/src/app/chat/[threadId]/overview/page.tsx) | Legacy overview subroute entry. | None. | Currently returns no page content. |
| [`frontend/src/app/chat/[threadId]/report/page.tsx`](../../frontend/src/app/chat/[threadId]/report/page.tsx) | Legacy report subroute entry. | None. | Currently returns no page content. |
| [`frontend/src/app/chat/[threadId]/technical-context/page.tsx`](../../frontend/src/app/chat/[threadId]/technical-context/page.tsx) | Legacy technical-context subroute entry. | None. | Currently returns no page content. |

The route shell and the client workspace are separate responsibilities: App Router registers the dynamic path, while `ChatWorkspace` selects and renders the Case view. See [Verified route surface](#verified-route-surface) for the runtime registration evidence.

### Workspace orchestration

| File | Why it exists | Receives | Sends / collaborates |
| --- | --- | --- | --- |
| [`frontend/src/components/ChatWorkspace.tsx`](../../frontend/src/components/ChatWorkspace.tsx) | Top-level client orchestration for Case-first and compatibility Chat routes, session, selection, submission, deletion, and projections. Key symbol: `ChatWorkspace`. | Current pathname/router, auth/session, Case/Chat React Query data, user actions. | `ChatWorkspaceLayout` props; keeps Case queries/polling independent and opens Chat lazily. |
| [`frontend/src/components/ChatWorkspaceLayout.tsx`](../../frontend/src/components/ChatWorkspaceLayout.tsx) | Renders workspace chrome and selects the active native Case or compatibility Chat view. Key symbol: `ChatWorkspaceLayout`. | Case/Chat identity, messages, result/material/run state, callbacks, UI state. | Sidebar/header, native intake/overview/materials/report views, optional Chat panel, dialogs. |
| [`frontend/src/hooks/use-case-queries.ts`](../../frontend/src/hooks/use-case-queries.ts) | Owns Case list/detail/material/evidence/result/clarification/report query keys and Case CRUD/action mutations. | Case ID, owner session, mutation payloads. | Case React Query caches and invalidation. |
| [`frontend/src/hooks/use-case-run-polling.ts`](../../frontend/src/hooks/use-case-run-polling.ts) | Polls a CaseRun and refreshes the Case result after completion. | Case/run IDs and selection guards. | Case query invalidation; no Chat dependency. |
| [`frontend/src/hooks/use-case-workspace-actions.ts`](../../frontend/src/hooks/use-case-workspace-actions.ts) | Maps native Case intake/material/analysis/report/chat actions to transport calls. | Case UI events and typed payloads. | Case client mutations and lazy Chat opening. |
| [`frontend/src/features/chat/workspace/chat-workspace-types.ts`](../../frontend/src/features/chat/workspace/chat-workspace-types.ts) | Defines pending-submission and layout prop contracts. | Type values only. | Compile-time handoff between orchestration hooks and layout. |
| [`frontend/src/features/chat/workspace/use-chat-thread-selection.ts`](../../frontend/src/features/chat/workspace/use-chat-thread-selection.ts) | Owns active selection, detail cache, abort lifecycle, draft reconciliation, polling, and deletion suspension. Key symbols: `readChatThreadDetail`, `useChatThreadSelection`. | Thread ID, cache upsert callback, API detail responses, selection actions. | `ChatSession`: messages, status/phase, submit/poll/select/delete callbacks to `ChatWorkspace`. |
| [`frontend/src/features/chat/workspace/use-chat-draft.ts`](../../frontend/src/features/chat/workspace/use-chat-draft.ts) | Keeps input, pending submission identity, follow-up action, phase, and local error state separate from server detail. Key symbols: `phaseForThread`, `useChatDraft`. | Detail status, local input/events, accepted/failure/reconcile events. | Draft state and callbacks to selection/submission/UI. |
| [`frontend/src/features/chat/workspace/use-workspace-submission-actions.ts`](../../frontend/src/features/chat/workspace/use-workspace-submission-actions.ts) | Maps intake/chat UI actions into one submission API. Key symbol: `useWorkspaceSubmissionActions`. | Narrative/title/document sources, follow-up choice, retry intent, router callbacks. | `submitContent`, title update, view navigation. |
| [`frontend/src/features/chat/workspace/use-chat-thread-deletion.ts`](../../frontend/src/features/chat/workspace/use-chat-thread-deletion.ts) | Coordinates delete confirmation, selection suspension, API mutation, cache removal, restore, and route re-selection. Key symbol: `useChatThreadDeletion`. | Candidate thread ID, active view, mutation/session/router callbacks. | Deletion lifecycle and safe navigation. |

### Authentication and account UI

| File | Why it exists | Receives | Sends / collaborates |
| --- | --- | --- | --- |
| [`frontend/src/components/auth/AccountForm.tsx`](../../frontend/src/components/auth/AccountForm.tsx) | Login/register form and OAuth provider controls. Key symbols: `AccountForm`, `getRedirectTarget`, `submit`, `handleOAuthClick`. | Form fields, URL redirect, provider discovery response. | `/auth/login` or `/auth/register` request, OAuth navigation, account/session-change storage. |
| [`frontend/src/components/auth/AccountGate.tsx`](../../frontend/src/components/auth/AccountGate.tsx) | Protects workspace routes and redirects based on session state. Key symbol: `AccountGate`. | `useAuth` session/loading/error and pathname. | Public/auth/protected route rendering, login redirect, saved-route update. |
| [`frontend/src/hooks/use-auth.ts`](../../frontend/src/hooks/use-auth.ts) | Observes session, coordinates dev login/logout, cache invalidation, and OAuth navigation. Key symbols: `useAuth`, `sync`, `loginWithOAuth`. | API session/auth responses, storage events, provider choice. | Auth query state, account ID/session-change markers, `/login` navigation. |
| [`frontend/src/hooks/use-account-state.ts`](../../frontend/src/hooks/use-account-state.ts) | Provides account-scoped local state for drafts and intake. Key symbol: `useAccountState`. | Storage key, initial value, React updates. | Account-prefixed local storage state and setter. |
| [`frontend/src/lib/account-storage.ts`](../../frontend/src/lib/account-storage.ts) | Prefixes local-storage keys by active account. Key symbols: `accountStorageKey`, `readAccountValue`, `writeAccountValue`. | Logical key/value and current account marker. | Isolated browser persistence; no backend write. |
| [`frontend/src/components/common/UserProfileMenu.tsx`](../../frontend/src/components/common/UserProfileMenu.tsx) | Displays account identity and invokes confirmed logout. | User profile, logout callback. | Sign-out dialog/action to `useAuth.logout`. |
| [`frontend/src/components/common/SignOutDialog.tsx`](../../frontend/src/components/common/SignOutDialog.tsx) | Shared sign-out confirmation presentation. | Open state, cancel/confirm callbacks. | User decision; no network call itself. |

### Layout, navigation, common status, and home

| File | Why it exists | Receives | Sends / collaborates |
| --- | --- | --- | --- |
| [`frontend/src/components/home/HomePage.tsx`](../../frontend/src/components/home/HomePage.tsx) | Composes the landing page. | Auth/session and landing callbacks. | `HomeSections` and home navigation. |
| [`frontend/src/components/home/HomeSections.tsx`](../../frontend/src/components/home/HomeSections.tsx) | Auth-aware landing content and entry actions. | User/session state, navigation and logout callbacks. | Home CTA navigation, account menu, sign-out dialog. |
| [`frontend/src/components/layout/WorkspaceHeader.tsx`](../../frontend/src/components/layout/WorkspaceHeader.tsx) | Workspace title, view controls, and account actions. | Active thread/view, navigation callbacks, profile. | Route changes and menu/dialog events. |
| [`frontend/src/components/layout/WorkspaceSidebar.tsx`](../../frontend/src/components/layout/WorkspaceSidebar.tsx) | Thread list, selection, new-case, and delete affordances. | Thread list/loading/error, active ID, CRUD callbacks. | Thread selection, create, delete candidate, route action. |
| [`frontend/src/components/common/CyberCaseLogo.tsx`](../../frontend/src/components/common/CyberCaseLogo.tsx) | Reusable product logo. | Display props. | SVG/UI only. |
| [`frontend/src/components/common/DeleteDialog.tsx`](../../frontend/src/components/common/DeleteDialog.tsx) | Thread-delete confirmation presentation. | Candidate/open state, cancel/confirm callbacks. | User decision; no API call itself. |
| [`frontend/src/components/common/MeaningfulErrorModal.tsx`](../../frontend/src/components/common/MeaningfulErrorModal.tsx) | Presents operation-level errors while keeping raw details secondary. | Error title/message, raw detail, close/retry callbacks. | UI recovery action. |
| [`frontend/src/components/common/CaseRequiredState.tsx`](../../frontend/src/components/common/CaseRequiredState.tsx) | Empty state when a view needs case evidence. Key symbols: `EmptyStateCaseRequired`, `EmptyChatIntakeNotice`. | Copy and open-intake callback. | Navigation callback; no data mutation. |
| [`frontend/src/components/common/StatusPill.tsx`](../../frontend/src/components/common/StatusPill.tsx) | Reusable status badge. | Status/label props. | UI only. |
| [`frontend/src/components/common/WorkspaceSectionHeader.tsx`](../../frontend/src/components/common/WorkspaceSectionHeader.tsx) | Reusable workspace section heading. | Heading/subheading/action props. | UI only. |
| [`frontend/src/components/common/types.ts`](../../frontend/src/components/common/types.ts) | Shared workspace view/status type declarations. | Type values only. | Compile-time contracts for route and layout. |
| [`frontend/src/components/common/icons.tsx`](../../frontend/src/components/common/icons.tsx) | Shared icon components. | Icon props. | UI-only SVG components. |

### Conversation and evidence presentation

| File | Why it exists | Receives | Sends / collaborates |
| --- | --- | --- | --- |
| [`frontend/src/components/conversation/ChatPanel.tsx`](../../frontend/src/components/conversation/ChatPanel.tsx) | Chat input, action selection, pending state, follow-up controls, and transcript shell. | Messages, phase/status, draft input, callbacks, follow-up metadata. | `submitContent`, `changeInput`, explicit `ask`/`add_case_info` choice, retry/open-view actions. |
| [`frontend/src/components/conversation/ChatTranscript.tsx`](../../frontend/src/components/conversation/ChatTranscript.tsx) | Orders and renders persisted conversation messages. | `PersistedChatMessage[]`, loading/phase, interaction callbacks. | `ChatMessageMarkdown`, evidence/analysis reference panels. |
| [`frontend/src/components/conversation/ChatMessageMarkdown.tsx`](../../frontend/src/components/conversation/ChatMessageMarkdown.tsx) | Renders one message’s markdown/text with role-aware presentation. | Message content and role. | Safe display markup; no mutation. |
| [`frontend/src/components/conversation/FollowUpActionCard.tsx`](../../frontend/src/components/conversation/FollowUpActionCard.tsx) | Makes the post-answer action explicit when the thread can ask or add information. | Parsed follow-up state and action callback. | Action choice to workspace submission layer. |
| [`frontend/src/components/conversation/AnalysisEvidenceReferences.tsx`](../../frontend/src/components/conversation/AnalysisEvidenceReferences.tsx) | Displays source-message/evidence references attached to an analysis. | Analysis message, message list, source metadata. | `SourceEvidenceContent`/citation interactions; does not alter trace. |
| [`frontend/src/components/conversation/MitreCandidatePanel.tsx`](../../frontend/src/components/conversation/MitreCandidatePanel.tsx) | Displays optional MITRE candidate associations with external-context labeling. | Assistant metadata/candidate mappings. | Violet external-context UI; no evidence admission. |
| [`frontend/src/components/evidence/EvidenceCitationChip.tsx`](../../frontend/src/components/evidence/EvidenceCitationChip.tsx) | Compact citation link/chip. | Citation/source reference. | Opens or selects evidence presentation. |
| [`frontend/src/components/evidence/HighlightedEvidenceText.tsx`](../../frontend/src/components/evidence/HighlightedEvidenceText.tsx) | Highlights a validated literal evidence span. | Source text and offsets/citation. | Visual evidence location; no new provenance. |
| [`frontend/src/components/evidence/SourceEvidenceContent.tsx`](../../frontend/src/components/evidence/SourceEvidenceContent.tsx) | Renders the selected source message/document-derived text. | Persisted messages, source IDs, document spans. | Evidence drawer/popover content. |

### Intake and document review

| File | Why it exists | Receives | Sends / collaborates |
| --- | --- | --- | --- |
| [`frontend/src/components/intake/CaseFirstIntakeView.tsx`](../../frontend/src/components/intake/CaseFirstIntakeView.tsx) | Native Case preparation view with document persistence, explicit admission, and Analyze action. | Case/material/evidence/run state and typed Case action callbacks. | Case document/evidence/analysis mutations; does not require Chat. |
| [`frontend/src/components/intake/CaseIntakeView.tsx`](../../frontend/src/components/intake/CaseIntakeView.tsx) | Compatibility Chat intake view for legacy message-based submission. | Thread/messages/status, account-scoped drafts, ingestion state, submission/navigation callbacks. | `CaseIntakeSubmission` to the Chat compatibility path. |
| [`frontend/src/components/intake/IntakeNarrativeForm.tsx`](../../frontend/src/components/intake/IntakeNarrativeForm.tsx) | Editable narrative/title form. | Title, description, document draft, disabled/source state, field callbacks. | Form events and document-use/remove actions. |
| [`frontend/src/components/intake/CaseIntakeFiles.tsx`](../../frontend/src/components/intake/CaseIntakeFiles.tsx) | Lists selected/saved/preview materials alongside intake. | Material items, selected ID, selection/open callbacks, preview child. | Material selection/navigation. |
| [`frontend/src/components/intake/DocumentIngestionPreview.tsx`](../../frontend/src/components/intake/DocumentIngestionPreview.tsx) | File picker and extraction-preview control. | Case key, disabled flag, local ingestion hook. | File/mode → `previewDocumentIngestion`; stores result locally. |
| [`frontend/src/components/intake/DocumentIngestionResult.tsx`](../../frontend/src/components/intake/DocumentIngestionResult.tsx) | Displays preview result, pages, confidence, warnings, and review state. | `IngestedDocumentPreview`. | Analyst-visible review decision; no persistence. |
| [`frontend/src/components/intake/ExtractedTextPreview.tsx`](../../frontend/src/components/intake/ExtractedTextPreview.tsx) | Displays normalized readable/raw extracted text. | Text and label. | Read-only text view. |
| [`frontend/src/components/intake/CaseNarrativeSourceNotice.tsx`](../../frontend/src/components/intake/CaseNarrativeSourceNotice.tsx) | Explains whether a narrative is linked to a reviewed document source. | Source/draft status. | User-facing provenance notice. |

### Case projections and analytical views

| File | Why it exists | Receives | Sends / collaborates |
| --- | --- | --- | --- |
| [`frontend/src/components/overview/CaseOverviewView.tsx`](../../frontend/src/components/overview/CaseOverviewView.tsx) | Primary structured case-analysis view. | Projected overview, messages, status, navigation callbacks. | Renders canonical findings, open questions, evidence links, status rail, and optional MITRE explanation. |
| [`frontend/src/components/overview/CaseOverviewHeader.tsx`](../../frontend/src/components/overview/CaseOverviewHeader.tsx) | Overview title/status/source summary. | Overview metadata and view callbacks. | Header navigation/UI. |
| [`frontend/src/components/overview/CaseFindingsSection.tsx`](../../frontend/src/components/overview/CaseFindingsSection.tsx) | Groups and renders findings by claim type and epistemic status. | Finding projection and evidence callbacks. | Finding cards/citations without upgrading status. |
| [`frontend/src/components/overview/OpenQuestionsSection.tsx`](../../frontend/src/components/overview/OpenQuestionsSection.tsx) | Renders unresolved gaps/open questions. | Gap projection and follow-up callback. | User action to chat/intake; preserves unknowns. |
| [`frontend/src/components/overview/OverviewStatusRail.tsx`](../../frontend/src/components/overview/OverviewStatusRail.tsx) | Displays analysis/readiness/provenance/RAG status. | Overview state and metadata counts. | Status-only UI. |
| [`frontend/src/components/overview/SourceEvidenceDrawer.tsx`](../../frontend/src/components/overview/SourceEvidenceDrawer.tsx) | Full evidence drawer for a selected source. | Source message/document data and close state. | Evidence content view. |
| [`frontend/src/components/overview/SourceEvidencePopover.tsx`](../../frontend/src/components/overview/SourceEvidencePopover.tsx) | Compact evidence preview for a finding. | Citation/source data. | Popover UI and selection. |
| [`frontend/src/components/overview/MitreExplainedSimply.tsx`](../../frontend/src/components/overview/MitreExplainedSimply.tsx) | Explains optional technical context in non-evidence language. | MITRE applicability/context state. | External-context explanation; no incident conclusion. |
| [`frontend/src/components/materials/CaseNativeMaterialsView.tsx`](../../frontend/src/components/materials/CaseNativeMaterialsView.tsx) | Lists Case-owned documents, extraction revisions, admitted evidence, and archive/admission actions. | Case material/evidence query data and action callbacks. | Native Case material UI; no Chat message inference. |
| [`frontend/src/components/materials/CaseMaterialsView.tsx`](../../frontend/src/components/materials/CaseMaterialsView.tsx) | Projects legacy message-derived materials for the compatibility Chat path. | Persisted messages and projected materials. | Legacy material cards and evidence navigation. |
| [`frontend/src/components/technical/TechnicalContextView.tsx`](../../frontend/src/components/technical/TechnicalContextView.tsx) | Displays optional RAG/MITRE context and its availability/applicability status. | Technical-context projection, source links. | Clearly isolated external context UI. |

The native analytical views are projections over persisted Case contracts; the compatibility Chat views project `ChatThreadDetail`. Neither path infers a person, event, timeline, or legal conclusion that the backend did not provide.

### Report and technical-context views

| File | Why it exists | Receives | Sends / collaborates |
| --- | --- | --- | --- |
| [`frontend/src/components/report/CaseReportView.tsx`](../../frontend/src/components/report/CaseReportView.tsx) | Native Case report workspace controller. | Case ID, selected result, report query/mutations, status/error callbacks. | Case-scoped report/PDF transport; renders result-bound history/card/empty state. |
| [`frontend/src/components/report/ChatReportView.tsx`](../../frontend/src/components/report/ChatReportView.tsx) | Compatibility Chat report workspace controller. | Active thread ID, report query/mutations, status/error callbacks. | Chat-scoped report transport for legacy/history rows. |
| [`frontend/src/components/report/PersistedReportCard.tsx`](../../frontend/src/components/report/PersistedReportCard.tsx) | Renders one persisted Case or compatibility report version. | `ChatReportRead`. | Structured report sections, validation/status/source metadata. |
| [`frontend/src/components/report/ReportHistory.tsx`](../../frontend/src/components/report/ReportHistory.tsx) | Renders report versions and selection. | Report list, selected ID, callbacks. | Report selection. |
| [`frontend/src/components/report/ReportEmptyState.tsx`](../../frontend/src/components/report/ReportEmptyState.tsx) | Explains missing/ineligible report state and next action. | Analysis/readiness/status callbacks. | Generate/open-intake action. |
| [`frontend/src/components/technical/TechnicalContextView.tsx`](../../frontend/src/components/technical/TechnicalContextView.tsx) | Technical-context workspace view. | Messages, RAG/ATT&CK projection, evidence callbacks. | External-context cards/labels and source links. |

### Chat route, submission, polling, and deletion modules

| File | Why it exists | Receives | Sends / collaborates |
| --- | --- | --- | --- |
| [`frontend/src/features/chat/routing/chat-route.ts`](../../frontend/src/features/chat/routing/chat-route.ts) | Parses `/case`/`/chat` route segments and builds workspace paths. Key symbols: `chatRouteState`, `chatPath`. | Pathname, thread ID, workspace view. | `ChatRouteState` and navigation string; current output is `/case/{threadId}/{view}`. |
| [`frontend/src/features/chat/runs/use-chat-submission.ts`](../../frontend/src/features/chat/runs/use-chat-submission.ts) | Coordinates one logical content submission, idempotency key, thread creation, accepted response, auto-title, polling, cancellation, and error state. Key symbol: `useChatSubmission`. | Session callbacks, thread list, content/kind/follow-up/source data. | `createChatMessage`, accepted message/run, `monitorThread`, title update, draft lifecycle. |
| [`frontend/src/features/chat/runs/chat-polling.ts`](../../frontend/src/features/chat/runs/chat-polling.ts) | Implements the single shared polling loop. Key symbols: `waitForNextChatPoll`, `isChatRequestCanceled`, `pollChatThreadUntilSettled`. | Thread/run IDs, abort/current guards, detail reader, apply callback. | Repeated thread/run reads and settled detail or failure message. |
| [`frontend/src/features/chat/workspace/chat-retry-request.ts`](../../frontend/src/features/chat/workspace/chat-retry-request.ts) | Restores a safe retry payload from persisted interrupted state. Key symbol: `restoreInterruptedSubmission`. | `ChatThreadDetail`. | `PendingChatSubmission` or null for retry UI. |

### Frontend transport and API types

| File | Why it exists | Receives | Sends / collaborates |
| --- | --- | --- | --- |
| [`frontend/src/lib/api-client.ts`](../../frontend/src/lib/api-client.ts) | Central Axios transport for auth, chat, run, report, and PDF operations. Key symbols: `getApiBaseUrl`, all `*Chat*` functions, auth functions, `getApiErrorMessage`. | Typed IDs/payloads, optional abort signals, idempotency keys. | HTTP requests with `withCredentials`; typed JSON, `Blob`, or normalized error message. |
| [`frontend/src/lib/api-types.ts`](../../frontend/src/lib/api-types.ts) | Frontend aliases/extensions over generated OpenAPI types plus hand-maintained report/auth contracts. | Generated declarations and local type definitions. | Compile-time shapes shared by components/hooks/client. |
| [`frontend/src/lib/api.ts`](../../frontend/src/lib/api.ts) | Single re-export façade for API client, API types, and document ingestion. | Module imports. | Stable import path used by feature code. |
| [`frontend/src/lib/generated/CaseNarrativeDocumentPageSpan.ts`](../../frontend/src/lib/generated/CaseNarrativeDocumentPageSpan.ts), [`CaseNarrativeDocumentSource.ts`](../../frontend/src/lib/generated/CaseNarrativeDocumentSource.ts) | Generated document provenance contracts. | Backend OpenAPI schema. | Type information for document-source binding; do not hand edit. |
| [`frontend/src/lib/generated/CaseRead.ts`](../../frontend/src/lib/generated/CaseRead.ts) | Generated standalone case aggregate contract. | Backend OpenAPI schema. | `CaseRead` type used by case transport/query modules; do not hand edit. |
| [`frontend/src/lib/generated/ChatActionMetadata.ts`](../../frontend/src/lib/generated/ChatActionMetadata.ts), [`DocumentSourceMetadata.ts`](../../frontend/src/lib/generated/DocumentSourceMetadata.ts), [`FollowUpMetadata.ts`](../../frontend/src/lib/generated/FollowUpMetadata.ts), [`MessageMetadata.ts`](../../frontend/src/lib/generated/MessageMetadata.ts), [`RagAttemptMetadata.ts`](../../frontend/src/lib/generated/RagAttemptMetadata.ts) | Generated message metadata contracts. | Backend OpenAPI schema. | Compile-time metadata shapes for projections/client types; do not hand edit. |
| [`frontend/src/lib/generated/ChatMessageAccepted.ts`](../../frontend/src/lib/generated/ChatMessageAccepted.ts), [`ChatMessageCreate.ts`](../../frontend/src/lib/generated/ChatMessageCreate.ts), [`ChatMessageRead.ts`](../../frontend/src/lib/generated/ChatMessageRead.ts), [`ChatRetryRequest.ts`](../../frontend/src/lib/generated/ChatRetryRequest.ts), [`ChatRunRead.ts`](../../frontend/src/lib/generated/ChatRunRead.ts) | Generated message/run request and response contracts. | Backend OpenAPI schema. | Transport typing for `api-client` and retry state; do not hand edit. |
| [`frontend/src/lib/generated/ChatThreadDetail.ts`](../../frontend/src/lib/generated/ChatThreadDetail.ts), [`ChatThreadRead.ts`](../../frontend/src/lib/generated/ChatThreadRead.ts) | Generated thread contracts. | Backend OpenAPI schema. | Thread list/detail typing; do not hand edit. |

The exact generated-file names can vary with the OpenAPI generator output; [`SYMBOL_INDEX.md`](SYMBOL_INDEX.md) is the authoritative list for the current checkout. Regenerate through the frontend API-type script when the backend schema changes rather than editing generated declarations manually.

### React Query and browser state

| File | Why it exists | Receives | Sends / collaborates |
| --- | --- | --- | --- |
| [`frontend/src/hooks/use-chat-queries.ts`](../../frontend/src/hooks/use-chat-queries.ts) | Defines chat query keys, thread list query, and create/update/delete mutations. Key symbols: `sortThreads`, `useChatThreads`, `useChatThreadMutations`. | API functions, thread IDs/titles, QueryClient. | Sorted cache data and mutation lifecycle callbacks. |
| [`frontend/src/hooks/use-case-queries.ts`](../../frontend/src/hooks/use-case-queries.ts) | Defines native Case query keys, material/evidence/result/clarification/report reads, and Case CRUD/action mutations. | Case API functions, Case IDs/payloads, QueryClient. | Independent Case caches and safe invalidation; Chat cache is touched only when the optional transcript is opened. |
| [`frontend/src/hooks/use-account-state.ts`](../../frontend/src/hooks/use-account-state.ts) | Account-scoped JSON state hook used by intake. | Logical key, initial value, setter. | Local state/storage subscription. |
| [`frontend/src/lib/document-ingestion-store.ts`](../../frontend/src/lib/document-ingestion-store.ts) | External browser store for selected file, mode, processing, preview result, error, hydration, and reset. | Case key, file/mode/events. | Local `DocumentIngestionState`; no server persistence. |
| [`frontend/src/lib/document-ingestion.ts`](../../frontend/src/lib/document-ingestion.ts) | Defines browser preview contracts and calls the protected preview route. Key symbols: `generateOcrIdempotencyKey`, `previewDocumentIngestion`. | File, mode, optional signal/case/idempotency key. | FormData request and `IngestedDocumentPreview`. |

## Frontend projection and contract files

These files explain how server data becomes UI data. They do not create new authoritative case state.

| File | Why it exists | Receives | Sends / collaborates |
| --- | --- | --- | --- |
| [`frontend/src/lib/case-evidence.ts`](../../frontend/src/lib/case-evidence.ts) | Canonical classifier for authoritative case-material messages. Key symbols: `getCaseEvidenceKind`, `isCaseEvidenceMessage`, `getCaseEvidencePresentation`. | Persisted message. | Evidence kind/presentation; excludes ordinary analyst asks. |
| [`frontend/src/lib/case-intake-model.ts`](../../frontend/src/lib/case-intake-model.ts) | Builds intake material cards and intake readiness/status. Key symbols: `intakeMaterials`, `intakeStatus`. | Messages, ingestion state, optional draft source. | Intake material/status model for `CaseIntakeView`. |
| [`frontend/src/lib/case-narrative-document.ts`](../../frontend/src/lib/case-narrative-document.ts) | Converts preview data into reviewed narrative/source metadata and exact page spans. Key symbols: `buildCaseNarrativeDraft`, `bindCaseNarrativeDocumentSource`. | Ingestion preview, edited narrative, page text/hash. | `CaseNarrativeDocumentSource` for the message request. |
| [`frontend/src/lib/intake-readable-text.ts`](../../frontend/src/lib/intake-readable-text.ts) | Sanitizes/normalizes text for readable intake display. | Extracted or persisted text. | Display-only readable copy. |
| [`frontend/src/lib/case-materials.ts`](../../frontend/src/lib/case-materials.ts) | Projects evidence messages into material records. Key symbols: `formatTimestamp`, `buildCaseMaterials`. | Persisted messages. | `CaseMaterialsData` for materials view. |
| [`frontend/src/lib/case-overview-contracts.ts`](../../frontend/src/lib/case-overview-contracts.ts) | Defines frontend overview/group/finding/gap metadata contracts. | Typed projection values. | Compile-time contracts for overview components. |
| [`frontend/src/lib/case-overview-parsing.ts`](../../frontend/src/lib/case-overview-parsing.ts) | Parses and validates persisted overview metadata without inventing v3 semantics. | Message metadata/trace values. | Validated/unsupported overview state. |
| [`frontend/src/lib/case-overview-v3.ts`](../../frontend/src/lib/case-overview-v3.ts) | Handles canonical v3 trace projection. | Validated `analysis_trace_v3` metadata. | Structured findings, claims, gaps, citations, and counts. |
| [`frontend/src/lib/case-overview.ts`](../../frontend/src/lib/case-overview.ts) | Main client-side overview projection and status selection. Key symbol: `buildCaseOverview`. | Messages and thread status. | `CaseOverviewData` for intake/overview/report readiness. |
| [`frontend/src/lib/chat-followup.ts`](../../frontend/src/lib/chat-followup.ts) | Reads follow-up metadata and terminal assistant questions. | Persisted messages/metadata. | `ActiveChatFollowUp` for action card and submission. |
| [`frontend/src/lib/mitre-candidate.ts`](../../frontend/src/lib/mitre-candidate.ts) | Parses optional candidate MITRE associations from assistant metadata. | Persisted metadata. | External-context candidate projection. |
| [`frontend/src/lib/technical-context.ts`](../../frontend/src/lib/technical-context.ts) | Projects RAG applicability/status/context/MITRE data. | Persisted messages and retrieval metadata. | `TechnicalContextData` for technical view. |
| [`frontend/src/lib/analysis-citations.ts`](../../frontend/src/lib/analysis-citations.ts) | Resolves source references attached to an analysis message. Key symbol: `sourceReferencesForAnalysisMessage`. | Analysis message and message list. | Source reference list for evidence UI. |
| [`frontend/src/lib/evidence-citation.ts`](../../frontend/src/lib/evidence-citation.ts) | Parses evidence citation metadata and display labels. | Citation/source metadata. | Citation view model. |
| [`frontend/src/lib/user-facing-error.ts`](../../frontend/src/lib/user-facing-error.ts) | Maps transport/domain failures to actionable UI categories. | Unknown error/API response. | Meaningful error model for modal/status UI. |
| [`frontend/src/lib/sha256.ts`](../../frontend/src/lib/sha256.ts) | Computes browser-side text/hash support for document-source binding. | Text/bytes. | Hash string used as a provenance input, not authorization. |

## Frontend function handoff map

| Function | Receives | Sends to next boundary |
| --- | --- | --- |
| `chatRouteState(pathname)` | URL pathname | Selected thread/view to `ChatWorkspace`. |
| `chatPath(threadId, view)` | Case/thread ID and view | URL string to the registered dynamic Case route. |
| `useCases()` | Query lifecycle | `listCases` → Case list cache. |
| `useCaseWorkspaceQueries(caseId)` | Case ID and Query lifecycle | Case/material/evidence/analysis/clarification/report reads → independent Case caches. |
| `useCaseRunPolling(caseId, runId)` | Case/run IDs and current-selection guards | Case run/result reads → settled Case state and invalidation. |
| `openCaseChat(caseId)` | Case ID | `POST /cases/{id}/chat` → optional ChatThread cache/selection. |
| `useChatThreads()` | Compatibility Chat query lifecycle | `listChatThreads` → optional transcript list cache. |
| `useChatThreadSelection.selectThread(threadId)` | Thread ID | `getChatThread` → sorted detail → draft/projection/layout. |
| `useCaseWorkspaceActions.submitCase(data)` | Native Case material/analysis input | Case document/evidence/analysis transport; no Chat message required. |
| `useWorkspaceSubmissionActions.submitCase(data)` | Compatibility intake title/narrative/source | `submitContent` with message content and source list. |
| `useChatSubmission.submitContent(...)` | Content, kind, action, selection, source | `createChatThread` if needed → `createChatMessage` → `monitorThread`. |
| `createChatMessage(...)` | Thread ID, content, idempotency key, action, sources | `POST /chats/{id}/messages` → accepted message/run. |
| `pollChatThreadUntilSettled(...)` | Thread/run IDs and current-selection guards | `getChatThread` + `getChatRun` → `applyThreadDetail`. |
| `buildCaseOverview(messages, status)` | Legacy persisted detail | Compatibility Overview data to intake/overview/report readiness. |
| `buildNativeCaseOverview(result, snapshot)` | CaseAnalysisResult and pinned snapshot | Native Overview data with typed source/revision citations and freshness. |
| `buildCaseMaterials(messages)` | Legacy persisted detail | Compatibility materials data to `CaseMaterialsView`. |
| `technicalContext(messages)` | Persisted metadata | External-context data to `TechnicalContextView`. |
| `generateChatReport(threadId, key)` | Thread ID/idempotency key | `POST /chats/{id}/reports` → persisted report. |
| `downloadChatReportPdf(threadId, reportId)` | IDs | `GET .../pdf` → browser `Blob`. |

## Frontend tests and build tooling

| Test/tool group | Files / coverage | What it proves |
| --- | --- | --- |
| Workspace and auth UI | [`frontend/src/test/components/home/HomePage.test.tsx`](../../frontend/src/test/components/home/HomePage.test.tsx), [`frontend/src/test/components/layout/WorkspaceSidebar.test.tsx`](../../frontend/src/test/components/layout/WorkspaceSidebar.test.tsx), auth/common component tests in the index | Authentication-aware navigation, sidebar selection/delete, dialogs, and presentation contracts. |
| Intake and evidence | [`frontend/src/test/features/chat/ChatWorkspaceIntake.test.tsx`](../../frontend/src/test/features/chat/ChatWorkspaceIntake.test.tsx), [`frontend/src/test/lib/case-evidence.test.ts`](../../frontend/src/test/lib/case-evidence.test.ts), [`case-narrative-document.test.ts`](../../frontend/src/test/lib/case-narrative-document.test.ts), [`case-materials.test.ts`](../../frontend/src/test/lib/case-materials.test.ts) | Intake submission, authoritative evidence classification, source binding, and materials projection. |
| Overview and citations | [`frontend/src/test/components/overview/CaseOverviewView.test.tsx`](../../frontend/src/test/components/overview/CaseOverviewView.test.tsx), [`frontend/src/test/lib/case-overview.test.ts`](../../frontend/src/test/lib/case-overview.test.ts), [`frontend/src/test/lib/evidence-citation.test.ts`](../../frontend/src/test/lib/evidence-citation.test.ts), [`analysis-retirement.test.ts`](../../frontend/src/test/lib/analysis-retirement.test.ts) | Canonical v3 projection, legacy retirement labels, citation display, and evidence navigation. |
| Chat lifecycle | [`frontend/src/test/features/chat/chat-polling.test.ts`](../../frontend/src/test/features/chat/chat-polling.test.ts), [`chat-session-selection.test.tsx`](../../frontend/src/test/features/chat/chat-session-selection.test.tsx), [`chat-submission-retry.test.tsx`](../../frontend/src/test/features/chat/chat-submission-retry.test.tsx), [`chat-interrupted-retry.test.tsx`](../../frontend/src/test/features/chat/chat-interrupted-retry.test.tsx), [`chat-thread-deletion.test.tsx`](../../frontend/src/test/features/chat/chat-thread-deletion.test.tsx) | Selection cancellation, single polling loop, retry identity, interrupted runs, draft isolation, and deletion coordination. |
| Routes and report/technical UI | [`frontend/src/test/features/chat/chat-route.test.ts`](../../frontend/src/test/features/chat/chat-route.test.ts), [`frontend/src/test/components/report/ChatReportView.test.tsx`](../../frontend/src/test/components/report/ChatReportView.test.tsx), [`PersistedReportCard.test.tsx`](../../frontend/src/test/components/report/PersistedReportCard.test.tsx), [`TechnicalContextView.test.tsx`](../../frontend/src/test/components/technical/TechnicalContextView.test.tsx) | Route helper mapping, report idempotency/UI state, PDF action, and external-context labeling. |
| Projection libraries | Remaining `frontend/src/test/lib/*` files listed in [`SYMBOL_INDEX.md`](SYMBOL_INDEX.md) | Pure helper contracts for follow-up, MITRE, technical context, errors, and citation parsing. |
| Static/build tooling | [`frontend/scripts/generate-api-types.mjs`](../../frontend/scripts/generate-api-types.mjs), [`frontend/next.config.ts`](../../frontend/next.config.ts), [`frontend/tailwind.config.ts`](../../frontend/tailwind.config.ts), [`frontend/eslint.config.mjs`](../../frontend/eslint.config.mjs), [`frontend/vitest.config.ts`](../../frontend/vitest.config.ts), [`frontend/postcss.config.mjs`](../../frontend/postcss.config.mjs) | Generated API types, Next build, styling, lint, test, and PostCSS configuration. |

The index contains each of the 43 frontend test files and every test symbol. Test success for a route helper is not equivalent to a successful Next.js route registration; the distinction matters for the current route caveat below.

## Verified route surface

The Case-first workspace uses a dynamic App Router view path rather than a separate page file for every workspace tab. The layout mounts `ChatWorkspace`, which selects the native Case view from the pathname and keeps the route shell independent from Chat data.

| Evidence | Current code fact |
| --- | --- |
| [`frontend/src/features/chat/routing/chat-route.ts`](../../frontend/src/features/chat/routing/chat-route.ts) | `chatPath(threadId, view)` emits `/case/{threadId}/{view}`. |
| [`frontend/src/app/case/[threadId]/[view]/page.tsx`](../../frontend/src/app/case/[threadId]/[view]/page.tsx) | Registers the dynamic Case view route used by Overview, Intake, Materials, Report, Technical Context, and Chat navigation. |
| [`frontend/src/app/case/layout.tsx`](../../frontend/src/app/case/layout.tsx) | Mounts `ChatWorkspace` for the Case route family; the client workspace renders the selected view. |
| [`frontend/src/app/chat/layout.tsx`](../../frontend/src/app/chat/layout.tsx) | Redirects legacy `/chat...` paths to the equivalent `/case...` paths while preserving compatibility selection. |
| `npm run build` | Next.js production compilation confirms `/case`, `/case/[threadId]`, `/case/[threadId]/[view]`, and legacy Chat routes are registered. |

The dynamic page components are intentionally route shells; Case data and view rendering belong to `ChatWorkspace` and its native child components. Helper tests do not replace production route compilation or live route smoke testing.

## Private RAG boundary

The repository contains a substantial `rag_service` source tree and regression suite. It is intentionally outside the backend/frontend public contract in this guide. The relevant integration is:

```text
backend workflow
    → backend rag_client
    → private rag_service /query
    → QueryResponse
    → validated RagContextPayload
    → PostgreSQL RagContext + assistant metadata
    → frontend technical-context projection
```

The frontend never imports the RAG service, calls its URL, or decides whether retrieval is applicable. The backend adapter and workflow own that decision. For the file/function inventory of the private service, use the `GraphRAG` and `GraphRAG Regression Suite` sections of [`SYMBOL_INDEX.md`](SYMBOL_INDEX.md); do not infer browser integration from those entries.

## Maintenance and change tracing

When changing the integration, update the smallest contract owner first and trace outward:

1. Change or verify the backend Pydantic schema and route registration.
2. Export the OpenAPI contract and regenerate frontend declarations.
3. Update `api-types.ts` only for intentional frontend aliases/projections.
4. Update the central `api-client.ts` transport function and its caller hook.
5. Update the persisted metadata/projection only when the backend contract actually changed.
6. Add or adjust the narrow backend/frontend boundary test.
7. Re-run the symbol index and confirm the route tree, imports, and public endpoint tests.

Useful checks from the repository root:

```powershell
python docs/developer-handover/generate_symbol_index.py
git diff --check
```

For an API change, also run the project’s backend route/schema tests and frontend API-type check before claiming the integration is complete. For a route change, inspect `frontend/src/app` in addition to route-helper tests. For provider or lease changes, use the focused workflow tests and a disposable database; do not use a successful static import as runtime proof.

## Current verification record

The current Case-first checkout was validated on 2026-09-10 with backend pytest `450 passed, 1 skipped, 2 subtests passed` against the Docker PostgreSQL instance, frontend Vitest `165 passed across 40 files`, generated API-type drift check, TypeScript, scoped ESLint, Next.js production build, Python compileall, and `git diff --check` passing. Full frontend lint still has two unrelated pre-existing errors in `AccountForm.tsx` and `HomeSections.tsx` plus the existing avatar warning. A disposable populated PostgreSQL migration rehearsal upgraded 0001→0010 and verified proven/unresolved report mappings, preserved IDs/hashes, and Chat deletion retention; it was destroyed afterward. Live Docker PostgreSQL remained at `0010_preserve_chat_reports (head)` with 2 existing Cases/ChatThreads and 0 native material/run/result/report rows before the coordinated rebuild. No paid provider call, OCR/HTR change, or `rag_service/**` change is part of this receipt.

## Quick navigation by task

| If you need to understand… | Start here | Then follow |
| --- | --- | --- |
| Login/session | [`frontend/src/hooks/use-auth.ts`](../../frontend/src/hooks/use-auth.ts) | [`backend/app/routers/auth.py`](../../backend/app/routers/auth.py), auth dependencies, `User`. |
| New Case intake | [`frontend/src/components/intake/CaseFirstIntakeView.tsx`](../../frontend/src/components/intake/CaseFirstIntakeView.tsx) | Case document upload/extraction review → explicit evidence admission → Case analysis; Chat is optional. |
| Why material is/isn’t evidence | [`backend/app/services/case_materials/material_service.py`](../../backend/app/services/case_materials/material_service.py) | Native EvidenceSource/Revision admission; legacy message classification is in [`frontend/src/lib/case-evidence.ts`](../../frontend/src/lib/case-evidence.ts). |
| CaseRun stuck/duplicated | [`frontend/src/hooks/use-case-run-polling.ts`](../../frontend/src/hooks/use-case-run-polling.ts) | CaseRun claim/lease/completion/recovery workflow files. |
| Main Case analysis | [`backend/app/services/workflow/case_run_execution.py`](../../backend/app/services/workflow/case_run_execution.py) | native case-analysis executor, claim-anchored package, and Case completion. |
| MITRE/RAG | [`backend/app/services/workflow/rag_routing.py`](../../backend/app/services/workflow/rag_routing.py) | [`backend/app/services/clients/rag_client.py`](../../backend/app/services/clients/rag_client.py), `rag_service` index, technical projection. |
| Evidence citations | [`backend/app/services/case_analysis/source_citations.py`](../../backend/app/services/case_analysis/source_citations.py) | frontend `analysis-citations`, `evidence-citation`, and evidence components. |
| Report generation | [`backend/app/services/reports/case_report_persistence.py`](../../backend/app/services/reports/case_report_persistence.py) | selected result snapshot → deterministic template → validation → Case report/PDF UI. |
| Route behavior | [`frontend/src/features/chat/routing/chat-route.ts`](../../frontend/src/features/chat/routing/chat-route.ts) | physical `frontend/src/app` tree and the caveat above. |
