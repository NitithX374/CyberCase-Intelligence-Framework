# Main Case Analysis diagnostic

This is a research-only fixture package for isolating the current Main Case
Analysis component. The first executable pilot uses the user-authorized no-RAG
fallback because the production RAG service could not be started:

```text
fixed Case State + explicitly empty analysis context
    -> current case_overview Main Case Analysis
    -> atomic claims -> independent audits -> coverage audit
```

It does not change the production prompt, services, database schema, RAG
pipeline, or frontend.

## No-RAG pilot

Run from the repository root with the project environment:

```powershell
& env_mitre\Scripts\python.exe research\diagnostic\run_no_rag_diagnostic.py
```

This calls the unchanged production Main Case Analysis service with
`retrieved_context: ""`, `mitre_table: []`, `retrieval_context_id: null`, and
`previous_analysis: null`. It does not call or emulate RAG. The report labels
this mode `NO_RAG_FIXED_EMPTY_CONTEXT`; it cannot establish behavior of the
RAG-grounded production flow.

The script writes the requested snapshots, analysis outputs, atomic claims,
two judge outputs, coverage results, `summary.json`, and
`DIAGNOSTIC_REPORT.md` into this directory. The completed pilot uses the
configured Luna model for Main Case Analysis, claim decomposition, both
judges, and coverage. Judge B is an independent same-model repeat, not a
model-diverse second opinion. Use `--skip-second-judge` only if the extra run
is unavailable; the resulting limitation is recorded.

The default claim decomposition is the research-only LLM decomposer. It reads
only generated Main Case Analysis text. `--deterministic-claim-extraction` is
available as a bounded fallback and records that mode explicitly.

The `diagnostic_notes` object in each JSONL record is authoring/evaluation
metadata. It must not be included in the Case State or any generator/claim
auditor prompt.

## Files

- `diagnostic_cases.jsonl`: 12 synthetic fixed Case State fixtures.
- `PHASE0_TECHNICAL_NOTE.md`: current production trace and execution stop note.
- `run_no_rag_diagnostic.py`: research-only runner for the no-RAG pilot.
- `snapshots/`: fixed Case State plus explicit empty context for each case.

No production application file was changed.
