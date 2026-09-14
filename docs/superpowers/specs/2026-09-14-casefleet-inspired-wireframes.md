# CyberCase CaseFleet-Inspired Wireframes

Status: design-only proposal

Date: 2026-09-14

## Intent

Give CyberCase a denser, evidence-first case workspace inspired by CaseFleet without copying its legal-case ontology, brand, or unsupported interactions.

The wireframes use only the current CyberCase concepts:

- Case
- Intake
- Analysis / Overview
- Materials and admitted evidence
- Optional Technical Context
- Reports
- Optional Case Chat / Ask

This document does not authorize production UI changes. It is the visual contract to review before implementation.

## What is borrowed, and what is not

CaseFleet's public product surfaces emphasize a unified case workspace, source-linked facts, chronology views, filters, and an assistant docked beside the case workspace. Its documentation also describes citations as links from a case record to the supporting source and location. See the [CaseFleet homepage](https://www.casefleet.com/), [timeline feature](https://www.casefleet.com/features/timelines), [facts and citations guide](https://support.casefleet.com/en/articles/9595939-facts-and-citations-explained), and [key concepts guide](https://support.casefleet.com/en/articles/1982995-key-concepts-in-casefleet).

CyberCase should borrow:

- a stable case shell
- compact, scannable rows instead of large dashboard cards
- source links visible at the point of a finding
- a contextual Ask panel beside the primary workspace
- clear status and review states

CyberCase should not borrow:

- Facts, Contacts, Issues, Tasks, or legal matter terminology as new domain objects
- a chronology that invents events from finding order
- a generic Create Fact action
- Saved Views, advanced search, or filters that have no current data contract
- CaseFleet branding, typography, colors, or product copy

## Recommended visual direction

Use a cool, quiet evidence workspace. The visual hierarchy comes from spacing, rules, status chips, and source links rather than decorative cards.

### Tokens

| Role | Token | Use |
| --- | --- | --- |
| Canvas | `#F5F6F8` | page background |
| Surface | `#FFFFFF` | panels, tables, drawers |
| Ink | `#20242A` | headings and primary actions |
| Muted | `#66707A` | supporting text |
| Line | `#D9DEE5` | dividers and table rules |
| Evidence blue | `#356C8A` | source links, citations, evidence actions |
| MITRE violet | existing semantic violet | Technical Context only |

Use Manrope or the existing project sans stack, sentence case, 4–8px radii, 1px borders, and minimal shadows. Do not use all-uppercase labels as the primary information hierarchy. Preserve visible focus rings and `prefers-reduced-motion` behavior.

### Layout principles

1. Case identity is always visible.
2. The current view is one primary surface, not two competing representations.
3. Every evidence-linked claim exposes a direct path to the source drawer.
4. Status explains what happened and what the user can do next.
5. Optional technical context is visually distinct and never looks like admitted evidence.
6. Ask is available without taking ownership of the case workspace.

## Global shell

Desktop target: 1440px wide, 72px minimum row height for primary controls, 240px case rail, flexible center, 360px Ask panel when open.

```text
┌──────────────────┬──────────────────────────────────────────────┬──────────────────────┐
│ CyberCase        │ Case title                         ● Ready   │ Ask                  │
│                  │ New case · Overview · Materials · Report     │                      │
│ + New case       ├──────────────────────────────────────────────┤ Case context        │
│                  │                                                │                      │
│ Recent cases     │  PRIMARY CASE SURFACE                         │  transcript          │
│ ● Incident A     │                                                │  ────────────────    │
│ ○ Vendor review  │  title / status / next action                  │  clarification      │
│ ○ New case       │                                                │  or ordinary Ask     │
│                  │  ┌────────────────────────────────────────┐  │                      │
│ Case             │  │ findings, materials, intake, or report │  │  [Ask a question…]  │
│   Intake         │  └────────────────────────────────────────┘  │                      │
│   Overview       │                                                │                      │
│   Materials      │                                                │                      │
│   Technical      │                                                │                      │
│   Report         │                                                │                      │
└──────────────────┴──────────────────────────────────────────────┴──────────────────────┘
```

Current ownership mapping:

- left rail: `WorkspaceSidebar`
- title/status/header: `WorkspaceHeader`
- center switch: `ChatWorkspaceLayout`
- Ask panel: `WorkspaceChatPanel`
- primary views: `CaseIntakeView`, `CaseOverviewView`, `CaseMaterialsView`, `TechnicalContextView`, `CaseReportView`

The navigation labels can be tuned during implementation, but the existing route meanings remain intact for this phase.

## Wireframe A — Case Home / Intake

`intake` remains the preparation state for a new or not-yet-analyzed Case. It is not a new route or a second case model.

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ New case                                           ● Ready                    │
│ Intake  Overview  Materials  Technical  Report                         [Ask] │
├──────────────────────────────────────────────────────────────────────────────┤
│ Prepare this case                                                            │
│ Add the case narrative, then attach and admit the evidence you want analyzed.│
│                                                                              │
│ Case narrative                                               [Edit]          │
│ ┌──────────────────────────────────────────────────────────────────────────┐ │
│ │ User-authored description                                                │ │
│ └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│ Evidence readiness                                                          │
│ 01  Documents      3 uploaded                                               │
│ 02  Review         2 extracted · 1 awaiting admission                       │
│ 03  Analysis       Ready when admitted evidence is complete                 │
│                                                                              │
│ [Upload document]       [Admit reviewed extraction]       [Run analysis]     │
└──────────────────────────────────────────────────────────────────────────────┘
```

Reuse current upload, extraction admission, error, pending, and run states. Do not add a CaseFleet-like review score or progress percentage unless it is already present in the Case API.

## Wireframe B — Analysis / Overview

The current `CaseOverviewView` is the canonical Case projection. It should become a dense analysis ledger, not a legal Facts table.

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ Incident A                                      ● Analysis available          │
│ Intake  Overview  Materials  Technical  Report                         [Ask] │
├──────────────────────────────────────────────────────────────────────────────┤
│ Analysis                                                [View report]        │
│ Evidence snapshot 2026-09-14 · 12 admitted sources     [Analyze latest]     │
│                                                                              │
│ Summary                                                                      │
│ Short grounded case summary                                                  │
│                                                                              │
│ Findings                                                13 validated         │
│ ┌───────────────┬───────────────────────┬──────────────────────────────────┐ │
│ │ Assessment    │ Finding               │ Evidence                           │ │
│ ├───────────────┼───────────────────────┼──────────────────────────────────┤ │
│ │ Established   │ User-authored claim…  │ [Source 01 · p. 4] [Source 03]   │ │
│ │ Unresolved    │ Material gap…         │ [Open clarification]              │ │
│ │ Conflicting   │ S1 and S2 disagree…   │ [Source 02] [Source 07]           │ │
│ └───────────────┴───────────────────────┴──────────────────────────────────┘ │
│                                                                              │
│ Open questions                                                               │
│ One bounded clarification with [Answer in Ask]                               │
│                                                                              │
│ Optional timeline                                                            │
│ Only explicit timeline entries from the validated analysis; otherwise hidden.│
└──────────────────────────────────────────────────────────────────────────────┘
```

Rules:

- `Established`, `Unresolved`, `Conflicting`, and `Not established` remain semantic statuses from the current analysis contract.
- Evidence pills open `SourceEvidenceDrawer` and preserve exact quote highlighting, source revision, page, and snapshot binding.
- Finding order is not a chronology.
- MITRE references remain in `Technical Context`, not inside the evidence ledger.
- Stale, failed, or processing run states stay visible in the status rail.

## Wireframe C — Materials / Evidence

`CaseMaterialsView` is the source-of-truth inspection surface. The layout should feel like a review table rather than a document gallery.

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ Incident A                                      ● Analysis available          │
│ Intake  Overview  Materials  Technical  Report                         [Ask] │
├──────────────────────────────────────────────────────────────────────────────┤
│ Materials                                             [Upload document]      │
│ Admitted evidence is the input boundary for Case Analysis.                    │
│                                                                              │
│ ┌────────────────┬──────────────┬──────────────┬───────────────────────────┐ │
│ │ Source         │ Extraction   │ Admission     │ Actions                   │ │
│ ├────────────────┼──────────────┼──────────────┼───────────────────────────┤ │
│ │ incident.pdf   │ Reviewed     │ Admitted      │ [Inspect] [Open]          │ │
│ │ email.txt      │ Ready        │ Needs review  │ [Review extraction]       │ │
│ │ notes.docx     │ Processing   │ —             │ [View status]             │ │
│ └────────────────┴──────────────┴──────────────┴───────────────────────────┘ │
│                                                                              │
│ Selected source                                                             │
│ ┌──────────────────────────────────────────────────────────────────────────┐ │
│ │ SourceEvidenceDrawer                                                     │ │
│ │ exact quote · source revision · page/location · [Open in materials]       │ │
│ └──────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘
```

The drawer is the consistent inspection interaction for Overview and Technical Context. Keep `SourceEvidenceContent` as the shared content boundary. A popover is not needed for a second, less capable citation path unless a real interaction requirement is demonstrated.

## Wireframe D — Technical Context

Technical Context is conditional. It is a separate analytical appendix, not another evidence status.

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ Incident A                                      ● Analysis available          │
│ Intake  Overview  Materials  Technical  Report                         [Ask] │
├──────────────────────────────────────────────────────────────────────────────┤
│ Technical context                                      MITRE augmentation    │
│ External context derived from the Case analysis; not admitted evidence.      │
│                                                                              │
│ Applicability                                                               │
│ Technical case · augmentation available                                     │
│                                                                              │
│ Technique / relationship summary                                             │
│ ┌──────────────────────────────────────────────────────────────────────────┐ │
│ │ Existing TechnicalContextView projection                                 │ │
│ │ technique · rationale · external source · linked case evidence            │ │
│ └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│ [Open supporting Case source]                                                │
└──────────────────────────────────────────────────────────────────────────────┘
```

For non-technical cases, keep the route valid and show an intentional empty state explaining that no technical augmentation applies. Do not show generic purple metadata elsewhere.

## Wireframe E — Report

Reports remain a frozen subsystem. This is a presentation shell around the existing persisted report and history components.

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ Incident A                                      ● Analysis available          │
│ Intake  Overview  Materials  Technical  Report                         [Ask] │
├──────────────────────────────────────────────────────────────────────────────┤
│ Report                                                                        │
│ Analysis result  ·  Generated 2026-09-14                    [Open / Export]  │
│                                                                              │
│ Versions                                                                     │
│ ● Current report                                                             │
│ ○ Previous report                                                           │
│                                                                              │
│ ┌──────────────────────────────────────────────────────────────────────────┐ │
│ │ Existing CaseReportView / ReportMarkdownView                             │ │
│ │ deterministic report content                                             │ │
│ └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│ Report provenance and source links remain available in the existing details.  │
└──────────────────────────────────────────────────────────────────────────────┘
```

Do not change report content, generation, persistence, validation, or PDF semantics as part of this visual direction.

## Wireframe F — Ask panel

`WorkspaceChatPanel` is a secondary Case inquiry utility. It is docked on desktop and becomes a full-screen drawer on mobile.

```text
┌───────────────────────────────┐
│ Ask about this Case       [×] │
│ Analysis context: current     │
├───────────────────────────────┤
│                               │
│ Follow-up question            │
│ assistant answer              │
│                               │
│ ───────────────────────────   │
│ Clarification needs your input│
│ [Answer clarification]        │
│                               │
├───────────────────────────────┤
│ Ask a question…          [↑]  │
└───────────────────────────────┘
```

Preserve transcript, ordinary Ask behavior, analysis-context freshness, pending clarification behavior, open/close behavior, keyboard access, and source navigation. Replace JS width/resizing state with CSS layout rules unless a documented resizing requirement is approved later.

## Responsive wireframes

### Tablet

```text
┌───────────────┬─────────────────────────────────────────────┐
│ collapsed rail│ Case header / view selector              [≡]│
│               ├─────────────────────────────────────────────┤
│               │ primary Case surface                 [Ask] │
└───────────────┴─────────────────────────────────────────────┘
```

The case rail collapses behind a button. Ask can remain a right drawer if there is room, otherwise it overlays the primary surface.

### Mobile

```text
┌─────────────────────────────────────┐
│ [≡] Incident A              [Ask]   │
│ Overview ▾                         │
├─────────────────────────────────────┤
│ primary Case surface                │
│                                     │
│ finding / source / action           │
│                                     │
└─────────────────────────────────────┘
```

Use the existing mobile view selector. Ask opens full-screen with a close control and returns focus to the trigger. Tables become stacked source rows; do not introduce horizontal overflow for essential actions.

## Existing component map

| Wireframe surface | Current implementation | Keep / change in a later implementation |
| --- | --- | --- |
| Shell | `ChatWorkspaceLayout.tsx` | keep ownership; simplify obsolete props only |
| Case rail | `layout/WorkspaceSidebar.tsx` | restyle density and labels; keep Case selection/delete |
| Header | `layout/WorkspaceHeader.tsx` | add stronger case/status hierarchy; keep route semantics |
| Case Home / Intake | `intake/CaseIntakeView.tsx` | restyle current preparation states |
| Analysis | `overview/CaseOverviewView.tsx`, `CaseFindingsSection.tsx`, `OverviewStatusRail.tsx` | use one canonical projection and ledger presentation |
| Evidence | `materials/CaseMaterialsView.tsx`, `evidence/SourceEvidenceDrawer.tsx`, `SourceEvidenceContent.tsx` | one inspection interaction |
| Technical | `technical/TechnicalContextView.tsx` | preserve conditional MITRE boundary |
| Report | `report/CaseReportView.tsx`, `PersistedReportCard.tsx`, `ReportHistory.tsx` | visual shell only; freeze semantics |
| Ask | `conversation/WorkspaceChatPanel.tsx`, `ChatPanel.tsx` | CSS-owned sizing; preserve Chat behavior |

## Deliberately absent from the wireframe

- Contacts, Issues, Tasks, or legal matter records
- Create Fact or manual fact editing
- Global search, saved views, or unsupported filters
- Fake document review percentages
- Model/provider controls in the main workspace
- A second Chat-owned analysis surface
- A new Dossier/Evidence/Report navigation model in this phase

## Implementation acceptance criteria

Before production implementation is approved, the result must satisfy all of the following:

1. Every visible row, status, count, and action maps to an existing Case API or existing UI state.
2. No new database table, migration, API contract, RAG behavior, or MITRE retrieval behavior is required.
3. Case Overview, Materials, Technical Context, and Report remain reachable through the current supported routes.
4. Source citations still resolve through `SourceEvidenceDrawer` with exact quote and source revision provenance.
5. Non-technical Cases remain valid without a Technical Context payload.
6. Pending clarification and ordinary Ask flows remain distinguishable.
7. Mobile layout does not hide the current Case, status, source, or Ask actions.
8. Focus restoration, keyboard navigation, reduced motion, and error states remain intact.
9. Visual tests cover the canonical Case path rather than a retired legacy presentation branch.

## Decisions requested before implementation

Recommended defaults:

- Keep the current route names and use `Overview` as the visible analysis label.
- Use the three-column desktop shell only when Ask is open; let the center expand when it is closed.
- Use the dense findings ledger as the primary Overview pattern.
- Show a timeline block only when the current validated analysis contains explicit timeline data.
- Use Evidence blue for source interaction and reserve violet for MITRE context.

The next implementation brief should be created only after these defaults are accepted or revised.

## Self-critique

The first CaseFleet comparison risked importing a legal-product vocabulary into CyberCase. This wireframe removes that risk by keeping the Case as the only domain object, treating findings as analysis output, keeping Materials as the evidence boundary, and making the Case API—not a visual analogy—the source of truth.
