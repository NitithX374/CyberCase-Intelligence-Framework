# CyberCase LLM Analysis Module

## Adversarial research assessment

**Assessment date:** 2026-08-23
**Scope:** redesign the Analysis Module for Threat Analysis, Summary Generation, and Impact Scope
**Research horizon:** literature and benchmarks available through 2026-08-23
**Status:** research assessment only; no production code or rag_service/** changes

## Ledger Snapshot

**Goal:** identify an analytically meaningful Analysis Module architecture, then test whether any part of it supports a defensible research contribution.

**Now:** the repository already has Case State, provenance identifiers, MITRE/RAG context, AnalysisTrace, and follow-up infrastructure. The unresolved weakness is that the core analysis path still performs one primary generation call followed by schema, provenance-membership, and status validation; it does not independently audit analytical adequacy.

**Next:** validate the surviving architecture with a controlled, task-specific experiment. The minimum credible research claim is empirical unless the audit policy is formalized and shown to generalize beyond CyberCase.

**Open questions:** the current 28-case results are exploratory; expert labels for claim support, completeness, conflict, and analytical inference are still required. The assessment does not assume those labels already exist.

## Executive verdict

### Best Phase-1 architecture

The strongest redesign is a **raw-preserving, task-aware analytical generation pipeline with an independent evidence-and-adequacy audit gate**:

Raw case evidence + task contract + optional CaseState/provenance sidecar + bounded MITRE context -> Analysis LLM -> independent audit of claim support, evidence membership, epistemic state, conflict, and task coverage -> deterministic finalization

The raw narrative remains authoritative. Case State and event/entity structures are sidecars that make evidence addressable; they are not replacements for the narrative. MITRE/RAG remains technical context, not incident evidence. The audit result is a typed decision: publish as supported, preserve as uncertain, mark contradicted, expose missing coverage, or route a bounded follow-up. A repair call is optional and should not be part of the minimum architecture.

This is technically meaningful because it creates a boundary between:

1. generating a useful analytical answer;
2. checking whether each claim is grounded in the correct incident evidence;
3. checking whether the answer covers the task without inventing certainty; and
4. deciding what the system is allowed to publish.

It is **not a new architecture family in the literature**. Claim decomposition, evidence alignment, NLI, attribution, completeness checking, debate, and revision are all established. The defensible contribution is therefore most likely a CyberCase-specific evaluation protocol, benchmark, or empirical finding about raw evidence preservation and analytical adequacy.

### Strongest Phase-2 contribution

The strongest near-term contribution is an empirical study:

> Under incomplete, conflicting, and distractor-rich cyber incident evidence, does retaining the raw narrative as the authoritative input outperform lossy structured or generic compressed representations, and can a task-aware evidence-and-adequacy gate improve supported-claim precision and critical-fact coverage without increasing unsupported inference or harmful source correction?

This question is narrow enough to test, grounded in the existing results, and more defensible than claiming a novel verifier.

### What must not be claimed

The following claims are not defensible without a substantially different invention and evidence:

- “We introduce claim extraction followed by NLI for grounded analysis.”
- “We introduce an LLM verifier that checks and revises generated claims.”
- “We introduce multi-agent evidence debate.”
- “We introduce evidence graphs or provenance-linked claims.”
- “We introduce confidence-aware or abstaining factuality evaluation.”
- “We introduce structured intermediate representations for cyber analysis.”
- “We improve factuality because the output is JSON.”
- “We solve hallucination, completeness, or forensic reliability.”

Those are, at most, engineering compositions or domain adaptations unless the work adds a formal task-specific property, a new benchmark, a new labeled resource, or a result that survives strong baselines and adversarial evaluation.

## 1. Scope and non-negotiable design constraints

The requested Analysis Module performs exactly three tasks:

1. Threat Analysis
2. Summary Generation
3. Impact Scope

The redesign must preserve the surrounding system rather than rebuild it:

- raw user-provided case evidence remains available and authoritative;
- Case State, entities, relationships, evidence identifiers, timeline data, and provenance remain existing infrastructure;
- MITRE ATT&CK retrieval remains external technical context;
- AnalysisTrace remains the typed record of claims and provenance;
- Gap Analysis and follow-up remain separate workflow components;
- extraction, NER, malware classification, log parsing, forensic tools, report generation, generic SOC agents, and a new RAG system are out of scope as core contributions.

The central design rule is:

> Do not use an intermediate representation as a lossy substitute for evidence unless the experiment proves that the loss is acceptable for the task.

## 2. What the current repository already does

The current repository is not literally Case Input -> General LLM -> Output. It already contains useful boundaries:

| Existing boundary | Current behavior | Implication for redesign |
|---|---|---|
| Initial workflow | Baseline extraction, Case State projection, MITRE/RAG context, main case overview, and separate follow-up evaluation | Do not re-propose extraction, retrieval, or follow-up as the Analysis Module contribution |
| Analysis input | The prompt builder can use validated Case State or the original raw narrative; raw-direct mode explicitly preserves the source narrative | Raw preservation is already an architectural option, not a new claim |
| Prompt contract | Incident narrative is authoritative; retrieved MITRE context is technical context only; reported, suspected, contradicted, and not-established states are distinguished | A redesign should strengthen this contract with an independent audit rather than replace it |
| Analysis executor | One structured analysis generation call, then parsing, forbidden-provenance checks, schema validation, and membership/status validation | The confirmed gap is analytical adequacy verification, not basic JSON or identifier validation |
| AnalysisTrace | Claims carry claim type, epistemic status, entity/relationship/evidence/timeline identifiers, and constrained MITRE associations | The trace is a useful audit substrate; do not invent a parallel provenance model |
| Retrieval projection | Case State is projected deterministically for retrieval and excludes operational metadata | Keep retrieval context and incident facts separate |
| Gap Analysis | A separate provider-backed evaluator identifies missing information and clarification needs | Do not call a new gap question generator a novel Analysis Module |

Relevant implementation paths:

- [initial workflow](<F:\Cybercase Framework\backend\app\services\workflow\pipeline_initial.py>)
- [question workflow](<F:\Cybercase Framework\backend\app\services\workflow\pipeline_question.py>)
- [prompt builder](<F:\Cybercase Framework\backend\app\services\case_analysis\case_analysis_prompt_builder.py>)
- [prompt configuration](<F:\Cybercase Framework\backend\app\services\case_analysis\case_analysis_prompt_config.py>)
- [analysis executor](<F:\Cybercase Framework\backend\app\services\case_analysis\case_analysis_executor.py>)
- [analysis contracts](<F:\Cybercase Framework\backend\app\services\case_analysis\contracts.py>)
- [Case State projector](<F:\Cybercase Framework\backend\app\services\case_state\projector.py>)
- [gap analysis](<F:\Cybercase Framework\backend\app\services\followup\gap_analysis.py>)

### Current production boundary

The production analysis path currently has a meaningful trust boundary but not a full verification boundary:

raw narrative / validated CaseState -> one analysis LLM call -> typed output and provenance validation

The proposed change is therefore not “add structure.” It is:

raw narrative + addressable sidecars -> generate claims -> independently test claim-to-evidence support and task adequacy -> apply publish/uncertainty/conflict policy

That distinction matters for both engineering scope and publication claims.

## 3. Local experimental evidence

The local experiments provide a strong design constraint, but not yet a publishable general conclusion.

### Frozen 28-case representation comparison

The downstream prompt, model, output budget, and metrics were held fixed across the representation conditions. The conditions were:

- B0: complete raw narrative
- B1: production Case State representation, with three fail-closed extraction cases
- B2: GLiNER2 source-grounded atomic-event representation only
- B3: complete raw narrative plus the frozen GLiNER2 event serialization

| Condition | n | ROUGE-L | SBERT | Mean input characters | Assessment |
|---|---:|---:|---:|---:|---|
| B0 raw narrative | 28 | 0.326070 | 0.699460 | 946.1 | Strongest robust reference |
| B1 production Case State | 25 valid | 0.332002 | 0.704340 | 11,479.0 | Similar quality at much larger input; 3 cases failed closed |
| B2 GLiNER2 structure only | 28 | 0.203042 | 0.567078 | 122.1 | Severe degradation; loses narrative context and relations |
| B3 raw plus GLiNER2 events | 28 | 0.335292 | 0.680145 | 1,117.2 | ROUGE-L slightly up, semantic score down; no consistent gain |

Paired comparisons:

- B1 versus B0: ROUGE-L delta -0.007564; SBERT delta +0.001307; B1 was better on 11 and worse on 14 of the 25 valid cases by ROUGE-L.
- B2 versus B0: ROUGE-L delta -0.123028; SBERT delta -0.132382; B2 was worse on 26 of 28 cases by ROUGE-L and 25 of 28 by SBERT.
- B3 versus B0: ROUGE-L delta +0.009222; SBERT delta -0.019315; ROUGE-L wins were 15/28 and SBERT wins were 12/28.

Artifacts:

- [representation comparison report](<F:\Cybercase Framework\experiments\representation_analysis\outputs\pilot_28\report.md>)
- [raw-plus-events report](<F:\Cybercase Framework\experiments\representation_analysis\outputs\pilot_28_b3\report.md>)
- [representation experiment README](<F:\Cybercase Framework\experiments\representation_analysis\README.md>)

### Generic context refinement comparison

The context-refinement run changed only the context string and used the same downstream model, prompt, output constraints, and paired 28-case sample:

| Condition | ROUGE-L | SBERT | Observation |
|---|---:|---:|---|
| B0 raw | 0.326070 | 0.699460 | Reference |
| B1 generic LLMLingua-2 refinement | 0.325878 | 0.702320 | Essentially null in aggregate; task-dependent |

The compressor was not a real compression win in this run: mean character retention was 1.010582. It also lost 12 of 19 protected cyber spans, including CVEs, domains, and time expressions. This rules out “generic compression improves analysis” as a default assumption.

Artifact:

- [context refinement report](<F:\Cybercase Framework\tmp\context_refinement_run_20260823\report.md>)

### Earlier 50-case pilot

The earlier 50-case pilot is useful as background but should not be treated as a clean architecture ablation: B0 used OpenRouter Llama 3.1 8B while B1 used vanilla mT5-base, so model and architecture were confounded. Its large gap is not evidence that an intermediate representation alone causes the difference.

Artifact:

- [50-case pilot report](<F:\Cybercase Framework\research\sevenllm_preflight\results\pilot_1_en\pilot_1_en_50_report.md>)

### What the local evidence rules out

The frozen results are not sufficient to prove a general law, but they make several proposals bad defaults:

1. replacing raw narratives with structure-only input;
2. assuming generic compression preserves cyber-critical facts;
3. assuming appending a structure sidecar will consistently improve generation;
4. treating a large Case State as automatically better because it is more explicit;
5. using ROUGE-L or SBERT alone as evidence of factuality, coverage, or analytical correctness.

The results support a conservative architecture: raw evidence first, structured data as addressable side information, and evaluation of the information-preserving boundary before adding more stages.

## 4. Architecture families

### Family A: raw monolithic generation

raw case -> prompt/task instruction -> Analysis LLM -> prose or JSON

This is the correct baseline and may remain surprisingly strong. Its weakness is not necessarily generation quality; it is the absence of an independent mechanism for detecting unsupported inference, missing critical facts, wrong evidence links, or conflict collapse.

### Family B: structured replacement

raw case -> extractor / CaseState / event graph -> Analysis LLM -> output

This makes evidence addressable but creates an information bottleneck. The frozen B2 result is a direct warning. The production Case State result shows that a large representation can match the raw baseline, but not that it is superior.

### Family C: generic compression or summarization

raw case -> compressor -> Analysis LLM -> output

This can reduce context length in other settings, but generic compression is not task-aware and can remove exact identifiers, temporal qualifiers, negation, or uncertainty markers. The local run found no aggregate gain and documented protected-span loss.

### Family D: raw plus task-conditioned sidecar

raw case + task contract -> evidence index / coverage checklist / CaseState sidecar -> Analysis LLM -> output

This preserves the source while exposing useful structure. It is a sensible engineering direction. It is not novel merely because the sidecar contains entities, relations, or a plan.

### Family E: claim-level evidence audit

raw case + candidate output -> atomic claims -> evidence alignment / entailment / conflict / epistemic audit

This is a mature family. FENICE, FActScore, RARR, A2R, FaStFact, attribution benchmarks, and later 2026 work cover major variants. A CyberCase implementation can be valuable without being a new method.

### Family F: independent verifier or debate

raw case + candidate output -> independent verifier(s) / debate -> decision

This can reduce correlated self-critique failure, but multi-agent debate and evidence contracts are already active research. The number of agents is not the contribution.

### Family G: task-aware analytical adequacy gate

raw case + candidate output -> task-specific coverage, support, conflict, epistemic, and inference-boundary checks -> publish/uncertain/contradicted/follow-up

This is the most promising design space for CyberCase. Its research value depends on defining the task contract and labels precisely enough that the gate is more than a collection of prompts.

### Family H: generate, verify, repair loop

raw case -> generate -> verify -> revise -> reverify -> final

This can improve outputs in some settings but introduces cost, correlated errors, and source-fidelity risk. It should be an optional extension after the audit gate, not the initial research identity.

## 5. Candidate architectures

### Candidate 1 — Raw-preserving analytical adequacy gate

**Pipeline**

raw case -> A: task contract + deterministic evidence index + optional CaseState/provenance sidecar -> Analysis LLM -> B: independent support/coverage/conflict/epistemic audit -> final answer + AnalysisTrace + gate decision

**A: input preparation**

- retain the complete raw case;
- bind the task to a fixed contract for Threat Analysis, Summary Generation, or Impact Scope;
- expose CaseState, entity, relation, timeline, and evidence identifiers as a sidecar;
- keep MITRE/RAG context explicitly external and non-authoritative;
- generate a small coverage checklist from the task contract, not from a lossy summary.

**Analysis LLM**

The generator produces the user-facing answer and typed claims. Each claim should carry the strongest available evidence identifiers and an epistemic status. Analytical inferences must be labeled as inferences rather than reported facts.

**B: audit**

- verify evidence identifiers are members of the case;
- test claim-to-evidence support at claim or subclaim level;
- detect conflict, missing evidence, and unsupported causality;
- evaluate required task slots and critical-fact coverage;
- calibrate reported, supported inference, suspected, contradicted, not established, and unknown;
- distinguish “not found in supplied evidence” from “false.”

**Finalization**

The default is not to rewrite silently. Supported claims publish; unsupported or contradictory claims remain explicitly marked; missing task slots are surfaced; high-risk unresolved gaps can trigger the existing follow-up boundary.

**Assessment**

This is the best Phase-1 architecture. It is modular, preserves raw evidence, uses the existing contracts, and creates a meaningful decision boundary. The general method is not novel.

### Candidate 2 — Task-conditioned coverage planner

**Pipeline**

raw case -> A: task-specific question/coverage plan and evidence ordering -> Analysis LLM -> B: coverage and provenance audit -> final answer

The planner does not summarize the case. It creates explicit slots:

- Threat Analysis: observed activity, actors/entities, sequence, relationships, evidence basis, alternative explanations, uncertainty.
- Summary Generation: incident identity, key events, timeline, reported facts, unresolved conflicts, analytical boundary.
- Impact Scope: affected assets, accounts, data, systems, time window, confidence, evidence basis, unknowns.

**Assessment**

This can improve consistency if the plan is evidence-grounded and the slots are labelable. It can also make the model fill empty slots with plausible text and may duplicate information already in the prompt. Planning and blueprinting are established prior art. The contribution would be a cyber-task contract and empirical benefit, not the existence of planning.

### Candidate 3 — Evidence map plus multi-premise analytical verifier

**Pipeline**

raw case -> A: evidence span/ID map and relation graph as sidecar -> Analysis LLM -> B: multi-premise support, conflict, and inference verifier -> final claim graph + answer

This is the most explicit provenance design. The verifier must handle claims supported by multiple non-contiguous pieces of evidence, temporal relations, negation, and conflicting reports. It should distinguish:

- direct support;
- support by composition;
- partial support;
- contradiction;
- unresolved conflict;
- not established.

**Assessment**

Technically meaningful, but expensive. FENICE, SciFact-style rationale evidence, complex claim verification, minimum evidence groups, CLAIM-BENCH, RECV, and GAVEL show that the core pattern is already well established. Existing CaseState and AnalysisTrace already provide part of the infrastructure. This is a strong engineering architecture and a possible dataset contribution, not a safe standalone method claim.

### Candidate 4 — Independent epistemic and conflict assessor

**Pipeline**

raw case + generated answer -> A: claim segmentation and evidence isolation -> Analysis LLM -> B: independent assessor deprived of generator rationale, checking support/conflict/unknown/abstention -> final answer with calibrated epistemic labels

The assessor should not inherit the generator's explanation as evidence. It receives the raw case, candidate claim, and addressable evidence units. It returns a decision and short evidence pointers. The policy layer can suppress unsupported certainty without replacing the case facts.

**Assessment**

This is a strong safety and evaluation target. It is not a novel verifier family: black-box self-consistency, fact-level hallucination detection, abstention, multi-agent verification, and evidence-contract systems already exist. The defensible CyberCase angle is controlled evaluation of epistemic calibration under cyber-specific uncertainty and conflict.

### Candidate 5 — Bounded audit-and-repair loop

**Pipeline**

raw case -> A: task contract and evidence sidecar -> Analysis LLM -> B: audit -> one targeted repair using only flagged evidence -> final re-audited answer

Repair is restricted to claims with localized evidence and cannot silently correct the raw case. A claim with unresolved conflict is marked unresolved, not “fixed.” The loop has a hard one-repair limit.

**Assessment**

This is a practical extension, not a good first contribution. RARR, A2R, self-refinement, FActScore-style correction, and 2026 harmful-factuality results make the novelty claim weak and the source-fidelity risk real. Use only after Candidate 1 demonstrates that audit findings are reliable.

## 6. Phase-1 ranking

Scores are directional design judgments, not measured results. Prior-art distance means distance from an obvious literature composition; higher is better.

| Rank | Candidate | Technical meaning | Raw preservation | Feasibility | Research leverage | Prior-art distance | Decision |
|---:|---|---:|---:|---:|---:|---:|---|
| 1 | C1 adequacy gate | 5 | 5 | 5 | 5 | 2 | Select as redesign baseline |
| 2 | C4 independent epistemic/conflict assessor | 5 | 5 | 4 | 5 | 2 | Select as evaluation focus |
| 3 | C2 task-conditioned coverage planner | 4 | 4 | 4 | 4 | 2 | Keep as ablation, not identity |
| 4 | C3 evidence map and multi-premise verifier | 5 | 5 | 2 | 4 | 1 | Engineering extension or dataset work |
| 5 | C5 bounded repair loop | 3 | 4 | 2 | 2 | 1 | Defer until audit reliability is proven |

### Phase-1 selection

Select C1 as the architecture and use C4 as its independent audit policy. C2 is an ablation. C3 is a future implementation depth, not a prerequisite. C5 is explicitly deferred.

The minimum implementation should therefore be:

1. preserve raw evidence;
2. reuse the existing AnalysisTrace and evidence IDs;
3. add a task contract for the three tasks;
4. produce candidate claims;
5. run an independent, claim-to-evidence and task-coverage audit;
6. make a deterministic publish/uncertain/contradicted/missing decision;
7. do not silently rewrite the source or invent facts.

## 7. Adversarial attack model

The module must be tested against attacks that target the proposed boundary, not only normal examples.

| Attack | What it changes | Expected failure if the design is weak | Required defense |
|---|---|---|---|
| Entity swap | Replace a host, account, hash, or CVE with a nearby entity | Correct-looking claim linked to the wrong entity | exact entity and evidence membership checks |
| Negation flip | Add or remove “not,” “failed,” or “no evidence” | Reported absence becomes an affirmative event | polarity and scope-aware support labels |
| Temporal reorder | Swap event order or time windows | Attack path and causality become false | timeline-aware relation checks |
| Cross-case contamination | Insert a fact from another incident | External or prior context is treated as current evidence | case-scoped evidence IDs and source partitions |
| Conflict collapse | Give two credible sources different values | Model silently chooses one | explicit conflict state and alternative presentation |
| Partial truth | Support a noun/entity but not the claimed action, time, or scope | A weakly related span is treated as full support | subclaim decomposition and partial-support class |
| Unsupported causality | Evidence shows A and B but not that A caused B | Analytical inference is presented as reported fact | inference-boundary and causal-support check |
| Impact inflation | Mention one affected asset and infer the entire organization | scope is broadened beyond evidence | task-specific impact slots and affected-object recall |
| Unknown-to-negative | No evidence for X is expressed as “X did not occur” | absence of search is misreported as disproof | not established distinct from contradicted |
| RAG contamination | MITRE or external context contains a matching technique | external technical context becomes incident evidence | source-level trust hierarchy |
| Identifier corruption | LLM alters a hash, domain, technique ID, or timestamp | fluent output no longer matches the case | deterministic value and span validation |
| Long-context dilution | Critical evidence is distant or surrounded by distractors | generator omits or misattributes salient facts | position-stratified tests and coverage audit |
| Prompt injection | Raw evidence includes instructions to the model | evidence changes system behavior or output policy | treat evidence as inert data and test injected strings |
| Generator gaming | LLM emits claims or trace links chosen to pass the checker | audit appears positive without real support | independent verifier and hidden adversarial perturbations |
| Verifier correlation | Generator and verifier share the same blind spot | false agreement is mistaken for validation | model/input asymmetry and human adjudication |
| Harmful correction | A source contains a true-looking but case-specific value | repair changes the source-faithful answer to an external “correct” answer | no silent correction; source fidelity is primary |

The attack set should be split by task. Impact Scope needs stronger scope and absence tests; Threat Analysis needs relation and causality tests; Summary Generation needs coverage, conflict, and source-fidelity tests.

## 8. Literature and prior-art audit

### 8.1 Claim extraction, NLI, and multi-granularity alignment

[FENICE: Factuality Evaluation for Natural Language Generation](https://aclanthology.org/2024.findings-acl.841/) already combines generated-summary claim extraction, DeBERTa NLI alignment, coreference refinement, and multi-granularity evidence alignment. Therefore LLM -> atomic claims -> NLI is a direct prior-art match, not a new CyberCase method.

[FActScore](https://aclanthology.org/2023.emnlp-main.741/) established atomic-fact precision with evidence retrieval and verification. [VeriScore](https://aclanthology.org/2024.findings-emnlp.552/) addresses the limitation that not every generated statement is cleanly verifiable, and [FaStFact](https://aclanthology.org/2025.findings-emnlp.1295/) improves the decompose-then-verify pipeline through chunk-level claim extraction, confidence pre-verification, and document-level evidence.

The 2026 [Truth or Mirage? LLM-Oasis](https://aclanthology.org/2026.cl-1.1/) benchmark further shows that end-to-end factuality evaluation remains difficult even for strong models. The problem is open; the decomposition pattern is not new.

### 8.2 Attribution, citations, and provenance

[ALCE](https://aclanthology.org/2023.emnlp-main.398/) benchmarks citation generation and reports that even strong systems can leave substantial content unsupported. [AttributionBench](https://aclanthology.org/2024.findings-acl.886/) evaluates whether generated answers are attributable, while [Fine-grained Citation Evaluation](https://aclanthology.org/2024.inlg-main.35/) distinguishes full, partial, and no support rather than treating attribution as binary.

[SUnsET](https://aclanthology.org/2025.emnlp-main.95/) generates citations to unstructured evidence spans. [LongCite](https://aclanthology.org/2025.findings-acl.264/) targets fine-grained citations for long-context question answering. [Evaluating Evidence Attribution in Generated Fact Checking Explanations](https://aclanthology.org/2025.naacl-long.282/) finds that strong LLMs still make attribution errors and that curated evidence matters.

The 2026 [Attribution, Citation, and Quotation survey](https://aclanthology.org/2026.acl-long.1430/) reviews 134 papers and 300 metrics across seven dimensions. It is strong evidence that the field is active and fragmented, not empty.

### 8.3 Verification, debate, and revision

[RARR](https://aclanthology.org/2023.acl-long.910/) performs research and revision for unsupported claims. [A2R](https://aclanthology.org/2024.eacl-long.149/) explicitly asks, assesses, and refines with evaluators for citation and hallucination. These make a generic audit-and-repair loop unsafe to call novel.

[MARCH](https://aclanthology.org/2026.acl-long.1828/) uses an information-asymmetric solver, proposer, and checker design. [FactSelfCheck](https://aclanthology.org/2026.findings-eacl.296/) performs black-box fact-level hallucination detection and correction. Most directly, [GAVEL](https://aclanthology.org/2026.findings-acl.1789/) introduces an evidence contract binding atomic subclaims to evidence units, deterministic validation, and neutral scrutiny. A CyberCase evidence contract would need to differ materially from these or be presented as an application.

### 8.4 Completeness and missing information

Factual precision is insufficient for incident analysis because an answer can be true but omit the only fact that changes impact scope. [A Critical Evaluation of Evaluations for LFQA](https://aclanthology.org/2023.acl-long.181/) argues for multifaceted evaluation rather than relying on a single automatic metric.

[Summary of a Haystack](https://aclanthology.org/2024.emnlp-main.552/) evaluates query-focused summary coverage and citation in multi-document settings. [Comprehensiveness Metrics for Automatic Evaluation of Factual Recall](https://aclanthology.org/2026.findings-acl.1744/) directly studies missing information and underrepresented viewpoints using NLI, QA, and end-to-end metrics. It finds a simple end-to-end metric surprisingly effective but less robust, interpretable, and granular.

Therefore a task-specific completeness contract for Threat Analysis, Summary Generation, and Impact Scope is useful, but “we check completeness” is not enough for a method claim.

### 8.5 Conflict, uncertainty, and epistemic calibration

[ECON](https://aclanthology.org/2024.emnlp-main.447/) studies conflict between evidence sources and finds that NLI and LLM methods can have high precision but weaker recall; models may favor one source without justification. [NATCONFQA](https://aclanthology.org/2025.uncertainlp-main.13/) studies conflicting answers. [MetaFaith](https://aclanthology.org/2025.emnlp-main.1505/) targets faithful uncertainty expression, while [Do LLMs Know When to NOT Answer?](https://aclanthology.org/2025.coling-main.627/) evaluates abstention.

These papers support the importance of a CyberCase epistemic state protocol. They also show that labels such as unknown, contradicted, and abstain are research variables, not free novelty.

### 8.6 Analytical claims and multi-premise reasoning

[RECV](https://aclanthology.org/2025.findings-acl.1059/) decomposes evidence-based claims into atomic reasoning types. [CLAIM-BENCH](https://aclanthology.org/2025.ijcnlp-long.127/) studies claim-to-evidence links and shows that additional passes can help dispersed evidence at greater cost. [Minimal Evidence Group Identification](https://aclanthology.org/2025.trustnlp-main.8/) directly studies finding the smallest sufficient evidence group.

[Complex Claim Verification with Evidence Retrieved in the Wild](https://aclanthology.org/2024.naacl-long.196/) already combines claim decomposition, retrieval, fine-grained evidence, claim summary, and veracity. [SciFact](https://aclanthology.org/2020.emnlp-main.609/) provides an established support/refute/rationale framing.

CyberCase analytical claims may still be harder because they include temporal relations, alternative explanations, and impact inference. That is a domain-specific challenge and an evaluation opportunity, not evidence that the general decomposition-and-verification method is new.

### 8.7 Source fidelity and revision risk

[Harmful Factuality](https://aclanthology.org/2026.findings-eacl.46/) formalizes the failure mode where an LLM “corrects” a source into a factually true but source-unfaithful output. This is directly relevant to cyber incident narratives, where the system must preserve what was reported even when an external model believes another value is more likely.

The implication is architectural: verification should normally mark, localize, and qualify a problem. It should not silently rewrite raw incident facts. Any repair experiment must measure source fidelity as a first-class outcome.

## 9. Cybersecurity-specific prior art and limits

The cyber domain is also moving beyond generic summarization:

- [SEvenLLM](https://arxiv.org/abs/2405.03446) provides a CTI instruction benchmark that motivates the local task subset, but it does not make a new Analysis Module architecture.
- [CTIBench](https://proceedings.neurips.cc/paper_files/paper/2024/file/5acd3c628aa1819fbf07c39ef73e7285-Paper-Datasets_and_Benchmarks_Track.pdf) benchmarks LLMs on multiple CTI tasks, so a generic “LLMs can analyze CTI” claim is weak.
- [CTISum](https://www.sciencedirect.com/science/article/pii/S0167404826001045) introduces CTI summarization and attack-process summarization tasks and finds that current models, including GPT-4o, still struggle. This supports importance and empirical opportunity, not a new summarization pipeline.
- [ExCyTIn-Bench](https://www.microsoft.com/en-us/research/publication/excytin-bench-evaluating-llm-agents-on-cyber-threat-investigation/) evaluates 7,542 questions grounded in Azure investigation graphs and reports substantial headroom. It is a different operational task, but it raises the bar for claims about cyber evidence reasoning.
- The 2026 [Cyber Defense Benchmark](https://arxiv.org/abs/2604.19533) reports that frontier models perform poorly on open-ended evidence-driven threat hunting. This is a warning against inferring real investigation capability from curated answer similarity.

CyberCase can still contribute by defining a narrower, source-bounded analytical task with expert labels, but it must compare against these broader cyber evaluation directions and clearly state the task boundary.

## 10. Phase-2 contribution candidates

| Candidate | Contribution type | Defensibility | Closest prior art | Evidence required | Recommendation |
|---|---|---|---|---|---|
| C-A | New claim-to-evidence verifier | Low | FENICE, FActScore, GAVEL, attribution work | new algorithm and cross-domain gains | Reject as stated |
| C-B | Raw-preserving task-aware adequacy gate | Medium as engineering; low as generic method | Comprehensiveness Metrics, GAVEL, FENICE | formal task contract, independent audit, strong ablations | Keep as system design; do not oversell novelty |
| C-C | Cyber-specific epistemic/conflict benchmark | High as empirical/resource contribution | ECON, NATCONFQA, abstention, MetaFaith | expert labels, conflict/unknown perturbations, calibration metrics | Strong candidate |
| C-D | Raw versus structure/compression/sidecar study | High as empirical if scaled | context-use, summarization, CTI benchmarks | matched model/prompt, multiple models, larger cases, human labels | Strongest near-term contribution |
| C-E | Cyber analytical-claim evidence graph | Medium as dataset/protocol; low as method | complex claim verification, RECV, CLAIM-BENCH, GAVEL | multi-premise labels, relation/temporal adjudication | Possible thesis extension |
| C-F | One-pass audit plus bounded repair | Low as method; useful engineering | RARR, A2R, harmful-factuality work | source-fidelity and cost study | Defer |
| C-G | Task-specific coverage contracts | Medium as evaluation protocol | SummHay, LFQA, Comprehensiveness Metrics, CTISum | task ontology, critical-fact annotation, omission stress tests | Pair with C-D |

### Strongest method candidate, if a method claim is required

The least weak method-shaped candidate is not a new verifier. It is a **task-specific analytical adequacy policy** that jointly evaluates:

1. support by incident evidence;
2. evidence specificity and completeness;
3. conflict and unknown state;
4. task-critical coverage;
5. distinction between reported facts and analytical inferences;
6. safe finalization behavior.

Even this is only a candidate. To become a method contribution, the policy needs a formal definition, an operational algorithm, a nontrivial reason existing metrics cannot express it, and cross-case evidence that it improves the target without trading away critical coverage or source fidelity.

### Strongest empirical candidate

The strongest empirical contribution is:

> A controlled study of information-preserving representations for cyber analytical generation, showing when raw narrative, validated CaseState, event structure, compression, and raw-plus-sidecar conditions help or hurt Threat Analysis, Summary Generation, and Impact Scope.

The current 28-case study is an exploratory seed. A publishable result requires more cases, more than one model family, expert labels, adversarial splits, and metrics aligned with support, coverage, conflict, and task utility.

## 11. Minimum credible experiment

### Research question

**RQ:** Does a raw-preserving, task-aware evidence-and-adequacy gate improve supported analytical claims and critical-fact coverage over raw LLM generation and representation-only alternatives on incomplete, conflicting, and distractor-rich cyber incident cases, while preserving source fidelity and controlling cost?

### Conditions

Use a fixed generator protocol and compare at least:

1. B0: raw narrative only;
2. B1: raw narrative plus existing CaseState/provenance sidecar;
3. B2: structure-only representation;
4. B3: raw narrative plus structure sidecar;
5. B4: B3 plus independent audit gate;
6. B5: B4 plus one bounded repair, only as an extension.

The key comparison is B4 versus B0/B3. B2 is a negative control, not a proposed production architecture.

### Dataset

Minimum exploratory continuation:

- retain the frozen 28 cases for direct comparability;
- add cases until all three tasks have balanced coverage;
- preserve full raw text and exact source identifiers;
- include naturally incomplete and conflicting cases where possible.

Minimum credible publication study:

- target at least 120–200 cases, stratified by the three tasks and by difficulty;
- use two or more independent model families or model sizes;
- keep evaluation cases and perturbation templates held out from prompt design;
- report the exact generator, verifier, temperature, context, and token budget;
- avoid treating synthetic perturbations as a substitute for real case diversity.

If the available corpus cannot reach that size, frame the work as a pilot or thesis engineering evaluation, not a general benchmark claim.

### Annotation schema

Annotators should label:

- atomic claim boundaries;
- support status: supported, partially supported, contradicted, not established;
- evidence IDs and spans;
- whether multiple evidence units are jointly required;
- reported versus analytical inference;
- epistemic status and confidence;
- conflict presence and which sources conflict;
- task-critical fact coverage;
- impact object, scope, and time-window correctness;
- whether an abstention or follow-up is appropriate.

Two cybersecurity-literate annotators plus adjudication are preferable. Report agreement by label type; do not hide disagreement inside a single score.

### Primary metrics

Primary metrics should be claim- and task-level:

- supported-claim precision, recall, and F1;
- unsupported and contradicted claim rate;
- exact and partial evidence-ID/span precision and recall;
- critical-fact coverage and missing-critical-fact recall;
- conflict detection precision and recall;
- epistemic calibration, Brier score, expected calibration error, and abstention precision/recall;
- impact-scope object and time-window accuracy;
- human pairwise preference or analyst adequacy rating.

Secondary metrics:

- ROUGE-L and SBERT for comparison with the existing pilot;
- latency, input/output tokens, verifier calls, and cost;
- fail-closed rate and follow-up rate;
- output length and readability.

ROUGE-L and SBERT must remain secondary. A semantically similar answer can be unsupported, overbroad, or incomplete.

### Statistical design

- use paired case-level bootstrap confidence intervals;
- use paired randomization or permutation tests for primary comparisons;
- report per-task results, not only an aggregate;
- use mixed-effects models if multiple outputs per case or multiple annotators are available;
- report variance and failure counts;
- preregister or freeze the attack templates and evaluation policy before final scoring.

### Required ablations

- audit on versus off;
- raw versus raw plus sidecar;
- task checklist on versus off;
- independent verifier versus same-model self-critique;
- evidence IDs only versus IDs plus spans;
- no repair versus one repair;
- with and without RAG technical context, while holding the incident narrative fixed;
- long-context position and distractor tests.

### Success criterion

The gate should not be declared successful because a single similarity metric increases. A credible success pattern is:

- lower unsupported and contradicted claim rates;
- higher critical-fact coverage;
- better evidence-link precision and conflict detection;
- no material increase in false abstention or omission;
- no harmful source correction;
- acceptable latency and cost;
- benefits replicated across tasks and at least two model conditions.

## 12. Engineering versus novelty

### Strong engineering contribution

The following is a good production design:

- raw-preserving input;
- existing CaseState and AnalysisTrace reuse;
- task-specific output contracts;
- independent claim/evidence and coverage audit;
- explicit unknown/conflict state;
- deterministic finalization;
- no silent source correction;
- existing follow-up boundary used only for actionable gaps.

That can be valuable, safe, and thesis-worthy as a systems engineering project.

### Weak novelty framing

The following wording would be rejected by an adversarial reviewer:

> “We propose a novel multi-stage LLM architecture that extracts claims, verifies them against evidence, and refines the answer.”

The literature already contains each component and several full combinations. Replace it with:

> “We study whether a raw-preserving, task-specific adequacy gate changes source fidelity, critical-fact coverage, and epistemic calibration for three cyber incident-analysis tasks under controlled evidence perturbations.”

That is an empirical research claim. It can be strong if the study is executed rigorously.

## 13. Final A–K verdict

### A. Best Phase-1 architecture

Raw-preserving generation with a task contract, existing evidence/provenance sidecars, an independent analytical adequacy audit, and deterministic finalization.

### B. Strongest method contribution, if one survives

A formal task-specific adequacy policy combining support, critical-fact coverage, conflict/unknown states, and inference-boundary enforcement. It is presently a hypothesis, not a confirmed novel method.

### C. Strongest empirical contribution

A matched study of raw evidence versus structured, compressed, raw-plus-sidecar, and audited conditions across Threat Analysis, Summary Generation, and Impact Scope, with expert claim/evidence labels and adversarial tests.

### D. Closest prior work

FENICE for claim/evidence alignment; GAVEL for evidence contracts and deterministic scrutiny; Comprehensiveness Metrics for missing information; FActScore/FaStFact for decompose-then-verify; RARR/A2R for revision; ECON and MetaFaith for conflict and uncertainty; CTISum and ExCyTIn-Bench for cyber evaluation context.

### E. Engineering versus novelty

The architecture is a strong engineering redesign. The method novelty is low unless the adequacy policy is formalized and demonstrated to generalize. The empirical study is the safer research contribution.

### F. Forbidden claims

Do not claim novelty for structured extraction, claim decomposition, NLI, evidence graphs, citation alignment, multi-agent verification, self-refinement, abstention, generic completeness checking, or “JSON improves factuality.”

### G. One research question

Does preserving raw cyber evidence and adding an independent, task-aware adequacy gate improve supported and complete analysis without increasing source-unfaithful correction or harmful omission?

### H. Minimum experiment

The six-condition matched comparison above, beginning with the existing 28 cases, expanding to at least 120–200 cases for a publishable study, and adding expert claim/evidence/coverage labels plus adversarial perturbations.

### I. Datasets and metrics

Use the frozen SEvenLLM-derived cases for continuity, add source-bounded cyber cases, and report claim support, evidence links, critical-fact coverage, conflict detection, epistemic calibration, impact-scope correctness, human adequacy, cost, and latency. Keep ROUGE-L and SBERT secondary.

### J. Thesis and publication suitability

Very suitable for a thesis as an empirical systems study and potentially suitable for an applied NLP/cybersecurity venue. A top-tier method paper is not supported by the current proposal alone. Publication suitability depends on annotation quality, cross-model replication, adversarial evaluation, and a clear distinction between domain contribution and algorithmic novelty.

### K. Confidence and risks

**Confidence:** high that generic claim-verification and audit-and-repair novelty claims will fail; high that raw preservation should remain the design default given the local evidence; medium that a task-specific adequacy gate will improve human-relevant quality; low that the current 28-case results generalize without expansion.

Main risks:

- small and possibly benchmark-shaped local sample;
- model, prompt, and metric dependence;
- imperfect or unavailable expert labels;
- verifier and generator correlated errors;
- coverage metric rewarding verbosity;
- repair improving external truth while damaging source fidelity;
- treating MITRE context as incident evidence;
- overclaiming a domain adaptation as a general method.

## 14. Decision

Proceed with Candidate 1 as the redesign baseline and Candidate 4 as the audit focus. Do not implement Candidate 5 yet. Do not replace the raw narrative with CaseState or event structure. Do not write the thesis contribution as a new claim-verification architecture.

The next artifact should be a frozen evaluation specification and annotation guide, not another model component. Once that specification exists, the implementation can be kept small: task contract, evidence-addressable sidecar, independent audit result, and deterministic finalization behind the existing Analysis Module facade.

## Selected references

The assessment used primary papers and benchmark pages wherever available. The following are the most decision-relevant sources:

- [FENICE: Factuality Evaluation for Natural Language Generation](https://aclanthology.org/2024.findings-acl.841/)
- [Attribution, Citation, and Quotation: A Survey](https://aclanthology.org/2026.acl-long.1430/)
- [FActScore](https://aclanthology.org/2023.emnlp-main.741/)
- [FaStFact](https://aclanthology.org/2025.findings-emnlp.1295/)
- [Truth or Mirage? LLM-Oasis](https://aclanthology.org/2026.cl-1.1/)
- [GAVEL](https://aclanthology.org/2026.findings-acl.1789/)
- [RARR](https://aclanthology.org/2023.acl-long.910/)
- [A2R](https://aclanthology.org/2024.eacl-long.149/)
- [Comprehensiveness Metrics](https://aclanthology.org/2026.findings-acl.1744/)
- [ALCE](https://aclanthology.org/2023.emnlp-main.398/)
- [Fine-grained Citation Evaluation](https://aclanthology.org/2024.inlg-main.35/)
- [ECON](https://aclanthology.org/2024.emnlp-main.447/)
- [RECV](https://aclanthology.org/2025.findings-acl.1059/)
- [Harmful Factuality](https://aclanthology.org/2026.findings-eacl.46/)
- [CTISum](https://www.sciencedirect.com/science/article/pii/S0167404826001045)
- [ExCyTIn-Bench](https://www.microsoft.com/en-us/research/publication/excytin-bench-evaluating-llm-agents-on-cyber-threat-investigation/)
- [Cyber Defense Benchmark](https://arxiv.org/abs/2604.19533)
