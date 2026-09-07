# Research alternatives for CyberCase

2026-09-06. Candidate directions beyond clarification admission, requested by the user. These are alternative single-contribution studies, not an implementation roadmap. No direction is accepted or evaluated, and no first-of-its-kind novelty claim has been established. Current system evidence is in `docs/product/BACKEND_EXPLAINABILITY_REVIEW.md`.

## 1 Contextual technical explanations

Research question: Does linking a technical explanation to the exact case passage, an authoritative definition and an explicit interpretation limit improve understanding compared with a standalone glossary explanation?

Method: represent the original term/passage, sourced definition, case relevance and limits separately. Generate bounded explanations from those components, with source-linked case statements kept distinct from external knowledge. Scope to a reviewed subset of digital evidence concepts; broader knowledge-source admission would require a deliberate product choice. MITRE remains applicable only for relevant adversary behavior.

Comparison: the same case summary, knowledge passages, model and approximate explanation-length budget, with glossary-only versus case-linked explanations. Readers receive counterbalanced, matched cases to reduce learning effects.

Measures: factual and technical comprehension, mistaken implications attributed to the evidence, reading time and expert-rated source support. Prosecutor-specific claims require representative prosecutor participants; student studies must be labelled as proxy studies.

Opportunity: strong fit to the stated goal; novelty must be in the explanation method/task evidence, not adding definitions. Related research already studies simplification and comprehension: https://aclanthology.org/2024.determit-1.15/ and https://aclanthology.org/2026.lrec-1.45/.

## 2 Preserve attribution and uncertainty during summarization

Research question: Can structured source/status constraints reduce the transformation of an allegation or reported opinion into an unqualified factual assertion while retaining useful case content?

Method: represent each proposition with speaker/source, reported/inferred/unknown status and exact supporting spans. Constrain summary generation against this representation and check changes of source/status. Deterministic checks cover references and explicit fields; semantic matching and inference checks remain fallible. Preserve exact page binding independently; do not use semantic similarity to invent source locations.

Comparison: current structured trace/prompt-based system versus additional source/status preservation checks, holding model and source material constant. Existing source IDs and status fields cannot themselves be claimed as new.

Measures: incorrect source attribution, unjustified certainty increases, contradiction loss, retained factual coverage, fluency and abstention/omission rate. Human annotation determines semantic errors; a model judge alone is insufficient.

Opportunity: strong backend fit. Attribution is established research: https://aclanthology.org/2023.emnlp-main.398/ and https://aclanthology.org/2025.emnlp-main.95/. The narrow claim concerns preserving who said what and how certain the supplied record is.

## 3 Timelines that preserve uncertain ordering

Research question: Can source-backed temporal constraints improve case chronology while avoiding invented exact dates and unsupported event order?

Method: extract events and explicit temporal expressions, distinguish event time from reporting/document time, retain approximate intervals and competing source accounts, and use a constraint graph to derive only supported before/after relations. Code detects incompatible constraints and leaves incomparable events unordered. Event extraction and identity remain fallible inputs. A graph database is not required.

Comparison: direct LLM timeline generation versus the same extracted events with temporal-constraint processing; report extraction and ordering errors separately. Cases should include missing years, approximate dates and conflicting accounts. Calendar conversion should occur only under an explicit, justified calendar interpretation.

Measures: event coverage, pairwise ordering accuracy/coverage, invented precision, conflict detection and source support. Report both abstention and accuracy to prevent an empty timeline winning.

Opportunity: a bounded mechanism with measurable errors; temporal extraction and constraint reasoning are established methods. Related timeline work: https://ojs.aaai.org/index.php/AAAI/article/view/34691 and temporal reasoning benchmark: https://aclanthology.org/2024.findings-acl.374/.

## 4 Prevent external knowledge from becoming case facts

Research question: Can separate evidence synthesis and knowledge explanation reduce unsupported incident claims introduced by retrieved technical context while retaining useful explanation?

Method: establish the case-claim representation from submitted material, then attach external explanations through explicit claim/term references. Evaluate additional semantic boundary enforcement against the existing trust prompts and source-ID checks. RAG output may explain a technique, but must not create a reported event.

Comparison: matched evidence, retrieved passages and model, with the current integrated generation path versus the proposed separation. Use an ablation/control for additional model calls or token budget where needed. Include relevant, plausible-but-irrelevant and conflicting retrieved context, and maintain a no-RAG diagnostic condition if useful.

Measures: external-context-only incident assertions, source attribution correctness, retained technical utility, factual coverage and latency/cost. Removing all external context is not evidence of useful boundary enforcement.

Opportunity: strong fit to the backend/RAG interface. Existing architectural trust separation is already implemented and is not itself new; a measured additional mechanism is required. Related hallucination benchmark: https://aclanthology.org/2024.acl-long.585/.

## 5 Evaluate evidence presentation for case understanding

Research question: Does presenting identical case content through an overview with linked sources and explicit uncertainty improve comprehension and error detection compared with a linear summary?

Method: a controlled HCI study. Freeze the content and vary its organization/navigation, using counterbalanced cases. Compare linear presentation with a structured overview and linked evidence. A component ablation is needed if claiming a benefit from one specific UI feature.

Measures: comprehension, source-finding success/time, unsupported-claim detection and confidence calibration. Accuracy and confidence must be analysed together; satisfaction alone does not demonstrate understanding. Include a plan for sample-size precision and independent ground truth.

Opportunity: an empirical contribution rather than a new LLM algorithm. Requires qualified participants for prosecutor-specific conclusions. Related work frames digital-forensics/legal collaboration as a usability problem: https://cris.fau.de/publications/361108373/.

## Recommendation and boundaries

Choose direction 1 for the closest match to the professor's technical-understanding requirement; direction 2 for the closest match to current backend analysis and reliability concerns; direction 3 for a bounded algorithmic project. Direction 5 is strongest when expert participant access is feasible. Each is an alternative; combining all directions would prevent a clean single-contribution evaluation.

For every option: establish a precise method beyond prompt wording, identify the closest prior work before claiming novelty, use meaningful matched baselines, retain source provenance, keep related case variants in one evaluation split, and report the loss of useful content alongside error reduction. No experiments for these proposals have run.
