# Evidence grounded clarification admission for case review

2026-09-06. Proposed research direction; not implemented or empirically validated. The user appears to request one contribution. This is a candidate for discussion, not an accepted thesis change.

## Working title

Evidence Grounded Clarification Admission for Police Case File Review

## One sentence thesis

We propose and evaluate an admission mechanism that connects each candidate clarification to a precise unresolved proposition, source coverage and a case-understanding criterion, to test whether it reduces unnecessary questions while retaining useful ones.

## Problem and literature position

Clarification is established research. CLAMBER (ACL 2024) studies ambiguity identification and clarification; Toles et al. (GEM 2025) study recovery of missing factual information; the NAACL 2021 paper Ask what is missing and what is useful studies questions about missing and useful information. The opportunity is a bounded application/method study of source-traceable admission decisions in police case-file review. An exhaustive novelty claim has not been established.

- https://aclanthology.org/2024.acl-long.578/
- https://aclanthology.org/2025.gem-1.15/
- https://aclanthology.org/2021.naacl-main.340/

Dehing et al. provide related forensic report-generation work, but their chat-corpus two-stage pipeline is not the current CyberCase backend and is not the matched control for the admission mechanism proposed here.

## Technical challenge

- A missing detail is not necessarily a material obstacle to understanding.
- A fact may already be supplied in another passage or paraphrase.
- Not found in the examined input is different from absent from the full dossier.
- A model-generated reason can be plausible without being supported.

## Method insight and summary

Treat a proposed question as an action requiring an explicit admission record. Preserve the same candidate-generation and question-generation components across experimental conditions. Each candidate packet records target proposition, affected claim IDs, source spans/coverage, applicable review criterion, evidence-status assessment and known clarification history. Semantic interpretation remains model-assisted. Code validates references and applies versioned eligibility rules, recording admission/rejection reasons. Missing source coverage produces an unknown assessment, not a proof of absence.

The generated explanation must reflect the actual recorded rule execution and distinguish model-assessed inputs from mechanically checked facts. This is process auditability, not token-level or neural interpretability. A schema alone is not a semantic verifier.

## One contribution

A source-traceable clarification admission mechanism, evaluated for the tradeoff between avoiding unnecessary questions and retaining useful clarification opportunities in case review.

## Experimental design

Compare the same shared pipeline with the admission mechanism disabled versus enabled. Generate/cache the same candidate packets for both conditions so richer prompting is not an unmeasured treatment. Keep model, source snapshot, RAG context, analysis/report prompts, question wording procedure and maximum one-question budget matched. The gate is the primary intervention; generation changes must be held constant or separately ablated.

Use independently annotated held-out case packets: relevant information already supplied (including paraphrases), genuinely missing but answerable from supplementary material, explicitly unavailable information, immaterial omissions, and conflicting accounts. Keep variants of the same case in one split. Separate appended drafting instructions/rewritten narratives from source reports before annotation.

Primary measures: unnecessary-question rate and useful-question selection rate, reported together to rule out an ask-nothing solution. Secondary measures: correct target-information recovery after a controlled answer, reviewer-rated source support of the admission record, latency and model cost. Independently verified supporting material supplies controlled answers; no fabricated facts or unconstrained LLM answer oracle. Masked-source experiments must be described as simulations. Report case-level uncertainty and repeat stochastic generations.

The professor and a second qualified reviewer should assess materiality and disagreements where feasible. Prosecutor comprehension benefits require a separate reader evaluation; offline gains alone do not support that claim. No sample-size adequacy, improvement, or statistical significance is claimed before a pilot and power/precision assessment.

## Claims and limits

- Supported now: current software contains source traces, LLM gap analysis and deterministic candidate selection; current audit identifies specific limits relevant to the research question.
- Hypothesis only: the new gate reduces unnecessary questions without unacceptable loss of useful opportunities.
- Avoid: first-ever clarification method, fully explainable LLM, verified truth from valid citations, improved prosecutorial decisions, or equating schema compliance with semantic correctness.

## Reviewer risks

The proposal could amount to routine validation unless the admission policy is precisely specified and the evaluation reveals a meaningful tradeoff. Other risks are biased materiality labels, a weak control, suppression of all questions, near-duplicate case leakage, gains caused by changed generation prompts, and insufficient natural cases. Address these before claiming a research contribution.

## Current evidence

No experiment for this method has run. The 39 tests and frontend parser reproduction in the preceding architecture audit are software evidence only, not research results. See project_inventory.md and experiment_inventory.md.
