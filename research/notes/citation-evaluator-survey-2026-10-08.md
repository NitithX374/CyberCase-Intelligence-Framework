# Citation evaluators actually used in published work

Date: 2026-10-08. Scope: a curated inspection of primary papers and official code, not a census of the field. Eleven scholarly records were verified: ten application/evaluation papers and the original MiniCheck paper. No models were downloaded or run, and no paid inference or Translation API was called.

The question is which independent checker could evaluate CyberCase citations when mDeBERTa already controls production admission. A checker is a measurement instrument; choosing one does not establish superiority over another complete system.

## Actual adoption

| Published work | Evaluator actually used | What it measures | Important distinction |
|---|---|---|---|
| [ALCE, EMNLP 2023](https://aclanthology.org/2023.emnlp-main.398/) | TRUE, `google/t5_xxl_true_nli_mixture` | Citation recall from joint cited passages; precision from independently supporting or necessary citations | The original binary entailment protocol; not coverage of all source facts |
| [L-CiteEval, ACL 2025](https://aclanthology.org/2025.acl-long.263/) | `tasksource/deberta-base-long-nli`; supplementary GPT-4o evaluation | ALCE-style citation precision/recall, with an additional LLM comparison | The published version includes GPT-4o; the NLI checkpoint is still the main automatic checker |
| [Attribute or Abstain, EMNLP 2024](https://aclanthology.org/2024.emnlp-main.463/) | MiniCheck-Flan-T5-Large for QASPER; TRUE for Natural Questions and GovReport | Fraction of statements supported by their cited material | Evaluators were compared against human labels; this is attributability/citation recall, not the complete ALCE precision pair |
| [VTG, EMNLP 2024](https://aclanthology.org/2024.emnlp-main.469/) | TRUE for ALCE scores; Qwen-MAX for LLM citation scores | Citation precision/recall under two scoring protocols | Appendix D additionally separates the system verifier, TrueTeacher, from the evaluator, TRUE |
| [LongCite, Findings ACL 2025](https://aclanthology.org/2025.findings-acl.264/) | GPT-4o | Joint citation recall with full/partial/no support; per-reference relevance for precision | Recall can be 0, 0.5 or 1; its precision rules differ from original ALCE |
| [Ai2 Scholar QA, ACL 2025 System Demonstrations](https://aclanthology.org/2025.acl-demo.49/) | GPT-4o | ALCE-based citation precision/recall for literature synthesis | The paper documents score differences across GPT-4o snapshots; freeze the evaluator version |
| [CiteEval, ACL 2025](https://aclanthology.org/2025.acl-long.1574/) | GPT-4o in CiteEval-Auto | Principle-based citation editing/rating and combined evaluation | A different evaluation framework, rather than a simple replacement NLI inside unchanged ALCE |
| [SourceCheckup, Nature Communications 2025](https://www.nature.com/articles/s41467-025-58551-6) | GPT-4o; Claude Sonnet 3.5 and Llama 3.1 70B also tested as judges | Whether cited medical references support statements; statement/response-level support | Not the same joint-support and leave-one-out CP/CR protocol as ALCE |
| [NitiBench, EMNLP 2025](https://aclanthology.org/2025.emnlp-main.1739/) | `gpt-4o-2024-08-06`, temperature 0.3 | Thai legal answer coverage, contradiction and citation metrics | Citation scoring concerns expected legal provisions; it does not establish accuracy for CyberCase claim-to-Source entailment |
| [Citation Failure / CITENTION, TACL 2026](https://aclanthology.org/2026.tacl-1.66/) | MiniCheck for QASPER; TRUE for GovReport in transfer evaluation | Attributability to selected documents | Its source-ranking evaluation is separate from semantic attributability; not a complete ALCE CP/CR adoption |

GPT-4o appears repeatedly in this inspected sample. That observation does not establish its prevalence across the entire literature or its superiority for Thai case analysis.

## The strongest precedent for a separate evaluator

VTG Appendix D reports an additional experiment with:

- Runtime verification: `google/t5_11b_trueteacher_and_anli`.
- Evaluation: `google/t5_xxl_true_nli_mixture`.

This directly demonstrates separating an internal verifier from the model used to measure outputs. It is an additional experiment, not a description of every VTG result. Different checkpoints can still share training sources and correlated errors; separation alone does not produce gold truth. [VTG Appendix D](https://aclanthology.org/2024.emnlp-main.469.pdf)

## Local alternatives with demonstrated adoption

| Candidate | Evidence of use | Fit and limitation |
|---|---|---|
| [MiniCheck-Flan-T5-Large](https://huggingface.co/lytang/MiniCheck-Flan-T5-Large) | Attribute or Abstain and Citation Failure use MiniCheck for QASPER | Separate T5 backbone from CyberCase's mDeBERTa; a practical local candidate. The model card is English, and Thai case performance remains unmeasured |
| [TRUE/T5-XXL](https://huggingface.co/google/t5_xxl_true_nli_mixture) | Original ALCE, LAB, VTG and Citation Failure | Closest to original ALCE's measurement implementation; much larger than a base/large encoder. Resource suitability needs a separate check |
| [DeBERTa-base-long-NLI](https://huggingface.co/tasksource/deberta-base-long-nli) | L-CiteEval | Another checkpoint with published citation-scoring use, but closer in model family to the deployed mDeBERTa gate |

MiniCheck's original paper is [MiniCheck: Efficient Fact-Checking of LLMs on Grounding Documents, EMNLP 2024](https://aclanthology.org/2024.emnlp-main.499/). Its grounding task is document plus claim. Adapting that prediction to a citation metric still requires an explicit joint/individual/leave-one-out scoring contract.

## LLM judges and the Thai boundary

GPT-4o has several direct citation-evaluation precedents: LongCite, Ai2 Scholar QA and CiteEval. Qwen-MAX is also an actual citation judge in VTG. Qwen-MAX is a proprietary service; substituting an open Qwen checkpoint would be a new adaptation requiring validation.

NitiBench provides a Thai legal LLM-judge precedent. Its Appendix F human comparison concerns coverage and contradiction, not a general validation of per-citation source entailment. SourceCheckup's medical human comparison is likewise domain-specific. Neither transfers evaluator accuracy automatically to CyberCase.

Within the inspected sources, no validated Thai CyberCase-style citation benchmark was identified for MiniCheck or TRUE. This is a limitation of this search, not proof that none exists anywhere.

## Minimal implication for CyberCase

1. Keep production mDeBERTa as the deployed gate and existing verifier-versus-public-gold experiments as classifier evaluation.
2. Evaluate identical saved outputs with a separate frozen checker if adding citation evaluation. Do not use gate decisions as evaluation labels.
3. For an English local pilot, MiniCheck-Flan-T5-Large has a stronger practical adoption case than an untested replacement chosen solely for its size. TRUE remains the original ALCE reference implementation.
4. For Thai outputs, GPT-4o is a candidate with relevant published precedents, but a small independently human-labelled audit is still needed to measure evaluator reliability for this task. No paid run is authorized by this recommendation.
5. Declare the exact citation rules. Changing NLI, joint-support rules, partial-support treatment, or averaging can change scores; numbers from different protocols are not interchangeable.

No final evaluator has been selected or implemented. An independent automatic score measures estimated support relative to cited Sources, not the truth of those Sources, legal correctness, or correctness of the whole pipeline.

## Reproduction and verification

Primary support locations inspected:

| Work | Method/evaluation locator | Official implementation where inspected |
|---|---|---|
| ALCE | Section 3.3; Appendix F | [ALCE eval.py](https://github.com/princeton-nlp/ALCE/blob/main/eval.py), `AUTOAIS_MODEL`, `compute_autoais` |
| L-CiteEval | Section 3.3; Appendices A/B | [eval_citation.py](https://github.com/LCM-Lab/L-CITEEVAL/blob/main/script/eval_citation.py) |
| Attribute or Abstain | Sections 4.2.2/4.2.3; Table 2; Appendix D | [Official repository](https://github.com/UKPLab/emnlp2024-attribute-or-abstain) |
| VTG | Section 3.2; Appendix B; Appendix D | Primary paper |
| LongCite | Sections 3.3 and 5.3; Figures 8–10 | [Official repository](https://github.com/THUDM/LongCite) |
| Ai2 Scholar QA | Section 4.3; Appendices F/J | Primary paper |
| CiteEval | Proposed automatic evaluator and experiment tables | [Official repository](https://github.com/amazon-science/CiteEval) |
| SourceCheckup | Methods: source verification, human evaluation and alternative judges | [Official repository](https://github.com/kevinwu23/SourceCheckup) |
| NitiBench | Section 3.2.2; Appendix F, Table 13 | Primary paper |
| Citation Failure | Section 6.1.2 | [Official repository](https://github.com/UKPLab/tacl2026-citation-failure) |

Fresh metadata and scoped support records: `tmp/citation-evaluator-survey-20261008/citation_requests.json` and `citation_lock.json`. All eleven requested scholarly records were verified via Crossref. Metadata verification establishes record identity; the paper/code inspection above establishes the specific evaluator claims.

Only this report and the workspace continuity ledger were edited for this literature task. No production validation semantics, datasets, model assets, database state or experiments were changed.
