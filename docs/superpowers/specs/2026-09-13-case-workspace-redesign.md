# CyberCase Case Workspace Redesign

Date: 2026-09-13

Status: Revision 2 for user review; implementation not started

Target branch: `main`

Baseline: `2358da3`

## 1. Outcome

CyberCase will use an English-default, three-pane Case workspace inspired by NotebookLM's source organization without adopting its Chat-centered interaction hierarchy or trust model. Thai is available as a complete switchable locale; the interface never duplicates both languages in the same label.

The permanent desktop structure is:

```text
┌────────────────────────────────────────────────────────────────────────────┐
│ CyberCase | Cases | Case title | Meaningful Case status | Account/actions │
├───────────────────┬──────────────────────────────┬─────────────────────────┤
│ Case Sources      │ Case Work                    │ Contextual Chat         │
│                   │                              │                         │
│ Uploaded files    │ Analysis                     │ Normal ASK              │
│ Narrative sources │ Information needed           │ or follow-up answer     │
│ Source selection  │ Technical context            │                         │
│                   │ Report                       │ Collapsible             │
└───────────────────┴──────────────────────────────┴─────────────────────────┘
```

The left Sources pane keeps its width and context while the center Case Work surface changes. Case Work receives the largest flexible region and is the default focus after entering a Case. Chat remains mounted on the right so its transcript and draft are not lost, but it may collapse to a narrow rail when it is not needed.

The hierarchy follows the investigator's real loop:

```text
Evidence → Analysis → Gap → Investigation → New Evidence → Revised Analysis
```

This is a Case workspace with contextual Chat:

- Sources are Case-owned.
- Analysis and reports are Case-owned.
- Chat has no independent user-facing lifecycle.
- A normal Chat question does not modify evidence.
- Only an explicit answer to a persisted follow-up question becomes evidence.
- A visible empty Chat shell does not create a `ChatThread` until the user actually opens or uses Chat, unless analysis already created one to publish a follow-up.
- Collapsing Chat changes presentation only; it does not destroy Chat state or affect Case processing.

## 2. Success Criteria

The redesigned workspace succeeds when an investigator can answer these questions without understanding backend terminology:

1. What information has been added to this Case?
2. Which original files can I open?
3. Which material is ready for analysis?
4. What does the latest analysis conclude?
5. Which source supports or conflicts with each important finding?
6. Has new information been added since the displayed analysis?
7. What information is still needed and why?
8. Will my Chat message only ask a question, or will it become evidence?
9. Can I open an existing report, and can I safely generate a new one?
10. What should I do next if processing fails?

## 3. Scope and Non-Goals

### Phase 1 scope

- Sources left, primary Case Work center, persistent/collapsible contextual Chat right.
- One Sources experience replacing duplicated Intake and Materials presentation.
- Existing evidence admission behavior.
- Current/stale analysis communication using investigator-facing language.
- Actionable information-gap presentation and explicit follow-up Chat mode.
- Explicit reconciliation of conflicting independent evidence at the Analysis layer.
- Current analysis, conditional technical context, saved reports, and report readiness in Case Work.
- Multiple file upload interaction using the existing per-file upload API sequentially.
- Original PDF and image viewing from the Sources pane.
- Shared PDF viewer foundation for original files and reports.
- Citation navigation to the exact selected source where existing metadata permits it.
- English-default interface and generated output with a complete Thai locale switch.
- Loading, empty, processing, stale, and failure states.

### Deferred from Phase 1

- Showing OCR text as a separate visible child item.
- Editing extracted text before admission.
- Evidence correction UI and revision comparison.
- Side-by-side original/OCR review.
- DOCX-to-PDF preview conversion.
- Git-like evidence or analysis diffs.
- Cross-document semantic clustering.
- New AI agents, model controls, prompt controls, or RAG configuration UI.
- Changes to the evidence, analysis, clarification, Chat, or report ownership model.

## 4. Current UX Audit

### 4.1 What already works

The current checkout has the correct Case-owned backend foundation:

- Case CRUD and Case-scoped materials.
- Stored original document bytes and extraction records.
- Explicit evidence admission and revisioned evidence sources.
- Immutable evidence snapshots.
- Case Analysis runs and current/stale freshness.
- Persisted follow-up questions and evidence-producing answers.
- Normal Case Chat ASK runs that do not mutate evidence.
- Case-scoped report persistence and PDF delivery.
- Analysis history read endpoints.

The frontend already contains reusable analysis, citation, Chat, technical-context, report, state, and error components.

### 4.2 Confusing or duplicated flows

#### Intake and Materials overlap

`CaseFirstIntakeView` and `CaseNativeMaterialsView` both upload documents, show extraction/admission status, and lead toward analysis. Intake also combines adding a narrative with starting analysis. The user therefore cannot easily distinguish preparing evidence from analyzing it.

The redesign removes Intake as a permanent destination. Empty-case onboarding is rendered inside Sources and Case Work. After the first source is added, the same workspace remains in place.

#### Overview carries too many responsibilities

`CaseOverviewView` combines the Case title, summary, findings, gaps, source inspection, MITRE context, run state, stale state, and report actions. It behaves as both dashboard and analysis document.

The redesign divides those responsibilities:

- Compact state and next actions live in the Case Work header and unresolved-work summary.
- Full analysis opens as the primary Case Work document.
- Source viewing stays in Sources.
- Follow-up answering stays in Chat.

#### Follow-up hides useful analysis

When a clarification is pending, the current Overview replaces the complete analysis with a blocking state screen. The investigator loses the existing findings and source context.

The redesign keeps the last successful analysis readable, shows the material gap in Case Work, and focuses the persisted follow-up question in Chat.

#### Freshness is local rather than workspace-wide

The current stale warning is useful but mostly limited to Overview. The Case list, header, Chat context, and Report action do not consistently expose the same meaning.

The redesign maps backend freshness to plain-language workspace states:

- `current` → `Up to date`
- `stale` → `New information was added after this analysis`
- `missing` with evidence → `Ready to analyze`
- queued/running → `Analyzing`
- failed without a result → `Analysis failed`
- failed with an earlier result → `Latest analysis failed · Previous result remains available`

Raw evidence revision numbers remain available only in details/history.

#### Citation navigation lacks a destination target

The current navigation can switch to Materials but does not retain a selected source, expand the correct file, or focus a cited page/quote consistently.

The redesign introduces source-focused navigation state:

```text
Citation click
→ preserve the active analysis
→ select the source in Sources
→ open the original-file viewer when available
→ focus the cited page when page metadata exists
```

#### Report generation can expose a stale action

The current report UI checks validated status but does not include analysis freshness in its generation predicate. The backend correctly rejects stale report generation, but the frontend can still offer the action.

The redesign disables new report generation when analysis is stale while keeping every saved report readable.

### 4.3 Chat-first remnants to retire

- `ChatWorkspace` and `ChatWorkspaceLayout` name the entire Case workspace after Chat.
- Several view props still use `threadId` for Case identity.
- Legacy message-derived and native Case branches coexist in presentation components.
- Some empty or progress states route the user to Chat when Sources or Case Work is the truthful destination.
- Legacy Materials paths can still describe content as coming from Chat.

These are migration targets, not justification for backend changes.

## 5. Information Architecture

### 5.1 Global Case header

The top header contains only global and Case-level context:

- CyberCase identity.
- Return to Case list.
- Active Case title.
- One meaningful status sentence or chip.
- Account and Case actions.

It does not contain a second permanent navigation row. Sources, Case Work, and Chat are the workspace itself.

### 5.2 Sources pane

The permanent left pane contains:

- `Add sources`.
- Uploaded original documents.
- User-authored narrative sources.
- Plain-language readiness status.
- Source selection.
- Original-file opening.
- Evidence admission when the current backend exposes an extraction ready for admission.
- Source details/history under progressive disclosure.

The list does not expose UUIDs, hashes, extraction provider configuration, or revision numbers by default.

### 5.3 Center Case Work

Case Work is the primary working surface and receives the largest flexible width. It presents the current analytical state as a readable working document rather than a grid of equal dashboard cards.

Its applicable sections are:

- Analysis.
- Information needed.
- Conditional technical context.
- Preliminary report.

Analysis is the dominant center artifact. Information Needed appears adjacent to the affected finding and also in a concise unresolved-work summary. Technical context and Report remain secondary artifacts below or beside Analysis according to available width.

When no analysis exists, the center surface explains readiness and presents one next action. When analysis exists, it stays readable during re-analysis, stale states, and recoverable failures.

### 5.4 Right contextual Chat

The right pane contains:

- Transcript.
- Draft-preserving composer.
- Normal ASK mode.
- Explicit follow-up-answer mode.
- Citations that open Sources.
- A context notice when the current analysis is stale.
- An empty shell before Chat exists.
- An explicit collapse/expand control.

Chat is expanded when the investigator opens it or chooses `Answer in Chat`. Otherwise it may collapse to a labeled rail. The panel remains mounted while collapsed so transcript, draft, scroll position, and follow-up context survive. Collapsing it never creates or deletes a `ChatThread`.

Sources remains stable when Chat expands. Case Work yields some horizontal space but remains the visual center and never becomes a hidden secondary panel on desktop.

## 6. Visual System

### 6.1 Direction

The visual language is a restrained investigation workspace:

- Document-oriented rather than dashboard-oriented.
- The analytical working document is the visual anchor; Chat chrome is quieter and subordinate.
- High-contrast monochrome surfaces.
- Color reserved for meaning.
- Few container styles with hierarchy created by spacing, rules, and pane behavior.
- No giant hero, glassmorphism, gradients, decorative analytics, or repeated SaaS cards.

### 6.2 Core tokens

| Token | Value | Use |
| --- | --- | --- |
| Charcoal | `#171717` | Primary text and primary actions |
| Paper | `#F5F5F4` | Workspace canvas |
| White | `#FFFFFF` | Reading surfaces and panes |
| Line | `#D6D3D1` | Structural boundaries |
| Evidence blue | `#315E7D` | Source links, active evidence focus, processing |
| Unresolved amber | `#9A5B13` | Gaps, stale analysis, review required |

Critical failure may use a restrained red semantic token. MITRE context may use a reserved violet accent only where external technical context must be distinguished from Case evidence.

### 6.3 Typography

- Primary English UI family: `IBM Plex Sans`.
- Thai locale family: `Noto Sans Thai`, matched to the English scale, weight, and vertical rhythm.
- Technical identifiers use monospace only inside expanded technical details.
- Sentence case replaces decorative uppercase eyebrows.
- Long analysis text uses a comfortable reading width and line height.
- Buttons use direct English actions such as `Add sources`, `Start analysis`, `Answer in Chat`, and `Generate report`.

### 6.4 Language model

- Interface locale and generated-output language are separate settings.
- The initial default for both settings is English.
- The interface can switch completely between English and Thai; bilingual labels are not shown simultaneously.
- Original source documents, filenames, quotes, and user-authored narratives remain in their original language.
- The selected generated-output language is sent through the existing `response_language` contract for analysis, clarification, and Chat requests. Reports preserve the language of their persisted analysis input unless a future report-language contract is approved.
- Changing the interface locale does not silently regenerate or translate persisted Case artifacts.
- All user-facing copy is stored behind locale keys from Phase 1A; Phase 1C completes the Thai catalog and locale-switching QA. New components do not hardcode mixed-language strings.
- The two language controls live in the header account/settings menu rather than adding another navigation row.
- The locale preference persists in browser-backed account state and is applied before the workspace renders to avoid a language flash.

### 6.5 Motion

- Pane expansion is the one memorable motion system.
- Source and Case Work panes animate only in response to explicit user actions.
- Loading uses a quiet inline progress treatment.
- Reduced-motion preferences remove width animation and use an immediate layout change.

## 7. Primary User Journey

### 7.1 Create Case

1. User creates a Case.
2. Workspace opens with empty Sources, an inactive Chat shell, and Case Work guidance.
3. Primary action is `Add sources`.

### 7.2 Add material

1. User uploads one or more files or adds a narrative.
2. Each file appears in Sources immediately with a truthful processing state.
3. Upload and extraction failures remain attached to the affected source rather than replacing the whole workspace.

### 7.3 Admit evidence

1. User sees which document-derived material is ready for admission.
2. User admits the available extraction using the existing Case evidence contract.
3. Source status changes to `Ready`.
4. Case Work offers `Start analysis` when at least one active evidence source exists.

Phase 1 does not display or edit OCR text as a separate source artifact.

### 7.4 Run analysis

1. User starts analysis from Case Work.
2. The Analysis card changes to `Analyzing`.
3. Sources and Chat remain usable.
4. If an older successful result exists, it remains readable with a clear notice.

### 7.5 Review results

1. The successful Analysis surface shows either `Up to date` or `New information available`.
2. User opens the full result in the primary center Case Work surface.
3. Summary, findings, impacts, source links, and gaps are arranged as a readable analytical document.
4. Citations open the corresponding source in the left viewer.

### 7.6 Resolve a material gap

1. Case Work shows one actionable Information Needed card.
2. The card states what is missing, why it matters, and what conclusion it affects.
3. `Answer in Chat` expands the right Chat panel and focuses the persisted follow-up question.
4. Chat visibly switches from ASK mode to evidence-answer mode.
5. Composer copy explicitly states that the answer will be added as Case evidence.
6. Submission admits the answer and starts the next analysis run using the current backend workflow.

### 7.7 Reconcile conflicting independent evidence

1. S1 states that Person A operated the workstation.
2. S2 independently states that Person B operated the workstation.
3. Both sources remain admitted and independently attributed; neither is edited, corrected, or superseded.
4. Re-analysis represents the operator identity finding as `Conflicting` and `Not established`.
5. The affected finding shows both opposing source statements and an Information Needed prompt asking which identification is correct and what evidence confirms it.
6. `Answer in Chat` opens evidence-answer mode for that exact persisted question.
7. The answer is admitted as S3 and triggers re-analysis.
8. The new Analysis Result reconciles S1, S2, and S3 while the earlier result and all three evidence sources remain preserved.

### 7.8 Re-analysis

1. The answer appears as a separate user-authored evidence source.
2. The previous analysis remains readable during processing.
3. The next successful result becomes current.
4. The previous result remains available in history.

### 7.9 Report

1. Saved reports remain readable at all times.
2. A new report can be generated only from a current validated analysis.
3. If evidence changed, Case Work explains that analysis must be refreshed first.
4. The Report artifact reuses the shared PDF viewer.

## 8. UI State Transition Map

| State | User-facing presentation | Primary action | Next state |
| --- | --- | --- | --- |
| A. Empty Case | `No sources yet` | `Add sources` | B or C |
| B. Files uploaded, not admitted | Per-source processing/admission state | `Admit as evidence` | C |
| C. Evidence, no analysis | `Ready to analyze` | `Start analysis` | D |
| D. Processing | Inline progress; previous result preserved | None or `Open previous result` | E, F, or L |
| E. Completed, no gaps | Current analysis card | `Open analysis` | K or I |
| F. Follow-up required, including conflict reconciliation | Actionable Information Needed linked to the affected finding | `Answer in Chat` | G |
| G. Answering follow-up | Evidence-answer Chat mode | `Submit answer and re-analyze` | H |
| H. Answer admitted/re-analysis | New source plus processing state | `Open previous result` | J or L |
| I. Analysis stale | `New information was added after this analysis` | `Analyze latest evidence` | D |
| J. New current analysis | New result primary; old result in history | `Open analysis` | K or I |
| K. Report available | Saved report card and PDF | `Open report` or `Generate new report` | K |
| L. Failure | Plain-language failure and retry guidance | `Try analysis again` | D |

States K and technical context can coexist with E, F, I, or J. They are Case artifacts, not exclusive workflow stages.

Conflict reconciliation uses the existing states as an explicit branch:

```text
C: S1 and S2 admitted
→ D: analyze
→ F: finding is CONFLICTING / NOT ESTABLISHED; reconciliation question shown
→ G: investigator answers the exact question in Chat
→ H: answer is admitted as independent source S3; re-analysis starts
→ J: revised current analysis reconciles S1, S2, and S3
```

S3 does not mutate or supersede S1 or S2. If S3 is insufficient, the revised result may remain conflicting or not established.

## 9. Source Viewer

### 9.1 Behavior

- Selecting an original source opens it inside the left pane.
- The pane can expand to the approved width but does not collapse merely because Case Work opens.
- The viewer supports continuous reading and browser-native PDF navigation.
- Closing the viewer returns to the source list without changing Chat or Case Work state.
- Citation navigation can open the selected file and page.

### 9.2 Shared viewer architecture

The current `ReportPdfViewer` is private inside `PersistedReportCard`. Phase 1B should extract the transport-independent behavior into focused modules:

```text
DocumentViewerShell
├── PdfDocumentViewer
├── ImageDocumentViewer
└── UnsupportedDocumentNotice
```

`PdfDocumentViewer` owns:

- Blob URL creation.
- Blob URL revocation.
- Loading state.
- Retry behavior.
- Secure iframe rendering.
- Accessible title and empty/failure state.

The Report surface and Source Viewer provide different fetch functions but use the same PDF component.

### 9.3 Supported formats

- PDF: inline preview through the shared PDF viewer.
- PNG/JPEG: inline preview through the image viewer.
- DOCX: download or open externally in Phase 1B.

The UI must not imply that DOCX is previewable inline until a reliable conversion contract exists.

## 10. Chat Modes

### 10.1 Normal ASK

User-facing notice:

`Ask about the current analysis. This message will not be added as evidence.`

Behavior:

- Requires a completed Analysis Result.
- Binds the ASK run to the selected/current result.
- Does not modify evidence.
- Does not start Main Case Analysis.

### 10.2 Follow-up answer

User-facing notice:

`This information is needed to continue the Case analysis. Your answer will be added as evidence.`

Behavior:

- Displays the persisted question and why it matters.
- Replies to the exact question message.
- Preserves the originating result identity.
- Admits the answer as a separate evidence source.
- Starts re-analysis.

No generic composer choice should let a normal ASK accidentally become evidence.

## 11. Case Work Artifacts

### 11.1 Analysis surface

Compact states:

- No result: `Ready to analyze`.
- Processing: `Analyzing`.
- Current: `Up to date`.
- Stale: `New information available`.
- Failed without result: `Analysis failed`.
- Failed with result: `Latest analysis failed · Previous result remains available`.

Expanded content:

- Executive summary.
- Structured findings.
- Impacts.
- Supporting and conflicting citations.
- Information gaps.
- Current/history selector under progressive disclosure.

The center Analysis surface uses this hierarchy for conflicting evidence:

```text
┌─ Case Work · Analysis ───────────────────────────────────────────────┐
│ Up to date                                      Generated 09:42     │
│                                                                    │
│ Workstation operator identity                                     │
│ [Conflicting] [Not established]                                   │
│                                                                    │
│ The operator identity cannot be established from current evidence.│
│                                                                    │
│ Sources in conflict                                                │
│ S1  Person A operated the workstation.             [Open source]  │
│ S2  Person B operated the workstation.             [Open source]  │
│                                                                    │
│ Information needed                                                 │
│ Which identification is correct, and what evidence confirms it?   │
│ Why it matters: operator attribution affects the Case conclusion. │
│                                                   [Answer in Chat] │
└────────────────────────────────────────────────────────────────────┘
```

`Conflicting` comes from the related gap status and `Not established` comes from the finding's epistemic status. The UI may associate them only through the gap's validated `affected_claim_ids`; it must not infer a conflict by comparing source text in the browser.

### 11.2 Information Needed card

The compact card shows:

- Count of actionable items.
- Selected gap topic.
- Why it matters.
- `Answer in Chat`.

The card is absent when no actionable gap exists. It never presents a vague AI disclaimer.

For a `CONFLICTING` gap, the expanded Information Needed treatment also shows:

- The affected finding title and `Not established` state.
- Each opposing statement under its independently preserved source.
- The exact reconciliation question.
- Why resolving the conflict changes the analysis.
- One `Answer in Chat` action bound to the persisted follow-up question.

The card never calls one source a correction of another. A follow-up answer appears as a new source after submission.

### 11.3 Technical Context card

The card appears only when technical augmentation is applicable or when a relevant attempt failed.

It always states:

`External context · Not Case evidence`

RAG failure never blocks Analysis or Report readiness when the general Case analysis is otherwise valid.

### 11.4 Report card

The compact card communicates:

- Whether a saved report exists.
- Whether a new report can be generated.
- Why generation is unavailable when analysis is missing, processing, stale, or failed.

The expanded artifact displays the selected saved report and report history.

## 12. Progressive Disclosure

### Primary UI

Show:

- `Needs review`.
- `Ready`.
- `Processing`.
- `Up to date`.
- `New information available`.
- `Re-analysis recommended`.
- `More information needed`.
- Clear next actions.

### Details/history only

Show:

- Evidence revision number.
- Extraction revision number.
- UUIDs.
- Content and manifest hashes.
- Provider/model configuration.
- Raw pipeline metadata.
- Full processing timestamps.

## 13. Data Flow and Backend/API Impact

### 13.1 Existing contracts used without change

- Case CRUD.
- List/upload Case documents.
- Admit document extraction.
- List/add/revise/archive evidence.
- Start and poll Case Analysis.
- Read latest and historical Analysis Results.
- Read evidence snapshots.
- Ensure/read Case Chat only on actual Chat use.
- Submit normal ASK and clarification answer intents.
- List/generate/read/download Case reports.

### 13.2 Required Phase 1B backend addition

Original bytes are stored in `CaseDocument.content_bytes`, but there is no authenticated read route. Add one ownership-checked endpoint:

```http
GET /api/v1/cases/{case_id}/documents/{document_id}/content
```

Required response behavior:

- Verify the authenticated user owns the Case and document.
- Return the original bytes with the persisted MIME type.
- Use a safe `Content-Disposition` filename.
- Set `Cache-Control: no-store`.
- Return 404 for missing or cross-Case documents without leaking existence.
- Stream or return bytes without sending content through JSON.

No database migration or evidence-model change is required.

### 13.3 Phase 2 API usage

The existing Analysis Result list/detail endpoints support history. The frontend needs client/query functions, not new backend endpoints.

Evidence correction UI can use the existing evidence-revision endpoint when it is authorized later.

## 14. Component Strategy

### 14.1 Reuse

- Chat transcript, markdown rendering, retry, persistence, and submission hooks.
- Follow-up parsing and explicit intent contracts.
- Analysis finding rendering and epistemic-state labels.
- Evidence citation chips and source-content rendering.
- Technical-context parsing and status handling.
- Report queries, history, PDF download, and generation mutation.
- Case queries, polling, generated API types, error translation, dialogs, icons, and focus handling.

### 14.2 Redesign or recompose

- Replace `WorkspaceSidebar` with the three-pane shell and compact global Case header.
- Recompose `ChatWorkspaceLayout` as a Case-owned workspace shell.
- Recompose `CaseFirstIntakeView` and `CaseNativeMaterialsView` into Sources and empty-case onboarding.
- Move `CaseOverviewView` content into the expandable Analysis artifact.
- Recompose `WorkspaceChatPanel` as the persistent/collapsible right contextual pane.
- Extract the private report PDF viewer into a shared document viewer.
- Introduce source-selection/navigation state independent from Chat messages.
- Introduce a primary center Case Work controller for readiness, current Analysis, actionable gaps, technical context, and Report readiness.

### 14.3 Retire after parity is proven

- Legacy message-derived Materials presentation.
- Native-versus-legacy branching inside Case-owned views.
- Unused direct clarification form if Chat remains the only canonical answer surface.
- Chat-first naming and props where Case identity is intended.
- Old route-only views after redirects and deep-link compatibility are verified.

No production code module introduced by this redesign should exceed 300 lines. Pane state, source viewing, Chat composition, Case Work state, and artifact rendering must remain separate modules with stable interfaces.

## 15. Responsive Behavior

### Desktop

- Three panes visible.
- Sources keeps a stable width.
- Case Work owns the largest flexible width and remains the primary visual surface.
- Chat uses a bounded contextual width and can collapse to a labeled rail without unmounting.

### Medium screens

- Sources remains available.
- Case Work remains primary.
- Chat collapses by default and expands as an overlay or bounded drawer without squeezing Analysis below its readable minimum width.

### Mobile

- Use three top-level tabs ordered `Case Work`, `Sources`, `Chat`; Case Work is the default.
- Preserve state while switching tabs.
- Follow-up mode can automatically select Chat once, with a clear back path.
- Original documents use a full-screen viewer.
- Do not reproduce a squeezed three-column layout.

## 16. Error Handling

| Failure | Presentation | Recovery |
| --- | --- | --- |
| Case list load | Header-level contained state | Retry list |
| One document upload | Error attached to that pending source | Retry/remove source |
| Document extraction | Source marked `Processing failed` | Retry upload/extraction where supported |
| Original-file fetch | Viewer-only empty state | Retry or download |
| Analysis start uncertainty | Preserve input and show uncertain state | Reconcile run before resubmitting |
| Analysis run failure, no result | Analysis failure card | Retry after checking evidence |
| Analysis run failure, old result exists | Keep old result visible | Retry latest run |
| Chat ASK failure | Preserve draft and transcript | Retry same request safely |
| Follow-up answer failure | Preserve answer and evidence-mode notice | Retry same idempotent request |
| Technical augmentation failure | External-context card only | Analysis remains usable |
| New report blocked by stale analysis | Explain prerequisite before request | Analyze latest evidence |
| Saved report PDF load | Report viewer-only failure | Retry or download |

Errors use action-oriented copy in the active locale. Raw error codes and validation payloads remain inside a technical-details disclosure.

## 17. Testing Strategy

### Unit and component tests

- Case status-to-presentation mapping.
- Case Work applicable-card selection.
- Conflicting gap association uses validated `affected_claim_ids` and never browser text comparison.
- Conflicting finding renders separate S1/S2 source roles and the `Conflicting` / `Not established` states.
- Collapsing and reopening Chat preserves transcript, draft, scroll position, and follow-up mode.
- Normal ASK versus follow-up composer behavior.
- A visible Chat shell does not call ensure/get Chat automatically.
- Source selection preserves Chat state.
- PDF Blob URL creation and revocation.
- Image viewer accessibility and fit behavior.
- Unsupported DOCX notice and download action.
- Stale Analysis disables new Report generation.
- Citation selection opens the expected source/page.
- Technical context never appears as Case evidence.
- English-default and Thai-localized empty, failure, and recovery copy.
- Locale switching changes interface copy without changing persisted source or analysis content.
- Generated-output language remains independent from the interface locale.

### Backend tests

- Original document content requires authentication and Case ownership.
- Cross-Case document IDs return 404.
- MIME type, filename, body bytes, and no-store headers are correct.
- Archived-document viewing behavior is explicit and tested.
- Existing evidence, analysis, clarification, and report tests remain unchanged.

### Integration tests

- New Case → upload → admit → analyze → open result.
- Analysis with no gap remains headless until Chat is actually used.
- Analysis with a gap creates the persisted question and focuses Chat.
- Follow-up answer becomes evidence and starts re-analysis.
- New material makes the displayed result stale.
- Re-analysis preserves the previous result and produces a new current result.
- Saved report remains readable while new generation is blocked by stale analysis.
- Citation opens the original source viewer.
- S1 identifies Person A and S2 identifies Person B; re-analysis preserves both, renders the operator finding as conflicting/not established, and exposes the linked reconciliation question.
- Answering the reconciliation question creates independent source S3, starts re-analysis, preserves S1/S2, and never calls a correction or supersession endpoint.
- If S3 does not resolve the conflict, the revised result may remain conflicting without losing any source.

### Browser and visual QA

- Desktop at wide and medium widths.
- Mobile tab switching with preserved Chat draft.
- Long English and Thai titles and long source filenames.
- Keyboard navigation and focus restoration across pane expansion.
- Reduced-motion behavior.
- PDF viewer loading, retry, and closing.
- Chat expansion/collapse without changing the stable Sources pane or displacing Case Work as the primary surface.

## 18. Phased Implementation Plan

### Phase 1A: Case-first hierarchy and workflow

1. Introduce the Case workspace shell with Sources left, primary Case Work center, and persistent/collapsible Chat right.
2. Consolidate Intake and Materials into one Sources experience while preserving existing upload, admission, narrative, and evidence behavior.
3. Make current/stale Analysis the primary center document and keep the last successful result readable during processing or failure.
4. Present actionable Information Needed beside affected findings, including explicit conflicting-evidence reconciliation.
5. Keep normal ASK distinct from evidence-producing follow-up mode and preserve Chat state through collapse/expand.
6. Move Report readiness and saved-report entry points into Case Work; block new generation when Analysis is stale.
7. Add conditional technical-context placement without treating it as Case evidence.
8. Prove route, ownership, and workflow parity before retiring duplicated Intake/Materials composition.

Phase 1A does not add original-file preview, citation targeting, multi-file queue UX, complete localization, or layout motion. Existing single-file upload and evidence inspection behavior remains available until Phase 1B replaces it.

### Phase 1B: Source interaction

1. Add multi-file upload sequencing with per-file status, retry, and removal.
2. Add the authenticated original-document content endpoint.
3. Extract the shared PDF viewer and add image and unsupported-file renderers.
4. Open original files from Sources without changing Case Work or Chat state.
5. Wire Analysis and Chat citations to the exact selected source and page where metadata permits.
6. Validate file security, Blob URL lifecycle, unsupported formats, and source-focused navigation.

### Phase 1C: Localization and interaction polish

1. Establish English-default localization and the complete Thai locale for all workspace states and actions.
2. Keep interface locale independent from generated-output language.
3. Complete desktop, medium-screen, and mobile behavior with Case Work primary at every breakpoint.
4. Refine Chat collapse/expand, source viewing, focus restoration, keyboard access, and reduced motion.
5. Validate long English/Thai content, accessible names, live regions, contrast, and recovery copy.

Each sub-phase has its own parity and regression gate. Phase 1B starts only after 1A is accepted; Phase 1C starts only after 1B is accepted. No sub-phase may rely on unfinished behavior from the next one.

### Phase 1 exit gates

- 1A exits only when Case routes, analysis freshness, conflicting-evidence reconciliation, follow-up admission, Chat persistence, and Report readiness pass focused component and E2E tests without changing backend ownership semantics.
- 1B exits only when authenticated original-file retrieval, viewer lifecycle, multi-file failure isolation, and citation targeting pass backend, component, and browser tests.
- 1C exits only when English/Thai coverage, locale independence, responsive hierarchy, keyboard focus, reduced motion, contrast, and accessible status announcements pass automated checks and visual QA.

### Phase 2: Analytical history and evidence evolution

1. Add lightweight Analysis history selection using existing endpoints.
2. Summarize meaningful evidence changes without exposing raw revision mechanics.
3. Show whether gaps were resolved, retained, or newly opened.
4. Add evidence correction UI with preserved source revisions.
5. Add original/OCR side-by-side review if authorized.
6. Evaluate reliable DOCX preview conversion.
7. Add a bounded comparison view for selected current and historical Analysis Results.

## 19. Additional Functions Recommended

These functions fit the approved design without changing its mental model:

- Deterministic next-action guidance derived from real Case state.
- Multi-file upload queue with per-file status and retry.
- Source filtering by file type and readiness.
- Direct source targeting from every citation.
- Explicit stale-analysis Report guard.
- Current-versus-history selector under progressive disclosure.
- Recent meaningful Case activity, excluding low-level processing noise.

OCR correction, source revision comparison, and Analysis diffing remain Phase 2.

## 20. Acceptance Criteria

The Phase 1 implementation is acceptable only when:

- The workspace clearly reads as one Case, not an independent Chat product.
- Sources remains present and stable while Case Work changes and Chat expands or collapses.
- Case Work is the primary center surface at desktop, medium, and mobile widths.
- Original PDFs and images can be opened securely from Sources.
- Chat history and draft survive every pane interaction.
- No ChatThread is created merely because a Case page rendered.
- Normal ASK is visibly and behaviorally non-evidentiary.
- Follow-up answer mode is visibly and behaviorally evidence-producing.
- Analysis freshness is understandable without exposing a revision number.
- Existing successful Analysis and Reports remain readable during processing or failure.
- Stale Analysis cannot generate a new Report.
- Every important finding can navigate to its Case source where metadata permits.
- Conflicting independent evidence is displayed as separately attributed source statements linked to a conflicting/not-established finding.
- A conflict-driven Information Needed item names the unresolved issue, explains why it matters, and opens the exact follow-up in Chat.
- A reconciliation answer is admitted as a new source and triggers re-analysis without correcting, replacing, or superseding the conflicting sources.
- External technical context is visibly separate from Case evidence.
- Empty, loading, stale, processing, failure, and historical states are covered.
- English copy is the default and is natural, consistent, and action-oriented.
- Thai locale copy is complete, natural, and never mixed inline with English labels.
- Interface locale and generated-output language can be changed independently without altering original source content.
- Keyboard access, focus management, mobile behavior, and reduced motion are verified.
- Existing backend ownership and trust boundaries remain intact.
