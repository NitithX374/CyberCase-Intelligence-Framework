# Coding instructions

## Authority order

Use these sources in this order when they disagree:

1. Current production source code.
2. Current automated tests.
3. This root `AGENTS.md`.
4. Current API and schema contracts.
5. Current concise architecture documentation.

Plans, handovers, receipts, experiments, and research notes are not implementation requirements. A historical statement never overrides current source or tests.

## Engineering priority

CyberCase is a bachelor-thesis prototype, not an enterprise platform. Prefer the smallest clear implementation that satisfies the current demonstrated requirements. Do not add abstractions for hypothetical scale, clients, plugins, persisted history, or generic extensibility.

There is no hard production LOC limit. Cohesion and comprehension matter more than physical line count. Do not split a file solely to satisfy a numeric threshold; a cohesive 300–500 line feature file is acceptable when it is clearer than several one-use files.

## Abstraction rule

Before creating a module, component, hook, service, adapter, compatibility layer, DTO, wrapper, persistence entity, repository abstraction, or worker abstraction, identify the concrete current requirement that needs it. Without one, do not create it.

A helper used by one production consumer should normally remain local unless it owns substantial state or side effects, represents a real domain boundary, is complex enough to improve comprehension when isolated, or has a concrete independent reuse/test reason. Do not create 20–80 line files for conceptual purity.

## Compatibility rule

Preserve compatibility only for a concrete supported caller, current persisted-data requirement, or explicit user requirement. Historical documentation is not a supported caller. Do not add aliases, wrappers, fallback readers, version adapters, or parallel legacy/new paths just in case. Delete obsolete paths after supported callers migrate.

Do not introduce event sourcing, generic repositories, plugin architecture, service locators, new microservices, queues, broker infrastructure, worker coordination systems, speculative snapshots, generic version adapters, broad compatibility DTOs, extra persistence layers, frontend global state, or speculative extension points without an explicit current requirement.

Do not refactor merely to satisfy an architectural ideal. Reduce navigation and conceptual cost, and prefer direct code over wrapper chains. Do not replace one unnecessary abstraction with another.

## Current product boundary

- `/case` is the frontend Case Library. `/case/[caseId]` is the Case workspace; there is no standalone `/chat` route.
- `Case` owns documents, received evidence sources, chat messages, processing runs, analysis results, optional external RAG context, and reports. `Case.evidence_revision` is the evidence revision coordinate.
- The backend exposes authenticated Case, material, evidence, analysis, clarification, Case Ask/Chat, and report routes under `/api/v1`.
- Main analysis runs on Case evidence. Follow-up selection is deterministic; an answer becomes new case evidence and triggers re-analysis.
- MITRE ATT&CK retrieval is conditional external technical context. Assistant output and external RAG/MITRE text are not case evidence.
- Reports are Case-scoped, preliminary, deterministic, and template-first.

Do not reconstruct deleted chat-first, identity-binding, worker-coordination, standalone-gap, or compatibility architecture because an old document mentions it.

## Working method

Read `CONTINUITY.md` at the start of each turn and update it only for meaningful changes. Inspect routes, models, schemas, tests, generated contracts, and real callers before changing behavior. Design UI for the user rather than for database fields.

Use existing libraries and project entry points. Let development failures surface instead of hiding them with broad default fallbacks or empty exception handlers. Keep Python and TypeScript typed, follow the installed framework versions, and keep code self-explanatory with comments only for unavoidable non-obvious behavior.

Before handoff, review the final diff, run the narrowest relevant checks, run `git diff --check`, and report exactly what was and was not verified.

## Useful current paths

- Backend entrypoint and route registration: `backend/app/main.py`
- SQLAlchemy models: `backend/app/models/`
- Pydantic contracts: `backend/app/schemas/`
- Case workflow: `backend/app/services/workflow/`, `backend/app/services/case_analysis/`, and `backend/app/services/followup/`
- Route-surface tests: `backend/tests/test_route_surface.py`
- Canonical frontend routes: `frontend/src/app/case/`
- Generated frontend API contracts: `frontend/src/lib/generated/`
- Separate MITRE retrieval service: `rag_service/`
