# Compatibility Ghost Removal Design

Date: 2026-09-14

## Outcome

The current `main` checkout will use one Case-owned interaction and evidence contract. Existing analysis, clarification, Ask, optional MITRE augmentation, report, and document-ingestion behavior remain intact. Compatibility artifacts that no longer represent runtime state are removed rather than reintroduced as adapters.

## Canonical model

`Case.evidence_revision` is the only evidence revision coordinate. Active `EvidenceSource` rows are assembled for a `CaseRun` created at revision `N`. The run and its `CaseAnalysisResult` retain `evidence_revision=N`; no persisted snapshot object, SHA chain, or source-revision entity is used.

Chat messages are directly owned by the Case. Case Chat reads and writes use the Case ID, and a read does not create an entity. Legacy `/chats/*`, `ChatThread`, and ChatReport compatibility surfaces are removed when no production caller remains.

Main Analysis produces the canonical gaps. Deterministic follow-up selection and optional question phrasing operate on that trace. If no canonical gaps are available, no standalone Gap Analysis call is made.

## Revision safety

The worker locks and rereads the Case after claiming a run and before assembling evidence. A revision mismatch marks the run failed as superseded. Completion locks the Case and run, checks the captured revision before assembling/validating, and checks it again immediately before creating and promoting an analysis result. A run that observes `N+1` never creates the current result for `N`.

## Scope boundaries

No changes are made under `rag_service/**` or `backend/app/services/document_ingestion/**`. No UI redesign, provider/prompt redesign, new product feature, or deployment is included. The disposable development database may use the canonical Alembic baseline after the ORM/API cutover.

## Verification

The implementation is validated with import/startup checks, focused revision/follow-up/route tests, generated frontend API parity, frontend type/test/lint/build gates, backend tests where the configured database is available, migration parity, and a final repository-wide ghost classification.
