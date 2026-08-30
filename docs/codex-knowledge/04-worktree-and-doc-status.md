# Worktree and Markdown Status

Snapshot date: 2026-08-22. This note is a diagnostic snapshot, not a promise
that the worktree is clean.

## Markdown files

The tracked Markdown status observed at snapshot time:

- `main` and `origin/main` resolve to
  `c87ce59eda119d79bacf27d152a2c5966b488983` after the approved refactor.
- The user-owned dirty change is `backend/requirements.txt`; pre-existing
  dirty files remain under `rag_service/**`.
- This documentation pass updates active root, backend, frontend, integration,
  and `docs/codex-knowledge/` notes without editing `rag_service/**`.
- `backend/app/routers/chat.py` implements chat-scoped report generation,
  listing, retrieval, and PDF endpoints. The standalone top-level
  `/api/v1/reports` route remains absent.
- Research plans, experiment outputs, deliverables, and the dated handoff are
  historical evidence and should not be rewritten as current runtime guides.

## Broader dirty worktree

The worktree also contains pre-existing `rag_service/**` changes and the
user-owned backend requirements change. These changes belong to the workspace
and must not be reset or silently folded into a docs cleanup.

## Safe documentation workflow

1. Read this index and the relevant source-backed note.
2. Verify behavior in code/tests before editing an existing document.
3. Add new knowledge notes under `docs/codex-knowledge/` when the change is
   architectural or cross-service.
4. Keep generated/runtime logs, secrets, raw incident text, and provider output
   out of committed Markdown.
5. Before handoff, run `git diff --check` and report the exact Markdown paths
   changed; do not claim the whole repository is clean.
