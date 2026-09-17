# Backend explainability and prosecutor comprehension review

2026-09-06. Historical product/research assessment based on the then-current working tree. This is not runtime documentation or an implementation requirement; current source, tests, contracts, and root `AGENTS.md` supersede its implementation observations. No production code or case material was changed by the assessment.

## Assessment

The current system partially supports the stated requirement: help prosecutors understand the case file supplied by police, with technical knowledge when relevant. It already has general-case summaries, source-linked claims, uncertainty distinctions, conditional MITRE retrieval, and stateful clarification. The entire backend is not one LLM call. However, the identification and interpretation of claims and gaps remain substantially model-generated, and the application does not yet establish that prosecutors understand cases better.

The useful engineering objective is to make each consequential system decision inspectable and testable. Explaining the internal cause of every generated token is a different research problem. A model-generated reasoning summary is an analytical justification to review, not proof of its internal computation.

## Sample evidence and scope

The user identified `F:\งานอัยการ` as the sample directory. Three DOCX files were read through paragraphs and table cells:

- `F:\งานอัยการ\Dataset\รายงานการสอบสวน 632-2564.docx` includes a police cover letter forwarding the investigation file to a prosecutor and a report addressed to that office. This supports the user's proposed handoff for this specimen.
- `F:\งานอัยการ\Dataset\รายงานการสอบสวน 378-2563.docx` describes an ordinary fraud allegation and lists LINE conversation copies and transfer slips. Digital material does not automatically imply an ATT&CK behavior.
- `F:\งานอัยการ\Dataset\รายงานการสอบสวน 211-2564.docx` contains a property-damage report, including reported conduct, evidence, procedural information, and police recommendations.

These samples use the title `รายงานการสอบสวน`. They contain parties, alleged conduct, chronology, evidence accounts, procedural information, and investigative opinions. A prosecutor needs to distinguish these kinds of information rather than receive a single undifferentiated factual narrative.

Some DOCX samples also contain appended drafting instructions and revised narrative. Those additions are not requirements for this audit and should be separated from original police material before constructing an evaluation dataset. The existing glossary and term-summary Markdown files are secondary notes whose source accuracy has not been verified here.

This inspection does not establish the complete Thai prosecutor workflow, legal requirements, or a validated prosecutor checklist. The reports are useful evidence for product design; the professor and representative prosecutors still need to validate the intended reading tasks.

## Current mechanism

For a fresh case overview, `backend/app/services/workflow/pipeline_execution.py:126` coordinates:

1. An LLM applicability gate evaluates whether authoritative evidence describes ATT&CK-relevant behavior.
2. The backend conditionally calls RAG and binds optional technical context.
3. Main Case Analysis makes a structured LLM request for answer, summary, claims, and optional MITRE associations.
4. Backend code validates structure, source membership, citations and retrieval bindings.
5. A separate LLM gap stage proposes unresolved issues, their status, affected claims, reason, priority, and askability.
6. Code assembles canonical gaps and applies clarification history.
7. Code chooses one eligible gap; another LLM request may phrase a question or choose to proceed.
8. The backend persists the result and follow-up metadata. A clarification answer becomes additional user evidence and causes a fresh analysis cycle.

Ordinary `ask` requests take a different path at `pipeline_execution.py:267`: they reuse existing analysis context and do not run this entire fresh-analysis sequence.

| Mechanism | What code establishes | What remains a model judgment |
|---|---|---|
| Main analysis | Typed output, admitted source IDs, retained exact quotes and conservative page binding | Which facts matter, interpretation, inference, summary coverage |
| Gap analysis | Valid fields, permitted states, valid claim references | Whether a gap actually exists, why it matters, its priority and askability |
| Follow-up selection | High before medium priority; linked claims preferred; stable array-order tie break; unknown and exhausted topics excluded | The upstream gap labels and priority; wording and final provider proceed decision |
| Clarification history | A normalized topic with an answer is exhausted for direct questioning | Whether the answer actually resolves the underlying proposition |
| MITRE routing | RETRIEVE requires admitted source references and exact trigger text | Whether observed behavior warrants ATT&CK context |

Relevant implementations:

- `backend/app/services/case_analysis/case_analysis_executor.py:35`
- `backend/app/services/case_analysis/validation.py:78`
- `backend/app/services/case_analysis/source_citations.py:39`
- `backend/app/services/followup/stateful.py:87` and `:111`
- `backend/app/services/followup/decision.py:163`
- `backend/app/services/followup/metadata.py:53`

The current Main Analysis prompt already requests readable case overview, parties, chronology, evidence and procedural information. Its 5W1H coverage check is an instruction inside the prompt, not an independently executed coverage assessment.

## Material gaps in explainability and requirement fit

### Existing follow-up explanation is lost at the UI contract

`decision.py:107` serializes the selected canonical `AnalysisGapV3`, containing `affected_claim_ids`. `frontend/src/lib/chat-followup.ts:100` requires the legacy `affects` string and returns null otherwise. `ChatTranscript.tsx` uses that parser to supply `FollowUpActionCard`.

A synthetic canonical v3 payload was passed through the actual transpiled frontend parser. It returned null. The same payload with the legacy `affects` field was accepted. This establishes a contract defect; no claim is made that a live provider/browser case was exercised.

### Validation is not semantic proof

The current validators can establish that a source is admitted and a retained quote occurs in that source. They cannot establish that the quote entails the complete claim, that a witness is correct, or that an inference is justified. Invalid quote locators are removed rather than replaced with invented page references. Validated trace must not be presented as verified truth.

Gap-to-claim assembly also contains free-text matching when explicit claim IDs are absent (`gap_assembly.py:115`). Substring/token overlap is a linking heuristic, not an explanation of why the gap affects that claim. Explicit references should be required for any strong dependency claim.

### Missing information is not yet defined against an external criterion

The gap prompt says absence must be demonstrated. But its output contract has no independently checked review criterion, precise target proposition, source-search coverage record, or resolution condition. Most admission rules are instructions to the LLM. An empty gap list is therefore not evidence that a complete case review occurred.

### Technical explanation has a broader scope than ATT&CK

`mitre_applicability_prompt.py:25` deliberately skips technology as an object, including ordinary recordings or communications without explicit cyber behavior. That is sensible for ATT&CK, but a reader might still need help understanding a log, GPS record, metadata, transfer slip, or conversation export.

No dedicated production glossary reference was found in the searched backend, frontend and RAG application paths. General prose may explain terms incidentally, but there is no reliable term-to-definition-to-source-to-case-relevance contract.

The applicability gate also reads bounded prefixes: at most 4,000 characters per source within a 20,000-character total budget. Behavior described later in a long report can be outside the gate input. A SKIP decision should not imply that the whole file contains no technical issue.

### RAG offers useful process structure, not complete transparency

`rag_service/app/RAG/GraphRAG/pipeline/agent_graph.py:398` has explicit routing, retrieval, evaluation, bounded broadening, reasoning and output nodes. Those operations can be inspected. Its evaluator still calls an LLM; `evaluator.py:201`, `:215`, `:248`, and its parser can return SUFFICIENT on retry exhaustion, unavailable evaluation, exceptions or unparseable output.

A new backend mechanism should distinguish evaluation success, unknown result, and exhausted budget. Copying a graph or adding a self-critique call does not establish explanation accuracy.

## Proposed mechanism

### Represent what the reader needs to understand

Define a small versioned review rubric with the professor and prosecutors. Initial candidates, derived from the samples, are: actors and roles, alleged conduct, material chronology, who reports each fact, what material is cited, investigative opinion, relevant procedural status as reported, and technical concepts that affect understanding.

These are reading objectives, not mandatory fields whose absence automatically triggers questions. An absent motive or exact timestamp may be irrelevant. Code should require an applicable review criterion and a specific consequence for understanding before admitting a follow-up candidate.

Extend the existing analysis contracts with source-linked propositions and explicit relationships sufficient for these objectives. Keep original material authoritative and the existing chat/run/report boundaries stable; this does not require resurrecting the deleted Case State architecture or adding a graph database.

### Make gap decisions executable and replayable

For each candidate, retain:

- A stable topic/target identity scoped to the case and evidence snapshot, plus explicit affected claim IDs.
- A review criterion ID and its version.
- The exact unresolved proposition and source-linked evidence considered.
- Search scope and coverage: distinguish absent from reviewed material from not examined or input omitted.
- The possible interpretations that matter to understanding, when applicable.
- Eligibility checks, priority basis, tie-break result, and exclusion reasons for other candidates.
- A precise resolution condition and the evidence that would satisfy it.

The LLM proposes structured observations and semantic links. Backend code executes applicability, eligibility, history and ranking rules. It produces the visible decision explanation from those recorded operations. Domain experts validate the rubric; it is not made authoritative merely by assigning rule IDs.

Allow the LLM to phrase an admitted question within the selected target. For common rule types, reviewed Thai/English templates offer a more tightly controlled initial option. Phrase generation must not silently change the target or introduce an allegation. Semantic checks remain imperfect and need human evaluation.

Represent `asked`, `answered`, `unavailable`, `resolved`, and `still_unresolved` separately. A reply or an exhausted question budget does not resolve the gap. Preserve uncertainties when stopping, and distinguish a module failure from a finding of no material gaps.

### Separate knowledge needs from missing case facts

If the information is already in supplied material, locate and explain it. If the reader needs a technical definition, use a reviewed technical knowledge source. Use ATT&CK when the behavior genuinely fits that knowledge base. If the submitted material does not answer a material factual question, record it as a review item and identify the relevant document or clarification needed.

A proposed explanation record should contain the original term and passage, a plain-language definition, authoritative knowledge citation, relevance to this case, and limits on what the cited case material establishes. Existing local glossaries require source checking before admission. A separate approved technical glossary would be a product/knowledge-source extension, not a reason to weaken the current ATT&CK gate.

Prosecutors should be able to read the current case overview with visible unresolved issues. They may not know the underlying incident facts; asking them a question should not be the only route forward. Any route for requesting additional investigation remains subject to workflow confirmation.

### Illustrative decision trace

This is a synthetic example, not a finding about the samples. Suppose two passages assign different dates to the same transfer. The trace records both passages, the common event identity, the differing dates, and a reviewed chronology criterion. If that distinction affects whether payment preceded a reported representation, the system can explain that dependency and seek clarification. If it does not affect the case narrative, the system records a qualified date discrepancy without interrupting the reader.

Event identity and relevance are still proposed interpretations. The interface must expose their sources and allow correction. The rule engine can justify its choice given those inputs; it cannot prove every input correct.

## Implementation order and evaluation

1. Repair the current v3 explanation contract and expose existing reasons with accurate labels. This fixes visibility, not semantic reliability.
2. Validate a small comprehension rubric against clean samples with the professor and representative prosecutors.
3. Pilot explicit gap targets, rule decisions, source coverage and resolution states inside the existing modules. Measure repeatability and false questions before expanding.
4. Add source-backed technical explanations independent of optional ATT&CK enrichment.
5. Compare the existing system with the proposed mechanism on held-out, expert-reviewed cases. Include ordinary cases with no technical terms, digital material without attacks, genuine ATT&CK behavior, contradictions, and unavailable information.

Measure factual comprehension, term comprehension, source-finding accuracy/time, unsupported conclusions, recognition of uncertainty, unnecessary/repeated questions, actual gap resolution, review time, and model calls/cost. Use counterbalanced reading tasks to reduce practice effects. Include source-only reading as a baseline. Do not use satisfaction, valid JSON, RAG retrieval quality, or an LLM judge alone as evidence of prosecutor benefit.

Mechanism tests should remove/add a relevant fact, vary irrelevant wording, place relevant passages late in a file, return an unrelated answer, and exhaust the budget. The expected rule changes should be declared before running the experiment.

## Validation performed

- Current checkout, dirty-tree baseline, backend workflow/contracts/prompts, frontend explanation render path, and RAG graph/evaluator inspected.
- Three local DOCX samples read as text; document layout and complete case dossiers were not visually reviewed.
- Actual frontend parser exercised in memory: canonical v3 detail rejected; legacy control accepted.
- `env_mitre/Scripts/python.exe -m pytest tests/test_stateful_clarification_decisions.py tests/test_gap_assembly.py tests/test_analysis_trace_v3.py -q` from `backend`: 39 passed.
- No live provider calls, browser end-to-end run, prosecutor user study, code changes, commit or push.

## Research basis

- [NIST Four Principles of Explainable Artificial Intelligence](https://www.nist.gov/publications/four-principles-explainable-artificial-intelligence): explanations should be meaningful, accurately reflect the system process, and respect knowledge limits.
- [Anthropic research on reasoning faithfulness](https://www.anthropic.com/research/reasoning-models-dont-say-think): stated reasoning is not a guaranteed account of the causes behind a model's answer.
- [MITRE ATT&CK introduction](https://attack.mitre.org/resources/): ATT&CK concerns observed adversary techniques and behavior. Its scope supports conditional attack-context enrichment; it does not supply a complete prosecutor workflow or general digital-evidence curriculum.
