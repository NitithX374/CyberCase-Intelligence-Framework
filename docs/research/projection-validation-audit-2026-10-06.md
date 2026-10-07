# Applied projection-validation boundary audit

Date: 2026-10-06. Working tree: completed grounding refactor on main `1d3c997a2b95933b2d45215c552ddf79579f875f`. This audit describes the inspected code, not an assumed deployed container version.

| Question | Current implementation |
|---|---|
| Structurally validated objects | Provider replies pass Pydantic shape/identifier/length validation. Evidence references check source identity, ID syntax, source membership, text revision, unit existence, nonblank content and per-claim duplicate occurrence. Backend reproduces source offsets/text/document locators. Projection claim IDs are checked; unknown IDs are removed after recording an unassessed verdict. Downstream summary/gap claim IDs and MITRE context membership receive reference checks. |
| Semantically validated objects | Complete Party name+role, Timeline time+event and Impact description against concatenated linked claim texts. The primary direct path does not perform evidence-to-claim NLI. Summary, gaps and MITRE explanations do not receive this projection validator. Legacy meaning recovery is a separate advisory path. |
| `supported` | Every linked claim exists, has a supporting citation, is `reported`, premise/hypothesis fits ≤512 tokenizer tokens, and pinned NLI selects entailment with entailment probability ≥0.5. This is model-predicted claim-to-projection support, not a truth/legal determination. |
| `not_supported` | NLI chooses neutral/contradiction, or chooses entailment below 0.5. This is not a proof the source or projection is false. |
| `unassessed` | `no_claim`, `unknown_claim`, `unbound_claim`, `qualified_claim`, `context_limit`, or `model_unavailable:<reason>`. Eligibility guards occur before NLI. Every referenced claim must pass, so an irrelevant suspected claim can withhold an otherwise supported item. |
| Withheld from Judgement | All Party/Timeline/Impact rows except those with `projection_grounding.verdict == "supported"`. Missing historical verdicts are also withheld by `projection_payload`. |
| Still supplied to Judgement | All claims, including unbound/qualified ones; claim text, epistemic status, supporting/contradicting citations with original source content and evidence IDs, source identities, source locators; answered follow-up history; optional external technical context. Backend diagnostics and projection verdicts are omitted from this model payload. |
| Are claims retained? | Yes. `reading_payload` iterates over every claim. It filters only the three projection arrays. |
| Can a rejected fact be reconstructed? | Yes: from a retained erroneous claim, a cited unit containing more facts than its claim, raw follow-up answers, or a fresh LLM inference. A fact unsupported by its linked claim can even be true elsewhere in the case. Filtering controls one input channel; it is not whole-output verification. |
| Report effect | Both. Indirectly, Judgement's filtered input can change summary/gaps. Directly, report rows retain `projection_grounding` and show semantic warnings. `joined_trace` and `build_case_report_content` retain rejected/unassessed projections, so the report can still display their text. |
| Reusable counters/logs | `CaseGroundingReport`: claimed/resolved/invalid evidence IDs and resolution rate; direct/recovered/without-evidence claims; legacy citation/duplicate/meaning-pointer counters; unknown summary IDs and out-of-context MITRE references. Each projection retains verdict, reason, model and entailment. Provider receipts retain stage/model/input estimate/status/usage/duration. No production projection totals, per-projection latency or NLI-call counters exist. |
| Deterministic versus model-dependent | Segmentation, evidence-ID validation/resolution, binding support, eligibility, token-limit check for fixed tokenizer, supported-only payload selection and metric arithmetic are deterministic. Semantic classification depends on pinned mDeBERTa. Judgement generation is stochastic; its final factual assertions need an independent target audit. |

## Code anchors

- [Evidence Unit segmentation and index](../../backend/app/sources/evidence.py)
- [ID binding and counters](../../backend/app/trace/evidence_binding.py)
- [Claim binding and reference checks](../../backend/app/trace/bind.py)
- [Binding terminology](../../backend/app/trace/support.py)
- [Projection hypotheses, eligibility and NLI verdicts](../../backend/app/trace/projection.py)
- [Pinned model loader and tokenizer limit](../../backend/app/trace/nli_model.py)
- [Reading → binding → Judgement and joined trace](../../backend/app/analysis/write.py)
- [Current Judgement instructions](../../backend/app/analysis/prompts.py)
- [Report projection preservation](../../backend/app/reports/display.py)
- [Claim-mediated chat projection filtering](../../backend/app/chat/compose.py)

`bound` means all surviving known linked claims have supporting citations; `mixed` means some do; `unbound` means none do; `no_claim` means no surviving known claim link. None of these is a semantic verdict. `validation_status="validated"` is a trace/schema/binding state, not a certificate of factual correctness.

## Measurements available without new semantic labels

ID-resolution, invalidity and duplicate rates; pointer/claim evidence coverage; verdict/reason distributions; admission/rejection/abstention counts; actual verifier calls/cache hits and local wall time. These can be recomputed from IDs, diagnostics and instrumentation. A valid pointer establishes a location, not entailment. Counts of rejected projections cannot by themselves establish prevention of unsupported facts.

## Measurements requiring independent labels

Projection precision/recall/F1/accuracy, false acceptance/rejection, unsupported admission and supported retention require gold support labels against linked claims. Final unsupported fact propagation additionally requires judgement-output annotation and a contamination audit. Whole-case correctness, legal correctness, source-to-claim faithfulness, summary quality and production latency require different evidence and are not established by these experiments.

## Reusable data and bounded experiment

The saved English benchmark has `written`/`bound` traces; the Thai clean benchmark has `reading`/`bound`. Six deterministic first-sorted samples contain 66 original projections, with both explicit support and clear mismatches. They are reused with original claim wording/status and frozen path/hash provenance. Citation remapping to addressable units is one-time preparation; failed remaps would remain unbound. The present six samples remap all 118 total controlled+saved claims into valid units.

The new [protocol](../../research/projection_validation/PROTOCOL.md) separates controlled construction, independently annotated saved outputs, ambiguous exclusions, structural diagnostics, admission baselines, paired Judgement replay and contamination controls. No new Reading model call, production edit, migration, external RAG request, model training or translation service is required.

The configured host path `backend/nli_mdeberta` lacks weights. Compose points at the same host folder. This establishes local configuration availability, not which code/model a previously running service has loaded. The harness measures this abstention path separately, then explicitly uses the existing cache snapshot `b5113eb38ab63efdd7f280f8c144ea8b13f978ce`, with the production loader/checksum/threshold and CPU execution. It does not repair or deploy model configuration.
