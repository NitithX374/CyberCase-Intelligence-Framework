# Codex Knowledge Index

This directory is a compact orientation layer for the current CyberCase implementation. The snapshot was verified on 2026-08-23 against the active `codex/fine-tune-prepare` checkout. Executable source, schemas, migrations, and tests remain authoritative.

## Current snapshot

- Backend owns persisted chat, deterministic raw-evidence projection, run-bound retrieval contexts, Main Case Analysis, bounded clarification, and chat-scoped reports.
- Frontend exposes Chat and Report and does not call `rag_service` directly.
- OpenRouter `openai/gpt-5.6-luna` is the explicit default core model.
- Existing research, experiment, and `rag_service/**` changes remain outside this architecture cutover.

## Notes

- [01-current-architecture.md](01-current-architecture.md): current boundaries and lifecycle.
- [02-chat-analysis-contract.md](02-chat-analysis-contract.md): evidence selection, analysis trace, and action semantics.
- [03-rag-backend-contract.md](03-rag-backend-contract.md): RAG HTTP boundary and durable retrieval context.
- [04-worktree-and-doc-status.md](04-worktree-and-doc-status.md): documentation/worktree status notes.

Keep these notes short and factual. Do not copy secrets, provider responses, incident content, or database data into this directory.
