# Project evidence for the clarification admission proposal

2026-09-06. Inventory scoped to the current contribution discussion.

## Repository map and method evidence

- `backend/app/services/workflow/pipeline_execution.py`: current fresh analysis, gap stage and clarification orchestration.
- `backend/app/services/case_analysis/contracts.py`: source-linked claims and canonical gaps.
- `backend/app/services/case_analysis/gap_assembly.py`: gap-to-claim linking, including free-text heuristics.
- `backend/app/services/followup/stateful.py`: history, eligibility and deterministic ranking.
- `backend/app/services/followup/decision.py`: current question policy and persisted decision record.
- `backend/app/services/followup/prompt_templates/`: current LLM gap and follow-up instructions.
- `frontend/src/lib/chat-followup.ts`: current explanation parsing defect recorded in the prior audit.

## Existing experiment and writing assets

- `docs/product/BACKEND_EXPLAINABILITY_REVIEW.md`: current audit, sample inspection, verified software findings and limitations.
- `docs/thesis_v1/`: existing thesis material; not revised by this proposal.
- `backend/experiments/`: earlier experiments exist; no results have been established as measurements of this new gate.
- `F:\งานอัยการ\Dataset`: user-supplied candidate samples; original/revised/instruction boundaries and permitted research use need assessment.

## Citation assets

Fresh primary-source pages inspected for CLAMBER (ACL 2024), factual clarification (GEM 2025), and missing/useful question generation (NAACL 2021). URLs are in paper_story.md. No manuscript-ready bibliography or exhaustive literature review was produced.

## Missing inputs

Expert comprehension/materiality rubric, clean source packets, annotation protocol, case-level splits, explicit gate specification, qualified reviewers, model configuration, experiment budget, repeat policy and sample-size justification. The proposed method is not implemented.
