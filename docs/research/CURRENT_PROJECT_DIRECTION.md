# Current Project Direction

Updated 2026-09-15.

This document records CyberCase research and thesis direction. It is not the implementation authority. Runtime behavior must be derived from current source code, tests, API/schema contracts, and the root [`AGENTS.md`](../../AGENTS.md).

## Current research scope

CyberCase studies general investigative case summarization and grounded analysis for Thai case material. The intended reader is an investigator or prosecutor who needs a clear distinction between reported facts, supporting material, unresolved information, technical context, and system limitations.

The main research questions are:

- **RQ1 — Claim-anchored faithfulness:** How does evidence-first, source-linked generation compare with ordinary end-to-end LLM summarization for factual faithfulness, hallucination reduction, and source attribution in Thai investigative case analysis?
- **RQ2 — OCR error propagation:** How do character substitutions, entity corruption, negation changes, and numeric changes in OCR input affect downstream Thai case summaries?
- **RQ3 — Reader usefulness:** Which presentation choices help prosecutors understand the supplied case material and identify what still needs review?

## Current implemented capability

- A Case can contain user-authored narratives, received document material, evidence sources, analysis runs/results, Case-owned Ask/Chat messages, optional technical context, and preliminary reports.
- Main analysis produces a structured overview, findings, source references, and material gaps. Deterministic follow-up policy can ask one focused question; an answer is added as new case evidence and causes re-analysis.
- MITRE ATT&CK retrieval is conditional external context. It may explain technical indicators, but it is never an incident fact or a substitute for case evidence.
- The frontend Case Library is at `/case`; the Case workspace is under `/case/[caseId]`.
- Reports are readable preliminary analysis artifacts. They do not establish legal conclusions or independent truth.

## Future and research ideas

The following are research directions, not implementation requirements:

- richer multi-document review and cross-document comparison;
- improved document viewing and precise page-region navigation;
- controlled OCR and summarization experiments with human evaluation;
- evaluation of claim-level faithfulness, source attribution, gap usefulness, and prosecutor comprehension;
- broader technical-context studies beyond the current conditional MITRE augmentation.

Do not implement a future idea only because it appears in this document or another research note. Confirm a current product requirement and trace the existing callers first.

## Research discipline

Real-case OCR observations without double-keyed transcription must be described as observed inconsistency or probable OCR-related variation, not as a definitive OCR error rate. Experimental results, benchmark reports, and literature notes retain their original dates and methods; they do not certify current runtime behavior.
